import sys

sys.path.append("/lustre/home/xuyuxing/python_project/Genome_work_tools/")


import re
import json
import networkx as nx
import uuid
import numpy as np
from mpl_toolkits.axisartist.axislines import SubplotZero
import matplotlib.pyplot as plt
from interlap import InterLap
import pandas as pd
from collections import Counter
from itertools import combinations
from toolbiox.lib.xuyuxing.math.set_operating import interval_length_sum
from toolbiox.lib.common.math.interval import merge_intervals, interval_minus_set, overlap_between_interval_set, \
    group_by_intervals_with_overlap_threshold
from toolbiox.api.xuyuxing.plot import gene_structure_plot, exon_box
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, get_gf_db_meta_dict, gf_info_retrieval, write_gff_file
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.api.xuyuxing.genome.repeatmasker import repeatmasker_parser
from toolbiox.api.xuyuxing.genome.cd_hit import cd_hit_runing
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
from toolbiox.lib.common.os import mkdir, multiprocess_running


def load_map_files(reference_genome_table, WPGmapper_dir):
    # read ref genome taxon_id
    ref_db = pd.read_excel(reference_genome_table)
    ref_taxon_id_list = []
    for index in ref_db.index:
        taxon_id = str(ref_db.loc[index]['id'])
        if not pd.isna(taxon_id):
            ref_taxon_id_list.append(taxon_id)

    # load map database
    ref_WPGmapper_dict = {}
    for taxon_id in ref_taxon_id_list:
        ref_WPGmapper_dict[taxon_id] = {}
        ref_WPGmapper_dict[taxon_id]['genblasta'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genblasta.db"
        ref_WPGmapper_dict[taxon_id]['genewise'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.db"
        ref_WPGmapper_dict[taxon_id]['pep_db'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.pep.db"
        ref_WPGmapper_dict[taxon_id]['cds_db'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.cds.db"

    return ref_WPGmapper_dict


def min_cds_start(cds_range_list):
    return min([min(i) for i in cds_range_list])


def get_overlap_ratio(gf1,gf2,similarity_type):
    gf1_cds_interval = [(j.start, j.end) for j in gf1.sub_features[0].sub_features]
    gf2_cds_interval = [(j.start, j.end) for j in gf2.sub_features[0].sub_features]

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(gf1_cds_interval, gf2_cds_interval, similarity_type=similarity_type)
    
    return overlap_ratio


def higher_in_lower_group(lower_merged_group, higher, cds_interval_dict, similarity_type, threshold):
    grouped_flag = False

    for lower in lower_merged_group:
        jaccord_score = overlap_between_interval_set(
            cds_interval_dict[lower], cds_interval_dict[higher], similarity_type)[0]
        if jaccord_score >= threshold:
            grouped_flag = True
            break

    return grouped_flag


def merge_evidence_by_cds_intervals_identity(ev_id_list, cds_interval_dict, similarity_type, threshold):

    sorted_by_lower_bound = sorted(
        ev_id_list, key=lambda x: min_cds_start(cds_interval_dict[x]))
    merged = Counter()

    num = 0
    for higher in sorted_by_lower_bound:
        if len(merged) == 0:
            merged[num] = [higher]
            num += 1
        else:
            g_id_list = list(merged.keys())
            g_id_list.reverse()

            grouped_flag = False
            for g_id in g_id_list:
                grouped_flag = higher_in_lower_group(
                    merged[g_id], higher, cds_interval_dict, similarity_type, threshold)
                if grouped_flag == True:
                    merged[g_id].append(higher)
                    break

            if not grouped_flag:
                merged[num] = [higher]
                num += 1

    return merged


def extract_evidence(contig, strand, ref_WPGmapper_dict, min_cover, min_aa_len, min_identity, given_range=None):

    # get all useable evidence on the contig(strand)

    evidence_dict = {}

    for taxon_id in ref_WPGmapper_dict:
        # print(taxon_id)

        gws_db = ref_WPGmapper_dict[taxon_id]['genewise']
        meta_dict = get_gf_db_meta_dict(gws_db)

        # read mRNA info

        for table_name in meta_dict['gene'][0]:
            # print(table_name)
            if given_range is None:
                sql_cmd_string = 'SELECT * FROM %s WHERE contig_name = \"%s\" AND strand = \"%s\"' % (
                    table_name, contig, strand)
            else:
                sql_cmd_string = 'SELECT * FROM %s WHERE contig_name = \"%s\" AND strand = \"%s\" AND start <= %d AND end >= %d' % (
                    table_name, contig, strand, max(given_range), min(given_range))

            data_list = sc.sqlite_execute(sql_cmd_string, gws_db)
            for gf_db_info_tuple in data_list:
                id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers = gf_db_info_tuple
                gf = gf_info_retrieval(gf_db_info_tuple, 0, 'A', gws_db)

                mRNA_gf = gf.sub_features[0]
                qualifiers = mRNA_gf.qualifiers

                # query coverage
                coverage = min((int(qualifiers['Target_End'][0]) - int(
                    qualifiers['Target_Start'][0]) + 1) / int(qualifiers['Target_Length'][0]), 1.00)

                # aln aa
                aln_aa_len = int(
                    qualifiers['Target_End'][0]) - int(qualifiers['Target_Start'][0]) + 1

                # identity
                identity = int(qualifiers['idt_len']) / \
                    int(qualifiers['aln_len'])

                # filter
                evidence_id = "%s.%s.%s" % (taxon_id, table_name, id_tmp)

                gf.evidence_indicator = {
                    "query_coverage":coverage,
                    "aln_aa_len":aln_aa_len,
                    "identity":identity,
                }

                if coverage >= min_cover and aln_aa_len >= min_aa_len and identity >= min_identity:
                    gf.map_quality_pass = True
                    gf.cl_cover_pass = None
                else:
                    gf.map_quality_pass = False
                    gf.cl_cover_pass = False
                    gf.evidence_indicator["evidence_range_cover"]=0.0

                evidence_dict[evidence_id] = gf

    return evidence_dict


def evidence_cluster(evidence_dict, similarity_type='jaccord_score', threshold=0.3):
    if len(evidence_dict) > 0:

        # CDS interval list
        cds_interval_dict = {}
        gene_interval_dict = {}
        for i in evidence_dict:
            if not evidence_dict[i].map_quality_pass:
                continue

            gene_interval_dict[i] = (
                evidence_dict[i].start, evidence_dict[i].end)
            cds_interval_dict[i] = [
                (j.start, j.end) for j in evidence_dict[i].sub_features[0].sub_features]

        big_group_dict = group_by_intervals_with_overlap_threshold(gene_interval_dict, 0)

        # # load evidences into interlap
        # evidence_interlap = InterLap()
        # evidence_interlap.update(
        #     [(gene_interval_dict[i][0], gene_interval_dict[i][1], i) for i in gene_interval_dict])

        # merge intervals into cluster
        ev_cluster_dict = {}
        num = 0
        for bg_id in big_group_dict:
            cds_interval_dict_in_group = {ev_id:cds_interval_dict[ev_id] for ev_id in big_group_dict[bg_id]['list']}

            ev_cluster_dict_in_group = merge_evidence_by_cds_intervals_identity(
                list(cds_interval_dict_in_group.keys()), cds_interval_dict_in_group, similarity_type, threshold)
            
            for i in ev_cluster_dict_in_group:
                num += 1
                ev_cluster_dict[num] = ev_cluster_dict_in_group[i]

        # ev_cluster_range_dict = {}
        # for cl_id in ev_cluster_dict:
        #     ev_cluster_range_dict[cl_id] = merge_intervals([gene_interval_dict[i] for i in ev_cluster_dict[cl_id]])[0]

        return ev_cluster_dict

    else:
        return Counter()


# def build_skip_interlap_dict(contig_list, target_gene_gff, target_repeatmasker):

#     target_gene_dict = read_gff_file(target_gene_gff)
#     target_repeat_dict = repeatmasker_parser(target_repeatmasker)

#     skip_interlap_dict = {contig_id: [] for contig_id in contig_list}
#     for repeat_type in target_repeat_dict:
#         for family_name in target_repeat_dict[repeat_type]:
#             for case in target_repeat_dict[repeat_type][family_name].case_list:
#                 contig = case.q_name
#                 start = case.q_start
#                 end = case.q_end

#                 if contig not in skip_interlap_dict:
#                     continue

#                 skip_interlap_dict[contig].append(
#                     (min(start, end), max(start, end)))

#     for gf_type in target_gene_dict:
#         for gene_id in target_gene_dict[gf_type]:
#             gf = target_gene_dict[gf_type][gene_id]
#             contig = gf.chr_id
#             start = gf.start
#             end = gf.end

#             if contig not in skip_interlap_dict:
#                 continue

#             skip_interlap_dict[contig].append(
#                 (min(start, end), max(start, end)))

#     for contig in skip_interlap_dict:
#         range_list = merge_intervals(skip_interlap_dict[contig])
#         skip_interlap_dict[contig] = InterLap()
#         if len(range_list) > 0:
#             skip_interlap_dict[contig].update(range_list)

#     return skip_interlap_dict

def read_skip_file(skip_file, contig_list):
    skip_range_dict = {i: InterLap() for i in contig_list}

    if skip_file is None:
        return skip_range_dict
    else:
        with open(skip_file, 'r') as f:
            for each_line in f:

                each_line = each_line.strip()
                chr_id, start, end = each_line.split()
                start = int(start)
                end = int(end)

                skip_range_dict[chr_id].add((min(start, end), max(start, end)))

        return skip_range_dict


def get_seq_from_db(seq_id, db_file):
    output_tuple = sc.sqlite_select(
        db_file, 'record', ['seqname_short', 'seqs'], 'seqname_short', [seq_id])
    return output_tuple[0][1]


def pseudo_judge(pseudo_event, evidence_gf_dict, event_range, ref_WPGmapper_dict):

    # cds interlap
    all_evidence_cds_interlap = InterLap()
    for ev_id in evidence_gf_dict:
        ggf = evidence_gf_dict[ev_id]
        if not ggf.cl_cover_pass:
            continue
        gf = ggf.sub_features[0]
        for sub_gf in gf.sub_features:
            all_evidence_cds_interlap.add(
                (sub_gf.start, sub_gf.end, (ev_id, sub_gf.id)))

    merged_pseudo_event = {}
    for site_range, ev_id, pseudo_type in pseudo_event:
        if pseudo_type not in merged_pseudo_event:
            merged_pseudo_event[pseudo_type] = InterLap()
        merged_pseudo_event[pseudo_type].add(
            (site_range[0]-int(event_range/2), site_range[1]+int(event_range/2), (site_range, ev_id)))

    output_pseudo_dict = {}
    all_support_ev_list = []
    for pseudo_type in merged_pseudo_event:
        output_pseudo_dict[pseudo_type] = {}
        for merge_range in merge_intervals([(i[0], i[1]) for i in merged_pseudo_event[pseudo_type]]):

            tmp_list = []
            support_ev_list = []
            for i in merged_pseudo_event[pseudo_type].find(merge_range):
                tmp_list.append(i[2][0][0])
                tmp_list.append(i[2][0][1])
                support_ev_list.append(i[2][1])

            merge_pseudo_event_range = (min(tmp_list), max(tmp_list))
            support_ev_list = tuple(list(set(support_ev_list)))
            all_support_ev_list.extend(support_ev_list)

            all_ev_list = tuple(list(
                set([i[2][0] for i in all_evidence_cds_interlap.find(merge_pseudo_event_range)])))

            if len(all_ev_list) == 0:
                support_ratio = 0
            else:
                support_ratio = len(support_ev_list) / len(all_ev_list)

            output_pseudo_dict[pseudo_type][merge_pseudo_event_range] = (
                support_ratio, support_ev_list, all_ev_list)

    # get representable gf

    if len(all_support_ev_list) > 0:
        taxon_list = [ev_id.split(".")[0] for ev_id in all_support_ev_list]

        seq_dict = {}
        cds_seq_dict = {}
        for ev_id in all_support_ev_list:
            taxon_id, table_name, id_tmp = ev_id.split(".")
            ggf = evidence_gf_dict[ev_id]
            gf = ggf.sub_features[0]
            gene_id = re.sub(r'.mRNA$', '', gf.id)

            seq_dict[ev_id] = get_seq_from_db(
                gene_id, ref_WPGmapper_dict[taxon_id]['pep_db'])
            cds_seq_dict[ev_id] = get_seq_from_db(gene_id,ref_WPGmapper_dict[taxon_id]['cds_db'])

        seq_cluster_dict = cd_hit_runing(seq_dict)

        if seq_cluster_dict is None:
            print("seq_cluster_dict is None， print seq_dict:")
            for i in seq_dict:
                print("%s\t%s\n" % (i, seq_dict[i]))

            raise ValueError("seq_cluster_dict is None")

        rep_ev_id = sorted(seq_cluster_dict, key=lambda x: len(
            seq_cluster_dict[x]), reverse=True)[0]

        rep_gf = evidence_gf_dict[rep_ev_id]
        rep_aa_seq = seq_dict[rep_ev_id]
        rep_cds_seq = cds_seq_dict[rep_ev_id]

    else:
        rep_gf = None
        rep_aa_seq = None
        rep_cds_seq = None

    return output_pseudo_dict, rep_gf, rep_aa_seq, rep_cds_seq
    # return output_pseudo_dict, rep_gf, rep_aa_seq


def filter_short_evidence(given_gf_dict, evidence_range_cover):
    total_ev_cds_range = []
    for ev_id in given_gf_dict:
        gf = given_gf_dict[ev_id]
        for sgf in gf.sub_features[0].sub_features:
            total_ev_cds_range.append((sgf.start, sgf.end))

    total_ev_cds_range = merge_intervals(total_ev_cds_range)
    print(total_ev_cds_range)

    # filter short evidence
    
    filtered_gf_dict = {}
    for ev_id in given_gf_dict:
        gf = given_gf_dict[ev_id]
        gf_cds_range_list = [(sgf.start, sgf.end)
                             for sgf in gf.sub_features[0].sub_features]
        print(gf_cds_range_list)
        overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
            total_ev_cds_range, gf_cds_range_list)

        gf.evidence_indicator['evidence_range_cover'] = overlap_length / interval_length_sum(total_ev_cds_range)
        if gf.evidence_indicator['evidence_range_cover'] > evidence_range_cover:
            gf.cl_cover_pass = True
            print(gf, True)
        else:
            gf.cl_cover_pass = False
            print(gf, False)
        filtered_gf_dict[ev_id] = gf
    
    return filtered_gf_dict

    # for i,j in list(combinations(filtered_gf_dict,2)):
    #     print(i,j)
    #     gf = given_gf_dict[i]
    #     i_gf_cds_range_list = [(sgf.start, sgf.end)
    #                             for sgf in gf.sub_features[0].sub_features]
    #     gf = given_gf_dict[j]
    #     j_gf_cds_range_list = [(sgf.start, sgf.end)
    #                             for sgf in gf.sub_features[0].sub_features]

    #     print(overlap_between_interval_set(i_gf_cds_range_list,j_gf_cds_range_list,"jaccord_score"))



def pseudo_event_in_range(given_gf_dict, gene_fragment_ratio, event_range, ref_WPGmapper_dict, min_support_ratio, min_support_evidence_num, get_seq_flag=True):
    """
    cluster_range = (131484, 144903)
    """
    # get pseudo report
    # short pseudo
    # stop and shift pseudo

    pseudo_event = []

    for ev_id in given_gf_dict:
        gf = given_gf_dict[ev_id]
        if not gf.cl_cover_pass:
            continue
        mgf = gf.sub_features[0]

        # pseudo site
        pseudo_gf = False
        if "Note" in mgf.qualifiers and mgf.qualifiers["Note"][0] == "pseudogene":
            for sub_gf in mgf.sub_features:
                if "Note_stop_code" in sub_gf.qualifiers:
                    pseudo_gf = True
                    for site in sub_gf.qualifiers["Note_stop_code"]:
                        pseudo_event.append(
                            ((int(site), int(site)), ev_id, "Note_stop_code"))

                if "Note_frame_shift" in sub_gf.qualifiers:
                    pseudo_gf = True
                    for site in sub_gf.qualifiers["Note_frame_shift"]:
                        pseudo_event.append(
                            ((int(site), int(site)), ev_id, "Note_frame_shift"))

        # gene fragment
        coverage = min((int(mgf.qualifiers['Target_End'][0]) - int(
            mgf.qualifiers['Target_Start'][0]) + 1) / int(mgf.qualifiers['Target_Length'][0]), 1.00)

        if coverage <= gene_fragment_ratio:
            pseudo_event.append(((mgf.start, mgf.end), ev_id, "Gene_Fragment"))
            pseudo_gf = True

        if pseudo_gf == False:
            pseudo_event.append(((mgf.start, mgf.end), ev_id, "Missed_Gene"))

    pseudo_judge_dict, rep_gf, rep_aa_seq, rep_cds_seq = pseudo_judge(
        pseudo_event, given_gf_dict, event_range, ref_WPGmapper_dict)

    for pseudo_type in pseudo_judge_dict:
        for pseudo_site_range in pseudo_judge_dict[pseudo_type]:
            support_ratio, support_ev_list, all_ev_list = pseudo_judge_dict[
                pseudo_type][pseudo_site_range]
            if support_ratio >= min_support_ratio and len(support_ev_list) >= min_support_evidence_num:
                good_pseudo = True
            else:
                good_pseudo = False
            pseudo_judge_dict[pseudo_type][pseudo_site_range] = support_ratio, support_ev_list, all_ev_list, good_pseudo

    return pseudo_judge_dict, rep_gf, rep_aa_seq, rep_cds_seq


def pseudogene_main(args):
    mkdir(args.output_dir, True)

    contig_list = list(read_fasta_by_faidx(args.target_genome_fasta).keys())

    # read gff file
    # skip_interlap_dict = build_skip_interlap_dict(
    #     contig_list, args.target_gene_gff, args.target_repeatmasker)

    # skip_interlap_dict = read_skip_file(args.skip_range_file, contig_list)

    # load WPGmapper data
    ref_WPGmapper_dict = load_map_files(
        args.reference_genome_table, args.WPGmapper_dir)

    # parse a contig
    args_list = []
    for contig in contig_list:
        args_list.append((contig, ref_WPGmapper_dict, args))

    multiprocess_running(pseudogene_by_contig, args_list,
                         args.threads, silence=True)

# ok

def pseudogene_by_contig(contig, ref_WPGmapper_dict, args):

    pseudo_report = args.output_dir + "/%s.pseudo.txt" % contig
    evidence_report = args.output_dir + "/%s.evidence.txt" % contig
    pseudo_gene_gff = args.output_dir + "/%s.pseudo.gff" % contig
    pseudo_gene_seq = args.output_dir + "/%s.pseudo.faa" % contig
    pseudo_gene_cds_seq = args.output_dir + "/%s.pseudo.cds.fna" % contig

    p = open(pseudo_report, 'w')
    printer_string = "# cluster_id\tcontig\tstrand\tclst_start\tclst_end\ttotal_ev_num\tgood_map_ev_num\tgood_cover_ev_num\trepresent_ev_id\tpseudo_site_start\tpseudo_site_end\tpseudo_type\tsupport_ev_num\tall_ev_num\tsupport_ratio\tgood_pseudo\tsupport_ev_list\n"
    p.write(printer_string)

    e = open(evidence_report, 'w')
    printer_string = "# ev_id\tcontig\tstrand\tev_start\tev_end\tquery_coverage\taln_aa_len\tidentity\tgood_map\tev_range_cover\tgood_cover\n"
    e.write(printer_string)

    rep_gf_list = []
    rep_aa_seq_dict = {}
    rep_cds_seq_dict = {}

    for strand in ["+", "-"]:

        evidence_dict = extract_evidence(
            contig, strand, ref_WPGmapper_dict, args.min_cover, args.min_aa_len, args.min_identity)

        ev_cluster_ev_id_dict = evidence_cluster(
            evidence_dict, args.similarity_type, args.similarity_threshold)

        ev_cluster_dict = {}
        for cl_id in ev_cluster_ev_id_dict:
            print(cl_id)
            given_gf_dict = {ev_id:evidence_dict[ev_id] for ev_id in ev_cluster_ev_id_dict[cl_id]}
            given_gf_dict_add_filter = filter_short_evidence(given_gf_dict, args.evidence_range_cover)

            for i in given_gf_dict_add_filter:
                evidence_dict[i] = given_gf_dict_add_filter[i]

            pseudo_judge_dict, rep_gf, rep_aa_seq, rep_cds_seq = pseudo_event_in_range(given_gf_dict_add_filter, args.gene_fragment_ratio, args.event_range, ref_WPGmapper_dict, args.min_support_ratio, args.min_support_evidence_num, get_seq_flag=True)

            if not rep_gf is None:
                rep_gf_list.append(rep_gf)
                rep_aa_seq_dict[rep_gf.id] = rep_aa_seq
                rep_cds_seq_dict[rep_gf.id] = rep_cds_seq

            cl_name = contig+"_"+strand+"_"+str(cl_id)
            ev_cluster_dict[cl_name] = (pseudo_judge_dict, rep_gf, rep_aa_seq, rep_cds_seq)


        # make report
        used_ev_gf = []
        for ev_id in evidence_dict:
            ev_gf = evidence_dict[ev_id]

            printer_string = printer_list([ev_id, contig, strand, ev_gf.start, ev_gf.end, ev_gf.evidence_indicator["query_coverage"], ev_gf.evidence_indicator["aln_aa_len"],
                                           ev_gf.evidence_indicator["identity"], ev_gf.map_quality_pass, ev_gf.evidence_indicator["evidence_range_cover"], ev_gf.cl_cover_pass])

            if ev_gf.cl_cover_pass:
                used_ev_gf.append(ev_gf)

            print(printer_string)

        write_gff_file(used_ev_gf, "used_ev.gff3")

        pseudo_num = 0
        good_rep_gf = []
        best_ev_id = []
        for cl_name in ev_cluster_dict:
            pseudo_judge_dict, rep_gf, rep_aa_seq, rep_cds_seq = ev_cluster_dict[cl_name]
            
            pseudo_true_flag = False
            for pseudo_type in pseudo_judge_dict:
                for site_range in pseudo_judge_dict[pseudo_type]:
                    if pseudo_judge_dict[pseudo_type][site_range][3]:
                        pseudo_true_flag = True
                        best_ev_id.extend(list(pseudo_judge_dict[pseudo_type][site_range][2]))
            
            if pseudo_true_flag:
                pseudo_num += 1
                good_rep_gf.append(rep_gf)
        
        best_ev_id = list(set(best_ev_id))
        best_ev_gf_list = [evidence_dict[i] for i in best_ev_id]

        write_gff_file(good_rep_gf, "rep.gff3")
        write_gff_file(best_ev_gf_list, "good_ev.gff3")
        







    write_gff_file(rep_gf_list, pseudo_gene_gff, "Pseudo")

    with open(pseudo_gene_seq, 'w') as f:
        for i in rep_aa_seq_dict:
            f.write(">%s\n%s\n" % (i, rep_aa_seq_dict[i]))

    with open(pseudo_gene_cds_seq, 'w') as f:
        for i in rep_cds_seq_dict:
            f.write(">%s\n%s\n" % (i, rep_cds_seq_dict[i]))

# used now

def get_ev_weight(idt_len, query_length):
    if query_length > 200:
        length_score = 5
    elif query_length > 150:
        length_score = 4
    elif query_length > 100:
        length_score = 3
    elif query_length > 50:
        length_score = 2
    
    # return (idt_len/aln_len) * (aln_len/query_length) * length_score
    return (idt_len/query_length) * length_score


def make_cds_vector(evidence_dict_range, range_now):
    cds_weight_interlap = InterLap()

    coordinate_list = []
    for ev_id in evidence_dict_range:
        ev_gf = evidence_dict_range[ev_id]
        mRNA = ev_gf.sub_features[0]
        idt_len = mRNA.qualifiers['idt_len']
        query_length = int(mRNA.qualifiers['Target_Length'][0])
        ev_weight_value = get_ev_weight(idt_len, query_length)
        
        for cds in mRNA.sub_features:
            cds_weight_interlap.add((cds.start,cds.end,ev_weight_value))
            coordinate_list.append(cds.start)
            coordinate_list.append(cds.end)

    coordinate_list = sorted(list(set(coordinate_list)))

    cds_vector_interlap = InterLap()
    getted_range = {}
    for i in range(0,len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            w_s_total = sum([w for s,e,w in cds_weight_interlap.find((start, start))])
            getted_range[(start, start)] = w_s_total
            cds_vector_interlap.add((start,start,w_s_total))

        if (end, end) not in getted_range:
            w_e_total = sum([w for s,e,w in cds_weight_interlap.find((end, end))])
            getted_range[(end, end)] = w_e_total
            cds_vector_interlap.add((end,end,w_e_total))
        
        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                w_i_total = sum([w for s,e,w in cds_weight_interlap.find(interval)])
                getted_range[interval] = w_i_total
                cds_vector_interlap.add((interval[0],interval[1],w_i_total))
    
    return cds_vector_interlap

def get_vector_score(vector_interlap, start, end):

    w = [w for s,e,w in vector_interlap.find((start, end))]
    if len(w) > 1:
        raise ValueError("cds error: %d, %d" % (start, end))
    elif len(w) == 0:
        w = 0.0
    else:
        w = w[0]
    
    return w


def get_ev_gf_score(gf, cds_vector_interlap):

    mRNA = gf.sub_features[0]
    idt_len = mRNA.qualifiers['idt_len']
    query_length = int(mRNA.qualifiers['Target_Length'][0])
    ev_weight_value = get_ev_weight(idt_len, query_length)

    sum_w = 0
    length = 0
    for cds in mRNA.sub_features:
        for i in range(cds.start,cds.end+1):
            length += 1
            sum_w += get_vector_score(cds_vector_interlap, i, i)
    
    gf_score = (sum_w + ev_weight_value * length)/length

    return gf_score


def mark_ev_score_for_gf_dict(input_gf_dict, cds_vector_interlap):
    output_gf_dict = {}
    for i in input_gf_dict:
        gf = input_gf_dict[i]
        gf_score = get_ev_gf_score(gf, cds_vector_interlap)
        gf.gf_score = gf_score
        output_gf_dict[i] = gf
    return output_gf_dict

def mark_exclusivity_for_gf_dict(input_gf_dict):
    evidence_cluster_range = evidence_cluster(input_gf_dict, similarity_type='shorter_overlap_coverage', threshold=0.1)
    output_gf_dict = {}

    for cl_id in evidence_cluster_range:
        ev_id_list = evidence_cluster_range[cl_id]
        if len(ev_id_list) == 1:
            gf = input_gf_dict[ev_id_list[0]]
            gf.exclusivity = [ev_id_list[0]]
            output_gf_dict[ev_id_list[0]] = gf
        else:
            score_pair_dict = {}
            for i,j in combinations(ev_id_list, 2):
                score_pair_dict[(i,j)] = get_overlap_ratio(input_gf_dict[i],input_gf_dict[j],'shorter_overlap_coverage')

            for ev_id_i in evidence_cluster_range[cl_id]:
                gf = input_gf_dict[ev_id_i]
                exclusivity_list = []
                for ev_id_j in evidence_cluster_range[cl_id]:
                    if ev_id_i == ev_id_j:
                        continue
                    if (ev_id_i, ev_id_j) in score_pair_dict:
                        overlap_ratio = score_pair_dict[(ev_id_i, ev_id_j)]
                    else:
                        overlap_ratio = score_pair_dict[(ev_id_j, ev_id_i)]

                    if overlap_ratio > 0.5:
                        exclusivity_list.append(ev_id_j)
                gf.exclusivity = exclusivity_list
                gf.exclusivity.append(ev_id_i)
                output_gf_dict[ev_id_i] = gf
    
    return output_gf_dict
    
def load_a_node(graph, give_node_id, remaining_selectable_ev_list, evidence_dict_range):
    # print(give_node_id)
    # print(remaining_selectable_ev_list)
    uuid_id, seq_id = give_node_id

    for i in remaining_selectable_ev_list:
        uuid_id = uuid.uuid1().hex
        node_id = (uuid_id, i)

        graph.add_edge(give_node_id, node_id, weight=-evidence_dict_range[i].gf_score)

        remaining_selectable_ev_list_for_i = list(set(remaining_selectable_ev_list) - set(evidence_dict_range[i].exclusivity))
        if len(remaining_selectable_ev_list_for_i) == 0:
            graph.add_edge(node_id, 'END', weight=-1)
            # print(node_id)
        else:
            load_a_node(graph, node_id, remaining_selectable_ev_list_for_i, evidence_dict_range)


def best_select(evidence_dict_range):

    cds_vector_interlap = make_cds_vector(evidence_dict_range)
    evidence_dict_range = mark_ev_score_for_gf_dict(evidence_dict_range, cds_vector_interlap)
    evidence_dict_range = mark_exclusivity_for_gf_dict(evidence_dict_range)

    for i in evidence_dict_range:
        gf = evidence_dict_range[i]
        print(gf.id, gf.exclusivity)


def use_graph_to_get_rep(evidence_dict_range):
    
    G = nx.DiGraph()
    uuid_id = uuid.uuid1().hex
    start = (uuid_id, 'START')

    load_a_node(G, start, list(evidence_dict_range.keys()), evidence_dict_range)
    # paths = nx.johnson(G, weight="weight")
    # paths[start]["END"]

    return nx.shortest_path(G,start,"END",weight='weight',method="bellman-ford")

class abc():
    pass

evidence_dict_range2 = {}

gf1 = abc()
gf1.gf_score = 1000
gf1.exclusivity = ['gf1', 'gf2', 'gf3']
evidence_dict_range2['gf1'] = gf1

gf2 = abc()
gf2.gf_score = 600
gf2.exclusivity = ['gf1', 'gf2']
evidence_dict_range2['gf2'] = gf2

gf3 = abc()
gf3.gf_score = 600
gf3.exclusivity = ['gf1', 'gf3']
evidence_dict_range2['gf3'] = gf3

use_graph_to_get_rep(evidence_dict_range2)

G = nx.DiGraph()
G.add_edge(1, 2, weight=-1)
G.add_edge(1, 5, weight=-1)
G.add_edge(2, 3, weight=-1)
G.add_edge(2, 4, weight=-1)
G.add_edge(5, 6, weight=-1)
G.add_edge(5, 8, weight=-1)
G.add_edge(6, 7, weight=-1)
G.add_edge(3, 9, weight=-1)
G.add_edge(4, 9, weight=19)
G.add_edge(7, 9, weight=19)
G.add_edge(8, 9, weight=1)

nx.shortest_path(G,1,9,weight='weight')



# other

target_genome_dict = read_fasta_by_faidx(args.target_genome_fasta)
target_genome_dict = {
    i: str(target_genome_dict[i].seq) for i in target_genome_dict}


def test_frame(cds_start,cds_end,frame_shift):

    # cds_start = 8343856
    # cds_end = 8343952
    # frame_shift = 8343901

    seq_str = target_genome_dict[contig][cds_start - 1: cds_end].upper()
    print(seq_str)
    print(cds_judgment(seq_str, False))

    seq_str = target_genome_dict[contig][cds_start - 1: frame_shift-1].upper()
    print(seq_str)
    print(cds_judgment(seq_str, False))

    seq_str = target_genome_dict[contig][frame_shift + 1 - 1: cds_end].upper()
    print(seq_str)
    print(cds_judgment(seq_str))



def try_evm_annotation(contig, strand, ref_WPGmapper_dict):
    range_now = (8300000,8450000)
    evidence_dict = extract_evidence(contig, strand, ref_WPGmapper_dict, args.min_cover, args.min_aa_len, args.min_identity, (8300000,8450000))


    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]
        
        aln_len = ev_gf.sub_features[0].qualifiers['aln_len']
        idt_len = ev_gf.sub_features[0].qualifiers['idt_len']
        query_length = int(ev_gf.sub_features[0].qualifiers['Target_Length'][0])
        ev_weight_value = get_ev_weight(idt_len, query_length)
        ev_name = ev_gf.sub_features[0].qualifiers['Parent'][0]

        ev_gf.ev_weight_value = ev_weight_value

    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]
        ev_mRNA = ev_gf.sub_features[0]

        break_all = False

        for cds in ev_mRNA.sub_features:
            frame_site = []
            stop_site =[]
            if 'Note_frame_shift' in cds.qualifiers:
                frame_site = [int(i) for i in cds.qualifiers['Note_frame_shift']]
            if 'Note_stop_code' in cds.qualifiers:
                stop_site = [int(i) for i in cds.qualifiers['Note_stop_code']]
            
            cds_phase = int(cds.qualifiers['phase'][0])

            print(cds.start,cds.end,cds.strand,cds_phase,frame_site,stop_site)
    
            if frame_site != []:
                break_all = True
                break
        
        if break_all:
            break


def make_cds_vector(evidence_dict_range, range_now):
    cds_weight_interlap = InterLap()
    coordinate_list = [range_now[0],range_now[1]]

    for ev_id in evidence_dict_range:
        ev_gf = evidence_dict_range[ev_id]
        mRNA = ev_gf.sub_features[0]
        idt_len = mRNA.qualifiers['idt_len']
        query_length = int(mRNA.qualifiers['Target_Length'][0])
        ev_weight_value = get_ev_weight(idt_len, query_length)
        
        for cds in mRNA.sub_features:
            cds_weight_interlap.add((cds.start,cds.end,ev_weight_value))
            coordinate_list.append(cds.start)
            coordinate_list.append(cds.end)

    coordinate_list = sorted(list(set(coordinate_list)))

    cds_vector_interlap = InterLap()
    getted_range = {}
    for i in range(0,len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            w_s_total = sum([w for s,e,w in cds_weight_interlap.find((start, start))])
            getted_range[(start, start)] = w_s_total
            cds_vector_interlap.add((start,start,w_s_total))

        if (end, end) not in getted_range:
            w_e_total = sum([w for s,e,w in cds_weight_interlap.find((end, end))])
            getted_range[(end, end)] = w_e_total
            cds_vector_interlap.add((end,end,w_e_total))
        
        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                w_i_total = sum([w for s,e,w in cds_weight_interlap.find(interval)])
                getted_range[interval] = w_i_total
                cds_vector_interlap.add((interval[0],interval[1],w_i_total))
    
    return cds_vector_interlap

def get_vector_score(vector_interlap, start, end):

    w = [w for s,e,w in vector_interlap.find((start, end))]
    if len(w) > 1:
        raise ValueError("cds error: %d, %d" % (start, end))
    elif len(w) == 0:
        w = 0.0
    else:
        w = w[0]
    
    return w


def get_ev_gf_score(gf, cds_vector_interlap):

    mRNA = gf.sub_features[0]
    idt_len = mRNA.qualifiers['idt_len']
    query_length = int(mRNA.qualifiers['Target_Length'][0])
    ev_weight_value = get_ev_weight(idt_len, query_length)

    sum_w = 0
    length = 0
    for cds in mRNA.sub_features:
        for i in range(cds.start,cds.end+1):
            length += 1
            sum_w += get_vector_score(cds_vector_interlap, i, i)
    
    gf_score = (sum_w + ev_weight_value * length)/length

    return gf_score


for i in evidence_dict_range:
    print(evidence_dict_range[i].id, get_ev_gf_score(evidence_dict_range[i], cds_vector_interlap))


def make_start_cds_vector(evidence_dict_range, range_now):
    cds_weight_interlap = InterLap()
    coordinate_list = [range_now[0],range_now[1]]

    for ev_id in evidence_dict_range:
        ev_gf = evidence_dict_range[ev_id]
        mRNA = ev_gf.sub_features[0]
        idt_len = mRNA.qualifiers['idt_len']
        query_length = int(mRNA.qualifiers['Target_Length'][0])
        ev_weight_value = get_ev_weight(idt_len, query_length)
        
        for cds in mRNA.sub_features:
            cds_weight_interlap.add((cds.start,cds.end,ev_weight_value))
            coordinate_list.append(cds.start)
            coordinate_list.append(cds.end)

    coordinate_list = sorted(list(set(coordinate_list)))

    cds_vector_interlap = InterLap()
    getted_range = {}
    for i in range(0,len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            w_s_total = sum([w for s,e,w in cds_weight_interlap.find((start, start))])
            getted_range[(start, start)] = w_s_total
            cds_vector_interlap.add((start,start,w_s_total))

        if (end, end) not in getted_range:
            w_e_total = sum([w for s,e,w in cds_weight_interlap.find((end, end))])
            getted_range[(end, end)] = w_e_total
            cds_vector_interlap.add((end,end,w_e_total))
        
        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                w_i_total = sum([w for s,e,w in cds_weight_interlap.find(interval)])
                getted_range[interval] = w_i_total
                cds_vector_interlap.add((interval[0],interval[1],w_i_total))
    
    return cds_vector_interlap

def make_intron_vector(evidence_dict_range, range_now):
    intron_weight_interlap = InterLap()
    coordinate_list = [range_now[0],range_now[1]]

    for ev_id in evidence_dict_range:
        ev_gf = evidence_dict_range[ev_id]
        mRNA = ev_gf.sub_features[0]
        idt_len = mRNA.qualifiers['idt_len']
        query_length = int(mRNA.qualifiers['Target_Length'][0])
        ev_weight_value = get_ev_weight(idt_len, query_length)
        
        # get intron
        cds_coord = []
        for cds in mRNA.sub_features:
            cds_coord.append((cds.start,cds.end))
        
        cds_min  = min([min(i) for i in cds_coord])
        cds_max  = max([max(i) for i in cds_coord])

        intron_coord = interval_minus_set((cds_min,cds_max), cds_coord)

        for intron_start, intron_end in intron_coord:
            intron_weight_interlap.add((intron_start,intron_end,ev_weight_value))
            coordinate_list.append(intron_start)
            coordinate_list.append(intron_end)

    coordinate_list = sorted(list(set(coordinate_list)))

    intron_vector_interlap = InterLap()
    getted_range = {}
    for i in range(0,len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            w_s_total = sum([w for s,e,w in intron_weight_interlap.find((start, start))])
            getted_range[(start, start)] = w_s_total
            intron_vector_interlap.add((start,start,w_s_total))

        if (end, end) not in getted_range:
            w_e_total = sum([w for s,e,w in intron_weight_interlap.find((end, end))])
            getted_range[(end, end)] = w_e_total
            intron_vector_interlap.add((end,end,w_e_total))
        
        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                w_i_total = sum([w for s,e,w in intron_weight_interlap.find(interval)])
                getted_range[interval] = w_i_total
                intron_vector_interlap.add((interval[0],interval[1],w_i_total))
    
    return intron_vector_interlap






def make_intergenic_vector(cds_vector_interlap, intron_vector_interlap):
    # cds_intron_sum 
    coordinate_list = []

    for s,e,w in cds_vector_interlap:
        coordinate_list.append(s)
        coordinate_list.append(e)

    for s,e,w in intron_vector_interlap:
        coordinate_list.append(s)
        coordinate_list.append(e)    

    coordinate_list = sorted(list(set(coordinate_list)))

    intergenic_vector_plus_interlap = InterLap()
    getted_range = {}
    max_cds_intron = 0
    for i in range(0,len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            cds_w = get_vector_score(cds_vector_interlap, start, start)
            intron_w = get_vector_score(intron_vector_interlap, start, start)
            intergenic_vector_plus_interlap.add((start,start,cds_w+intron_w))
            getted_range[(start, start)] = cds_w+intron_w
            if cds_w+intron_w > max_cds_intron:
                max_cds_intron = cds_w+intron_w
        
        if (end, end) not in getted_range:
            cds_w = get_vector_score(cds_vector_interlap, end, end)
            intron_w = get_vector_score(intron_vector_interlap, end, end)
            intergenic_vector_plus_interlap.add((end,end,cds_w+intron_w))
            getted_range[(end, end)] = cds_w+intron_w
            if cds_w+intron_w > max_cds_intron:
                max_cds_intron = cds_w+intron_w
            
        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                cds_w = get_vector_score(cds_vector_interlap, interval[0], interval[1])
                intron_w = get_vector_score(intron_vector_interlap, interval[0], interval[1])
                intergenic_vector_plus_interlap.add((interval[0], interval[1],cds_w+intron_w))
                getted_range[interval] = cds_w+intron_w
                if cds_w+intron_w > max_cds_intron:
                    max_cds_intron = cds_w+intron_w

    intergenic_vector_interlap = InterLap()
    for s,e,w in intergenic_vector_plus_interlap:
        intergenic_vector_interlap.add((s, e, max_cds_intron - w))

    return intergenic_vector_interlap
    




def make_vector(evidence_dict_range, range_now):
    # cds vector
    cds_vector_interlap = make_cds_vector(evidence_dict_range, range_now)
    intron_vector_interlap = make_intron_vector(evidence_dict_range, range_now)
    intergenic_vector_interlap = make_intergenic_vector(cds_vector_interlap, intron_vector_interlap)




    # plot

    fig = plt.figure(figsize=(20, 30))

    ax1 = plt.subplot2grid((3, 1), (0, 0))
    ax2 = plt.subplot2grid((3, 1), (1, 0), sharex=ax1)
    ax3 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)

    ax1.plot(range(range_now[0],range_now[1]), [get_vector_score(cds_vector_interlap, i, i) for i in range(range_now[0],range_now[1])])
    ax2.plot(range(range_now[0],range_now[1]), [get_vector_score(intron_vector_interlap, i, i) for i in range(range_now[0],range_now[1])])
    ax3.plot(range(range_now[0],range_now[1]), [get_vector_score(intergenic_vector_interlap, i, i) for i in range(range_now[0],range_now[1])])

    plt.show()




def pseudogene_plot(contig, start, end, evidence_gf_dict):
    fig = plt.figure(figsize=(20, 10))
    # fig = plt.figure()
    # fig.subplots_adjust(right=2)
    ax = SubplotZero(fig, 1, 1, 1)
    fig.add_subplot(ax)

    # ax limit

    expand_length = int((end - start) * 0.3)

    ax.set_xlim(start - expand_length,
                end + expand_length)
    ax.set_ylim((-len(evidence_gf_dict) - 3), 1)
    ax.set_title('%s:%d-%d' % (contig, start, end))

    # plot
    num = 0
    for id_tmp in evidence_gf_dict:
        gf = evidence_gf_dict[id_tmp]
        num += 1
        gene_structure_plot(ax, gf, plot_feature_types=[
                            'CDS'], width=0.5, horizon=-num)

        # pseudo site
        if "Note" in gf.qualifiers and gf.qualifiers["Note"][0] == "pseudogene":
            for sub_gf in gf.sub_features:
                if "Note_stop_code" in sub_gf.qualifiers:
                    for site in sub_gf.qualifiers["Note_stop_code"]:
                        exon_box(ax, int(site), int(site),
                                 edgecolor='r', width=0.5, horizon=-num)
                if "Note_frame_shift" in sub_gf.qualifiers:
                    for site in sub_gf.qualifiers["Note_frame_shift"]:
                        exon_box(ax, int(site), int(site),
                                 edgecolor='r', width=0.5, horizon=-num)

    # axis set
    for direction in ["left", "right", "bottom", "top"]:
        # hides borders
        ax.axis[direction].set_visible(False)

    for direction in ["xzero"]:
        # adds arrows at the ends of each axis
        ax.axis[direction].set_axisline_style("-|>")

        # adds X and Y-axis from the origin
        ax.axis[direction].set_visible(True)

    ax.get_yaxis().set_visible(False)
    plt.show()


if __name__ == "__main__":
    class abc():
        pass

    args = abc()

    args.WPGmapper_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/T267555N0C000.WPGmaper.new.skip_all"
    args.reference_genome_table = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/ref.xlsx"
    args.target_genome_fasta = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/T267555N0C000.WPGmaper.new.skip_all/T267555N0C000.genome.fasta"
    args.OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ortho/protein/OrthoFinder/Results_Oct06/Orthogroups/Orthogroups.tsv"
    args.output_dir = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/T267555N0C000.WPGmaper.new.skip_all.pseudo.test'

    # A valid evidence alignment region needs to account for at least min_cover of the reference gene
    args.min_cover = 0.5

    # A valid evidence alignment region needs at least min_aa_len in reference gene
    args.min_aa_len = 50

    # A valid evidence alignment region needs at least min_identity in genewise indentity
    args.min_identity = 0.2

    # A valid evidence alignment region needs at least min_identity in genewise indentity
    args.min_score = 50

    args.min_OG_support = 2

    args.min_av_supp_score = 200

    args.min_cluster_supp = 2

    # # Ignore if a evidence that the coverage in the discussion range is less than args.evidence_range_cover
    # args.evidence_range_cover = 0.5

    # # The area of evidence alignment that accounts for less than 50% of the reference gene is considered to be a gene fragment
    # args.gene_fragment_ratio = 0.5

    # # Events within event_range bases will be treated as the same event
    # args.event_range = 20

    # # Each event requires at least min_support_ratio evidence to support
    # args.min_support_ratio = 0.6

    # # Each event requires at least min_support_evidence_num evidence to support
    # args.min_support_evidence_num = 3

    # args.similarity_type = 'jaccord_score'
    
    # args.similarity_threshold = 0.6

    args.threads = 20

    # whole genome pseudogene calling
    pseudogene_main(args)











