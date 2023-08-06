from toolbiox.config import dlcpar_search_path
import os
from toolbiox.lib.common.os import cmd_run
from Bio import Phylo
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.evolution.tree_operate import add_clade_name, lookup_by_names

def run_dlcpar(species_tree_FN, gene_to_species_map_FN, rooted_gene_tree_FN):
    species_tree_FN = os.path.abspath(species_tree_FN)
    gene_to_species_map_FN = os.path.abspath(gene_to_species_map_FN)
    rooted_gene_tree_FN = os.path.abspath(rooted_gene_tree_FN)

    cmd_string = "%s -s %s -S %s -D 1 -C 0.125 %s -x 1" % (
        dlcpar_search_path, species_tree_FN, gene_to_species_map_FN, rooted_gene_tree_FN)
    cmd_run(cmd_string, silence=True)

    recon_tree_file = rooted_gene_tree_FN + ".dlcpar.locus.tree"
    recon_node_file = rooted_gene_tree_FN + ".dlcpar.locus.recon"

    return recon_tree_file, recon_node_file


def merge_locus_tree_and_recon_file(recon_tree_file, recon_node_file, output_file, gene_to_species_map_dict):
    recon_tree = Phylo.read(recon_tree_file, 'newick')
    node_info_dict = tsv_file_dict_parse(recon_node_file, fieldnames=['node_id', 'sp_name', 'type'], key_col='node_id')

    recon_tree = add_clade_name(recon_tree)
    recon_node_dict = lookup_by_names(recon_tree)

    for i in recon_node_dict:
        if not recon_node_dict[i].is_terminal():
            duplication = 'Y' if node_info_dict[i]['type'] == 'dup' else 'N'
            comment_string = "&&NHX:S=%s:D=%s" % (node_info_dict[i]['sp_name'], duplication)
        else:
            comment_string = "&&NHX:S=%s" % gene_to_species_map_dict[i]
        recon_node_dict[i].comment = comment_string

    with open(output_file, 'w') as f:
        Phylo.write(recon_tree, f, 'newick')


