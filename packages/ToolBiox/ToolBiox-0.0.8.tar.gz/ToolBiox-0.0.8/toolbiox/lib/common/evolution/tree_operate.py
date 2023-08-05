from io import StringIO
from itertools import permutations, combinations
from Bio import Phylo
from Bio.Phylo.BaseTree import Tree, Clade
import re
import copy
import numpy
import sys
import operator
import math
from collections import OrderedDict
from toolbiox.lib.xuyuxing.math.set_operating import jaccord_index
from toolbiox.api.xuyuxing.plot.path_patch import scale_to_give_size, line_segment_plot
from toolbiox.lib.xuyuxing.base.common_command import num_to_chr
import networkx as nx


__author__ = 'Yuxing Xu'

"""
from Bio import Phylo
from toolbiox.lib.common.evolution.tree_operate import add_clade_name

tree_file = "/Users/yuxingxu/Downloads/SpeciesTreeAlignment.fa.raxml.bestTree"
tree = Phylo.read(tree_file, 'newick')
tree = add_clade_name(tree)
"""


# see a tree

def lookup_by_names(tree, order='preorder'):
    """
    order ({'preorder', 'postorder', 'level'}) - Tree traversal order: 'preorder' (default) is depth-first search, 'postorder' is DFS with child nodes preceding parents, and 'level' is breadth-first search.

    order: depth-first search (DFS), preorder from root to first leaf one clade by clade, and second leaf... ; postorder, same search but from leaf to root
    level: breadth-frist search (BFS), from root to leaf one level by level

    see: https://biopython.org/DIST/docs/api/Bio.Phylo.BaseTree.TreeMixin-class.html
    """
    names = OrderedDict()
    for clade in tree.find_clades(order=order):
        if clade.name:
            if clade.name in names:
                raise ValueError("Duplicate key: %s" % clade.name)
            names[clade.name] = clade
    return names


def get_newick_string(tree):
    return tree.format('newick')

# clades relationship


def get_ancestors(child_clade, tree):
    """
    return the list path of parent-child links from the tree root to the clade of choice (root will return null list)
    """
    node_path = tree.get_path(child_clade)
    if len(node_path) == 0:
        return []
    else:
        return [tree.root] + node_path[:-1]


def get_parent(child_clade, tree):
    """
    get most close parent node for child_clade in a tree (root will return null list)
    """
    if child_clade == tree.root:
        return []
    node_path = tree.get_path(child_clade)
    if len(node_path) == 1:
        return tree.root
    else:
        return node_path[-2]


def get_sister(clade, tree):
    """
    get sister clade list
    """

    parent_node = get_parent(clade, tree)
    return [i for i in parent_node.clades if i != clade]


def get_sons(parent_clade):
    """
    get most close son nodes for clade in a tree
    """
    return parent_clade.clades


def get_offspring(parent_clade):
    """
    get all offspring clade for a parent clade
    """
    offspring = []
    for i in parent_clade.find_clades(order='level'):
        if i == parent_clade:
            continue
        offspring.append(i)
    return offspring


def get_leaves(parent_clade, return_name=False):
    if return_name:
        return [leaf.name for leaf in parent_clade.get_terminals()]
    else:
        return [leaf for leaf in parent_clade.get_terminals()]


def get_intranode(parent_clade, return_name=False):
    if return_name:
        return [clade.name for clade in parent_clade.get_nonterminals()]
    else:
        return [clade for clade in parent_clade.get_nonterminals()]


def get_closest_leaf(clade, topology_only=False):
    """Returns node's closest descendant leaf and the distance to
    it.

    :argument False topology_only: If set to True, distance
      between nodes will be referred to the number of nodes
      between them. In other words, topological distance will be
      used instead of branch length distances.

    :return: A tuple containing the closest leaf referred to the
      current node and the distance to it.

    """
    min_dist = None
    min_node = None
    if clade.is_terminal():
        return clade, 0.0
    else:
        for ch in get_sons(clade):
            node, d = get_closest_leaf(ch, topology_only=topology_only)
            if topology_only:
                d += 1.0
            else:
                d += ch.branch_length
            if min_dist is None or d < min_dist:
                min_dist = d
                min_node = node
        return min_node, min_dist


def all_clades_parent(tree):
    parents = {}
    for clade in tree.find_clades(order='level'):
        for child in clade:
            parents[child] = clade
    return parents


def is_offspring_of(A, B, tree):
    """
    A is offspring of B
    """
    return B in get_ancestors(A, tree)


def is_ancestors_of(A, B, tree):
    """
    A is ancestors of B
    """
    return A in get_ancestors(B, tree)


def is_son_of(A, B):
    """
    A is son of B
    """
    return A in get_sons(B)


def is_parent_of(A, B, tree):
    """
    A is parent of B
    """
    return A in get_parent(B, tree)


def is_pass_node(clade, tree):
    if clade.is_terminal():
        return False
    elif clade == tree.root:
        return False
    else:
        clade_son = get_sons(clade)
        if len(clade_son) == 1:
            return True
        else:
            return False


def monophyly(leaf_set, tree, support_threshold=0.8, jaccard_threshold=0.8, exclude_leaf_set=None):
    """
    give a list of gene (gene_set) to check if this gene in a single clade in the tree
    :param tree:
    :param gene_set:
    :param support_threshold:
    :param jaccard_threshold:
    :return:
    """
    tree_old = copy.deepcopy(tree)
    pass_monophyly = []
    for leaf in tree_old.get_terminals():
        if not leaf.name in leaf_set:
            # unroot tree
            tree = copy.deepcopy(tree_old)
            tree = add_clade_name(tree)
            node_dict = lookup_by_names(tree)

            # reroot tree
            tree_new, node_dict_new = reroot_by_outgroup_clade(
                tree, node_dict, leaf.name)
            if not support_threshold is None:
                for clade_name in get_low_support_clade(tree_new, support_threshold):
                    tree_new.collapse(node_dict_new[clade_name])
            node_dict_new = lookup_by_names(tree_new)

            # check monophyly

            for clade_name in node_dict_new:
                clade_leaf_list = [
                    clade_leaf.name for clade_leaf in node_dict_new[clade_name].get_terminals()]
                if exclude_leaf_set:
                    clade_leaf_list_without_exclude = set(
                        clade_leaf_list) - set(exclude_leaf_set)
                else:
                    clade_leaf_list_without_exclude = set(clade_leaf_list)

                if jaccord_index(clade_leaf_list_without_exclude, leaf_set) >= jaccard_threshold:
                    pass_monophyly.append(clade_leaf_list)

    if len(pass_monophyly) > 0:
        min_monophyly_list = sorted(
            pass_monophyly, key=lambda x: jaccord_index(x, leaf_set), reverse=True)[0]
        return True, list(min_monophyly_list)
    else:
        return False, []


def get_MRCA(A, B, tree):
    """
    get most recent common ancestor MRCA
    """
    A_ancest = get_ancestors(A, tree) + [A]
    B_ancest = get_ancestors(B, tree) + [B]

    if len(set(A_ancest) & set(B_ancest)) == 0:
        return tree.root
    else:
        i = 0
        MRCA = None
        while i < len(A_ancest) and i < len(B_ancest) and A_ancest[i] == B_ancest[i]:
            MRCA = A_ancest[i]
            i = i + 1
        return MRCA


def get_MRCA_from_list(clade_list, tree):
    """
    get most recent common ancestor MRCA
    """
    ancest_list = []
    for i in clade_list:
        ancest_list.extend(get_ancestors(i, tree) + [i])

    A_ancest = get_ancestors(clade_list[0], tree) + [clade_list[0]]

    MRCA = A_ancest[0]
    for clade in A_ancest:
        if ancest_list.count(clade) == len(clade_list):
            MRCA = clade
        else:
            break

    return MRCA


def get_distance_to_root(A, tree):
    """
    get distance (sum of branch length) from given clade to root
    """
    ancest_list = get_ancestors(A, tree) + [A]
    distance = 0.0
    for i in ancest_list:
        distance = distance + i.branch_length
    return distance


def get_distance(A, B, tree):
    """
    get distance (sum of branch length) for two clade
    """

    MRCA = get_MRCA(A, B, tree)

    MRCA_to_root = get_distance_to_root(MRCA, tree)
    A_to_root = get_distance_to_root(A, tree)
    B_to_root = get_distance_to_root(B, tree)

    if A_to_root < MRCA_to_root or B_to_root < MRCA_to_root:
        raise ValueError("evolution distance small than ancestor, maybe BUG")

    return (A_to_root - MRCA_to_root) + (B_to_root - MRCA_to_root)


def get_path_to_root(A, tree):
    """
    get path number from A to root
    """
    if A == tree.root:
        return []
    else:
        ancest_list = get_ancestors(A, tree) + [A]
        return ancest_list


def get_path_step_to_root(A, tree):
    """
    get path number from A to root
    """
    if A == tree.root:
        return 0
    else:
        ancest_list = get_ancestors(A, tree) + [A]
        return len(ancest_list)


def get_path_step(A, B, tree):
    """
    get the path number between clades
    """
    MRCA = get_MRCA(A, B, tree)

    MRCA_to_root = get_path_step_to_root(MRCA, tree)
    A_to_root = get_path_step_to_root(A, tree)
    B_to_root = get_path_step_to_root(B, tree)

    if A_to_root < MRCA_to_root or B_to_root < MRCA_to_root:
        raise ValueError("evolution distance small than ancestor, maybe BUG")

    return (A_to_root - MRCA_to_root) + (B_to_root - MRCA_to_root)


# change treeadd_clade_name


def add_clade_name(tree, chr_name=False):
    used_name = []
    for clade in tree.find_clades():
        if clade.name:
            used_name.append(clade.name)

    num = 0
    for clade in tree.find_clades():
        if clade.name is None:
            if chr_name:
                new_id = "Node_%s" % num_to_chr(num, 3)
            else:
                new_id = "N%d" % num
            while new_id in used_name:
                num = num + 1
                if chr_name:
                    new_id = "Node_%s" % num_to_chr(num, 3)
                else:
                    new_id = "N%d" % num
            clade.name = new_id
            used_name.append(new_id)
    return tree


def clade_rename(tree, rename_dict):

    for clade in tree.find_clades():
        if clade.name in rename_dict:
            clade.name = rename_dict[clade.name]

    return tree


def equalCladeTopo(clade1, clade2):
    if clade1.is_terminal() and clade2.is_terminal():
        if clade1.name == clade2.name:
            return True
        else:
            return False
    elif (not clade1.is_terminal()) and (not clade2.is_terminal()):
        if len(clade1.clades) != len(clade2.clades):
            return False
        all_true_flag = True
        for sub_clade1 in clade1.clades:
            true_flag = False
            for sub_clade2 in clade2.clades:
                if equalCladeTopo(sub_clade1, sub_clade2):
                    true_flag = True
            if not true_flag:
                all_true_flag = False
        return all_true_flag
    else:
        return False


def get_low_support_clade(tree, threshold=0.8):
    bad_support = []
    for clade in tree.get_nonterminals():
        if clade.confidence:
            if clade.confidence < threshold:
                bad_support.append(clade.name)
    return bad_support


def collapse_clade_list(tree, name_dict, want_to_collapse_list):
    for j in want_to_collapse_list:
        tree.collapse(name_dict[j])
    return tree


def collapse_low_support(tree, threshold=0.8):
    tree = add_clade_name(tree)
    tree_name_dir = lookup_by_names(tree)
    low_support_clade_list = get_low_support_clade(tree, threshold)
    for j in low_support_clade_list:
        try:
            tree.collapse(tree_name_dir[j])
        except:
            pass
    return tree


def ignore_branch_length(tree, to_None=False):
    """
    remove length to 1.0
    """
    tree = add_clade_name(tree)
    tree_name_dir = lookup_by_names(tree)
    for clade_name in tree_name_dir:
        if to_None:
            tree_name_dir[clade_name].branch_length = None
        else:
            tree_name_dir[clade_name].branch_length = 1.0
    return tree


def remove_given_node(clade, remove_name_list):
    if clade.name in remove_name_list:
        return None
    else:
        if clade.is_terminal():
            return clade
        else:
            son_clade_list = []
            for i in clade.clades:
                filtered_clade = remove_given_node(i, remove_name_list)
                if filtered_clade:
                    son_clade_list.append(filtered_clade)

            if len(son_clade_list) == 0:
                return None
            else:
                clade.clades = son_clade_list
                return clade


def remove_given_node_from_tree(tree, remove_name_list):
    tree_clade = copy.deepcopy(tree.clade)
    clade = remove_given_node(tree_clade, remove_name_list)

    new_tree = Tree(clade, tree.rooted)
    new_tree = remove_pass_node(new_tree)

    return new_tree


def remove_all_node_name(clade):
    clade_now = copy.deepcopy(clade)
    if clade_now.is_terminal():
        return clade_now
    else:
        clade_now.name = None
        new_sub_clade = []
        for i in clade_now.clades:
            new_sub_clade.append(remove_all_node_name(i))
        clade_now.clades = new_sub_clade
        return clade_now


def remove_tree_node_name(tree):
    tree_clade = copy.deepcopy(tree.clade)
    clade = remove_all_node_name(tree_clade)
    new_tree = Tree(clade, tree.rooted)

    return new_tree


def remove_pass_node(tree):
    iter_flag = True
    new_tree = copy.deepcopy(tree)

    while iter_flag:
        tree_tmp = copy.deepcopy(new_tree)
        tree_tmp = add_clade_name(tree_tmp)
        tree_tmp_name_dir = lookup_by_names(tree_tmp, order='level')

        # new_tree_root = tree_name_dir[list(tree_name_dir.keys())[0]]

        # build give son to find parent
        son_to_parent_hash = {}
        for clade_name in tree_tmp_name_dir:
            for son_clade in tree_tmp_name_dir[clade_name].clades:
                if son_clade.name in son_to_parent_hash:
                    raise ValueError("same son for different parent")
                son_to_parent_hash[son_clade.name] = clade_name

        # fund pass node
        pass_node_list = [clade_name for clade_name in tree_tmp_name_dir if
                          is_pass_node(tree_tmp_name_dir[clade_name], tree_tmp)]

        if len(pass_node_list) != 0:
            # for pass node give son to parent
            for pass_node_name in pass_node_list:
                parent_name = son_to_parent_hash[pass_node_name]
                if len(tree_tmp_name_dir[pass_node_name].clades) != 1:
                    raise ValueError("find a error pass node")
                son_name = tree_tmp_name_dir[pass_node_name].clades[0].name

                brother_list = tree_tmp_name_dir[parent_name].clades
                new_brother_list = []
                for i in brother_list:
                    if i.name == pass_node_name:
                        new_brother_list.append(tree_tmp_name_dir[son_name])
                    else:
                        new_brother_list.append(tree_tmp_name_dir[i.name])

                tree_tmp_name_dir[parent_name].clades = new_brother_list

            # build new tree
            root_id = list(tree_tmp_name_dir.keys())[0]
            new_tree = Tree(
                root=tree_tmp_name_dir[root_id], rooted=tree_tmp.rooted)

        else:
            iter_flag = False

    return new_tree


def mid_unrooted_tree(tree):
    """
    root a unrooted tree at midpoint
    """
    tree.root_at_midpoint()
    tree_new = add_clade_name(tree)
    node_dict = lookup_by_names(tree_new)
    return tree_new, node_dict


def reroot_by_outgroup_clade(tree, node_dict, outgroups_clade_name, keep_old=False):
    outgroup_clade = node_dict[outgroups_clade_name]
    outgroup_clade_old = copy.deepcopy(outgroup_clade)

    if keep_old:
        tree_old = copy.deepcopy(tree)

    tree.root_with_outgroup(outgroup_clade)
    tree_new = add_clade_name(tree)

    sis = [i for i in tree_new.clade.clades if i not in outgroup_clade_old.clades][0]

    new_outgroup_clade = copy.deepcopy(outgroup_clade_old)

    if sis.confidence is None:
        sis.confidence = 100

    root_clade = Clade(clades=[sis, new_outgroup_clade], name='root')

    tree_new = Tree(root=root_clade, rooted=True)
    node_dict_new = lookup_by_names(tree_new)

    if keep_old:
        tree_old = add_clade_name(tree_old)
        node_dict_old = lookup_by_names(tree_old)
        return tree_new, node_dict_new, tree_old, node_dict_old
    else:
        return tree_new, node_dict_new


def reroot_by_outgroup_seqid(tree, outgroups_seq_list):
    tree_old = copy.deepcopy(tree)
    for leaf in tree_old.get_terminals():
        if not leaf.name in outgroups_seq_list:
            # unroot tree
            tree = copy.deepcopy(tree_old)
            tree = add_clade_name(tree)
            node_dict = lookup_by_names(tree)

            tree_new, node_dict_new = reroot_by_outgroup_clade(
                tree, node_dict, leaf.name)
            for clade_name in node_dict_new:
                clade_leaf_list = [
                    clade_leaf.name for clade_leaf in node_dict_new[clade_name].get_terminals()]
                if set(clade_leaf_list) == set(outgroups_seq_list):
                    tree_out, node_dict_out = reroot_by_outgroup_clade(
                        tree_new, node_dict_new, clade_name)
                    return tree_out, node_dict_out
    return None


# root a tree rewrite from orthofinder
# need more test

class RootMap(object):
    def __init__(self, setA, setB, GeneToSpecies):
        self.setA = setA
        self.setB = setB
        self.GeneToSpecies = GeneToSpecies

    def GeneMap(self, gene_name):
        sp = self.GeneToSpecies(gene_name)
        if sp in self.setA:
            return True
        elif sp in self.setB:
            return False
        else:
            print(gene_name)
            print(sp)
            raise Exception


def StoreSpeciesSets(t, GeneMap, tag="sp_"):
    tag_up = tag + "up"
    tag_down = tag + "down"
    for clade in t.find_clades(order='postorder'):
        if clade.is_terminal():
            setattr(clade, tag_down, {GeneMap(clade.name)})
        elif clade == t.root:
            continue
        else:
            setattr(clade, tag_down, set.union(
                *[ch.__getattribute__(tag_down) for ch in get_sons(clade)]))

    for clade in t.find_clades(order='preorder'):
        if clade == t.root:
            setattr(clade, tag_up, set())
        else:
            parent = get_parent(clade, t)
            if parent == t.root:
                others = [ch for ch in get_sons(parent) if ch != clade]
                setattr(clade, tag_up, set.union(
                    *[other.__getattribute__(tag_down) for other in others]))
            else:
                others = [ch for ch in get_sons(parent) if ch != clade]
                sp_downs = set.union(
                    *[other.__getattribute__(tag_down) for other in others])
                setattr(clade, tag_up, parent.__getattribute__(
                    tag_up).union(sp_downs))
    # setattr(t, tag_down, set.union(*[ch.__getattribute__(tag_down) for ch in get_sons(t)]))


def OutgroupIngroupSeparationScore(sp_up, sp_down, sett1, sett2, N_recip, n1, n2):
    f_dup = len(sp_up.intersection(sett1)) * len(sp_up.intersection(sett2)) * len(sp_down.intersection(sett1)) * len(
        sp_down.intersection(sett2)) * N_recip
    f_a = len(sp_up.intersection(sett1)) * (n2 - len(sp_up.intersection(sett2))) * (
        n1 - len(sp_down.intersection(sett1))) * len(sp_down.intersection(sett2)) * N_recip
    f_b = (n1 - len(sp_up.intersection(sett1))) * len(sp_up.intersection(sett2)) * len(sp_down.intersection(sett1)) * (
        n2 - len(sp_down.intersection(sett2))) * N_recip
    choice = (f_dup, f_a, f_b)
    #    print(choice)
    return max(choice)


def map_to_method(gene_to_species_map):
    def f(gene_id):
        return gene_to_species_map[gene_id]

    return f


def get_roots_by_species(gene_tree, species_rooted_tree, gene_to_species_map):
    """
    rewrite from orthofinder trees2ologs_of.py GetRoots
    """
    # reads tree
    gene_tree = add_clade_name(gene_tree)
    gene_tree_node_dict = lookup_by_names(gene_tree)
    species_rooted_tree = add_clade_name(species_rooted_tree)
    species_rooted_tree_node_dict = lookup_by_names(species_rooted_tree)
    GeneToSpecies = map_to_method(gene_to_species_map)

    speciesObserved = set([GeneToSpecies(leaf_name)
                           for leaf_name in get_leaves(gene_tree, True)])

    if len(speciesObserved) == 1:
        # arbitrary root if all genes are from the same species
        return [next(n for n in gene_tree.clade)]

    # use species tree to find correct outgroup according to what species are present in the gene tree
    n = species_rooted_tree.clade
    children = get_sons(n)
    leaves = [set(get_leaves(ch, True)) for ch in children]
    # make sure two group have species in gene tree
    have = [len(l.intersection(speciesObserved)) != 0 for l in leaves]
    while sum(have) < 2:
        n = children[have.index(True)]
        children = get_sons(n)
        leaves = [set(get_leaves(ch, True)) for ch in children]
        have = [len(l.intersection(speciesObserved)) != 0 for l in leaves]

    # Get splits to look for
    roots_list = []
    scores_list = []  # the fraction completeness of the two clades
    #    roots_set = set()
    for i in range(0, len(leaves)):
        t1 = leaves[i]
        t2 = set.union(*[l for j, l in enumerate(leaves) if j != i])
        # G - set of species in gene tree
        # First relevant split in species tree is (A,B), such that A \cap G \neq \emptyset and A \cap G \neq \emptyset
        # label all nodes in gene tree according the whether subsets of A, B or both lie below node
        StoreSpeciesSets(gene_tree, GeneToSpecies)  # sets of species
        root_mapper = RootMap(t1, t2, GeneToSpecies)
        sett1 = set(t1)
        sett2 = set(t2)
        nt1 = float(len(t1))
        nt2 = float(len(t2))
        N_recip = 1. / (nt1 * nt1 * nt2 * nt2)
        GeneMap = root_mapper.GeneMap
        # ingroup/outgroup identification
        StoreSpeciesSets(gene_tree, GeneMap, "inout_")
        # find all possible locations in the gene tree at which the root should be

        T = {True, }
        F = {False, }
        TF = set([True, False])
        for m in gene_tree.find_clades(order='postorder'):
            if m.is_terminal():
                if len(m.inout_up) == 1 and m.inout_up != m.inout_down:
                    # this is the unique root
                    return [m]
                    # print(m)
            else:
                if len(m.inout_up) == 1 and len(m.inout_down) == 1 and m.inout_up != m.inout_down:
                    # this is the unique root
                    return [m]
                    # print(m)
                nodes = get_sons(m) if m == gene_tree.root else [
                    m] + get_sons(m)
                clades = [ch.inout_down for ch in nodes] if m == gene_tree.root else (
                    [m.inout_up] + [ch.inout_down for ch in get_sons(m)])
                # do we have the situation A | B or (A,B),S?
                if len(nodes) == 3:
                    if all([len(c) == 1 for c in clades]) and T in clades and F in clades:
                        # unique root
                        if clades.count(T) == 1:
                            return [nodes[clades.index(T)]]
                            # print([nodes[clades.index(T)]])
                        else:
                            return [nodes[clades.index(F)]]
                            # print([nodes[clades.index(F)]])
                    elif T in clades and F in clades:
                        # AB-(A,B) or B-(AB,A)
                        ab = [c == TF for c in clades]
                        i = ab.index(True)
                        roots_list.append(nodes[i])
                        sp_down = nodes[i].sp_down
                        sp_up = nodes[i].sp_up
                        #                        print(m)
                        scores_list.append(
                            OutgroupIngroupSeparationScore(sp_up, sp_down, sett1, sett2, N_recip, nt1, nt2))
                    elif clades.count(TF) >= 2:
                        # (A,A,A)-excluded, (A,A,AB)-ignore as want A to be bigest without including B, (A,AB,AB), (AB,AB,AB)
                        i = 0
                        roots_list.append(nodes[i])
                        sp_down = nodes[i].sp_down
                        sp_up = nodes[i].sp_up
                        #                        print(m)
                        scores_list.append(
                            OutgroupIngroupSeparationScore(sp_up, sp_down, sett1, sett2, N_recip, nt1, nt2))
                elif T in clades and F in clades:
                    roots_list.append(m)
                    scores_list.append(0)  # last choice
    # If we haven't found a unique root then use the scores for completeness of ingroup/outgroup to root
    if len(roots_list) == 0:
        return []  # This shouldn't occur

    return [sorted(zip(scores_list, roots_list), key=lambda x:x[0], reverse=True)[0][1]]


def get_root_by_species(gene_tree, species_rooted_tree, gene_to_species_map):
    roots = get_roots_by_species(
        gene_tree, species_rooted_tree, gene_to_species_map)
    if len(roots) > 0:
        root_dists = [get_closest_leaf(r)[1] for r in roots]
        i, _ = max(enumerate(root_dists), key=operator.itemgetter(1))
        return roots[i]
    else:
        return None  # single species tree


def get_rooted_tree_by_species_tree(unrooted_gene_tree, species_tree, gene_to_species_map_dict):
    unrooted_gene_tree = add_clade_name(unrooted_gene_tree)
    unrooted_gene_tree_node_dict = lookup_by_names(unrooted_gene_tree)

    best_root_clade = get_root_by_species(
        unrooted_gene_tree, species_tree, gene_to_species_map_dict)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(unrooted_gene_tree,
                                                                                                            unrooted_gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    return gene_tree_rooted


def get_root_by_species_for_file(unrooted_tree_file, species_tree_file, gene_to_species_map_dict, output_tree_file):
    species_tree = Phylo.read(species_tree_file, 'newick')
    unrooted_gene_tree = Phylo.read(unrooted_tree_file, 'newick')
    unrooted_gene_tree = add_clade_name(unrooted_gene_tree)
    unrooted_gene_tree_node_dict = lookup_by_names(unrooted_gene_tree)

    best_root_clade = get_root_by_species(
        unrooted_gene_tree, species_tree, gene_to_species_map_dict)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(unrooted_gene_tree,
                                                                                                            unrooted_gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    for i in gene_tree_rooted_node_dict:
        c = gene_tree_rooted_node_dict[i]
        if not c.is_terminal():
            c.name = None

    Phylo.write(gene_tree_rooted, output_tree_file, format='newick')

# for nhx format


def map_node_species_info(rooted_gene_tree, species_tree, GeneToSpecies_dict):
    species_tree_node_dict = lookup_by_names(species_tree)

    for clade in rooted_gene_tree.find_clades(order='preorder'):
        if clade.is_terminal():
            clade.taxon = GeneToSpecies_dict[clade.name]
        else:
            sp_list = list(set([GeneToSpecies_dict[i.name]
                                for i in clade.get_terminals()]))
            sp_clade_list = [species_tree_node_dict[j] for j in sp_list]
            mrca_name = get_MRCA_from_list(sp_clade_list, species_tree).name
            clade.taxon = mrca_name

            num = 0
            sub_clades = {}
            for i in clade.clades:
                sub_clades[num] = i
                num += 1

            duplication = False
            speciation = True
            for a, b in combinations(list(sub_clades.keys()), 2):
                s1 = sub_clades[a]
                s2 = sub_clades[b]

                s1_sp_list = list(set([GeneToSpecies_dict[i.name]
                                       for i in s1.get_terminals()]))
                s2_sp_list = list(set([GeneToSpecies_dict[i.name]
                                       for i in s2.get_terminals()]))

                over_sp = set(s1_sp_list) & set(s2_sp_list)
                if len(over_sp) > 0:
                    duplication = True
                    speciation = False
                    break

            clade.duplication = duplication
            clade.speciation = speciation

    return rooted_gene_tree


def get_nhx_comment(gene_tree):
    for clade in gene_tree.find_clades(order='preorder'):
        if clade.is_terminal():
            clade.comment = "&&NHX:S=%s" % clade.taxon
        else:
            if clade.confidence:
                if isinstance(clade.confidence, float):
                    confidence = min(100, int(clade.confidence * 100))
                else:
                    confidence = clade.confidence
            else:
                confidence = 0
            clade.confidence = None

            clade.comment = "&&NHX:S=%s:D=%s:B=%d" % (
                clade.taxon, 'Y' if clade.duplication else 'N', confidence)

    return gene_tree


def get_nhx_tree_with_taxon_info(gene_tree, species_tree_rooted, GeneToSpecies_dict, output_file):
    gene_tree = add_clade_name(gene_tree)
    species_tree_rooted = add_clade_name(species_tree_rooted)

    gene_tree = map_node_species_info(
        gene_tree, species_tree_rooted, GeneToSpecies_dict)
    nhx_tree = get_nhx_comment(gene_tree)

    with open(output_file, 'w') as f:
        Phylo.write(nhx_tree, f, 'newick')


def nhx_comment_parse(comment_string):
    output_dict = {
        "speciation": 0,
        "duplication": 0,
        "confidence": 0,
        "scientific name": None,
    }

    if comment_string == "&&NHX:None":
        return output_dict
    else:
        info_dict = {}
        for info in comment_string.split(":"):
            info = info.split("=")
            if len(info) > 1:
                info_dict[info[0]] = info[1]

        if 'D' in info_dict and info_dict['D'] == 'Y':
            output_dict["duplication"] = 1
            output_dict["speciation"] = 0
        else:
            output_dict["duplication"] = 0
            output_dict["speciation"] = 1

        if 'B' in info_dict:
            output_dict["confidence"] = int(info_dict['B'])

        if 'S' in info_dict:
            output_dict["scientific name"] = info_dict['S']

        return output_dict


def add_nhx_for_node(clade):
    nhx_dict = nhx_comment_parse(clade.comment)
    clade.nhx_dict = nhx_dict

    if "scientific name" in nhx_dict:
        # clade.species = nhx_dict["scientific name"]
        clade.taxon = nhx_dict["scientific name"]
    if "speciation" in nhx_dict:
        clade.speciation = True if nhx_dict["speciation"] else False
    if "duplication" in nhx_dict:
        clade.duplication = True if nhx_dict["duplication"] else False
    if "confidence" in nhx_dict:
        clade.confidence = True if nhx_dict["confidence"] else False

    return clade


def load_nhx_tree(nhx_file):
    try:
        nhx_tree = Phylo.read(nhx_file, 'newick')
        nhx_tree = add_clade_name(nhx_tree)
        nhx_tree_node_dict = lookup_by_names(nhx_tree)

        # for i in gene_tree_node_dict:
        #     if not gene_tree_node_dict[i].is_terminal():
        #         gene_tree_node_dict[i] = add_nhx_for_node(gene_tree_node_dict[i])

        for i in nhx_tree_node_dict:
            nhx_tree_node_dict[i] = add_nhx_for_node(nhx_tree_node_dict[i])

        return nhx_tree, nhx_tree_node_dict
    except:
        raise ValueError(nhx_file)


def get_top_taxon_clade(taxon_labeled_tree, species_tree, taxonomy, node_type=None):
    sp_tree_dict = lookup_by_names(species_tree)
    sp_list = [i.name for i in sp_tree_dict[taxonomy].get_terminals()]

    candi_clade_list = []
    for clade in taxon_labeled_tree.find_clades(order='preorder'):
        good_type = True

        if clade.taxon == taxonomy:
            good_type = False

            if node_type == 'speciation' and hasattr(clade, 'speciation') and clade.speciation:
                good_type = True
            elif node_type == 'duplication' and hasattr(clade, 'duplication') and clade.duplication:
                good_type = True
            elif node_type is None:
                good_type = True

        if good_type and len(set([l.taxon for l in clade.get_terminals()]) - set(sp_list)) == 0:
            candi_clade_list.append(clade)

    top_clade_list = []
    for i in candi_clade_list:
        top_flag = True
        for j in candi_clade_list:
            if is_offspring_of(i, j, taxon_labeled_tree):
                top_flag = False
        if top_flag:
            top_clade_list.append(i)

    return top_clade_list


# plot tree

# draw function fork from biopython

def draw_ascii(raw_tree, file=None, column_width=80, clade_name=False, clade_confidence=False, rename_dict=None):
    """Draw an ascii-art phylogram of the given tree.

    The printed result looks like::

                                        _________ Orange
                         ______________|
                        |              |______________ Tangerine
          ______________|
         |              |          _________________________ Grapefruit
        _|              |_________|
         |                        |______________ Pummelo
         |
         |__________________________________ Apple


    :Parameters:
        file : file-like object
            File handle opened for writing the output drawing. (Default:
            standard output)
        column_width : int
            Total number of text columns used by the drawing.

    """
    if file is None:
        file = sys.stdout

    tree = copy.deepcopy(raw_tree)

    if rename_dict:
        for clade in tree.find_clades(order='postorder'):
            if clade.name and clade.name in rename_dict:
                clade.name = rename_dict[clade.name]

    taxa = tree.get_terminals()
    # Some constants for the drawing calculations
    max_label_width = max(len(str(taxon)) for taxon in taxa)
    drawing_width = column_width - max_label_width - 1
    drawing_height = 2 * len(taxa) - 1

    def get_col_positions(tree):
        """Create a mapping of each clade to its column position."""
        depths = tree.depths()
        # If there are no branch lengths, assume unit branch lengths
        if not max(depths.values()):
            depths = tree.depths(unit_branch_lengths=True)
        # Potential drawing overflow due to rounding -- 1 char per tree layer
        fudge_margin = int(math.ceil(math.log(len(taxa), 2)))
        cols_per_branch_unit = ((drawing_width - fudge_margin) /
                                float(max(depths.values())))
        return dict((clade, int(blen * cols_per_branch_unit + 1.0))
                    for clade, blen in depths.items())

    def get_row_positions(tree):
        positions = dict((taxon, 2 * idx) for idx, taxon in enumerate(taxa))

        def calc_row(clade):
            for subclade in clade:
                if subclade not in positions:
                    calc_row(subclade)
            positions[clade] = ((positions[clade.clades[0]] +
                                 positions[clade.clades[-1]]) // 2)

        calc_row(tree.root)
        return positions

    col_positions = get_col_positions(tree)
    row_positions = get_row_positions(tree)
    char_matrix = [[' ' for x in range(drawing_width)]
                   for y in range(drawing_height)]

    def draw_clade(clade, startcol):
        thiscol = col_positions[clade]
        thisrow = row_positions[clade]
        # Draw a horizontal line
        for col in range(startcol, thiscol):
            char_matrix[thisrow][col] = '_'
        if clade.clades:
            # Draw a vertical line
            toprow = row_positions[clade.clades[0]]
            botrow = row_positions[clade.clades[-1]]
            for row in range(toprow + 1, botrow + 1):
                char_matrix[row][thiscol] = '|'
            # NB: Short terminal branches need something to stop rstrip()
            if (col_positions[clade.clades[0]] - thiscol) < 2:
                char_matrix[toprow][thiscol] = ','

            # add label for clade draw, by xuyuxing
            clade_string = ""
            if clade_name and clade.name:
                clade_string = clade_string + clade.name + ":"
            if clade_confidence and clade.confidence:
                if len(str(clade.confidence)) <= len("%.2e" % clade.confidence):
                    clade_string = clade_string + str(clade.confidence)
                else:
                    clade_string = clade_string + "%.2e" % clade.confidence
            for i in range(len(clade_string)):
                if len(clade.get_terminals()) % 2:
                    char_matrix[thisrow - 1][thiscol + 1 + i] = clade_string[i]
                else:
                    char_matrix[thisrow][thiscol + 1 + i] = clade_string[i]

            # Draw descendents
            for child in clade:
                draw_clade(child, thiscol + 1)

    draw_clade(tree.root, 0)
    # Print the complete drawing
    for idx, row in enumerate(char_matrix):
        line = ''.join(row).rstrip()
        # Add labels for terminal taxa in the right margin
        if idx % 2 == 0:
            line += ' ' + str(taxa[idx // 2])
        file.write(line + '\n')
    file.write('\n')


def normal_tree_rela_coord(tree):
    """
    add an attr named 'rela_coord' to every clade in the tree. The X is the branch value, and the Y is base on leaf number.
    """
    # get X axis aka branch length from root to clade
    tree = add_clade_name(tree)
    tree_name_dir = lookup_by_names(tree, order='preorder')

    for clade_name in tree_name_dir:
        X_clade = get_distance_to_root(tree_name_dir[clade_name], tree)
        tree_name_dir[clade_name].rela_coord = (X_clade, None)

    # get Y axis
    # first for leaf
    order_leaf_list = [
        clade_name for clade_name in tree_name_dir if tree_name_dir[clade_name].is_terminal()]
    for leaf_name in order_leaf_list:
        X_clade, Y_clade = tree_name_dir[leaf_name].rela_coord
        if (X_clade is None) or (not Y_clade is None):
            raise ValueError("somebady make a rela_coord already")
        Y_clade = float(order_leaf_list.index(leaf_name))
        tree_name_dir[leaf_name].rela_coord = (X_clade, Y_clade)

    # for orther clade, we should cal node which close to leaf
    path_for_target_to_most_far_leaf_dict = {}
    for clade_name in tree_name_dir:
        if clade_name in order_leaf_list:
            continue
        else:
            most_far_path = max([get_path_step(leaf_tmp, tree_name_dir[clade_name], tree) for leaf_tmp in
                                 tree_name_dir[clade_name].get_terminals()])
            if most_far_path not in path_for_target_to_most_far_leaf_dict:
                path_for_target_to_most_far_leaf_dict[most_far_path] = []
            path_for_target_to_most_far_leaf_dict[most_far_path].append(
                clade_name)

    for i in sorted(path_for_target_to_most_far_leaf_dict.keys()):
        for clade_name in path_for_target_to_most_far_leaf_dict[i]:
            X_clade, Y_clade = tree_name_dir[clade_name].rela_coord
            son_Y = [son.rela_coord[1] for son in tree_name_dir[clade_name]]
            Y_clade = (max(son_Y) - min(son_Y)) / 2 + min(son_Y)
            tree_name_dir[clade_name].rela_coord = (X_clade, Y_clade)

    return tree


def normal_tree_abs_coord(tree, figure_size):
    tree_name_dict = lookup_by_names(tree)

    tree_clade_rela_coord = {
        clade_name: tree_name_dict[clade_name].rela_coord for clade_name in tree_name_dict}
    rela_x_list = [x for x, y in tree_clade_rela_coord.values()]
    rela_y_list = [y for x, y in tree_clade_rela_coord.values()]
    rela_fig_size = (min(rela_x_list), max(rela_x_list),
                     min(rela_y_list), max(rela_y_list))

    tree_clade_abs_coord = {
        clade_name: scale_to_give_size(tree_clade_rela_coord[clade_name], figure_size, rela_fig_size) for clade_name in
        tree_clade_rela_coord}

    for clade_name in tree_name_dict:
        tree_name_dict[clade_name].abs_coord = tree_clade_abs_coord[clade_name]

    return tree


def draw_tree(ax, tree):
    tree_name_dict = lookup_by_names(tree, 'level')
    for clade_name in tree_name_dict:
        clade_tmp = tree_name_dict[clade_name]
        son_clade = clade_tmp.clades
        son_y = []
        for son_clade_tmp in son_clade:
            line_segment_plot(ax, (son_clade_tmp.abs_coord[0], son_clade_tmp.abs_coord[1]),
                              (clade_tmp.abs_coord[0], son_clade_tmp.abs_coord[1]))
            son_y.append(son_clade_tmp.abs_coord[1])
        if not clade_tmp.is_terminal():
            line_segment_plot(ax, (clade_tmp.abs_coord[0], min(
                son_y)), (clade_tmp.abs_coord[0], max(son_y)))


# #########################3
#
# def get_speci_id(seq_id):
#     return re.findall(r'^(\d+)\_.*', seq_id)[0]
#
#
# def orthofinder_find_root(gene_tree, speci_tree):
#     """
#     https://www.biorxiv.org/content/biorxiv/early/2019/04/24/466201.full.pdf
#     """
#     pass
#
#
# def get_node_from_target_to_leaf(target_node, leaf):
#     if target_node not in leaf.get_ancestors():
#         raise ValueError("target node is not an ancestor of leaf")
#     output_list = []
#     for i in leaf.get_ancestors():
#         if i == target_node:
#             break
#         output_list.append(i)
#     return output_list
#
#
# def get_node_depth(node, ignore_pass_node):
#     """
#     given a node return the depth of this node, leaf is -1, end node is 0
#     """
#
#     # tmp_dir = {}
#     # for leaves in node.get_leaves():
#     #    tmp_dir[leaves.name]=[tmp_anc for tmp_anc in get_node_from_target_to_leaf(node,leaves) if not pass_node(tmp_anc)]
#
#     if node.is_leaf():
#         return -1
#     else:
#         if ignore_pass_node:
#             return max(
#                 [len([tmp_anc for tmp_anc in get_node_from_target_to_leaf(node, leaves) if not pass_node(tmp_anc)]) for
#                  leaves in node.get_leaves()])
#         else:
#             return max(
#                 [len([tmp_anc for tmp_anc in get_node_from_target_to_leaf(node, leaves)]) for
#                  leaves in node.get_leaves()])
#
#
# if __name__ == '__main__':
#     tree_file = '/lustre/home/xuyuxing/tmp/tree14.tre'
#     tree = Phylo.read(tree_file, "newick")
#     tree = add_clade_name(tree)
#     node_dict = lookup_by_names(tree)
#
#     import pickle
#     import sys
#
#     sys.path.extend(['/lustre/home/xuyuxing/python_project/Genome_work_tools'])
#
#     import argparse
#
#     ###### argument parse
#     parser = argparse.ArgumentParser(
#         prog='PhylTools',
#     )
#
#     subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")
#
#     # argparse for get_close_node_info
#     parser_a = subparsers.add_parser('get_close_node_info',
#                                      help='build a protein gene tree from raw sequence',
#                                      description='build a protein gene tree from raw sequence')
#
#     parser_a.add_argument('tree_file', type=str, help='Path of raw protein sequences')
#     parser_a.add_argument('target_speci', type=str, help='Path of raw protein sequences')
#     parser_a.add_argument('taxon_info', type=str, help='Path of raw protein sequences')
#     parser_a.add_argument('taxonomy_dir', type=str, help='Path of raw protein sequences')
#     parser_a.add_argument('taxon_lineage_file', type=str, help='Path of raw protein sequences')
#
#     args = parser.parse_args()
#     args_dict = vars(args)
#
#     # taxon_info = "/lustre/home/xuyuxing/Work/Balanophora/orthofinder/pep2/OrthoFinder/Results_Sep05/WorkingDirectory/tmp/taxon_vs_ortho"
#     # tree_file = "/lustre/home/xuyuxing/Work/Balanophora/orthofinder/pep2/OrthoFinder/Results_Sep05/WorkingDirectory/tmp/OG0000443_tree_id.txt"
#     # taxonomy_dir = "/lustre/home/xuyuxing/Database/genome/info/NCBI/taxonomy"
#     # taxon_lineage_file = "/lustre/home/xuyuxing/Work/Balanophora/orthofinder/pep2/OrthoFinder/Results_Sep05/WorkingDirectory/tmp/lineage.pyb"
#     # target_speci = "15"
#
#     if args_dict["subcommand_name"] == "get_close_node_info":
#
#         from toolbiox.lib.common.fileIO import tsv_file_dict_parse
#
#         tax_info_dict = tsv_file_dict_parse(args.taxon_info, fieldnames=["taxon_id", "speci_ID"], key_col="speci_ID",
#                                             seq=",")
#         tree = Phylo.read(args.tree_file, "newick")
#         tree, node_dict = mid_unrooted_tree(tree)
#
#         leaf_dict = {}
#         leaf_speci_hash = {}
#         for leaf in tree.get_terminals():
#             speci_id = get_speci_id(leaf.name)
#             leaf_speci_hash[leaf.name] = speci_id
#             if speci_id not in leaf_dict:
#                 leaf_dict[speci_id] = []
#             leaf_dict[speci_id].append(leaf.name)
#
#         target_leaf = []
#         for leaf in tree.get_terminals():
#             if leaf_speci_hash[leaf.name] == args.target_speci:
#                 target_leaf.append(leaf.name)
#
#         # from toolbiox.lib.resource.ncbi_taxonomy import build_taxon_database
#         #
#         # tax_record_dict = build_taxon_database(taxonomy_dir)
#         #
#         # lineage_dict = {}
#         # for speci_id in leaf_dict:
#         #     taxon_record = tax_record_dict[tax_info_dict[speci_id]['taxon_id']]
#         #     lineage = taxon_record.get_lineage(tax_record_dict)
#         #     lineage_dict[speci_id] = lineage
#         #
#         # OUT = open(taxon_lineage_file, 'wb')
#         # pickle.dump(lineage_dict, OUT)
#         # OUT.close()
#
#         TEMP = open(args.taxon_lineage_file, 'rb')
#         lineage_dict = pickle.load(TEMP)
#         TEMP.close()
#
#
#         def get_close_node_without_same_speci(tree, child_node, leaf_speci_hash, target_speci):
#             parent_node = get_parent(child_node, tree)
#             close_node_leaf = [leaf.name for leaf in parent_node.get_terminals() if
#                                leaf_speci_hash[leaf.name] != target_speci]
#             if len(close_node_leaf) == 0 and parent_node != tree:
#                 return get_close_node_without_same_speci(tree, parent_node, leaf_speci_hash, target_speci)
#             else:
#                 return parent_node
#
#
#         def common_lineage(lineage_list):
#             if len(lineage_list) == 1:
#                 return lineage_list[0][-1]
#
#             common_taxon = set(lineage_list[0])
#             for i in lineage_list:
#                 common_taxon = set(i) & common_taxon
#
#             a = []
#             for i in lineage_list[0]:
#                 if not i in common_taxon:
#                     return a[-1]
#                 else:
#                     a.append(i)
#
#
#         for leaf_name in leaf_dict[args.target_speci]:
#             close_node = get_close_node_without_same_speci(tree, node_dict[leaf_name], leaf_speci_hash,
#                                                            args.target_speci)
#             close_taxon = common_lineage(
#                 [lineage_dict[get_speci_id(leaf.name)] for leaf in close_node.get_terminals() if
#                  leaf_speci_hash[leaf.name] != args.target_speci])
#             print(args.tree_file, leaf_name, close_node.name, close_taxon[0], close_taxon[1], close_node.confidence)

# for binary tree


class BinaryTreeNode(Clade):
    def __init__(
        self,
        branch_length=None,
        name=None,
        left=None,
        right=None,
        confidence=None,
        color=None,
        width=None,
    ):
        """Define parameters for the BinaryTreeNode Clade."""
        if left is None and right is None:
            clades = None
        else:
            clades = [left, right]
        super(BinaryTreeNode, self).__init__(
            branch_length=branch_length,
            name=name,
            clades=clades,
            confidence=confidence,
            color=color,
            width=width,
        )

        self.left = left
        self.right = right


def normalCalde2BinaryTreeNode(clade):
    if clade.is_terminal():
        return BinaryTreeNode(clade.branch_length, clade.name, None, None, clade.confidence, clade.color, clade.width)
    elif len(clade.clades) == 2:
        left = normalCalde2BinaryTreeNode(clade.clades[0])
        right = normalCalde2BinaryTreeNode(clade.clades[1])
        return BinaryTreeNode(clade.branch_length, clade.name, left, right, clade.confidence, clade.color, clade.width)
    else:
        raise ValueError("clade is not good to be a Binary clade")


def Tree2BinaryTree(tree):
    tree_now = copy.deepcopy(tree)

    tree_clade = tree_now.clade
    BT_clade = normalCalde2BinaryTreeNode(tree_clade)

    new_tree = Tree(BT_clade, tree_now.rooted)

    return new_tree


def allPossibleFBT(N):
    """
    get all possible full binary tree structure, left or right will be treat as difference

    N: all node number, 2 * leaf -1
    return: a list of BinaryTreeNode
    """

    if N == 1:
        return [BinaryTreeNode()]
    res = []

    for i in range(1, N, 2):
        for left in allPossibleFBT(i):
            for right in allPossibleFBT(N-i-1):
                node = BinaryTreeNode(left=left, right=right)
                res.append(node)

    return res


def equalBT(BT1, BT2):
    if BT1.left is None and BT1.right is None and BT2.left is None and BT2.right is None:
        if BT1.name == BT2.name:
            return True
    elif BT1.left is not None and BT1.right is not None and BT2.left is not None and BT2.right is not None:
        if (equalBT(BT1.left, BT2.left) and equalBT(BT1.right, BT2.right)) or (equalBT(BT1.left, BT2.right) and equalBT(BT1.right, BT2.left)):
            return True

    return False


def equalBTtree(BT1, BT2):
    return equalBT(BT1.clade, BT2.clade)


def get_newick(tree):
    f = StringIO()
    Phylo.write(tree, f, 'newick')
    string_tmp = f.getvalue()
    f.close()
    return string_tmp


def merge_same_binary_tree(BT_list):
    edge_list = []
    for i in BT_list:
        for j in BT_list:
            if equalBTtree(i, j):
                edge_list.append((i, j))

    G = nx.Graph()
    G.add_nodes_from(BT_list)
    G.add_edges_from(edge_list)

    output_list = []
    for sub_graph in (G.subgraph(c) for c in nx.connected_components(G)):
        output_list.append(list(sub_graph.nodes))

    return output_list


def all_possible_tree(leaf_list):
    node_num = len(leaf_list) * 2 - 1
    tree_structure_list = [i[0]
                           for i in merge_same_binary_tree(allPossibleFBT(node_num))]

    renamed_tree_list = []
    for tree_structure in tree_structure_list:

        for leaf_order in permutations(leaf_list):
            tree_now = copy.deepcopy(tree_structure)

            num = 0
            for clade in tree_now.find_clades(order='preorder'):
                if clade.is_terminal():
                    # print(num)
                    clade.name = leaf_order[num]
                    num += 1

            renamed_tree_list.append(tree_now)

    renamed_tree_list = [i[0]
                         for i in merge_same_binary_tree(renamed_tree_list)]

    return renamed_tree_list


def gene_loss_model_test(full_model_gene_tree, gene_species_map_dict):
    """
    if we have a gene tree model, but may gene loss will change the topologist of the tree. so test if how many possible case when gene loss

    from io import StringIO
    full_tree_string = "(((Gel_a1,Gel_a2)B1,(Ash_a1,Ash_a2)C1)S1,((Gel_b1,Gel_b2)B2,(Ash_b1,Ash_b2)C2)S2)A,Aco"

    full_model_gene_tree = Phylo.read(StringIO(full_tree_string), 'newick')

    gene_species_map_dict = {
        'Gel_a1': 'Gel',
        'Gel_a2': 'Gel',
        'Gel_b1': 'Gel',
        'Gel_b2': 'Gel',
        'Ash_a1': 'Ash',
        'Ash_a2': 'Ash',
        'Ash_b1': 'Ash',
        'Ash_b2': 'Ash',
    }

    gene not in gene_species_map_dict will not loss

    """

    may_loss_gene_list = gene_species_map_dict.keys()

    keep_case_dict = {}
    num = 0
    for i in range(1, len(may_loss_gene_list)+1):
        for keep_case in combinations(may_loss_gene_list, i):
            keep_case_dict[num] = {
                'keep_gene': keep_case,
                'lost_gene': list(set(may_loss_gene_list) - set(keep_case)),
            }
            num += 1

    # get gene loss tree
    for id_tmp in keep_case_dict:
        lost_gene_id = keep_case_dict[id_tmp]['lost_gene']
        gene_loss_tree = remove_given_node_from_tree(
            full_model_gene_tree, lost_gene_id)
        gene_loss_tree = remove_tree_node_name(gene_loss_tree)
        gene_loss_tree = clade_rename(gene_loss_tree, gene_species_map_dict)
        gene_loss_tree = Tree2BinaryTree(gene_loss_tree)
        keep_case_dict[id_tmp]['BT_tree'] = gene_loss_tree

    # merge
    BT_list = [keep_case_dict[i]['BT_tree'] for i in keep_case_dict]
    uniq_BT_list = [i[0] for i in merge_same_binary_tree(BT_list)]

    uniq_BT_dict = {}
    for uniq_BT in uniq_BT_list:
        uniq_BT_dict[uniq_BT] = []
        for id_tmp in keep_case_dict:
            gene_loss_tree = keep_case_dict[id_tmp]['BT_tree']
            if equalBTtree(uniq_BT, gene_loss_tree):
                uniq_BT_dict[uniq_BT].append(id_tmp)

    return keep_case_dict, uniq_BT_dict


if __name__ == '__main__':
    gene_tree_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/Orthologues_Apr11/WorkingDirectory/Trees_ids/OG0000532_tree_id.txt'
    species_rooted_tree_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/Orthologues_Apr11/SpeciesTree_rooted.id.txt'

    # reads a tree file
    gene_tree = Phylo.read(gene_tree_file, 'newick')
    gene_tree = add_clade_name(gene_tree)
    gene_tree_node_dict = lookup_by_names(gene_tree)

    species_rooted_tree = Phylo.read(species_rooted_tree_file, 'newick')

    # get all leaf
    leaf_name_list = [leaf.name for leaf in gene_tree.get_terminals()]

    gene_to_species_map = {'1_7601': '1', '8_15565': '8', '1_16489': '1', '8_8464': '8', '9_13535': '9', '6_10585': '6',
                           '2_11400': '2', '5_10489': '5', '4_30192': '4', '5_24848': '5', '6_28832': '6',
                           '2_18137': '2', '4_9871': '4', '5_294': '5', '4_9272': '4', '5_24710': '5', '4_9271': '4',
                           '0_26868': '0', '3_2604': '3', '7_24217': '7', '1_9240': '1', '9_19573': '9', '8_12531': '8',
                           '6_14246': '6', '4_20069': '4', '5_23488': '5', '4_15038': '4', '5_3351': '5', '2_9356': '2',
                           '6_7876': '6', '4_23206': '4', '5_41654': '5', '4_43364': '4', '2_12645': '2',
                           '4_23207': '4', '5_4308': '5', '0_3911': '0', '0_13321': '0', '3_8434': '3', '7_5793': '7'}

    # root gene tree by species info
    best_root_clade = get_root_by_species(
        gene_tree, species_rooted_tree, gene_to_species_map)

    gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(gene_tree,
                                                                                                            gene_tree_node_dict,
                                                                                                            best_root_clade.name,
                                                                                                            True)

    # draw a tree
    from io import StringIO

    # normal tree
    tree_string = "(((Orange:0.1,Tangerine:0.2):0.3,(Grapefruit:0.4,Pummelo:0.2):0.1):0.2,Apple:0.6)"
    # tree with comment
    tree_string = "(((Orange:0.1,Tangerine:0.2):0.3[50],(Grapefruit:0.4,Pummelo:0.2):0.1[50]):0.2[60],Apple:0.6)"
    # tree with confidence
    tree_string = "(((Orange:0.1,Tangerine:0.2)50:0.3,(Grapefruit:0.4,Pummelo:0.2)50:0.1)60:0.2,Apple:0.6)"
    tree = Phylo.read(StringIO(tree_string), 'newick')

    draw_ascii(tree)

    # work with nhx tree file
    from toolbiox.lib.common.fileIO import tsv_file_dict_parse

    normal_gene_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics_old/tree/fasttree/OG0002678/tree.phb"
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/species.tree.txt"
    rename_map = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics_old/tree/fasttree/OG0002678/rename.map"

    gene_tree = Phylo.read(normal_gene_tree_file, 'newick')
    gene_tree = add_clade_name(gene_tree)
    species_tree = Phylo.read(species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)

    tmp_info = tsv_file_dict_parse(rename_map, fieldnames=[
                                   'new_id', 'old_id', 'speci'], key_col='new_id')
    gene_to_species_map_dict = {i: tmp_info[i]["speci"] for i in tmp_info}

    rooted_gene_tree = get_rooted_tree_by_species_tree(
        gene_tree, species_tree, gene_to_species_map_dict)
    rooted_taxon_gene_tree = map_node_species_info(
        rooted_gene_tree, species_tree, gene_to_species_map_dict)

    nhx_tree = get_nhx_comment(rooted_taxon_gene_tree)

    nhx_file = '/lustre/home/xuyuxing/temp/best.nhx'
    nhx_tree, clade_dict = load_nhx_tree(nhx_file)

    for clade_name in clade_dict:
        clade = clade_dict[clade_name]
        if not clade.is_terminal():
            print(clade.name, clade.nhx_dict['Duplications'])

    # get all possible tree
    leaf_list = ['Gel_a1', 'Gel_a2', 'Ash_a1', 'Ash_a2']
    tree_list = all_possible_tree(leaf_list)

    num = 0
    for i in tree_list:
        print(num)
        num += 1
        Phylo.draw_ascii(i)

    # get all possible tree
    leaf_list = ['Gel', 'Gel', 'Ash', 'Ash']
    tree_list = all_possible_tree(leaf_list)

    num = 0
    for i in tree_list:
        print(num)
        num += 1
        Phylo.draw_ascii(i)

    # gene loss tree
    from io import StringIO
    full_tree_string = "(((Gel_a1,Gel_a2)B1,(Ash_a1,Ash_a2)C1)S1,((Gel_b1,Gel_b2)B2,(Ash_b1,Ash_b2)C2)S2)A,Aco"

    tree = Phylo.read(StringIO(full_tree_string), 'newick')
    draw_ascii(tree, clade_name=True)

    """
                                                     _________________ Gel_a1
                                    ________________|B1:
                                   |                |_________________ Gel_a2
                   ________________|S1:
                  |                |                 _________________ Ash_a1
                  |                |________________|C1:
                  |                                 |_________________ Ash_a2
  ________________|A:
 |                |                                  _________________ Gel_b1
 |                |                 ________________|B2:
 |                |                |                |_________________ Gel_b2
_|                |________________|S2:
 |                                 |                 _________________ Ash_b1
 |                                 |________________|C2:
 |                                                  |_________________ Ash_b2
 |
 |________________ Aco
    
    
    """

    gene_species_map_dict = {
        'Gel_a1': 'Gel',
        'Gel_a2': 'Gel',
        'Gel_b1': 'Gel',
        'Gel_b2': 'Gel',
        'Ash_a1': 'Ash',
        'Ash_a2': 'Ash',
        'Ash_b1': 'Ash',
        'Ash_b2': 'Ash',
    }

    keep_case_dict, uniq_BT_dict = gene_loss_model_test(
        tree, gene_species_map_dict)

    Phylo.draw(tree)

    from Bio.AlignIO import NexusIO

    from Bio import SeqIO

    from Bio.SeqIO import parse

    #

    