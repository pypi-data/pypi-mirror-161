import os
from Bio import Phylo
from io import StringIO
import toolbiox.api.xuyuxing.comp_genome.orthofinder_tree_resolve.tree as tree_lib
from toolbiox.api.xuyuxing.comp_genome.orthofinder_tree_resolve.trees2ologs_of import CheckAndRootTree, Resolve
from toolbiox.lib.common.evolution.tree_operate import map_to_method
from toolbiox.config import dlcpar_search_path
from toolbiox.lib.common.os import cmd_run


def phylo2ete(phylo_tree, tree_type='species_tree'):
    """
    species_tree will keep node name
    gene_tree will keep node support
    """
    tmp_handle = StringIO()
    Phylo.write(phylo_tree, tmp_handle, "newick")
    tree_string = tmp_handle.getvalue().strip()

    if tree_type == 'species_tree':
        ete_tree = tree_lib.Tree(tree_string, format=3)
    elif tree_type == 'gene_tree':
        ete_tree = tree_lib.Tree(tree_string, format=0)

    return ete_tree


def ete2phylo(ete_tree, tree_type='species_tree'):
    """
    species_tree will keep node name
    gene_tree will keep node support
    """
    if tree_type == 'species_tree':
        tree_string = ete_tree.write(format=3)
    elif tree_type == 'gene_tree':
        tree_string = ete_tree.write(format=0)

    phylo_tree = Phylo.read(StringIO(tree_string), 'newick')

    return phylo_tree


def root_gene_tree(gene_tree, species_tree_rooted, GeneToSpecies_dict):
    GeneToSpecies = map_to_method(GeneToSpecies_dict)
    species_tree_rooted_ete = phylo2ete(species_tree_rooted, 'species_tree')
    gene_tree_ete = phylo2ete(gene_tree, 'gene_tree')

    rooted_gene_tree_ete, qHaveSupport = CheckAndRootTree(
        gene_tree_ete.write(format=0), species_tree_rooted_ete, GeneToSpecies)
    rooted_gene_tree = ete2phylo(rooted_gene_tree_ete, tree_type='gene_tree')

    return rooted_gene_tree


def resolve_rooted_gene_tree(rooted_gene_tree, GeneToSpecies_dict):
    GeneToSpecies = map_to_method(GeneToSpecies_dict)

    rooted_gene_tree_ete = phylo2ete(rooted_gene_tree, 'gene_tree')
    resolved_gene_tree_ete = Resolve(rooted_gene_tree_ete, GeneToSpecies)
    resolved_gene_tree = ete2phylo(
        resolved_gene_tree_ete, tree_type='gene_tree')

    return resolved_gene_tree


if __name__ == '__main__':
    # let gene tree resolved

    gene_tree_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/orthofinder/pt_file/OrthoFinder/Results_Jun23/MultipleSequenceAlignments/test/OG0001554.fa.phb'
    gene_tree = Phylo.read(gene_tree_file, 'newick')

    sp_tree_file = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/orthofinder/pt_file/OrthoFinder/Results_Jun23/Species_Tree/SpeciesTree_rooted_node_labels.txt'
    species_tree_rooted = Phylo.read(sp_tree_file, 'newick')

    GeneToSpecies_dict = {}
    for i in gene_tree.get_terminals():
        GeneToSpecies_dict[i.name] = i.name.split("_")[0]

    # root gene tree by species tree
    rooted_gene_tree = root_gene_tree(
        gene_tree, species_tree_rooted, GeneToSpecies_dict)

    Phylo.draw_ascii(gene_tree)
    Phylo.draw_ascii(rooted_gene_tree)

    # resolve gene tree (orthofinder way)
    resolved_gene_tree = resolve_rooted_gene_tree(
        rooted_gene_tree, GeneToSpecies_dict)

    Phylo.draw_ascii(resolved_gene_tree)

    #
