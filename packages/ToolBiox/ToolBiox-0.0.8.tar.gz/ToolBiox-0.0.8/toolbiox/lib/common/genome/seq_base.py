import re
import gzip
import numpy as np
import os
import time
import random
import math
from Bio import Seq, SeqIO
from collections import OrderedDict, Counter
from pyfaidx import Fasta
from toolbiox.lib.common.util import logging_init
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.os import remove_file_name_suffix, cmd_run
# from toolbiox.lib.common.genome.genome_feature2 import cds_judgment


# tools for seq as string

def slice_scaffold_by_N(sequence, scaffold_maker="N"):
    """
    some scaffold sequence have many N in the seq, I can find the start and end for each Non-N seq, e.g. contig. I will
    return a list which have tuple(start,end) 0-base
    """
    subseqs = sequence.split(scaffold_maker)
    sub_seq_slice = []
    pointer = 0
    for i in subseqs:
        if len(i) == 0:
            pointer = pointer + 1
            continue
        sub_seq_slice.append((pointer, pointer + len(i)))
        pointer = pointer + len(i) + 1
    return sub_seq_slice


def contig_cutting(sequence, step, length, pointer_start=1):
    """
    cutting a sequence as windows, you can give me step and window length. I will return a generator which every one is
    start point and window sequence. pointer_start is the begin pointer it just for ID, will not change sequence cutting
    """
    seq_len = len(sequence)
    sub_seq_dict = {}
    for i in range(pointer_start - 1, seq_len, step):
        if seq_len - i > length:
            sub_seq = sequence[i:i + length]
            yield (pointer_start, sub_seq)
            sub_seq_dict[pointer_start] = sub_seq
        else:
            sub_seq = sequence[i:seq_len]
            yield (pointer_start, sub_seq)
            break
        pointer_start = pointer_start + step


def scaffold_cutting(sequence, step=500, length=1000, Consider_scaffold=True, shift_start=0):
    """
    cutting a sequence as windows, you can give me step and window length. I will return a generator which every one is
    start point and window sequence. pointer_start is the begin pointer it just for ID, will not change sequence cutting
    If the sequence is scaffold, I can split scaffold by N firstly, and get contig to make windows, the pointer will follow
    scaffold which based on 1
    """
    if Consider_scaffold is True:
        sub_seq_slice = slice_scaffold_by_N(sequence)
        # output_dict = {}
        for start, end in sub_seq_slice:
            sub_seq = sequence[start:end]
            for pointer, sub_sub_seq in contig_cutting(sub_seq, step, length, start + 1):
                yield (pointer, sub_sub_seq)
                # output_dict[pointer] = sub_sub_seq
    else:
        if shift_start != 0:
            # print(shift_start)
            yield (1, sequence[1 - 1:shift_start])

        # output_dict = {}
        for pointer, sub_seq in contig_cutting(sequence, step, length, shift_start + 1):
            yield (pointer, sub_seq)
            # output_dict[pointer] = sub_seq

    # return output_dict


def reverse_complement(seq, RNA=False):
    """
    #>>> seq = "TCGGinsGCCC"
    #>>> print "Reverse Complement:"
    #>>> print(reverse_complement(seq))
    #GGGCinsCCGA
    """
    alt_map = {'ins': '0'}
    if RNA:
        complement = {'A': 'U', 'C': 'G', 'G': 'C', 'U': 'A'}
    else:
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    # for k, v in alt_map.iteritems():
    for k, v in alt_map.items():
        seq = seq.replace(k, v)
    bases = list(seq)
    bases = reversed([complement.get(base, base) for base in bases])
    bases = ''.join(bases)
    # for k, v in alt_map.iteritems():
    for k, v in alt_map.items():
        bases = bases.replace(v, k)
    return bases


def reverse_seq(seq):
    """just reverse"""
    return "".join(reversed(seq))


def complement_seq(seq):
    """just complement"""
    if 'U' in seq:
        complement = {'A': 'U', 'C': 'G', 'G': 'C', 'U': 'A'}
    else:
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    bases = list(seq)
    bases = [complement.get(base, base) for base in bases]
    bases = ''.join(bases)
    return bases


def sub_seq(seq, site_start, site_end, strand, RNA):
    """get sub set of a seq"""
    start = min(site_start, site_end)
    end = max(site_start, site_end)
    sub_seq_out = seq[start - 1:end]

    if RNA is True:
        sub_seq_out = sub_seq_out.replace("T", "U")
    if strand == "-":
        sub_seq_out = reverse_complement(sub_seq_out, RNA)

    return sub_seq_out


def iter_kmers(seq, k, overlap=True):
    """
    from skbio.Sequence.iter_kmers
    """
    if k < 1:
        raise ValueError("k must be greater than 0.")

    if overlap:
        step = 1
        count = len(seq) - k + 1
    else:
        step = k
        count = len(seq) // k

    seq_bytes = np.array([ord(i) for i in seq], dtype='uint8')

    # Optimized path when positional metadata doesn't need slicing.
    kmers = np.lib.stride_tricks.as_strided(
        seq_bytes, shape=(k, count), strides=(1, step)).T

    for s in kmers:
        yield s


def kmer_frequencies(seq, k, overlap=True, relative=False):
    """
    from skbio.Sequence.kmer_frequencies
    """
    kmers = iter_kmers(seq, k, overlap=overlap)
    freqs = dict(Counter((str(seq) for seq in kmers)))

    if relative:
        if overlap:
            num_kmers = len(seq) - k + 1
        else:
            num_kmers = len(seq) // k

        relative_freqs = {}
        for kmer, count in freqs.items():
            relative_freqs[kmer] = count / num_kmers
        freqs = relative_freqs

    return freqs


def sequence_entropy(sequence_input, kmer):
    freqs = kmer_frequencies(sequence_input, kmer,
                             overlap=False, relative=False)
    t_num = sum([freqs[i] for i in freqs])

    entropy = 0
    for i in freqs:
        p = freqs[i]/t_num
        entropy = entropy - (p * math.log(p, 2))

    return entropy


def random_sequence(seq_char, length, random_seed=None):
    """
    get random sequence
    :param seq_char: for DNA, you can give "ATCG"
    """
    random.seed(random_seed)
    sa = []
    for i in range(length):
        sa.append(random.choice(seq_char))
    salt = ''.join(sa)
    return salt


def get_seq_index_ignore_gap(give_site, seq_with_gap, seq_start=1, gap_chr='-'):
    """
    seq_with_gap = "------------ATGC---CAGTCA---ACG-GCATGCTA"
    give_site = 5
    seq_start = 1
    gap_chr = '-'

    give a seq with gap, and a site number, return index in gap seq
    """
    go_on_flag = True
    round_use_range = (0, 0)
    add_length = give_site - seq_start + 1
    round_true_site = 0
    while (go_on_flag):
        round_use_range = (
            round_use_range[1] + 1, round_use_range[1] + add_length)
        round_seq = seq_with_gap[round_use_range[0] - 1:round_use_range[1]]
        round_true_site = round_true_site + \
            len(round_seq) - round_seq.count(gap_chr)
        add_length = round_seq.count(gap_chr)
        print(round_use_range, round_seq, round_true_site, add_length)

        if add_length == 0:
            go_on_flag = False

    return round_use_range[1]


# tools for fasta file

class BioSeq(object):
    def __init__(self, seq, seqname=None, seq_type='nucl'):
        self.seqname = seqname
        self.seq = seq
        self.seq_type = seq_type

    nucl = ["A", "T", "C", "G", "U"]
    nucl_degenerate = ["M", "S", "W", "B", "D", "R", "H", "Y", "V", "K"]
    any_nucl = ["N"]
    prot = ["A", "P", "B", "Q", "C", "R", "D", "S", "E", "T", "F", "U", "G", "V", "H", "W", "I", "Y", "K", "Z", "L",
            "M", "N"]
    any_prot = ["X"]
    stop_site = ["*"]
    gap_site = ['-']

    def __str__(self):
        return self.seq

    def seqs_length(self):
        return len(self.seq)

    def seq_clean(self, degenerate_sites_allowed=False, gap_allowed=False,
                  translation_stop_allowed=False, replace_flag=True):
        # make code
        if self.seq_type == 'nucl':
            seq_type_flag = 0b0001
        elif self.seq_type == 'prot':
            seq_type_flag = 0b0000

        dsa_flag = degenerate_sites_allowed
        if dsa_flag:
            dsa_flag = 0b0010

        ga_flag = gap_allowed
        if ga_flag:
            ga_flag = 0b0100

        tsa_flag = translation_stop_allowed
        if tsa_flag:
            tsa_flag = 0b1000

        bit_field = seq_type_flag + dsa_flag + ga_flag + tsa_flag

        if bit_field == 0b0111:
            all_allowed = self.nucl + self.any_nucl + self.nucl_degenerate + self.gap_site
            safe_remove = []
            safe_replace = self.any_nucl
        elif bit_field == 0b0011:
            all_allowed = self.nucl + self.any_nucl + self.nucl_degenerate
            safe_remove = self.gap_site
            safe_replace = self.any_nucl
        elif bit_field == 0b0101:
            all_allowed = self.nucl + self.any_nucl + self.gap_site
            safe_remove = []
            safe_replace = self.any_nucl
        elif bit_field == 0b0001:
            all_allowed = self.nucl + self.any_nucl
            safe_remove = self.gap_site
            safe_replace = self.any_nucl
        elif bit_field == 0b0000:
            all_allowed = self.prot + self.any_prot
            safe_remove = self.gap_site + self.stop_site
            safe_replace = self.any_prot
        elif bit_field == 0b0100:
            all_allowed = self.prot + self.any_prot + self.gap_site
            safe_remove = self.stop_site
            safe_replace = self.any_prot
        elif bit_field == 0b1100:
            all_allowed = self.prot + self.any_prot + self.gap_site + self.stop_site
            safe_remove = []
            safe_replace = self.any_prot
        elif bit_field == 0b1000:
            all_allowed = self.prot + self.any_prot + self.stop_site
            safe_remove = self.gap_site
            safe_replace = self.any_prot
        else:
            raise ValueError("Bad input flag")

        new_seq = self.seq
        char_site = set(new_seq)
        bad_flag = False
        for i in char_site:
            if i in all_allowed:
                continue
            elif i in safe_remove:
                if i == "*":
                    new_seq = re.sub("\*", "", new_seq)
                else:
                    new_seq = re.sub(i, "", new_seq)
            else:
                if replace_flag:
                    if i == "*":
                        new_seq = re.sub("\*", "", new_seq)
                    else:
                        new_seq = re.sub(i, safe_replace[0], new_seq)
                bad_flag = True

        if replace_flag:
            self.seq = new_seq
        else:
            if bad_flag:
                return False
            else:
                return True

    def seqs_upper(self):
        self.seq = self.seq.upper()

    def seqs_lower(self):
        self.seq = self.seq.lower()

    def no_wrap(self):
        self.seq = re.sub("\n", "", self.seq)

    def wrap(self, line_length=75):
        raw_seq = str(self.seq)
        raw_seq = re.sub("\n", "", raw_seq)
        new_seq = ""

        for j in (raw_seq[x: x + line_length] for x in range(0, len(raw_seq), line_length)):
            new_seq += j + "\n"

        self.seq = new_seq

        return new_seq

    def sub(self, site_start, site_end, strand, RNA):
        return sub_seq(self.seq, site_start, site_end, strand, RNA)

    def RNA(self):
        return self.seq.replace("T", "U")

    def reverse(self):
        return reverse_seq(self.seq)

    def complement(self):
        return complement_seq(self.seq)

    def reverse_complement(self):
        return complement_seq(reverse_seq(self.seq))

    def write_to_file(self, output_file, wrap_length=75):
        raw_seq = str(self.seq)
        with open(output_file, 'a') as f:
            f.write(">%s\n" % self.seqname)
            for x in range(0, len(raw_seq), wrap_length):
                # print(self.seqname, x)
                i = raw_seq[x: x + wrap_length]
                f.write(i + "\n")

    # def write_to_file(self, output_file, wrap_length=75):
    #     print(self.seqname, len(self.seq))
    #     self.wrap(line_length=wrap_length)
    #     print('ok wrap')
    #     # self.seq = re.sub("\n", "", self.seq)
    #     with open(output_file, 'a') as f:
    #         f.write(">%s\n%s" % (self.seqname, self.seq))


class FastaRecord(BioSeq):
    def __init__(self, seqname, seq=None, faidx=None):
        super(FastaRecord, self).__init__(seq)
        self.seqname = seqname
        self.faidx = faidx
        self.qualifiers = re.findall('\[([^\[\]]+)=([^\[\]]+)\]', seqname)

    def seqname_short(self):
        name_short = re.search('^(\S+)', self.seqname).group(1)
        return name_short

    @property
    def seq(self):
        if self.faidx is not None:
            return str(self.faidx)
        else:
            return self._seq

    @seq.setter
    def seq(self, value):
        self._seq = value

    def read_seq_to_mem(self):
        self._seq = str(self.faidx)

    def sub(self, site_start, site_end, strand, RNA):
        if self.faidx is not None:
            output = str(self.faidx[site_start - 1:site_end])
            if RNA is True:
                output = output.replace("T", "U")
            if strand == "-":
                output = reverse_complement(output, RNA)
            return output
        else:
            return sub_seq(self.seq, site_start, site_end, strand, RNA)

    def len(self):
        if hasattr(self, 'faidx'):
            return len(self.faidx)
        else:
            return len(self.seq)

    def get_GC_ratio(self):
        gc_now = (self.seq.count('C') + self.seq.count('G') +
                  self.seq.count('c') + self.seq.count('g'))/self.len()
        return gc_now


class FastqRecord(FastaRecord):
    def __init__(self, seqname, seq, quality):
        super(FastqRecord, self).__init__(seqname, seq)
        self.quality = quality


def read_fastq_big(file_name1, file_name2=None, gzip_flag=False):
    file_handle = []
    if gzip_flag is False:
        f1 = open(file_name1, 'r')
    else:
        f1 = gzip.open(file_name1, 'rt')
    file_handle.append(f1)
    if not file_name2 is None:
        if gzip_flag is False:
            f2 = open(file_name2, 'r')
        else:
            f2 = gzip.open(file_name2, 'rt')
        file_handle.append(f2)

    done = 0
    num = 0
    seqname = []
    seqs = []
    seqquality = []
    while not done:
        num = num + 1
        for f in file_handle:
            line_tmp = re.sub(r'\n', '', f.readline())

            if line_tmp == "":
                done = 1
                continue

            if num % 4 == 1:
                line_tmp = re.match(r'@(.*)', line_tmp).groups()[0]
                if re.match(r'^(.*)/1$', line_tmp):
                    line_tmp = re.match(r'^(.*)/1$', line_tmp).groups()[0]
                if re.match(r'^(.*)/2$', line_tmp):
                    line_tmp = re.match(r'^(.*)/2$', line_tmp).groups()[0]
                seqname.append(line_tmp)
            elif num % 4 == 2:
                seqs.append(line_tmp)
            elif num % 4 == 0:
                seqquality.append(line_tmp)

        if num % 4 == 0:
            if not file_name2 is None:
                f1_record = FastqRecord(seqname[0], seqs[0], seqquality[0])
                f2_record = FastqRecord(seqname[1], seqs[1], seqquality[1])
                yield (f1_record, f2_record)
            else:
                f1_record = FastqRecord(seqname[0], seqs[0], seqquality[0])
                yield (f1_record,)
            seqname = []
            seqs = []
            seqquality = []

    for f in file_handle:
        f.close()


def read_fasta(file_name, upper=True, filter_speci_char=False, gzip_flag=False, full_name=False):
    seqdict = {}
    seqname_list = []
    if gzip_flag is False:
        f = open(file_name, 'r')
    else:
        f = gzip.open(file_name, 'rt')
    all_text = f.read()
    all_text = re.sub('\r\n', '\n', all_text)
    # info = string.split(all_text, '>') python2
    info = all_text.split('\n>')
    while '' in info:
        info.remove('')
    for i in info:
        # seq = string.split(i, '\n', 1) python2
        seq = i.split('\n', 1)
        seq[1] = re.sub(r'\n', '', seq[1])
        seq[1] = re.sub(r' ', '', seq[1])
        seqname = seq[0]
        seqname = re.sub(r'^>', '', seqname)
        if filter_speci_char is True:
            seqname = re.search('^(\S+)', seqname).group(1)
            seqname = re.sub(r'[^A-Za-z0-9]', '_', seqname)
        name_short = re.search('^(\S+)', seqname).group(1)
        seqs = seq[1]
        if full_name:
            seqdict[seqname] = FastaRecord(seqname, seqs)
        else:
            seqdict[name_short] = FastaRecord(seqname, seqs)
        if upper is True:
            seqdict[name_short].seqs_upper()
        seqname_list.append(seqname)
    f.close()
    return seqdict, seqname_list


def read_fasta_big(file_name, upper=True, filter_speci_char=False, gzip_flag=False, log_file=None):
    module_log = logging_init("read_fasta_big", log_file)
    module_log.info('received a call to "lib.file_parser.read_fasta_big"')

    last_record_name = ""
    last_record_seq = ""
    top = 1

    if gzip_flag is False:
        f = open(file_name, 'r')
    else:
        f = gzip.open(file_name, 'rt')

    for each_line in f:
        each_line = re.sub(r'\n', '', each_line)
        match = re.match(r'^>(.*)', each_line)
        if match:
            seqname = match.group(1)
            # print(seqname)
            # short_name = re.search('^(\S+)', seqname).group(1)
            if top == 1:
                top = 2
                last_record_name = seqname
                if filter_speci_char is True:
                    last_record_name = re.search('^(\S+)', seqname).group(1)
                    last_record_name = re.sub(
                        r'[^A-Za-z0-9]', '_', last_record_name)
                last_record_seq = ""
                continue
            else:
                new_record = FastaRecord(last_record_name, last_record_seq)

                last_record_name = seqname
                if filter_speci_char is True:
                    last_record_name = re.search('^(\S+)', seqname).group(1)
                    last_record_name = re.sub(
                        r'[^A-Za-z0-9]', '_', last_record_name)
                last_record_seq = ""

                if upper is True:
                    new_record.seqs_upper()
                yield new_record

        else:
            each_line = re.sub(r'\n', '', each_line)
            last_record_seq = last_record_seq + each_line

    f.close()

    new_record = FastaRecord(last_record_name, last_record_seq)
    if upper is True:
        new_record.seqs_upper()
    yield new_record

    del module_log.handlers[:]


def faidx2xyx(pyfaidx_record, write_seq_mem):
    try:
        seq_name = pyfaidx_record.long_name
    except:
        seq_name = pyfaidx_record.name

    if write_seq_mem:
        return FastaRecord(seq_name, str(pyfaidx_record), pyfaidx_record)
    else:
        return FastaRecord(seq_name, None, pyfaidx_record)


def bioidx2xyx(Biopython_SeqRecord, write_seq_mem):
    try:
        seq_name = Biopython_SeqRecord.description
    except:
        seq_name = Biopython_SeqRecord.id

    if write_seq_mem:
        return FastaRecord(seq_name, str(Biopython_SeqRecord.seq), Biopython_SeqRecord)
    else:
        return FastaRecord(seq_name, None, Biopython_SeqRecord)


def wrap_fasta_file(file_name, wrap_file_name, wrap_length=75):
    with open(wrap_file_name, 'w') as w:
        for record_tmp in read_fasta_big(file_name, upper=False):
            w.write(">%s\n" % record_tmp.seqname)
            for i in (record_tmp.seq[x: x + wrap_length] for x in range(0, len(record_tmp.seq), wrap_length)):
                w.write("%s\n" % i)


def read_fasta_by_faidx(file_name, write_seq_mem=False, force_wrap_file=False):
    # if file_name.split(".")[-1] == 'gz':
    #     cmd_run("gzip %s" % file_name, slience=True)
    #     file_name = remove_file_name_suffix(file_name, 1)

    try:
        output_dict = OrderedDict()
        for i in Fasta(file_name):
            output_dict[i.name] = faidx2xyx(i, write_seq_mem)
        return output_dict
    except:
        try:
            cmd_run("samtools faidx %s" % file_name)
            output_dict = OrderedDict()
            for i in Fasta(file_name):
                output_dict[i.name] = faidx2xyx(i, write_seq_mem)
            return output_dict
        except:
            raise EnvironmentError("fasta file not suit for pyfaidx")

    #
    #
    # wrap_file_name = remove_file_name_suffix(file_name, 1) + ".pyfaidx.fasta"
    # if force_wrap_file:
    #     wrap_fasta_file(file_name, wrap_file_name, 75)
    #     try:
    #         return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #     except:
    #         raise EnvironmentError("fasta file not suit for pyfaidx")
    # else:
    #     if os.path.exists(wrap_file_name):
    #         try:
    #             return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #         except:
    #             wrap_fasta_file(file_name, wrap_file_name, 75)
    #             try:
    #                 return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #             except:
    #                 raise EnvironmentError("fasta file not suit for pyfaidx")
    #     else:
    #         try:
    #             return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(file_name)}
    #         except:
    #             wrap_fasta_file(file_name, wrap_file_name, 75)
    #             try:
    #                 return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #             except:
    #                 raise EnvironmentError("fasta file not suit for pyfaidx")
    #


def read_fasta_by_bioidx(file_name, write_seq_mem=False):
    # if file_name.split(".")[-1] == 'gz':
    #     cmd_run("gzip %s" % file_name, slience=True)
    #     file_name = remove_file_name_suffix(file_name, 1)

    index_file = file_name + ".idx"

    bioidx_dict = SeqIO.index_db(index_file, file_name, 'fasta')
    output_dict = {}
    for i in bioidx_dict:
        try:
            seq_name = bioidx_dict[i].description
        except:
            seq_name = bioidx_dict[i].id

        output_dict[seq_name] = bioidx2xyx(bioidx_dict[i], write_seq_mem)

    return bioidx_dict


def read_fasta_to_sqlite(fasta_file_name, db_name, gzip_flag, log_file=None):
    module_log = logging_init("read_fasta_to_sqlite", log_file)
    module_log.info(
        'received a call to "lib.file_parser.read_fasta_to_sqlite"')

    # making a new sql database for store sequences'
    module_log.info('making a new sql database for store sequences')
    table_columns_dict = {
        "record": ["id", "seqname_short", "seqname", "seqs", "seqslen"]
    }
    sc.init_sql_db_many_table(db_name, table_columns_dict)
    module_log.info('made a new sql database for store sequences')

    # loading fasta file and store to sqlite
    module_log.info('loading fasta file and storing in sqlite')
    start_time = time.time()
    num = 0
    record_tmp_dict = []
    for record in read_fasta_big(fasta_file_name, upper=False, filter_speci_char=False, gzip_flag=gzip_flag):
        record_tmp_dict.append((num, record.seqname_short(
        ), record.seqname, record.seq, record.seqs_length()))
        num = num + 1

        if num % 10000 == 0:
            sc.sqlite_write(record_tmp_dict, db_name, "record",
                            table_columns_dict["record"])
            record_tmp_dict = []

        round_time = time.time()
        if round_time - start_time > 10:
            module_log.info("\tparsed: %d" % (num))
            start_time = round_time

    if len(record_tmp_dict) > 0:
        sc.sqlite_write(record_tmp_dict, db_name, "record",
                        table_columns_dict["record"])
        record_tmp_dict = []
        module_log.info("\tparsed: %d" % (num))

    module_log.info('loaded fasta file and stored in sqlite ')
    del module_log.handlers[:]


def extract_seq_from_sqlite(seq_name_list, db_name):
    records_info = sc.sqlite_select(
        db_name, 'record', key_name="seqname_short", value_tuple=seq_name_list)

    record_dict = {}
    for i in records_info:
        record_dict[i[1]] = FastaRecord(i[2], i[3])

    return record_dict


def split_fasta(file_or_dict_name, split_num, output_dir, file=1):
    if file == 1:
        seqdict, seqname_list = read_fasta(file_or_dict_name)
    else:
        seqdict, seqname_list = file_or_dict_name
    num = 0
    for i in (seqname_list[x: x + split_num] for x in range(0, len(seqname_list), split_num)):
        num = num + 1
        with open(output_dir + "/" + str(num) + ".seq", 'w') as f:
            for seq in i:
                seq_rec = seqdict[seq]
                seq_rec.wrap()
                f.write(">" + seq_rec.seqname + "\n" + seq_rec.seq)


def extract_seq_to_fasta(path_file_name, list1, fasta_dict, gzip_flag=False, silence=True):
    num = 0
    if gzip_flag is True:
        OUT = gzip.open(path_file_name, 'wt', newline='')
    else:
        OUT = open(path_file_name, 'w', newline='')
    for i in list1:
        if i in fasta_dict:
            fasta_dict[i].wrap()
            seq_now = fasta_dict[i].seqs
            printer = ">" + i + "\n" + seq_now + "\n"
            OUT.write(printer)
            num = num + 1
    OUT.close()
    if not silence:
        return num


def rename_seq_to_fasta(path_file_name, name_map_list, fasta_dict, gzip_flag=False, silence=True):
    num = 0
    if gzip_flag is True:
        OUT = gzip.open(path_file_name, 'wt', newline='')
    else:
        OUT = open(path_file_name, 'w', newline='')
    for raw_name, new_name in name_map_list:
        if raw_name in fasta_dict:
            fasta_dict[raw_name].wrap()
            seq_now = fasta_dict[raw_name].seq
            seq_now = seq_now.replace("*", "")
            # printer = ">" + new_name + "\n" + seq_now + "\n"
            printer = ">" + new_name + "\n" + seq_now
            OUT.write(printer)
            num = num + 1
    OUT.close()
    if not silence:
        return num


def sub_fasta(genome_file, seq_name, site_start, site_end, strand="+", RNA=False):
    target_record = None
    for i in read_fasta_big(genome_file):
        if seq_name == i.seqname_short():
            target_record = i
            break

    if target_record:
        sub_seq_out = sub_seq(
            target_record.seq, site_start, site_end, strand, RNA)

        start = min(site_start, site_end)
        end = max(site_start, site_end)

        sub_seq_name = "%s:%d-%d:%s" % (seq_name, start, end, strand)
        record = FastaRecord(sub_seq_name, sub_seq_out)
        return record
    else:
        raise NameError('No target seq')


def sub_fasta_many(genome_file, bed_dict):
    """
    :param genome_file:
    :param bed_dict: a dict whoes keys are subseq names and values should be tuple as (seq_name, site_start, site_end, strand="+", RNA=False)
    :return:
    """
    bed_dict_seqname = OrderedDict()
    for sub_seq_name in bed_dict:
        seq_name, site_start, site_end, strand, RNA = bed_dict[sub_seq_name]
        if not seq_name in bed_dict_seqname:
            bed_dict_seqname[seq_name] = []
        bed_dict_seqname[seq_name].append(sub_seq_name)

    output_dict = OrderedDict()
    for record in read_fasta_big(genome_file):
        if not record.seqname_short() in bed_dict_seqname:
            continue
        for sub_seq_name in bed_dict_seqname[record.seqname_short()]:
            seq_name, site_start, site_end, strand, RNA = bed_dict[sub_seq_name]
            start = min(int(site_start), int(site_end))
            end = max(int(site_start), int(site_end))
            sub_seq = record.seq[start - 1:end]

            if strand == "-":
                sub_seq = reverse_complement(sub_seq)
            if RNA is True:
                sub_seq = sub_seq.replace("T", "U")

            output_dict[sub_seq_name] = FastaRecord(sub_seq_name, sub_seq)

    return output_dict


def aa_aln_to_cds_aln(aa_aln, cds_fasta, cds_aln):
    cmd_string = "treebest backtrans "+aa_aln+" "+cds_fasta+" > "+cds_aln
    cmd_run(cmd_string, silence=True)


# normal seq id parse

def fancy_name_parse(input_string):
    contig_name, c_start, c_end = re.search(
        r'^(\S+):(\d+)-(\d+)$', input_string).groups()
    return contig_name, int(c_start), int(c_end)


def fancy_name_get(contig_name, c_start, c_end):
    return "%s:%s-%s" % (contig_name, str(c_start), str(c_end))


# database seq parser tools

def record_qulifiers_dict(qualifiers):
    """
    this function work for NCBI fasta id
    :param qualifiers:
    :return:
    """
    output = {}
    for i in qualifiers:
        i = re.sub(r'\[', '', i)
        i = re.sub(r'\]', '', i)
        try:
            key_tmp, value_tmp = i.split("=")
            output[key_tmp] = value_tmp
        except:
            pass
    return output


def NCBI_id_parse(nt_file, gzip_flag=False):
    """
    # gene id in ncbi gff hard to link to pt cds fasta id, so we need change to locus_tag or Dbxref and so on

    parse NCBI seq fasta file, to locus_tag or Dbxref as seq ID
    :param nt_file:
    :param gzip_flag:
    :return:
    """

    seqdict, seqname_list = read_fasta(nt_file, gzip_flag=gzip_flag)
    qualifiers_dict = {}
    seqdict_new = {}
    for i in seqdict:
        record = seqdict[i]
        qualifiers = re.findall(r'\[\S+\]', record.seqname)
        qualifiers = record_qulifiers_dict(qualifiers)
        if 'pseudo' in qualifiers and qualifiers['pseudo'] == 'true':
            continue

        prot_id = re.findall(r'^lcl\|(\S+)_prot_(\S+)$', i)
        cds_id = re.findall(r'^lcl\|(\S+)_cds_(\S+)$', i)

        if len(prot_id) > 0:
            contig_id = prot_id[0][0]
        elif len(cds_id) > 0:
            contig_id = cds_id[0][0]
        else:
            raise ValueError("new type fasta? %s" % nt_file)

        qualifiers['raw_id'] = i
        qualifiers['contig'] = contig_id

        if (contig_id, qualifiers['location']) in qualifiers_dict:
            if not seqdict_new[(contig_id, qualifiers['location'])].seq == record.seq:
                # I find in GCF_000001215, gene CG33301 have two protein from same CDS, but one AA to be *
                # if len(re.sub('\*','',seqdict_new[(contig_id, qualifiers['location'])].seq)) < len(re.sub('\*','',record.seq)):
                #     seqdict_new[(contig_id, qualifiers['location'])] = record
                #
                if contig_id == 'NT_033779.5' and qualifiers[
                        'location'] == 'join(10049616..10050642,10050702..10050898)':
                    if len(re.sub('\*', '', seqdict_new[(contig_id, qualifiers['location'])].seq)) < len(
                            re.sub('\*', '', record.seq)):
                        seqdict_new[(
                            contig_id, qualifiers['location'])] = record
                    else:
                        continue
                else:
                    raise ValueError("same seq id but diff seq: %s %s" % (
                        record.seqname, nt_file))
        else:
            qualifiers_dict[(contig_id, qualifiers['location'])] = qualifiers
            record.seqname = i
            seqdict_new[(contig_id, qualifiers['location'])] = record

        # """use protein_id as gene id"""
        # #
        # # if 'protein_id' in qualifiers:
        # #     if qualifiers['protein_id'] in qualifiers_dict:
        # #         del qualifiers_dict[qualifiers['protein_id']]
        # #         del seqdict_new[qualifiers['protein_id']]
        # #     else:
        # #         qualifiers_dict[qualifiers['protein_id']] = qualifiers
        # #         record.seqname = qualifiers['protein_id']
        # #         seqdict_new[qualifiers['protein_id']] = record
        #
        # if qualifiers[renew_id_flag] in qualifiers_dict:
        #     if not seqdict_new[qualifiers[renew_id_flag]].seq == record.seq:
        #         raise ValueError("same seq id but diff seq: %s %s" % (record.seqname, nt_file))
        # else:
        #     qualifiers_dict[qualifiers[renew_id_flag]] = qualifiers
        #     record.seqname = qualifiers[renew_id_flag]
        #     seqdict_new[qualifiers[renew_id_flag]] = record
        #
        # """go back to locus_tag"""
        #
        # # if 'locus_tag' in qualifiers:
        # #     qualifiers_dict[qualifiers['locus_tag']] = qualifiers
        # #     record.seqname = qualifiers['locus_tag']
        # #     seqdict_new[qualifiers['locus_tag']] = record

    return qualifiers_dict, seqdict_new


def JGI_id_parse(file, gzip_flag=False):
    seqdict, seqname_list = read_fasta(file, gzip_flag=gzip_flag)
    qualifiers_dict = {}
    seqdict_new = {}
    for i in seqdict:
        record = seqdict[i]
        qualifiers = record.seqname.split("|", 3)
        spec_tag = qualifiers[1]
        seq_id = qualifiers[2]
        seq_name = qualifiers[3]
        seqdict_new[seq_name] = record
        qualifiers_dict[seq_name] = {}
        qualifiers_dict[seq_name]["seq_id"] = seq_id
        qualifiers_dict[seq_name]["spec_tag"] = spec_tag
        qualifiers_dict[seq_name]["seq_name"] = seq_name
    return qualifiers_dict, seqdict_new


def BIG_id_parse(nt_file, gzip_flag=False):
    """
    # gene id in ncbi gff hard to link to pt cds fasta id, so we need change to locus_tag or Dbxref and so on

    parse NCBI seq fasta file, to locus_tag or Dbxref as seq ID
    :param nt_file:
    :param gzip_flag:
    :return:
    """

    seqdict, seqname_list = read_fasta(nt_file, gzip_flag=gzip_flag)
    qualifiers_dict = {}
    seqdict_new = {}
    for i in seqdict:
        record = seqdict[i]

        # parse ID info
        qualifiers = {}
        record_info = record.seqname.split('\t')
        qualifiers['raw_id'] = record_info[0]
        for j in record_info[1:]:
            name, value = re.findall(r'^(\S+)=(.*)$', j)[0]
            qualifiers[name] = value

        if 'Protein' in qualifiers:
            uniq_name = qualifiers['Protein']
        else:
            uniq_name = qualifiers['raw_id']

        qualifiers_dict[uniq_name] = qualifiers
        record.seqname = uniq_name
        seqdict_new[uniq_name] = record

    return qualifiers_dict, seqdict_new


def PreExtractNr(nr_fasta_file, sql3_db_file):
    import time
    import sqlite3
    from toolbiox.lib.xuyuxing.base.common_command import log_print
    import toolbiox.lib.common.sqlite_command as sc

    start_time = time.time()
    table_columns_dict = {
        "name_record": ("accession_id", "annotation_string", "record_id"),
        "seq_record": ("record_id", "seq")
    }
    sc.init_sql_db_many_table(sql3_db_file, table_columns_dict)

    record_id = 0
    name_record = []
    seq_record = []
    for record in read_fasta_big(nr_fasta_file, upper=True, filter_speci_char=False, gzip_flag=False):
        record_id = record_id + 1
        huge_name = record.seqname
        seq = record.seq
        for name in re.split('\x01', huge_name):
            accession_id = name.split(" ", 1)[0]
            # print("acc:%s\tfunc:%s\tspeci:%s" % (accession_id, function_string, speci_name))
            name_record.append((accession_id, name, record_id))
        seq_record.append((record_id, seq))

        if record_id % 10000 == 0:
            sc.sqlite_write(name_record, sql3_db_file,
                            "name_record", table_columns_dict["name_record"])
            name_record = []
            sc.sqlite_write(seq_record, sql3_db_file,
                            "seq_record", table_columns_dict["seq_record"])
            seq_record = []

        round_time = time.time()
        if round_time - start_time > 10:
            log_print("%d finished" % (record_id))
            start_time = round_time

    sc.sqlite_write(name_record, sql3_db_file, "name_record",
                    table_columns_dict["name_record"])
    sc.sqlite_write(seq_record, sql3_db_file, "seq_record",
                    table_columns_dict["seq_record"])
    log_print("%d finished" % (record_id))

    conn = sqlite3.connect(sql3_db_file)
    conn.execute("CREATE UNIQUE INDEX name_index on %s (\"%s\")" %
                 ("name_record", "accession_id"))
    conn.execute("CREATE UNIQUE INDEX seq_index on %s (\"%s\")" %
                 ("seq_record", "record_id"))
    conn.close()


def ExtractNr(nr_fasta_file, key_IDs, output_file, short_name=True):
    from toolbiox.lib.common.sqlite_command import sqlite_select_by_a_key
    name_IDs = sqlite_select_by_a_key(
        nr_fasta_file, "name_record", "accession_id", key_IDs)
    seq_IDs = tuple(set([i[2] for i in name_IDs]))
    seq_IDs = sqlite_select_by_a_key(
        nr_fasta_file, "seq_record", "record_id", seq_IDs)
    record_dict = []
    for accession_id, annotation_string, record_id in name_IDs:
        seqs = [i[1] for i in seq_IDs if i[0] == record_id][0]
        if short_name is True:
            seqname = accession_id
        else:
            seqname = annotation_string
        record_dict.append(FastaRecord(seqname, seqs))

    if output_file is not None:
        F1 = open(output_file, 'w')

    record_dict = list(set(record_dict))

    for record in record_dict:
        record.wrap()
        if output_file is not None:
            F1.write(">%s\n%s\n" % (record.seqname, record.seq))
        else:
            print(">%s\n%s" % (record.seqname, record.seq))
    if output_file is not None:
        F1.close()

    return len(record_dict), len(key_IDs)


def seq_cleaner(fasta_seq_record, seq_type='prot', degenerate_sites_allowed=False, gap_allowed=False,
                translation_stop_allowed=False, replace_flag=False, full_name_flag=False):
    """
    usage: SeqParser FastaFormatClean [-h] [-t {prot,nucl}] [-d] [-g] [-s]
                                  [-w WRAP] [-r] [-n] [-l LOG_FILE]
                                  raw_fasta_file output_fasta_file

    positional arguments:
      raw_fasta_file        raw fasta file
      output_fasta_file     output fasta file

    optional arguments:
      -h, --help            show this help message and exit
      -t {prot,nucl}, --seq_type {prot,nucl}
                            what type sequences you have? (default:prot)
      -d, --degenerate_sites_allowed
                            allow degenerate sites
      -g, --gap_allowed     allow gap sites
      -s, --translation_stop_allowed
                            allow translation stop sites
      -w WRAP, --wrap WRAP  all lines of text be shorter than warp characters in
                            length
      -r, --replace_flag    if find a unknown or not allowed site, should we
                            replace to any site? (default: no and skip sequence)
      -n, --full_name_flag  use full sequence name in output
      -l LOG_FILE, --log_file LOG_FILE
                            path for log file (default:None)

    """

    # argument parser
    if seq_type == 'nucl':
        seq_type = 0b0001
    elif seq_type == 'prot':
        seq_type = 0b0000

    dsa_flag = degenerate_sites_allowed
    if dsa_flag:
        dsa_flag = 0b0010

    ga_flag = gap_allowed
    if ga_flag:
        ga_flag = 0b0100

    tsa_flag = translation_stop_allowed
    if tsa_flag:
        tsa_flag = 0b1000

    bit_field = seq_type + dsa_flag + ga_flag + tsa_flag

    if bit_field == 0b0111:
        all_allowed = FastaRecord.nucl + FastaRecord.any_nucl + \
            FastaRecord.nucl_degenerate + FastaRecord.gap_site
        safe_remove = []
        safe_replace = FastaRecord.any_nucl
    elif bit_field == 0b0011:
        all_allowed = FastaRecord.nucl + FastaRecord.any_nucl + FastaRecord.nucl_degenerate
        safe_remove = FastaRecord.gap_site
        safe_replace = FastaRecord.any_nucl
    elif bit_field == 0b0101:
        all_allowed = FastaRecord.nucl + FastaRecord.any_nucl + FastaRecord.gap_site
        safe_remove = []
        safe_replace = FastaRecord.any_nucl
    elif bit_field == 0b0001:
        all_allowed = FastaRecord.nucl + FastaRecord.any_nucl
        safe_remove = FastaRecord.gap_site
        safe_replace = FastaRecord.any_nucl
    elif bit_field == 0b0000:
        all_allowed = FastaRecord.prot + FastaRecord.any_prot
        safe_remove = FastaRecord.gap_site + FastaRecord.stop_site
        safe_replace = FastaRecord.any_prot
    elif bit_field == 0b0100:
        all_allowed = FastaRecord.prot + FastaRecord.any_prot + FastaRecord.gap_site
        safe_remove = FastaRecord.stop_site
        safe_replace = FastaRecord.any_prot
    elif bit_field == 0b1100:
        all_allowed = FastaRecord.prot + FastaRecord.any_prot + \
            FastaRecord.gap_site + FastaRecord.stop_site
        safe_remove = []
        safe_replace = FastaRecord.any_prot
    elif bit_field == 0b1000:
        all_allowed = FastaRecord.prot + FastaRecord.any_prot + FastaRecord.stop_site
        safe_remove = FastaRecord.gap_site
        safe_replace = FastaRecord.any_prot
    else:
        raise ValueError("Bad input flag")

    fasta_seq_record.no_wrap()
    new_seq = fasta_seq_record.seq
    char_site = set(new_seq)
    bad_flag = False
    for i in char_site:
        if i in all_allowed:
            continue
        elif i in safe_remove:
            if i == "*":
                new_seq = re.sub("\*", "", new_seq)
            else:
                new_seq = re.sub(i, "", new_seq)
        else:
            if replace_flag:
                if i == "*":
                    new_seq = re.sub("\*", "", new_seq)
                else:
                    new_seq = re.sub(i, safe_replace[0], new_seq)
            else:
                bad_flag = True

    if bad_flag is True:
        good_flag = False
    else:
        good_flag = True
        fasta_seq_record.seq = new_seq

        if full_name_flag:
            fasta_seq_record.seqname = fasta_seq_record.seqname
        else:
            fasta_seq_record.seqname = fasta_seq_record.seqname_short()

    return good_flag, fasta_seq_record


def write_fasta(fasta_record_list, output_file, wrap_length=75, upper=False):
    with open(output_file, 'w') as f:
        for record in fasta_record_list:
            # print(record.seqname)
            # print(record.seq)
            record.no_wrap()
            raw_seq = str(record.seq)

            if upper:
                raw_seq = raw_seq.upper()

            f.write(">%s\n" % record.seqname)
            for x in range(0, len(raw_seq), wrap_length):
                # print(self.seqname, x)
                i = raw_seq[x: x + wrap_length]
                f.write(i + "\n")


if __name__ == '__main__':
    fasta_file = "/lustre/home/xuyuxing/Work/Other/saif/jupyter/A188.rename.fa"
    seq_dict = read_fasta_by_faidx(fasta_file)
    seq_tmp = seq_dict['CHR1']
    sub_seq_tmp = seq_tmp.sub(1, 100, '+', RNA=False)
    sub_seq_tmp = BioSeq(sub_seq_tmp)
    sub_seq_tmp.reverse_complement()

    # from Bio import SeqIO
    #
    # from toolbiox.lib.base.base_function import cmd_run
    #
    # # build
    # a = SeqIO.index_db('/lustre/home/xuyuxing/Work/Other/saif/jupyter/A188.rename.fa.gz.idx',
    #                    '/lustre/home/xuyuxing/Work/Other/saif/jupyter/A188.rename.fa.gz', 'fasta')
    # a['CHR1'][1000:100000]
    # seq_dict={}
    # for i in a:
    #     seq_dict[i]=a[i]
    #
    # seq_dict = read_fasta_by_bioidx(fasta_file)
