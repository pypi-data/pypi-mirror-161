import os
from toolbiox.lib.common.os import mkdir, cmd_run, multiprocess_running
from toolbiox.lib.common.util import pickle_step
from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
from toolbiox.lib.common.evolution.tree_operate import Phylo, get_newick_string
from toolbiox.config import trimal_path
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx


def filter_og_by_copy_num(OGs, min_num, max_num):
    passed_og_list = []

    for og_id in OGs.OG_dict:
        og = OGs.OG_dict[og_id]
        pass_flag = True

        for sp_id in og.species_stat:
            if not (min_num <= og.species_stat[sp_id] <= max_num):
                pass_flag = False

        if pass_flag:
            passed_og_list.append(og_id)

    return passed_og_list


def load_seq(OGs, sp_info_dict):

    aa_dict = {}
    for sp_id in sp_info_dict:
        aa_dict[sp_id] = read_fasta_by_faidx(sp_info_dict[sp_id].pt_file)

    cds_dict = {}
    for sp_id in sp_info_dict:
        cds_dict[sp_id] = read_fasta_by_faidx(sp_info_dict[sp_id].cds_file)

    for og_id in OGs.OG_dict:
        #     print(og_id)
        og = OGs.OG_dict[og_id]
        for gene in og.gene_list:
            gene.model_aa_seq = aa_dict[gene.species][gene.id].seq
            gene.model_cds_seq = cds_dict[gene.species][gene.id].seq

    return OGs


def build_a_og(og, top_work_dir):

    og.work_dir = top_work_dir + "/" + og.id
    mkdir(og.work_dir, True)

    og.pt_fa = og.work_dir + "/pt.fa"
    og.cds_fa = og.work_dir + "/cds.fa"
    og.pt_aln = og.pt_fa + ".aln"
    og.pt_trim = og.pt_aln + ".trim"
    og.pt_trim_clean = og.pt_trim + ".clean"
    og.tree_file = og.pt_trim_clean + ".raxml.bestTree"

    if not os.path.exists(og.tree_file):

        # pt_file
        with open(og.pt_fa, 'w') as f:
            for sp_id in og.species_list:
                for gene in og.gene_dict[sp_id]:
                    pt_seq = gene.model_aa_seq
                    f.write(">%s\n%s\n" % (gene.id, pt_seq))

        # cds_file
        with open(og.cds_fa, 'w') as f:
            for sp_id in og.species_list:
                for gene in og.gene_dict[sp_id]:
                    pt_seq = gene.model_cds_seq
                    f.write(">%s\n%s\n" % (gene.id, pt_seq))

        # aln
        cmd_string = "clustalw2 -INFILE="+og.pt_fa + \
            " -ALIGN -OUTPUT=FASTA -OUTFILE="+og.pt_aln+" -type=protein"
        cmd_run(cmd_string, silence=True, cwd=og.work_dir)

        # trim
        og.pt_trim = og.pt_aln + ".trim"
        cmd_string = "%s -in %s -out %s -gt 0.1 >/dev/null" % (
            trimal_path, og.pt_aln, og.pt_trim)
        cmd_run(cmd_string, silence=True, cwd=og.work_dir)

        og.pt_trim_clean = og.pt_aln + ".trim.clean"
        with open(og.pt_trim_clean, 'w') as f:
            aln_dict = read_fasta_by_faidx(og.pt_trim)
            for i in aln_dict:
                f.write(">%s\n%s\n" % (i, aln_dict[i].seq))

        # tree
        cmd_string = "raxml-ng --msa %s --model LG+G4 --seed 12345 --threads 1" % og.pt_trim_clean
        cmd_run(cmd_string, silence=True)
        og.tree_file = og.pt_trim_clean + ".raxml.bestTree"

    return og


def build_trees(OGs, sp_info_dict, top_work_dir, threads):
    OGs = load_seq(OGs, sp_info_dict)

    mkdir(top_work_dir, True)

    args_list = []
    for og_id in OGs.OG_dict:
        args_list.append((OGs.OG_dict[og_id], top_work_dir))

    mlt_out = multiprocess_running(
        build_a_og, args_list, threads, silence=False)

    og_dict = {}
    for i in mlt_out:
        og = mlt_out[i]['output']
        og_dict[og.id] = og

    new_OGs = OrthoGroups(from_OG_dict=og_dict, species_list=OGs.species_list)

    return new_OGs


def get_species_tree_by_genome_pipeline(OGs, sp_info_dict, work_dir, threads, astral_jar_path, astral_jar_lib_path):

    # filter OGs
    for max_gene in range(1, 5):
        passed_og_id_list = filter_og_by_copy_num(OGs, 1, max_gene)
        if len(passed_og_id_list) > 500:
            break

    print(max_gene, len(passed_og_id_list))

    tree_OGs = OrthoGroups(from_OG_list=[
        OGs.OG_dict[i] for i in passed_og_id_list], species_list=OGs.species_list)

    # build tree
    OGs_with_tree_pyb_file = work_dir + "/OGs_with_tree.pyb"
    tree_OGs = pickle_step(
        build_trees, [tree_OGs, sp_info_dict, work_dir + "/trees", threads], OGs_with_tree_pyb_file)

    # write ASTRAL input
    astral_trees_file = work_dir + "/astral.trees"
    astral_seqmap_file = work_dir + "/astral.seqmap.txt"

    with open(astral_trees_file, 'w') as tree_f:
        with open(astral_seqmap_file, 'w') as map_f:
            for og_id in tree_OGs.OG_dict:
                og = tree_OGs.OG_dict[og_id]
                tree_file = og.tree_file
                tree = Phylo.read(tree_file, 'newick')
                tree_string = get_newick_string(tree).replace("\n", "")
                tree_f.write(tree_string + "\n")

                for g in og.gene_list:
                    map_f.write("%s\t%s\n" % (g.id, g.species))

    astral_output_file = work_dir + '/astral.output'
    cmd_string = "java -Djava.library.path=%s -jar %s -i %s -a %s -o %s" % (
        astral_jar_lib_path, astral_jar_path, astral_trees_file, astral_seqmap_file, astral_output_file)

    cmd_run(cmd_string, cwd=work_dir, silence=False)

    return astral_output_file


OG_tsv_file = "/lustre/home/xuyuxing/Work/PlantWGD/3.each_order/Fabales/1.orthofinder/pt_file/OrthoFinder/Results_Jul08/Orthogroups/Orthogroups.tsv"
species_info_xlsx = "/lustre/home/xuyuxing/Work/PlantWGD/1.prepare_data/species_info.xlsx"
work_dir = "/lustre/home/xuyuxing/Work/PlantWGD/3.each_order/Fabales/species.tree"
threads = 80
astral_jar_path = '/lustre/home/xuyuxing/Program/ASTRAL/A-pro-master/ASTRAL-MP/astral.1.1.6.jar'
astral_jar_lib_path = '/lustre/home/xuyuxing/Program/ASTRAL/A-pro-master/ASTRAL-MP/lib'

OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)
sp_info_dict = read_species_info(species_info_xlsx)
sp_info_dict = {i: sp_info_dict[i] for i in OGs.species_list}

astral_output_file = get_species_tree_pipeline(
    OGs, sp_info_dict, work_dir, threads, astral_jar_path, astral_jar_lib_path)
