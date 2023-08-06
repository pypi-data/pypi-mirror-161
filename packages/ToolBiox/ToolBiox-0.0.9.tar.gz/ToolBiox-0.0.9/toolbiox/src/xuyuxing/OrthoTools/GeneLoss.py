from toolbiox.lib.common.os import mkdir, copy_file, cmd_run, multiprocess_running
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.xuyuxing.evolution.orthotools import OG_tsv_file_parse
import os
import pandas as pd
from toolbiox.lib.common.evolution.tree_operate import get_root_by_species, add_clade_name, lookup_by_names, reroot_by_outgroup_clade, collapse_low_support
from Bio import Phylo
from toolbiox.lib.common.fileIO import tsv_file_dict_parse, excel_file_parse
from toolbiox.lib.common.math.interval import merge_intervals, overlap_between_interval_set, \
    group_by_intervals_with_overlap_threshold, sum_interval_length
import pickle
from collections import OrderedDict
from toolbiox.api.xuyuxing.genome.genblasta import genblasta_run, genblasta_to_genewise
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, read_fasta
from toolbiox.config import wu_blast_path
from BCBio import GFF
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, sub_gf_traveler
from interlap import InterLap
from toolbiox.api.common.genome.blast import outfmt6_read_big, evalue_to_wvalue
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from toolbiox.lib.common.evolution.tree_operate import monophyly
from toolbiox.src.xuyuxing.tools.phytools import PtTree


def if_conserved(species_list, conserved_arguments_dict):
    core_ref_list = conserved_arguments_dict["core_ref_list"]
    norm_ref_list = conserved_arguments_dict["norm_ref_list"]
    min_genome_in_norm_ref_tolerance = conserved_arguments_dict["min_genome_in_norm_ref_tolerance"]

    conserved_flag = True

    if len(set(species_list) & set(core_ref_list)) != len(core_ref_list):
        conserved_flag = False

    if len(set(species_list) & set(norm_ref_list)) < min_genome_in_norm_ref_tolerance:
        conserved_flag = False

    return conserved_flag


def if_conserved2(species_list, conserved_arguments_dict):
    """
    full_species_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    core_ref_list = ["1", "2"]
    sp_group_lol = [["3", "4", "5"],["6", "7"],["8", "9"]]
    group_min_num_list = [2,1,1]

    species_list = ["1","2","3","4","6","8"]
    """

    core_ref_list = conserved_arguments_dict["core_ref_list"]
    sp_group_lol = conserved_arguments_dict["sp_group_lol"]
    group_min_num_list = conserved_arguments_dict["group_min_num_list"]

    conserved_flag = True

    if len(set(species_list) & set(core_ref_list)) != len(core_ref_list):
        conserved_flag = False

    for sp_group_list, min_num in zip(sp_group_lol, group_min_num_list):
        if len(set(species_list) & set(sp_group_list)) < min_num:
            conserved_flag = False

    return conserved_flag


def get_conserved_clades(rooted_tree_node_dict, gene_to_species_map_dict, conserved_function, conserved_arguments):
    """
    filter all conserved clades on a rooted tree, return clades may overlap with each other
    """
    conserved_clades = []
    for clade_id in rooted_tree_node_dict:
        clade = rooted_tree_node_dict[clade_id]
        if not clade.is_terminal():
            sp_list = list(set([gene_to_species_map_dict[leaf.name]
                                for leaf in clade.get_terminals()]))
            if conserved_function(sp_list, conserved_arguments):
                conserved_clades.append(clade_id)
    return conserved_clades


def get_orthogroups_from_tree(tree_prefix, gene_tree, species_tree, gene_to_species_map_dict, conserved_function, conserved_arguments, support_threshold):
    # root gene tree
    gene_tree = add_clade_name(gene_tree)
    gene_tree_node_dict = lookup_by_names(gene_tree)

    best_root_clade = get_root_by_species(
        gene_tree, species_tree, gene_to_species_map_dict)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(gene_tree,
                                                                                                            gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    # collapse low support clades
    gene_tree_rooted_collapsed = collapse_low_support(
        gene_tree_rooted, support_threshold)
    gene_tree_rooted_collapsed = add_clade_name(gene_tree_rooted_collapsed)
    gene_tree_rooted_collapsed_node_dict = lookup_by_names(
        gene_tree_rooted_collapsed)

    # get conserved clades
    conserved_clades_id_list = get_conserved_clades(
        gene_tree_rooted_collapsed_node_dict, gene_to_species_map_dict, conserved_function, conserved_arguments)

    # get sub_orthogroups
    num = 0

    orthogroup_id = "%s_%d" % (tree_prefix, num)
    zero_clade_conserved = conserved_function(list(set(
        [gene_to_species_map_dict[leaf.name] for leaf in gene_tree_rooted_collapsed.get_terminals()])), conserved_arguments)
    sub_orthogroup_dict = {orthogroup_id: (
        [leaf.name for leaf in gene_tree_rooted_collapsed.get_terminals()], zero_clade_conserved)}

    for clade_id in conserved_clades_id_list:
        num += 1
        orthogroup_id = "%s_%d" % (tree_prefix, num)
        clade = gene_tree_rooted_collapsed_node_dict[clade_id]
        sub_orthogroup_dict[orthogroup_id] = (
            [leaf.name for leaf in clade.get_terminals()], True)

    return sub_orthogroup_dict


def get_orthopairs_from_orthogroups(sp_a, sp_b, orthogroup_dict, gene_to_species_map_dict):
    sp_a_dict = {}

    for og_id in orthogroup_dict:
        orthogroup_gene_list = orthogroup_dict[og_id][0]

        a_list = tuple(
            [gene_id for gene_id in orthogroup_gene_list if gene_to_species_map_dict[gene_id] == sp_a])
        b_list = tuple(
            [gene_id for gene_id in orthogroup_gene_list if gene_to_species_map_dict[gene_id] == sp_b])

        for a in a_list:
            if a not in sp_a_dict:
                sp_a_dict[a] = (b_list, og_id)
            else:
                if len(b_list) < len(sp_a_dict[a]):
                    sp_a_dict[a] = (b_list, og_id)

    return sp_a_dict


def get_orthopairs_from_one_tree_dir(sp_a, sp_b, gene_tree_file, species_tree_file, gene_to_species_map_file, conserved_function, conserved_arguments, support_threshold):
    gene_tree = Phylo.read(gene_tree_file, 'newick')
    species_tree = Phylo.read(species_tree_file, 'newick')

    info_dict = tsv_file_dict_parse(gene_to_species_map_file, fieldnames=[
                                    "new_id", "old_id", "sp_id"])
    gene_to_species_map_dict = {}
    rename_dict = {}
    for i in info_dict:
        gene_to_species_map_dict[info_dict[i]["new_id"] +
                                 "_" + info_dict[i]["sp_id"]] = info_dict[i]["sp_id"]
        rename_dict[info_dict[i]["new_id"] + "_" +
                    info_dict[i]["sp_id"]] = info_dict[i]["old_id"]

    sub_orthogroup_dict = get_orthogroups_from_tree(
        "text", gene_tree, species_tree, gene_to_species_map_dict, conserved_function, conserved_arguments, support_threshold=support_threshold)

    ortho_output_dict = get_orthopairs_from_orthogroups(
        sp_a, sp_b, sub_orthogroup_dict, gene_to_species_map_dict)

    output_dict = {}
    for a_g_id in ortho_output_dict:
        b_g_id_tuple, support_OG_id = ortho_output_dict[a_g_id]
        support_OG_id_list = sub_orthogroup_dict[support_OG_id][0]
        old_a_g_id = rename_dict[a_g_id]
        old_b_g_id_tuple = tuple([rename_dict[i] for i in b_g_id_tuple])
        old_support_OG_id_list = tuple(
            [rename_dict[i] for i in support_OG_id_list])

        output_dict[old_a_g_id] = (
            old_b_g_id_tuple, old_support_OG_id_list, sub_orthogroup_dict[support_OG_id][1])

    return output_dict


def get_orthopairs_fasttree_pipeline(OG_tsv_file, fasttree_dir, species_tree_file, sp_a, sp_b, conserved_function, conserved_arguments, support_threshold, threads=56):
    """
    output_dict['Ath_id'] = (('Gel_id',), (OG_gene_list), conserved_flag)
    """

    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    num = 0

    args_list = []

    for og_id in OG_dict:
        num += 1

        og_dir = fasttree_dir + "/" + og_id
        gene_tree_file = og_dir + "/fasttree.phb"
        gene_to_species_map_file = og_dir + "/rename.map"
        args_list.append((sp_a, sp_b, gene_tree_file, species_tree_file, gene_to_species_map_file,
                          conserved_function, conserved_arguments, support_threshold))

    tmp_out = multiprocess_running(
        get_orthopairs_from_one_tree_dir, args_list, threads, None, True, None)

    output_dict = {}
    for i in tmp_out:
        tmp_output_dict = tmp_out[i]['output']
        for i in tmp_output_dict:
            output_dict[i] = tmp_output_dict[i]

    return output_dict


# gene loss test

def if_OG_conserved(species_list, conserved_arguments_dict):
    """
    full_species_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    sp_group_lol = [["3", "4", "5"],["6", "7"],["8", "9"]]
    group_min_num_list = [2,1,1]

    species_list = ["1","2","3","4","6","8"]
    """
    sp_group_lol = conserved_arguments_dict["sp_group_lol"]
    group_min_num_list = conserved_arguments_dict["group_min_num_list"]

    conserved_flag = True

    for sp_group_list, min_num in zip(sp_group_lol, group_min_num_list):
        if len(set(species_list) & set(sp_group_list)) < min_num:
            conserved_flag = False

    return conserved_flag


def get_conserved_OGs(OG_dict, conserved_arguments):
    """
    filter all Orthogroups, return conserved orthogroups id list
    """
    conserved_OG_list = []
    for og_id in OG_dict:
        sp_list = [sp_id for sp_id in OG_dict[og_id]
                   if len(OG_dict[og_id][sp_id]) != 0]
        if if_OG_conserved(sp_list, conserved_arguments):
            conserved_OG_list.append(og_id)

    return conserved_OG_list


def load_annotated_range(gff_file, target_feature="CDS"):
    gf_dict = read_gff_file(gff_file)
    annotated_range_dict = {}
    for top_feature in gf_dict:
        for gf_id in gf_dict[top_feature]:
            gf = gf_dict[top_feature][gf_id]
            for sub_gf in sub_gf_traveler(gf):
                if sub_gf.type == target_feature:
                    chr_id = sub_gf.chr_id
                    strand = sub_gf.strand
                    if chr_id not in annotated_range_dict:
                        annotated_range_dict[chr_id] = {
                            "+": InterLap(),
                            "-": InterLap(),
                        }
                    annotated_range_dict[chr_id][strand].add(
                        (sub_gf.start, sub_gf.end))

    return annotated_range_dict


def load_genewise_gff(gff_file):
    output_gf_dict = {}
    gf_dict = read_gff_file(gff_file)
    for top_feature in gf_dict:
        for gf_id in gf_dict[top_feature]:
            output_gf_dict[gf_id] = gf_dict[top_feature][gf_id]
    return output_gf_dict


def tree_check(og_dir, target_sp_id, cpu_num, support_threshold, jaccard_threshold):
    seq_info_file = og_dir + "/seq_info.pyb"
    TEMP = open(seq_info_file, 'rb')
    ref_seq_dict, ref_seq_sp_map, homo_seq_dict, homo_seq_sp_map, add_seq_dict = pickle.load(
        TEMP)
    TEMP.close()

    # if no new wise out
    if len(add_seq_dict) == 0:
        return True, "No new genewise"

    # if no outgroup
    if len(homo_seq_dict) == 0:
        if len(add_seq_dict) != 0:
            return False, "No outgroup and have new genewise"

    # else need treeing
    tree_dir = og_dir + "/tree"
    mkdir(tree_dir, True)
    tree_output_dir = tree_dir + "/tree_out"
    mkdir(tree_output_dir, True)
    tree_file = tree_output_dir + "/tree_out.phb"

    seq_dict = merge_dict([ref_seq_dict, homo_seq_dict, add_seq_dict], False)
    map_dict = merge_dict([ref_seq_sp_map, homo_seq_sp_map], False)
    for i in add_seq_dict:
        map_dict[i] = target_sp_id

    # make tree
    top_tree_seq_file = tree_dir + "/tree.faa"
    with open(top_tree_seq_file, 'w') as f:
        for seq_name in seq_dict:
            f.write(">%s\n%s\n" % (seq_name, seq_dict[seq_name]))

    if not(os.path.exists(tree_file) and os.path.getsize(tree_file) != 0):
        PtTree(top_tree_seq_file, 'fasttree', False,
               tree_output_dir, cpu_num, "clustalo")

    # tree check
    query_gene_name_list = list(ref_seq_dict.keys())
    new_gene_name_list = list(add_seq_dict.keys())
    target_speci_gene_name_list = [
        i for i in homo_seq_sp_map if homo_seq_sp_map[i] == target_sp_id]

    tree = Phylo.read(tree_file, 'newick')
    good_topo, monophyly_leaf = monophyly(query_gene_name_list, tree, support_threshold=support_threshold,
                                          jaccard_threshold=jaccard_threshold, exclude_leaf_set=new_gene_name_list)

    added_new_gene = list(set(new_gene_name_list) & set(monophyly_leaf)) + list(
        set(target_speci_gene_name_list) & set(monophyly_leaf))

    if good_topo:
        if len(added_new_gene):
            return False, added_new_gene
        else:
            return True, "Good topo and no added gene"
    else:
        return False, "Bad topo"


def main(args):
    """
    class abc():
        pass

    args = abc()

    # path
    args.aa_fof_excel = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/2.order_level_OrthoFinder/Asparagales/pt_file/tmp/aa_fof.xlsx"
    args.orthogroups_tsv = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/2.order_level_OrthoFinder/Asparagales/pt_file/tmp/Orthogroups.tsv"
    args.target_genome_fasta = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/2.order_level_OrthoFinder/Asparagales/pt_file/tmp/T91201N0.genome.fasta"
    args.target_gene_gff = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/2.order_level_OrthoFinder/Asparagales/pt_file/tmp/T91201N0.genome.gff3"
    args.work_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/2.order_level_OrthoFinder/Asparagales/pt_file/tmp"

    # parameter
    args.target_list = "Gel"
    args.core_ref_list = ["Aof", "Ath", "Osa"]
    args.norm_ref_list = ["Ash", "Dca", "Peq", "Vpl"]
    args.bad_genome_in_norm_ref_tolerance = 1
    args.flank_rage = 1000
    args.gene_coverage = 0.5
    args.genblasta_hit_num = 20
    args.annotated_coverage = 0.8
    args.same_loci_overlap_threshold = 0.5
    args.query_in_mcl_cluster_ratio = 0.8
    args.support_threshold = 0.8
    args.jaccard_threshold = 0.8
    args.top_outgroup_num = 5    
    """

    mkdir(args.work_dir, True)

    log_file = args.work_dir + "/log"

    logger = logging_init("GeneLoss", log_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    logger.info("Step1: parse orthogroups tsv")
    ortho_dict = OG_tsv_file_parse(args.orthogroups_tsv)
    species_list_in_ortho = list(ortho_dict[list(ortho_dict.keys())[0]].keys())

    pt_file_df = pd.read_excel(
        args.aa_fof_excel, sheet_name='Sheet1', header=[0])
    species_list_in_pt_file = list(pt_file_df.sp_id)

    if set(species_list_in_ortho) != set(species_list_in_ortho):
        raise ValueError("species should same in orthofile and pt_file")

    sp_list = species_list_in_ortho
    ortho_count_df = pd.DataFrame(
        columns=sp_list, index=list(ortho_dict.keys()))

    for og_id in ortho_count_df.index:
        ortho_count_df.loc[og_id] = [
            len(ortho_dict[og_id][sp_id]) for sp_id in ortho_count_df.columns]

    logger.info("Step2: defined conserved OG")
    ortho_count_df.insert(ortho_count_df.shape[1], 'conserved', False)
    for og_id in ortho_count_df.index:
        # print(og_id)
        sp_list_now = [
            sp_id for sp_id in sp_list if ortho_count_df.loc[og_id, sp_id] != 0]
        ortho_count_df.loc[og_id, "conserved"] = if_conserved(
            sp_list_now, args)

    # todo

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


if __name__ == '__main__':

    # orthogroups level gene loss test

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/pt_file/OrthoFinder/Results_Mar16/Orthogroups/Orthogroups.tsv"
    work_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check"
    species_info_xlsx = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/species_info.xlsx"

    species_info_dict = excel_file_parse(species_info_xlsx, key_col='sp_id')

    conserved_arguments = {
        "sp_group_lol": [['Csi', 'Cnu', 'Acom', 'Bdi', 'Osa', 'Oth', 'Zma', 'Eve', 'Mac'], ['Vvi', 'Ptr', 'Mes', 'Gma', 'Fve', 'Csa', 'Ath', 'Gra'], ['Cca', 'Mgu', 'Oeu', 'Sin', 'Can', 'Sly', 'Stu', 'Ini']],
        "group_min_num_list": [3, 3, 3],
    }

    gene_loss_define = OrderedDict([('Ash', ["Aof"]),
                                    ('Vpl', ["Aof"]),
                                    ('Gel', ["Aof"]),
                                    ('Sas', ["Mgu"]),
                                    ('Cau', ["Ini"]),
                                    ('Shi', ["Mes"])])

    stem_sp_list = ['Atr', 'Pni', 'Nco', 'Osa', 'Aof',
                    'Mgu', 'Ini', 'Mes', 'Ath', 'Aco', 'Xvi']
    core_ref_sp_list = ['Ath', 'Osa']

    # read OG
    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    # get conserved OG
    conserved_OG_list = get_conserved_OGs(OG_dict, conserved_arguments)

    # get lost OG in target species
    gene_lost_dict = OrderedDict()
    for target_sp in gene_loss_define:
        gene_lost_dict[target_sp] = []
        for og_id in conserved_OG_list:
            lost_flag = True
            # target species should have not this gene
            if len(OG_dict[og_id][target_sp]) != 0:
                lost_flag = False
            # ref species must have this gene
            for ref_sp_id in gene_loss_define[target_sp]:
                if len(OG_dict[og_id][ref_sp_id]) == 0:
                    lost_flag = False
            if lost_flag:
                gene_lost_dict[target_sp].append(og_id)

    for target_sp in gene_lost_dict:
        print(target_sp, len(gene_lost_dict[target_sp]))

    # re-annotated genome
    reanno_jobs_dict = {}

    for target_sp in gene_lost_dict:
        ref_sp_list = gene_loss_define[target_sp] + core_ref_sp_list
        reanno_jobs_dict[target_sp] = {ref_sp_id: []
                                       for ref_sp_id in ref_sp_list}

        for og_id in gene_lost_dict[target_sp]:
            for ref_sp_id in ref_sp_list:
                reanno_jobs_dict[target_sp][ref_sp_id] += OG_dict[og_id][ref_sp_id]

    for target_sp in reanno_jobs_dict:
        for ref_sp_id in reanno_jobs_dict[target_sp]:
            print(target_sp, ref_sp_id, len(
                reanno_jobs_dict[target_sp][ref_sp_id]))

    # genblasta + genewise
    # mkdir and copy file
    reanno_dir = work_dir + "/reanno"
    mkdir(reanno_dir, True)

    run_file_dict = {}
    for target_sp in gene_loss_define:
        run_file_dict[target_sp] = {"genome": reanno_dir + "/" + target_sp + ".genome.fasta",
                                    "gff": reanno_dir + "/" + target_sp + ".gff",
                                    }

        copy_file(species_info_dict[target_sp]['genome_file'],
                  run_file_dict[target_sp]["genome"])
        copy_file(species_info_dict[target_sp]
                  ['gff_file'], run_file_dict[target_sp]["gff"])

    # prepare genblasta
    genblasta_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        mkdir(target_sp_dir, True)
        for ref_sp in reanno_jobs_dict[target_sp]:
            print(target_sp, ref_sp)
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            mkdir(ref_sp_dir, True)
            ref_sp_aa_dict = read_fasta_by_faidx(
                species_info_dict[ref_sp]['pt_file'])
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq = ref_sp_aa_dict[q_seq_id]
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                with open(q_seq_file, 'w') as f:
                    f.write(">%s\n%s" % (q_seq.seqname, q_seq.seq))
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                genblasta_jobs_args_list.append(
                    (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, 0.5, 20))

    for target_sp in reanno_jobs_dict:
        cmd_string = "%s/xdformat -n %s" % (wu_blast_path,
                                            run_file_dict[target_sp]["genome"])
        cmd_run(cmd_string, silence=True)

    # run genblasta
    genblasta_out = multiprocess_running(
        genblasta_run, genblasta_jobs_args_list, 80, silence=False)

    # prepare genewise
    genewise_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                genewise_jobs_args_list.append(
                    (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/reanno/tmp', 1000, wise_prefix, False, 20))

    # run genewise
    genewise_running_out = multiprocess_running(
        genblasta_to_genewise, genewise_jobs_args_list, 80, silence=False)

    # check
    genewise_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                gff_file = wise_prefix + ".gff3"
                if not os.path.exists(gff_file):
                    genewise_jobs_args_list.append(
                        (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/reanno/tmp', 1000, wise_prefix, False, 20))

    # rerun
    genewise_running_out = multiprocess_running(
        genblasta_to_genewise, genewise_jobs_args_list, 80, silence=False)

    # compare with gff file, filter out short one

    reanno_results_dict = {}
    for target_sp in reanno_jobs_dict:
        reanno_results_dict[target_sp] = {}
        # load annoed dict
        target_sp_annoed_dict = load_annotated_range(
            run_file_dict[target_sp]["gff"])
        target_sp_dir = reanno_dir+"/"+target_sp

        # load genewise output
        load_genewise_args_list = []
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                gff_file = wise_prefix + ".gff3"
                load_genewise_args_list.append((gff_file,))

        tmp_out = multiprocess_running(
            load_genewise_gff, load_genewise_args_list, 80, silence=True)

        genewise_dict = {}
        for i in tmp_out:
            for gf_id in tmp_out[i]['output']:
                if gf_id in genewise_dict:
                    print("warnning: same gf id !")
                genewise_dict[gf_id] = tmp_out[i]['output'][gf_id]

        # remove genewise gf which not good coverage or has been annotated
        for gf_id in genewise_dict:
            gf = genewise_dict[gf_id]
            mRNA_qual = gf.sub_features[0].qualifiers
            coverage_ratio = abs(int(mRNA_qual['Target_Start'][0]) - int(mRNA_qual['Target_End'][0])) / int(
                mRNA_qual['Target_Length'][0])

            if coverage_ratio < 0.5:
                continue

            cds_range = [(cds.start, cds.end)
                         for cds in gf.sub_features[0].sub_features]
            cds_length = sum_interval_length(cds_range)

            overlaped_anno_range = []
            for tr in cds_range:
                if gf.chr_id in target_sp_annoed_dict:
                    overlaped_anno_range.extend(
                        list(target_sp_annoed_dict[gf.chr_id][gf.strand].find(tr)))
            overlaped_anno_range = merge_intervals(overlaped_anno_range)

            a, overlength, c = overlap_between_interval_set(
                cds_range, overlaped_anno_range)

            annoed_ratio = overlength/cds_length

            if annoed_ratio > 0.5:
                continue

            reanno_results_dict[target_sp][gf_id] = gf

    for target_sp in reanno_results_dict:
        tmp_dict = {}
        for gf_id in reanno_results_dict[target_sp]:
            gf = reanno_results_dict[target_sp][gf_id]
            gf_query = gf.sub_features[0].qualifiers['Target'][0]
            if gf_query not in tmp_dict:
                tmp_dict[gf_query] = {}
            tmp_dict[gf_query][gf_id] = gf
        reanno_results_dict[target_sp] = tmp_dict

    # diamond db
    diamond_dir = work_dir + "/diamond"
    mkdir(diamond_dir, True)

    all_sp_list = stem_sp_list + list(gene_loss_define.keys())

    # copy file
    for sp_id in all_sp_list:
        if sp_id not in run_file_dict:
            run_file_dict[sp_id] = {}
        run_file_dict[sp_id]["pt_file"] = diamond_dir + "/" + sp_id + ".faa"
        copy_file(species_info_dict[sp_id]['pt_file'],
                  run_file_dict[sp_id]["pt_file"])

    # makedb
    diamond_makedb_args_list = []
    for sp_id in all_sp_list:
        cmd_string = "diamond makedb --in %s/%s.faa --db %s/%s.dmnd" % (
            diamond_dir, sp_id, diamond_dir, sp_id)
        diamond_makedb_args_list.append((cmd_string, None, 1, True, None))

    tmp_out = multiprocess_running(
        cmd_run, diamond_makedb_args_list, 80, silence=True)

    # running
    diamond_args_list = []
    for i in all_sp_list:
        for j in all_sp_list:
            cmd_string = "diamond blastp -d %s/%s.dmnd -q %s/%s.faa -o %s/%s_vs_%s.bls --more-sensitive -p 1 --quiet -e 0.001 --compress 1" % (
                diamond_dir, j, diamond_dir, i, diamond_dir, i, j)
            diamond_args_list.append((cmd_string, None, 1, True, None))

    tmp_out = multiprocess_running(
        cmd_run, diamond_args_list, 80, silence=True)

    # reading bls results

    wvalue_dict = {}
    num = 0
    for i in all_sp_list:
        num += 1
        print(num, len(all_sp_list))
        wvalue_dict[i] = {}
        for j in all_sp_list:
            wvalue_dict[i][j] = {}
            blast_file = "%s/%s_vs_%s.bls.gz" % (diamond_dir, i, j)
            bls_file_parser = outfmt6_read_big(blast_file, gzip_flag=True)
            for query in bls_file_parser:
                q_def = query.qDef
                wvalue_dict[i][j][q_def] = {}
                for subject in query.hit:
                    s_def = subject.Hit_def
                    hsp = subject.hsp[0]
                    evalue = hsp.Hsp_evalue
                    wvalue_dict[i][j][q_def][s_def] = evalue_to_wvalue(
                        float(evalue))

    # tree check
    # prepare

    tree_dir = work_dir + "/tree"
    mkdir(tree_dir, True)

    ref_sp_aa_dict = {}
    for ref_sp in all_sp_list:
        ref_sp_aa_dict[ref_sp], b = read_fasta(
            species_info_dict[ref_sp]['pt_file'])

    for sp_id in gene_lost_dict:
        lost_og_list = gene_lost_dict[sp_id]
        tree_now_dir = tree_dir + "/" + sp_id
        mkdir(tree_now_dir, True)
        num = 0
        for og_id in lost_og_list:
            num += 1
            print(sp_id, og_id, num, len(lost_og_list))

            og_dir = tree_now_dir + "/" + og_id
            mkdir(og_dir, True)

            ref_seq_dict = {}
            wise_dict = {}
            ref_seq_sp_map = {}

            for ref_sp in stem_sp_list:
                for g_id in OG_dict[og_id][ref_sp]:
                    ref_seq_dict[g_id] = ref_sp_aa_dict[ref_sp][g_id].seq
                    if g_id in reanno_results_dict[sp_id]:
                        wise_dict[g_id] = reanno_results_dict[sp_id][g_id]
                    else:
                        wise_dict[g_id] = {}
                    ref_seq_sp_map[g_id] = ref_sp

            # get homology gene
            homology_gene_dir = {}
            homology_gene_sp_map = {}

            for ref_g_id in ref_seq_sp_map:
                for sp_id_now in stem_sp_list + [sp_id]:
                    if ref_g_id in wvalue_dict[ref_seq_sp_map[ref_g_id]][sp_id_now]:
                        for hit in wvalue_dict[ref_seq_sp_map[ref_g_id]][sp_id_now][ref_g_id]:
                            if hit not in ref_seq_sp_map:
                                wvalue = wvalue_dict[ref_seq_sp_map[ref_g_id]
                                                     ][sp_id_now][ref_g_id][hit]
                                if hit not in homology_gene_dir:
                                    homology_gene_dir[hit] = 0
                                    homology_gene_sp_map[hit] = sp_id_now
                                homology_gene_dir[hit] += wvalue

            homo_seq_dict = {}
            homo_seq_sp_map = {}
            for sp_id_now in stem_sp_list + [sp_id]:
                for i in sorted([i for i in homology_gene_dir if homology_gene_sp_map[i] == sp_id_now],
                                key=lambda x: homology_gene_dir[x], reverse=True)[0:5]:
                    homo_seq_dict[i] = ref_sp_aa_dict[sp_id_now][i].seq
                    homo_seq_sp_map[i] = sp_id_now

            # merge the same loci, get a new seq file
            good_genewise_hit_dir = {}
            wise_seq_dir = {}
            for q_id in wise_dict:
                for s_id in wise_dict[q_id]:
                    gf = wise_dict[q_id][s_id]
                    if gf.chr_id not in good_genewise_hit_dir:
                        good_genewise_hit_dir[gf.chr_id] = {"+": {}, "-": {}}
                    good_genewise_hit_dir[gf.chr_id][gf.strand][s_id] = gf.chr_loci.range
                    pep_file = reanno_dir + "/" + sp_id + "/" + \
                        ref_seq_sp_map[q_id] + "/" + q_id + ".wise.pep"
                    pep_dict, b = read_fasta(pep_file)
                    wise_seq_dir[s_id] = pep_dict[s_id+".pep"].seq

            new_gene_list = []
            for contig in good_genewise_hit_dir:
                for strand in good_genewise_hit_dir[contig]:
                    good_genewise_hit_dir[contig][strand] = group_by_intervals_with_overlap_threshold(
                        good_genewise_hit_dir[contig][strand], 0.5)

                    for group_id in good_genewise_hit_dir[contig][strand]:
                        genewise_hit_list = good_genewise_hit_dir[contig][strand][group_id]['list']
                        lengthest_hit = sorted(genewise_hit_list, key=lambda x: len(wise_seq_dir[x]), reverse=True)[
                            0]
                        good_genewise_hit_dir[contig][strand][group_id]['rep_hit'] = lengthest_hit
                        new_gene_list.append(lengthest_hit)

            add_seq_dict = {i: wise_seq_dir[i] for i in new_gene_list}

            pickle_info = (ref_seq_dict, ref_seq_sp_map,
                           homo_seq_dict, homo_seq_sp_map, add_seq_dict)

            seq_info_file = og_dir + "/seq_info.pyb"

            OUT = open(seq_info_file, 'wb')
            pickle.dump(pickle_info, OUT)
            OUT.close()

    # treeing

    args_list = []
    args_info_list = []
    for sp_id in gene_lost_dict:
        tree_now_dir = tree_dir + "/" + sp_id
        lost_og_list = gene_lost_dict[sp_id]
        for og_id in lost_og_list:
            args_info_list.append((sp_id, og_id))
            og_dir = tree_now_dir + "/" + og_id
            args_list.append((og_dir, sp_id, 10, 0.5, 0.5))

    tmp_out = multiprocess_running(
        tree_check, args_list, 80, None, False, args_info_list)

    # report
    with open(work_dir + "/tree_check.out", 'w') as f:
        for sp_id, og_id in tmp_out:
            flag, note = tmp_out[(sp_id, og_id)]['output']

            if isinstance(note, list):
                note_string = ",".join(note)
            else:
                note_string = note

            f.write("%s\t%s\t%s\t%s\n" %
                    (sp_id, og_id, str(flag), note_string))

    # %%
    # map Gel and Cau gene to Ath

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/pt_file/OrthoFinder/Results_Apr13/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/fasttree"
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/species.txt"

    Ang_conserved_arguments = {
        "core_ref_list": ["Ath", "Osa"],
        "sp_group_lol": [["Cca", "Mgu", "Sly", "Ini", "Aco"], ["Xvi", "Aof", "Cnu", "Acom", "Eve"]],
        "group_min_num_list": [3, 3],
    }

    Eud_conserved_arguments = {
        "core_ref_list": ["Ath"],
        "sp_group_lol": [["Cca", "Mgu", "Sly", "Ini", "Aco"]],
        "group_min_num_list": [3],
    }

    conserved_function = if_conserved2
    support_threshold = 0.7
    threads = 160

    ref_sp = 'Ath'

    # Ang
    sum_dict = {}
    for sp_now in ['Osa', 'Aof', 'Ash', 'Vpl', 'Gel']:
        sum_dict[sp_now] = get_orthopairs_fasttree_pipeline(
            OG_tsv_file, fasttree_dir, species_tree_file, ref_sp, sp_now, conserved_function, Ang_conserved_arguments, support_threshold)

    # Eud
    for sp_now in ['Mgu', 'Sly', 'Ini', 'Cau']:
        sum_dict[sp_now] = get_orthopairs_fasttree_pipeline(
            OG_tsv_file, fasttree_dir, species_tree_file, ref_sp, sp_now, conserved_function, Eud_conserved_arguments, support_threshold)

    sp_id_list = ['Osa', 'Aof', 'Ash', 'Vpl',
                  'Gel'] + ['Mgu', 'Sly', 'Ini', 'Cau']

    Ath_gene_dict = {}
    for sp_now in sp_id_list:
        for ath_id in sum_dict[sp_now]:
            gene_id, og_list, conser_flag = sum_dict[sp_now][ath_id]
            if ath_id not in Ath_gene_dict:
                Ath_gene_dict[ath_id] = {}
            Ath_gene_dict[ath_id][sp_now] = gene_id

    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    Ath_OG_dict = {}
    for i in OG_dict:
        for j in OG_dict[i]['Ath']:
            Ath_OG_dict[j] = i

    Ang_conserved_dict = {}
    for i in sum_dict['Osa']:
        Ang_conserved_dict[i] = sum_dict['Osa'][i][2]

    Eud_conserved_dict = {}
    for i in sum_dict['Mgu']:
        Eud_conserved_dict[i] = sum_dict['Mgu'][i][2]

    Ath_gene_annotation_tsv = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/all_annotation.tsv'
    Ath_gene_annotation_dict = tsv_file_dict_parse(
        Ath_gene_annotation_tsv, key_col='clean_id')

    anno_col_list = list(Ath_gene_annotation_dict[list(
        Ath_gene_annotation_dict.keys())[0]].keys())

    columns = anno_col_list[:2] + ['OG_id', 'Ang_conserved', 'Eud_conserved'] + [
        i+"_num" for i in sp_id_list] + sp_id_list + anno_col_list[2:]

    ath_anno_excel_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/Ath_anno.xlsx"

    ath_anno_df = pd.DataFrame(columns=columns)

    num = 0
    for ath_id in Ath_gene_annotation_dict:
        anno_info = [Ath_gene_annotation_dict[ath_id][i]
                     for i in anno_col_list]

        if ath_id in Ath_gene_dict:
            num_list = [len(Ath_gene_dict[ath_id][i]) for i in sp_id_list]
            gene_id_list = [";".join(Ath_gene_dict[ath_id][i])
                            for i in sp_id_list]
            OG_id = Ath_OG_dict[ath_id]
        else:
            num_list = [0] * len(sp_id_list)
            gene_id_list = [""] * len(sp_id_list)
            OG_id = "-"

        if ath_id in Ang_conserved_dict:
            Ang_conserved_flag = Ang_conserved_dict[ath_id]
        else:
            Ang_conserved_flag = False

        if ath_id in Eud_conserved_dict:
            Eud_conserved_flag = Eud_conserved_dict[ath_id]
        else:
            Eud_conserved_flag = False

        row_data = anno_info[:2] + [OG_id, str(Ang_conserved_flag), str(
            Eud_conserved_flag)] + num_list + gene_id_list + anno_info[2:]

        ath_anno_df.loc[num] = row_data
        num = num+1

        if num % 1000 == 0:
            print(num)

    writer = pd.ExcelWriter(ath_anno_excel_file)
    ath_anno_df.to_excel(writer)
    writer.save()

    # %%
    # %%
    # map Pae and Cau gene to Ath

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Phelipanche/flower_for_zhentianyin/pt_file/OrthoFinder/Results_Apr19/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Phelipanche/flower_for_zhentianyin/fasttree"
    species_tree_file = "/lustre/home/xuyuxing/Work/Phelipanche/flower_for_zhentianyin/species.txt"

    conserved_arguments = {
        "sp_group_lol": [["Ath"], ["Cca", "Sly", "Oeu", "Sin", "Mgu"]],
        "group_min_num_list": [1, 3],
    }

    conserved_function = if_OG_conserved
    support_threshold = 0.7
    threads = 80

    ref_sp = 'Ath'

    sum_dict = {}
    for sp_now in ['Mgu', 'Sas', 'Pae']:
        sum_dict[sp_now] = get_orthopairs_fasttree_pipeline(
            OG_tsv_file, fasttree_dir, species_tree_file, ref_sp, sp_now, conserved_function, conserved_arguments, support_threshold)

    sp_id_list = ['Mgu', 'Sas', 'Pae']

    Ath_gene_dict = {}
    for sp_now in sp_id_list:
        for ath_id in sum_dict[sp_now]:
            gene_id, og_list, conser_flag = sum_dict[sp_now][ath_id]
            if ath_id not in Ath_gene_dict:
                Ath_gene_dict[ath_id] = {}
            Ath_gene_dict[ath_id][sp_now] = gene_id

    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    Ath_OG_dict = {}
    for i in OG_dict:
        for j in OG_dict[i]['Ath']:
            Ath_OG_dict[j] = i

    conserved_dict = {}
    for i in sum_dict['Mgu']:
        conserved_dict[i] = sum_dict['Mgu'][i][2]

    Ath_gene_annotation_tsv = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/all_annotation.tsv'
    Ath_gene_annotation_dict = tsv_file_dict_parse(
        Ath_gene_annotation_tsv, key_col='clean_id')

    anno_col_list = list(Ath_gene_annotation_dict[list(
        Ath_gene_annotation_dict.keys())[0]].keys())

    columns = anno_col_list[:2] + ['OG_id', 'conserved'] + [
        i+"_num" for i in sp_id_list] + sp_id_list + anno_col_list[2:]

    ath_anno_excel_file = "/lustre/home/xuyuxing/Work/Phelipanche/flower_for_zhentianyin/Ath_anno.xlsx"

    ath_anno_df = pd.DataFrame(columns=columns)

    num = 0
    for ath_id in Ath_gene_annotation_dict:
        anno_info = [Ath_gene_annotation_dict[ath_id][i]
                     for i in anno_col_list]

        if ath_id in Ath_gene_dict:
            num_list = [len(Ath_gene_dict[ath_id][i]) for i in sp_id_list]
            gene_id_list = [";".join(Ath_gene_dict[ath_id][i])
                            for i in sp_id_list]
            OG_id = Ath_OG_dict[ath_id]
        else:
            num_list = [0] * len(sp_id_list)
            gene_id_list = [""] * len(sp_id_list)
            OG_id = "-"

        if ath_id in conserved_dict:
            conserved_flag = conserved_dict[ath_id]
        else:
            conserved_flag = False

        row_data = anno_info[:2] + [OG_id,
                                    str(conserved_flag)] + num_list + gene_id_list + anno_info[2:]

        ath_anno_df.loc[num] = row_data
        num = num+1

        if num % 1000 == 0:
            print(num)

    writer = pd.ExcelWriter(ath_anno_excel_file)
    ath_anno_df.to_excel(writer)
    writer.save()


    # %%
    # map Pae and Cau gene to Ath

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/pt_file/OrthoFinder/Results_May08/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree"
    species_tree_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/species.txt"

    conserved_arguments = {
        "sp_group_lol": [["Osa","Zma","Acom","Xvi"],["Aco","Ath","Mdo","Sly"]],
        "group_min_num_list": [2, 2],
    }

    conserved_function = if_OG_conserved
    support_threshold = 0.7
    threads = 80

    
    
    get_orthogroups_from_tree(tree_prefix, gene_tree, species_tree, gene_to_species_map_dict, conserved_function, conserved_arguments, support_threshold)




    ref_sp = 'Ath'

    sum_dict = {}
    for sp_now in ['Mgu', 'Sas', 'Pae']:
        sum_dict[sp_now] = get_orthopairs_fasttree_pipeline(
            OG_tsv_file, fasttree_dir, species_tree_file, ref_sp, sp_now, conserved_function, conserved_arguments, support_threshold)

    sp_id_list = ['Mgu', 'Sas', 'Pae']

    Ath_gene_dict = {}
    for sp_now in sp_id_list:
        for ath_id in sum_dict[sp_now]:
            gene_id, og_list, conser_flag = sum_dict[sp_now][ath_id]
            if ath_id not in Ath_gene_dict:
                Ath_gene_dict[ath_id] = {}
            Ath_gene_dict[ath_id][sp_now] = gene_id

    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    Ath_OG_dict = {}
    for i in OG_dict:
        for j in OG_dict[i]['Ath']:
            Ath_OG_dict[j] = i

    conserved_dict = {}
    for i in sum_dict['Mgu']:
        conserved_dict[i] = sum_dict['Mgu'][i][2]

    Ath_gene_annotation_tsv = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/all_annotation.tsv'
    Ath_gene_annotation_dict = tsv_file_dict_parse(
        Ath_gene_annotation_tsv, key_col='clean_id')

    anno_col_list = list(Ath_gene_annotation_dict[list(
        Ath_gene_annotation_dict.keys())[0]].keys())

    columns = anno_col_list[:2] + ['OG_id', 'conserved'] + [
        i+"_num" for i in sp_id_list] + sp_id_list + anno_col_list[2:]

    ath_anno_excel_file = "/lustre/home/xuyuxing/Work/Phelipanche/flower_for_zhentianyin/Ath_anno.xlsx"

    ath_anno_df = pd.DataFrame(columns=columns)

    num = 0
    for ath_id in Ath_gene_annotation_dict:
        anno_info = [Ath_gene_annotation_dict[ath_id][i]
                     for i in anno_col_list]

        if ath_id in Ath_gene_dict:
            num_list = [len(Ath_gene_dict[ath_id][i]) for i in sp_id_list]
            gene_id_list = [";".join(Ath_gene_dict[ath_id][i])
                            for i in sp_id_list]
            OG_id = Ath_OG_dict[ath_id]
        else:
            num_list = [0] * len(sp_id_list)
            gene_id_list = [""] * len(sp_id_list)
            OG_id = "-"

        if ath_id in conserved_dict:
            conserved_flag = conserved_dict[ath_id]
        else:
            conserved_flag = False

        row_data = anno_info[:2] + [OG_id,
                                    str(conserved_flag)] + num_list + gene_id_list + anno_info[2:]

        ath_anno_df.loc[num] = row_data
        num = num+1

        if num % 1000 == 0:
            print(num)

    writer = pd.ExcelWriter(ath_anno_excel_file)
    ath_anno_df.to_excel(writer)
    writer.save()


# %%

    # orthogroups level gene loss test

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/pt_file/OrthoFinder/Results_Mar16/Orthogroups/Orthogroups.tsv"
    work_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check"
    species_info_xlsx = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/species_info.xlsx"

    species_info_dict = excel_file_parse(species_info_xlsx, key_col='sp_id')

    conserved_arguments = {
        "sp_group_lol": [['Csi', 'Cnu', 'Acom', 'Bdi', 'Osa', 'Oth', 'Zma', 'Eve', 'Mac'], ['Vvi', 'Ptr', 'Mes', 'Gma', 'Fve', 'Csa', 'Ath', 'Gra'], ['Cca', 'Mgu', 'Oeu', 'Sin', 'Can', 'Sly', 'Stu', 'Ini']],
        "group_min_num_list": [3, 3, 3],
    }

    gene_loss_define = OrderedDict([('Ash', ["Aof"]),
                                    ('Vpl', ["Aof"]),
                                    ('Gel', ["Aof"]),
                                    ('Sas', ["Mgu"]),
                                    ('Cau', ["Ini"]),
                                    ('Shi', ["Mes"])])

    stem_sp_list = ['Atr', 'Pni', 'Nco', 'Osa', 'Aof',
                    'Mgu', 'Ini', 'Mes', 'Ath', 'Aco', 'Xvi']
    core_ref_sp_list = ['Ath', 'Osa']

    # read OG
    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    # get conserved OG
    conserved_OG_list = get_conserved_OGs(OG_dict, conserved_arguments)

    # get lost OG in target species
    gene_lost_dict = OrderedDict()
    for target_sp in gene_loss_define:
        gene_lost_dict[target_sp] = []
        for og_id in conserved_OG_list:
            lost_flag = True
            # target species should have not this gene
            if len(OG_dict[og_id][target_sp]) != 0:
                lost_flag = False
            # ref species must have this gene
            for ref_sp_id in gene_loss_define[target_sp]:
                if len(OG_dict[og_id][ref_sp_id]) == 0:
                    lost_flag = False
            if lost_flag:
                gene_lost_dict[target_sp].append(og_id)

    for target_sp in gene_lost_dict:
        print(target_sp, len(gene_lost_dict[target_sp]))

    # re-annotated genome
    reanno_jobs_dict = {}

    for target_sp in gene_lost_dict:
        ref_sp_list = gene_loss_define[target_sp] + core_ref_sp_list
        reanno_jobs_dict[target_sp] = {ref_sp_id: []
                                       for ref_sp_id in ref_sp_list}

        for og_id in gene_lost_dict[target_sp]:
            for ref_sp_id in ref_sp_list:
                reanno_jobs_dict[target_sp][ref_sp_id] += OG_dict[og_id][ref_sp_id]

    for target_sp in reanno_jobs_dict:
        for ref_sp_id in reanno_jobs_dict[target_sp]:
            print(target_sp, ref_sp_id, len(
                reanno_jobs_dict[target_sp][ref_sp_id]))

    # genblasta + genewise
    # mkdir and copy file
    reanno_dir = work_dir + "/reanno"
    mkdir(reanno_dir, True)

    run_file_dict = {}
    for target_sp in gene_loss_define:
        run_file_dict[target_sp] = {"genome": reanno_dir + "/" + target_sp + ".genome.fasta",
                                    "gff": reanno_dir + "/" + target_sp + ".gff",
                                    }

        copy_file(species_info_dict[target_sp]['genome_file'],
                  run_file_dict[target_sp]["genome"])
        copy_file(species_info_dict[target_sp]
                  ['gff_file'], run_file_dict[target_sp]["gff"])

    # prepare genblasta
    genblasta_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        mkdir(target_sp_dir, True)
        for ref_sp in reanno_jobs_dict[target_sp]:
            print(target_sp, ref_sp)
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            mkdir(ref_sp_dir, True)
            ref_sp_aa_dict = read_fasta_by_faidx(
                species_info_dict[ref_sp]['pt_file'])
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq = ref_sp_aa_dict[q_seq_id]
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                with open(q_seq_file, 'w') as f:
                    f.write(">%s\n%s" % (q_seq.seqname, q_seq.seq))
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                genblasta_jobs_args_list.append(
                    (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, 0.5, 20))

    for target_sp in reanno_jobs_dict:
        cmd_string = "%s/xdformat -n %s" % (wu_blast_path,
                                            run_file_dict[target_sp]["genome"])
        cmd_run(cmd_string, silence=True)

    # run genblasta
    genblasta_out = multiprocess_running(
        genblasta_run, genblasta_jobs_args_list, 80, silence=False)

    # prepare genewise
    genewise_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                genewise_jobs_args_list.append(
                    (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/reanno/tmp', 1000, wise_prefix, False, 20))

    # run genewise
    genewise_running_out = multiprocess_running(
        genblasta_to_genewise, genewise_jobs_args_list, 80, silence=False)

    # check
    genewise_jobs_args_list = []
    for target_sp in reanno_jobs_dict:
        target_sp_dir = reanno_dir+"/"+target_sp
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                q_seq_file = ref_sp_dir+"/"+q_seq_id+".faa"
                gba_file = ref_sp_dir+"/"+q_seq_id+".gba"
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                gff_file = wise_prefix + ".gff3"
                if not os.path.exists(gff_file):
                    genewise_jobs_args_list.append(
                        (q_seq_file, run_file_dict[target_sp]['genome'], gba_file, '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.all_OrthoFinder/gene_loss_check/reanno/tmp', 1000, wise_prefix, False, 20))

    # rerun
    genewise_running_out = multiprocess_running(
        genblasta_to_genewise, genewise_jobs_args_list, 80, silence=False)

    # compare with gff file, filter out short one

    reanno_results_dict = {}
    for target_sp in reanno_jobs_dict:
        reanno_results_dict[target_sp] = {}
        # load annoed dict
        target_sp_annoed_dict = load_annotated_range(
            run_file_dict[target_sp]["gff"])
        target_sp_dir = reanno_dir+"/"+target_sp

        # load genewise output
        load_genewise_args_list = []
        for ref_sp in reanno_jobs_dict[target_sp]:
            ref_sp_dir = target_sp_dir + "/" + ref_sp
            for q_seq_id in reanno_jobs_dict[target_sp][ref_sp]:
                wise_prefix = ref_sp_dir+"/"+q_seq_id+".wise"
                gff_file = wise_prefix + ".gff3"
                load_genewise_args_list.append((gff_file,))

        tmp_out = multiprocess_running(
            load_genewise_gff, load_genewise_args_list, 80, silence=True)

        genewise_dict = {}
        for i in tmp_out:
            for gf_id in tmp_out[i]['output']:
                if gf_id in genewise_dict:
                    print("warnning: same gf id !")
                genewise_dict[gf_id] = tmp_out[i]['output'][gf_id]

        # remove genewise gf which not good coverage or has been annotated
        for gf_id in genewise_dict:
            gf = genewise_dict[gf_id]
            mRNA_qual = gf.sub_features[0].qualifiers
            coverage_ratio = abs(int(mRNA_qual['Target_Start'][0]) - int(mRNA_qual['Target_End'][0])) / int(
                mRNA_qual['Target_Length'][0])

            if coverage_ratio < 0.5:
                continue

            cds_range = [(cds.start, cds.end)
                         for cds in gf.sub_features[0].sub_features]
            cds_length = sum_interval_length(cds_range)

            overlaped_anno_range = []
            for tr in cds_range:
                if gf.chr_id in target_sp_annoed_dict:
                    overlaped_anno_range.extend(
                        list(target_sp_annoed_dict[gf.chr_id][gf.strand].find(tr)))
            overlaped_anno_range = merge_intervals(overlaped_anno_range)

            a, overlength, c = overlap_between_interval_set(
                cds_range, overlaped_anno_range)

            annoed_ratio = overlength/cds_length

            if annoed_ratio > 0.5:
                continue

            reanno_results_dict[target_sp][gf_id] = gf

    for target_sp in reanno_results_dict:
        tmp_dict = {}
        for gf_id in reanno_results_dict[target_sp]:
            gf = reanno_results_dict[target_sp][gf_id]
            gf_query = gf.sub_features[0].qualifiers['Target'][0]
            if gf_query not in tmp_dict:
                tmp_dict[gf_query] = {}
            tmp_dict[gf_query][gf_id] = gf
        reanno_results_dict[target_sp] = tmp_dict

    # diamond db
    diamond_dir = work_dir + "/diamond"
    mkdir(diamond_dir, True)

    all_sp_list = stem_sp_list + list(gene_loss_define.keys())

    # copy file
    for sp_id in all_sp_list:
        if sp_id not in run_file_dict:
            run_file_dict[sp_id] = {}
        run_file_dict[sp_id]["pt_file"] = diamond_dir + "/" + sp_id + ".faa"
        copy_file(species_info_dict[sp_id]['pt_file'],
                  run_file_dict[sp_id]["pt_file"])

    # makedb
    diamond_makedb_args_list = []
    for sp_id in all_sp_list:
        cmd_string = "diamond makedb --in %s/%s.faa --db %s/%s.dmnd" % (
            diamond_dir, sp_id, diamond_dir, sp_id)
        diamond_makedb_args_list.append((cmd_string, None, 1, True, None))

    tmp_out = multiprocess_running(
        cmd_run, diamond_makedb_args_list, 80, silence=True)

    # running
    diamond_args_list = []
    for i in all_sp_list:
        for j in all_sp_list:
            cmd_string = "diamond blastp -d %s/%s.dmnd -q %s/%s.faa -o %s/%s_vs_%s.bls --more-sensitive -p 1 --quiet -e 0.001 --compress 1" % (
                diamond_dir, j, diamond_dir, i, diamond_dir, i, j)
            diamond_args_list.append((cmd_string, None, 1, True, None))

    tmp_out = multiprocess_running(
        cmd_run, diamond_args_list, 80, silence=True)

    # reading bls results

    wvalue_dict = {}
    num = 0
    for i in all_sp_list:
        num += 1
        print(num, len(all_sp_list))
        wvalue_dict[i] = {}
        for j in all_sp_list:
            wvalue_dict[i][j] = {}
            blast_file = "%s/%s_vs_%s.bls.gz" % (diamond_dir, i, j)
            bls_file_parser = outfmt6_read_big(blast_file, gzip_flag=True)
            for query in bls_file_parser:
                q_def = query.qDef
                wvalue_dict[i][j][q_def] = {}
                for subject in query.hit:
                    s_def = subject.Hit_def
                    hsp = subject.hsp[0]
                    evalue = hsp.Hsp_evalue
                    wvalue_dict[i][j][q_def][s_def] = evalue_to_wvalue(
                        float(evalue))

    # tree check
    # prepare

    tree_dir = work_dir + "/tree"
    mkdir(tree_dir, True)

    ref_sp_aa_dict = {}
    for ref_sp in all_sp_list:
        ref_sp_aa_dict[ref_sp], b = read_fasta(
            species_info_dict[ref_sp]['pt_file'])

    for sp_id in gene_lost_dict:
        lost_og_list = gene_lost_dict[sp_id]
        tree_now_dir = tree_dir + "/" + sp_id
        mkdir(tree_now_dir, True)
        num = 0
        for og_id in lost_og_list:
            num += 1
            print(sp_id, og_id, num, len(lost_og_list))

            og_dir = tree_now_dir + "/" + og_id
            mkdir(og_dir, True)

            ref_seq_dict = {}
            wise_dict = {}
            ref_seq_sp_map = {}

            for ref_sp in stem_sp_list:
                for g_id in OG_dict[og_id][ref_sp]:
                    ref_seq_dict[g_id] = ref_sp_aa_dict[ref_sp][g_id].seq
                    if g_id in reanno_results_dict[sp_id]:
                        wise_dict[g_id] = reanno_results_dict[sp_id][g_id]
                    else:
                        wise_dict[g_id] = {}
                    ref_seq_sp_map[g_id] = ref_sp

            # get homology gene
            homology_gene_dir = {}
            homology_gene_sp_map = {}

            for ref_g_id in ref_seq_sp_map:
                for sp_id_now in stem_sp_list + [sp_id]:
                    if ref_g_id in wvalue_dict[ref_seq_sp_map[ref_g_id]][sp_id_now]:
                        for hit in wvalue_dict[ref_seq_sp_map[ref_g_id]][sp_id_now][ref_g_id]:
                            if hit not in ref_seq_sp_map:
                                wvalue = wvalue_dict[ref_seq_sp_map[ref_g_id]
                                                     ][sp_id_now][ref_g_id][hit]
                                if hit not in homology_gene_dir:
                                    homology_gene_dir[hit] = 0
                                    homology_gene_sp_map[hit] = sp_id_now
                                homology_gene_dir[hit] += wvalue

            homo_seq_dict = {}
            homo_seq_sp_map = {}
            for sp_id_now in stem_sp_list + [sp_id]:
                for i in sorted([i for i in homology_gene_dir if homology_gene_sp_map[i] == sp_id_now],
                                key=lambda x: homology_gene_dir[x], reverse=True)[0:5]:
                    homo_seq_dict[i] = ref_sp_aa_dict[sp_id_now][i].seq
                    homo_seq_sp_map[i] = sp_id_now

            # merge the same loci, get a new seq file
            good_genewise_hit_dir = {}
            wise_seq_dir = {}
            for q_id in wise_dict:
                for s_id in wise_dict[q_id]:
                    gf = wise_dict[q_id][s_id]
                    if gf.chr_id not in good_genewise_hit_dir:
                        good_genewise_hit_dir[gf.chr_id] = {"+": {}, "-": {}}
                    good_genewise_hit_dir[gf.chr_id][gf.strand][s_id] = gf.chr_loci.range
                    pep_file = reanno_dir + "/" + sp_id + "/" + \
                        ref_seq_sp_map[q_id] + "/" + q_id + ".wise.pep"
                    pep_dict, b = read_fasta(pep_file)
                    wise_seq_dir[s_id] = pep_dict[s_id+".pep"].seq

            new_gene_list = []
            for contig in good_genewise_hit_dir:
                for strand in good_genewise_hit_dir[contig]:
                    good_genewise_hit_dir[contig][strand] = group_by_intervals_with_overlap_threshold(
                        good_genewise_hit_dir[contig][strand], 0.5)

                    for group_id in good_genewise_hit_dir[contig][strand]:
                        genewise_hit_list = good_genewise_hit_dir[contig][strand][group_id]['list']
                        lengthest_hit = sorted(genewise_hit_list, key=lambda x: len(wise_seq_dir[x]), reverse=True)[
                            0]
                        good_genewise_hit_dir[contig][strand][group_id]['rep_hit'] = lengthest_hit
                        new_gene_list.append(lengthest_hit)

            add_seq_dict = {i: wise_seq_dir[i] for i in new_gene_list}

            pickle_info = (ref_seq_dict, ref_seq_sp_map,
                           homo_seq_dict, homo_seq_sp_map, add_seq_dict)

            seq_info_file = og_dir + "/seq_info.pyb"

            OUT = open(seq_info_file, 'wb')
            pickle.dump(pickle_info, OUT)
            OUT.close()

    # treeing

    args_list = []
    args_info_list = []
    for sp_id in gene_lost_dict:
        tree_now_dir = tree_dir + "/" + sp_id
        lost_og_list = gene_lost_dict[sp_id]
        for og_id in lost_og_list:
            args_info_list.append((sp_id, og_id))
            og_dir = tree_now_dir + "/" + og_id
            args_list.append((og_dir, sp_id, 10, 0.5, 0.5))

    tmp_out = multiprocess_running(
        tree_check, args_list, 80, None, False, args_info_list)

    # report
    with open(work_dir + "/tree_check.out", 'w') as f:
        for sp_id, og_id in tmp_out:
            flag, note = tmp_out[(sp_id, og_id)]['output']

            if isinstance(note, list):
                note_string = ",".join(note)
            else:
                note_string = note

            f.write("%s\t%s\t%s\t%s\n" %
                    (sp_id, og_id, str(flag), note_string))
