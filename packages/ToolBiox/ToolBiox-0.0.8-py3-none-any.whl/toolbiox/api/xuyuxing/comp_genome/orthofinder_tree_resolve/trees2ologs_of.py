# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 09:11:11 2017
@author: david
Perform directed 'reconciliation' first and then apply EggNOG method
1 - root gene trees on outgroup: unique one this time
2 - infer orthologues
"""
import os
import sys
import csv
import glob
import argparse
import operator
import itertools
import multiprocessing as mp
from collections import defaultdict, deque

from . import tree as tree_lib
from . import resolve
try:
    import queue
except ImportError:
    import Queue as queue

PY2 = sys.version_info <= (3,)
csv_write_mode = 'wb' if PY2 else 'wt'
csv_append_mode = 'ab' if PY2 else 'at'
csv_read_mode = 'rb' if PY2 else 'rt'

debug = False   # HOGs

if not PY2:
    xrange = range


def GeneToSpecies_dash(g):
    return g.split("_", 1)[0]


OrthoFinderIDs = GeneToSpecies_dash


def GeneToSpecies_secondDash(g):
    return "_".join(g.split("_", 2)[:2])


def GeneToSpecies_3rdDash(g):
    return "_".join(g.split("_", 3)[:3])


def GeneToSpecies_dot(g):
    return g.split(".", 1)[0]


def GeneToSpecies_hyphen(g):
    return g.split("-", 1)[0]


def SpeciesAndGene_dash(g):
    return g.split("_", 1)


def SpeciesAndGene_secondDash(g):
    a, b, c = g.split("_", 2)
    return (a+"_"+b, c)


def SpeciesAndGene_3rdDash(g):
    a, b, c, d = g.split("_", 3)
    return (a+"_"+b+"_"+c, d)


def SpeciesAndGene_dot(g):
    return g.split(".", 1)


def SpeciesAndGene_hyphen(g):
    return g.split("-", 1)


SpeciesAndGene_lookup = {GeneToSpecies_dash: SpeciesAndGene_dash,
                         GeneToSpecies_secondDash: SpeciesAndGene_secondDash,
                         GeneToSpecies_3rdDash: SpeciesAndGene_3rdDash,
                         GeneToSpecies_dot: SpeciesAndGene_dot,
                         GeneToSpecies_hyphen: SpeciesAndGene_hyphen}


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
    for node in t.traverse('postorder'):
        if node.is_leaf():
            node.add_feature(tag_down, {GeneMap(node.name)})
        elif node.is_root():
            continue
        else:
            node.add_feature(tag_down, set.union(
                *[ch.__getattribute__(tag_down) for ch in node.get_children()]))
    for node in t.traverse('preorder'):
        if node.is_root():
            node.add_feature(tag_up, set())
        else:
            parent = node.up
            if parent.is_root():
                others = [ch for ch in parent.get_children() if ch != node]
                node.add_feature(tag_up, set.union(
                    *[other.__getattribute__(tag_down) for other in others]))
            else:
                others = [ch for ch in parent.get_children() if ch != node]
                sp_downs = set.union(
                    *[other.__getattribute__(tag_down) for other in others])
                node.add_feature(tag_up, parent.__getattribute__(
                    tag_up).union(sp_downs))
    t.add_feature(tag_down, set.union(
        *[ch.__getattribute__(tag_down) for ch in t.get_children()]))


"""
HOGs
-------------------------------------------------------------------------------
"""


def MRCA_node(t_rooted, taxa):
    return (t_rooted & next(taxon for taxon in taxa)) if len(taxa) == 1 else t_rooted.get_common_ancestor(taxa)


def GetHOGs_from_tree(iog, tree, hog_writer, lock_hogs, q_split_paralogous_clades):
    og_name = "OG%07d" % iog
    if debug:
        print("\n===== %s =====" % og_name)
    try:
        tree = hog_writer.mark_dups_below(tree)
        cached_hogs = []
        for n in tree.traverse("preorder"):
            cached_hogs.extend(hog_writer.write_clade_v2(
                n, og_name, q_split_paralogous_clades))
        hog_writer.WriteCachedHOGs(cached_hogs, lock_hogs)
    except:
        print("WARNING: HOG analysis for %s failed" % og_name)
        print("Please report to https://github.com/davidemms/OrthoFinder/issues including \
SpeciesTree_rooted_ids.txt and Trees_ids/%s_tree_id.txt from WorkingDirectory/" % og_name)
        print(cached_hogs)
        raise


def get_highest_nodes(nodes, comp_nodes):
    """
    Returns the nodes closest to the root
    Args:
        nodes - the list of nodes to examine
        comp_nodes - dict:NX -> ( {closer to root}, {further from root} )
    """
    return {n for n in nodes if not any(n in comp_nodes[n2][1] for n2 in nodes)}


def get_comparable_nodes(sp_tree):
    """
    Return a dictionary of comaprable nodes
    Node NX < NY if NX is on the path between NY and the root.
    If a node is not <, =, > another then they are incomparable
    Args:
        sp_tree - sp_tree with labelled nodes
    Returns:
        comp_nodes - dict:NX -> ( {n|n<NX}, {n|n>NX} ) i.e. (higher_nodes, lower_nodes)
    """
    comp_nodes = dict()
    for n in sp_tree.traverse('postorder'):
        nodes_below = set()
        if not n.is_leaf():
            for ch in n.get_children():
                if not ch.is_leaf():
                    nodes_below.update(ch.nodes_below)
                nodes_below.add(ch.name)
        above = set([nn.name for nn in n.get_ancestors()])
        n.add_feature('nodes_below', nodes_below)
        comp_nodes[n.name] = (above, nodes_below, above.union(
            nodes_below.union(set(n.name))))
    return comp_nodes


"""
Orthologs
-------------------------------------------------------------------------------
"""


def OutgroupIngroupSeparationScore(sp_up, sp_down, sett1, sett2, N_recip, n1, n2):
    f_dup = len(sp_up.intersection(sett1)) * len(sp_up.intersection(sett2)) * \
        len(sp_down.intersection(sett1)) * \
        len(sp_down.intersection(sett2)) * N_recip
    f_a = len(sp_up.intersection(sett1)) * (n2-len(sp_up.intersection(sett2))) * \
        (n1-len(sp_down.intersection(sett1))) * \
        len(sp_down.intersection(sett2)) * N_recip
    f_b = (n1-len(sp_up.intersection(sett1))) * len(sp_up.intersection(sett2)) * \
        len(sp_down.intersection(sett1)) * \
        (n2-len(sp_down.intersection(sett2))) * N_recip
    choice = (f_dup, f_a, f_b)
    return max(choice)


def GetRoots(tree, species_tree_rooted, GeneToSpecies):
    """
    Allow non-binary gene or species trees.
    (A,B,C) => consider splits A|BC, B|AC, C|AB - this applies to gene and species tree
    If a clean ingroup/outgroup split cannot be found then score root by geometric mean of fraction of expected species actually 
    observed for the two splits
    """
    speciesObserved = set([GeneToSpecies(g) for g in tree.get_leaf_names()])
    if len(speciesObserved) == 1:
        # arbitrary root if all genes are from the same species
        return [next(n for n in tree)]

    # use species tree to find correct outgroup according to what species are present in the gene tree
    n = species_tree_rooted
    children = n.get_children()
    leaves = [set(ch.get_leaf_names()) for ch in children]
    have = [len(l.intersection(speciesObserved)) != 0 for l in leaves]
    while sum(have) < 2:
        n = children[have.index(True)]
        children = n.get_children()
        leaves = [set(ch.get_leaf_names()) for ch in children]
        have = [len(l.intersection(speciesObserved)) != 0 for l in leaves]

    # Get splits to look for
    roots_list = []
    scores_list = []   # the fraction completeness of the two clades
#    roots_set = set()
    for i in xrange(len(leaves)):
        t1 = leaves[i]
        t2 = set.union(*[l for j, l in enumerate(leaves) if j != i])
        # G - set of species in gene tree
        # First relevant split in species tree is (A,B), such that A \cap G \neq \emptyset and A \cap G \neq \emptyset
        # label all nodes in gene tree according the whether subsets of A, B or both lie below node
        StoreSpeciesSets(tree, GeneToSpecies)   # sets of species
        root_mapper = RootMap(t1, t2, GeneToSpecies)
        sett1 = set(t1)
        sett2 = set(t2)
        nt1 = float(len(t1))
        nt2 = float(len(t2))
        N_recip = 1./(nt1*nt1*nt2*nt2)
        GeneMap = root_mapper.GeneMap
        # ingroup/outgroup identification
        StoreSpeciesSets(tree, GeneMap, "inout_")
        # find all possible locations in the gene tree at which the root should be

        T = {True, }
        F = {False, }
        TF = set([True, False])
        for m in tree.traverse('postorder'):
            if m.is_leaf():
                if len(m.inout_up) == 1 and m.inout_up != m.inout_down:
                    # this is the unique root
                    return [m]
            else:
                if len(m.inout_up) == 1 and len(m.inout_down) == 1 and m.inout_up != m.inout_down:
                    # this is the unique root
                    return [m]
                nodes = m.get_children() if m.is_root() else [
                    m] + m.get_children()
                clades = [ch.inout_down for ch in nodes] if m.is_root() else (
                    [m.inout_up] + [ch.inout_down for ch in m.get_children()])
                # do we have the situation A | B or (A,B),S?
                if len(nodes) == 3:
                    if all([len(c) == 1 for c in clades]) and T in clades and F in clades:
                        # unique root
                        if clades.count(T) == 1:
                            return [nodes[clades.index(T)]]
                        else:
                            return [nodes[clades.index(F)]]
                    elif T in clades and F in clades:
                        #AB-(A,B) or B-(AB,A)
                        ab = [c == TF for c in clades]
                        i = ab.index(True)
                        roots_list.append(nodes[i])
                        sp_down = nodes[i].sp_down
                        sp_up = nodes[i].sp_up
#                        print(m)
                        scores_list.append(OutgroupIngroupSeparationScore(
                            sp_up, sp_down, sett1, sett2, N_recip, nt1, nt2))
                    elif clades.count(TF) >= 2:
                        # (A,A,A)-excluded, (A,A,AB)-ignore as want A to be bigest without including B, (A,AB,AB), (AB,AB,AB)
                        i = 0
                        roots_list.append(nodes[i])
                        sp_down = nodes[i].sp_down
                        sp_up = nodes[i].sp_up
#                        print(m)
                        scores_list.append(OutgroupIngroupSeparationScore(
                            sp_up, sp_down, sett1, sett2, N_recip, nt1, nt2))
                elif T in clades and F in clades:
                    roots_list.append(m)
                    scores_list.append(0)  # last choice
    # If we haven't found a unique root then use the scores for completeness of ingroup/outgroup to root
    if len(roots_list) == 0:
        return []  # This shouldn't occur
    return [sorted(zip(scores_list, roots_list), key=lambda x: x[0], reverse=True)[0][1]]


def WriteQfO2(orthologues_list_pairs_list, outfilename, qAppend=True):
    """ takes a list where each entry is a pair, (genes1, genes2), which are orthologues of one another
    """
    with open(outfilename, 'a' if qAppend else 'w') as outfile:
        for gs1, gs2, _, _ in orthologues_list_pairs_list:
            for sp1, genes1 in gs1.items():
                for sp2, genes2 in gs2.items():
                    for g1 in genes1:
                        for g2 in genes2:
                            outfile.write("%s_%s\t%s_%s\n" %
                                          (sp1, g1, sp2, g2))


def GetGeneToSpeciesMap(args):
    GeneToSpecies = GeneToSpecies_dash
    if args.separator and args.separator == "dot":
        GeneToSpecies = GeneToSpecies_dot
    elif args.separator and args.separator == "second_dash":
        GeneToSpecies = GeneToSpecies_secondDash
    elif args.separator and args.separator == "3rd_dash":
        GeneToSpecies = GeneToSpecies_3rdDash
    elif args.separator and args.separator == "hyphen":
        GeneToSpecies = GeneToSpecies_hyphen
    return GeneToSpecies


def OverlapSize(node, GeneToSpecies, suspect_genes):
    descendents = [{GeneToSpecies(l) for l in n.get_leaf_names()}.difference(
        suspect_genes) for n in node.get_children()]
    intersection = descendents[0].intersection(descendents[1])
    return len(intersection), intersection, descendents[0], descendents[1]


def ResolveOverlap(overlap, sp0, sp1, ch, tree, neighbours, GeneToSpecies, relOverlapCutoff=4):
    """
    Is an overlap suspicious and if so can it be resolved by identifying genes that are out of place?
    Args:
        overlap - the species with genes in both clades
        sp0 - the species below ch[0]
        sp1 - the species below ch[1]
        ch - the two child nodes
        tree - the gene tree
        neighbours - dictionary species->neighbours, where neighbours is a list of the sets of species observed at successive topological distances from the species
    Returns:
        qSuccess - has the overlap been resolved
        genes_removed - the out-of-place genes that have been removed so as to resolve the overlap

    Implementation:
        - The number of species in the overlap must be a 5th or less of the number of species in each clade - What if it's a single gene that's out of place? Won't make a difference then to the orthologs!
        - for each species with genes in both clades: the genes in one clade must all be more out of place (according to the 
          species tree) than all the gene from that species in the other tree
    """
    oSize = len(overlap)
    lsp0 = len(sp0)
    lsp1 = len(sp1)
    if (oSize == lsp0 or oSize == lsp1) or (relOverlapCutoff*oSize >= lsp0 and relOverlapCutoff*oSize >= lsp1):
        return False, []
    # The overlap looks suspect, misplaced genes?
    # for each species, we'd need to be able to determine that all genes from A or all genes from B are misplaced
    genes_removed = []
    nA_removed = 0
    nB_removed = 0
    qResolved = True
    for sp in overlap:
        A = [g for g in ch[0].get_leaf_names() if GeneToSpecies(g) == sp]
        B = [g for g in ch[1].get_leaf_names() if GeneToSpecies(g) == sp]
        A_levels = []
        B_levels = []
        for X, level in zip((A, B), (A_levels, B_levels)):
            for g in X:
                gene_node = tree & g
                r = gene_node.up
                nextSpecies = set([GeneToSpecies(gg)
                                   for gg in r.get_leaf_names()])
                # having a gene from the same species isn't enough?? No, but we add to the count I think.
                while len(nextSpecies) == 1:
                    r = r.up
                    nextSpecies = set([GeneToSpecies(gg)
                                       for gg in r.get_leaf_names()])
                nextSpecies.remove(sp)
                # get the level
                # the sum of the closest and furthest expected distance topological distance for the closest genes in the gene tree (based on species tree topology)
                neigh = neighbours[sp]
                observed = [neigh[nSp] for nSp in nextSpecies]
                level.append(min(observed) + max(observed))
        # if the clade is one step up the tree further way (min=max) then this gives +2. There's no way this is a problem
        qRemoveA = max(B_levels) + 2 < min(A_levels)
        qRemoveB = max(A_levels) + 2 < min(B_levels)
        if qRemoveA and relOverlapCutoff*oSize < len(sp0):
            nA_removed += len(A_levels)
            genes_removed.extend(A)
        elif qRemoveB and relOverlapCutoff*oSize < len(sp1):
            nB_removed += len(B_levels)
            genes_removed.extend(B)
        else:
            qResolved = False
            break
    if qResolved:
        return True, set(genes_removed)
    else:
        return False, set()


def GetRoot(tree, species_tree_rooted, GeneToSpecies):
    roots = GetRoots(tree, species_tree_rooted, GeneToSpecies)
    if len(roots) > 0:
        root_dists = [r.get_closest_leaf()[1] for r in roots]
        i, _ = max(enumerate(root_dists), key=operator.itemgetter(1))
        return roots[i]
    else:
        return None  # single species tree


def CheckAndRootTree(treeFN, species_tree_rooted, GeneToSpecies):
    """
    Check that the tree can be analysed and rooted
    Root tree
    Returns None if this fails, i.e. checks: exists, has more than one gene, can be rooted
    """
    # if (not os.path.exists(treeFN)) or os.stat(treeFN).st_size == 0:
    #     return None, False
    qHaveSupport = False
    try:
        tree = tree_lib.Tree(treeFN, format=2)
        qHaveSupport = True
    except:
        try:
            tree = tree_lib.Tree(treeFN)
        except:
            tree = tree_lib.Tree(treeFN, format=3)
    if len(tree) == 1:
        return None, False
    root = GetRoot(tree, species_tree_rooted, GeneToSpecies)
    if root == None:
        return None, False
    # Pick the first root for now
    if root != tree:
        tree.set_outgroup(root)
    return tree, qHaveSupport


def Orthologs_and_Suspect(ch, suspect_genes, misplaced_genes, SpeciesAndGene):
    """
    ch - the two child nodes that are orthologous
    suspect_genes - genes already identified as misplaced at lower levels
    misplaced_genes - genes identified as misplaced at this level
    Returns the tuple (o_0, o_1, os_0, os_1) where each element is a dictionary from species to genes from that species,
    the o are orthologs, the os are 'suspect' orthologs because the gene was previously identified as suspect
    """
    d = [defaultdict(list) for _ in range(2)]
    d_sus = [defaultdict(list) for _ in range(2)]
    for node, di, d_susi in zip(ch, d, d_sus):
        for g in [g for g in node.get_leaf_names() if g not in misplaced_genes]:
            sp, seq = SpeciesAndGene(g)
            if g in suspect_genes:
                d_susi[sp].append(seq)
            else:
                di[sp].append(seq)
    return d[0], d[1], d_sus[0], d_sus[1]


def GetOrthologues_from_tree(iog, tree, species_tree_rooted, GeneToSpecies, neighbours,
                             q_get_dups=False, qNoRecon=False):
    """ 
    Returns:
        orthologues 
        tree - Each node of the tree has two features added: dup (bool) and sp_node (str)
        suspect_genes - set
        duplications - list of (sp_node_name, genes0, genes1)
    """
    og_name = "OG%07d" % iog
    n_species = len(species_tree_rooted)
    # max_genes_dups = 5*n_species
    # max_genes_text = (">%d genes" % max_genes_dups,)
    qPrune = False
    SpeciesAndGene = SpeciesAndGene_lookup[GeneToSpecies]
    orthologues = []
    duplications = []
    if not qNoRecon:
        tree = Resolve(tree, GeneToSpecies)
    if qPrune:
        tree.prune(tree.get_leaf_names())
    if len(tree) == 1:
        return set(orthologues), tree, set(), duplications
    """ At this point need to label the tree nodes """
    iNode = 1
    tree.name = "n0"
    suspect_genes = set()
    empty_set = set()
    # preorder traverse so that suspect genes can be identified first, before their closer orthologues are proposed.
    # Tree resolution has already been performed using a postorder traversal
    for n in tree.traverse('preorder'):
        if n.is_leaf():
            continue
        if not n.is_root():
            n.name = "n%d" % iNode
            iNode += 1
        sp_present = None
        ch = n.get_children()
        if len(ch) == 2:
            oSize, overlap, sp0, sp1 = OverlapSize(
                n, GeneToSpecies, suspect_genes)
            sp_present = sp0.union(sp1)
            stNode = MRCA_node(species_tree_rooted, sp_present)
            n.add_feature("sp_node", stNode.name)
            if oSize != 0:
                # this should be moved to the tree resolution step. Except that doesn't use the species tree, so can't
                qResolved, misplaced_genes = ResolveOverlap(
                    overlap, sp0, sp1, ch, tree, neighbours, GeneToSpecies)
                # label the removed genes
                for g in misplaced_genes:
                    nn = tree & g
                    nn.add_feature("X", True)
            else:
                misplaced_genes = empty_set
            dup = oSize != 0 and not qResolved
            n.add_feature("dup", dup)
            if dup:
                if q_get_dups:
                    # genes0 = ch[0].get_leaf_names() if len(ch[0]) <= max_genes_dups else max_genes_text
                    # genes1 = ch[1].get_leaf_names() if len(ch[1]) <= max_genes_dups else max_genes_text
                    genes0 = ch[0].get_leaf_names()
                    genes1 = ch[1].get_leaf_names()
                    duplications.append((stNode.name, n.name, float(
                        oSize)/(len(stNode)), genes0, genes1))
            else:
                # sort out bad genes - no orthology for all the misplaced genes at this level (misplaced_genes).
                # For previous levels, (suspect_genes) have their orthologues written to suspect orthologues file
                orthologues.append(Orthologs_and_Suspect(
                    ch, suspect_genes, misplaced_genes, SpeciesAndGene))
                suspect_genes.update(misplaced_genes)
        elif len(ch) > 2:
            species = [{GeneToSpecies(l)
                        for l in n_.get_leaf_names()} for n_ in ch]
            all_species = set.union(*species)
            stNode = MRCA_node(species_tree_rooted, all_species)
            n.add_feature("sp_node", stNode.name)
            # should skip if everything below this is a single species, but should write out the duplications
            if len(all_species) == 1:
                # genes = n.get_leaf_names() if len(n) <= max_genes_dups else max_genes_text
                genes = n.get_leaf_names()
                duplications.append((stNode.name, n.name, 1., genes, []))
                n.add_feature("dup", True)
            else:
                dups = []
                for (n0, s0), (n1, s1) in itertools.combinations(zip(ch, species), 2):
                    if len(s0.intersection(s1)) == 0:
                        orthologues.append(Orthologs_and_Suspect(
                            (n0, n1), suspect_genes, empty_set, SpeciesAndGene))
                        dups.append(False)
                    else:
                        dups.append(True)
                if all(dups):
                    # genes = n.get_leaf_names() if len(n) <= max_genes_dups else max_genes_text
                    genes = n.get_leaf_names()
                    duplications.append((stNode.name, n.name, 1., genes, []))
                n.add_feature("dup", all(dups))
                # # if there are nodes below with same MRCA then dup (no HOGs) otherwise not dup (=> HOGS at this level)
                # descendant_nodes = [MRCA_node(species_tree_rooted, sp) for sp in species]
                # dup = any(down_sp_node == stNode for down_sp_node in descendant_nodes)
                # n.add_feature("dup", dup)
                # print(n.name + ": dup3")
    return orthologues, tree, suspect_genes, duplications


def Resolve(tree, GeneToSpecies):
    StoreSpeciesSets(tree, GeneToSpecies)
    for n in tree.traverse("postorder"):
        tree = resolve.resolve(n, GeneToSpecies)
    return tree


def GetSpeciesNeighbours(t):
    """
    Args: t = rooted species tree

    Returns:
    dict: species -> species_dict, such that species_dict: other_species -> toplogical_dist 
    """
    species = t.get_leaf_names()
    levels = {s: [] for s in species}
    for n in t.traverse('postorder'):
        if n.is_leaf():
            continue
        children = n.get_children()
        leaf_sets = [set(ch.get_leaf_names()) for ch in children]
        not_i = [set.union(*[l for j, l in enumerate(leaf_sets) if j != i])
                 for i in xrange(len(children))]
        for l, n in zip(leaf_sets, not_i):
            for ll in l:
                levels[ll].append(n)
    neighbours = {sp: {other: n for n, others in enumerate(
        lev) for other in others} for sp, lev in levels.items()}
    return neighbours


def RootAndGetOrthologues_from_tree(iog, tree_fn, species_tree_rooted, GeneToSpecies, neighbours, qWrite=False, qNoRecon=False):
    rooted_tree_ids, qHaveSupport = CheckAndRootTree(
        tree_fn, species_tree_rooted, GeneToSpecies)  # this can be parallelised easily
    if rooted_tree_ids is None:
        return
    orthologues, recon_tree, suspect_genes, dups = GetOrthologues_from_tree(
        iog, rooted_tree_ids, species_tree_rooted, GeneToSpecies, neighbours, qNoRecon=qNoRecon)
    if qWrite:
        directory = os.path.split(tree_fn)[0]
        WriteQfO2(orthologues, directory + "_Orthologues_M3/" +
                  os.path.split(tree_fn)[1], qAppend=False)


def RootTreeStandalone_Serial(trees_dir, species_tree_rooted_fn, GeneToSpecies, output_dir, qSingleTree):
    species_tree_rooted = tree_lib.Tree(species_tree_rooted_fn)
#    args_queue = mp.Queue()
    for treeFN in glob.glob(trees_dir + ("*" if qSingleTree else "/*")):
        if (not os.path.exists(treeFN)) or os.stat(treeFN).st_size == 0:
            return
        try:
            tree = tree_lib.Tree(treeFN)
        except:
            tree = tree_lib.Tree(treeFN, format=3)
        if len(tree) == 1:
            return
        root = GetRoot(tree, species_tree_rooted, GeneToSpecies)
        if root == None:
            return
        # Pick the first root for now
        if root != tree:
            tree.set_outgroup(root)
        tree.write(outfile=treeFN + ".rooted.txt")


def GetOrthologuesStandalone_Serial(trees_dir, species_tree_rooted_fn, GeneToSpecies, output_dir, qSingleTree):
    species_tree_rooted = tree_lib.Tree(species_tree_rooted_fn)
    neighbours = GetSpeciesNeighbours(species_tree_rooted)
#    args_queue = mp.Queue()
    for treeFn in glob.glob(trees_dir + ("*" if qSingleTree else "/*")):
        print(treeFn)
        # Now need to root the tree first
        RootAndGetOrthologues_from_tree(
            0, treeFn, species_tree_rooted, GeneToSpecies, neighbours)


def SortFile(fn, f_type):
    """
    Sort the contents of the file by the first column and save back to the same filename.
    Args:
        fn - filename
        f_type - o, x, h or d for orthologs, xenologs, hogs or duplications
    """
    def first_column_sort(s): return s.split("\t", 1)[0]
    if f_type == "h":
        # Need to renumber the hogs as the parallel numbering is incorrect
        with open(fn, csv_read_mode) as infile:
            try:
                header = next(infile)
            except StopIteration:
                return
            lines = []
            # remove incorrect HOG numbering
            for line in infile:
                lines.append(line.split("\t", 1)[-1])
            if len(lines) == 0:
                return
            hog_base = line.split(".", 1)[0]
        lines.sort(key=first_column_sort)
        with open(fn, csv_write_mode) as outfile:
            outfile.write(header)
            for ihog, l in enumerate(lines):
                outfile.write(hog_base + (".HOG%07d" % ihog) + "\t" + l)
    else:
        with open(fn, csv_read_mode) as infile:
            try:
                header = next(infile)
            except StopIteration:
                return
            lines = list(infile)
        lines.sort(key=first_column_sort)
        with open(fn, csv_write_mode) as outfile:
            outfile.write(header)
            outfile.write("".join(lines))


def GetOrthologues_from_phyldog_tree(iog, treeFN, GeneToSpecies, qWrite=False, dupsWriter=None, seqIDs=None, spIDs=None):
    """ if dupsWriter != None then seqIDs and spIDs must also be provided"""
    empty = set()
    orthologues = []
    if (not os.path.exists(treeFN)) or os.stat(treeFN).st_size == 0:
        return set(orthologues)
    tree = tree_lib.Tree(treeFN)
    if len(tree) == 1:
        return set(orthologues)
    """ At this point need to label the tree nodes """
    leaf_labels = dict()
    empty_dict = dict()
    for n in tree.traverse('preorder'):
        if n.is_leaf():
            leaf_labels[n.name] = ("n" + n.ND)
            continue
        else:
            n.name = "n" + n.ND
        ch = n.get_children()
        if len(ch) == 2:
            oSize, overlap, sp0, sp1 = OverlapSize(n, GeneToSpecies, empty)
            if n.Ev == "D":
                if dupsWriter != None:
                    sp_present = sp0.union(sp1)
                    stNode = "N" + n.S
                    if len(sp_present) == 1:
                        isSTRIDE = "Terminal"
                    else:
                        isSTRIDE = "Non-Terminal"
                    dupsWriter.writerow(["OG%07d" % iog, spIDs[stNode] if len(stNode) == 1 else stNode, n.name, "-", isSTRIDE, ", ".join(
                        [seqIDs[g] for g in ch[0].get_leaf_names()]), ", ".join([seqIDs[g] for g in ch[1].get_leaf_names()])])
            else:
                d0 = defaultdict(list)
                for g in ch[0].get_leaf_names():
                    sp, seq = g.split("_")
                    d0[sp].append(seq)
                d1 = defaultdict(list)
                for g in ch[1].get_leaf_names():
                    sp, seq = g.split("_")
                    d1[sp].append(seq)
                orthologues.append((d0, d1, empty_dict, empty_dict))
        elif len(ch) > 2:
            print("Non-binary node")
            print((n.get_leaf_names()))
    if qWrite:
        directory = os.path.split(treeFN)[0]
        WriteQfO2(orthologues, directory + "/../Orthologues_M3/" +
                  os.path.split(treeFN)[1], qAppend=False)
    return orthologues
