from toolbiox.lib.common.os import mkdir, copy_file, cmd_run, multiprocess_running
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, get_orthogroups_from_tree, get_non_overlap_orthogroups, OGs_gene_rename, merge_OGs, read_species_info, if_conserved
from Bio import Phylo
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.evolution.tree_operate import get_root_by_species, reroot_by_outgroup_clade, add_clade_name, lookup_by_names


def prepare_OG_work_dir(OGs, species_info_dict, top_work_dir, need_cds_flag=False):
    mkdir(top_work_dir, True)

    huge_pt_dict = {}
    if need_cds_flag:
        huge_cds_dict = {}
    huge_rename_map = {}

    # read fasta
    for sp_id in OGs.species_list:
        sp = species_info_dict[sp_id]
        pt_fa_dict = read_fasta_by_faidx(sp.pt_file)
        if need_cds_flag:
            cds_fa_dict = read_fasta_by_faidx(sp.cds_file)

        pt_dict = {}
        if need_cds_flag:
            cds_dict = {}
        rename_map = {}

        num = 0
        for j in pt_fa_dict:
            pt_dict[num] = pt_fa_dict[j].seq
            if need_cds_flag:
                cds_dict[num] = cds_fa_dict[j].seq
            rename_map[j] = num
            num += 1

        huge_pt_dict[sp_id] = pt_dict
        if need_cds_flag:
            huge_cds_dict[sp_id] = cds_dict
        huge_rename_map[sp_id] = rename_map

    # write seq to each OG
    for OG_id in OGs.OG_dict:
        OG_work = top_work_dir + "/" + OG_id
        mkdir(OG_work, True)

        # pt_file
        pt_fa = OG_work + "/pt.fa"
        with open(pt_fa, 'w') as f:
            OG_gene_dict = OGs.get((OG_id, None))
            for sp_id in OG_gene_dict:
                for gene in OG_gene_dict[sp_id]:
                    g_id = gene.id
                    if g_id != '':
                        pt_seq = huge_pt_dict[sp_id][huge_rename_map[sp_id][g_id]]
                        f.write(">%s\n%s\n" % (
                            str(huge_rename_map[sp_id][g_id])+"_"+sp_id, pt_seq))

        # cds_file
        if need_cds_flag:
            cds_fa = OG_work + "/cds.fa"
            with open(cds_fa, 'w') as f:
                for sp_id in OG_gene_dict:
                    for gene in OG_gene_dict[sp_id]:
                        g_id = gene.id
                        if g_id != '':
                            cds_seq = huge_cds_dict[sp_id][huge_rename_map[sp_id][g_id]]
                            f.write(">%s\n%s\n" % (
                                str(huge_rename_map[sp_id][g_id])+"_"+sp_id, cds_seq))

        # rename_map
        rename_map = OG_work + "/rename.map"
        with open(rename_map, 'w') as f:
            for sp_id in OG_gene_dict:
                for gene in OG_gene_dict[sp_id]:
                    g_id = gene.id
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


def fasttree_one(OG_work_dir):
    pt_fa = OG_work_dir + "/pt.fa"

    aa_aln_file = pt_fa+".aln"
    aa_dnd_file = pt_fa+".dnd"
    #cmd_string = "t_coffee "+aa_file+" -method mafftgins_msa muscle_msa kalign_msa t_coffee_msa -output=fasta_aln -outfile="+aa_aln_file+" -newtree "+aa_dnd_file
    cmd_string = "clustalw2 -INFILE="+pt_fa + \
        " -ALIGN -OUTPUT=FASTA -OUTFILE="+aa_aln_file+" -type=protein"
    cmd_run(cmd_string, silence=True)

    tree_file = OG_work_dir+"/fasttree.phb"
    cmd_string = "FastTree -wag -gamma -out %s %s >/dev/null" % (
        tree_file, aa_aln_file)
    cmd_run(cmd_string, silence=True)

    return pt_fa, aa_aln_file, tree_file


def fasttree_many(OGs, species_info_dict, work_dir, num_threads):
    mkdir(work_dir, True)
    log_file = work_dir + "/log"

    module_log = logging_init("FastTree pipeline", log_file)

    # load orthofinder group
    module_log.info('load orthofinder group')

    # prepare OG work dir
    module_log.info('prepare OG work dir')
    prepare_OG_work_dir(OGs, species_info_dict, work_dir)

    # running treebest
    module_log.info('running fasttree')
    args_list = []

    for OG_id in OGs.OG_dict:
        OG_work_dir = work_dir + "/" + OG_id
        args_list.append((OG_work_dir,))

    multiprocess_running(fasttree_one, args_list,
                         num_threads, log_file=log_file)

    return work_dir


def read_rename_map_file(rename_map_file):
    info_dict = tsv_file_dict_parse(rename_map_file, fieldnames=[
                                    "new_id", "old_id", "sp_id"])
    gene_to_species_map_dict = {}
    rename_dict = {}
    for i in info_dict:
        gene_to_species_map_dict[info_dict[i]["new_id"] +
                                 "_" + info_dict[i]["sp_id"]] = info_dict[i]["sp_id"]
        rename_dict[info_dict[i]["new_id"] + "_" +
                    info_dict[i]["sp_id"]] = info_dict[i]["old_id"]

    return rename_dict, gene_to_species_map_dict


unrooted_tree_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/fasttree/OG0001487/fasttree.phb'
species_tree_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/species.tree.txt'
rename_map_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/fasttree/OG0001487/rename.map'
output_tree_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/fasttree/OG0001487/fasttree.rooted.phb'

def rooted_tree(unrooted_tree_file, species_tree_file, rename_map_file, output_tree_file):
    species_tree = Phylo.read(species_tree_file, 'newick')
    unrooted_gene_tree = Phylo.read(unrooted_tree_file, 'newick')
    unrooted_gene_tree = add_clade_name(unrooted_gene_tree)
    unrooted_gene_tree_node_dict = lookup_by_names(unrooted_gene_tree)

    rename_dict, gene_to_species_map_dict = read_rename_map_file(rename_map_file)

    best_root_clade = get_root_by_species(unrooted_gene_tree, species_tree, gene_to_species_map_dict)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(unrooted_gene_tree,
                                                                                                            unrooted_gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    for i in gene_tree_rooted_node_dict:
        c = gene_tree_rooted_node_dict[i]
        if not c.is_terminal():
            c.name = None

    Phylo.write(gene_tree_rooted, output_tree_file, format='newick')


def get_suborthogroups_from_one_tree_dir(tree_prefix, gene_tree_file, species_tree_file, gene_to_species_map_file, conserved_function, conserved_arguments, support_threshold, no_overlap=True):

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

    sp_in_tree = list(set([gene_to_species_map_dict[i.name]
                           for i in gene_tree.get_terminals()]))
    gene_in_tree = list(set([i.name for i in gene_tree.get_terminals()]))
    sp_list = list(set([i.name for i in species_tree.get_terminals()]))

    if conserved_function(sp_in_tree, conserved_arguments):

        OGs = get_orthogroups_from_tree(tree_prefix, gene_tree, species_tree,
                                        gene_to_species_map_dict, conserved_function, conserved_arguments, support_threshold)

        if no_overlap:
            OGs = get_non_overlap_orthogroups(OGs)

        OGs = OGs_gene_rename(OGs, rename_dict)

    else:
        OG_dict = {tree_prefix: {i: [] for i in sp_list}}
        for g_id in gene_in_tree:
            OG_dict[tree_prefix][gene_to_species_map_dict[g_id]].append(g_id)

        OGs = OrthoGroups(from_OG_dict=OG_dict, species_list=sp_list)
        OGs = OGs_gene_rename(OGs, rename_dict)

    return OGs


def get_orthogroups_from_fasttree_pipeline(OG_tsv_file, fasttree_dir, species_tree_file, conserved_function, conserved_arguments, support_threshold, threads=56, no_overlap=True):

    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)

    num = 0

    args_list = []

    for og_id in OGs.OG_id_list:
        num += 1

        og_dir = fasttree_dir + "/" + og_id
        gene_tree_file = og_dir + "/fasttree.phb"
        gene_to_species_map_file = og_dir + "/rename.map"
        args_list.append((og_id, gene_tree_file, species_tree_file, gene_to_species_map_file,
                          conserved_function, conserved_arguments, support_threshold, no_overlap))

    tmp_out = multiprocess_running(
        get_suborthogroups_from_one_tree_dir, args_list, threads, None, True, None)

    OGs_list = [tmp_out[i]['output'] for i in tmp_out]

    OGs = merge_OGs(OGs_list)

    return OGs


if __name__ == '__main__':

    # running fasttree pipeline

    ref_xlsx = '/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/seq_info.xlsx'
    sp_list = ["Osa", "Zma", "Acom", "Xvi",
               "Aco", "Ath", "Mdo", "Sly", "Pni", "Atr"]
    OG_tsv_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/pt_file/OrthoFinder/Results_May08/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree"

    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)

    species_info_dict = read_species_info(ref_xlsx)
    species_info_dict = {i: species_info_dict[i]
                         for i in species_info_dict if i in sp_list}

    fasttree_many(OGs, species_info_dict, fasttree_dir, 56)

    # get orthogroups
    OG_tsv_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/pt_file/OrthoFinder/Results_May08/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree"
    species_tree_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/species.txt"
    conserved_arguments = [
        [["Osa", "Zma", "Acom", "Xvi"], ["Aco", "Ath", "Mdo", "Sly"]], [2, 2]]
    support_threshold = 0.5
    no_overlap_OGs = get_orthogroups_from_fasttree_pipeline(
        OG_tsv_file, fasttree_dir, species_tree_file, if_conserved, conserved_arguments, support_threshold, threads=56, no_overlap=True)

    overlap_OGs = get_orthogroups_from_fasttree_pipeline(
        OG_tsv_file, fasttree_dir, species_tree_file, if_conserved, conserved_arguments, support_threshold, threads=56, no_overlap=False)

    # write
    no_overlap_OGs.write_OG_tsv_file(
        "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree/no_overlap_OGs.tsv")
    overlap_OGs.write_OG_tsv_file(
        "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree/overlap_OGs.tsv")
