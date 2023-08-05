import toolbiox.lib.common.os
from toolbiox.lib.common.evolution.tree_operate import add_clade_name, lookup_by_names, normal_tree_rela_coord, normal_tree_abs_coord, draw_tree, \
    draw_ascii, get_root_by_species, reroot_by_outgroup_clade
import pickle
from toolbiox.api.common.genome.blast import evalue_to_wvalue
import networkx as nx
from Bio import Phylo
import sys
import re
import toolbiox.lib.xuyuxing.evolution.tree_operate_ete3 as to
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
import os
from toolbiox.lib.common.genome.seq_base import read_fasta_big
from toolbiox.config import *
import toolbiox.lib.xuyuxing.base.base_function as bf
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')


def PtTree(in_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num, MSA_flag):
    if output_dir is None:
        output_dir = "phyout"

    output_tag_file = output_dir.split("/")[-1]

    lib.common.os.mkdir(output_dir, keep=True)
    output_tag = output_dir + "/" + output_tag_file

    # alignment
    aln_file = output_tag + ".aa.aln"
    cmd_string = "sed -i 's/*//g' %s" % (in_file)
    lib.common.os.cmd_run(cmd_string)
    if MSA_flag == "clustalo":
        cmd_string = clustalo_path + " -i %s -o %s -t Protein --force --auto --threads=%d" % (
            in_file, aln_file, cpu_num)
        lib.common.os.cmd_run(cmd_string)
    elif MSA_flag == "clustalw2":
        cmd_string = clustalw_path + " -INFILE=%s -ALIGN -OUTPUT=FASTA -OUTFILE=%s -type=protein" % (
            in_file, aln_file)
        lib.common.os.cmd_run(cmd_string)

    # trimAl
    if trimal_flag:
        used_aln = output_tag + ".trimal.aln"
        used_aln_for_raxml = output_tag_file + ".trimal.aln"
        cmd_string = trimal_path + \
            " -fasta -gappyout -in %s -out %s" % (aln_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    else:
        used_aln = aln_file
        used_aln_for_raxml = output_tag_file + ".aa.aln"

    # tree builder
    tree_file = output_tag + ".phb"
    tree_file_for_raxml = output_tag_file + ".phb"
    if phylogeneic_tree_builder == 'fasttree':
        cmd_string = fasttree_path + \
            " -wag -gamma -out %s %s" % (tree_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    elif phylogeneic_tree_builder == 'raxml':
        cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m PROTGAMMAJTT -s %s -n %s" % (
            cpu_num, used_aln_for_raxml, tree_file_for_raxml)
        cwd_string = output_dir
        lib.common.os.cmd_run(cmd_string, cwd_string)

    print("Finished")


def TrueNtTree(in_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num, MSA_flag):
    if output_dir is None:
        output_dir = "phyout"

    lib.common.os.mkdir(output_dir)
    output_tag = output_dir + "/" + output_dir

    # alignment
    aln_file = output_tag + ".nt.aln"

    if MSA_flag == "clustalo":
        cmd_string = clustalo_path + \
            " -i %s -o %s --force --auto --threads=%d" % (
                in_file, aln_file, cpu_num)
        lib.common.os.cmd_run(cmd_string)
    elif MSA_flag == "clustalw2":
        cmd_string = clustalw_path + " -INFILE=%s -ALIGN -OUTPUT=FASTA -OUTFILE=%s -type=DNA" % (
            in_file, aln_file)
        lib.common.os.cmd_run(cmd_string)

    # trimAl
    if trimal_flag:
        used_aln = output_tag + ".trimal.aln"
        used_aln_for_raxml = output_dir + ".trimal.aln"
        cmd_string = trimal_path + \
            " -fasta -gappyout -in %s -out %s" % (aln_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    else:
        used_aln = aln_file
        used_aln_for_raxml = output_dir + ".nt.aln"

    # tree builder
    tree_file = output_tag + ".phb"
    tree_file_for_raxml = output_dir + ".phb"
    if phylogeneic_tree_builder == 'fasttree':
        cmd_string = fasttree_path + \
            " -nt -gtr -gamma -out %s %s" % (tree_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    elif phylogeneic_tree_builder == 'raxml':
        cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m GTRGAMMA -s %s -n %s" % (
            cpu_num, used_aln_for_raxml, tree_file_for_raxml)
        cwd_string = os.getcwd() + "/" + output_dir
        lib.common.os.cmd_run(cmd_string, cwd_string)

    print("Finished")


def PtNtTree(nucl_file, pt_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num):
    if output_dir is None:
        output_dir = "phyout"

    lib.common.os.mkdir(output_dir)
    output_tag = output_dir + "/" + output_dir

    # alignment
    pt_aln_file = output_tag + ".aa.aln"
    cmd_string = "sed -i 's/*//g' %s" % (pt_file)
    lib.common.os.cmd_run(cmd_string)
    cmd_string = clustalo_path + " -i %s -o %s -t Protein --force --auto --threads=%d" % (
        pt_file, pt_aln_file, cpu_num)
    lib.common.os.cmd_run(cmd_string)

    # backtrans
    pt_aln_file = output_tag + ".aa.aln"
    nt_aln_file = output_tag + ".nt.aln"
    cmd_string = treebest_path + \
        " backtrans %s %s > %s" % (pt_aln_file, nucl_file, nt_aln_file)
    lib.common.os.cmd_run(cmd_string)

    # trimAl
    if trimal_flag:
        used_aln = output_tag + ".trimal.aln"
        used_aln_for_raxml = output_dir + ".trimal.aln"
        cmd_string = trimal_path + \
            " -fasta -gappyout -in %s -out %s" % (nt_aln_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    else:
        used_aln = nt_aln_file
        used_aln_for_raxml = output_dir + ".nt.aln"

    # tree builder
    tree_file = output_tag + ".phb"
    tree_file_for_raxml = output_dir + ".phb"
    if phylogeneic_tree_builder == 'fasttree':
        cmd_string = fasttree_path + \
            " -nt -gtr -gamma -out %s %s" % (tree_file, used_aln)
        lib.common.os.cmd_run(cmd_string)
    elif phylogeneic_tree_builder == 'raxml':
        cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m GTRGAMMA -s %s -n %s" % (
            cpu_num, used_aln_for_raxml, tree_file_for_raxml)
        cwd_string = os.getcwd() + "/" + output_dir
        lib.common.os.cmd_run(cmd_string, cwd_string)

    print("Finished")


def FullFamily(query, database, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num):
    # ToDO
    pass


def PartFamily(query, database, num_top, phylogeneic_tree_builder, trimal_flag, mcl_flag, makeblastdb_flag, output_tag,
               cpu_num):
    from functools import cmp_to_key
    if output_tag is None:
        output_tag = query
    output_tag = output_tag.split("/")[-1]
    output_dir = os.getcwd() + "/" + output_tag
    lib.common.os.mkdir(output_dir, keep=True)
    output_tag = output_dir + "/" + output_tag

    ##

    if makeblastdb_flag is True:
        for files in os.listdir(database):
            if not files.split(".")[-1] == "fasta":
                continue
            cmd_string = "makeblastdb -in %s -dbtype prot" % (
                database + "/" + files)
            lib.common.os.cmd_run(cmd_string)

    query_record = ""
    for files in os.listdir(database):
        if files.split(".")[-1] in ("phr", "pin", "psq"):
            continue
        for record in read_fasta_big(database + "/" + files):
            if record.seqname_short() == query:
                query_record = record
                break
        if query_record != "":
            break
    query_fa = output_tag + ".query.fa"
    with open(query_fa, "w") as f:
        f.write(">" + query_record.seqname_short() + "\n" + query_record.seqs)

    # blast
    blast_result = []
    for files in os.listdir(database):
        if files.split(".")[-1] in ("phr", "pin", "psq"):
            continue
        bls_out = output_tag + "_vs_" + files
        db_file = database + "/" + files
        cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d -max_target_seqs %d" % (
            query_fa, db_file, bls_out, cpu_num, num_top)
        lib.common.os.cmd_run(cmd_string)
        blast_result.append(bls_out)

    subject_id = []
    for bls_file in blast_result:
        subject_id.extend(list(tsv_file_parse(bls_file, key_col=2).keys()))
    subject_record = []
    for files in os.listdir(database):
        if files.split(".")[-1] in ("phr", "pin", "psq"):
            continue
        for record in read_fasta_big(database + "/" + files):
            if record.seqname_short() in subject_id:
                subject_record.append(record)
    subject_fa = output_tag + ".blast.subject.fa"
    with open(subject_fa, "w") as f:
        for record in subject_record:
            f.write(">" + record.seqname_short() + "\n" + record.seqs + "\n")

    # mcl cluster
    if mcl_flag is True:
        # all to all blast
        cmd_string = "makeblastdb -in %s -dbtype prot" % subject_fa
        lib.common.os.cmd_run(cmd_string)
        all_to_all_blast = output_tag + ".subject.all_to_all.bls"
        cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d" % (
            subject_fa, subject_fa, all_to_all_blast, cpu_num)
        lib.common.os.cmd_run(cmd_string)

        # mcl pre
        tsv_dict = tsv_file_parse(all_to_all_blast, fields="1,2,11")
        mcl_abc_file = output_tag + ".seq.abc"
        with open(mcl_abc_file, "w") as f:
            for a, b, c in [tsv_dict[i] for i in tsv_dict]:
                f.write(a + "\t" + b + "\t" + c + "\n")

        # mcl
        mcl_mci_file = output_tag + ".seq.mci"
        mcl_tab_file = output_tag + ".seq.tab"
        cmd_string = "mcxload -abc %s --stream-mirror --stream-neg-log10 -stream-tf 'ceil(200)' -o %s -write-tab %s" % (
            mcl_abc_file, mcl_mci_file, mcl_tab_file)
        lib.common.os.cmd_run(cmd_string)

        inflation = 1.5
        mcl_out_files = []
        mcl_out_group = {}
        while (inflation <= 6.0):
            mcl_output = "%s.%.1f.mcl.out" % (output_tag, inflation)
            cmd_string = "mcl %s -I %s -use-tab %s -o %s" % (
                mcl_mci_file, inflation, mcl_tab_file, mcl_output)
            lib.common.os.cmd_run(cmd_string)
            mcl_out_files.append(mcl_output)
            mcl_output_dir = tsv_file_parse(mcl_output)
            for group_id in mcl_output_dir:
                if query in mcl_output_dir[group_id]:
                    mcl_out_group[inflation] = mcl_output_dir[group_id]
            inflation = inflation + 0.5

        def cmp_tmp(x, y):
            x_speci_list = list(set([i.split("|")[0]
                                     for i in mcl_out_group[x]]))
            y_speci_list = list(set([i.split("|")[0]
                                     for i in mcl_out_group[y]]))

            if len(x_speci_list) > len(y_speci_list):
                return -1
            elif len(x_speci_list) < len(y_speci_list):
                return 1
            elif len(x_speci_list) == len(y_speci_list):
                if x > y:
                    return -1
                elif y > x:
                    return 1

        best_mcl = sorted(mcl_out_group, key=cmp_to_key(cmp_tmp))[0]
        best_mcl_list = mcl_out_group[best_mcl]

        mcl_cluster_fa = output_tag + ".mcl.fa"
        with open(mcl_cluster_fa, "w") as f:
            for record in subject_record:
                if record.seqname_short() in best_mcl_list:
                    f.write(">" + record.seqname_short() +
                            "\n" + record.seqs + "\n")

        tree_fa = mcl_cluster_fa
    else:
        tree_fa = subject_fa

    PtTree(tree_fa, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num)


def RootGeneTree(gene_tree, species_tree, gene_to_species_map_dict):
    gene_tree = add_clade_name(gene_tree)
    gene_tree_node_dict = lookup_by_names(gene_tree)

    best_root_clade = get_root_by_species(
        gene_tree, species_tree, gene_to_species_map_dict)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(gene_tree,
                                                                                                            gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    gene_tree_rooted_node_dict = lookup_by_names(gene_tree_rooted)

    for i in gene_tree_rooted_node_dict:
        clade = gene_tree_rooted_node_dict[i]
        if not clade.is_terminal():
            clade.name = None

    return gene_tree_rooted
