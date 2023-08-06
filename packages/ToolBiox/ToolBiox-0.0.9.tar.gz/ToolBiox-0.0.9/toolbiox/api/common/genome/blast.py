import os
import re
import uuid
import xml.etree.ElementTree as ET
from math import log10
import gzip
from lxml import etree
import sqlite3
from toolbiox.lib.common.sqlite_command import sqlite_select, check_sql_table, init_sql_db_many_table, sqlite_write
from collections import OrderedDict
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.util import logging_init
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.os import mkdir, cmd_run
from toolbiox.lib.common.math.interval import section


class BlastQuery(object):
    def __init__(self, num=None, qID=None, qDef=None, qLen=None, hit=None):
        self.num = num
        self.qID = qID
        self.qDef = qDef
        self.qLen = int(qLen) if not qLen is None else qLen
        self.hit = hit

    def __str__(self):
        short_qDef = re.search('^(\S+)', self.qDef).group(1)
        num_hit = len(self.hit)
        return "Query: %s\n" \
               "Hit_num: %d\n" % (short_qDef, num_hit)

    def all_subject(self):
        subject_id = []
        for i in self.hit:
            short_hDef = re.search('^(\S+)', i.Hit_def).group(1)
            if short_hDef in subject_id:
                continue
            else:
                subject_id.append(short_hDef)
        return subject_id

    def short_qDef(self):
        short_qDef = re.search('^(\S+)', self.qDef).group(1)
        return short_qDef


class BlastHit(object):
    def __str__(self):
        short_qDef = re.search('^(\S+)', self.query.qDef).group(1)
        short_hDef = re.search('^(\S+)', self.Hit_def).group(1)
        num_hit = len(self.hsp)
        return "Query: %s\n" \
               "Subject: %s\n" \
               "Hsp_num: %d\n" % (short_qDef, short_hDef, num_hit)

    def __init__(self, query=None, Hit_num=None, Hit_id=None, Hit_def=None, Hit_accession=None, Hit_len=None, hsp=None):
        self.query = query
        self.Hit_num = Hit_num
        self.Hit_id = Hit_id
        self.Hit_def = Hit_def
        self.Hit_accession = Hit_accession
        self.Hit_len = int(Hit_len) if not Hit_len is None else Hit_len
        self.hsp = hsp

    def short_hDef(self):
        short_hDef = re.search('^(\S+)', self.Hit_def).group(1)
        return short_hDef


class BlastHsp(object):
    def __init__(self, query, subject, Hsp_num=None, Hsp_bit_score=None, Hsp_score=None, Hsp_evalue=None,
                 Hsp_query_from=None, Hsp_query_to=None,
                 Hsp_hit_from=None, Hsp_hit_to=None, Hsp_query_frame=None, Hsp_hit_frame=None, Hsp_identity=None,
                 Hsp_positive=None, Hsp_gaps=None,
                 Hsp_align_len=None, Hsp_qseq=None, Hsp_hseq=None, Hsp_midline=None):
        self.query = query
        self.subject = subject
        self.Hsp_num = int(Hsp_num)
        self.Hsp_bit_score = float(Hsp_bit_score)
        if Hsp_score is None:
            self.Hsp_score = None
        else:
            self.Hsp_score = int(Hsp_score)
        self.Hsp_evalue = float(Hsp_evalue)
        self.Hsp_query_from = int(Hsp_query_from)
        self.Hsp_query_to = int(Hsp_query_to)
        self.Hsp_hit_from = int(Hsp_hit_from)
        self.Hsp_hit_to = int(Hsp_hit_to)
        if Hsp_query_frame is None:
            self.Hsp_query_frame = None
        else:
            self.Hsp_query_frame = int(Hsp_query_frame)
        if Hsp_hit_frame is None:
            self.Hsp_hit_frame = None
        else:
            self.Hsp_hit_frame = int(Hsp_hit_frame)

        try:
            self.Hsp_identical_site = int(Hsp_identity)
            self.Hsp_identical_ratio = int(Hsp_identity)/int(Hsp_align_len)
        except:
            self.Hsp_identical_ratio = float(Hsp_identity)/100
            self.Hsp_identical_site = self.Hsp_identical_ratio * int(Hsp_align_len)

        if Hsp_positive is None:
            self.Hsp_positive = None
        else:
            self.Hsp_positive = int(Hsp_positive)
        self.Hsp_gaps = int(Hsp_gaps)
        self.Hsp_align_len = int(Hsp_align_len)
        if Hsp_qseq is None:
            self.Hsp_qseq = None
        else:
            self.Hsp_qseq = str(Hsp_qseq)
        if Hsp_hseq is None:
            self.Hsp_hseq = None
        else:
            self.Hsp_hseq = str(Hsp_hseq)
        if Hsp_midline is None:
            self.Hsp_midline = None
        else:
            self.Hsp_midline = str(Hsp_midline)


# blast output parser

def fast_iter(context, func, *args, **kwargs):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for event, elem in context:
        func(elem, *args, **kwargs)
        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context


def outfmt5_complete(input_file):
    from toolbiox.lib.xuyuxing.base.base_function import cmd_run
    output = cmd_run('tail -2 %s' % input_file, silence=True)
    if output[0] is True and output[1] == "</BlastOutput>\n\n":
        return True
    else:
        return False


def outfmt5_parameters(input_file):
    doc = etree.iterparse(input_file, events=('start', 'end'))
    _, root = next(doc)
    start_tag = None
    output_dict = {}
    for event, element in doc:
        if event == 'start' and start_tag is None:
            start_tag = element.tag
        if event == 'end' and element.tag == start_tag:
            if element.tag == 'BlastOutput_program':
                output_dict['program'] = element.text
            elif element.tag == 'BlastOutput_db':
                output_dict['db'] = element.text
            elif element.tag == 'BlastOutput_param':
                for params in element:
                    for param in params:
                        output_dict[re.sub(
                            'Parameters_', '', param.tag)] = param.text
                break
            start_tag = None
            root.clear()
    return output_dict


def outfmt5_read(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    output_dict = {}
    for Iteration in root.iter('Iteration'):
        Iteration_iter_num = Iteration.find('Iteration_iter-num').text
        Iteration_query_ID = Iteration.find('Iteration_query-ID').text
        Iteration_query_def = Iteration.find('Iteration_query-def').text
        Iteration_query_len = Iteration.find('Iteration_query-len').text
        query_tmp = BlastQuery(Iteration_iter_num, Iteration_query_ID,
                               Iteration_query_def, Iteration_query_len, [])
        # if Iteration.find('Iteration_message') is not None:
        #    if Iteration.find('Iteration_message').text == "No hits found":
        #        output_dict[Iteration_query_def] = query_tmp
        #        continue
        #    else:
        #        print Iteration.find('Iteration_message').text
        for Hit in Iteration.iter('Hit'):
            Hit_num = Hit.find('Hit_num').text
            Hit_id = Hit.find('Hit_id').text
            Hit_def = Hit.find('Hit_def').text
            Hit_accession = Hit.find('Hit_accession').text
            Hit_len = Hit.find('Hit_len').text
            Hit_tmp = BlastHit(query_tmp, Hit_num, Hit_id,
                               Hit_def, Hit_accession, Hit_len, [])
            for Hsp in Hit.iter('Hsp'):
                Hsp_num = Hsp.find('Hsp_num').text
                Hsp_bit_score = Hsp.find('Hsp_bit-score').text
                Hsp_score = Hsp.find('Hsp_score').text
                Hsp_evalue = Hsp.find('Hsp_evalue').text
                Hsp_query_from = Hsp.find('Hsp_query-from').text
                Hsp_query_to = Hsp.find('Hsp_query-to').text
                Hsp_hit_from = Hsp.find('Hsp_hit-from').text
                Hsp_hit_to = Hsp.find('Hsp_hit-to').text
                Hsp_query_frame = Hsp.find('Hsp_query-frame').text
                Hsp_hit_frame = Hsp.find('Hsp_hit-frame').text
                Hsp_identity = Hsp.find('Hsp_identity').text
                Hsp_positive = Hsp.find('Hsp_positive').text
                Hsp_gaps = Hsp.find('Hsp_gaps').text
                Hsp_align_len = Hsp.find('Hsp_align-len').text
                Hsp_qseq = Hsp.find('Hsp_qseq').text
                Hsp_hseq = Hsp.find('Hsp_hseq').text
                Hsp_midline = Hsp.find('Hsp_midline').text
                Hsp_tmp = BlastHsp(query_tmp, Hit_tmp, Hsp_num, Hsp_bit_score, Hsp_score, Hsp_evalue, Hsp_query_from,
                                   Hsp_query_to, Hsp_hit_from, Hsp_hit_to, Hsp_query_frame, Hsp_hit_frame, Hsp_identity,
                                   Hsp_positive, Hsp_gaps, Hsp_align_len, Hsp_qseq, Hsp_hseq, Hsp_midline)
                Hit_tmp.hsp.append(Hsp_tmp)
            query_tmp.hit.append(Hit_tmp)
        output_dict[Iteration_query_def] = query_tmp
    return output_dict


def outfmt5_read_big(input_file, keep_no_hits=False):
    context = etree.iterparse(input_file, tag="Iteration")
    for event, Iteration in context:
        Iteration_iter_num = Iteration.find('Iteration_iter-num').text
        Iteration_query_ID = Iteration.find('Iteration_query-ID').text
        Iteration_query_def = Iteration.find('Iteration_query-def').text
        Iteration_query_len = Iteration.find('Iteration_query-len').text
        query_tmp = BlastQuery(Iteration_iter_num, Iteration_query_ID,
                               Iteration_query_def, Iteration_query_len, [])
        if not (Iteration.find('Iteration_message') is not None and Iteration.find(
                'Iteration_message').text == "No hits found" and keep_no_hits is False):
            for Hit in Iteration.iter('Hit'):
                Hit_num = Hit.find('Hit_num').text
                Hit_id = Hit.find('Hit_id').text
                Hit_def = Hit.find('Hit_def').text
                Hit_accession = Hit.find('Hit_accession').text
                Hit_len = Hit.find('Hit_len').text
                Hit_tmp = BlastHit(query_tmp, Hit_num, Hit_id,
                                   Hit_def, Hit_accession, Hit_len, [])
                for Hsp in Hit.iter('Hsp'):
                    Hsp_num = Hsp.find('Hsp_num').text
                    Hsp_bit_score = Hsp.find('Hsp_bit-score').text
                    Hsp_score = Hsp.find('Hsp_score').text
                    Hsp_evalue = Hsp.find('Hsp_evalue').text
                    Hsp_query_from = Hsp.find('Hsp_query-from').text
                    Hsp_query_to = Hsp.find('Hsp_query-to').text
                    Hsp_hit_from = Hsp.find('Hsp_hit-from').text
                    Hsp_hit_to = Hsp.find('Hsp_hit-to').text
                    Hsp_query_frame = Hsp.find('Hsp_query-frame').text
                    Hsp_hit_frame = Hsp.find('Hsp_hit-frame').text
                    Hsp_identity = Hsp.find('Hsp_identity').text
                    Hsp_positive = Hsp.find('Hsp_positive').text
                    Hsp_gaps = Hsp.find('Hsp_gaps').text
                    Hsp_align_len = Hsp.find('Hsp_align-len').text
                    Hsp_qseq = Hsp.find('Hsp_qseq').text
                    Hsp_hseq = Hsp.find('Hsp_hseq').text
                    Hsp_midline = Hsp.find('Hsp_midline').text
                    print(Hsp_identity)
                    Hsp_tmp = BlastHsp(query_tmp, Hit_tmp, Hsp_num, Hsp_bit_score, Hsp_score, Hsp_evalue,
                                       Hsp_query_from,
                                       Hsp_query_to, Hsp_hit_from, Hsp_hit_to, Hsp_query_frame, Hsp_hit_frame,
                                       Hsp_identity,
                                       Hsp_positive, Hsp_gaps, Hsp_align_len, Hsp_qseq, Hsp_hseq, Hsp_midline)
                    Hit_tmp.hsp.append(Hsp_tmp)
                query_tmp.hit.append(Hit_tmp)
            # print(query_tmp.qDef)
            yield query_tmp
        # It's safe to call clear() here because no descendants will be
        # accessed
        Iteration.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in Iteration.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context
    # fast_iter(context, iteration_parser, keep_no_hits=keep_no_hits)


def outfmt6_read(input_file, gzip_flag=False):
    fieldname = ["q_id", "s_id", "identity", "aln_len", "mis", "gap", "q_start", "q_end", "s_start", "s_end", "e_value",
                 "score"]
    all_file = tsv_file_dict_parse(
        input_file, fieldnames=fieldname, gzip_flag=gzip_flag)
    query_dir = {}
    for i in all_file:
        q_id = all_file[i]["q_id"]
        s_id = all_file[i]["s_id"]
        if q_id not in query_dir:
            query_dir[q_id] = {"subject_key_list": []}
        if s_id not in query_dir[q_id]:
            query_dir[q_id][s_id] = []
            query_dir[q_id]["subject_key_list"].append(s_id)
        query_dir[q_id][s_id].append(all_file[i])
    output_dict = {}
    num = 0
    for query in query_dir:
        num = num + 1
        query_tmp = BlastQuery(num, query, None, None, [])
        hit_num = 0
        for hit in query_dir[query]["subject_key_list"]:
            hit_num = hit_num + 1
            hit_tmp = BlastHit(query_tmp, hit_num, hit, None, None, None, [])
            hsp_num = 0
            for hsp in query_dir[query][hit]:
                hsp_num = hsp_num + 1
                hsp_tmp = BlastHsp(query_tmp, hit_tmp, hsp_num, hsp["score"], None, hsp["e_value"], hsp["q_start"],
                                   hsp["q_end"], hsp["s_start"], hsp["s_end"], None, None, hsp["identity"], None,
                                   hsp["gap"],
                                   hsp["aln_len"], None, None, None)
                hit_tmp.hsp.append(hsp_tmp)
            query_tmp.hit.append(hit_tmp)
        output_dict[query] = query_tmp
    return output_dict


def outfmt6_read_big(input_file,
                     fieldname=["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", "qstart", "qend",
                                "sstart", "send", "evalue", "bitscore"], gzip_flag=False):
    if gzip_flag:
        f = gzip.open(input_file, 'rt')
    else:
        f = open(input_file, 'r')

    query_num = 0
    query_tmp = None
    for each_line in f:
        each_line = each_line.strip()
        info = each_line.split("\t")

        info_dict = {}
        for i in range(len(fieldname)):
            info_dict[fieldname[i]] = info[i]

        if query_tmp is None:
            new_query_flag = 1
            new_hit_flag = 1
        else:
            last_query_def = query_tmp.qDef
            last_hit_def = query_tmp.hit[-1].Hit_def
            if last_query_def != info_dict['qseqid']:
                new_query_flag = 1
                new_hit_flag = 1
            else:
                new_query_flag = 0
                if last_hit_def != info_dict['sseqid']:
                    new_hit_flag = 1
                else:
                    new_hit_flag = 0

        if new_query_flag:
            if query_tmp is not None:
                yield query_tmp

            query_num = query_num + 1
            query_tmp = BlastQuery(
                query_num, info_dict['qseqid'], info_dict['qseqid'], None, [])
            hit_num = 0

        if new_hit_flag:
            hit_num = hit_num + 1
            hit_tmp = BlastHit(query_tmp, hit_num, info_dict['sseqid'], info_dict['sseqid'], info_dict['sseqid'], None,
                               [])
            if "staxids" in fieldname:
                hit_tmp.Hit_taxon_id = info_dict['staxids'].split(";")

            query_tmp.hit.append(hit_tmp)
            hsp_num = 0

        hsp_num = hsp_num + 1
        hsp_tmp = BlastHsp(query_tmp, query_tmp.hit[-1], hsp_num, float(info_dict['bitscore']), None,
                           float(info_dict['evalue']), int(
                               info_dict['qstart']),
                           int(info_dict['qend']), int(info_dict['sstart']), int(
                               info_dict['send']), None, None,
                           info_dict['pident'], None, int(
                               info_dict['gapopen']),
                           int(info_dict['length']), None, None, None)
        hsp_tmp.Hsp_mismatch = float(info_dict['mismatch'])

        query_tmp.hit[-1].hsp.append(hsp_tmp)

    if query_tmp is not None:
        yield query_tmp

    f.close()


def outfmt6_write(output_dict_from_outfmt6):
    for query in output_dict_from_outfmt6:
        for subject in output_dict_from_outfmt6[query].hit:
            for hsp in subject.hsp:
                query_id = output_dict_from_outfmt6[query].short_qDef()
                subject_id = subject.short_hDef()
                identity = float(hsp.Hsp_identity) / \
                    float(hsp.Hsp_align_len) * 100
                alignment_length = hsp.Hsp_align_len
                mismatches = hsp.Hsp_align_len - hsp.Hsp_identity
                gap_openings = hsp.Hsp_gaps
                q_start = hsp.Hsp_query_from
                q_end = hsp.Hsp_query_to
                s_start = hsp.Hsp_hit_from
                s_end = hsp.Hsp_hit_to
                e_value = hsp.Hsp_evalue

                outfmt6_print = "%s\t%s\t%.2f\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.5e\t%.2f" % \
                                (query_id, subject_id, identity, alignment_length, mismatches,
                                 gap_openings, q_start, q_end, s_start, s_end, e_value, hsp.Hsp_bit_score)

                yield outfmt6_print


def keep_outfmt6_info(query_record, fancy_name=False, fancy_name_type=1):
    for subject in query_record.hit:
        for hsp in subject.hsp:
            query_id = query_record.short_qDef()
            if fancy_name is True:
                if fancy_name_type == 1:
                    query_id, c_start, c_end = re.search(
                        r'^(\S+):(\d+)-(\d+)$', query_id).groups()
                elif fancy_name_type == 2:
                    query_id, c_start, c_end = re.search(
                        r'^(\S+)_(\d+)-(\d+)$', query_id).groups()
                q_start = int(c_start) + hsp.Hsp_query_from - 1
                q_end = int(c_start) + hsp.Hsp_query_to - 1
            else:
                q_start = hsp.Hsp_query_from
                q_end = hsp.Hsp_query_to
            subject_id = subject.short_hDef()
            identity = float(hsp.Hsp_identity) / float(hsp.Hsp_align_len) * 100
            alignment_length = hsp.Hsp_align_len
            mismatches = hsp.Hsp_align_len - hsp.Hsp_identity
            gap_openings = hsp.Hsp_gaps
            s_start = hsp.Hsp_hit_from
            s_end = hsp.Hsp_hit_to
            e_value = hsp.Hsp_evalue

            outfmt6_print = (query_id, subject_id, identity, alignment_length, mismatches,
                             gap_openings, q_start, q_end, s_start, s_end, e_value, hsp.Hsp_bit_score)

            yield outfmt6_print


# store blast results to sqlite

def blast_to_sqlite(db_name, bls_file, query_fasta=None, subject_fasta=None, outfmt=6, hsp_keep=None, hit_keep=None,
                    log_file=None, fancy_name=False, gzip_flag=False):
    """
    take blast into sqlite file

    sqlite3 structure
    tables

    1. query
        query_num: query rank id
        qDef: query name in blast results
        qID: query name ID in blast results
        qLen: query seq length
        q_hsp_id: a comma split number string to store hsp_id which query is this query record

    2. subject
        hit_num: subject rank_id
        hit_def: subject name in blast results
        hit_id: subject name ID in blast results
        hit_len: subject seq length
        hit_accession: subject seq accession
        s_hsp_id: a comma split number string to store hsp_id which subject is this subject record

    3. hsp
        hsp_id: hsp rank id
        query_num: query rank id
        hit_num: subject rank id
        query_id: query name ID in blast results
        hit_id: subject name ID in blast results
        hit_rank
        Hsp_num
        Hsp_bit_score
        Hsp_score
        Hsp_evalue
        Hsp_query_from
        Hsp_query_to
        Hsp_hit_from
        Hsp_hit_to
        Hsp_query_frame
        Hsp_hit_frame
        Hsp_identity
        Hsp_positive
        Hsp_gaps
        Hsp_align_len
        Hsp_qseq
        Hsp_hseq
        Hsp_midline

    db_name='/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pt_file/OrthoFinder/Results_Aug01/WorkingDirectory/Blast39_23.db.txt'
    bls_file='/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pt_file/OrthoFinder/Results_Aug01/WorkingDirectory/Blast39_23.txt.gz'
    query_fasta=None
    subject_fasta=None
    outfmt=6
    hsp_keep=None
    hit_keep=None
    log_file=None
    fancy_name=False
    gzip_flag=True

    """

    # give column name
    query_columns = ["query_num", "qDef", "qID", "qLen", "q_hsp_id"]

    subject_columns = ["hit_num", "hit_def", "hit_id",
                       "hit_len", "hit_accession", "s_hsp_id"]

    hsp_columns = ["hsp_id", "query_num", "hit_num", "query_id", "hit_id", "hit_rank", "Hsp_num", "Hsp_bit_score",
                   "Hsp_score", "Hsp_evalue", "Hsp_query_from", "Hsp_query_to", "Hsp_hit_from", "Hsp_hit_to",
                   "Hsp_query_frame", "Hsp_hit_frame", "Hsp_identity", "Hsp_positive", "Hsp_gaps", "Hsp_align_len",
                   "Hsp_qseq", "Hsp_hseq", "Hsp_midline"]

    # begin
    module_log = logging_init("blast_to_sqlite", log_file)
    module_log.info(
        'received a call to load bls file %s into sqlite db %s' % (bls_file, db_name))

    # init database
    init_sql_db_many_table(db_name, {
                           "query": query_columns, "subject": subject_columns, "hsp": hsp_columns}, True)

    # load blast results
    if outfmt == 6:
        bls_file_parser = outfmt6_read_big(bls_file, gzip_flag=gzip_flag)
    elif outfmt == 5:
        bls_file_parser = outfmt5_read_big(bls_file)
    else:
        raise ValueError("unknown format")

    waitting_hsp = []
    stored_subject = {}
    stored_query = {}
    hsp_id = 0
    for query in bls_file_parser:
        # store query

        # parse fancy name
        if fancy_name is True:
            query_true_name, c_start, c_end = re.search(
                r'^(\S+):(\d+)-(\d+)$', query.short_qDef()).groups()
            query_info = [len(stored_query) + 1, query_true_name,
                          query_true_name, query.qLen]
        else:
            query_info = [len(stored_query) + 1, query.qDef,
                          query.qID, query.qLen]

        q_def = query_info[1]
        if not q_def in stored_query:
            stored_query[q_def] = {
                "info": query_info,
                "hsp_list": []
            }

        for subject in query.hit:
            # make sure subject is need to store
            if not hit_keep is None and subject.Hit_num > hit_keep:
                break

            # store subject info
            subject_info = [len(stored_subject) + 1, subject.Hit_def, subject.Hit_id, subject.Hit_len,
                            subject.Hit_accession]

            s_def = subject_info[1]
            if not s_def in stored_subject:
                stored_subject[s_def] = {
                    "info": subject_info,
                    "hsp_list": []
                }

            # get hsp info and store
            for hsp in subject.hsp:
                # make sure subject is need to store
                if not hsp_keep is None and hsp.Hsp_num > hsp_keep:
                    break

                # parse fancy name
                if fancy_name is True:
                    query_true_name, c_start, c_end = re.search(
                        r'^(\S+):(\d+)-(\d+)$', query.short_qDef()).groups()
                    q_start = int(c_start) + hsp.Hsp_query_from - 1
                    q_end = int(c_start) + hsp.Hsp_query_to - 1
                else:
                    q_start = hsp.Hsp_query_from
                    q_end = hsp.Hsp_query_to

                hsp_id = hsp_id + 1

                hsp_info = (
                    hsp_id, stored_query[q_def]["info"][0], stored_subject[s_def]["info"][0], q_def, s_def,
                    subject.Hit_num,
                    hsp.Hsp_num, hsp.Hsp_bit_score, hsp.Hsp_score, hsp.Hsp_evalue, q_start, q_end, hsp.Hsp_hit_from,
                    hsp.Hsp_hit_to, hsp.Hsp_query_frame, hsp.Hsp_hit_frame, hsp.Hsp_identity, hsp.Hsp_positive,
                    hsp.Hsp_gaps, hsp.Hsp_align_len, hsp.Hsp_qseq, hsp.Hsp_hseq, hsp.Hsp_midline)

                stored_query[q_def]["hsp_list"].append(hsp_id)
                stored_subject[s_def]["hsp_list"].append(hsp_id)

                waitting_hsp.append(hsp_info)

            if len(waitting_hsp) > 10000:
                sqlite_write(waitting_hsp, db_name, "hsp", hsp_columns)
                waitting_hsp = []
                module_log.info("load %d record" % hsp_id)

    if not len(waitting_hsp) == 0:
        sqlite_write(waitting_hsp, db_name, "hsp", hsp_columns)
        module_log.info("load %d record" % hsp_id)

    from toolbiox.lib.common.util import printer_list

    # write query table
    module_log.info("load query table")
    waitting_query = []
    for q_def in stored_query:
        tmp_info = stored_query[q_def]['info']
        hsp_list_tmp = stored_query[q_def]['hsp_list']
        hsp_list_str = printer_list(hsp_list_tmp, ",")
        tmp_info.append(hsp_list_str)
        waitting_query.append(tmp_info)
    sqlite_write(waitting_query, db_name, "query", query_columns)

    # write subject table
    module_log.info("load subject table")
    waitting_subject = []
    for s_def in stored_subject:
        tmp_info = stored_subject[s_def]['info']
        hsp_list_tmp = stored_subject[s_def]['hsp_list']
        hsp_list_str = printer_list(hsp_list_tmp, ",")
        tmp_info.append(hsp_list_str)
        waitting_subject.append(tmp_info)
    sqlite_write(waitting_subject, db_name, "subject", subject_columns)

    conn = sqlite3.connect(db_name)
    conn.execute("CREATE UNIQUE INDEX %s on %s (\"%s\")" %
                 ("query_index", "query", "qDef"))
    conn.execute("CREATE UNIQUE INDEX %s on %s (\"%s\")" %
                 ("subject_index", "subject", "hit_def"))
    conn.execute("CREATE UNIQUE INDEX %s on %s (\"%s\")" %
                 ("hsp_index", "hsp", "hsp_id"))
    conn.close()

    del waitting_hsp
    del waitting_subject
    del waitting_query
    module_log.info("Finished")
    del module_log.handlers[:]

    # module_log = logging_init("store_bls_in_sqlite", log_file)
    # module_log.info('received a call to "store_bls_in_sqlite"')
    #
    # # making a new sql database for store sequences
    # module_log.info('check the database for if have the tables already')
    # db_info = sc.all_database_stat(db_name)
    # prefix_matched_table = []
    # for table_name in db_info:
    #     if re.match('^%s.*' % table_name_prefix, table_name):
    #         prefix_matched_table.append(table_name)
    # if len(prefix_matched_table) == 0:
    #     module_log.info('need a new tables to store blast results')
    # elif len(prefix_matched_table) > 0:
    #     module_log.info('there are prefix matched tables in the database already, drop them')
    #     conn = sqlite3.connect(db_name)
    #     for i in prefix_matched_table:
    #         conn.execute("DROP TABLE %s" % i)
    #     conn.close()
    #
    # # loading fasta file and store to sqlite
    # module_log.info('loading blast results file and storing in sqlite')
    # record_list = []
    # table_id = 0
    # record_id = 0
    # output_dict = {}
    #
    # if outfmt == 6:
    #     bls_file_parser = outfmt6_read_big(bls_file, gzip_flag)
    # elif outfmt == 5:
    #     bls_file_parser = outfmt5_read_big(bls_file)
    # else:
    #     raise ValueError("unknown format")
    #
    # for query in bls_file_parser:
    #     hit_num = 0
    #     for subject in query.hit:
    #         hit_num = hit_num + 1
    #         if not hit_keep is None and hit_num > hit_keep:
    #             break
    #         hsp_num = 0
    #         for hsp in subject.hsp:
    #             hsp_num = hsp_num + 1
    #             if not hsp_keep is None and hsp_num > hsp_keep:
    #                 break
    #             query_short_name = query.short_qDef()
    #             query_name = query.qDef
    #             if fancy_name is True:
    #                 query_short_name, c_start, c_end = re.search(r'^(\S+):(\d+)-(\d+)$', query_short_name).groups()
    #                 q_start = int(c_start) + hsp.Hsp_query_from - 1
    #                 q_end = int(c_start) + hsp.Hsp_query_to - 1
    #             else:
    #                 q_start = hsp.Hsp_query_from
    #                 q_end = hsp.Hsp_query_to
    #             subject_short_name = subject.short_hDef()
    #             subject_name = subject.Hit_def
    #             record_id = record_id + 1
    #             record_list.append((
    #                 record_id, query_short_name, query_name, q_start, q_end, subject_short_name, subject_name,
    #                 hsp.Hsp_hit_from, hsp.Hsp_hit_to, hsp.Hsp_align_len, hsp.Hsp_gaps, hsp.Hsp_hit_frame,
    #                 hsp.Hsp_identity, hsp.Hsp_positive, hsp.Hsp_query_frame, hsp.Hsp_score, hsp.Hsp_bit_score,
    #                 hsp.Hsp_evalue, hsp.Hsp_hseq, hsp.Hsp_qseq, hsp.Hsp_midline))
    #
    #             if len(record_list) == table_max_rows:
    #                 table_name = table_name_prefix + "hsp_" + str(table_id)
    #                 table_name, index_name = add_hsp_record(record_list, db_name, table_name, outfmt5_columns)
    #                 output_dict[table_name] = {
    #                     "index": index_name,
    #                     "record_num": len(record_list)
    #                 }
    #                 module_log.info(
    #                     "\tAdd %d record in table: %s with index %s" % (len(record_list), table_name, index_name))
    #                 table_id = table_id + 1
    #                 record_list = []
    #
    # if len(record_list) > 0:
    #     table_name = table_name_prefix + "hsp_" + str(table_id)
    #     table_name, index_name = add_hsp_record(record_list, db_name, table_name, outfmt5_columns)
    #     output_dict[table_name] = {
    #         "index": index_name,
    #         "record_num": len(record_list)
    #     }
    #     module_log.info(
    #         "\tAdd %d record in table: %s with index %s" % (len(record_list), table_name, index_name))
    #     table_id = table_id + 1
    #     record_list = []
    #
    # module_log.info('loaded blast file and stored in sqlite ')
    #
    # del module_log.handlers[:]
    #
    # return output_dict


def sqlite_read(db_name):
    query_tmp = None

    for hsp_info in sqlite_select(db_name, 'hsp'):

        if query_tmp is None:
            new_query_flag = 1
            new_hit_flag = 1
        else:
            last_query_def = query_tmp.qDef
            last_hit_def = query_tmp.hit[-1].Hit_def
            if last_query_def != hsp_info[3]:
                new_query_flag = 1
                new_hit_flag = 1
            else:
                new_query_flag = 0
                if last_hit_def != hsp_info[4]:
                    new_hit_flag = 1
                else:
                    new_hit_flag = 0

        if new_query_flag:
            if query_tmp is not None:
                yield query_tmp

            query_num = hsp_info[1]
            query_info = sqlite_select(
                db_name, "query", key_name='query_num', value_tuple=(query_num,))[0]
            query_tmp = BlastQuery(
                query_info[0], query_info[1], query_info[2], query_info[3], [])

        if new_hit_flag:
            hit_num = hsp_info[2]
            hit_info = sqlite_select(
                db_name, "subject", key_name='hit_num', value_tuple=(hit_num,))[0]
            hit_tmp = BlastHit(
                query_tmp, hit_info[0], hit_info[2], hit_info[1], hit_info[4], hit_info[3], [])
            query_tmp.hit.append(hit_tmp)

        hsp_tmp = BlastHsp(query_tmp, hit_tmp, hsp_info[6], hsp_info[7], hsp_info[8], hsp_info[9], hsp_info[10],
                           hsp_info[11], hsp_info[12], hsp_info[13], hsp_info[14], hsp_info[15], hsp_info[
                               16], hsp_info[17], hsp_info[18], hsp_info[19], hsp_info[20], hsp_info[21],
                           hsp_info[22])

        query_tmp.hit[-1].hsp.append(hsp_tmp)

    if query_tmp is not None:
        yield query_tmp


# blast running

def blastn_running(query_file, db_file, blast_out_file, evalue, num_threads, realy_run=True, blast_dir="", outfmt=5,
                   task="blastn"):
    query_file = os.path.abspath(query_file)
    query_file_dir = os.path.dirname(query_file)

    db_file = os.path.abspath(db_file)
    db_file_dir = os.path.dirname(db_file)

    blast_out_file = os.path.abspath(blast_out_file)
    blast_out_file_dir = os.path.dirname(blast_out_file)

    # makeblastdb
    if (not ((os.path.exists(db_file + ".nhr") and os.path.exists(db_file + ".nin") and os.path.exists(
            db_file + ".nsq")))) and (not os.path.exists(db_file + ".nal")):
        cmd_string = blast_dir + "makeblastdb -in %s -dbtype nucl" % db_file
        cmd_run(cmd_string, cwd=db_file_dir, silence=True)

    # blastn
    cmd_string = blast_dir + "blastn -query %s -db %s -out %s -outfmt %d -task %s -evalue %s -num_threads %d" % (
        query_file, db_file, blast_out_file, outfmt, task, evalue, num_threads)

    if realy_run:
        cmd_run(cmd_string, cwd=blast_out_file_dir, silence=True)
    else:
        return cmd_string


def blastn_pair_running(query, hit, dir, keep_file=True):
    mkdir(dir, True)
    query_file = os.path.abspath(dir + "/" + uuid.uuid1().hex)
    subject_file = os.path.abspath(dir + "/" + uuid.uuid1().hex)
    blast_out_file = os.path.abspath(dir + "/" + uuid.uuid1().hex)
    with open(query_file, "w") as f:
        f.write(">" + query[0] + "\n" + query[1])
    with open(subject_file, "w") as f:
        f.write(">" + hit[0] + "\n" + hit[1])
    cmd_string = "makeblastdb -in %s -dbtype nucl" % subject_file
    cmd_run(cmd_string, cwd=dir, silence=True)
    cmd_string = "blastn -query %s -db %s -out %s -outfmt 5 -task blastn -evalue 1e-10 " % (
        query_file, subject_file, blast_out_file)
    cmd_run(cmd_string, cwd=dir, silence=True)

    if keep_file is False:
        cmd_string = "rm %s" % subject_file
        cmd_run(cmd_string, cwd=dir, silence=True)
        cmd_string = "rm %s.*" % subject_file
        cmd_run(cmd_string, cwd=dir, silence=True)
        os.remove(query_file)

    if outfmt5_complete(blast_out_file):
        output = outfmt5_read(blast_out_file)
        os.remove(blast_out_file)
        return output
    else:
        raise ValueError("Failed blast")


def evalue_to_wvalue(evalue):
    if evalue == 0.0:
        return 100
    else:
        return min(100, round(-log10(evalue) / 2))


def hit_CIP(blast_hit):
    """
    CIP (cumulative identity percentage) corresponds to the cumulative percent of sequence identity obtained for all the HSPs   
    """

    identity_list = []
    hsp_align_len = []
    for hsp in blast_hit.hsp:
        identity_list.append(hsp.Hsp_identical_site)
        hsp_align_len.append(hsp.Hsp_align_len)

    return sum(identity_list)/sum(hsp_align_len)

def hit_CALP(blast_hit):
    """
    CALP is the cumulative alignment length percentage. It represents the sum of the HSP lengths (AL) for all the HSPs divided by the length of the query sequence (CALP = AL/Query length)
    """

    
    hsp_align_len = []
    for hsp in blast_hit.hsp:
        hsp_align_len.append(hsp.Hsp_align_len)

    return sum(hsp_align_len)/blast_hit.query.qLen

def blastp_running(query_file, db_file, blast_out_file, evalue, num_threads, realy_run=True, blast_dir="", outfmt=5):
    query_file = os.path.abspath(query_file)
    query_file_dir = os.path.dirname(query_file)

    db_file = os.path.abspath(db_file)
    db_file_dir = os.path.dirname(db_file)

    blast_out_file = os.path.abspath(blast_out_file)
    blast_out_file_dir = os.path.dirname(blast_out_file)

    # makeblastdb
    if (not ((os.path.exists(db_file + ".phr") and os.path.exists(db_file + ".pin") and os.path.exists(
            db_file + ".psq")))):
        cmd_string = blast_dir + "makeblastdb -in %s -dbtype prot" % db_file
        cmd_run(cmd_string, cwd=db_file_dir, silence=True)

    # blastn
    cmd_string = blast_dir + "blastp -query %s -db %s -out %s -outfmt %d -evalue %s -num_threads %d" % (
        query_file, db_file, blast_out_file, outfmt, evalue, num_threads)

    if realy_run:
        cmd_run(cmd_string, cwd=blast_out_file_dir, silence=True)
    else:
        return cmd_string


def blastx_running(query_file, db_file, blast_out_file, evalue, num_threads, realy_run=True, blast_dir="", outfmt=5):
    query_file = os.path.abspath(query_file)
    query_file_dir = os.path.dirname(query_file)

    db_file = os.path.abspath(db_file)
    db_file_dir = os.path.dirname(db_file)

    blast_out_file = os.path.abspath(blast_out_file)
    blast_out_file_dir = os.path.dirname(blast_out_file)

    # makeblastdb
    if (not ((os.path.exists(db_file + ".phr") and os.path.exists(db_file + ".pin") and os.path.exists(
            db_file + ".psq")))):
        cmd_string = blast_dir + "makeblastdb -in %s -dbtype prot" % db_file
        cmd_run(cmd_string, cwd=db_file_dir, silence=True)

    # blastn
    cmd_string = blast_dir + "blastx -query %s -db %s -out %s -outfmt %d -evalue %s -num_threads %d" % (
        query_file, db_file, blast_out_file, outfmt, evalue, num_threads)

    if realy_run:
        cmd_run(cmd_string, cwd=blast_out_file_dir, silence=True)
    else:
        return cmd_string


def tblastn_running(query_file, db_file, blast_out_file, evalue, num_threads, realy_run=True, blast_dir="", outfmt=5):
    query_file = os.path.abspath(query_file)
    query_file_dir = os.path.dirname(query_file)

    db_file = os.path.abspath(db_file)
    db_file_dir = os.path.dirname(db_file)

    blast_out_file = os.path.abspath(blast_out_file)
    blast_out_file_dir = os.path.dirname(blast_out_file)

    # makeblastdb
    if (not ((os.path.exists(db_file + ".phr") and os.path.exists(db_file + ".pin") and os.path.exists(
            db_file + ".psq")))):
        cmd_string = blast_dir + "makeblastdb -in %s -dbtype prot" % db_file
        cmd_run(cmd_string, cwd=db_file_dir, silence=True)

    # blastn
    cmd_string = blast_dir + "tblastn -query %s -db %s -out %s -outfmt %d -evalue %s -num_threads %d" % (
        query_file, db_file, blast_out_file, outfmt, evalue, num_threads)

    if realy_run:
        cmd_run(cmd_string, cwd=blast_out_file_dir, silence=True)
    else:
        return cmd_string

# other


def NR_blast_annotation_extractor(nr_blast_results_file):
    blast_results = outfmt5_read(nr_blast_results_file)
    output_dict = {}
    for query_blast in blast_results:
        query_blast = blast_results[query_blast]
        query_name = query_blast.qDef
        query_name = query_name.split()[0]
        function_anno = []
        for hits in query_blast.hit:
            hits_def = hits.Hit_def
            # print(hits_def)
            if re.match('(.*)\[(.*)\]', hits_def):
                anno, speci = re.findall('(.*)\[(.*)\]', hits_def)[0]
                anno = re.sub(r'>.*', '', anno)
                anno = re.sub(r'\[.*', '', anno)
            else:
                continue
            if re.match(
                    r'Uncharacterized protein|uncharacterized protein|unknown|hypothetical protein|unnamed protein product|protein with unknown function|expressed protein|hCG\d{4,}|KIAA\d{4,}|predicted protein',
                    anno):
                continue
            if anno not in function_anno:
                function_anno.append(anno)
        output_dict[query_name] = function_anno
    return output_dict


def blast_plot(ax, hit, q_name, q_start, q_end, s_name, s_start, s_end):
    ax.set_xlim(q_start, q_end)
    ax.set_ylim(s_start, s_end)
    ax.set_title('blast plot')
    ax.set_xlabel(q_name)
    ax.set_ylabel(s_name)

    for hsp in hit.hsp:
        if not section((hsp.Hsp_query_from, hsp.Hsp_query_to), (q_start, q_end), just_judgement=True):
            continue

        if not section((hsp.Hsp_hit_from, hsp.Hsp_hit_to), (s_start, s_end), just_judgement=True):
            continue

        #     print((hsp.Hsp_query_from,hsp.Hsp_hit_from),(hsp.Hsp_query_to,hsp.Hsp_hit_to))

        ax.plot((hsp.Hsp_query_from, hsp.Hsp_query_to),
                (hsp.Hsp_hit_from, hsp.Hsp_hit_to), marker='.', c='k')


def BBH_call(bls_file1, bls_file2):
    """
    bidirectional best hit method
    """
    bls1_dict = outfmt6_read(bls_file1)
    bls2_dict = outfmt6_read(bls_file2)

    BBH_pair_list = []
    for q_id in bls1_dict:
        s_id = bls1_dict[q_id].hit[0].Hit_id
        if s_id in bls2_dict and q_id == bls2_dict[s_id].hit[0].Hit_id:
            BBH_pair_list.append((q_id, s_id))

    only_q1 = list(set([i for i in bls1_dict]) - set([i[0]
                                                      for i in BBH_pair_list]))
    only_q2 = list(set([i for i in bls2_dict]) - set([i[1]
                                                      for i in BBH_pair_list]))

    return BBH_pair_list, only_q1, only_q2


if __name__ == '__main__':
    """
    file = "C006N.fa.vs.ip"
    bls_dir = outfmt5_read(file)

    file2 = "/share/home/xuyuxing/Work/cuscuta/HGT/blast/bls/GCF_000001215.4/10.seq.bls"
    bls_dir2 = outfmt5_read(file2)
    """

    bls_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/WorkingDirectory/Blast0_1.txt.gz'
    db_name = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/WorkingDirectory/test2.db'

    blast_to_sqlite(db_name, bls_file, gzip_flag=True)

    query_tmp = next(sqlite_read(db_name))

    # plot
    import matplotlib.pyplot as plt

    hit_used = [hit for hit in query_tmp.hit if hit.Hit_id ==
                'G001N_fragment_2'][0]

    q_start = 1
    q_end = 35304
    s_start = 20277869
    s_end = 20321356

    fig, ax = plt.subplots(1, 1)

    blast_plot(ax, hit_used, 'MF163256.1', q_start - 3000, q_end + 3000, 'G001N_fragment_2', s_start - 3000,
               s_end + 3000)

    plt.show()


    ###
    bls_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Oro/blat/Trinity.bls'
    query_file = '/lustre/home/xuyuxing/Database/Orobanche/annotation/trinity/trinity_output/Trinity.fasta'

    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx

    seq_dict = read_fasta_by_faidx(query_file)
    len_dict = {i:seq_dict[i].len() for i in seq_dict}

    for query in outfmt6_read_big(bls_file):
        query.qLen = len_dict[query.qID]
        for hit in query.hit:
            print(query.qID,hit.Hit_id,hit_CIP(hit),hit_CALP(hit))