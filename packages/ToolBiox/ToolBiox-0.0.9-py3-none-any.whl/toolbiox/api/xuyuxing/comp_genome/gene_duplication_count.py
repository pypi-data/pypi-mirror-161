from Bio import Phylo
from toolbiox.lib.common.evolution.tree_operate import lookup_by_names, add_clade_name, draw_ascii, get_MRCA_from_list, is_ancestors_of
from toolbiox.lib.common.os import multiprocess_running
from toolbiox.api.xuyuxing.evolution.PAML_tools import quick_get_dNdS
from itertools import combinations


gene_tree_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/OroWGD/time/tree/treebest/OG0005933/tree.nhx'
species_tree_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/OroWGD/time/species.tree.txt'
target_taxon_node = 'Lamiales'

gene_tree = Phylo.read(gene_tree_file, 'newick')
gene_tree = add_clade_name(gene_tree)
gene_tree_node_dict = lookup_by_names(gene_tree)
gene_list = [i.name for i in gene_tree.get_terminals()]

species_tree = Phylo.read(species_tree_file, 'newick')
species_tree = add_clade_name(species_tree)
species_tree_node_dict = lookup_by_names(species_tree)

map_dict = {}
for i in gene_list:
    j, species = i.split("_")
    map_dict[i] = species


def get_duplication_and_speciation_node(gene_tree, species_tree, map_dict, target_taxon_node):
    gene_tree_node_dict = lookup_by_names(gene_tree)
    species_tree_node_dict = lookup_by_names(species_tree)

    leaf_test_flag = species_tree_node_dict[target_taxon_node].is_terminal()

    DS_dict = {'D': [], 'S': []}

    for c_id in gene_tree_node_dict:
        clade = gene_tree_node_dict[c_id]

        if not clade.is_terminal():
            # get species_node
            sp_list_in_clade = list(
                set([map_dict[i.name] for i in clade.get_terminals()]))
            species_node_now = get_MRCA_from_list(
                [species_tree_node_dict[i] for i in sp_list_in_clade], species_tree).name

            if species_node_now != target_taxon_node:
                continue

            # get duplication or speciation
            D_flag = False

            for s1, s2 in combinations(clade.clades, 2):
                s1_leaf_list = [i.name for i in s1.get_terminals()]
                s2_leaf_list = [i.name for i in s2.get_terminals()]
                s1_species_list = list(
                    set([map_dict[i] for i in s1_leaf_list]))
                s2_species_list = list(
                    set([map_dict[i] for i in s2_leaf_list]))

                if len(set(s1_species_list) & set(s2_species_list)) > 0:
                    D_flag = True

            if D_flag:
                DS_dict['D'].append(c_id)
            else:
                DS_dict['S'].append(c_id)

        else:
            if leaf_test_flag:
                if map_dict[c_id] == target_taxon_node:
                    DS_dict['S'].append(c_id)

    return DS_dict


def check_duplication_for_one_tree_one_node(gene_tree, species_tree, map_dict, test_node, if_tandom_function):
    gene_tree_node_dict = lookup_by_names(gene_tree)
    species_tree_node_dict = lookup_by_names(species_tree)

    leaf_test_flag = species_tree_node_dict[test_node].is_terminal()

    DS_dict = {'D': [], 'S': []}

    for c_id in gene_tree_node_dict:
        clade = gene_tree_node_dict[c_id]

        if not clade.is_terminal():
            if not len(clade.clades) > 2:
                # get species_node
                sp_list_in_clade = list(
                    set([map_dict[i.name] for i in clade.get_terminals()]))
                species_node_now = get_MRCA_from_list(
                    [species_tree_node_dict[i] for i in sp_list_in_clade], species_tree).name

                if species_node_now != test_node:
                    continue

                # get duplication or speciation
                D_flag = False
                S_flag = False

                s1 = clade.clades[0]
                s2 = clade.clades[1]
                s1_leaf_list = [i.name for i in s1.get_terminals()]
                s2_leaf_list = [i.name for i in s2.get_terminals()]
                s1_species_list = list(
                    set([map_dict[i] for i in s1_leaf_list]))
                s2_species_list = list(
                    set([map_dict[i] for i in s2_leaf_list]))

                if len(set(s1_species_list) & set(s2_species_list)) > 0:
                    DS_dict['D'].append(c_id)
                    DS_dict['S'].append(c_id)
                else:
                    DS_dict['S'].append(c_id)

        else:
            if leaf_test_flag:
                if map_dict[c_id] == test_node:
                    DS_dict['S'].append(c_id)

    # rm overlap
    overlaped_s_c_id = []
    for s_c_id in DS_dict['S']:
        for d_c_id in DS_dict['D']:
            if s_c_id == d_c_id:
                overlaped_s_c_id.append(s_c_id)
            if is_ancestors_of(gene_tree_node_dict[d_c_id], gene_tree_node_dict[s_c_id], gene_tree):
                overlaped_s_c_id.append(s_c_id)

    DS_dict['S'] = list(set(DS_dict['S']) - set(overlaped_s_c_id))

    # filter tandom repeat
    tandom_c_id = []
    for d_c_id in DS_dict['D']:
        clade = gene_tree_node_dict[d_c_id]
        s1 = clade.clades[0]
        s2 = clade.clades[1]
        s1_leaf_list = [i.name for i in s1.get_terminals()]
        s2_leaf_list = [i.name for i in s2.get_terminals()]

        # make leaf_name_dict
        leaf_name_dict = {}
        for i in s1_leaf_list:
            sp = map_dict[i]
            if sp not in leaf_name_dict:
                leaf_name_dict[sp] = ([], [])
            leaf_name_dict[sp][0].append(i)

        for i in s2_leaf_list:
            sp = map_dict[i]
            if sp not in leaf_name_dict:
                leaf_name_dict[sp] = ([], [])
            leaf_name_dict[sp][1].append(i)

        # tandom repeat
        tandom_flag = False
        for sp in leaf_name_dict:
            s1_g_list = leaf_name_dict[sp][0]
            s2_g_list = leaf_name_dict[sp][1]

            for g1 in s1_g_list:
                for g2 in s2_g_list:
                    if if_tandom_function(g1, g2):
                        tandom_flag = True
                        break

        if tandom_flag:
            tandom_c_id.append(d_c_id)

    # move tandom to speciation
    for i in tandom_c_id:
        DS_dict['S'].append(i)
        DS_dict['D'].remove(i)

    dup_pair_dict = {}
    for c_id in DS_dict['D']:
        s1 = gene_tree_node_dict[c_id].clades[0]
        s2 = gene_tree_node_dict[c_id].clades[1]
        s1_list = [(map_dict[i.name], i.name) for i in s1.get_terminals()]
        s2_list = [(map_dict[i.name], i.name) for i in s2.get_terminals()]
        dup_pair_dict[c_id] = (s1_list, s2_list)

    all_gene_dict = {}
    for c_id in DS_dict['D'] + DS_dict['S']:
        all_gene_dict[c_id] = [(map_dict[i.name], i.name)
                               for i in gene_tree_node_dict[c_id].get_terminals()]

    return DS_dict, dup_pair_dict, all_gene_dict


def check_duplication_for_all_tree_one_node(OGs, gene_tree_dir, species_tree, test_node, if_tandom_function):
    args_list = []
    args_id_list = []
    for og_id in OGs.OG_dict:
        # og_id = 'OG0001125'
        og = OGs.OG_dict[og_id]
        og.tree_file = "%s/%s_tree.txt" % (gene_tree_dir, og_id)

        # filter not good OG, species number more than 3, single species not more than 50 gene, top two species not have more than 90% gene
        # species more than 3
        if len([i for i in og.species_stat if og.species_stat[i] > 0]) < 3:
            continue
        if max(og.species_stat.values()) > 50:
            continue
        if sum(sorted(og.species_stat.values())[-2:]) / sum(og.species_stat.values()) > 0.9:
            continue
        if sum(og.species_stat.values()) <= 3:
            continue

        # do
        gene_tree = Phylo.read(og.tree_file, 'newick')
        gene_tree = add_clade_name(gene_tree)

        gene_list = [i.name for i in gene_tree.get_terminals()]
        map_dict = {}
        for i in gene_list:
            species, j = i.split("_")
            map_dict[i] = species

        args_list.append((gene_tree, species_tree, map_dict,
                          test_node, if_tandom_function))
        args_id_list.append(og_id)

    mlt_out = multiprocess_running(
        check_duplication_for_one_tree_one_node, args_list, 56, None, True, args_id_list)

    DS_dict = {}
    dup_pair_dict = {}
    all_gene_dict = {}

    for i in mlt_out:
        DS_dict[i] = mlt_out[i]['output'][0]
        dup_pair_dict[i] = mlt_out[i]['output'][1]
        all_gene_dict[i] = mlt_out[i]['output'][2]

    # # stat
    # keep_OG = 0
    # sum_OG = 0
    # for i in DS_dict:
    #     keep_OG += len(DS_dict[i]['D'])
    #     sum_OG += (len(DS_dict[i]['D']) + len(DS_dict[i]['S']))

    return DS_dict, dup_pair_dict, all_gene_dict


def get_gene_pair_Ks(gene_pairs_list):
    args_list = []
    args_id_list = []
    for i in gene_pairs_list:
        args_list.append((i, "/tmp"))
        args_id_list.append(i)

    mlt_out = multiprocess_running(
        quick_get_dNdS, args_list, 160, None, True, args_id_list)

    output_dict = {}
    for i in mlt_out:
        if mlt_out[i]['output'] == {}:
            continue
        for j in mlt_out[i]['output']:
            for k in mlt_out[i]['output'][j]:
                output_dict[i] = mlt_out[i]['output'][j][k][2]

    return output_dict


if __name__ == '__main__':
    from toolbiox.api.xuyuxing.comp_genome.gene_duplication_count import check_duplication_for_all_tree_one_node
    from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
    from toolbiox.lib.common.evolution.tree_operate import draw_ascii, add_clade_name, lookup_by_names
    from Bio import Phylo
    import re

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun03/Orthogroups/Orthogroups.tsv"
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun03/Species_Tree/SpeciesTree_rooted.txt"
    gene_tree_dir = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun03/Resolved_Gene_Trees"
    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'

    # species tree
    species_tree = Phylo.read(species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)
    species_tree_node_dict = lookup_by_names(species_tree)
    draw_ascii(species_tree, clade_name=True)
    sp_list = [i.name for i in species_tree.get_terminals()]
    sp_info_dict = read_species_info(ref_xlsx, ['interpro_function_anno'])
    sp_info_dict = {i: sp_info_dict[i] for i in sp_info_dict if i in sp_list}

    # read fasta
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
    for sp_id in sp_info_dict:
        sp = sp_info_dict[sp_id]
        sp.cds_dict = read_fasta_by_faidx(sp.cds_file)
        sp.pt_dict = read_fasta_by_faidx(sp.pt_file)

    # get function
    from toolbiox.api.xuyuxing.file_parser.interproscan_results import interproscan_results_parser
    from toolbiox.lib.common.fileIO import tsv_file_dict_parse
    import pickle

    ath_ortho_dir = '/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder_ath/pt_file/OrthoFinder/Results_Jun10/Orthologues/Orthologues_Ath'
    ath_anno_pyb = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/all_annotation.pyb'

    TEMP = open(ath_anno_pyb, 'rb')
    data_dict = pickle.load(TEMP)
    TEMP.close()

    ath_go_dict = {}
    for i in data_dict:
        ath_go_dict[i] = data_dict[i][13].split("; ")

    for sp_id in sp_info_dict:
        # print(sp_id)
        sp = sp_info_dict[sp_id]

        # use ath go firstly
        ortho_file = ath_ortho_dir + "/Ath__v__%s.tsv" % sp_id
        ortho_file_info = tsv_file_dict_parse(ortho_file)

        to_ath_dict = {}
        for i in ortho_file_info:
            for j in ortho_file_info[i][sp_id].split(", "):
                to_ath_dict[j] = ortho_file_info[i]['Ath'].split(", ")

        to_ath_go_dict = {}
        for i in to_ath_dict:
            go_list = []
            for j in to_ath_dict[i]:
                go_list.extend(ath_go_dict[j])
            to_ath_go_dict[i] = list(set(go_list))

        sp.go_dict = to_ath_go_dict

        # use interpro
        if sp.interpro_function_anno:
            interproscan_output_tsv = sp.interpro_function_anno
            interpro_dict = interproscan_results_parser(
                interproscan_output_tsv)

            for i in interpro_dict:
                go_anno = []
                for j in interpro_dict[i].domain_list:
                    if not j["GO"] is None and not j['GO'] == '':
                        go_anno.extend(j["GO"].split("|"))
                go_anno = list(set(go_anno))

                if i not in sp.go_dict or len(sp.go_dict[i]) == 0:
                    sp.go_dict[i] = go_anno

    # orthogroups
    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file, species_list=sp_list)

    # get tandom function
    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
    from toolbiox.lib.xuyuxing.base.base_function import multiprocess_running
    from toolbiox.lib.common.genome.genome_feature2 import Gene

    def get_rank_dict(gff_file):
        gff_dict = read_gff_file(gff_file)
        gf_dict = gff_dict['gene']
        chr_dict = {}
        for gf_id in gf_dict:
            gf = gf_dict[gf_id]
            if gf.chr_id not in chr_dict:
                chr_dict[gf.chr_id] = []
            chr_dict[gf.chr_id].append(gf)
        rank_dict = {}
        for chr_id in chr_dict:
            num = 0
            for gf in sorted(chr_dict[chr_id], key=lambda x: x.start):
                num += 1
                rank_dict[gf.id] = (chr_id, num)
        return rank_dict

    def get_gff_info():
        ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'
        sp_info_dict = read_species_info(ref_xlsx)

        args_list = []
        args_id_list = []

        for sp_id in sp_info_dict:
            sp = sp_info_dict[sp_id]
            args_list.append((sp.gff_file, ))
            args_id_list.append(sp_id)

        mlt_out = multiprocess_running(
            get_rank_dict, args_list, 160, None, True, args_id_list)

        all_rank_dict = {}
        for i in mlt_out:
            all_rank_dict[i] = mlt_out[i]['output']

        return all_rank_dict

    all_rank_dict = get_gff_info()

    def if_tandom(g1, g2):
        sp1, g1 = g1.split("_")
        sp2, g2 = g2.split("_")

        ch1, r1 = all_rank_dict[sp1][g1]
        ch2, r2 = all_rank_dict[sp2][g2]

        if sp1 == sp2 and ch1 == ch2 and abs(r1 - r2):
            return True
        else:
            return False

    # for test_node in species_tree_node_dict:
    #     print(test_node)
    #     check_duplication_for_all_tree_one_node(
    #         OGs, gene_tree_dir, species_tree, test_node, if_tandom)

    # for test_node in species_tree_node_dict:
    #     if test_node == 'N0':
    #         continue

    #     print(test_node)

    # running Ks
    # all_Ks_gene_pair_dict = {}
    # for test_node in species_tree_node_dict:
    #     if test_node == 'N0':
    #         continue

    #     print(test_node)

    #     DS_dict, dup_pair_dict, all_gene_dict = check_duplication_for_all_tree_one_node(
    #         OGs, gene_tree_dir, species_tree, test_node, if_tandom)

    #     # get gene pair seq
    #     dup_pair_seq = {}
    #     for og_id in dup_pair_dict:
    #         for c_id in dup_pair_dict[og_id]:
    #             s1_g_list = dup_pair_dict[og_id][c_id][0]
    #             s2_g_list = dup_pair_dict[og_id][c_id][1]

    #             for i in s1_g_list:
    #                 sp_id, gene_id = i
    #                 gene_id = gene_id.split("_")[1]
    #                 gi = Gene(gene_id, sp_id, model_aa_seq=sp_info_dict[sp_id].pt_dict[gene_id].seq,
    #                           model_cds_seq=sp_info_dict[sp_id].cds_dict[gene_id].seq)

    #                 for j in s2_g_list:
    #                     sp_id, gene_id = j
    #                     gene_id = gene_id.split("_")[1]
    #                     gj = Gene(
    #                         gene_id, sp_id, model_aa_seq=sp_info_dict[sp_id].pt_dict[gene_id].seq, model_cds_seq=sp_info_dict[sp_id].cds_dict[gene_id].seq)

    #                     dup_pair_seq[(gi, gj)] = (og_id, c_id)

    #     # get Ks for all pair

    #     Ks_dict = get_gene_pair_Ks(list(dup_pair_seq.keys()))

    #     all_Ks_gene_pair_dict[test_node] = dup_pair_seq, Ks_dict

    # import pickle

    # pyb_file = '/lustre/home/xuyuxing/Work/Gel/orcWGD/all_Ks_gene_pair_dict.pyb'
    # OUT = open(pyb_file, 'wb')
    # pickle.dump(all_Ks_gene_pair_dict, OUT)
    # OUT.close()

    # #
    import pickle

    pyb_file = '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/all_Ks_gene_pair_dict.pyb'
    TEMP = open(pyb_file, 'rb')
    all_Ks_gene_pair_dict = pickle.load(TEMP)
    TEMP.close()

    # retend gene
    def test_a_node(test_node, ks_judge_function):
        import numpy as np

        DS_dict, dup_pair_dict, all_gene_dict = check_duplication_for_all_tree_one_node(
            OGs, gene_tree_dir, species_tree, test_node, if_tandom)

        dup_pair_seq, Ks_dict = all_Ks_gene_pair_dict[test_node]

        node_Ks_dict = {}

        for i in dup_pair_seq:
            if dup_pair_seq[i] not in node_Ks_dict:
                node_Ks_dict[dup_pair_seq[i]] = []
            if (i[0], i[1]) in Ks_dict:
                node_Ks_dict[dup_pair_seq[i]].append(Ks_dict[(i[0], i[1])])
            elif (i[1], i[0]) in Ks_dict:
                node_Ks_dict[dup_pair_seq[i]].append(Ks_dict[(i[1], i[0])])

        # filter by ks
        D_node_list = []
        S_node_list = []
        D_node_list_raw = []
        S_node_list_raw = []
        for og_id in DS_dict:
            S_node_list_raw.extend([(og_id, i) for i in DS_dict[og_id]['S']])
            D_node_list_raw.extend([(og_id, i) for i in DS_dict[og_id]['D']])

            S_node_list.extend([(og_id, i) for i in DS_dict[og_id]['S']])

            filter_out_D_node_id = []
            for d_node in DS_dict[og_id]['D']:
                ks_list = node_Ks_dict[(og_id, d_node)]
                if len(ks_list) > 0:
                    ks = np.median(ks_list)
                    # if (0.0 < ks < 1.0):
                    if ks_judge_function(ks):
                        D_node_list.append((og_id, d_node))
                    else:
                        S_node_list.append((og_id, d_node))
                else:
                    S_node_list.append((og_id, d_node))

        print(len(D_node_list), len(D_node_list + S_node_list),
              len(D_node_list)/len(D_node_list + S_node_list))

        # GO
        # prepare gene list
        fore_node_dict = {}
        for og_id, node_id in D_node_list:
            fore_node_dict[(og_id, node_id)] = all_gene_dict[og_id][node_id]

        back_node_dict = {}
        for og_id, node_id in D_node_list + S_node_list:
            back_node_dict[(og_id, node_id)] = all_gene_dict[og_id][node_id]

        # map function
        fore_node_go_dict = {}
        for og_id, node_id in fore_node_dict:
            node_function = []
            for sp_id, g_id in fore_node_dict[(og_id, node_id)]:
                g_id = g_id.split("_")[1]
                if g_id in sp_info_dict[sp_id].go_dict:
                    node_function.extend(sp_info_dict[sp_id].go_dict[g_id])
            fore_node_go_dict[(og_id, node_id)] = list(set(node_function))

        back_node_go_dict = {}
        for og_id, node_id in back_node_dict:
            node_function = []
            for sp_id, g_id in back_node_dict[(og_id, node_id)]:
                g_id = g_id.split("_")[1]
                if g_id in sp_info_dict[sp_id].go_dict:
                    node_function.extend(sp_info_dict[sp_id].go_dict[g_id])
            back_node_go_dict[(og_id, node_id)] = list(set(node_function))

        # GO enrich
        from toolbiox.api.xuyuxing.resource.GO import GO_enrichment_by_topGO
        fore_nodename_list = [i[0] + "_" + i[1] for i in fore_node_go_dict]
        back_nodename_dict = {i[0] + "_" + i[1]                              : back_node_go_dict[i] for i in back_node_go_dict}

        GO_dict = GO_enrichment_by_topGO(
            fore_nodename_list, back_nodename_dict, Ontology='BP')

        import pandas as pd

        df = pd.DataFrame(columns=(['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                    'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']))

        for i in GO_dict:
            df.loc[i] = [GO_dict[i][j] for j in ['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                                 'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']]

        writer = pd.ExcelWriter(
            '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/'+test_node+".xlsx")
        df.to_excel(writer)
        writer.save()

        return fore_nodename_list, back_nodename_dict

    def ks_judge_function_N6(ks):
        return 0.86317289 - 0.2735924 * 1.5 < ks < 0.86317289 + 0.2735924 * 1.5

    def ks_judge_function_Vpl(ks):
        return 8.13054074e-01 - 3.30130199e-01 * 1.5 < ks < 8.13054074e-01 + 3.30130199e-01 * 1.5

    def ks_judge_function_Ash(ks):
        return 7.28064268e-01 - 2.61349661e-01 * 1.5 < ks < 7.28064268e-01 + 2.61349661e-01 * 1.5

    def ks_judge_function_N4(ks):
        return 1.09801254e+00 - 3.49635332e-01 * 1.5 < ks < 1.09801254e+00 + 3.49635332e-01 * 1.5

    def ks_judge_function_Aof(ks):
        return 0.2 < ks < 2

    def ks_judge_function_N9(ks):
        return 6.76080024e-01 - 3.29107510e-01 * 1.5 < ks < 6.76080024e-01 + 3.29107510e-01 * 1.5

    def ks_judge_function_Acom(ks):
        return 0.2 < ks < 8.39765692e-01 + 6.89888870e-01 * 1.5

    def ks_judge_function_Sly(ks):
        return 6.53568229e-01 - 2.18996450e-01 * 1.5 < ks < 6.53568229e-01 + 2.18996450e-01 * 1.5

    test_node_dict = {
        'N6': {
            'id': 'N6',
            'function': ks_judge_function_N6,
        },
        'Vpl': {
            'id': 'Vpl',
            'function': ks_judge_function_Vpl,
        },
        'Ash': {
            'id': 'Ash',
            'function': ks_judge_function_Ash,
        },
        'N4': {
            'id': 'N4',
            'function': ks_judge_function_N4,
        },
        'Aof': {
            'id': 'Aof',
            'function': ks_judge_function_Aof,
        },
        'N6': {
            'id': 'N6',
            'function': ks_judge_function_N6,
        },
        'N9': {
            'id': 'N9',
            'function': ks_judge_function_N9,
        },
        'Acom': {
            'id': 'Acom',
            'function': ks_judge_function_Acom,
        },
        'Sly': {
            'id': 'Sly',
            'function': ks_judge_function_Sly,
        }
    }

    for test_node in test_node_dict:
        fore_nodename_list, back_nodename_dict = test_a_node(
            test_node, test_node_dict[test_node]['function'])
        test_node_dict[test_node]['output'] = (
            fore_nodename_list, back_nodename_dict)

    # for OG level
    back_OG_dict = {}
    for test_node in test_node_dict:
        fore_nodename_list, back_nodename_dict = test_node_dict[test_node]['output']
        for i in back_nodename_dict:
            og_id, node_id = i.split("_", 1)
            if not og_id in back_OG_dict:
                back_OG_dict[og_id] = []
            back_OG_dict[og_id].extend(back_nodename_dict[i])

    for i in back_OG_dict:
        back_OG_dict[i] = list(set(back_OG_dict[i]))

    from toolbiox.api.xuyuxing.resource.GO import GO_enrichment_by_topGO
    import pandas as pd

    fore_OG_dict = {}
    for test_node in test_node_dict:
        fore_nodename_list, back_nodename_dict = test_node_dict[test_node]['output']
        fore_OG_dict[test_node] = list(
            set([i.split("_", 1)[0] for i in fore_nodename_list]))
        print(test_node, len(fore_OG_dict[test_node]))

        GO_dict = GO_enrichment_by_topGO(
            fore_OG_dict[test_node], back_OG_dict, Ontology='BP')

        df = pd.DataFrame(columns=(['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                    'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']))

        for i in GO_dict:
            df.loc[i] = [GO_dict[i][j] for j in ['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                                 'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']]

        writer = pd.ExcelWriter(
            '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/'+test_node+".OG_level.xlsx")
        df.to_excel(writer)
        writer.save()

    # core Kp gene
    sum_OG_list = []
    for test_node in ['Sly', 'Acom', 'Aof', 'N9']:
        sum_OG_list.extend(fore_OG_dict[test_node])

    from collections import Counter

    sum_OG_counter = Counter(sum_OG_list)
    core_Kp_OG = [i for i in sum_OG_counter if sum_OG_counter[i] >= 3]

    GO_dict = GO_enrichment_by_topGO(core_Kp_OG, back_OG_dict, Ontology='BP')

    df = pd.DataFrame(columns=(['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']))

    for i in GO_dict:
        df.loc[i] = [GO_dict[i][j] for j in ['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                             'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']]

    writer = pd.ExcelWriter(
        '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/coreKP.OG_level.xlsx')
    df.to_excel(writer)
    writer.save()

    # venn
    import toolbiox.api.xuyuxing.plot.VennDiagram as venn

    for test_node in fore_OG_dict:
        labels, set_collections = venn.get_labels([fore_OG_dict[test_node], list(set(core_Kp_OG))], fill=['number'],
                                                  return_set_collections=True)

        print(test_node, labels, int(
            labels['11'])/(int(labels['11'])+int(labels['10'])))

    for test_node in fore_OG_dict:
        labels, set_collections = venn.get_labels([list(set(fore_OG_dict[test_node] + fore_OG_dict['N4'])), list(set(core_Kp_OG))], fill=['number'],
                                                  return_set_collections=True)

        print(test_node, labels, int(
            labels['11'])/(int(labels['11'])+int(labels['10'])))

    # N46
    only_N46_list = list(
        set(fore_OG_dict['N6'] + fore_OG_dict['N4']) - set(core_Kp_OG))

    GO_dict = GO_enrichment_by_topGO(
        only_N46_list, back_OG_dict, Ontology='BP')

    df = pd.DataFrame(columns=(['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']))

    for i in GO_dict:
        df.loc[i] = [GO_dict[i][j] for j in ['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                             'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']]

    writer = pd.ExcelWriter(
        '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/only_N46.OG_level.xlsx')
    df.to_excel(writer)
    writer.save()

    # N46
    N46_list = list(set(fore_OG_dict['N6'] + fore_OG_dict['N4']))

    GO_dict = GO_enrichment_by_topGO(N46_list, back_OG_dict, Ontology='BP')

    df = pd.DataFrame(columns=(['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']))

    for i in GO_dict:
        df.loc[i] = [GO_dict[i][j] for j in ['GO_id', 'Rank_in_weight', 'Term', 'Annotated',
                                             'Significant', 'Expected', 'Rank_in_classic', 'classic', 'KS', 'weight']]

    writer = pd.ExcelWriter(
        '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/WGD/N46.OG_level.xlsx')
    df.to_excel(writer)
    writer.save()

    # -----------------
    # get speciation Ks
    work_dir = '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/speciation'
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder_old/pt_file/OrthoFinder/Results_Jun01/Species_Tree/SpeciesTree_rooted.txt"
    orthogroups_for_species_tree = '/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder_old/pt_file/OrthoFinder/Results_Jun01/Species_Tree/Orthogroups_for_concatenated_alignment.txt'
    OG_tsv_file = '/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder_old/pt_file/OrthoFinder/Results_Jun01/Orthogroups/Orthogroups.tsv'
    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'

    from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
    from toolbiox.lib.common.fileIO import read_list_file
    from toolbiox.lib.common.genome.genome_feature2 import Gene
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
    from Bio import Phylo
    from toolbiox.lib.common.evolution.tree_operate import draw_ascii, add_clade_name, lookup_by_names

    # read species
    species_tree = Phylo.read(species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)
    species_tree_node_dict = lookup_by_names(species_tree)
    draw_ascii(species_tree, clade_name=True)
    sp_list = [i.name for i in species_tree.get_terminals()]
    sp_info_dict = read_species_info(ref_xlsx)
    sp_info_dict = {i: sp_info_dict[i] for i in sp_info_dict if i in sp_list}

    # read fasta
    for sp_id in sp_info_dict:
        sp = sp_info_dict[sp_id]
        sp.cds_dict = read_fasta_by_faidx(sp.cds_file)
        sp.pt_dict = read_fasta_by_faidx(sp.pt_file)

    # read OGs
    OGs = OrthoGroups('for_speciation', OG_tsv_file, species_list=sp_list)
    used_GO_list = read_list_file(orthogroups_for_species_tree)

    # running Ks
    spec_pair_seq = {}
    for test_node_id in species_tree_node_dict:
        test_node = species_tree_node_dict[test_node_id]
        if test_node.is_terminal():
            continue
        s1 = test_node.clades[0]
        s2 = test_node.clades[1]

        sp1 = [i.name for i in s1.get_terminals()]
        sp2 = [i.name for i in s2.get_terminals()]

        print(sp1, sp2)

        # get gene pair seq
        for og_id in used_GO_list:
            og = OGs.OG_dict[og_id]
            sp1_gene_list = []
            for sp_id in sp1:
                for gene in og.gene_dict[sp_id]:
                    gene.sp_id = sp_id
                    gene.model_aa_seq = sp_info_dict[sp_id].pt_dict[gene.id].seq
                    gene.model_cds_seq = sp_info_dict[sp_id].cds_dict[gene.id].seq
                    sp1_gene_list.append(gene)

            sp2_gene_list = []
            for sp_id in sp2:
                for gene in og.gene_dict[sp_id]:
                    gene.sp_id = sp_id
                    gene.model_aa_seq = sp_info_dict[sp_id].pt_dict[gene.id].seq
                    gene.model_cds_seq = sp_info_dict[sp_id].cds_dict[gene.id].seq
                    sp2_gene_list.append(gene)

            for i in sp1_gene_list:
                for j in sp2_gene_list:
                    if i == j:
                        continue
                    spec_pair_seq[(i, j)] = (og_id, test_node_id)

    Ks_dict = get_gene_pair_Ks(list(spec_pair_seq.keys()))

    import pickle

    pyb_file = '/lustre/home/xuyuxing/Work/Gel/orcWGD/Ks/speciation/all_Ks_gene_pair_dict.pyb'
    OUT = open(pyb_file, 'wb')
    pickle.dump((spec_pair_seq, Ks_dict), OUT)
    OUT.close()
