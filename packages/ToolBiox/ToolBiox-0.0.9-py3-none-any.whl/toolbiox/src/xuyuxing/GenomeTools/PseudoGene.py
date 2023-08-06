import os
import re
import pickle
import pandas as pd
from itertools import combinations
from collections import Counter
from interlap import InterLap
from toolbiox.lib.common.os import multiprocess_running
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init
from toolbiox.api.xuyuxing.comp_genome.orthofinder import OG_tsv_file_parse
from toolbiox.lib.common.sqlite_command import sqlite_execute
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
from toolbiox.lib.common.math.interval import overlap_between_interval_set, group_by_intervals_with_overlap_threshold
from toolbiox.api.common.genome.blast import outfmt6_read_big
from toolbiox.lib.common.genome.genome_feature2 import get_gf_db_meta_dict, gf_info_retrieval, write_gff_file, read_gff_file, get_mRNA_overlap, convert_dict_structure
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, extract_seq_from_sqlite, write_fasta
from toolbiox.src.xuyuxing.GenomeTools.WPGmapper import load_map_files, extract_all_evidences


def min_cds_start(cds_range_list):
    return min([min(i) for i in cds_range_list])


def get_overlap_ratio(gf1, gf2, similarity_type):
    gf1_cds_interval = [(j.start, j.end)
                        for j in gf1.sub_features[0].sub_features]
    gf2_cds_interval = [(j.start, j.end)
                        for j in gf2.sub_features[0].sub_features]

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
        gf1_cds_interval, gf2_cds_interval, similarity_type=similarity_type)

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
            grouped_flag = False
            for g_id in range(len(merged)-1, -1, -1):
                grouped_flag = higher_in_lower_group(
                    merged[g_id], higher, cds_interval_dict, similarity_type, threshold)
                if grouped_flag == True:
                    merged[g_id].append(higher)
                    break

            if not grouped_flag:
                merged[num] = [higher]
                num += 1

    return merged


def evidence_cluster(evidence_dict, similarity_type='jaccord_score', threshold=0.3):
    if len(evidence_dict) > 0:

        # CDS interval list
        cds_interval_dict = {}
        gene_interval_dict = {}
        for i in evidence_dict:
            # if not evidence_dict[i].map_quality_pass:
            #     continue

            gene_interval_dict[i] = (
                evidence_dict[i].start, evidence_dict[i].end)
            cds_interval_dict[i] = [
                (j.start, j.end) for j in evidence_dict[i].sub_features[0].sub_features]

        big_group_dict = group_by_intervals_with_overlap_threshold(
            gene_interval_dict, 0)

        # merge intervals into cluster
        ev_cluster_dict = {}
        num = 0
        for bg_id in big_group_dict:
            # print(bg_id)
            cds_interval_dict_in_group = {
                ev_id: cds_interval_dict[ev_id] for ev_id in big_group_dict[bg_id]['list']}

            ev_cluster_dict_in_group = merge_evidence_by_cds_intervals_identity(
                list(cds_interval_dict_in_group.keys()), cds_interval_dict_in_group, similarity_type, threshold)

            for i in ev_cluster_dict_in_group:
                num += 1
                ev_cluster_dict[num] = ev_cluster_dict_in_group[i]

        return ev_cluster_dict

    else:
        return Counter()


def mark_cluster_supp_score(evidence_dict):

    evidence_cluster_dict = evidence_cluster(
        evidence_dict, similarity_type='jaccord_score', threshold=0.7)

    cluster_support_dict = {}
    for i in evidence_cluster_dict:
        length = len(evidence_cluster_dict[i])
        for j in evidence_cluster_dict[i]:
            cluster_support_dict[j] = length

    output_dict = {}
    for cl_id in evidence_cluster_dict:
        # cl_id_rank = sorted(
        #     evidence_cluster_dict[cl_id], key=lambda x: evidence_dict[x].score_dict['score'], reverse=True)
        cl_id_rank = sorted(
            evidence_cluster_dict[cl_id], key=lambda x: evidence_dict[x].score_dict['bit_score'], reverse=True)
        for i in evidence_cluster_dict[cl_id]:
            gf = evidence_dict[i]
            gf.evidence_indicator["cluster_support"] = cluster_support_dict[i]
            gf.evidence_indicator["cluster_rank"] = cl_id_rank.index(i)
            gf.evidence_indicator["cluster_id"] = cl_id
            output_dict[i] = gf

    return output_dict


def mark_map_quality_for_gf_dict(input_gf_dict, args):
    for ev_id in input_gf_dict:
        # quality control
        coverage_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= args.min_cover
        aln_aa_len_flag = input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= args.min_aa_len
        identity_flag = input_gf_dict[ev_id].evidence_indicator["identity"] >= args.min_identity
        score_flag = input_gf_dict[ev_id].evidence_indicator["score"] >= args.min_score
        cluster_support_flag = input_gf_dict[ev_id].evidence_indicator["cluster_support"] >= args.min_cluster_supp
        OG_support_flag = input_gf_dict[ev_id].evidence_indicator["OG_support"][0] >= args.min_OG_support
        parent_evalue_flag = input_gf_dict[ev_id].parent_blast["evalue"] <= args.evalue
        parent_blast_identity_flag = input_gf_dict[ev_id].parent_blast["identity"] >= args.min_identity
        # support_score_flag = input_gf_dict[ev_id].score_dict["average_supp_score"] > args.min_av_supp_score

        # Special arrow
        special_arrow_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= 0.8 and input_gf_dict[ev_id].evidence_indicator["identity"] >= 0.9 and input_gf_dict[
            ev_id].parent_blast["identity"] >= 0.9 and input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= 200 and input_gf_dict[ev_id].parent_blast["evalue"] <= 1e-30

        # if coverage_flag and aln_aa_len_flag and identity_flag and score_flag and OG_support_flag and support_score_flag and cluster_support_flag:
        if coverage_flag and aln_aa_len_flag and identity_flag and score_flag and OG_support_flag and cluster_support_flag and parent_evalue_flag and parent_blast_identity_flag:
            input_gf_dict[ev_id].map_quality_pass = True
        elif score_flag and special_arrow_flag:
            input_gf_dict[ev_id].map_quality_pass = True
        else:
            input_gf_dict[ev_id].map_quality_pass = False

    return input_gf_dict


def mark_score_rank_for_gf_dict(input_gf_dict):
    gf_score_dict = {}
    for i in input_gf_dict:
        gf = input_gf_dict[i]
        # average_supp_score = gf.score_dict["average_supp_score"]
        # score = gf.score_dict["score"]
        score = gf.score_dict["bit_score"]
        # gf_score_dict[i] = [average_supp_score, score]
        gf_score_dict[i] = [score]

    # get rank score
    # support_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][0], reverse=True)
    self_rank = sorted(list(gf_score_dict.keys()),
                       key=lambda x: gf_score_dict[x][0], reverse=True)

    for i in gf_score_dict:
        gf_score_dict[i].append((self_rank.index(i) + 1))

    output_gf_dict = {}
    for i in gf_score_dict:
        gf = input_gf_dict[i]

        gf.score_dict["self_rank"] = gf_score_dict[i][1]

        output_gf_dict[i] = gf

    return output_gf_dict


def mark_exclusivity_for_gf_dict(input_gf_dict):
    ev_id_list = list(input_gf_dict.keys())

    score_pair_dict = {}
    for i, j in combinations(ev_id_list, 2):
        score_pair_dict[(i, j)] = get_overlap_ratio(
            input_gf_dict[i], input_gf_dict[j], 'shorter_overlap_coverage')

    output_gf_dict = {}
    for ev_id_i in ev_id_list:
        gf = input_gf_dict[ev_id_i]
        exclusivity_list = []
        for ev_id_j in ev_id_list:
            if ev_id_i == ev_id_j:
                continue
            if (ev_id_i, ev_id_j) in score_pair_dict:
                overlap_ratio = score_pair_dict[(ev_id_i, ev_id_j)]
            else:
                overlap_ratio = score_pair_dict[(ev_id_j, ev_id_i)]

            if overlap_ratio > 0.1:
                exclusivity_list.append(ev_id_j)
        gf.exclusivity = exclusivity_list
        gf.exclusivity.append(ev_id_i)
        output_gf_dict[ev_id_i] = gf

    return output_gf_dict

# greedy algorithm


def greedy_get_rep(ev_in_cluster_dict):
    gf_score_rank = sorted(list(ev_in_cluster_dict.keys(
    )), key=lambda x: ev_in_cluster_dict[x].score_dict["self_rank"])

    rep_gf_list = []
    ex_gf_set = set()
    for i in gf_score_rank:
        if i not in ex_gf_set:
            rep_gf_list.append(i)
            ex_gf_set = ex_gf_set | set(ev_in_cluster_dict[i].exclusivity)

    for i in ev_in_cluster_dict:
        if i in rep_gf_list:
            ev_in_cluster_dict[i].is_rep = True
        else:
            ev_in_cluster_dict[i].is_rep = False

    return ev_in_cluster_dict


def rep_gf_cluster(ev_in_cluster_dict):

    ev_in_cluster_dict = mark_score_rank_for_gf_dict(ev_in_cluster_dict)
    ev_in_cluster_dict = mark_exclusivity_for_gf_dict(ev_in_cluster_dict)
    ev_in_cluster_dict = greedy_get_rep(ev_in_cluster_dict)

    return ev_in_cluster_dict


def rep_gf_judge(evidence_dict):
    # give me cleaned evidence_dict
    evidence_dict_cleaned = {
        i: evidence_dict[i] for i in evidence_dict if evidence_dict[i].map_quality_pass}
    output_dict = {i: evidence_dict[i]
                   for i in evidence_dict if not evidence_dict[i].map_quality_pass}

    # for jaccord cluster only use highest ev
    j_cl_dict = {}
    for i in evidence_dict_cleaned:
        gf = evidence_dict_cleaned[i]
        cl_id = gf.evidence_indicator['cluster_id']
        if cl_id not in j_cl_dict:
            j_cl_dict[cl_id] = []
        j_cl_dict[cl_id].append(gf.id)

    cl_best_rep_list = []
    for cl_id in j_cl_dict:
        cl_best_rep = min(
            j_cl_dict[cl_id], key=lambda x: evidence_dict[x].evidence_indicator['cluster_rank'])
        cl_best_rep_list.append(cl_best_rep)

    for i in evidence_dict_cleaned:
        if i not in cl_best_rep_list:
            output_dict[i] = evidence_dict[i]

    evidence_dict_cleaned = {i: evidence_dict[i] for i in cl_best_rep_list}

    #
    evidence_cluster_dict = evidence_cluster(
        evidence_dict_cleaned, similarity_type='shorter_overlap_coverage', threshold=0.1)

    evidence_cluster_dict_hash = {}
    for cl_id in evidence_cluster_dict:
        for gf_id in evidence_cluster_dict[cl_id]:
            evidence_cluster_dict_hash[gf_id] = cl_id

    for cl_id in evidence_cluster_dict:

        ev_in_cluster_dict = {
            ev_id: evidence_dict_cleaned[ev_id] for ev_id in evidence_cluster_dict[cl_id]}
        ev_in_cluster_dict = rep_gf_cluster(ev_in_cluster_dict)

        for ev_id in ev_in_cluster_dict:
            gf = ev_in_cluster_dict[ev_id]
            gf.cl_id = evidence_cluster_dict_hash[gf.id]
            output_dict[ev_id] = gf

    return output_dict


def filter_known_gene(evidence_dict, known_gene_gff, similarity_type='shorter_overlap_coverage', threshold=0.5):

    gff_dict = read_gff_file(known_gene_gff)
    gene_dict, chr_dict = convert_dict_structure(gff_dict)

    chr_interlap_dict = {}
    for contig in chr_dict:
        chr_interlap_dict[contig] = {}
        for strand in chr_dict[contig]:
            chr_interlap_dict[contig][strand] = InterLap()
            ranges = [(chr_dict[contig][strand][i].start, chr_dict[contig][strand]
                       [i].end, chr_dict[contig][strand][i]) for i in chr_dict[contig][strand]]
            if len(ranges) > 0:
                chr_interlap_dict[contig][strand].update(ranges)

    output_gf_dict = {}
    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]

        overlaped_gene = []
        if ev_gf.chr_id in chr_interlap_dict and ev_gf.strand in chr_interlap_dict[ev_gf.chr_id]:
            for g_s, g_e, gene_gf in chr_interlap_dict[ev_gf.chr_id][ev_gf.strand].find((ev_gf.start, ev_gf.end)):

                overlap_flag = False

                for m1 in ev_gf.sub_features:
                    if overlap_flag:
                        break
                    for m2 in gene_gf.sub_features:
                        if overlap_flag:
                            break
                        if get_mRNA_overlap(m1, m2, similarity_type) > threshold:
                            overlap_flag = True
                            print(ev_id)

                if overlap_flag:
                    overlaped_gene.append(gene_gf.id)

        ev_gf.overlaped_gene_list = overlaped_gene

        if len(overlaped_gene) > 0 and ev_gf and hasattr(ev_gf, 'is_rep') and ev_gf.is_rep:
            ev_gf.is_rep = False

        output_gf_dict[ev_id] = ev_gf

    return output_gf_dict


def get_ortho_support(OG_tsv_file):

    OG_dict = OG_tsv_file_parse(OG_tsv_file)
    seq_support_dict = {}
    for OG_id in OG_dict:
        empty_num = len([i for i in OG_dict[OG_id] if len(
            OG_dict[OG_id][i]) == 1 and OG_dict[OG_id][i][0] == ''])
        total_num = len(OG_dict[OG_id])
        support_num = total_num - empty_num

        for i in OG_dict[OG_id]:
            for j in OG_dict[OG_id][i]:
                if j == '':
                    continue
                seq_support_dict[j] = (support_num, total_num)

    return seq_support_dict


def contig_parser(evidence_dict, args):
    evidence_dict = mark_cluster_supp_score(evidence_dict)
    evidence_dict = mark_map_quality_for_gf_dict(evidence_dict, args)
    evidence_dict = rep_gf_judge(evidence_dict)
    return evidence_dict


def pseudogene_main(args):
    logger_file = args.output_prefix+".log"
    logger = logging_init("PseudoGene", logger_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    logger.info("Read input data from argument list")

    fasta_dict = read_fasta_by_faidx(args.target_genome_fasta)
    contig_dict = {i: fasta_dict[i].len() for i in fasta_dict}

    # load WPGmapper data

    ref_db = pd.read_excel(args.reference_genome_table)
    ref_taxon_id_list = []
    for index in ref_db.index:
        taxon_id = str(ref_db.loc[index]['id'])
        if not pd.isna(taxon_id):
            ref_taxon_id_list.append(taxon_id)

    ref_WPGmapper_dict = load_map_files(
        ref_taxon_id_list, args.WPGmapper_dir)

    # load all evidences
    logger.info("Load all evidences")
    evidence_all_dict_pyb = args.output_prefix+".evidence_all_dict.pyb"
    if os.path.exists(evidence_all_dict_pyb):
        TEMP = open(evidence_all_dict_pyb, 'rb')
        evidence_all_dict = pickle.load(TEMP)
        TEMP.close()
    else:
        seq_support_dict = get_ortho_support(args.OG_tsv_file)
        evidence_meta_dict = extract_all_evidences(
            ref_WPGmapper_dict, evidence_id_list=None, seq_support_dict=seq_support_dict, num_thread=args.threads, log_file=logger_file)

        evidence_all_dict = {}
        for contig in contig_dict:
            evidence_all_dict[contig] = {}
            for strand in ['+', '-']:
                evidence_all_dict[contig][strand] = {}

        for i in evidence_meta_dict:
            gf = evidence_meta_dict[i]
            evidence_all_dict[gf.chr_id][gf.strand][i] = gf

        OUT = open(evidence_all_dict_pyb, 'wb')
        pickle.dump(evidence_all_dict, OUT)
        OUT.close()

    # parse a contig
    logger.info("Parse pseudogene by bins")
    args_list = []
    for contig in contig_dict:
        for strand in ['+', '-']:
            for index, start, end in split_sequence_to_bins(contig_dict[contig], 500000):
                evidence_dict = {i: evidence_all_dict[contig][strand][i] for i in evidence_all_dict[contig][strand]
                                 if evidence_all_dict[contig][strand][i].start <= end and evidence_all_dict[contig][strand][i].end >= start}
                # print(contig,strand,start,end,len(evidence_dict))

                if len(evidence_dict) > 0:
                    args_list.append((evidence_dict, args))

    mp_output = multiprocess_running(
        contig_parser, args_list, args.threads, silence=True, log_file=logger_file)

    huge_evidence_dict = {}
    for i in mp_output:
        evidence_dict = mp_output[i]['output']
        for j in evidence_dict:
            huge_evidence_dict[j] = evidence_dict[j]

    logger.info("filter by known gene")

    huge_evidence_dict = filter_known_gene(
        huge_evidence_dict, args.known_gene_gff, similarity_type='shorter_overlap_coverage', threshold=0.5)

    logger.info("Make report to output")

    all_evidence_list = [huge_evidence_dict[i] for i in huge_evidence_dict]
    map_quality_passed_gf_list = [huge_evidence_dict[i]
                                  for i in huge_evidence_dict if huge_evidence_dict[i].map_quality_pass]
    rep_gf_list = [huge_evidence_dict[i] for i in huge_evidence_dict if hasattr(
        huge_evidence_dict[i], 'is_rep') and huge_evidence_dict[i].is_rep]

    rep_prot_hash = {}
    for gf in rep_gf_list:
        q_id = gf.db_path.split(".")[0]
        if q_id not in rep_prot_hash:
            rep_prot_hash[q_id] = []
        rep_prot_hash[q_id].append(gf.id)

    rep_pt_fasta = args.output_prefix + ".pt.fasta"
    rep_prot_dict = {}
    for q_id in rep_prot_hash:
        gf_id_list = rep_prot_hash[q_id]
        db_name = ref_WPGmapper_dict[q_id]['pep_db']
        gf_seq_dict = extract_seq_from_sqlite(gf_id_list, db_name)
        for i in gf_seq_dict:
            rep_prot_dict[i] = gf_seq_dict[i]

    write_fasta([rep_prot_dict[i] for i in rep_prot_dict],
                rep_pt_fasta, wrap_length=75, upper=True)

    rep_cds_fasta = args.output_prefix + ".cds.fasta"
    rep_prot_dict = {}
    for q_id in rep_prot_hash:
        gf_id_list = rep_prot_hash[q_id]
        db_name = ref_WPGmapper_dict[q_id]['cds_db']
        gf_seq_dict = extract_seq_from_sqlite(gf_id_list, db_name)
        for i in gf_seq_dict:
            rep_prot_dict[i] = gf_seq_dict[i]

    write_fasta([rep_prot_dict[i] for i in rep_prot_dict],
                rep_cds_fasta, wrap_length=75, upper=True)

    all_gff_file = args.output_prefix + ".all.gff3"
    passed_gff_file = args.output_prefix + ".passed.gff3"
    rep_gff_file = args.output_prefix + ".rep.gff3"

    write_gff_file(all_evidence_list, all_gff_file)
    write_gff_file(map_quality_passed_gf_list, passed_gff_file)
    write_gff_file(rep_gf_list, rep_gff_file)

    detail_output_file = args.output_prefix + ".detail.tsv"

    with open(detail_output_file, 'w') as f:
        header = ["gf_id", "chr_id", "strand", "start", "end", "q_id", "q_len", "q_start", "q_end", "q_cover", "q_identity", "q_aln_length", "genewise_score",  "diamond_identity",
                  "diamond_hit_rank", "diamond_bit_score", "diamond_evalue", "OG_support", "r1_cl_id", "r1_cl_support", "map_quality_pass", "r1_cl_rank", "r2_cl_id", "r2_cl_rank", "overlap_with_gene", "is_rep"]
        f.write(printer_list(header)+"\n")

        for gf_id in sorted(huge_evidence_dict, key=lambda x: (huge_evidence_dict[x].chr_id, huge_evidence_dict[x].strand, huge_evidence_dict[x].start)):
            gf = huge_evidence_dict[gf_id]
            gf_id = gf_id
            chr_id = gf.chr_id
            strand = gf.strand
            start = gf.start
            end = gf.end
            q_id = gf.id
            q_len = gf.evidence_indicator['query_length']
            q_start = int(gf.sub_features[0].qualifiers['Target_Start'][0])
            q_end = int(gf.sub_features[0].qualifiers['Target_End'][0])
            q_cover = gf.evidence_indicator['query_coverage']
            q_identity = gf.evidence_indicator['identity']
            q_aln_length = gf.evidence_indicator['aln_aa_len']
            # cds_aln_length = gf.score_dict['cds_aln_length']
            OG_support = "%d/%d" % (
                gf.evidence_indicator['OG_support'][0], gf.evidence_indicator['OG_support'][1])
            genewise_score = gf.score_dict['score']
            diamond_bit_score = gf.score_dict['bit_score']
            diamond_identity = gf.parent_blast["identity"]
            diamond_hit_rank = gf.parent_blast["hit_rank"]
            diamond_evalue = gf.parent_blast["evalue"]
            r1_cl_id = gf.evidence_indicator["cluster_id"]
            r1_cl_support = gf.evidence_indicator['cluster_support']
            map_quality_pass = gf.map_quality_pass
            r1_cl_rank = gf.evidence_indicator["cluster_rank"]
            if hasattr(gf, 'cl_id'):
                r2_cl_id = gf.cl_id
                r2_cl_rank = gf.score_dict['self_rank']
                is_rep = gf.is_rep
            else:
                r2_cl_id = None
                r2_cl_rank = None
                is_rep = False

            if hasattr(gf, 'overlaped_gene_list'):
                overlaped_gene_list = gf.overlaped_gene_list
                overlap_with_gene = printer_list(overlaped_gene_list, ', ')
            else:
                overlap_with_gene = ''

            print_list = [gf_id, chr_id, strand, start, end, q_id, q_len, q_start, q_end, q_cover, q_identity, q_aln_length, genewise_score, diamond_identity,
                          diamond_hit_rank, diamond_bit_score, diamond_evalue, OG_support, r1_cl_id, r1_cl_support, map_quality_pass, r1_cl_rank, r2_cl_id, r2_cl_rank, overlap_with_gene, is_rep]
            f.write(printer_list(print_list)+"\n")


if __name__ == "__main__":

    class abc():
        pass

    args = abc()

    args.WPGmapper_dir = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Ath_WPGmapper"
    args.reference_genome_table = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ref.xlsx"
    args.target_genome_fasta = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Ath_WPGmapper/T3702N0.genome.fasta"
    args.OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ortho/protein/OrthoFinder/Results_Oct06/Orthogroups/Orthogroups.tsv"
    args.output_prefix = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/Ath5'
    args.evidence_all_dict_pyb = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/Ath5.evidence_all_dict.pyb'
    args.log_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/Ath5.log'
    args.known_gene_gff = ""

    # A valid evidence alignment region needs to account for at least min_cover of the reference gene
    args.min_cover = 0.5

    args.evalue = 1e-10

    # A valid evidence alignment region needs at least min_aa_len in reference gene
    args.min_aa_len = 50

    # A valid evidence alignment region needs at least min_identity in genewise indentity
    args.min_identity = 0.2

    # A valid evidence alignment region needs at least min_score in genewise score
    args.min_score = 50

    # A valid evidence alignment region needs at least query sequence have min_OG_support orthology from orthofinder
    args.min_OG_support = 2

    # A valid evidence alignment region needs at least min_cluster_supp in jaccord cluster
    args.min_cluster_supp = 2

    args.threads = 80

    # whole genome pseudogene calling
    pseudogene_main(args)

    #
    class abc():
        pass

    args = abc()

    args.WPGmapper_dir = "/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/Gel_WPGmapper"
    args.reference_genome_table = "/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/fungi_genus.xlsx"
    args.target_genome_fasta = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_WPGmapper/Gel.genome.v2.0.fasta"
    args.OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/HGT/6.orthogrouping/6.1.fungi_ortho/pt_files/OrthoFinder/Results_Jul21/WorkingDirectory/OrthoFinder/Results_Jul22_1/Orthogroups/Orthogroups.tsv"
    args.output_prefix = '/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/Gel'
    args.evidence_all_dict_pyb = '/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/Gel.evidence_all_dict.pyb'
    args.log_file = '/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/Gel.log'

    # A valid evidence alignment region needs to account for at least min_cover of the reference gene
    args.min_cover = 0.5

    args.evalue = 1e-10

    # A valid evidence alignment region needs at least min_aa_len in reference gene
    args.min_aa_len = 50

    # A valid evidence alignment region needs at least min_identity in genewise indentity
    args.min_identity = 0.2

    # A valid evidence alignment region needs at least min_score in genewise score
    args.min_score = 50

    # A valid evidence alignment region needs at least query sequence have min_OG_support orthology from orthofinder
    args.min_OG_support = 2

    # A valid evidence alignment region needs at least min_cluster_supp in jaccord cluster
    args.min_cluster_supp = 2

    args.threads = 80

    # whole genome pseudogene calling
    pseudogene_main(args)

    class abc():
        pass

    args = abc()

    args.WPGmapper_dir = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_WPGmapper"
    args.reference_genome_table = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ref.xlsx"
    args.target_genome_fasta = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta"
    args.OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ortho/protein/OrthoFinder/Results_Oct06/Orthogroups/Orthogroups.tsv"
    args.output_prefix = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/redo/Gel'
    args.evidence_all_dict_pyb = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/redo/Gel.evidence_all_dict.pyb'
    args.log_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/redo/Gel.log'
    args.known_gene_gff = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.gff3"

    # A valid evidence alignment region needs to account for at least min_cover of the reference gene
    args.min_cover = 0.5

    args.evalue = 1e-10

    # A valid evidence alignment region needs at least min_aa_len in reference gene
    args.min_aa_len = 50

    # A valid evidence alignment region needs at least min_identity in genewise indentity
    args.min_identity = 0.2

    # A valid evidence alignment region needs at least min_score in genewise score
    args.min_score = 50

    # A valid evidence alignment region needs at least query sequence have min_OG_support orthology from orthofinder
    args.min_OG_support = 2

    # A valid evidence alignment region needs at least min_cluster_supp in jaccord cluster
    args.min_cluster_supp = 2

    args.threads = 80

    # whole genome pseudogene calling
    pseudogene_main(args)
