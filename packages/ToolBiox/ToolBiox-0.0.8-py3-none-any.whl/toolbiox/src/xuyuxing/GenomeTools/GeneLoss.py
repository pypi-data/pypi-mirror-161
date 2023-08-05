from toolbiox.src.xuyuxing.GenomeTools.WPGmapper import load_map_files, extract_all_evidences
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
from toolbiox.lib.common.genome.genome_feature2 import HomoPredictResults
from datetime import datetime
from collections import Counter
from toolbiox.lib.common.math.interval import section, merge_intervals, overlap_between_interval_set, \
    group_by_intervals_with_overlap_threshold, sum_interval_length
from toolbiox.src.xuyuxing.tools.phytools import PtTree
from Bio import Phylo
import pickle
import sqlite3
import re
import os
from interlap import InterLap
from toolbiox.config import wu_blast_path
from BCBio import GFF
from toolbiox.api.xuyuxing.genome.mcl import gene_mcl
from toolbiox.lib.common.sqlite_command import sqlite_select
from toolbiox.lib.common.evolution.tree_operate import monophyly
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init, configure_parser
from toolbiox.api.common.genome.blast import evalue_to_wvalue
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, extract_seq_from_sqlite, write_fasta
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.os import mkdir, cmd_run, multiprocess_running
from toolbiox.api.xuyuxing.genome.genblasta import genblasta_run, genblasta_to_genewise, get_HPR_from_genewise_results, gene_to_aa, \
    gene_to_cds, query_gene_to_speci
from toolbiox.api.xuyuxing.comp_genome.orthofinder import OrthoFinderResults, get_species_id_from_gene_id
import configparser
import argparse
import sys


def if_conserve_and_target_speci_loss(input_GeneSet, target_speci, core_ref_list, norm_ref_list, tolerance_ratio=1.0):
    """
    To say if a gene set is good to say a target speci is lossed
    :param input_GeneSet: GeneSet object from orthofinder
    :param target_speci: "2"
    :param core_ref_list: ["0"]
    :param norm_ref_list: ["1","3","6","7","8","9"]
    :param tolerance_ratio: 0.83

    orthofinder_dir_path = "/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10"

    # parse orthofinder dir
    ortho_obj = OrthoFinderResults(orthofinder_dir_path)
    ortho_obj.get_Orthologues()

    input_GeneSet = ortho_obj.orthologues_dir['OG0000001_0']
    core_ref_list = ["0"]
    norm_ref_list = ["1","3","6","7","8","9"]
    target_speci = "2"
    tolerance_ratio = 0.83

    """
    speci_info_dir = input_GeneSet.speci_stat()
    conserve_flag = False
    target_loss_flag = False
    if (set(core_ref_list) & set(speci_info_dir.keys()) == set(core_ref_list)) and (len(
            set(norm_ref_list) & set(speci_info_dir.keys())) / len(norm_ref_list) >= tolerance_ratio):
        conserve_flag = True

    if conserve_flag and (target_speci not in speci_info_dir):
        target_loss_flag = True

    return conserve_flag, target_loss_flag


def get_hit_evalue_list(query_gene_name_list, db_file):

    content1 = sqlite_select(db_file, "query",
                             column_list=["q_hsp_id"], key_name="qDef",
                             value_tuple=query_gene_name_list)
    if len(content1) == 0:
        return []

    hsp_id_list = []
    for i in content1:
        q_hsp_id_str = i[0]
        for j in q_hsp_id_str.split(","):
            hsp_id_list.append(int(j))

    content2 = sqlite_select(db_file, "hsp",
                             column_list=["query_id", "hit_id", "Hsp_evalue"], key_name="hsp_id",
                             value_tuple=hsp_id_list)
    return content2


def get_homology_gene(query_gene_name_list, blast_results_file, log_file):

    args_list = []
    for blast_pair in blast_results_file:
        db_file = blast_results_file[blast_pair]['db']
        args_list.append((query_gene_name_list, db_file))

    mlt_outdir = multiprocess_running(
        get_hit_evalue_list, args_list, 30, log_file=log_file)

    query_gene_name_hash = {i: 0 for i in query_gene_name_list}

    homology_gene_dict = {}
    for i in mlt_outdir:
        hit_evalue_list_tmp = mlt_outdir[i]['output']
        for query_id, hit_id, Hsp_evalue in hit_evalue_list_tmp:

            if query_id not in homology_gene_dict:
                homology_gene_dict[query_id] = {}

            if hit_id not in homology_gene_dict[query_id]:
                homology_gene_dict[query_id][hit_id] = 0

            homology_gene_dict[query_id][hit_id] = homology_gene_dict[query_id][hit_id] + evalue_to_wvalue(
                float(Hsp_evalue))

    return homology_gene_dict


def tree_check_prepare(OL_gene_list, work_dir, homology_gene_dict, sequences_info, target_speci, core_ref, norm_ref,
                       genewise_dict, annotated_coverage=0.8, outgroup_seq_num=5, full_family_tree=False, threads=10):
    """
    OL_gene_list = OL_gene_list
    work_dir = work_dir
    blast_results_file = ortho_obj.blast_results_file
    sequences_info = ortho_obj.sequences_info
    target_speci = target_speci
    core_ref = core_ref
    norm_ref = norm_ref
    genewise_dict = genewise_dict
    gene_coverage = args.gene_coverage
    annotated_coverage = args.annotated_coverage
    outgroup_seq_num = args.top_outgroup_num
    full_family_tree = False
    """

    mkdir(work_dir, True)

    # get homo seq and new loci seq
    seq_info_file = work_dir + "/seq_info.pyb"
    if not os.path.exists(seq_info_file):
        # load HPR to every query

        # build homology_gene_dir
        query_gene_name_dict = {
            query_gene.id: 0 for query_gene in OL_gene_list}

        homology_gene_dict_in_this_tree = {}
        for q_id in query_gene_name_dict:
            if q_id in homology_gene_dict:
                for h_id in homology_gene_dict[q_id]:
                    if h_id in query_gene_name_dict:
                        continue
                    else:
                        if h_id not in homology_gene_dict_in_this_tree:
                            homology_gene_dict_in_this_tree[h_id] = 0
                        homology_gene_dict_in_this_tree[h_id] += homology_gene_dict_in_this_tree[h_id] + \
                            homology_gene_dict[q_id][h_id]

        # get homology gene
        if full_family_tree:
            homology_gene_list = [sequences_info[get_species_id_from_gene_id(i)][i] for i in
                                  homology_gene_dict]
        else:
            # get top wvalue for each speci
            homology_gene_name_list = list(query_gene_name_dict.keys())
            for speci in core_ref + norm_ref + [target_speci]:
                homology_gene_name_list.extend(
                    sorted([i for i in homology_gene_dict_in_this_tree if get_species_id_from_gene_id(i) == speci],
                           key=lambda x: homology_gene_dict_in_this_tree[x], reverse=True)[0:outgroup_seq_num])
            homology_gene_list = [sequences_info[get_species_id_from_gene_id(i)][i] for i in
                                  homology_gene_name_list]

        # build good_genewise_hit_dir
        good_genewise_hit_dir = {}
        tmp_num = 0
        for query_gene in OL_gene_list:
            tmp_num += 1
            # print(tmp_num)
            if query_gene.species in core_ref + norm_ref:
                # get genewise out from query
                # query should have genewise output
                if query_gene.id in genewise_dict:
                    HPR_tmp = genewise_dict[query_gene.id]
                    query_gene.HPR = HPR_tmp
                    for genewise_hit in query_gene.HPR.hit_gene_list:
                        # HPR should be good: good coverage and new annotation
                        if genewise_hit.map_quality_pass and genewise_hit.new_anno[0]:
                            # put HPR from diff query in chr strand index
                            genewise_hit.query_gene = query_gene
                            hit_chr_loci = genewise_hit.chr_loci
                            if hit_chr_loci.chr_id not in good_genewise_hit_dir:
                                good_genewise_hit_dir[hit_chr_loci.chr_id] = {
                                    "+": {}, "-": {}}
                            good_genewise_hit_dir[hit_chr_loci.chr_id][hit_chr_loci.strand][
                                genewise_hit] = genewise_hit.chr_loci.range

        # merge the same loci, get a new seq file
        new_gene_list = []
        for contig in good_genewise_hit_dir:
            for strand in good_genewise_hit_dir[contig]:
                good_genewise_hit_dir[contig][strand] = group_by_intervals_with_overlap_threshold(
                    good_genewise_hit_dir[contig][strand], annotated_coverage)

                for group_id in good_genewise_hit_dir[contig][strand]:
                    genewise_hit_list = good_genewise_hit_dir[contig][strand][group_id]['list']
                    lengthest_hit = sorted(genewise_hit_list, key=lambda x: len(x.model_aa_seq.seq), reverse=True)[
                        0]
                    good_genewise_hit_dir[contig][strand][group_id]['rep_hit'] = lengthest_hit
                    new_gene_list.append(lengthest_hit)

        # subject will let no ref gene into homology list
        homology_gene_list_filter = [
            i for i in homology_gene_list if i.species in core_ref + norm_ref + [target_speci]]

        pickle_info = (homology_gene_list_filter, new_gene_list)

        OUT = open(seq_info_file, 'wb')
        pickle.dump(pickle_info, OUT)
        OUT.close()


def tree_check(OL_id, OL_gene_list, work_dir, species_info, target_speci, target_speci_raw_name,
               query_in_mcl_cluster_ratio=0.8, support_threshold=0.8, jaccard_threshold=0.8, full_family_tree=False,
               cpu_num=1):
    query_gene_name_list = [query_gene.id for query_gene in OL_gene_list]

    # get homo seq and new loci seq
    seq_info_file = work_dir + "/seq_info.pyb"
    TEMP = open(seq_info_file, 'rb')
    homology_gene_list, new_gene_list = pickle.load(TEMP)
    TEMP.close()

    # if no outgroup
    if len(homology_gene_list) == len(query_gene_name_list):
        # make a report for seq
        OL_seq_report_file = work_dir + "/seq_report.txt"
        with open(OL_seq_report_file, 'w') as f:
            f.write("Seq_ID\tSeq_raw_ID\tSpeci\tSpeci_name\tSeq_type\tSeq\n")
            for query_gene in OL_gene_list:
                print_string = printer_list(
                    [query_gene.id, query_gene.old_name['raw_short_id'], query_gene.species,
                     species_info[query_gene.species]['id'], "query",
                     query_gene.model_aa_seq])
                f.write(print_string + "\n")
            for gene in homology_gene_list:
                if gene not in OL_gene_list:
                    print_string = printer_list([gene.id, gene.old_name['raw_short_id'], gene.species,
                                                 species_info[gene.species]['id'], "homology",
                                                 gene.model_aa_seq])
                    f.write(print_string + "\n")

            for gene in new_gene_list:
                print_string = printer_list([gene.id, None, target_speci, target_speci_raw_name, "genewise",
                                             gene.model_aa_seq])
                f.write(print_string + "\n")

        # if len(new_gene_list) == 0:
        #     return True, "No new genewise"
        # elif len(homology_gene_list) == len(query_gene_name_list):
        #     return False, "No outgroup seq and have new genewise"

        if len(new_gene_list) != 0:
            return False, "No outgroup and have new genewise"
        else:
            return True, "No outgroup and no new genewise"

    else:
        # make tree
        tree_dir = work_dir + "/tree"
        tree_output_dir = tree_dir + "/tree_out"
        tree_file = tree_output_dir + "/tree_out.phb"

        if not os.path.exists(tree_file):
            if full_family_tree:
                # make mcl to get gene cluster
                mcl_info_file = work_dir + "/mcl_info.pyb"
                if not os.path.exists(mcl_info_file):
                    all_gene_list = homology_gene_list + new_gene_list
                    mcl_dir = work_dir + "/mcl"
                    mkdir(mcl_dir, True)
                    mcl_group_dir = gene_mcl(all_gene_list, cpu_num=cpu_num, work_dir=mcl_dir, keep_flag=True,
                                             diamond_flag=True)
                    mcl_group_hash = {}
                    for i in mcl_group_dir:
                        for j in mcl_group_dir[i]:
                            mcl_group_hash[j] = i

                    # found cluster which have query seq
                    best_cluster = sorted(mcl_group_dir,
                                          key=lambda x: len(
                                              set([i.id for i in OL_gene_list]) & set(mcl_group_dir[x])) / len(
                                              OL_gene_list), reverse=True)[0]
                    if len(set([i.id for i in OL_gene_list]) & set(mcl_group_dir[best_cluster])) / len(
                            OL_gene_list) < query_in_mcl_cluster_ratio:
                        OL_cluster = False

                    # make a report for seq
                    OL_seq_report_file = work_dir + "/seq_report.txt"
                    with open(OL_seq_report_file, 'w') as f:
                        f.write(
                            "Seq_ID\tSeq_raw_ID\tSpeci\tSpeci_name\tSeq_type\tCluster\tSeq\n")
                        for query_gene in OL_gene_list:
                            if query_gene.id in mcl_group_hash:
                                cluster_id = mcl_group_hash[query_gene.id]
                            else:
                                cluster_id = None
                            print_string = printer_list(
                                [query_gene.id, query_gene.old_name['raw_short_id'], query_gene.species,
                                 species_info[query_gene.species]['id'], "query",
                                 cluster_id, query_gene.model_aa_seq])
                            f.write(print_string + "\n")
                        for gene in homology_gene_list:
                            if gene not in OL_gene_list:
                                if gene.id in mcl_group_hash:
                                    cluster_id = mcl_group_hash[gene.id]
                                else:
                                    cluster_id = None
                                print_string = printer_list([gene.id, gene.old_name['raw_short_id'], gene.species,
                                                             species_info[gene.species]['id'], "homology",
                                                             cluster_id, gene.model_aa_seq])
                                f.write(print_string + "\n")

                        for gene in new_gene_list:
                            if gene.id in mcl_group_hash:
                                cluster_id = mcl_group_hash[gene.id]
                            else:
                                cluster_id = None
                            print_string = printer_list(
                                [gene.id, None, target_speci, target_speci_raw_name, "genewise",
                                 cluster_id, gene.model_aa_seq])
                            f.write(print_string + "\n")

                    # store pickle
                    pickle_info = (mcl_group_dir, best_cluster)

                    OUT = open(mcl_info_file, 'wb')
                    pickle.dump(pickle_info, OUT)
                    OUT.close()
                else:
                    TEMP = open(mcl_info_file, 'rb')
                    mcl_group_dir, best_cluster = pickle.load(TEMP)
                    TEMP.close()

                # make tree
                all_gene_list = homology_gene_list + new_gene_list
                all_gene_dir = {i.id: i for i in all_gene_list}
                tree_dir = work_dir + "/tree"
                mkdir(tree_dir, True)
                best_cluster_seq_file = tree_dir + "/tree.faa"
                with open(best_cluster_seq_file, 'w') as f:
                    for seq_name in mcl_group_dir[best_cluster]:
                        f.write(">%s\n%s\n" %
                                (seq_name, all_gene_dir[seq_name].model_aa_seq))

                PtTree(best_cluster_seq_file, 'fasttree', False,
                       tree_output_dir, cpu_num, "clustalo")

            else:
                # make tree
                all_gene_list = homology_gene_list + new_gene_list
                all_gene_dir = {i.id: i for i in all_gene_list}
                tree_dir = work_dir + "/tree"
                mkdir(tree_dir, True)
                top_tree_seq_file = tree_dir + "/tree.faa"
                with open(top_tree_seq_file, 'w') as f:
                    for seq_name in all_gene_dir:
                        f.write(">%s\n%s\n" %
                                (seq_name, all_gene_dir[seq_name].model_aa_seq))

                PtTree(top_tree_seq_file, 'fasttree', False,
                       tree_output_dir, cpu_num, "clustalo")

        # tree check
        query_gene_name_list = [query_gene.id for query_gene in OL_gene_list]
        new_gene_name_list = [gene.id for gene in new_gene_list]
        target_speci_gene_name_list = [
            gene.id for gene in homology_gene_list if gene.species == target_speci]

        tree = Phylo.read(tree_file, 'newick')
        good_topo, monophyly_leaf = monophyly(query_gene_name_list, tree, support_threshold=support_threshold,
                                              jaccard_threshold=jaccard_threshold, exclude_leaf_set=new_gene_name_list)

        added_new_gene = list(set(new_gene_name_list) & set(monophyly_leaf)) + list(
            set(target_speci_gene_name_list) & set(monophyly_leaf))

        # make a report for seq
        if good_topo:
            Tree_Check = "good_topo"
        else:
            Tree_Check = "bad_topo"

        OL_seq_report_file = work_dir + "/seq_report.txt"
        with open(OL_seq_report_file, 'w') as f:
            f.write(
                "Seq_ID\tSeq_raw_ID\tSpeci\tSpeci_name\tSeq_type\tTree_Check\tSeq\n")
            for query_gene in OL_gene_list:
                print_string = printer_list(
                    [query_gene.id, query_gene.old_name['raw_short_id'], query_gene.species,
                     species_info[query_gene.species]['id'], "query", Tree_Check,
                     query_gene.model_aa_seq])
                f.write(print_string + "\n")
            for gene in homology_gene_list:
                if gene not in OL_gene_list:
                    if gene.id in added_new_gene:
                        print_string = printer_list(
                            [gene.id, gene.old_name['raw_short_id'], gene.species, species_info[gene.species]['id'],
                             "homology", "add", gene.model_aa_seq])
                    else:
                        print_string = printer_list([gene.id, gene.old_name['raw_short_id'], gene.species,
                                                     species_info[gene.species]['id'], "homology", "None",
                                                     gene.model_aa_seq])
                    f.write(print_string + "\n")

            for gene in new_gene_list:
                if gene.id in added_new_gene:
                    print_string = printer_list(
                        [gene.id, None, target_speci, target_speci_raw_name, "genewise", "add",
                         gene.model_aa_seq])
                else:
                    print_string = printer_list(
                        [gene.id, None, target_speci, target_speci_raw_name, "genewise", "None",
                         gene.model_aa_seq])
                f.write(print_string + "\n")

        if good_topo:
            if len(new_gene_list) == 0:
                return True, "Good topo and no added gene"

            if len(added_new_gene):
                return False, added_new_gene
            else:
                return True, "Good topo and no added gene"
        else:
            if len(new_gene_list) == 0:
                return True, "Bad topo but no new gene"
            else:
                return False, "Bad topo"


def get_query_id_from_HPR_id(HPR_id):
    return re.sub('_\d+$', '', HPR_id)


def mark_map_quality_for_gf_dict(input_gf_dict, args):
    for ev_id in input_gf_dict:
        # quality control
        coverage_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= args.min_cover
        aln_aa_len_flag = input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= args.min_aa_len
        identity_flag = input_gf_dict[ev_id].evidence_indicator["identity"] >= args.min_identity
        score_flag = input_gf_dict[ev_id].evidence_indicator["score"] >= args.min_score
        # parent_evalue_flag = input_gf_dict[ev_id].parent_blast["evalue"] <= args.evalue
        # parent_blast_identity_flag = input_gf_dict[ev_id].parent_blast["identity"] >= args.min_identity

        # Special arrow
        # special_arrow_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= 0.8 and input_gf_dict[ev_id].evidence_indicator["identity"] >= 0.9 and input_gf_dict[
        #     ev_id].parent_blast["identity"] >= 0.9 and input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= 200 and input_gf_dict[ev_id].parent_blast["evalue"] <= 1e-30

        # if coverage_flag and aln_aa_len_flag and identity_flag and score_flag and parent_evalue_flag and parent_blast_identity_flag:
        if coverage_flag and aln_aa_len_flag and identity_flag and score_flag:
            input_gf_dict[ev_id].map_quality_pass = True
        # elif score_flag and special_arrow_flag:
        #     input_gf_dict[ev_id].map_quality_pass = True
        else:
            input_gf_dict[ev_id].map_quality_pass = False

    return input_gf_dict


def get_HPR_from_evidence_dict(query_gene_dict, evidence_dict, ref_WPGmapper_dict, subject_species=None):
    hit_gene_dir = {}
    for gf_id in evidence_dict:
        gf = evidence_dict[gf_id]
        query_id = gf.evidence_indicator['query_id']

        if not query_id in hit_gene_dir:
            hit_gene_dir[query_id] = []
        hit_gene_dir[query_id].append(gf)

    output_list = []
    for query_id in hit_gene_dir:
        query_gene = query_gene_dict[query_id]
        output_list.append(
            HomoPredictResults(query_gene, subject_species=subject_species, hit_gene_list=hit_gene_dir[query_id]))

    return output_list


def GeneLoss_main(args):
    mkdir(args.tmp_path, True)

    logger = logging_init("GeneLoss", args.log_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    # # todo next row is test
    # return True

    logger.info("Step1: parse orthofinder dir")
    ortho_obj = OrthoFinderResults(args.orthofinder_dir_path)

    # get file and dir info
    if not hasattr(args, 'modify_dict'):
        args.modify_dict = {}

    ortho_obj.pase_file_and_dir(modify_dict=args.modify_dict)

    # get orthologues or orthogroups
    ortho_obj.get_name_info(hash_table=True)
    if args.ortho_level == 'orthologues':
        ortho_obj.get_Orthologues()
        group_dir = ortho_obj.orthologues_dir

    elif args.ortho_level == 'orthogroups':
        ortho_obj.get_OrthoGroups()
        group_dir = ortho_obj.orthogroup_dir

    ortho_obj.read_aa_fasta()
    ortho_obj.blast_to_sqlite(threads=args.num_threads)

    # get candidate gene loss orthologues
    logger.info("Step2: get candidate gene loss orthologues")
    target_speci = [
        i for i in ortho_obj.species_info if ortho_obj.species_info[i]['id'] == args.target_speci][0]
    core_ref = [i for i in ortho_obj.species_info if ortho_obj.species_info[i]
                ['id'] in args.core_ref.split(',')]
    norm_ref = [i for i in ortho_obj.species_info if ortho_obj.species_info[i]
                ['id'] in args.norm_ref.split(',')]

    candidate_gene_loss = args.output_dir + "/1.candidate_gene_loss.txt"
    candi_loss_list = []
    conserved_OL_list = []

    if not os.path.exists(candidate_gene_loss):
        logger.info("first running Step2")
        for OL_id in group_dir:
            conserve_flag, target_loss_flag = if_conserve_and_target_speci_loss(group_dir[OL_id],
                                                                                target_speci,
                                                                                core_ref, norm_ref,
                                                                                args.tolerance_ratio)
            group_dir[OL_id].target_loss_flag = target_loss_flag
            group_dir[OL_id].conserve_flag = conserve_flag
            if target_loss_flag:
                candi_loss_list.append(OL_id)
            if conserve_flag:
                conserved_OL_list.append(OL_id)

        print_speci_list = args.core_ref.split(
            ',') + args.norm_ref.split(',') + args.target_speci.split(',')
        print_speci_id_list = []
        for i in print_speci_list:
            print_speci_id_list.append(
                [j for j in ortho_obj.species_info if ortho_obj.species_info[j]['id'] == i][0])

        with open(candidate_gene_loss, 'w') as f:
            f.write(printer_list(print_speci_list, head='OL_id\t') + "\n")
            for OL_id in conserved_OL_list:
                gene_set = group_dir[OL_id]
                speci_stat_dir = gene_set.speci_stat()
                gene_num_list = []
                for i in print_speci_id_list:
                    if i in speci_stat_dir:
                        gene_num_list.append(speci_stat_dir[i])
                    else:
                        gene_num_list.append(0)
                f.write(printer_list(gene_num_list, head=OL_id + "\t") + "\n")
    else:
        logger.info(
            "find 1.candidate_gene_loss.txt, get gene loss list from this file")
        gene_loss_dict = tsv_file_dict_parse(candidate_gene_loss)
        for i in gene_loss_dict:
            conserved_OL_list.append(gene_loss_dict[i]['OL_id'])
            if int(gene_loss_dict[i][args.target_speci]) == 0:
                candi_loss_list.append(gene_loss_dict[i]['OL_id'])

    logger.info("Step2: get %d conserved orthologues in which %d may lost in %s" % (
        len(conserved_OL_list), len(candi_loss_list), args.target_speci))

    # # todo next row is test
    # candi_loss_list = candi_loss_list[0:10]

    # get sequence of loss ortho
    logger.info("Step3: check if annotation error make gene loss in %s" %
                args.target_speci)

    # test if need redo
    genewise_dict_file = args.output_dir + "/2.genewise_dict.pyb"
    if not os.path.exists(genewise_dict_file):
        logger.info("Step3.1: load data from WPGmapper")

        speci_id_map = {}
        if hasattr(args, 'orthofinder_wpgmapper_id_map'):
            file_info = tsv_file_parse(args.orthofinder_wpgmapper_id_map)
            for i in file_info:
                OF_id, WPG_id = file_info[i]
                speci_id_map[OF_id] = WPG_id

        query_gene_dict = {}
        ref_gene_in_candi_loss_OL = []
        WPGmapper_species_id_list = []
        for OL_id in candi_loss_list:
            gene_set = group_dir[OL_id]
            for gene in gene_set.gene_list:
                if gene.species in core_ref + norm_ref:
                    query_gene_dict[gene.old_name['raw_short_id']] = gene

                    ref_gene_in_candi_loss_OL.extend(
                        [gene.old_name['raw_short_id']+"_"+str(i) for i in range(args.top_evidence_num)])

                    species_old_id = ortho_obj.species_info[gene.species]['id']
                    if species_old_id in speci_id_map:
                        species_old_id = speci_id_map[species_old_id]

                    if species_old_id not in WPGmapper_species_id_list:
                        WPGmapper_species_id_list.append(species_old_id)

        ref_WPGmapper_dict = load_map_files(
            WPGmapper_species_id_list, args.wpgmapper_dir)
        evidence_dict = extract_all_evidences(
            ref_WPGmapper_dict, evidence_id_list=ref_gene_in_candi_loss_OL, log_file=args.log_file)
        evidence_dict = mark_map_quality_for_gf_dict(evidence_dict, args)

        logger.info("Step3.1: begin compare")
        # load genewise output
        genewise_out = get_HPR_from_evidence_dict(
            query_gene_dict, evidence_dict, ref_WPGmapper_dict, subject_species=target_speci)

        # load annotated range
        annotated_range_dict = {}
        gene_cds_intervals_dict = {}
        with open(args.target_speci_annotation, 'r') as in_handle:
            for rec in GFF.parse(in_handle):
                if rec.id not in annotated_range_dict:
                    annotated_range_dict[rec.id] = {}
                    annotated_range_dict[rec.id]["+"] = InterLap()
                    annotated_range_dict[rec.id]["-"] = InterLap()
                for gene in rec.features:
                    if args.target_speci_feature == 'None' or gene.type == args.target_speci_feature:
                        start_tmp = gene.location.start.position + 1
                        end_tmp = gene.location.end.position
                        if gene.id == "":
                            gene.id = list(
                                set(gene.qualifiers.keys()) - {'source'})[0]
                        if gene.strand == 1:
                            annotated_range_dict[rec.id]["+"].add(
                                (start_tmp, end_tmp, gene.id))
                        else:
                            annotated_range_dict[rec.id]["-"].add(
                                (start_tmp, end_tmp, gene.id))

                        gene_cds_intervals_dict[gene.id] = [(int(i.location.start)+1, int(
                            i.location.end)) for i in gene.sub_features[0].sub_features if i.type == 'CDS']

        # mark new range which not in annotated range and have good coverage
        for query_HPR in genewise_out:
            for hit_gene in query_HPR.hit_gene_list:
                cds_range = [(i.start, i.end)
                             for i in hit_gene.sub_features[0].sub_features if i.type == 'CDS']
                cds_length = sum_interval_length(cds_range)

                mRNA_qual = hit_gene.sub_features[0].qualifiers

                # test if have been annotated
                loci_tmp = hit_gene.chr_loci
                hit_gene.new_anno = (True, None, 0.0)

                overlaped_gene_id = []

                if loci_tmp.chr_id in annotated_range_dict:
                    for annotated_range in annotated_range_dict[loci_tmp.chr_id][loci_tmp.strand].find(
                            (loci_tmp.start, loci_tmp.end)):
                        anno_s = annotated_range[0]
                        anno_e = annotated_range[1]
                        known_gene_id = annotated_range[2]
                        overlaped_gene_id.append(known_gene_id)

                overlaped_gene_id = list(set(overlaped_gene_id))

                for gene_id in overlaped_gene_id:
                    gene_cds_range = gene_cds_intervals_dict[gene_id]
                    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
                        cds_range, gene_cds_range)
                    overlap_ratio = overlap_length/cds_length

                    if overlap_ratio >= args.annotated_coverage:
                        hit_gene.new_anno = (
                            False, known_gene_id, overlap_ratio)
                    else:
                        hit_gene.new_anno = (
                            True, known_gene_id, overlap_ratio)

        # turn genewise_out to a dict, key is query_name
        genewise_dict = {}
        for query_HPR in genewise_out:
            genewise_dict[query_HPR.query_gene.id] = query_HPR

        OUT = open(genewise_dict_file, 'wb')
        pickle.dump(genewise_dict, OUT)
        OUT.close()
    else:
        logger.info("comparsion already finished")
        TEMP = open(genewise_dict_file, 'rb')
        genewise_dict = pickle.load(TEMP)
        TEMP.close()

    logger.info(
        "%d query seq get %d genewise hit, %d can pass coverage test, %d are on the known gene loci, %d are good new hit" % (
            len(genewise_dict),
            sum([len(genewise_dict[i].hit_gene_list) for i in genewise_dict]),
            sum([len([j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass]) for i in
                 genewise_dict]),
            sum([len([j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass and not j.new_anno[0]])
                 for i in genewise_dict]),
            sum([len(
                [j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass and j.new_anno[0]])
                for i in genewise_dict])
        ))

    logger.info("Step3.4: tree check for gene loss orthologous")
    tree_check_pickle = args.output_dir + "/3.tree_check_pickle.pyb"
    if not os.path.exists(tree_check_pickle):
        logger.info(
            "Step3.4.1: make dir for every orthologous, and prepare new seq and old seq")
        tree_check_dir = args.tmp_path + "/tree_check"
        mkdir(tree_check_dir, True)

        homology_gene_dict = get_homology_gene(
            list(genewise_dict.keys()), ortho_obj.blast_results_file, args.log_file)

        args_list = []
        num = 0
        for OL_id in candi_loss_list:
            num = num + 1
            logger.info("%d/%d parse OL: %s" %
                        (num, len(candi_loss_list), OL_id))
            OL_dir = tree_check_dir + "/" + OL_id
            work_dir = OL_dir + "/o%ds%.1fj%.1f" % (
                args.top_outgroup_num, args.support_threshold, args.jaccard_threshold)
            OL_obj = group_dir[OL_id]
            OL_gene_list = [
                i for i in OL_obj.gene_list if i.species in core_ref + norm_ref + [target_speci]]

            tree_check_prepare(OL_gene_list, work_dir, homology_gene_dict, ortho_obj.sequences_info,
                               target_speci, core_ref, norm_ref, genewise_dict, args.annotated_coverage, args.top_outgroup_num, False, args.num_threads)

            args_list.append((OL_id, OL_gene_list, work_dir, ortho_obj.species_info, target_speci, args.target_speci,
                              args.query_in_mcl_cluster_ratio, args.support_threshold, args.jaccard_threshold, False,
                              1))

        logger.info("Step3.4.2: running tree check")
        cmd_result = multiprocess_running(
            tree_check, args_list, args.num_threads, args.log_file, True)

        tree_check_output = {}
        for i in cmd_result:
            tree_check_output[cmd_result[i]['args']
                              [0]] = cmd_result[i]['output']

        OUT = open(tree_check_pickle, 'wb')
        pickle.dump(tree_check_output, OUT)
        OUT.close()
    else:
        logger.info("comparsion already finished")
        TEMP = open(tree_check_pickle, 'rb')
        tree_check_output = pickle.load(TEMP)
        TEMP.close()

    logger.info("Step4: make report")

    # summary report
    summary_report_file = args.output_dir + "/4.summary_report.txt"

    with open(summary_report_file, 'w') as f:
        # head
        f.write("GeneLoss report writing in %s\n\n" % str(datetime.now()))

        # Arg list
        f.write("\nArgument list: \n--------------------------------\n")
        args_info_string = ""
        attrs = vars(args)

        for item in attrs.items():
            args_info_string = args_info_string + ("    %s: %s\n" % item)

        f.write(args_info_string)

        # ortho sum
        f.write("\nOrthologues: \n--------------------------------\n")
        f.write("Conserved / Total orthologues: %d / %d = %.2f%%\n" % (
            len(conserved_OL_list), len(group_dir),
            len(conserved_OL_list) / len(group_dir) * 100))

        gene_speci_in_OL = []
        gene_speci_in_conser_OL = []
        for OL_id in group_dir:
            gene_set_now = group_dir[OL_id]
            speci_list = [gene.species for gene in gene_set_now.gene_list]
            gene_speci_in_OL.extend(speci_list)
            if OL_id in conserved_OL_list:
                gene_speci_in_conser_OL.extend(speci_list)

        gene_speci_in_OL_counter = Counter(gene_speci_in_OL)
        gene_speci_in_conser_OL_counter = Counter(gene_speci_in_conser_OL)

        for i in core_ref + norm_ref + [target_speci]:
            f.write("    %s: %d / %d = %.2f%%\n" % (ortho_obj.species_info[i]['id'],
                                                    gene_speci_in_conser_OL_counter[i], gene_speci_in_OL_counter[i],
                                                    gene_speci_in_conser_OL_counter[i] / gene_speci_in_OL_counter[
                                                        i] * 100))

        f.write("\nCandidate gene loss: %d / %d = %.2f%%\n" % (
            len(candi_loss_list), len(conserved_OL_list),
            len(candi_loss_list) / len(conserved_OL_list) * 100))

        # tree test

        all_true = len(
            [i for i in tree_check_output if tree_check_output[i][0]])
        good_topo_no_new_gene = len(
            [i for i in tree_check_output if tree_check_output[i][1] == 'Good topo and no added gene'])
        no_outgroup_no_new_gene = len(
            [i for i in tree_check_output if tree_check_output[i][1] == 'No outgroup and no new genewise'])
        bad_topo_no_new_gene = len(
            [i for i in tree_check_output if tree_check_output[i][1] == 'Bad topo but no new gene'])

        all_false = len(
            [i for i in tree_check_output if not tree_check_output[i][0]])
        good_topo_new_gene = len(
            [i for i in tree_check_output if isinstance(tree_check_output[i][1], list)])
        bad_topo = len(
            [i for i in tree_check_output if tree_check_output[i][1] == 'Bad topo'])
        no_outgroup_new_gene = len(
            [i for i in tree_check_output if tree_check_output[i][1] == 'No outgroup and have new genewise'])

        f.write("\nTree test: \n--------------------------------\n")
        f.write("There are %d Orthologues group may have gene loss, in which:\n" % len(
            candi_loss_list))
        f.write("%d pass tree test, because:\n" % all_true)
        f.write("    %d have good topology and no new genewise hit can be cluster into clade\n" %
                good_topo_no_new_gene)
        f.write("    %d not found outgroup seq and not found new genewise hit\n" %
                no_outgroup_no_new_gene)
        f.write("    %d have a bad topology in tree and not found new genewise hit\n" %
                bad_topo_no_new_gene)
        f.write("%d not pass tree test, because:\n" % all_false)
        f.write(
            "    %d have good topology and have some new genewise hit can be cluster into clade\n" % good_topo_new_gene)
        f.write("    %d have a bad topology in tree\n" % bad_topo)
        f.write("    %d not found outgroup seq but can found new genewise hit\n" %
                no_outgroup_new_gene)

        f.write("\nPassed gene loss: %d / %d = %.2f%%\n" % (
            all_true, len(conserved_OL_list),
            all_true / len(conserved_OL_list) * 100))

    # table report
    table_report_file = args.output_dir + "/4.table_report.txt"

    print_speci_list = args.core_ref.split(
        ',') + args.norm_ref.split(',') + args.target_speci.split(',')
    print_speci_id_list = []
    for i in print_speci_list:
        print_speci_id_list.append(
            [j for j in ortho_obj.species_info if ortho_obj.species_info[j]['id'] == i][0])

    with open(table_report_file, 'w') as f:
        head_line_list = ['OL_id', 'conserved', 'gene_loss',
                          'gene_loss_detail'] + print_speci_list + print_speci_list
        f.write(printer_list(head_line_list) + "\n")

        for OL_id in conserved_OL_list:

            print_line_list = [OL_id, 'True']
            if OL_id in tree_check_output:
                if OL_id in [i for i in tree_check_output if tree_check_output[i][0]]:
                    print_line_list.extend(
                        ['True', tree_check_output[OL_id][1]])
                else:
                    print_line_list.append('False')
                    if isinstance(tree_check_output[OL_id][1], list):
                        loss_detail = printer_list(
                            tree_check_output[OL_id][1], sep=', ')
                    else:
                        loss_detail = tree_check_output[OL_id][1]
                    print_line_list.append(loss_detail)
            else:
                print_line_list.extend(['False', 'Not in candidate list'])

            gene_set = group_dir[OL_id]
            speci_stat_dir = gene_set.speci_stat()
            gene_num_list = []
            for i in print_speci_id_list:
                if i in speci_stat_dir:
                    gene_num_list.append(speci_stat_dir[i])
                else:
                    gene_num_list.append(0)

            print_line_list.extend(gene_num_list)

            gene_set_by_speci = {}
            for i in print_speci_id_list:
                gene_set_by_speci[i] = []
            for gene in gene_set.gene_list:
                if gene.species in print_speci_id_list:
                    gene_set_by_speci[gene.species].append(
                        gene.old_name['raw_short_id'])

            print_line_list.extend(
                [printer_list(gene_set_by_speci[i], sep=', ') for i in print_speci_id_list])

            f.write(printer_list(print_line_list) + "\n")

    # new gene gff and sequences
    genewise_hit_in_added_id_list = [tree_check_output[i][1] for i in tree_check_output if
                                     isinstance(tree_check_output[i][1], list)]

    tmp = []
    for i in genewise_hit_in_added_id_list:
        tmp.extend(i)

    genewise_hit_in_added_id_list = tmp

    table_report_file = args.output_dir + "/4.table_report.txt"

    # todo

    return tree_check_output


def GeneLoss_args_parser(args):

    # configure file argument parse

    try:
        script_dir_path = os.path.split(os.path.realpath(__file__))[0]
        defaults_config_file = script_dir_path + \
            "/GeneLoss_defaults.ini"
    except:
        defaults_config_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/src/xuyuxing/GenomeTools/GeneLoss_defaults.ini"
    # print(defaults_config_file)

    args_type = {
        # str
        "config_file": "str",
        "target_speci": "str",
        "target_speci_genome": "str",
        "target_speci_annotation": "str",
        "target_speci_feature": "str",
        "wpgmapper_dir": "str",
        "core_ref": "str",
        "norm_ref": "str",
        "log_file": "str",
        "orthofinder_dir_path": "str",
        "output_dir": "str",
        "tmp_path": "str",
        "ortho_level": "str",
        "orthofinder_wpgmapper_id_map": "str",

        # float
        "tolerance_ratio": "float",
        "annotated_coverage": "float",
        "query_in_mcl_cluster_ratio": "float",
        "support_threshold": "float",
        "jaccard_threshold": "float",
        "min_cover": "float",
        "min_identity": "float",

        # int
        "num_threads": "int",
        "top_evidence_num": "int",
        "min_aa_len": "int",
        "min_score": "int",
        "top_outgroup_num": "int",
    }

    args = configure_parser(args, defaults_config_file,
                            args.config_file, args_type, None)

    # Modify_dict parse
    cfg = configparser.ConfigParser()
    cfg.read(args.config_file)

    if "Modify_dict" in cfg.sections():
        args.modify_dict = {}
        for key in cfg["Modify_dict"]:
            value = cfg["Modify_dict"][key]
            args.modify_dict[key] = value

    # geneloss running
    tree_check_output = GeneLoss_main(args)


if __name__ == '__main__':
    # command argument parse
    class abc(object):
        pass

    args = abc()

    args.target_speci_genome = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Cau_WPGmapper/T267555N0.genome.fasta"
    args.target_speci = "T267555N0.gene_model.protein"
    args.target_speci_annotation = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/T267555N0.genome.gff3"
    args.target_speci_feature = "gene"
    args.wpgmapper_dir = '/lustre/home/xuyuxing/Work/Gel/WPGmapper/Cau_WPGmapper'
    args.core_ref = "T13333N0.gene_model.protein,T4686N0.gene_model.protein,T4530N0.gene_model.protein,T3702N0.gene_model.protein,T35883N0.gene_model.protein"
    args.norm_ref = "T210225N0.gene_model.protein,T13216N0.gene_model.protein,T3414N0.gene_model.protein,T337451N0.gene_model.protein,T3435N0.gene_model.protein,T55571N0.gene_model.protein,T167602N0.gene_model.protein,T90708N0.gene_model.protein,T746888N0.gene_model.protein,T13894N0.gene_model.protein,T1510057N0.gene_model.protein,T51953N0.gene_model.protein,T42345N0.gene_model.protein,T4615N0.gene_model.protein,T15368N0.gene_model.protein,T1148796N0.gene_model.protein,T4577N0.gene_model.protein,T4639N0.gene_model.protein,T4641N0.gene_model.protein,T218851N0.gene_model.protein,T4432N0.gene_model.protein,T63787N0.gene_model.protein,T29760N0.gene_model.protein,T3694N0.gene_model.protein,T3847N0.gene_model.protein,T57918N0.gene_model.protein,T3659N0.gene_model.protein,T29730N0.gene_model.protein,T49390N0.gene_model.protein,T4155N0.gene_model.protein,T4146N0.gene_model.protein,T4182N0.gene_model.protein,T4072N0.gene_model.protein,T4081N0.gene_model.protein"
    args.ortho_level = 'orthogroups'
    args.orthofinder_wpgmapper_id_map = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/orthofinder_wpgmapper_id_map.txt'

    args.orthofinder_dir_path = "/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ortho/protein/OrthoFinder/Results_Oct06"
    args.output_dir = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/Cau'
    args.tmp_path = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/Cau/tmp'
    args.log_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/Cau/log"

    args.top_evidence_num = 20
    args.tolerance_ratio = 0.80
    args.num_threads = 56
    args.annotated_coverage = 0.8
    args.query_in_mcl_cluster_ratio = 0.8
    args.support_threshold = 0.8
    args.jaccard_threshold = 0.8
    args.top_outgroup_num = 5

    args.min_cover = 0.5
    args.min_aa_len = 50
    args.min_identity = 0.3
    args.min_score = 50

    GeneLoss_main(args)