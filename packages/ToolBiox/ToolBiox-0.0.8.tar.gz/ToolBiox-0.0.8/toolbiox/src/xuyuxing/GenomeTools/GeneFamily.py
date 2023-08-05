from toolbiox.api.xuyuxing.evolution.badirate import main_pipeline, F_index, get_branch_name
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import numpy as np
from toolbiox.config import badirate_path
from collections import OrderedDict
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.os import mkdir, rmdir, multiprocess_running
from io import StringIO
from Bio import Phylo
from toolbiox.lib.common.evolution.tree_operate import get_sons
import re


def badirate_one(c_id, gene_count_tuple, species_name_list, species_tree, work_dir, just_load):
    # build size file
    tmp_dir = work_dir + "/" + c_id
    mkdir(tmp_dir, True)

    try:
        size_file = tmp_dir+"/size_file"
        with open(size_file, 'w') as f:
            head_string = printer_list(
                species_name_list, sep='\t', head="FAM_ID\t")
            f.write(head_string+"\n")
            count_string = printer_list(
                gene_count_tuple, sep='\t', head=c_id+"\t")
            f.write(count_string+"\n")

        output = main_pipeline(c_id, size_file, species_tree,
                               tmp_dir+"/run", badirate_path, None, True, just_load)

        return output

    except:
        return None


def get_leaf_branch(labeled_tree_string):
    labeled_tree = StringIO(labeled_tree_string)

    tree = Phylo.read(labeled_tree, 'newick')

    all_branch = []
    species_name_map = {}
    for clade in tree.find_clades(order='level'):
        if clade.is_terminal():
            continue
        else:
            for son in get_sons(clade):
                clade_name = clade.confidence
                if son.is_terminal():
                    son_speci_name, son_name = re.match(
                        r'^(\S+)_(\d+)$', son.name).groups()
                    species_name_map[son_speci_name] = son_name
                else:
                    son_name = son.confidence

                all_branch.append("%s->%s" % (clade_name, son_name))

    for species_name in species_name_map:
        for i in all_branch:
            if i.split(">")[-1] == species_name_map[species_name]:
                species_name_map[species_name] = (
                    species_name_map[species_name], i)
                break

    return species_name_map


def gene_family_stat_main(Orthogroups_GeneCount_tsv, species_tree, species_name_list, conserved_species_name_list, work_dir, threads, log_file, output_prefix, just_load=False):
    mkdir(work_dir, True)

    # get gene count
    gene_count_dict = tsv_file_dict_parse(
        Orthogroups_GeneCount_tsv, key_col='Orthogroup', fields=species_name_list)
    for OG_id in gene_count_dict:
        for i in gene_count_dict[OG_id]:
            gene_count_dict[OG_id][i] = int(gene_count_dict[OG_id][i])

    # # test
    # import random
    # gene_count_dict = {i: gene_count_dict[i]
    #                    for i in random.sample(list(gene_count_dict), 56)}
    # # test end

    # get f index
    F_index_dict = OrderedDict()
    for OG_id in gene_count_dict:
        gene_count_tuple = tuple([gene_count_dict[OG_id][i]
                                  for i in species_name_list])
        f_index_tuple = F_index(gene_count_tuple)
        F_index_dict[OG_id] = OrderedDict()
        for i in range(len(species_name_list)):
            F_index_dict[OG_id][species_name_list[i]] = f_index_tuple[i]

    # get badirate
    badirate_input_dict_tmp = {}
    single_species_OG_list = []
    huge_OG_list = []
    for OG_id in gene_count_dict:

        f_index_tuple = tuple([F_index_dict[OG_id][i]
                               for i in F_index_dict[OG_id]])
        gene_count_tuple = tuple([gene_count_dict[OG_id][i]
                                  for i in gene_count_dict[OG_id]])

        if 1.0 in f_index_tuple:
            single_species_OG_list.append(OG_id)
        elif len([i for i in gene_count_tuple if i >= 100]) > 0:
            huge_OG_list.append(OG_id)
        else:
            if gene_count_tuple not in badirate_input_dict_tmp:
                badirate_input_dict_tmp[gene_count_tuple] = []

            badirate_input_dict_tmp[gene_count_tuple].append(OG_id)

    badirate_input_dict = {}
    num = 0
    for gene_count_tuple in badirate_input_dict_tmp:
        badirate_input_dict["C"+str(num)] = {
            "tuple": gene_count_tuple,
            "OG": badirate_input_dict_tmp[gene_count_tuple]
        }
        num += 1

    # run badirate

    args_list = []
    args_id_list = []
    for c_id in badirate_input_dict:
        gene_count_tuple = badirate_input_dict[c_id]["tuple"]
        args_list.append(
            (c_id, gene_count_tuple, species_name_list, species_tree, work_dir, just_load))
        args_id_list.append(c_id)

        # badirate_one(c_id, gene_count_tuple, species_name_list, species_tree, work_dir)

    # mp_out = multiprocess_running(badirate_one, args_list, threads,
    #                               log_file=log_file, silence=True, args_id_list=args_id_list, timeout=86400)

    # mp_out = multiprocess_running(badirate_one, args_list, threads,
    #                               log_file=log_file, silence=True, args_id_list=args_id_list, timeout=3600)

    mp_out = multiprocess_running(badirate_one, args_list, threads,
                                  log_file=log_file, silence=True, args_id_list=args_id_list)

    for c_id in mp_out:
        output = mp_out[c_id]['output']
        error = mp_out[c_id]['error']

        if error == "timeout":
            badirate_input_dict[c_id]["output"] = None
        else:
            if output:
                badirate_input_dict[c_id]["output"] = output
            else:
                badirate_input_dict[c_id]["output"] = None

    # make report
    report_dict = {}
    for c_id in badirate_input_dict:
        gene_count_tuple = badirate_input_dict[c_id]['tuple']
        output = badirate_input_dict[c_id]['output']
        OG_list = badirate_input_dict[c_id]['OG']

        species_num = len(gene_count_tuple) - gene_count_tuple.count(0)
        gene_sum = sum(gene_count_tuple)

        if [gene_count_tuple[species_name_list.index(i)] for i in conserved_species_name_list].count(0) == 0:
            conserved = True
        else:
            conserved = False

        for OG_id in OG_list:

            report_dict[OG_id] = {
                'gene_count': gene_count_tuple,
                'F_index':  tuple([F_index_dict[OG_id][i] for i in species_name_list]),
                'species_num': species_num,
                'gene_sum': gene_sum,
                'conserved': conserved,
            }

            if output is None:
                report_dict[OG_id]['Gain'] = []
                report_dict[OG_id]['Loss'] = []
                report_dict[OG_id]['Expansion'] = []
                report_dict[OG_id]['Contraction'] = []
                report_dict[OG_id]['Likeilhood'] = -999
            else:
                report_dict[OG_id]['Gain'] = output[1]
                report_dict[OG_id]['Loss'] = output[2]
                report_dict[OG_id]['Expansion'] = output[3]
                report_dict[OG_id]['Contraction'] = output[4]
                report_dict[OG_id]['Likeilhood'] = output[5]
                labeled_tree_string = output[6]

    species_name_map = get_leaf_branch(labeled_tree_string)

    for OG_id in gene_count_dict:
        if OG_id in report_dict:
            continue

        gene_count_tuple = tuple([gene_count_dict[OG_id][i]
                                  for i in species_name_list])
        f_index_tuple = tuple([F_index_dict[OG_id][i]
                               for i in species_name_list])

        species_num = len(gene_count_tuple) - gene_count_tuple.count(0)
        gene_sum = sum(gene_count_tuple)

        conserved = False

        Gains = []
        for i in gene_count_dict[OG_id]:
            if gene_count_dict[OG_id][i] != 0:
                Gains = [species_name_map[i][1]]

        report_dict[OG_id] = {
            'gene_count': gene_count_tuple,
            'F_index':  f_index_tuple,
            'species_num': species_num,
            'gene_sum': gene_sum,
            'conserved': conserved,
            'Gain': Gains,
            'Loss': [],
            'Expansion': [],
            'Contraction': [],
            'Likeilhood': -999
        }

    output_tsv_file = output_prefix + ".tsv"
    output_label_tre = output_prefix + ".label.tree"

    with open(output_label_tre, 'w') as f:
        f.write(labeled_tree_string)

    with open(output_tsv_file, 'w') as f:
        header_string = printer_list(["Family ID"] + species_name_list + ['Conserved',
                                                                          'Sum', 'Species', 'Gain', 'Loss', 'Expansion', 'Contraction', 'Likeilhood'] + species_name_list, sep='\t')
        f.write(header_string+"\n")

        for OG_id in gene_count_dict:
            Gains_string = printer_list(report_dict[OG_id]['Gain'], sep=',')
            Losses_string = printer_list(report_dict[OG_id]['Loss'], sep=',')
            Expansion_string = printer_list(
                report_dict[OG_id]['Expansion'], sep=',')
            Contraction_string = printer_list(
                report_dict[OG_id]['Contraction'], sep=',')

            output_list = [OG_id] + list(report_dict[OG_id]['gene_count']) + [report_dict[OG_id]['conserved'], report_dict[OG_id]['gene_sum'],
                                                                              report_dict[OG_id]['species_num'], Gains_string, Losses_string, Expansion_string, Contraction_string, report_dict[OG_id]['Likeilhood']] + list(report_dict[OG_id]['F_index'])
            output_string = printer_list(output_list, sep='\t')
            f.write(output_string+"\n")


if __name__ == "__main__":

    Orthogroups_GeneCount_tsv = '/lustre/home/xuyuxing/Work/Gel/gene_family_expand/pt_file/badirate/Orthogroups.GeneCount.tsv'
    species_tree = '/lustre/home/xuyuxing/Work/Gel/gene_family_expand/pt_file/badirate/species_tree.tre'
    species_name_list = ["Osa", "Dal", "Tze",
                         "Xvi", "Aof", "Ash", "Dca", "Peq", "Gel"]
    conserved_species_name_list = ["Osa", "Dal", "Tze", "Xvi", "Aof"]
    work_dir = '/lustre/home/xuyuxing/Work/Gel/gene_family_expand/pt_file/badirate/tmp'
    threads = 56
    log_file = '/lustre/home/xuyuxing/Work/Gel/gene_family_expand/pt_file/badirate/log'
    output_prefix = '/lustre/home/xuyuxing/Work/Gel/gene_family_expand/pt_file/badirate/genefamily'

    gene_family_stat_main(Orthogroups_GeneCount_tsv, species_tree, species_name_list,
                          conserved_species_name_list, work_dir, threads, log_file, output_prefix, just_load)

    #
    Orthogroups_GeneCount_tsv = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.6.hcluster/hcluster/hcluster.GeneCount.tsv"
    species_tree = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.6.hcluster/hcluster/SpeciesTree_rooted.txt"
    species_name_list = ["Atr", "Cka", "Lch", "Cnu", "Osa", "Zma",
                         "Acom", "Aof", "Gel", "Dca", "Peq", "Vpl", "Ash", "Xvi", "Dal"]
    conserved_species_name_list = [
        "Atr", "Cka", "Lch", "Cnu", "Osa", "Zma", "Acom", "Aof", "Xvi", "Dal"]
    work_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.6.hcluster/hcluster/tmp"
    threads = 160
    log_file = work_dir+"/log"
    output_prefix = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/OrthoFinder/3.6.hcluster/hcluster/badirates"
    just_load = False

    gene_family_stat_main(Orthogroups_GeneCount_tsv, species_tree, species_name_list,
                          conserved_species_name_list, work_dir, threads, log_file, output_prefix, just_load=False)

    #
    Orthogroups_GeneCount_tsv = "/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/merge_OGs_num.tsv"
    species_tree = "/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/species_time.tre"
    species_name_list = ["Ath","Cau","Cca","Ini","Llu","Mgu","Ocu","Pae","Pcr","Pja","Sas","Sin","Sly"]
    conserved_species_name_list = ["Atr", "Cca", "Ini", "Llu", "Mgu", "Sly"]
    work_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/tmp"
    threads = 160
    log_file = work_dir+"/log"
    output_prefix = "/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/badirates"
    just_load = False

    gene_family_stat_main(Orthogroups_GeneCount_tsv, species_tree, species_name_list,
                          conserved_species_name_list, work_dir, threads, log_file, output_prefix, just_load=False)
