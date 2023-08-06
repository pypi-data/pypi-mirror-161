import os
import re
from Bio import Phylo
from io import StringIO
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.math.set import merge_same_element_set
from toolbiox.lib.common.os import have_file, mkdir, copy_file, move_file, cmd_run, multiprocess_running
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.evolution.tree_operate import add_clade_name, lookup_by_names, ignore_branch_length, clade_rename, get_root_by_species_for_file, get_nhx_tree_with_taxon_info, get_offspring, load_nhx_tree, get_rooted_tree_by_species_tree, map_node_species_info, get_top_taxon_clade
from toolbiox.lib.common.evolution.orthotools2 import OrthoGroup, OrthoGroups, get_orthogroups_from_gene_tree, OG_gene_rename
from toolbiox.api.xuyuxing.comp_genome.dlcpar import run_dlcpar, merge_locus_tree_and_recon_file
from toolbiox.api.xuyuxing.comp_genome.orthofinder_tree_resolve.main import resolve_rooted_gene_tree

# about tree building


def prepare_OG_work_dir(OGs, species_info_dict, top_work_dir, species_tree_file=None, need_cds_flag=False, check_run=False):

    OGs.work_dir = os.path.abspath(top_work_dir)

    mkdir(OGs.work_dir, True)

    if check_run:
        OGs.species_tree_file = OGs.work_dir+"/species_tree.phb"
        if not os.path.exists(OGs.species_tree_file):
            raise EnvironmentError("species_tree_file failed")

        for OG_id in OGs.OG_dict:
            og = OGs.OG_dict[OG_id]
            og.work_dir = top_work_dir + "/" + OG_id

            if not os.path.exists(og.work_dir):
                raise EnvironmentError("%s work_dir failed" % OG_id)

            og.pt_fa = og.work_dir + "/pt.fa"
            if not os.path.exists(og.pt_fa):
                raise EnvironmentError("%s pt_fa failed" % OG_id)

            if need_cds_flag:
                og.cds_fa = og.work_dir + "/cds.fa"

                if not os.path.exists(og.cds_fa):
                    raise EnvironmentError("%s cds_fa failed" % OG_id)

            og.rename_map = og.work_dir + "/rename.map"
            if not os.path.exists(og.rename_map):
                raise EnvironmentError("%s rename_map failed" % OG_id)

            og.species_tree_file = OGs.species_tree_file

        return OGs

    if species_tree_file:
        OGs.species_tree_file = OGs.work_dir+"/species_tree.phb"
        copy_file(species_tree_file, OGs.species_tree_file)

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
        og = OGs.OG_dict[OG_id]
        og.work_dir = top_work_dir + "/" + OG_id
        mkdir(og.work_dir, True)

        # pt_file
        og.pt_fa = og.work_dir + "/pt.fa"
        with open(og.pt_fa, 'w') as f:
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
            og.cds_fa = og.work_dir + "/cds.fa"
            with open(og.cds_fa, 'w') as f:
                for sp_id in OG_gene_dict:
                    for gene in OG_gene_dict[sp_id]:
                        g_id = gene.id
                        if g_id != '':
                            cds_seq = huge_cds_dict[sp_id][huge_rename_map[sp_id][g_id]]
                            f.write(">%s\n%s\n" % (
                                str(huge_rename_map[sp_id][g_id])+"_"+sp_id, cds_seq))

        # rename_map
        og.rename_map = og.work_dir + "/rename.map"
        og.rename_dict = {}
        with open(og.rename_map, 'w') as f:
            for sp_id in OG_gene_dict:
                for gene in OG_gene_dict[sp_id]:
                    g_id = gene.id
                    if g_id != '':
                        f.write("%s\t%s\t%s\n" %
                                (str(huge_rename_map[sp_id][g_id])+"_"+sp_id, g_id, sp_id))
                        og.rename_dict[g_id] = str(
                            huge_rename_map[sp_id][g_id])+"_"+sp_id
        
        if species_tree_file:
            og.species_tree_file = OGs.species_tree_file

    # write rename file
    # all_rename_map = top_work_dir + "/rename.map"
    # with open(all_rename_map, 'w') as f:
    #     for sp_id in huge_rename_map:
    #         for g_id in huge_rename_map[sp_id]:
    #             if g_id != '':
    #                 f.write("%s\t%s\t%s\n" %
    #                         (huge_rename_map[sp_id][g_id], g_id, sp_id))

    return OGs


def prepare_treebest_species_tree(SpeciesTree_rooted_file, treebest_species_tree_file):
    species_rooted_tree = Phylo.read(SpeciesTree_rooted_file, 'newick')
    rename_map = {
        i.name: i.name+"*" for i in species_rooted_tree.get_terminals()}

    tmp_handle = StringIO()

    species_rooted_tree = clade_rename(
        species_rooted_tree, rename_map)
    species_rooted_tree = add_clade_name(species_rooted_tree, True)
    species_rooted_tree = ignore_branch_length(species_rooted_tree, True)
    Phylo.write(species_rooted_tree, tmp_handle, "newick")
    tree_string = tmp_handle.getvalue()

    tree_string = re.sub(r'\d+\.\d+', '', tree_string)
    tree_string = re.sub(r':', '', tree_string)

    with open(treebest_species_tree_file, 'w') as f:
        f.write(tree_string)

    return treebest_species_tree_file


def msa(og, program='clustalw'):
    og.aa_aln = og.pt_fa+".aln"

    if program == 'clustalw':
        cmd_string = "clustalw2 -INFILE="+og.pt_fa + \
            " -ALIGN -OUTPUT=FASTA -OUTFILE="+og.aa_aln+" -type=protein"
    elif program == 't_coffee':
        cmd_string = "t_coffee "+og.pt_fa+" -method mafftgins_msa muscle_msa kalign_msa t_coffee_msa -output=fasta_aln -outfile=" + \
            og.aa_aln+" -newtree "+og.aa_aln+".dnd"

    cmd_run(cmd_string, silence=True)

    return og


def tree(og, program='fasttree'):
    og.tree_file = og.work_dir+"/tree.phb"

    if program == 'fasttree':
        cmd_string = "FastTree -wag -gamma -out %s %s >/dev/null" % (
            og.tree_file, og.aa_aln)
        cmd_run(cmd_string, silence=True)
    elif program == 'raxml':
        cmd_string = "raxml-ng --msa %s --model LG+G4 --seed 12345 --threads 1" % og.aa_aln
        cmd_run(cmd_string, silence=True)
        output_filename = og.aa_aln + ".raxml.bestTree"
        move_file(output_filename, og.tree_file)
    elif program == 'raxml_support':
        cmd_string = "raxml-ng --msa %s --model LG+G4 --seed 12345 --threads 1 --all --bs-trees 100" % og.aa_aln
        cmd_run(cmd_string, silence=True)
        output_filename = og.aa_aln + ".raxml.support"
        move_file(output_filename, og.tree_file)

    return og


def root_tree(og):
    tmp_info = tsv_file_dict_parse(og.rename_map, fieldnames=[
                                   'new_id', 'old_id', 'speci'], key_col='new_id')
    gene_to_species_map_dict = {i: tmp_info[i]["speci"] for i in tmp_info}

    og.rooted_tree = og.work_dir+"/tree.rooted.phb"
    get_root_by_species_for_file(
        og.tree_file, og.species_tree_file, gene_to_species_map_dict, og.rooted_tree)

    return og


def resolve_tree(og, program='auto'):
    og.resolve_tree = og.work_dir+"/tree.resolve.phb"
    tmp_info = tsv_file_dict_parse(og.rename_map, fieldnames=[
        'new_id', 'old_id', 'speci'], key_col='new_id')
    gene_to_species_map_dict = {i: tmp_info[i]["speci"] for i in tmp_info}

    if program == 'dlcpar':

        dlcpar_name_map_file = og.work_dir+"/dlcpar.name.map"
        with open(dlcpar_name_map_file, 'w') as f:
            for i in tmp_info:
                f.write("%s\t%s\n" % (i, tmp_info[i]["speci"]))

        recon_tree_file, recon_node_file = run_dlcpar(
            og.species_tree_file, dlcpar_name_map_file, og.rooted_tree)

        move_file(recon_tree_file, og.resolve_tree)

    elif program == 'orthofinder':
        gene_tree = Phylo.read(og.rooted_tree, 'newick')

        resolve_gene_tree = resolve_rooted_gene_tree(
            gene_tree, gene_to_species_map_dict)
        with open(og.resolve_tree, 'w') as f:
            Phylo.write(resolve_gene_tree, f, 'newick')

    elif program == 'auto':
        try:
            dlcpar_name_map_file = og.work_dir+"/dlcpar.name.map"
            with open(dlcpar_name_map_file, 'w') as f:
                for i in tmp_info:
                    f.write("%s\t%s\n" % (i, tmp_info[i]["speci"]))

            recon_tree_file, recon_node_file = run_dlcpar(
                og.species_tree_file, dlcpar_name_map_file, og.rooted_tree)

            move_file(recon_tree_file, og.resolve_tree)

        except:
            gene_tree = Phylo.read(og.rooted_tree, 'newick')

            resolve_gene_tree = resolve_rooted_gene_tree(
                gene_tree, gene_to_species_map_dict)
            with open(og.resolve_tree, 'w') as f:
                Phylo.write(resolve_gene_tree, f, 'newick')

    return og


def tree_map_taxon_info(og, use_reslove_tree=True):
    tmp_info = tsv_file_dict_parse(og.rename_map, fieldnames=[
        'new_id', 'old_id', 'speci'], key_col='new_id')
    gene_to_species_map_dict = {i: tmp_info[i]["speci"] for i in tmp_info}

    if use_reslove_tree:
        resolve_tree = Phylo.read(og.resolve_tree, 'newick')
    else:
        resolve_tree = Phylo.read(og.rooted_tree, 'newick')
    species_tree = Phylo.read(og.species_tree_file, 'newick')

    og.nhx_file = og.work_dir+"/tree.nhx"
    get_nhx_tree_with_taxon_info(
        resolve_tree, species_tree, gene_to_species_map_dict, og.nhx_file)

    return og


def treebest(og):
    og.cds_aln = og.cds_fa+".cds.aln"
    cmd_string = "treebest backtrans "+og.aa_aln+" "+og.cds_fa+" > "+og.cds_aln
    cmd_run(cmd_string, silence=True)

    og.nhx_file = og.work_dir+"/tree.nhx"
    cmd_string = "treebest best -f "+og.treebest_species_tree_file + \
        " -o "+og.nhx_file+" "+og.cds_aln
    cmd_run(cmd_string, silence=True)

    og.nhx_out = og.work_dir+"/tree.nhx.out"
    cmd_string = "treebest nj -s "+og.treebest_species_tree_file + \
        " -t dm -vc "+og.nhx_file+" "+og.cds_aln+" > "+og.nhx_out
    cmd_run(cmd_string, silence=True)

    return og


def tree_pipeline(OGs, method='fasttree', threads=56, resolve_flag=True):
    """
    OGs should have work_dir attr (run prepare_OG_work_dir)
    """

    # running msa
    print("running MSA")
    args_list = []
    args_id_list = []
    for og_id in OGs.OG_dict:
        og = OGs.OG_dict[og_id]
        args_list.append((og, ))
        args_id_list.append(og_id)

    mlt_out = multiprocess_running(
        msa, args_list, threads, None, False, args_id_list)

    for og_id in OGs.OG_dict:
        OGs.OG_dict[og_id] = mlt_out[og_id]['output']

    if method == 'treebest':
        OGs.treebest_species_tree_file = OGs.work_dir + "/species_treebest.phb"
        prepare_treebest_species_tree(
            OGs.species_tree_file, OGs.treebest_species_tree_file)

        for i in OGs.OG_dict:
            OGs.OG_dict[i].treebest_species_tree_file = OGs.treebest_species_tree_file

        print("running treebest")
        args_list = []
        args_id_list = []
        for og_id in OGs.OG_dict:
            og = OGs.OG_dict[og_id]

            if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
                continue

            og = OGs.OG_dict[og_id]
            args_list.append((og, ))
            args_id_list.append(og_id)

        mlt_out = multiprocess_running(
            treebest, args_list, threads, None, False, args_id_list)

        for og_id in OGs.OG_dict:
            if og_id in mlt_out:
                OGs.OG_dict[og_id] = mlt_out[og_id]['output']
                
    else:
        # running tree
        print("running tree")
        args_list = []
        args_id_list = []
        for og_id in OGs.OG_dict:
            og = OGs.OG_dict[og_id]

            if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
                continue

            args_list.append((og, method))
            args_id_list.append(og_id)

        mlt_out = multiprocess_running(
            tree, args_list, threads, None, False, args_id_list)

        for og_id in OGs.OG_dict:
            if og_id in mlt_out:
                OGs.OG_dict[og_id] = mlt_out[og_id]['output']

        # running root_tree
        print("running root_tree")
        args_list = []
        args_id_list = []
        for og_id in OGs.OG_dict:
            og = OGs.OG_dict[og_id]

            if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
                continue

            args_list.append((og, ))
            args_id_list.append(og_id)

        mlt_out = multiprocess_running(
            root_tree, args_list, threads, None, False, args_id_list)

        for og_id in OGs.OG_dict:
            if og_id in mlt_out:
                OGs.OG_dict[og_id] = mlt_out[og_id]['output']

        # running resolve_tree
        if resolve_flag:
            print("running resolve_tree")
            args_list = []
            args_id_list = []
            for og_id in OGs.OG_dict:
                og = OGs.OG_dict[og_id]

                if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
                    continue

                args_list.append((og, ))
                args_id_list.append(og_id)

            mlt_out = multiprocess_running(
                resolve_tree, args_list, threads, None, False, args_id_list)

            for og_id in OGs.OG_dict:
                if og_id in mlt_out:
                    OGs.OG_dict[og_id] = mlt_out[og_id]['output']

        # running tree_map_taxon_info
        print("running tree_map_taxon_info")
        args_list = []
        args_id_list = []
        for og_id in OGs.OG_dict:
            og = OGs.OG_dict[og_id]

            if len(og.gene_list) <= 3 or len([og.species_stat[i] for i in og.species_stat if og.species_stat[i] > 0]) <= 1:
                continue

            args_list.append((og, resolve_flag))
            args_id_list.append(og_id)

        mlt_out = multiprocess_running(
            tree_map_taxon_info, args_list, threads, None, False, args_id_list)

        for og_id in OGs.OG_dict:
            if og_id in mlt_out:
                OGs.OG_dict[og_id] = mlt_out[og_id]['output']

    return OGs


# about extract orthogroups

def get_orthogroups_from_tree_file(gene_tree_file, species_tree_file, gene_to_species_map_dict=None, taxonomy_level=None, conserved_arguments=None, nhx_input=True):
    species_tree = Phylo.read(species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)

    if not nhx_input:
        gene_tree = Phylo.read(gene_tree_file, 'newick')
        gene_tree = add_clade_name(gene_tree)

        rooted_gene_tree = get_rooted_tree_by_species_tree(
            gene_tree, species_tree, gene_to_species_map_dict)
        rooted_taxon_gene_tree = map_node_species_info(
            rooted_gene_tree, species_tree, gene_to_species_map_dict)

    else:
        rooted_taxon_gene_tree, clade_dict = load_nhx_tree(gene_tree_file)

    og_list = get_orthogroups_from_gene_tree(
        rooted_taxon_gene_tree, species_tree, taxonomy_level=taxonomy_level, conserved_arguments=conserved_arguments)

    return og_list


def get_orthogroups_pipeline(OGs, taxonomy_level=None, conserved_arguments=None, threads=56):
    species_tree = Phylo.read(OGs.species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)
    species_tree_dict = lookup_by_names(species_tree)

    if taxonomy_level is None:
        taxonomy_level = species_tree.root.name

    sp_list = [i.name for i in species_tree_dict[taxonomy_level].get_terminals()]

    args_list = []
    args_id_list = []
    not_tree_list = []
    for og_id in OGs.OG_dict:
        og = OGs.OG_dict[og_id]
        if hasattr(og, 'nhx_file') and have_file(og.nhx_file):
            args_list.append((og.nhx_file, OGs.species_tree_file,
                            None, taxonomy_level, conserved_arguments, True))
            args_id_list.append(og_id)
        else:
            not_tree_list.append(og_id)

    mlt_out = multiprocess_running(
        get_orthogroups_from_tree_file, args_list, threads, None, False, args_id_list)

    og_list = []

    for og_id in not_tree_list:
        raw_og = OGs.OG_dict[og_id]
        og_list.append(raw_og)

    for og_id in args_id_list:
        raw_og = OGs.OG_dict[og_id]
        if hasattr(raw_og, 'rename_dict'):
            rename_dict = {}
            for i in raw_og.rename_dict:
                rename_dict[raw_og.rename_dict[i]] = i

        output_og_list = mlt_out[og_id]['output']
        num = 0
        for og in output_og_list:
            sub_og_id = '%s_%d' % (og_id, num)
            num += 1
            og.id = sub_og_id
            if hasattr(raw_og, 'rename_dict'):
                og = OG_gene_rename(og, rename_dict)
            og_list.append(og)

    new_OGs = OrthoGroups(from_OG_list=og_list, species_list=sp_list)

    return new_OGs


# # about extract orthogroups
# def get_orthogroups_from_nhx_tree(nhx_tree_file, species_tree, taxonomy_level=None):
#     """return sub_orthogroups for at least two species, and paralogous will be removed"""

#     species_tree = add_clade_name(species_tree)
#     species_node_dict = lookup_by_names(species_tree)

#     if taxonomy_level:
#         taxonomy_list = set([offspring_clade.name for offspring_clade in get_offspring(
#             species_node_dict[taxonomy_level])] + [species_node_dict[taxonomy_level].name])
#     else:
#         taxonomy_list = set([offspring_clade.name for offspring_clade in get_offspring(
#             species_tree)])

#     nhx_tree, clade_dict = load_nhx_tree(nhx_tree_file)
#     pairs = []
#     for clade_name in clade_dict:
#         clade = clade_dict[clade_name]
#         if clade.is_terminal():
#             if clade.name in taxonomy_list:
#                 pairs.append([clade.name])
#         else:
#             if clade.nhx_dict['duplication'] == 0 and clade.nhx_dict['speciation'] == 1 and clade.nhx_dict["scientific name"] in taxonomy_list:
#                 pairs.append([i.name for i in clade.get_terminals()])

#     orthogroups_list = merge_same_element_set(pairs)
#     sp_list = [i for i in taxonomy_list if species_node_dict[i].is_terminal()]

#     OGs_dict = {}
#     num = 0
#     for og_list in orthogroups_list:
#         og_dict = {i: [] for i in sp_list}
#         for g_id in og_list:
#             sp_id = clade_dict[g_id].nhx_dict['scientific name']
#             og_dict[sp_id].append(g_id)
#         OrthoGroup(id=num,)
#         OGs_dict[num] = og_dict
#         num += 1

#     return orthogroups


# def get_taxonomy_list_from_species_tree_file(species_tree_file, taxonomy_level=None, include_clade=True):
#     species_tree = Phylo.read(species_tree_file, 'newick')
#     species_tree = add_clade_name(species_tree)
#     species_node_dict = lookup_by_names(species_tree)

#     if taxonomy_level:
#         clade_need = species_node_dict[taxonomy_level]
#     else:
#         clade_need = species_tree

#     if include_clade:
#         if taxonomy_level:
#             taxonomy_list = set([offspring_clade.name for offspring_clade in get_offspring(
#                 clade_need)] + [clade_need.name])
#         else:
#             taxonomy_list = set([offspring_clade.name for offspring_clade in get_offspring(
#                 clade_need)])
#     else:
#         taxonomy_list = set([offspring_clade.name for offspring_clade in get_offspring(
#             clade_need) if offspring_clade.is_terminal()])

#     return taxonomy_list


# def get_sub_orthogroups_from_nhx_tree(nhx_tree_file, species_tree_file, taxonomy_level=None):
#     """return sub_orthogroups for at least two species, and paralogous will be removed"""

#     taxonomy_list = get_taxonomy_list_from_species_tree_file(
#         species_tree_file, taxonomy_level, include_clade=True)

#     nhx_tree, clade_dict = load_nhx_tree(nhx_tree_file)
#     pairs = []
#     for clade_name in clade_dict:
#         clade = clade_dict[clade_name]
#         if clade.is_terminal():
#             if clade.name in taxonomy_list:
#                 pairs.append([clade.name])
#         else:
#             if clade.nhx_dict['Duplications'] == 0 and clade.nhx_dict['Speciations'] == 1 and clade.nhx_dict["Scientific name"] in taxonomy_list:
#                 pairs.append([i.name for i in clade.get_terminals()])

#     orthogroups = merge_same_element_set(pairs)

#     return orthogroups
# def get_sub_orthogroups_from_nhx_tree(nhx_tree_file, species_tree_file, taxonomy_level=None):
#     """return sub_orthogroups for at least two species, and paralogous will be removed"""

#     taxonomy_list = get_taxonomy_list_from_species_tree_file(
#         species_tree_file, taxonomy_level, include_clade=True)

#     nhx_tree, clade_dict = load_nhx_tree(nhx_tree_file)
#     pairs = []
#     for clade_name in clade_dict:
#         clade = clade_dict[clade_name]
#         if clade.is_terminal():
#             if clade.name in taxonomy_list:
#                 pairs.append([clade.name])
#         else:
#             if clade.nhx_dict['Duplications'] == 0 and clade.nhx_dict['Speciations'] == 1 and clade.nhx_dict["Scientific name"] in taxonomy_list:
#                 pairs.append([i.name for i in clade.get_terminals()])

#     orthogroups = merge_same_element_set(pairs)

#     return orthogroups

# def get_two_species_orthologous_pairs_from_nhx_tree(sp_a, sp_b, nhx_tree_file, species_tree_file):
#     pass

if __name__ == '__main__':

    from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info

    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/genome_info.xlsx'
    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics/orthofinder/pt_file/OrthoFinder/Results_Jul26/Orthogroups/Orthogroups.tsv"
    top_work_dir = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics/fasttree"
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/species.tree.txt"

    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)
    species_info_dict = read_species_info(ref_xlsx)

    OGs = prepare_OG_work_dir(OGs, species_info_dict,
                              top_work_dir, species_tree_file)

    og_id = 'OG0003674'
    og = OGs.OG_dict[og_id]

    msa(og)
    tree(og, 'raxml')
    root_tree(og)
    resolve_tree(og)
    tree_map_taxon_info(og)

    # fasttree pipeline

    OGs = prepare_OG_work_dir(OGs, species_info_dict,
                              top_work_dir, species_tree_file)

    OGs = tree_pipeline(OGs, "fasttree", threads=56)

    # treebest pipeline

    OGs = prepare_OG_work_dir(OGs, species_info_dict,
                              top_work_dir, species_tree_file, need_cds_flag=True)

    OGs = tree_pipeline(OGs, "treebest", threads=56)

    # get OG from tree
    og_list = get_orthogroups_from_tree_file(
        og.nhx_file, species_tree_file, taxonomy_level=None, conserved_arguments=None, nhx_input=True)

    # get OG pipeline
    subOGs = get_orthogroups_pipeline(
        OGs, taxonomy_level=None, conserved_arguments=None, threads=56)
