import os
from toolbiox.config import cutadapt_path
from toolbiox.lib.common.os import get_file_dir, cmd_run, multiprocess_running
import re
import io
import sys
import pysam
from pyfaidx import Fasta
from toolbiox.api.xuyuxing.file_parser.deep_data_parser import split_read_sorted_bam, hit_counter, split_sorted_bam_by_contig
from toolbiox.lib.common.util import logging_init
import array
from toolbiox.lib.common.genome.seq_base import read_fastq_big
from collections import OrderedDict


def clean_fastq_main(tag, fq1, fq2, adapter='illumina'):
    if adapter == 'illumina':
        adapter_string = 'AGATCGGAAGAGC'
    elif adapter == 'mgi_seq':
        adapter_string = 'AAGTCGGAGGCCAAGCGGTCTTAGGAAGACAA'
    else:
        adapter_string = adapter

    script_dir_path = os.path.split(os.path.realpath(__file__))[0]
    btrim_path = script_dir_path + "/../../api/genome/btrim/btrim64-static"
    paired_end_trim_path = script_dir_path + \
        "/../../api/genome/btrim/paired_end_trim.pl"
    work_dir = get_file_dir(fq1)

    # cutadapt
    cutted_fq1 = "%s/%s.cut.1.fq" % (work_dir, tag)
    cutted_fq2 = "%s/%s.cut.2.fq" % (work_dir, tag)

    cmd_string = "%s -a %s -o %s %s" % (cutadapt_path,
                                        adapter_string, cutted_fq1, fq1)
    cmd_run(cmd_string, cwd=work_dir, silence=True)
    cmd_string = "%s -a %s -o %s %s" % (cutadapt_path,
                                        adapter_string, cutted_fq2, fq2)
    cmd_run(cmd_string, cwd=work_dir, silence=True)

    # btrim
    trim1 = "%s/%s.cut.1.fq.trim" % (work_dir, tag)
    trim2 = "%s/%s.cut.2.fq.trim" % (work_dir, tag)
    trim1_sum = "%s/%s.cut.1.fq.trim.sum" % (work_dir, tag)
    trim2_sum = "%s/%s.cut.2.fq.trim.sum" % (work_dir, tag)

    cmd_string = "%s -a 25 -q -t %s -o %s -s %s -P -Q" % (
        btrim_path, cutted_fq1, trim1, trim1_sum)
    cmd_run(cmd_string, cwd=work_dir, silence=True)
    cmd_string = "%s -a 25 -q -t %s -o %s -s %s -P -Q" % (
        btrim_path, cutted_fq2, trim2, trim2_sum)
    cmd_run(cmd_string, cwd=work_dir, silence=True)

    # paired_end_trim
    cmd_string = "%s %s %s %s %s" % (
        paired_end_trim_path, trim1_sum, trim2_sum, trim1, trim2)
    cmd_run(cmd_string, cwd=work_dir, silence=True)
    pe1_file = "%s/%s.cut.1.fq.trim.pe" % (work_dir, tag)
    pe2_file = "%s/%s.cut.2.fq.trim.pe" % (work_dir, tag)
    se1_file = "%s/%s.cut.1.fq.trim.se" % (work_dir, tag)
    se2_file = "%s/%s.cut.2.fq.trim.se" % (work_dir, tag)

    # gzip
    cmd_string = "gzip %s" % pe1_file
    cmd_run(cmd_string, cwd=work_dir, silence=True)
    cmd_string = "gzip %s" % pe2_file
    cmd_run(cmd_string, cwd=work_dir, silence=True)

    # rename and clean
    output1_file = "%s/%s.clean.1.fq.gz" % (work_dir, tag)
    output2_file = "%s/%s.clean.2.fq.gz" % (work_dir, tag)

    cmd_string = "mv %s %s" % (pe1_file+'.gz', output1_file)
    cmd_run(cmd_string, cwd=work_dir, silence=True)
    cmd_string = "mv %s %s" % (pe2_file+'.gz', output2_file)
    cmd_run(cmd_string, cwd=work_dir, silence=True)

    for i in [cutted_fq1, cutted_fq2, trim1, trim2, trim1_sum, trim2_sum, se1_file, se2_file]:
        os.remove(i)


def BamSplit_main(args):
    if args.by_contig:
        if args.keep_head:
            split_sorted_bam_by_contig(
                args.input_bam_file, args.log_file, False)
        else:
            split_sorted_bam_by_contig(args.input_bam_file, args.log_file)
    else:
        split_read_sorted_bam(args.input_bam_file,
                              args.reads_per_file, args.log_file)


def ReadMapStats_main(args):
    """
    class abc(object):
        pass

    args = abc()

    args.log_file = '/lustre/home/xuyuxing/Work/Other/saif/Meth/test/log'
    args.input_bam_file = '/lustre/home/xuyuxing/Work/Other/saif/Meth/test/test.bam'
    args.reads_per_file = 10000
    args.threads = 50
    """


    logger = logging_init(
        "ReadMapStats: stats the reads hits for bam file", args.log_file)

    logger.info("Start: parsing fasta file")

    splited_file_list = split_read_sorted_bam(
        args.input_bam_file, args.reads_per_file, args.log_file)

    args_list = [(i, None) for i in splited_file_list]
    tmp_out = multiprocess_running(
        hit_counter, args_list, args.threads, log_file=args.log_file)

    total_count_stat_dict = {0: 0, 1: 0}
    for i in tmp_out:
        for j in tmp_out[i]['output']:
            if j not in total_count_stat_dict:
                total_count_stat_dict[j] = 0
            total_count_stat_dict[j] = total_count_stat_dict[j] + \
                tmp_out[i]['output'][j]

    total_reads_count = sum(total_count_stat_dict.values())
    uniq_mapping_ratio = total_count_stat_dict[1] / total_reads_count * 100
    total_mapping_ratio = (
        1 - total_count_stat_dict[0] / total_reads_count) * 100

    for i in splited_file_list:
        os.remove(i)

    logger.info("Finished.")

    logger.info("Report: ")
    logger.info("Bam file: %s" % args.input_bam_file)
    logger.info("Reads num: %s" % total_reads_count)
    logger.info("Uniq mapping ratio: %.2f%%" % uniq_mapping_ratio)
    logger.info("total mapping ratio: %.2f%%" % total_mapping_ratio)
    logger.info("reads have hit number: hits\treads")
    for i in range(0, max(list(total_count_stat_dict.keys()))):
        if i not in total_count_stat_dict:
            logger.info("%d\t0" % i)
        else:
            logger.info("%d\t%d" % (i, total_count_stat_dict[i]))

    print("Report: ")
    print("Bam file: %s" % args.input_bam_file)
    print("Reads num: %s" % total_reads_count)
    print("Uniq mapping ratio: %.2f%%" % uniq_mapping_ratio)
    print("total mapping ratio: %.2f%%" % total_mapping_ratio)
    print("reads have hit number: hits\treads")
    for i in range(0, max(list(total_count_stat_dict.keys()))):
        if i not in total_count_stat_dict:
            print("%d\t0" % i)
        else:
            print("%d\t%d" % (i, total_count_stat_dict[i]))


def Fastq2pbbam_main(args):
    raw_fastq = read_fastq_big(args.fastq_file)
    leaf_fastq = read_fastq_big(args.leaf_cut_fastq)
    right_fastq = read_fastq_big(args.right_cut_fastq)

    num = 0
    for read_tmp, in raw_fastq:
        leaf_read_tmp, = next(leaf_fastq)
        right_read_tmp, = next(right_fastq)
        if not (read_tmp.seqname == leaf_read_tmp.seqname == right_read_tmp.seqname):
            raise ValueError("reads name error")

        PU_tag = read_tmp.seqname.split('/')[0]
        ZM_tag = read_tmp.seqname.split('/')[1]
        site_tag = read_tmp.seqname.split('/')[2]
        start, end = site_tag.split('_')

        a = pysam.AlignedSegment()
        a.query_name = read_tmp.seqname
        a.query_sequence = read_tmp.seq
        a.flag = 4
        a.query_qualities = pysam.qualitystring_to_array(read_tmp.quality)
        a.mapping_quality = 255

        # get cx tag
        cx_tag = 0
        if leaf_read_tmp.seq[0].islower():
            cx_tag = cx_tag + 1
        if right_read_tmp.seq[-1].islower():
            cx_tag = cx_tag + 2

        a.tags = (
            ("cx", cx_tag),
            # ("ip", read.tags[1][1]),
            ("ip", array.array('B', [10] * len(a.query_sequence))),
            ("np", 1),
            # ("pw", read.tags[3][1]),
            ("pw", array.array('B', [10] * len(a.query_sequence))),
            ("qe", int(end)),
            ("qs", int(start)),
            ("rq", 0.80),
            ("sn", array.array('f', [5.81927, 11.0514, 6.24621, 10.8449])),
            ("zm", int(ZM_tag)),
            ("RG", 'ad13e653')
        )

        if num == 0:
            header = {'HD': {'VN': '1.5', 'SO': 'unknown', 'pb': '3.0.5'},
                        'RG': [OrderedDict({'ID': 'ad13e653', 'PL': 'PACBIO',
                                            'DS': 'READTYPE=SUBREAD;Ipd:CodecV1=ip;PulseWidth:CodecV1=pw;BINDINGKIT=101-500-400;SEQUENCINGKIT=101-427-500;BASECALLERVERSION=5.0.0;FRAMERATEHZ=100.000000',
                                            'PU': PU_tag, 'PM': 'SEQUEL'})]}

            outf = pysam.AlignmentFile(args.bam_file, "wb", header=header)
            num = num + 1

        outf.write(a)    