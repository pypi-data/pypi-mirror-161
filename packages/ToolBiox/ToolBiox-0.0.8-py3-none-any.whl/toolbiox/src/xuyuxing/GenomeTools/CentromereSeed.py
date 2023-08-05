import os
import re
from collections import OrderedDict
from itertools import combinations
from toolbiox.config import trf_path
from toolbiox.api.xuyuxing.genome.trf import trf_dat_to_dict
from toolbiox.api.common.genome.blast import blastn_running, outfmt6_read_big
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.xuyuxing.base.base_function import merge_file
from toolbiox.lib.common.os import mkdir, rmdir, get_file_name, cmd_run, multiprocess_running
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.math.set import merge_same_element_set
from toolbiox.lib.common.math.interval import section


def good_overlap(trf1, trf2):
    """
    function to find if two trf record is same loci but diff patten, used in step2 filter trf
    :param trf1:
    :param trf2:
    :return:
    """
    If_sect, delta = section(
        (trf1['start'], trf1['end']), (trf2['start'], trf2['end']))

    if If_sect:
        trf1_len = abs(trf1['start'] - trf1['end']) + 1
        trf2_len = abs(trf2['start'] - trf2['end']) + 1
        delta_len = abs(delta[1] - delta[0]) + 1
        if (delta_len / trf1_len) > 0.8 and (delta_len / trf2_len) > 0.8:
            return True
    return False


def remove_overlaped_trf(trf_list, trf_dict_ID):

    overlap_trfs = []
    for pairs in combinations(trf_list, 2):
        trf1 = trf_dict_ID[pairs[0]]
        trf2 = trf_dict_ID[pairs[1]]
        if good_overlap(trf1, trf2):
            overlap_trfs.append([pairs[0], pairs[1]])
    overlap_trfs = merge_same_element_set(overlap_trfs)
    for trf_group in overlap_trfs:
        for i in sorted(trf_group, key=lambda x: trf_dict_ID[x]['period_size'])[1:]:
            trf_list.remove(i)

    return trf_list


def CentromereSeed_main(args):
    mkdir(args.work_dir, True)
    log_file = args.work_dir + "/log"

    logger = logging_init("Centromere", log_file)

    logger.info("Find Centromere in an assembly")
    logger.info("Step1: get the data file from trf program")

    if args.trf_dat is None:
        logger.info("do not have a dat file, running trf now")

        trf_dir = args.work_dir + "/trf_dir"
        mkdir(trf_dir, True)
        split_trf_dir = trf_dir + "/split_dir"
        mkdir(split_trf_dir, True)

        record_dict = read_fasta_by_faidx(args.fasta_file)
        num = 0
        args_list = []
        for i in record_dict:
            record_tmp = record_dict[i]
            file_name = "seq%d.fa" % num
            with open(split_trf_dir + "/" + file_name, 'w') as f:
                f.write(">%s\n%s" % (record_tmp.seqname, record_tmp.seq))
            cmd_string = "%s %s 1 1 2 80 5 200 2000 -d -h" % (
                trf_path, file_name)
            print(cmd_string)
            args_list.append((cmd_string, split_trf_dir, 5, True, None))
            num += 1

        multiprocess_running(cmd_run, args_list,
                             args.threads, log_file=log_file)

        sub_file_list = []
        for i in os.listdir(split_trf_dir):
            if re.match(r'^.*\.dat$', i):
                sub_file_list.append("%s/%s" % (split_trf_dir, i))

        trf_dat = trf_dir + "/" + \
            get_file_name(args.fasta_file) + ".1.1.2.80.5.200.2000.dat"

        merge_file(sub_file_list, trf_dat)

        # rmdir(split_trf_dir)
    else:
        logger.info("have a dat file already, pass step1")
        trf_dat = args.trf_dat

    logger.info("Step1: finished")

    logger.info("Step2: parse trf dat file and filter same loci")

    trf_dict = trf_dat_to_dict(trf_dat)
    # data shift
    trf_dict_ID = {}
    for contig in trf_dict:
        num = 0
        for i in trf_dict[contig]:
            trf_element_ID = "%s_%d" % (contig, num)
            num = num + 1
            trf_dict_ID[trf_element_ID] = i

    trf_dict_ID_contig_hash = {}
    for trf_ID in trf_dict_ID:
        if trf_dict_ID[trf_ID]["chr"] not in trf_dict_ID_contig_hash:
            trf_dict_ID_contig_hash[trf_dict_ID[trf_ID]["chr"]] = []
        trf_dict_ID_contig_hash[trf_dict_ID[trf_ID]["chr"]].append(trf_ID)

    # filter: remove overlaped but bigger period size record
    filter_ID = {}
    args_list = []
    args_id_list = []
    for contig in trf_dict_ID_contig_hash:
        if len(trf_dict_ID_contig_hash[contig]) >= 2:
            trf_list = trf_dict_ID_contig_hash[contig]
            args_list.append((trf_list, trf_dict_ID))
            args_id_list.append(contig)
        else:
            filter_ID[contig] = trf_dict_ID_contig_hash[contig]

    mp_out = multiprocess_running(
        remove_overlaped_trf, args_list, 56, None, True, args_id_list)

    for i in mp_out:
        filter_ID[i] = mp_out[i]['output']

    # filter to small trf
    filter_dict_ID = {}
    for contig in filter_ID:
        for i in filter_ID[contig]:
            if trf_dict_ID[i]['period_size'] > 100:
                filter_dict_ID[i] = trf_dict_ID[i]

    logger.info("Step2: finished")

    logger.info("Step3: merge same unit")

    # blast
    trf_dir = args.work_dir + "/trf_dir"
    mkdir(trf_dir, True)

    trf_unit_fasta_file = trf_dir + "/trf_unit.fa"

    with open(trf_unit_fasta_file, 'w') as f:
        for i in filter_dict_ID:
            trf = filter_dict_ID[i]
            f.write(">%s\n%s\n" % (i, trf['unit']))

    trf_two_unit_fasta_file = trf_dir + "/trf_two_unit.fa"

    with open(trf_two_unit_fasta_file, 'w') as f:
        for i in filter_dict_ID:
            trf = filter_dict_ID[i]
            f.write(">%s\n%s%s\n" % (i, trf['unit'], trf['unit']))

    trf_unit_self_bls_file = trf_dir + "/trf_unit.bls"
    blastn_running(trf_unit_fasta_file, trf_two_unit_fasta_file,
                   trf_unit_self_bls_file, 1e-10, 56, realy_run=True, outfmt=6, task="blastn")

    # merge same unit trf

    trf_len_dir = {i: trf_dict_ID[i]['period_size'] for i in trf_dict_ID}

    one_way_dict = {}
    num = 0
    for record in outfmt6_read_big(trf_unit_self_bls_file):
        num += 1
        if num % 1000 == 0:
            print(num)
        one_way_dict[record.qID] = []
        for hit in record.hit:
            if hit.Hit_id == record.qID:
                continue

            top_hsp = hit.hsp[0]
            if top_hsp.Hsp_identical_ratio > 0.95 and top_hsp.Hsp_align_len / trf_len_dir[record.qID] > 0.95:
                one_way_dict[record.qID].append(hit.Hit_id)

    pair_list = []
    for i in one_way_dict:
        i_list = []
        for j in one_way_dict[i]:
            if j in one_way_dict and i in set(one_way_dict[j]):
                i_list.append(j)
        if len(i_list) > 0:
            i_list.append(i)
            pair_list.append(i_list)

    merged_list = merge_same_element_set(pair_list)

    merged_trf_dict = {}
    for i, j in enumerate(merged_list):
        merged_trf_dict[i] = j

    logger.info("Step3: finished")

    logger.info("Step4: find top candidate centromere unit")
    merged_trf_sum_dict = {}
    for m_id in merged_trf_dict:
        merged_trf_sum_dict[m_id] = sum([float(trf_dict_ID[trf_element_ID]['period_size']) * float(
            trf_dict_ID[trf_element_ID]['copy_num']) for trf_element_ID in merged_trf_dict[m_id]])

    # make huge report
    column_list = ['cluster_ID', 'cluster_sum_length', 'trf_ID', 'chr', 'start', 'end', 'period_size', 'copy_num',
                   'consensus_size', 'matches', 'indels', 'score', 'A_perc', 'C_perc', 'G_perc', 'T_perc', 'entropy', 'unit']

    with open(args.work_dir + "/trf_report.txt", 'w') as f:
        f.write("\t".join(column_list) + "\n")
        for c_id in sorted(merged_trf_sum_dict, key=lambda x: merged_trf_sum_dict[x], reverse=True):
            for trf_ID in sorted(merged_trf_dict[c_id], key=lambda x: len(trf_dict_ID[x]['sequence']), reverse=True):
                print_string = "\t".join(["Cluster_" + str(c_id), str(merged_trf_sum_dict[c_id]), trf_ID] + [str(trf_dict_ID[trf_ID][i]) for i in [
                                         'chr', 'start', 'end', 'period_size', 'copy_num', 'consensus_size', 'matches', 'indels', 'score', 'A_perc', 'C_perc', 'G_perc', 'T_perc', 'entropy', 'unit']])
                f.write(print_string + "\n")


if __name__ == "__main__":
    class abc():
        pass

    args = abc()

    args.trf_dat = None
    args.fasta_file = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/contig_filter/nextpolish2_canu.rawchrom.fasta'
    args.work_dir = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/contig_filter/Centromere'
    args.threads = 56
