from Bio import Phylo
import sys
import re
import os
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

# import toolbiox.lib.base.base_function as bf
# from toolbiox.lib.config import *
# from toolbiox.lib.seq.seq_base import read_fasta_big
# import os
# from toolbiox.lib.file_parser.fileIO import tsv_file_parse
# import toolbiox.lib.evolution.tree_operate_ete3 as to
# import re
# import sys
# from Bio import Phylo
# import networkx as nx
# from toolbiox.lib.seq.blast import evalue_to_wvalue
# import pickle
# from toolbiox.lib.evolution.tree_operate import lookup_by_names, normal_tree_rela_coord, normal_tree_abs_coord, draw_tree, \
#     draw_ascii


# def PtTree(in_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num, MSA_flag):
#     if output_dir is None:
#         output_dir = "phyout"

#     output_tag_file = output_dir.split("/")[-1]

#     bf.mkdir(output_dir, keep=True)
#     output_tag = output_dir + "/" + output_tag_file

#     # alignment
#     aln_file = output_tag + ".aa.aln"
#     cmd_string = "sed -i 's/*//g' %s" % (in_file)
#     bf.cmd_run(cmd_string)
#     if MSA_flag == "clustalo":
#         cmd_string = clustalo_path + " -i %s -o %s -t Protein --force --auto --threads=%d" % (
#             in_file, aln_file, cpu_num)
#         bf.cmd_run(cmd_string)
#     elif MSA_flag == "clustalw2":
#         cmd_string = clustalw_path + " -INFILE=%s -ALIGN -OUTPUT=FASTA -OUTFILE=%s -type=protein" % (
#             in_file, aln_file)
#         bf.cmd_run(cmd_string)

#     # trimAl
#     if trimal_flag:
#         used_aln = output_tag + ".trimal.aln"
#         used_aln_for_raxml = output_tag_file + ".trimal.aln"
#         cmd_string = trimal_path + " -fasta -gappyout -in %s -out %s" % (aln_file, used_aln)
#         bf.cmd_run(cmd_string)
#     else:
#         used_aln = aln_file
#         used_aln_for_raxml = output_tag_file + ".aa.aln"

#     # tree builder
#     tree_file = output_tag + ".phb"
#     tree_file_for_raxml = output_tag_file + ".phb"
#     if phylogeneic_tree_builder == 'fasttree':
#         cmd_string = fasttree_path + " -wag -gamma -out %s %s" % (tree_file, used_aln)
#         bf.cmd_run(cmd_string)
#     elif phylogeneic_tree_builder == 'raxml':
#         cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m PROTGAMMAJTT -s %s -n %s" % (
#             cpu_num, used_aln_for_raxml, tree_file_for_raxml)
#         cwd_string = output_dir
#         bf.cmd_run(cmd_string, cwd_string)

#     print("Finished")


# def TrueNtTree(in_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num, MSA_flag):
#     if output_dir is None:
#         output_dir = "phyout"

#     bf.mkdir(output_dir)
#     output_tag = output_dir + "/" + output_dir

#     # alignment
#     aln_file = output_tag + ".nt.aln"

#     if MSA_flag == "clustalo":
#         cmd_string = clustalo_path + " -i %s -o %s --force --auto --threads=%d" % (in_file, aln_file, cpu_num)
#         bf.cmd_run(cmd_string)
#     elif MSA_flag == "clustalw2":
#         cmd_string = clustalw_path + " -INFILE=%s -ALIGN -OUTPUT=FASTA -OUTFILE=%s -type=DNA" % (
#             in_file, aln_file)
#         bf.cmd_run(cmd_string)

#     # trimAl
#     if trimal_flag:
#         used_aln = output_tag + ".trimal.aln"
#         used_aln_for_raxml = output_dir + ".trimal.aln"
#         cmd_string = trimal_path + " -fasta -gappyout -in %s -out %s" % (aln_file, used_aln)
#         bf.cmd_run(cmd_string)
#     else:
#         used_aln = aln_file
#         used_aln_for_raxml = output_dir + ".nt.aln"

#     # tree builder
#     tree_file = output_tag + ".phb"
#     tree_file_for_raxml = output_dir + ".phb"
#     if phylogeneic_tree_builder == 'fasttree':
#         cmd_string = fasttree_path + " -nt -gtr -gamma -out %s %s" % (tree_file, used_aln)
#         bf.cmd_run(cmd_string)
#     elif phylogeneic_tree_builder == 'raxml':
#         cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m GTRGAMMA -s %s -n %s" % (
#             cpu_num, used_aln_for_raxml, tree_file_for_raxml)
#         cwd_string = os.getcwd() + "/" + output_dir
#         bf.cmd_run(cmd_string, cwd_string)

#     print("Finished")


# def PtNtTree(nucl_file, pt_file, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num):
#     if output_dir is None:
#         output_dir = "phyout"

#     bf.mkdir(output_dir)
#     output_tag = output_dir + "/" + output_dir

#     # alignment
#     pt_aln_file = output_tag + ".aa.aln"
#     cmd_string = "sed -i 's/*//g' %s" % (pt_file)
#     bf.cmd_run(cmd_string)
#     cmd_string = clustalo_path + " -i %s -o %s -t Protein --force --auto --threads=%d" % (
#         pt_file, pt_aln_file, cpu_num)
#     bf.cmd_run(cmd_string)

#     # backtrans
#     pt_aln_file = output_tag + ".aa.aln"
#     nt_aln_file = output_tag + ".nt.aln"
#     cmd_string = treebest_path + " backtrans %s %s > %s" % (pt_aln_file, nucl_file, nt_aln_file)
#     bf.cmd_run(cmd_string)

#     # trimAl
#     if trimal_flag:
#         used_aln = output_tag + ".trimal.aln"
#         used_aln_for_raxml = output_dir + ".trimal.aln"
#         cmd_string = trimal_path + " -fasta -gappyout -in %s -out %s" % (nt_aln_file, used_aln)
#         bf.cmd_run(cmd_string)
#     else:
#         used_aln = nt_aln_file
#         used_aln_for_raxml = output_dir + ".nt.aln"

#     # tree builder
#     tree_file = output_tag + ".phb"
#     tree_file_for_raxml = output_dir + ".phb"
#     if phylogeneic_tree_builder == 'fasttree':
#         cmd_string = fasttree_path + " -nt -gtr -gamma -out %s %s" % (tree_file, used_aln)
#         bf.cmd_run(cmd_string)
#     elif phylogeneic_tree_builder == 'raxml':
#         cmd_string = raxml_path + " -T %d -f a -x 12345 -p 12345 -# 100 -m GTRGAMMA -s %s -n %s" % (
#             cpu_num, used_aln_for_raxml, tree_file_for_raxml)
#         cwd_string = os.getcwd() + "/" + output_dir
#         bf.cmd_run(cmd_string, cwd_string)

#     print("Finished")


# def FullFamily(query, database, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num):
#     # ToDO
#     pass


# def PartFamily(query, database, num_top, phylogeneic_tree_builder, trimal_flag, mcl_flag, makeblastdb_flag, output_tag,
#                cpu_num):
#     from functools import cmp_to_key
#     if output_tag is None:
#         output_tag = query
#     output_tag = output_tag.split("/")[-1]
#     output_dir = os.getcwd() + "/" + output_tag
#     bf.mkdir(output_dir, keep=True)
#     output_tag = output_dir + "/" + output_tag

#     ##

#     if makeblastdb_flag is True:
#         for files in os.listdir(database):
#             if not files.split(".")[-1] == "fasta":
#                 continue
#             cmd_string = "makeblastdb -in %s -dbtype prot" % (database + "/" + files)
#             bf.cmd_run(cmd_string)

#     query_record = ""
#     for files in os.listdir(database):
#         if files.split(".")[-1] in ("phr", "pin", "psq"):
#             continue
#         for record in read_fasta_big(database + "/" + files):
#             if record.seqname_short() == query:
#                 query_record = record
#                 break
#         if query_record != "":
#             break
#     query_fa = output_tag + ".query.fa"
#     with open(query_fa, "w") as f:
#         f.write(">" + query_record.seqname_short() + "\n" + query_record.seqs)

#     # blast
#     blast_result = []
#     for files in os.listdir(database):
#         if files.split(".")[-1] in ("phr", "pin", "psq"):
#             continue
#         bls_out = output_tag + "_vs_" + files
#         db_file = database + "/" + files
#         cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d -max_target_seqs %d" % (
#             query_fa, db_file, bls_out, cpu_num, num_top)
#         bf.cmd_run(cmd_string)
#         blast_result.append(bls_out)

#     subject_id = []
#     for bls_file in blast_result:
#         subject_id.extend(list(tsv_file_parse(bls_file, key_col=2).keys()))
#     subject_record = []
#     for files in os.listdir(database):
#         if files.split(".")[-1] in ("phr", "pin", "psq"):
#             continue
#         for record in read_fasta_big(database + "/" + files):
#             if record.seqname_short() in subject_id:
#                 subject_record.append(record)
#     subject_fa = output_tag + ".blast.subject.fa"
#     with open(subject_fa, "w") as f:
#         for record in subject_record:
#             f.write(">" + record.seqname_short() + "\n" + record.seqs + "\n")

#     # mcl cluster
#     if mcl_flag is True:
#         # all to all blast
#         cmd_string = "makeblastdb -in %s -dbtype prot" % subject_fa
#         bf.cmd_run(cmd_string)
#         all_to_all_blast = output_tag + ".subject.all_to_all.bls"
#         cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d" % (
#             subject_fa, subject_fa, all_to_all_blast, cpu_num)
#         bf.cmd_run(cmd_string)

#         # mcl pre
#         tsv_dict = tsv_file_parse(all_to_all_blast, fields="1,2,11")
#         mcl_abc_file = output_tag + ".seq.abc"
#         with open(mcl_abc_file, "w") as f:
#             for a, b, c in [tsv_dict[i] for i in tsv_dict]:
#                 f.write(a + "\t" + b + "\t" + c + "\n")

#         # mcl
#         mcl_mci_file = output_tag + ".seq.mci"
#         mcl_tab_file = output_tag + ".seq.tab"
#         cmd_string = "mcxload -abc %s --stream-mirror --stream-neg-log10 -stream-tf 'ceil(200)' -o %s -write-tab %s" % (
#             mcl_abc_file, mcl_mci_file, mcl_tab_file)
#         bf.cmd_run(cmd_string)

#         inflation = 1.5
#         mcl_out_files = []
#         mcl_out_group = {}
#         while (inflation <= 6.0):
#             mcl_output = "%s.%.1f.mcl.out" % (output_tag, inflation)
#             cmd_string = "mcl %s -I %s -use-tab %s -o %s" % (mcl_mci_file, inflation, mcl_tab_file, mcl_output)
#             bf.cmd_run(cmd_string)
#             mcl_out_files.append(mcl_output)
#             mcl_output_dir = tsv_file_parse(mcl_output)
#             for group_id in mcl_output_dir:
#                 if query in mcl_output_dir[group_id]:
#                     mcl_out_group[inflation] = mcl_output_dir[group_id]
#             inflation = inflation + 0.5

#         def cmp_tmp(x, y):
#             x_speci_list = list(set([i.split("|")[0] for i in mcl_out_group[x]]))
#             y_speci_list = list(set([i.split("|")[0] for i in mcl_out_group[y]]))

#             if len(x_speci_list) > len(y_speci_list):
#                 return -1
#             elif len(x_speci_list) < len(y_speci_list):
#                 return 1
#             elif len(x_speci_list) == len(y_speci_list):
#                 if x > y:
#                     return -1
#                 elif y > x:
#                     return 1

#         best_mcl = sorted(mcl_out_group, key=cmp_to_key(cmp_tmp))[0]
#         best_mcl_list = mcl_out_group[best_mcl]

#         mcl_cluster_fa = output_tag + ".mcl.fa"
#         with open(mcl_cluster_fa, "w") as f:
#             for record in subject_record:
#                 if record.seqname_short() in best_mcl_list:
#                     f.write(">" + record.seqname_short() + "\n" + record.seqs + "\n")

#         tree_fa = mcl_cluster_fa
#     else:
#         tree_fa = subject_fa

#     PtTree(tree_fa, phylogeneic_tree_builder, trimal_flag, output_dir, cpu_num)


if __name__ == '__main__':

    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='PhylTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for PtTree
    parser_a = subparsers.add_parser('PtTree',
                                     help='build a protein gene tree from raw sequence',
                                     description='build a protein gene tree from raw sequence')

    parser_a.add_argument('protein_fasta', type=str,
                          help='Path of raw protein sequences')
    parser_a.add_argument("-p", "--phylogeneic_tree_builder", help="what tree builder you want? (default:fasttree)",
                          default="fasttree", choices=['raxml', 'fasttree'])
    parser_a.add_argument("-c", "--MSA", help="what multiple sequence alignment you want? (default:clustalo)",
                          default="clustalo", choices=['clustalo', 'clustalw2'])
    parser_a.add_argument(
        "-t", "--trimal", help="use trimal to trim alignment", action='store_true')
    parser_a.add_argument(
        "-T", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-o", "--output_dir", help="the dir name for all output file (default:phyout)", default=None,
                          type=str)

    # argparse for TrueNtTree
    parser_a = subparsers.add_parser('TrueNtTree',
                                     help='build a nucl gene tree from raw sequence',
                                     description='just need nucl information')

    parser_a.add_argument('nucl_fasta', type=str,
                          help='Path of raw nucl sequences')
    parser_a.add_argument("-p", "--phylogeneic_tree_builder", help="what tree builder you want? (default:fasttree)",
                          default="fasttree", choices=['raxml', 'fasttree'])
    parser_a.add_argument("-c", "--MSA", help="what multiple sequence alignment you want? (default:clustalo)",
                          default="clustalo", choices=['clustalo', 'clustalw2'])
    parser_a.add_argument(
        "-t", "--trimal", help="use trimal to trim alignment", action='store_true')
    parser_a.add_argument(
        "-T", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-o", "--output_dir", help="the dir name for all output file (default:phyout)", default=None,
                          type=str)

    # argparse for PtNtTree
    parser_a = subparsers.add_parser('PtNtTree',
                                     help='build a coden gene tree from nt aligned sequence based on protein alignment',
                                     description='need nucl and protein information')

    parser_a.add_argument('nucl_fasta', type=str,
                          help='Path of raw nucl sequences')
    parser_a.add_argument('protein_fasta', type=str,
                          help='Path of raw protein sequences')
    parser_a.add_argument("-p", "--phylogeneic_tree_builder", help="what tree builder you want? (default:fasttree)",
                          default="fasttree", choices=['raxml', 'fasttree'])
    parser_a.add_argument(
        "-t", "--trimal", help="use trimal to trim alignment", action='store_true')
    parser_a.add_argument(
        "-T", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-o", "--output_dir", help="the dir name for all output file (default:phyout)", default=None,
                          type=str)

    # argparse for Print
    parser_a = subparsers.add_parser('Print',
                                     help='print a tree by Ascii on screen',
                                     description='print a tree by Ascii on screen')

    parser_a.add_argument('tree_file', type=str,
                          help='tree file with newick format')
    parser_a.add_argument(
        "-o", "--output_file", help="output file (default:stdout)", default=None, type=str)
    parser_a.add_argument(
        "-t", "--target_list", help="leaf in target list will be highlighted", default="", type=str)
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:newick)",
                          default="newick", choices=['newick', 'phyloxml'])

    # argparse for SubTree
    parser_a = subparsers.add_parser('SubTree',
                                     help='cut a sub tree from a big tree by MRCA of two leaves',
                                     description='cut a sub tree from a big tree')

    parser_a.add_argument('tree_file', type=str,
                          help='tree file with newick format')
    parser_a.add_argument('leaf1', type=str, help='leaf 1')
    parser_a.add_argument('leaf2', type=str, help='leaf 2')
    parser_a.add_argument(
        "-r", "--root", help="re-root tree by this leaf", type=str)
    parser_a.add_argument("-o", "--output_file", help="output file", type=str)
    parser_a.add_argument(
        "-n", "--name_flag", help="output the name list of subtree", action='store_true')

    # argparse for Newick2PhyloXML
    parser_a = subparsers.add_parser('Newick2PhyloXML',
                                     help='change Newick file to PhyloXML')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')

    # argparse for RenameNodeID
    parser_a = subparsers.add_parser('RenameNodeID',
                                     help='Rename node on a tree')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument('ID_map_file', type=str,
                          help='file with ID in first column and new ID in a second column')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="newick", choices=['newick', 'phyloxml'])

    # argparse for AddNodeID
    parser_a = subparsers.add_parser('AddNodeID',
                                     help='Add ordered ID for node in the tree')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="phyloxml", choices=['newick', 'phyloxml'])

    # argparse for ClearNodeID
    parser_a = subparsers.add_parser('ClearNodeID',
                                     help='clear ID for nodes in the tree')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="phyloxml", choices=['newick', 'phyloxml'])

    # argparse for ClearConfidence
    parser_a = subparsers.add_parser('ClearConfidence',
                                     help='clear confidence for nodes in the tree')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="phyloxml", choices=['newick', 'phyloxml'])

    # argparse for ClearComment
    parser_a = subparsers.add_parser('ClearComment',
                                     help='clear comment for nodes in the tree')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="phyloxml", choices=['newick', 'phyloxml'])

    # argparse for RootTree
    parser_a = subparsers.add_parser('RootTree',
                                     help='Root a Tree with outgroup or at midpoint')

    parser_a.add_argument('input_tree', type=str, help='path for input tree')
    parser_a.add_argument('output_tree', type=str, help='path for output tree')
    parser_a.add_argument('-n', '--node_name', type=str,
                          help='node name for reroot, default is root at midpoint')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:phyloxml)",
                          default="phyloxml", choices=['newick', 'phyloxml'])

    # argparse for RootTreeBySpecies
    parser_a = subparsers.add_parser('RootTreeBySpecies',
                                     help='Root a Gene Tree by species tree')

    parser_a.add_argument(
        "gene_tree", help="input gene tree in newick", type=str)
    parser_a.add_argument(
        "species_tree", help="species tree in newick", type=str)
    parser_a.add_argument(
        "gene_to_species_map", help="gene name to species map file in tsv file, gene id in first col, species id in second", type=str)
    parser_a.add_argument("-o", "--output_tree",
                          help="output tree name", type=str, default="gene_rooted.phb")

    # argparse for MonophylyTest
    parser_a = subparsers.add_parser('MonophylyTest',
                                     help='use Bootstrap tree to support a list leaves is monophyly or not')

    parser_a.add_argument('gene_list_file', type=str,
                          help='path for gene list file')
    parser_a.add_argument('Bootstrap_trees', type=str,
                          help='path for file which have many bootstrap trees')
    parser_a.add_argument("-f", "--file_format", help="tree file format (default:newick)",
                          default="newick", choices=['newick', 'phyloxml'])
    parser_a.add_argument(
        "-o", "--output_file", help="output file (default:stdout)", default=None, type=str)

    # argparse for FullFamily
    parser_a = subparsers.add_parser('FullFamily',
                                     help='build a full family gene tree by hmm searching for a database',
                                     description='build a full family gene tree by hmm search a database')

    parser_a.add_argument(
        'query', type=str, help='query sequences file in fasta format')
    parser_a.add_argument('database', type=str,
                          help='all sequences file in fasta format')
    parser_a.add_argument(
        "-t", "--trimal", help="use trimal to trim alignment", action='store_true')
    parser_a.add_argument(
        "-T", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-p", "--phylogeneic_tree_builder", help="what tree builder you want? (default:fasttree)",
                          default="fasttree", choices=['raxml', 'fasttree'])
    parser_a.add_argument("-o", "--output_prefix",
                          help="prefix for all output", default="phyout", type=str)

    # argparse for PartFamily
    parser_a = subparsers.add_parser('PartFamily',
                                     help='build a Part family gene tree by top blast searching for a every species',
                                     description='build a Part family gene tree by top blast searching for a every species')

    parser_a.add_argument('query', type=str, help='query id')
    parser_a.add_argument('database', type=str,
                          help='a dir in which each species sequence is placed in a separate file')
    parser_a.add_argument("-n", "--num_top", help="num of top gene from each species (default:20)", default=20,
                          type=int)
    parser_a.add_argument(
        "-t", "--trimal", help="use trimal to trim alignment", action='store_true')
    parser_a.add_argument(
        "-m", "--mcl", help="use mcl to cluster subject from blast", action='store_true')
    parser_a.add_argument("-b", "--blast_db_maker", help="makeblastdb for fasta file, only need in first run",
                          action='store_true')
    parser_a.add_argument(
        "-T", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-p", "--phylogeneic_tree_builder", help="what tree builder you want? (default:fasttree)",
                          default="fasttree", choices=['raxml', 'fasttree'])
    parser_a.add_argument("-o", "--output_prefix",
                          help="prefix for all output", default="phyout", type=str)

    # argparse for OrthofinderParser
    parser_a = subparsers.add_parser('OrthofinderParser',
                                     help='parser orthofinder recon tree for orthology')

    parser_a.add_argument('recon_tree', type=str,
                          help='path for recon tree build by orthofinder')
    parser_a.add_argument('speci_tree', type=str,
                          help='path for species tree build by orthofinder (SpeciesTree_rooted_node_labels.txt)')
    parser_a.add_argument('base_speci_tab', type=str,
                          help='tab of species which you want to be base species for orthology find')
    parser_a.add_argument("-o", "--output_prefix",
                          help="prefix for all output", default="phyout", type=str)

    # argparse for mcl
    parser_a = subparsers.add_parser('mcl',
                                     help='make mcl for a fasta file')

    parser_a.add_argument('input_fasta', type=str,
                          help='path for input fasta file')
    parser_a.add_argument('output_prefix', type=str,
                          help='prefix for output')
    parser_a.add_argument("-t", "--cpu_num", type=int,
                          help='cpu num', default=5)
    parser_a.add_argument("-bls", "--blast_output",
                          help="give a output of all 2 all blast for skip blast", type=str)

    # argparse for WvalueGroup
    parser_a = subparsers.add_parser('WvalueGroup',
                                     help='')

    parser_a.add_argument('all_2_all_blast_results', type=str,
                          help='path for input blast results outfmt 6')
    parser_a.add_argument('node_group_output_file',
                          type=str, help='prefix for output')
    parser_a.add_argument("-t", "--threshold", type=int,
                          help='group threshold', default=100)

    # argparse for blastEtoW
    parser_a = subparsers.add_parser('blastEtoW',
                                     help='')

    parser_a.add_argument('a2a_blast', type=str,
                          help='path for input blast results outfmt 6')
    parser_a.add_argument('w_value_file', type=str, help='output file')

    # argparse for EasyABSREL
    parser_a = subparsers.add_parser('EasyABSREL',
                                     help='run ABSREL quickly')

    parser_a.add_argument('cds_aln_fasta', type=str,
                          help='path for input cds aln fasta')
    parser_a.add_argument('rooted_gene_tree', type=str,
                          help='path for rooted gene tree')
    parser_a.add_argument('-o', '--output_prefix', type=str,
                          help='path for output', default='ABSREL')
    parser_a.add_argument('-t', '--threads', type=int,
                          help='CPU for ABSREL', default=8)
    parser_a.add_argument('-f', '--tree_format', type=str,
                          help='tree format', default='newick')

    # argparse for EasyRELAX
    parser_a = subparsers.add_parser('EasyRELAX',
                                     help='run RELAX quickly')

    parser_a.add_argument('cds_aln_fasta', type=str,
                          help='path for input cds aln fasta')
    parser_a.add_argument('rooted_gene_tree', type=str,
                          help='path for rooted gene tree')
    parser_a.add_argument('output_dir', type=str,
                          help='path for output_dir')
    parser_a.add_argument('-n', '--test_node', type=str, default="",
                          help='test node list "N1,N2,N3"')
    parser_a.add_argument('-f', '--tree_format', type=str, default="newick",
                          help='tree file format')
    parser_a.add_argument('-t', '--threads', type=int, default=8,
                          help='num of threads')

    # argparse for parserSSN
    parser_a = subparsers.add_parser('parserSSN',
                                     help='parse blast results to Sequence similarity network')

    parser_a.add_argument('a2a_blast', type=str,
                          help='path for input blast results outfmt 6')
    parser_a.add_argument('graph_pyb_file', type=str, help='graph file output')
    parser_a.add_argument("graph_pos_file", type=str, help='pos file output')

    # argparse for SSNplot
    parser_a = subparsers.add_parser('SSNplot',
                                     help='parse blast results to Sequence similarity network')

    parser_a.add_argument('graph_pyb_file', type=str, help='graph file')
    parser_a.add_argument('graph_pos_file', type=str, help='pos file')
    parser_a.add_argument("plot_file", type=str, help='plot pdf')

    # argparse for BlastTo1KP
    parser_a = subparsers.add_parser('BlastTo1KP',
                                     help='parse blast results from a genome to 1kp')

    parser_a.add_argument('blast_result', type=str,
                          help='path for blast_result')
    parser_a.add_argument('taxon_dir', type=str, help='path for taxon_dir')
    parser_a.add_argument("acc_taxon_map", type=str,
                          help='path for acc_taxon_map')

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    if args_dict["subcommand_name"] == "PtTree":
        from toolbiox.src.xuyuxing.tools.phytools import PtTree

        in_file = args.protein_fasta
        phylogeneic_tree_builder = args.phylogeneic_tree_builder
        trimal_flag = args.trimal
        output_dir = args.output_dir
        cpu_num = args.num_threads
        MSA = args.MSA

        PtTree(in_file, phylogeneic_tree_builder,
               trimal_flag, output_dir, cpu_num, MSA)

    elif args_dict["subcommand_name"] == "TrueNtTree":
        from toolbiox.src.xuyuxing.tools.phytools import TrueNtTree

        in_file = args.nucl_fasta
        phylogeneic_tree_builder = args.phylogeneic_tree_builder
        trimal_flag = args.trimal
        output_dir = args.output_dir
        cpu_num = args.num_threads
        MSA = args.MSA

        TrueNtTree(in_file, phylogeneic_tree_builder,
                   trimal_flag, output_dir, cpu_num, MSA)

    elif args_dict["subcommand_name"] == "PtNtTree":
        from toolbiox.src.xuyuxing.tools.phytools import PtNtTree

        nucl_file = args.nucl_fasta
        pt_file = args.protein_fasta
        phylogeneic_tree_builder = args.phylogeneic_tree_builder
        trimal_flag = args.trimal
        output_dir = args.output_dir
        cpu_num = args.num_threads

        PtNtTree(nucl_file, pt_file, phylogeneic_tree_builder,
                 trimal_flag, output_dir, cpu_num)

    elif args_dict["subcommand_name"] == "Print":
        from toolbiox.lib.common.evolution.tree_operate import draw_ascii

        tree = Phylo.read(args.tree_file, args.file_format)

        draw_ascii(tree, args.output_file, clade_name=True)

        # tree_file = args.tree_file
        # target_list = args.target_list
        # target_list = target_list.split(",")
        #
        # t = Tree(tree_file)
        # # tree_string = t.get_ascii(show_internal=True, attributes=["name", "dist", "label", "support"])
        # tree_string = t.get_ascii(show_internal=True, attributes=["name", "support"])
        #
        # target_list = list(set(target_list))
        # for target in target_list:
        #     tree_string = tree_string.replace(target, "\033[0;31m" + target + "\033[0m")
        #
        # print(tree_string)

    elif args_dict["subcommand_name"] == "SubTree":
        import toolbiox.lib.xuyuxing.evolution.tree_operate_ete3 as to

        """
            tree_file = '/lustre/home/xuyuxing/Work/Cuscuta_HGT/123/HGT_case/case_001/genblastG/mcl/Cauv1.1_5.blast/Cauv1.1_5.blast.taxon.phb'
            leaf1 = '4039_0'
            leaf2 = '35608_14'
            root_node = None
            """

        tree_file = args.tree_file
        leaf1 = args.leaf1
        leaf2 = args.leaf2
        root_node = args.root
        output_file = args.output_file
        name_flag = args.name_flag

        subnode = to.subtree(tree_file, leaf1, leaf2, root_node)
        if name_flag:
            if output_file is not None:
                F1 = open(output_file, 'w')

            for i in subnode.get_leaf_names():
                if output_file is not None:
                    F1.write(i + "\n")
                else:
                    print(i)

            if output_file is not None:
                F1.close()

        else:
            if output_file is not None:
                with open(output_file, 'w') as f:
                    f.write(subnode.write())
            else:
                print(subnode)

    elif args_dict["subcommand_name"] == "FullFamily":
        # ToDo
        pass

    elif args_dict["subcommand_name"] == "PartFamily":
        from toolbiox.src.xuyuxing.tools.phytools import PartFamily

        query = args.query
        database = args.database
        num_top = args.num_top
        phylogeneic_tree_builder = args.phylogeneic_tree_builder
        trimal_flag = args.trimal
        mcl_flag = args.mcl
        makeblastdb_flag = args.blast_db_maker
        output_tag = args.output_prefix
        cpu_num = args.num_threads

        PartFamily(query, database, num_top, phylogeneic_tree_builder, trimal_flag, mcl_flag, makeblastdb_flag,
                   output_tag, cpu_num)

    elif args_dict["subcommand_name"] == "OrthofinderParser":
        """
        class abc(object):
            pass

        args = abc()

        args.recon_tree = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/Orthologues_Apr11/Recon_Gene_Trees/OG0000001_tree.txt'
        args.speci_tree = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/Orthologues_Apr11/SpeciesTree_rooted_node_labels.txt'
        args.base_speci_tab = 'Ini'
        args.output_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/Orthologues/tmp.out'
        """
        from ete3 import Tree

        def read_orthofinder_lab_tree(tree_file):
            with open(tree_file, "r") as myfile:
                data = myfile.read()
                tree_string = re.sub('\)n0;$', ');', data)
                tree_string = re.sub('\)N0;$', ');', tree_string)
                t = Tree(tree_string, format=3)
            return t

        t_r = read_orthofinder_lab_tree(args.recon_tree)
        t_s = read_orthofinder_lab_tree(args.speci_tree)

    elif args_dict["subcommand_name"] == "mcl":
        """
        class abc(object):
            pass

        args = abc()

        args.input_fasta = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/sj90'
        args.output_prefix = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/sj90_mcl'
        args.cpu_num=5
        args.blast_output = None
        """
        from toolbiox.lib.common.os import cmd_run

        work_dir = os.path.dirname(args.input_fasta)

        # mcl cluster
        # all to all blast
        if args.blast_output is None:
            cmd_string = "makeblastdb -in %s -dbtype prot" % args.input_fasta
            cmd_run(cmd_string)
            all_to_all_blast = args.input_fasta + ".all_to_all.bls"
            cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d" % (
                args.input_fasta, args.input_fasta, all_to_all_blast, args.cpu_num)
            cmd_run(cmd_string)
        else:
            all_to_all_blast = args.blast_output

        # mcl pre
        mcl_abc_file = args.output_prefix + ".seq.abc"
        with open(all_to_all_blast, 'r') as r:
            with open(mcl_abc_file, "w") as f:
                for each_line in r:
                    if re.match(r'^#', each_line):
                        continue
                    each_line = re.sub('\n', '', each_line)
                    info = each_line.split("\t")
                    a, b, c = info[0], info[1], info[10]
                    f.write(a + "\t" + b + "\t" + c + "\n")

        # mcl
        mcl_mci_file = args.output_prefix + ".seq.mci"
        mcl_tab_file = args.output_prefix + ".seq.tab"
        cmd_string = "mcxload -abc %s --stream-mirror --stream-neg-log10 -stream-tf 'ceil(200)' -o %s -write-tab %s" % (
            mcl_abc_file, mcl_mci_file, mcl_tab_file)
        cmd_run(cmd_string)

        inflation = 1.5
        mcl_out_files = []
        mcl_out_group = {}
        while (inflation <= 6.0):
            mcl_output = "%s.%.1f.mcl.out" % (args.output_prefix, inflation)
            cmd_string = "mcl %s -I %s -use-tab %s -o %s" % (
                mcl_mci_file, inflation, mcl_tab_file, mcl_output)
            cmd_run(cmd_string)
            inflation = inflation + 0.5

    elif args_dict["subcommand_name"] == "WvalueGroup":
        """
        class abc(object):
            pass

        args = abc()

        args.all_2_all_blast_results = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/tmp/sj90_a2a.bls'
        args.node_group_output_file = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/tmp/sj90_a2a.node_group.tsv' 
        args.threshold = 80
        """

        # group seq to node (by a thre)
        import networkx as nx
        from toolbiox.api.common.genome.blast import evalue_to_wvalue

        G = nx.Graph()

        with open(args.all_2_all_blast_results, 'r') as r:
            num = 0
            for each_line in r:
                num = num + 1
                if re.match(r'^#', each_line):
                    continue
                each_line = re.sub('\n', '', each_line)
                info = each_line.split("\t")
                seq1, seq2, evalue = info[0], info[1], info[10]
                wvalue = evalue_to_wvalue(float(evalue))
                G.add_nodes_from([seq1, seq2])
                if wvalue >= args.threshold:
                    G.add_edge(seq1, seq2)
                if num % 1000000 == 0:
                    print("added %s records to graph" % num)
                    tmp_G = nx.Graph()
                    tmp_G.add_nodes_from(list(G.node))
                    for sub_graph in (G.subgraph(c) for c in nx.connected_components(G)):
                        nodes_in_sub_graph = list(sub_graph.node)
                        tmp_G.add_edges_from([(nodes_in_sub_graph[i], nodes_in_sub_graph[i + 1]) for i in
                                              range(0, len(nodes_in_sub_graph) - 1)])
                    G = tmp_G

        num = 0
        with open(args.node_group_output_file, 'w') as f:
            for sub_graph in (G.subgraph(c) for c in nx.connected_components(G)):
                num = num + 1
                for node in sub_graph.node:
                    f.write("%d\t%s\n" % (num, node))

    elif args_dict["subcommand_name"] == "blastEtoW":
        """
        class abc(object):
            pass

        args = abc()

        args.a2a_blast = '/Users/yuxingxu/Job/Work/FKN/all.tmp.bls'
        args.w_value_file = '/Users/yuxingxu/Job/Work/FKN/graph.py'
        """

        import matplotlib.pyplot as plt
        import networkx as nx
        import re
        import pickle

        G = nx.Graph()

        with open(args.a2a_blast, 'r') as r:
            num = 0
            for each_line in r:
                num = num + 1
                if re.match(r'^#', each_line):
                    continue
                each_line = re.sub('\n', '', each_line)
                info = each_line.split("\t")
                seq1, seq2, evalue = info[0], info[1], info[10]
                wvalue = evalue_to_wvalue(float(evalue))
                G.add_nodes_from([seq1, seq2])
                G.add_weighted_edges_from([(seq1, seq2, wvalue)])

        with open(args.w_value_file, 'w') as w:
            for edge_node_pair in G.edges:
                wvalue = G.edges[edge_node_pair]['weight']
                w.write("%s\t%s\t%d\n" %
                        (edge_node_pair[0], edge_node_pair[1], wvalue))

    elif args_dict["subcommand_name"] == "parserSSN":
        """
        class abc(object):
            pass

        args = abc()

        args.a2a_blast = '/Users/yuxingxu/Job/Work/FKN/all.tmp.bls'
        args.graph_pyb_file = '/Users/yuxingxu/Job/Work/FKN/graph.py'
        args.graph_pos_file ='/Users/yuxingxu/Job/Work/FKN/graph.pos.py' 
        """

        import matplotlib.pyplot as plt
        import networkx as nx
        import re
        import pickle

        G = nx.Graph()

        with open(args.a2a_blast, 'r') as r:
            num = 0
            for each_line in r:
                num = num + 1
                if re.match(r'^#', each_line):
                    continue
                each_line = re.sub('\n', '', each_line)
                info = each_line.split("\t")
                seq1, seq2, evalue = info[0], info[1], info[10]
                wvalue = evalue_to_wvalue(float(evalue))
                G.add_nodes_from([seq1, seq2])
                G.add_weighted_edges_from([(seq1, seq2, wvalue)])
                if num % 1000000 == 0:
                    print("added %s records to graph" % num)

        pos = nx.spring_layout(G)

        nx.write_gpickle(G, args.graph_pyb_file)
        with open(args.graph_pos_file, 'wb') as f:
            pickle.dump(pos, f)

    elif args_dict["subcommand_name"] == 'SSNplot':
        """
        class abc(object):
            pass

        args = abc()


        args.graph_pyb_file = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/sj50/graph/tmp/graph.py'
        args.graph_pos_file ='/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/sj50/graph/tmp/graph.pos.py' 
        args.plot_file = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/sj50/graph/tmp/graph.pdf'
        """
        import networkx as nx

        with open(args.graph_pos_file, 'rb') as f:
            pos = pickle.load(f)

        G = nx.read_gpickle(args.graph_pyb_file)

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_nodes(G, pos,
                               node_size=10)
        # nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, alpha=0.4)
        plt.axis('off')
        # plt.show()
        plt.savefig(args.plot_file, dpi=1000)

    elif args_dict["subcommand_name"] == "GroupWvalue":
        """
        class abc(object):
            pass

        args = abc()

        args.group_list = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/small_blast/80/all.80.group'
        args.bls_output = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/small_blast/all.bls'
        args.fasta_file = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/sj90'
        args.refgroup_seq = '/lustre/home/xuyuxing/Work/Kena/version3/mcl/cd_hit/mcl/small_blast/80/refgp.fa'
        """
        import networkx as nx

        group_dict = {}
        with open(args.group_list, 'r') as f:
            for each_line in f:
                each_line = re.sub('\n', '', each_line)
                group_id, seq_name = each_line.split("\t")
                if group_id not in group_dict:
                    group_dict[group_id] = []
                group_dict[group_id].append(seq_name)

        from pyfaidx import Fasta

        seqdict = Fasta(args.fasta_file)

        ref_seq_dict = {}
        for i in group_dict:
            ref_seq = sorted(group_dict[i], key=lambda x: len(
                seqdict[x]), reverse=True)[0]
            ref_seq_dict[i] = ref_seq

        with open(args.refgroup_seq, 'w') as f:
            for i in ref_seq_dict:
                f.write(">refgp_" + i + "\n" +
                        str(seqdict[ref_seq_dict[i]]) + "\n")

        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.Graph()

        G.add_nodes_from([1, 2, 3, 4])
        G.add_weighted_edges_from([(1, 2, 10), (3, 4, 10), (1, 3, 1)])
        pos = nx.spring_layout(G)

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_nodes(G, pos,
                               node_size=80)
        nx.draw_networkx_labels(G, pos)
        plt.axis('off')
        plt.show()

        #########

        """
        class abc(object):
            pass
        
        args = abc()
        
        args.all_2_all_blast_results = '/Users/yuxingxu/Job/Work/FKN/all.tmp.bls'
        args.graph_pyb_file = '/Users/yuxingxu/Job/Work/FKN/graph.py'
        args.graph_pos_file ='/Users/yuxingxu/Job/Work/FKN/graph.pos.py' 
        """

        import matplotlib.pyplot as plt
        import networkx as nx
        import re
        import pickle

        G = nx.Graph()

        with open(args.all_2_all_blast_results, 'r') as r:
            num = 0
            for each_line in r:
                num = num + 1
                if re.match(r'^#', each_line):
                    continue
                each_line = re.sub('\n', '', each_line)
                info = each_line.split("\t")
                seq1, seq2, evalue = info[0], info[1], info[10]
                wvalue = evalue_to_wvalue(float(evalue))
                G.add_nodes_from([seq1, seq2])
                G.add_weighted_edges_from([(seq1, seq2, wvalue)])

        pos = nx.spring_layout(G)

        nx.write_gpickle(G, args.graph_pyb_file)
        with open(args.graph_pos_file, 'wb') as f:
            pickle.dump(pos, f)

        #####

        with open(args.graph_pos_file, 'rb') as f:
            pos = pickle.load(f)

        G = nx.read_gpickle(args.graph_pyb_file)

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_nodes(G, pos,
                               node_size=10)
        # nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, alpha=0.4)
        plt.axis('off')
        # plt.show()
        plt.savefig(args.output_file, dpi=1000)

    elif args_dict["subcommand_name"] == "GroupWvalue":
        pass

    elif args_dict["subcommand_name"] == "RenameNodeID":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Balanophora/speci_tree/genome/OrthoFinder/Results_Nov02/WorkingDirectory/Alignments_ids/SpeciesTreeAlignment.fa.raxml.bestTree'
        args.output_tree = '/lustre/home/xuyuxing/Work/Balanophora/speci_tree/genome/OrthoFinder/Results_Nov02/WorkingDirectory/Alignments_ids/SpeciesTreeAlignment.fa.raxml.bestTree.rename'
        args.ID_map_file = '/lustre/home/xuyuxing/Work/Balanophora/speci_tree/genome/OrthoFinder/Results_Nov02/WorkingDirectory/Alignments_ids/rename_map.txt'
        args.file_format = 'newick'
        """
        from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse

        rename_map_dict = tsv_file_parse(args.ID_map_file, key_col=1)

        tree = Phylo.read(args.input_tree, args.file_format)

        for clade in tree.find_clades():
            if clade.name:
                if clade.name in rename_map_dict:
                    clade.name = rename_map_dict[clade.name][1]

        Phylo.write([tree], args.output_tree, args.file_format)

    elif args_dict["subcommand_name"] == "AddNodeID":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Other/liunaiyong/test/test.phb'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/xml/pr17.group.fasttree.node.xml'
        args.file_format = 'phyloxml'
        """

        tree = Phylo.read(args.input_tree, args.file_format)

        num = 0
        for clade in tree.find_clades():
            if clade.name is None:
                clade.name = "N%d" % num
                num = num + 1

        Phylo.write([tree], args.output_tree, args.file_format)

        # from ete3 import Tree

        # if args.file_format == 'newick':
        #     tree = Tree(args.input_tree, format=1)
        # elif args.file_format == 'phyloxml':
        #     tree = phyloxml_read_ete(args.input_tree)
        #
        # num = 0
        # for node in tree.traverse("postorder"):
        #     if not node.is_leaf():
        #         num = num + 1
        #         node.name = "N%d" % num
        #
        # if args.file_format == 'newick':
        #     tree.write(format=1, outfile=args.output_tree)
        # elif args.file_format == 'phyloxml':
        #     phyloxml_write_ete(tree, args.output_tree)

    elif args_dict["subcommand_name"] == "ClearNodeID":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.phb'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.nodeID.phb'
        """

        tree = Phylo.read(args.input_tree, args.file_format)

        for clade in tree.find_clades():
            if not clade.is_terminal():
                clade.name = None

        Phylo.write([tree], args.output_tree, args.file_format)

        # from ete3 import Tree

        # if args.file_format == 'newick':
        #     tree = Tree(args.input_tree, format=1)
        # elif args.file_format == 'phyloxml':
        #     tree = phyloxml_read_ete(args.input_tree)
        #
        # for node in tree.traverse("postorder"):
        #     if not node.is_leaf():
        #         node.name = ""
        #
        # if args.file_format == 'newick':
        #     tree.write(format=1, outfile=args.output_tree)
        # elif args.file_format == 'phyloxml':
        #     phyloxml_write_ete(tree, args.output_tree)

    elif args_dict["subcommand_name"] == "ClearComment":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.phb'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.nodeID.phb'
        """

        tree = Phylo.read(args.input_tree, args.file_format)

        for clade in tree.find_clades():
            if clade.comment:
                clade.comment = None

        Phylo.write([tree], args.output_tree, args.file_format)

    elif args_dict["subcommand_name"] == "ClearConfidence":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.phb'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.nodeID.phb'
        """

        tree = Phylo.read(args.input_tree, args.file_format)

        for clade in tree.find_clades():
            if clade.confidence:
                clade.confidence = None

        Phylo.write([tree], args.output_tree, args.file_format)

        # from ete3 import Tree

        # if args.file_format == 'newick':
        #     tree = Tree(args.input_tree, format=1)
        # elif args.file_format == 'phyloxml':
        #     tree = phyloxml_read_ete(args.input_tree)
        #
        # for node in tree.traverse("postorder"):
        #     if not node.is_leaf():
        #         node.name = ""
        #
        # if args.file_format == 'newick':
        #     tree.write(format=1, outfile=args.output_tree)
        # elif args.file_format == 'phyloxml':
        #     phyloxml_write_ete(tree, args.output_tree)

    elif args_dict["subcommand_name"] == "RootTree":
        """
        class abc(object):
            pass

        args = abc()

        args.node_name = "N390"
        args.input_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/xml/pr17.group.fasttree.node.xml'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/xml/pr17.group.fasttree.node.root.xml'
        """
        from toolbiox.lib.common.evolution.tree_operate import lookup_by_names

        tree = Phylo.read(args.input_tree, args.file_format)

        node_dict = lookup_by_names(tree)

        if args.node_name is None:
            tree.root_at_midpoint()
        else:
            tree.root_with_outgroup(node_dict[args.node_name])

        Phylo.write([tree], args.output_tree, args.file_format)

    elif args_dict["subcommand_name"] == "Newick2PhyloXML":
        """
        class abc(object):
            pass

        args = abc()

        args.input_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.phb'
        args.output_tree = '/lustre/home/xuyuxing/Work/Kena/version2/mcl/pr17/cluster/all/pr17.group.fasttree/pr17.group.fasttree.xml'
        """

        Phylo.convert(args.input_tree, 'newick', args.output_tree, 'phyloxml')

    elif args_dict["subcommand_name"] == "DrawTree":
        """
        class abc(object):
            pass

        args = abc()
        args.tree_file = "/Users/yuxingxu/Downloads/SpeciesTreeAlignment.fa.raxml.bestTree"
        args.input_format = 'newick'
        args.output_file = "/Users/yuxingxu/Downloads/SpeciesTreeAlignment.fa.raxml.pdf"
        args.output_format = 'pdf'
        args.figure_size = (-20.0,20.0,-20.0,20.0)
        """

        tree = Phylo.read(args.tree_file, args.input_format)
        tree = normal_tree_rela_coord(tree)
        tree = normal_tree_abs_coord(tree, args.figure_size)

        fig, ax = plt.subplots(figsize=(21, 21))

        ax.set_xlim(-21, 21)
        ax.set_ylim(-21, 21)

        # ax.plot([10],[50],'ro')

        draw_tree(ax, tree)
        plt.savefig(args.output_file)
        # plt.show()

    elif args_dict["subcommand_name"] == "MonophylyTest":
        """
        class abc(object):
            pass

        args = abc()
        args.Bootstrap_trees = "/lustre/home/xuyuxing/Database/Balanophora/Comp_genome/dongming/orthofinder_191218/output/topo_test/subfile6.output/OG0010028/RAxML_bootstrap.OG0010028"
        args.file_format = 'newick'
        args.gene_list_file = '/lustre/home/xuyuxing/Database/Balanophora/Comp_genome/dongming/orthofinder_191218/output/topo_test/subfile6.output/OG0010028/tmp'
        """

        from toolbiox.lib.common.evolution.tree_operate import monophyly
        from toolbiox.lib.common.fileIO import read_list_file

        if not args.output_file is None:
            sys.stdout = open(args.output_file, 'w')

        gene_list = read_list_file(args.gene_list_file)

        for jacc_thre in [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]:
            tree_gen = Phylo.parse(args.Bootstrap_trees, args.file_format)
            num = 0
            for tree in tree_gen:
                flag, gene_list_tmp = monophyly(
                    gene_list, tree, None, jacc_thre)
                if flag:
                    num = num + 1
                # print(flag, len(gene_list_tmp))

            print("%.2f\t%d" % (jacc_thre, num))

    elif args_dict["subcommand_name"] == "RootTreeBySpecies":
        from Bio import Phylo
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        from toolbiox.src.xuyuxing.tools.phytools import RootGeneTree

        file_info = tsv_file_dict_parse(args.gene_to_species_map, fieldnames=[
                                        'g_id', 's_id'], key_col='g_id')
        gene_to_species_map_dict = {}
        for i in file_info:
            gene_to_species_map_dict[i] = file_info[i]['s_id']

        gene_tree = Phylo.read(args.gene_tree, 'newick')
        species_tree = Phylo.read(args.species_tree, 'newick')

        gene_tree_rooted = RootGeneTree(
            gene_tree, species_tree, gene_to_species_map_dict)

        Phylo.write(gene_tree_rooted, args.output_tree, 'newick')

    elif args_dict["subcommand_name"] == "EasyABSREL":
        from toolbiox.src.xuyuxing.tools.hyphy_tools import easy_ABSREL
        import os

        args.rooted_gene_tree = os.path.realpath(args.rooted_gene_tree)
        args.cds_aln_fasta = os.path.realpath(args.cds_aln_fasta)
        args.output_prefix = os.path.realpath(args.output_prefix)

        easy_ABSREL(args.rooted_gene_tree, args.cds_aln_fasta, args.output_prefix,
                    tree_format=args.tree_format, threads=args.threads)

    elif args_dict["subcommand_name"] == "EasyRELAX":
        from toolbiox.src.xuyuxing.tools.hyphy_tools import easy_RELAX
        import os

        args.rooted_gene_tree = os.path.realpath(args.rooted_gene_tree)
        args.cds_aln_fasta = os.path.realpath(args.cds_aln_fasta)
        args.output_dir = os.path.realpath(args.output_dir)

        test_node_list = [i for i in args.test_node.split(",") if i != '']
        # print(test_node_list)

        easy_RELAX(args.rooted_gene_tree, args.cds_aln_fasta, args.output_dir,
                   test_node=test_node_list, tree_format=args.tree_format, threads=args.threads)
