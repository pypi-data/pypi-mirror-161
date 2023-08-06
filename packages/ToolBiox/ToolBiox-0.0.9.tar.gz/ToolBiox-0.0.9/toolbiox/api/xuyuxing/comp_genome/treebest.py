from toolbiox.api.xuyuxing.comp_genome.orthofinder import OG_tsv_file_parse, write_OG_tsv_file
from toolbiox.lib.common.evolution.tree_operate import add_clade_name, clade_rename, ignore_branch_length, load_nhx_tree, lookup_by_names, get_offspring
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
import os
import re
import pandas as pd
from io import StringIO
from Bio import Phylo
from toolbiox.lib.common.os import mkdir, cmd_run, multiprocess_running
from toolbiox.lib.common.math.set import merge_same_element_set
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.fileIO import tsv_file_dict_parse


def get_species_from_tree(SpeciesTree_rooted_file):
    species_rooted_tree = Phylo.read(SpeciesTree_rooted_file, 'newick')
    return [i.name for i in species_rooted_tree.get_terminals()]


def prepare_treebest_species_tree(SpeciesTree_rooted_file, treebest_species_tree_file, OG_sp_name_map):
    OG_sp_name_map_for_rename_tree = {
        i: OG_sp_name_map[i]+"*" for i in OG_sp_name_map}

    tmp_handle = StringIO()

    species_rooted_tree = Phylo.read(SpeciesTree_rooted_file, 'newick')
    species_rooted_tree = clade_rename(
        species_rooted_tree, OG_sp_name_map_for_rename_tree)
    species_rooted_tree = add_clade_name(species_rooted_tree, True)
    species_rooted_tree = ignore_branch_length(species_rooted_tree, True)
    Phylo.write(species_rooted_tree, tmp_handle, "newick")
    tree_string = tmp_handle.getvalue()

    tree_string = re.sub(r'\d+\.\d+', '', tree_string)
    tree_string = re.sub(r':', '', tree_string)

    with open(treebest_species_tree_file, 'w') as f:
        f.write(tree_string)

    return treebest_species_tree_file


def rename_OG_dict(OG_dict, OG_sp_name_map):
    rename_OG_dict = {}
    for i in OG_dict:
        rename_OG_dict[i] = {}
        for j in OG_dict[i]:
            rename_OG_dict[i][OG_sp_name_map[j]] = OG_dict[i][j]

    return rename_OG_dict


def read_species_info(species_info_table):
    species_info_df = pd.read_excel(species_info_table)
    species_info_dict = {}
    for index in species_info_df.index:
        sp_id = str(species_info_df.loc[index]['sp_id'])
        species_info_dict[sp_id] = {}
        species_info_dict[sp_id]['pt_file'] = str(
            species_info_df.loc[index]['pt_file'])
        species_info_dict[sp_id]['cds_file'] = str(
            species_info_df.loc[index]['cds_file'])
        species_info_dict[sp_id]['OG_species_id'] = str(
            species_info_df.loc[index]['OG_species_id'])
        species_info_dict[sp_id]['sp_id'] = sp_id

    return species_info_dict


def prepare_OG_work_dir(OG_dict, species_info_dict, top_work_dir):
    mkdir(top_work_dir, True)

    huge_pt_dict = {}
    huge_cds_dict = {}
    huge_rename_map = {}

    # read fasta
    for i in species_info_dict:
        pt_fa_dict = read_fasta_by_faidx(species_info_dict[i]['pt_file'])
        cds_fa_dict = read_fasta_by_faidx(species_info_dict[i]['cds_file'])

        pt_dict = {}
        cds_dict = {}
        rename_map = {}

        num = 0
        for j in pt_fa_dict:
            pt_dict[num] = pt_fa_dict[j].seq
            cds_dict[num] = cds_fa_dict[j].seq
            rename_map[j] = num
            num += 1

        huge_pt_dict[i] = pt_dict
        huge_cds_dict[i] = cds_dict
        huge_rename_map[i] = rename_map

    # write seq to each OG
    for OG_id in OG_dict:
        OG_work = top_work_dir + "/" + OG_id
        mkdir(OG_work, True)

        # pt_file
        pt_fa = OG_work + "/pt.fa"
        with open(pt_fa, 'w') as f:
            for sp_id in OG_dict[OG_id]:
                for g_id in OG_dict[OG_id][sp_id]:
                    if g_id != '':
                        pt_seq = huge_pt_dict[sp_id][huge_rename_map[sp_id][g_id]]
                        f.write(">%s\n%s\n" % (
                            str(huge_rename_map[sp_id][g_id])+"_"+sp_id, pt_seq))

        # cds_file
        cds_fa = OG_work + "/cds.fa"
        with open(cds_fa, 'w') as f:
            for sp_id in OG_dict[OG_id]:
                for g_id in OG_dict[OG_id][sp_id]:
                    if g_id != '':
                        cds_seq = huge_cds_dict[sp_id][huge_rename_map[sp_id][g_id]]
                        f.write(">%s\n%s\n" % (
                            str(huge_rename_map[sp_id][g_id])+"_"+sp_id, cds_seq))

        # rename_map
        rename_map = OG_work + "/rename.map"
        with open(rename_map, 'w') as f:
            for sp_id in OG_dict[OG_id]:
                for g_id in OG_dict[OG_id][sp_id]:
                    if g_id != '':
                        f.write("%s\t%s\t%s\n" %
                                (huge_rename_map[sp_id][g_id], g_id, sp_id))

    # write rename file
    all_rename_map = top_work_dir + "/rename.map"
    with open(all_rename_map, 'w') as f:
        for sp_id in huge_rename_map:
            for g_id in huge_rename_map[sp_id]:
                if g_id != '':
                    f.write("%s\t%s\t%s\n" %
                            (huge_rename_map[sp_id][g_id], g_id, sp_id))


def treebest_one(OG_work_dir, treebest_species_tree_file):
    pt_fa = OG_work_dir + "/pt.fa"
    cds_fa = OG_work_dir + "/cds.fa"

    aa_aln_file = pt_fa+".aln"
    aa_dnd_file = pt_fa+".dnd"
    #cmd_string = "t_coffee "+aa_file+" -method mafftgins_msa muscle_msa kalign_msa t_coffee_msa -output=fasta_aln -outfile="+aa_aln_file+" -newtree "+aa_dnd_file
    cmd_string = "clustalw2 -INFILE="+pt_fa + \
        " -ALIGN -OUTPUT=FASTA -OUTFILE="+aa_aln_file+" -type=protein"
    cmd_run(cmd_string, silence=True)

    cds_aln_file = cds_fa+".cds.aln"
    cmd_string = "treebest backtrans "+aa_aln_file+" "+cds_fa+" > "+cds_aln_file
    cmd_run(cmd_string, silence=True)

    nhx_file = OG_work_dir+"/best.nhx"
    cmd_string = "treebest best -f "+treebest_species_tree_file + \
        " -o "+nhx_file+" "+cds_aln_file
    cmd_run(cmd_string, silence=True)

    out_file = OG_work_dir+"/best.nhx.out"
    cmd_string = "treebest nj -s "+treebest_species_tree_file + \
        " -t dm -vc "+nhx_file+" "+cds_aln_file+" > "+out_file
    cmd_run(cmd_string, silence=True)


def get_orthologous_from_nhx_out(nhx_out_file):
    with open(nhx_out_file, 'r') as f:
        all_text = f.read()

        info = all_text.split('@')
        pairs = []
        for i in info:
            match = re.match(r'.*begin full_ortholog.*', i)
            if match:
                lines = i.split('\n')
                while '' in lines:
                    lines.remove('')
                while 'begin full_ortholog' in lines:
                    lines.remove('begin full_ortholog')
                for j in lines:
                    details = j.split("\t")
                    if details[4] == "1":
                        pairs.append([details[0], details[1]])

        pairs = merge_same_element_set(pairs)

    return pairs







def get_homologous_under_give_tax_from_nhx_tree(nhx_tree_file, species_tree_file, taxonomy_level):
    """return all homologous under a taxonomy level, paralogous will not be removed"""

    taxonomy_list = get_taxonomy_list_from_species_tree_file(
        species_tree_file, taxonomy_level, include_clade=True)

    nhx_tree, clade_dict = load_nhx_tree(nhx_tree_file)
    pairs = []
    for clade_name in clade_dict:
        clade = clade_dict[clade_name]
        if clade.nhx_dict["Scientific name"] in taxonomy_list:
            pairs.append([i.name for i in clade.get_terminals()])

    pairs = merge_same_element_set(pairs)

    return pairs


def OG_dict_to_gene_species_hash(OG_dict):
    output = {}
    for i in OG_dict:
        for j in OG_dict[i]:
            for k in OG_dict[i][j]:
                output[k] = j
    return output


def treebest_many(OG_tsv_file, species_info_table, SpeciesTree_rooted_file, work_dir, num_threads):
    mkdir(work_dir, True)
    log_file = work_dir + "/log"
    treebest_species_tree_file = work_dir + "/treebest_species_tree.txt"

    module_log = logging_init("TreeBest pipeline", log_file)

    # load species information
    module_log.info('load species information')
    species_list = get_species_from_tree(SpeciesTree_rooted_file)
    species_info_dict = read_species_info(species_info_table)
    species_info_dict = {i: species_info_dict[i]
                         for i in species_info_dict if i in species_list}
    OG_sp_name_map = {}
    for i in species_info_dict:
        OG_sp_name_map[species_info_dict[i]['OG_species_id']] = i

    # get species tree
    module_log.info('load species tree')
    prepare_treebest_species_tree(
        SpeciesTree_rooted_file, treebest_species_tree_file, OG_sp_name_map)

    # load orthofinder group
    module_log.info('load orthofinder group')
    OG_dict = OG_tsv_file_parse(OG_tsv_file)
    OG_dict = rename_OG_dict(OG_dict, OG_sp_name_map)

    # prepare OG work dir
    module_log.info('prepare OG work dir')
    prepare_OG_work_dir(OG_dict, species_info_dict, work_dir)

    # running treebest
    module_log.info('running treebest')
    args_list = []

    for OG_id in OG_dict:
        OG_work_dir = work_dir + "/" + OG_id
        args_list.append((OG_work_dir, treebest_species_tree_file))

    multiprocess_running(treebest_one, args_list,
                         num_threads, log_file=log_file)

    return work_dir


def get_orthologous_from_treebest(treebest_work_dir, species_tree_file, taxonomy_level, used_OG_list=None):

    tmp_info = tsv_file_dict_parse(
        treebest_work_dir+"/rename.map", fieldnames=['new_id', 'old_id', 'speci'])

    gene_info = {}
    for i in tmp_info:
        id_tmp = tmp_info[i]['new_id'] + "_" + tmp_info[i]['speci']
        gene_info[id_tmp] = {
            'speci': tmp_info[i]['speci'],
            'old_id': tmp_info[i]['old_id'],
        }

    # get OL_dict
    OL_dict = {}

    if used_OG_list is None:
        OG_list = os.listdir(treebest_work_dir)
    else:
        OG_list = used_OG_list

    for OG_id in OG_list:
        # print(OG_id)
        OG_dir = treebest_work_dir+"/"+OG_id
        
        if not os.path.isdir(OG_dir):
            continue

        nhx_tree_file = OG_dir + "/best.nhx"

        if not os.path.exists(nhx_tree_file):
            continue

        num = 0
        for pair in get_orthologous_from_nhx_tree(nhx_tree_file, species_tree_file, taxonomy_level):
            OL_id = OG_id + "_" + str(num)
            num += 1
            # print(OL_id)
            # print(pair)

            OL_dict[OL_id] = {}
            for i in get_taxonomy_list_from_species_tree_file(species_tree_file, taxonomy_level, include_clade=False):
                OL_dict[OL_id][i] = []

            for i in pair:
                speci_now = gene_info[i]['speci']
                old_id_now = gene_info[i]['old_id']
                OL_dict[OL_id][speci_now].append(old_id_now)

    return OL_dict


def get_homologous_under_give_tax_from_treebest(treebest_work_dir, species_tree_file, taxonomy_level_list=None):

    species_list = get_taxonomy_list_from_species_tree_file(species_tree_file, include_clade=True)

    tmp_info = tsv_file_dict_parse(
        treebest_work_dir+"/rename.map", fieldnames=['new_id', 'old_id', 'speci'])

    gene_info = {}
    for i in tmp_info:
        id_tmp = tmp_info[i]['new_id'] + "_" + tmp_info[i]['speci']
        gene_info[id_tmp] = {
            'speci': tmp_info[i]['speci'],
            'old_id': tmp_info[i]['old_id'],
        }

    # get OL_dict
    clade_dict = {}
    OG_id_list = os.listdir(treebest_work_dir)
    num=0
    for OG_id in OG_id_list:
        num+=1
        print("%d/%d" % (num,len(OG_id_list)))

        clade_dict[OG_id] = {}
        
        # print(OG_id)
        OG_dir = treebest_work_dir+"/"+OG_id
        
        if not os.path.isdir(OG_dir):
            continue

        nhx_tree_file = OG_dir + "/best.nhx"

        if not os.path.exists(nhx_tree_file):
            continue

        if not taxonomy_level_list:
            taxonomy_level_list = species_list

        for taxonomy_level in taxonomy_level_list:
            clade_dict[OG_id][taxonomy_level] = []
            for pair in get_homologous_under_give_tax_from_nhx_tree(nhx_tree_file, species_tree_file, taxonomy_level):
                re_name_pair = []
                for i in pair:
                    speci_now = gene_info[i]['speci']
                    old_id_now = gene_info[i]['old_id']
                    re_name_pair.append(old_id_now)
                clade_dict[OG_id][taxonomy_level].append(re_name_pair)

    return clade_dict


if __name__ == "__main__":
    # input
    OG_tsv_file = '/lustre/home/xuyuxing/Work/Gel/synteny/6/gene/treebest/Orthogroups.tsv'
    species_info_table = '/lustre/home/xuyuxing/Work/Gel/synteny/6/gene/treebest/gene_file_info.xlsx'
    SpeciesTree_rooted_file = '/lustre/home/xuyuxing/Work/Gel/synteny/6/gene/treebest/species.txt'
    work_dir = '/lustre/home/xuyuxing/Work/Gel/synteny/6/gene/treebest/output'
    OL_tsv_file = '/lustre/home/xuyuxing/Work/Gel/synteny/6/gene/treebest/Orthologous.tsv'
    num_threads = 56

    treebest_work_dir = treebest_many(
        OG_tsv_file, species_info_table, SpeciesTree_rooted_file, work_dir, num_threads)

    OL_dict = get_orthologous_from_treebest(
        treebest_work_dir, SpeciesTree_rooted_file, taxonomy_level='Orchidaceae')

    write_OG_tsv_file(OL_dict, OL_tsv_file)
