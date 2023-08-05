import os
import pickle
from Bio import Phylo
from itertools import combinations
from toolbiox.config import project_dir
from toolbiox.lib.common.util import pickle_step
from toolbiox.lib.common.os import have_file, logging_init, mkdir, cmd_run, multiprocess_running
from toolbiox.lib.common.evolution.orthotools2 import read_species_info, OrthoGroups
from toolbiox.lib.common.evolution.tree_operate import lookup_by_names, get_leaves, get_MRCA
from toolbiox.api.xuyuxing.comp_genome.phylogenomics import prepare_OG_work_dir, tree_pipeline, get_orthogroups_pipeline
from toolbiox.api.xuyuxing.comp_genome.mcscan import WGD_check_pipeline
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.ticker as ticker


def write_keep_gene_id_file(filter_work_dir, sp_list, keep_OG_list, OG_dict):
    # open
    keep_file_handle_dict = {}
    keep_file_dict = {}
    for sp_id in sp_list:
        keep_file_dict[sp_id] = "%s/%s.keep.id" % (filter_work_dir, sp_id)
        keep_file_handle_dict[sp_id] = open(keep_file_dict[sp_id], 'w')

    # write
    keep_gene_num_dict = {}
    for sp_id in sp_list:
        keep_gene_num_dict[sp_id] = 0
        for OG_id in keep_OG_list:
            og = OG_dict[OG_id]
            for g in og.gene_dict[sp_id]:
                g_id = g.id
                keep_file_handle_dict[sp_id].write(g_id+"\n")
                keep_gene_num_dict[sp_id] += 1

    # close
    for sp_id in sp_list:
        keep_file_handle_dict[sp_id].close()

    return keep_file_dict


def make_trees(OG_tsv_file, sp_info_dict, sp_tree_file, top_dir, method, threads):
    mkdir(top_dir, True)

    # print("read OG file")
    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)

    og_list = list(OGs.OG_dict.keys())

    for og_id in og_list:
        og = OGs.OG_dict[og_id]
        if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
            del OGs.OG_dict[og_id]
            OGs.OG_id_list.remove(og_id)

    # print("prepare_OG_work_dir")
    OGs = prepare_OG_work_dir(
        OGs, sp_info_dict, top_dir, sp_tree_file, need_cds_flag=True)

    # print("treeing")
    OGs = tree_pipeline(OGs, method, threads=threads)

    return OGs


def save_WGD_check_pipeline(save_file, *args):
    q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = WGD_check_pipeline(
        *args)
    OUT = open(save_file, 'wb')
    pickle.dump((q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict,
                 s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict), OUT)
    OUT.close()


def get_all_orthogroups(raw_OGs, OG_dir, node_list):
    mkdir(OG_dir, True)

    OG_dict = {}
    OG_tsv_dict = {}

    for taxon in node_list:
        # print(taxon)
        OG_dict[taxon] = get_orthogroups_pipeline(
            raw_OGs, taxonomy_level=taxon, conserved_arguments=None, threads=56)
        OG_tsv_file = OG_dir+"/"+taxon+".tsv"
        OG_dict[taxon].write_OG_tsv_file(OG_tsv_file)
        OG_tsv_dict[taxon] = OG_tsv_file

    return OG_dict, OG_tsv_dict


def get_gene_cover(sp_pair_list, OCF_pickle_dict):

    arrays = [['sp_pair_info'] * 5 + ['count'] * 11 + ['no_zero_ratio'] * 10,
              ['query_species', 'subject_species', 'subject_gene_num', 'no_zero_gene', 'no_zero_ratio'] + list(range(11)) + list(range(1, 11))]

    tuples = list(zip(*arrays))

    index = pd.MultiIndex.from_tuples(tuples)

    gene_cover_df = pd.DataFrame(columns=index)

    num = 0
    for sp_pair in sp_pair_list:
        # print(sp_pair)
        ocf_pyb_file = OCF_pickle_dict[sp_pair]

        TEMP = open(ocf_pyb_file, 'rb')
        q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = pickle.load(
            TEMP)
        TEMP.close()

        q_count_dict = dict(Counter([q_gene_covered_dict[i]
                                     for i in q_gene_covered_dict]))
        q_num = list(range(max(q_count_dict.keys())+1))
        q_count = [q_count_dict[i] if i in q_count_dict else 0 for i in q_num]
        q_zero = q_count_dict[0]
        q_sum = sum(q_count)
        q_no_zero_sum = q_sum - q_zero
        q_no_zero_sum_ratio = q_no_zero_sum/q_sum
        q_no_zero_num = q_num[1:]
        q_no_zero_count = [q_count_dict[i]
                           if i in q_count_dict else 0 for i in q_no_zero_num]
        q_no_zero_ratio = [i/q_no_zero_sum for i in q_no_zero_count]

        s_count_dict = dict(Counter([s_gene_covered_dict[i]
                                     for i in s_gene_covered_dict]))
        s_num = list(range(max(s_count_dict.keys())+1))
        s_count = [s_count_dict[i] if i in s_count_dict else 0 for i in s_num]
        s_zero = s_count_dict[0]
        s_sum = sum(s_count)
        s_no_zero_sum = s_sum - s_zero
        s_no_zero_sum_ratio = s_no_zero_sum/s_sum
        s_no_zero_num = s_num[1:]
        s_no_zero_count = [s_count_dict[i]
                           if i in s_count_dict else 0 for i in s_no_zero_num]
        s_no_zero_ratio = [i/s_no_zero_sum for i in s_no_zero_count]

    #     print(sp_pair)
    #     print(q_no_zero_sum_ratio)
    #     print(q_no_zero_ratio)
    #     print(s_no_zero_sum_ratio)
    #     print(s_no_zero_ratio)

#         pair_dict[sp_pair]['gene_cover_stat'] = (q_no_zero_sum_ratio, q_no_zero_ratio, s_no_zero_sum_ratio, s_no_zero_ratio)

        i, j = sp_pair

        gene_cover_df.loc[num] = [i, j, sum(s_count), s_no_zero_sum, s_no_zero_sum_ratio] + s_count + [
            0] * (11 - len(s_count)) + s_no_zero_ratio + [0] * (11 - len(s_count))
        num += 1
        gene_cover_df.loc[num] = [j, i, sum(q_count), q_no_zero_sum, q_no_zero_sum_ratio] + q_count + [
            0] * (11 - len(q_count)) + q_no_zero_ratio + [0] * (11 - len(q_count))
        num += 1

    return gene_cover_df


def hWGDdetector_main(args):
    args.work_dir = os.path.abspath(args.work_dir)

    mkdir(args.work_dir, True)

    logger = logging_init("hWGDdetector", args.log_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    # step1
    logger.info("Step1: load species info")
    sp_info_dict = read_species_info(args.sp_info_excel)
    sp_tree = Phylo.read(args.sp_tree_file, "newick")
    sp_tree_dict = lookup_by_names(sp_tree)
    sp_list = get_leaves(sp_tree, return_name=True)
    logger.info("    There are %d species in the dataset" % (len(sp_list)))

    # step2
    logger.info("Step2: load and filter orthogroups")
    OGs = OrthoGroups(OG_tsv_file=args.OG_tsv_file)

    huge_OG_list = []
    for i in OGs.OG_dict:
        og = OGs.OG_dict[i]
        for j in og.gene_dict:
            if len(og.gene_dict[j]) > args.huge_OG_gene_num:
                huge_OG_list.append(i)

    huge_OG_list = list(set(huge_OG_list))
    keep_OG_list = sorted(
        list(set(list(OGs.OG_dict.keys())) - set(list(huge_OG_list))))
    logger.info("    There are %d OGs in the database, %d of which are huge OGs, and we keep the remaining %d OGs" % (
        len(OGs.OG_dict), len(huge_OG_list), len(keep_OG_list)))

    logger.info("    Filtering cds, pt, gff files")
    filter_work_dir = args.work_dir + "/gene_filter"
    mkdir(filter_work_dir, True)
    keep_file_dict = write_keep_gene_id_file(
        filter_work_dir, sp_list, keep_OG_list, OGs.OG_dict)

    for sp_id in sp_list:
        sp = sp_info_dict[sp_id]

        # aa
        input_file = sp.pt_file
        output_file = "%s/%s.aa.filter.fasta" % (filter_work_dir, sp_id)
        gene_id_list = keep_file_dict[sp_id]

        cmd_string = "python %s/SeqParser.py FastaByID -f %s -o %s %s" % (
            project_dir, gene_id_list, output_file, input_file)
        if not have_file(output_file):
            cmd_run(cmd_string, silence=True)
        sp.raw_pt_file = sp.pt_file
        sp.pt_file = output_file
        # logger.info("%s aa ok" % sp_id)

        # cds
        input_file = sp.cds_file
        output_file = "%s/%s.cds.filter.fasta" % (filter_work_dir, sp_id)
        gene_id_list = keep_file_dict[sp_id]

        cmd_string = "python %s/SeqParser.py FastaByID -f %s -o %s %s" % (
            project_dir, gene_id_list, output_file, input_file)
        if not have_file(output_file):
            cmd_run(cmd_string, silence=True)
        sp.raw_cds_file = sp.cds_file
        sp.cds_file = output_file
        # logger.info("%s cds ok" % sp_id)

        # gff
        input_file = sp.gff_file
        output_file = "%s/%s.filter.gff3" % (filter_work_dir, sp_id)
        gene_id_list = keep_file_dict[sp_id]

        cmd_string = "python %s/GenFeatTools.py ExtractGFF %s %s %s" % (
            project_dir, gene_id_list, input_file, output_file)
        if not have_file(output_file):
            cmd_run(cmd_string, silence=True)
        sp.raw_gff_file = sp.gff_file
        sp.gff_file = output_file
        # logger.info("%s gff ok" % sp_id)

    # step3
    logger.info("Step3: Identification of orthologous genes")
    phylo_work_dir = args.work_dir + "/phylogenomics"
    mkdir(phylo_work_dir, True)

    keepOGs = OrthoGroups(from_OG_list=[
                          OGs.OG_dict[i] for i in keep_OG_list], species_list=OGs.species_list)
    keepOGs_file = phylo_work_dir + "/filter.orthogroups.tsv"
    keepOGs.write_OG_tsv_file(keepOGs_file)

    tree_dir = phylo_work_dir + "/tree"
    mkdir(tree_dir, True)

    logger.info("    Building trees")
    # fasttree
    fasttree_OGs_pyb = tree_dir + "/fasttree_OGs.pyb"
    FT_OGs = pickle_step(make_trees, [
                         keepOGs_file, sp_info_dict, args.sp_tree_file, tree_dir+"/fasttree", "fasttree", args.threads], fasttree_OGs_pyb)

    # # treebest
    # treebest_OGs_pyb = tree_dir + "/treebest_OGs.pyb"
    # TB_OGs = pickle_step(make_trees, [
    #                      OG_tsv_file, sp_info_dict, sp_tree_file, tree_dir+"/treebest", "treebest"], treebest_OGs_pyb)

    # # raxml
    # raxml_OGs_pyb = tree_dir + "/raxml_OGs.pyb"
    # RM_OGs = pickle_step(make_trees, [OG_tsv_file, sp_info_dict, species_tree_file, tree_dir+"/raxml", "raxml"], raxml_OGs_pyb)

    logger.info("    Get orthologous genes")
    node_list = [clade.name for clade in sp_tree.get_nonterminals()]
    logger.info("        There are %d nodes in species tree" %
                (len(node_list)))

    OG_dir = args.work_dir + "/orthogroups"

    subOGs_dict_pyb = OG_dir + "/subOGs_dict.pyb"
    subOGs_dict, subOGs_tsv_dict = pickle_step(
        get_all_orthogroups, [FT_OGs, OG_dir, node_list], subOGs_dict_pyb)

    species_tree_clade_dict = lookup_by_names(sp_tree)

    mrca_dict = {}
    for sp_pair in combinations(sp_list, 2):
        mrca_dict[tuple(sorted(sp_pair))] = get_MRCA(
            species_tree_clade_dict[sp_pair[0]], species_tree_clade_dict[sp_pair[1]], sp_tree).name

    sp_pair_list = list(mrca_dict.keys())

    logger.info("        There are %d species, %d species-pair, all orthologous gene extracted!" %
                (len(sp_list), len(sp_pair_list)))

    # step4
    logger.info("Step4: Use orthologous gene build OCF")
    logger.info("    Running mcscanxh")
    mcscanxh_dir = args.work_dir + "/mcscanxh"
    mkdir(mcscanxh_dir, True)

    mcscanxh_file_dict = {}

    args_list = []

    for sp_pair in sp_pair_list:
        i, j = sp_pair
        mrca = mrca_dict[sp_pair]
        orthologous_file = subOGs_tsv_dict[mrca]
        mcscanxh_file_dict[sp_pair] = "%s/%s_vs_%s_h" % (
            mcscanxh_dir, i, j)
        cmd_string = "python %s/OrthoTools.py mcscanxhGO -sp1 %s -sp2 %s -sp2_gff %s -w %s %s %s" % (
            project_dir, i, j, sp_info_dict[j].gff_file, mcscanxh_file_dict[sp_pair], sp_info_dict[i].gff_file, orthologous_file)

        args_list.append((cmd_string, mcscanxh_dir, 1, True))

    multiprocess_running(cmd_run, args_list, 16, silence=False)

    logger.info("    Load OCFs")

    OCF_pickle_dict = {}
    for sp_pair in sp_pair_list:
        # print(sp_pair)

        i, j = sp_pair

        mcscanx_collinearity_file = mcscanxh_file_dict[sp_pair] + \
            "/mcscanx.collinearity"
        query_gff3 = sp_info_dict[i].gff_file
        subject_gff3 = sp_info_dict[j].gff_file

        ocf_pyb_file = mcscanxh_file_dict[sp_pair] + "/ocf.pyb"
        OCF_pickle_dict[sp_pair] = ocf_pyb_file

        if os.path.exists(ocf_pyb_file):
            continue

        save_WGD_check_pipeline(
            ocf_pyb_file, mcscanx_collinearity_file, i, query_gff3, None, j, subject_gff3, None)

    # step5
    logger.info("Step5: Identification of hWGD")

    gene_cover_pyb = args.work_dir + "/gene_cover_df.pyb"
    gene_cover_df = pickle_step(
        get_gene_cover, [sp_pair_list, OCF_pickle_dict], gene_cover_pyb)

    gene_cover_excel = args.work_dir + "/gene_cover_df.xlsx"
    writer = pd.ExcelWriter(gene_cover_excel)
    gene_cover_df.to_excel(writer)
    writer.save()

    fig = plt.figure(figsize=(20, 20))

    speci_num = len(sp_list)

    num = 1
    for i in sp_list:
        for j in sp_list:

            ax = fig.add_subplot(speci_num, speci_num, num)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
            ax.set_xlim(0, 8)
            ax.set_ylim(0, 1)

            if not num % speci_num == 1 and num != 2:
                labels = [item.get_text() for item in ax.get_yticklabels()]

                empty_string_labels = ['']*len(labels)
                ax.set_yticklabels(empty_string_labels)

            if num < speci_num * (speci_num - 1):
                labels = [item.get_text() for item in ax.get_xticklabels()]

                empty_string_labels = ['']*len(labels)
                ax.set_xticklabels(empty_string_labels)

            if i == j:
                text = ax.text(3.5, 0.5, i, ha='center', va='center', size=20)
                text.set_path_effects([path_effects.Normal()])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                num += 1
                continue
            else:
                row = gene_cover_df[(gene_cover_df.sp_pair_info.query_species == i) & (
                    gene_cover_df.sp_pair_info.subject_species == j)]
                plot_no_zero_sum_ratio = float(row.sp_pair_info.no_zero_ratio)
                plot_no_zero_ratio = list(row.no_zero_ratio.iloc[0])[0:8]

    #             sp_pair = (i,j)
    #             sp_pair_r = (j,i)
    #             if sp_pair in pair_dict:
    #                 q_no_zero_sum_ratio, q_no_zero_ratio, s_no_zero_sum_ratio, s_no_zero_ratio = pair_dict[sp_pair]['gene_cover_stat']
    #                 plot_no_zero_sum_ratio, plot_no_zero_ratio = s_no_zero_sum_ratio, s_no_zero_ratio
    #             else:
    #                 q_no_zero_sum_ratio, q_no_zero_ratio, s_no_zero_sum_ratio, s_no_zero_ratio = pair_dict[sp_pair_r]['gene_cover_stat']
    #                 plot_no_zero_sum_ratio, plot_no_zero_ratio = q_no_zero_sum_ratio, q_no_zero_ratio

                text = ax.text(3.5, 0.80, "%.2f%%" %
                               (plot_no_zero_sum_ratio*100), size=12)
                ax.bar(list(range(1, len(plot_no_zero_ratio)+1)),
                       plot_no_zero_ratio)
                num += 1

    plt.show()

    save_file = args.work_dir + "/hWGD_fig.pdf"

    fig.savefig(save_file, format='pdf', facecolor='none',
                edgecolor='none', bbox_inches='tight')


if __name__ == "__main__":
    class abc():
        pass

    args = abc()

    args.work_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/publish2/2.WGD/tmp'
    args.log_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/publish2/2.WGD/tmp/log'
    args.sp_info_excel = '/lustre/home/xuyuxing/Work/Orobanchaceae/publish2/2.WGD/tmp/Oro_ref.xlsx'
    args.sp_tree_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/publish2/2.WGD/tmp/species.tre'
    args.OG_tsv_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/publish2/2.WGD/tmp/Orthogroups.tsv'
    args.huge_OG_gene_num = 30
    args.threads = 56

    hWGDdetector_main(args)
