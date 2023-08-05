from toolbiox.lib.common.genome.genome_feature2 import Gene, GeneSet
from collections import OrderedDict
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.util import printer_list
import pandas as pd
# from toolbiox.lib.common.evolution.tree_operate import get_top_taxon_clade, get_root_by_species, add_clade_name, lookup_by_names, reroot_by_outgroup_clade, collapse_low_support, get_rooted_tree_by_species_tree
from toolbiox.lib.common.evolution.tree_operate import get_top_taxon_clade
from Bio import Phylo

__author__ = 'Yuxing Xu'


def if_conserved(species_list, conserved_arguments):
    """
    conserved_arguments = [
        [['Cau', 'Ini', 'Sly'], ['Ath', 'Aco']],
        [2,2]
    ]
    """
    sp_group_lol = conserved_arguments[0]
    group_min_num_list = conserved_arguments[1]

    conserved_flag = True

    for sp_group_list, min_num in zip(sp_group_lol, group_min_num_list):
        if len(set(species_list) & set(sp_group_list)) < min_num:
            conserved_flag = False

    return conserved_flag


class OrthoGroup(GeneSet):
    def __init__(self, id=None, from_gene_list=None, species_list=None, from_OG_dict=None, properties=None):
        if from_OG_dict and from_gene_list is None:
            if not species_list:
                species_list = list(from_OG_dict.keys())

            from_gene_list = []
            for sp_id in from_OG_dict:
                for g_id in from_OG_dict[sp_id]:
                    from_gene_list.append(Gene(id=g_id, species=sp_id))

        if species_list:
            gene_dict = {i: [] for i in species_list}
        else:
            gene_dict = {}
            for i in from_gene_list:
                gene_dict[i.species] = []

        gene_list = [i for i in from_gene_list if i.species in gene_dict]

        super(OrthoGroup, self).__init__(id=id, gene_list=gene_list)

        self.gene_dict = gene_dict
        for i in self.gene_list:
            self.gene_dict[i.species].append(i)

        self.species_stat = {}
        for sp_id in self.gene_dict:
            self.species_stat[sp_id] = len(self.gene_dict[sp_id])

        self.species_list = list(self.species_stat.keys())

        self.properties = properties

    def conserved(self, conserved_arguments):
        non_zero_species_list = [
            i for i in self.species_stat if self.species_stat[i] != 0]

        return if_conserved(non_zero_species_list, conserved_arguments)


class OrthoGroups(object):
    def __init__(self, id=None, OG_tsv_file=None, from_OG_dict=None, from_OG_list=None, species_list=None, note=None, new_OG_name=False):
        self.id = id
        self.note = note
        self.OG_tsv_file = OG_tsv_file
        self.from_OG_dict = from_OG_dict

        if OG_tsv_file:
            OG_dict = self.build_from_OG_tsv_file(
                OG_tsv_file, species_list=species_list)
        elif from_OG_dict:
            OG_dict = self.build_from_OG_dict(
                from_OG_dict, species_list=species_list)
        elif from_OG_list:
            OG_dict = self.build_from_OG_list(
                from_OG_list, species_list=species_list, new_OG_name=new_OG_name)
        else:
            OG_dict = OrderedDict()

        self.OG_dict = OG_dict
        if species_list:
            self.species_list = species_list
        else:
            self.species_list = OG_dict[list(OG_dict.keys())[0]].species_list
        self.OG_id_list = list(self.OG_dict.keys())

    def get(self, key_tuple):
        """
        key_tuple: ('OG1234', 'Ath'), or ('OG1234', None), or (None, 'Ath')
        """

        OG_id, sp_id = key_tuple

        if OG_id and sp_id:
            return self.OG_dict[OG_id].gene_dict[sp_id]
        elif OG_id:
            return self.OG_dict[OG_id].gene_dict
        elif sp_id:
            output_dict = {}
            for i in self.OG_dict:
                output_dict[i] = self.OG_dict[i].gene_dict[sp_id]
            return output_dict

    def build_from_OG_tsv_file(self, OG_tsv_file, species_list=None):
        file_info = tsv_file_dict_parse(OG_tsv_file)

        full_species_list = list(
            file_info[list(file_info.keys())[0]].keys())[1:]

        OG_dict = OrderedDict()

        for i in file_info:
            OG_id = file_info[i]['Orthogroup']

            gene_list = []
            for j in file_info[i]:
                if j == 'Orthogroup':
                    continue
                if file_info[i][j] == '' or file_info[i][j] is None:
                    continue
                gene_list.extend([Gene(id=k, species=j)
                                  for k in file_info[i][j].split(", ")])

            if species_list:
                OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=species_list)
            else:
                OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=full_species_list)

        return OG_dict

    def build_from_OG_dict(self, OG_dict, species_list=None):
        """
        OG_dict = {
            "OG0001": {
                "Ath": ['AT0001', 'AT0002'],
                "Osa": ['OS0001', 'OS0002']
            }
        }
        """
        new_OG_dict = OrderedDict()

        for OG_id in OG_dict:

            if isinstance(OG_dict[OG_id], dict):
                gene_list = []
                for sp_id in OG_dict[OG_id]:
                    gene_list.extend([Gene(id=i, species=sp_id)
                                      for i in OG_dict[OG_id][sp_id]])
                new_OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=species_list)
            else:
                new_OG_dict[OG_id] = OG_dict[OG_id]

        return new_OG_dict

    def build_from_OG_list(self, OG_list, species_list=None, new_OG_name=False):
        if species_list:
            all_species_list = species_list
        else:
            all_species_list = []
            for og in OG_list:
                all_species_list.extend(og.species_list)
            all_species_list = list(set(all_species_list))

        new_OG_dict = OrderedDict()

        num = 0
        for og in OG_list:
            if new_OG_name:
                og_id = "OG%d" % num
                num += 1
            else:
                og_id = og.id

            gene_list = [
                gene for gene in og.gene_list if gene.species in set(all_species_list)]
            new_OG_dict[og_id] = OrthoGroup(
                id=og_id, from_gene_list=gene_list, species_list=all_species_list)

        return new_OG_dict

    def write_OG_tsv_file(self, output_file, species_list=None):
        if not species_list:
            species_list = self.species_list

        with open(output_file, 'w') as f:
            f.write(printer_list(species_list, head='Orthogroup\t')+"\n")

            for OG_id in self.OG_dict:
                OG = self.OG_dict[OG_id]
                string_list = []
                for sp_id in species_list:
                    string_list.append(printer_list(
                        [i.id for i in OG.gene_dict[sp_id]], sep=', '))
                output_string = printer_list(string_list, head=OG_id+"\t")
                f.write(output_string+"\n")

        return output_file

    def write_OG_num_file(self, output_file, species_list=None):
        if not species_list:
            species_list = self.species_list

        with open(output_file, 'w') as f:
            f.write(printer_list(species_list, head='Orthogroup\t')+"\n")

            for OG_id in self.OG_dict:
                OG = self.OG_dict[OG_id]
                string_list = []
                for sp_id in species_list:
                    string_list.append(len(
                        [i.id for i in OG.gene_dict[sp_id]]))
                output_string = printer_list(string_list, head=OG_id+"\t")
                f.write(output_string+"\n")

        return output_file

    def get_conserved_OG_list(self, conserved_arguments):

        output_list = []
        for i in self.OG_dict:  
            og = self.OG_dict[i]
            if og.conserved(conserved_arguments):
                output_list.append(i)

        return output_list

    def remove_some_OG(self, removed_OG_list):
        for i in removed_OG_list:
            self.OG_id_list.remove(i)
            del self.OG_dict[i]


class Species(object):
    def __init__(self,
                 sp_id=None,
                 taxon_id=None,
                 species_name=None,
                 genome_file=None,
                 gff_file=None,
                 pt_file=None,
                 cDNA_file=None,
                 cds_file=None):

        self.sp_id = sp_id
        self.taxon_id = taxon_id
        self.species_name = species_name
        self.genome_file = genome_file
        self.gff_file = gff_file
        self.pt_file = pt_file
        self.cDNA_file = cDNA_file
        self.cds_file = cds_file


def read_species_info(species_info_table, add_option=[]):
    species_info_df = pd.read_excel(species_info_table)
    species_info_dict = {}
    for index in species_info_df.index:
        sp_id = str(species_info_df.loc[index]['sp_id'])

        base_info_dict = {i: None for i in [
            'taxon_id', 'species_name', 'genome_file', 'gff_file', 'pt_file', 'cDNA_file', 'cds_file']}

        for i in base_info_dict:
            if i in species_info_df.loc[index]:
                base_info_dict[i] = species_info_df.loc[index][i]

        species_info_dict[sp_id] = Species(
            sp_id, base_info_dict['taxon_id'], base_info_dict['species_name'], base_info_dict['genome_file'], base_info_dict['gff_file'], base_info_dict['pt_file'], base_info_dict['cDNA_file'], base_info_dict['cds_file'])

        for i in add_option:
            if i in species_info_df.loc[index]:
                setattr(species_info_dict[sp_id], i,
                        species_info_df.loc[index][i])

    return species_info_dict


# about get orthoclade from tree
def treeclade_to_OG(clade, species_list, og_id=None):
    if not og_id:
        og_id = clade.name

    # g_id_list = [leaf.name for leaf in clade.get_terminals()]
    gene_list = [Gene(id=leaf.name, species=leaf.taxon)
                 for leaf in clade.get_terminals()]
    og = OrthoGroup(id=og_id, from_gene_list=gene_list,
                    species_list=species_list)

    return og


def get_orthogroups_from_gene_tree(taxon_labeled_tree, species_tree, taxonomy_level=None, conserved_arguments=None):
    all_sp_list = [i.name for i in species_tree.get_terminals()]

    if taxonomy_level is None:
        taxonomy_level = species_tree.root.name

    if conserved_arguments is None:
        conserved_arguments = [
            [all_sp_list],
            [0]
        ]

    top_speciation_clade_list = get_top_taxon_clade(
        taxon_labeled_tree, species_tree, taxonomy_level, node_type='speciation')

    og_list = []
    for clade in top_speciation_clade_list:
        clade_taxon_list = [i.taxon for i in clade.get_terminals()]
        if if_conserved(clade_taxon_list, conserved_arguments):
            og = treeclade_to_OG(clade, all_sp_list)
            og_list.append(og)

    return og_list


# def get_conserved_clades(rooted_tree_node_dict, gene_to_species_map_dict, conserved_function, conserved_arguments):
#     """
#     filter all conserved clades on a rooted tree, return clades may overlap with each other
#     """
#     conserved_clades = []
#     for clade_id in rooted_tree_node_dict:
#         clade = rooted_tree_node_dict[clade_id]
#         if not clade.is_terminal():
#             sp_list = list(set([gene_to_species_map_dict[leaf.name]
#                                 for leaf in clade.get_terminals()]))
#             if conserved_function(sp_list, conserved_arguments):
#                 conserved_clades.append(clade_id)
#     return conserved_clades


# def get_orthogroups_from_tree(tree_prefix, gene_tree, species_tree, gene_to_species_map_dict, conserved_function, conserved_arguments, support_threshold):
#     """
#     warning: this function will get multi-level OGs at sametime
#     """
#     # root gene tree
#     gene_tree = add_clade_name(gene_tree)
#     gene_tree_node_dict = lookup_by_names(gene_tree)

#     best_root_clade = get_root_by_species(
#         gene_tree, species_tree, gene_to_species_map_dict)

#     gene_tree_rooted, gene_tree_rooted_node_dict, gene_tree, gene_tree_node_dict = reroot_by_outgroup_clade(gene_tree,
#                                                                                                             gene_tree_node_dict,
#                                                                                                             best_root_clade.name,
#                                                                                                             True)

#     # collapse low support clades
#     gene_tree_rooted_collapsed = collapse_low_support(
#         gene_tree_rooted, support_threshold)
#     gene_tree_rooted_collapsed = add_clade_name(gene_tree_rooted_collapsed)
#     gene_tree_rooted_collapsed_node_dict = lookup_by_names(
#         gene_tree_rooted_collapsed)

#     # get conserved clades
#     conserved_clades_id_list = get_conserved_clades(
#         gene_tree_rooted_collapsed_node_dict, gene_to_species_map_dict, conserved_function, conserved_arguments)

#     # get sub_orthogroups
#     num = 0

#     orthogroup_id = "%s_%d" % (tree_prefix, num)
#     zero_clade_conserved = conserved_function(list(set(
#         [gene_to_species_map_dict[leaf.name] for leaf in gene_tree_rooted_collapsed.get_terminals()])), conserved_arguments)
#     sub_orthogroup_dict = {orthogroup_id: (
#         [leaf.name for leaf in gene_tree_rooted_collapsed.get_terminals()], zero_clade_conserved)}

#     for clade_id in conserved_clades_id_list:
#         num += 1
#         orthogroup_id = "%s_%d" % (tree_prefix, num)
#         clade = gene_tree_rooted_collapsed_node_dict[clade_id]
#         sub_orthogroup_dict[orthogroup_id] = (
#             [leaf.name for leaf in clade.get_terminals()], True)

#     for orthogroup_id in sub_orthogroup_dict:
#         tmp_dict = {}
#         for i in sub_orthogroup_dict[orthogroup_id][0]:
#             if not gene_to_species_map_dict[i] in tmp_dict:
#                 tmp_dict[gene_to_species_map_dict[i]] = []
#             tmp_dict[gene_to_species_map_dict[i]].append(i)
#         sub_orthogroup_dict[orthogroup_id] = tmp_dict

#     sp_list = [leaf.name for leaf in species_tree.get_terminals()]
#     sub_OGs = OrthoGroups(
#         id=tree_prefix, from_OG_dict=sub_orthogroup_dict, species_list=sp_list)

#     return sub_OGs


def if_sub_OG(A_OG, B_OG):
    """
    if A is a sub OG of B
    """

    A_gene_set = set([(i.id, i.species) for i in A_OG.gene_list])
    B_gene_set = set([(i.id, i.species) for i in B_OG.gene_list])

    return A_gene_set & B_gene_set == A_gene_set


def get_non_overlap_orthogroups(OGs):
    exclude_list = []
    for i in OGs.OG_id_list:
        for j in OGs.OG_id_list:
            if i == j:
                continue
            else:
                if if_sub_OG(OGs.OG_dict[i], OGs.OG_dict[j]):
                    exclude_list.append(j)

    exclude_list = set(exclude_list)

    used_OG_dict = OrderedDict()
    for i in OGs.OG_dict:
        if not i in exclude_list:
            used_OG_dict[i] = OGs.OG_dict[i]

    return OrthoGroups(from_OG_dict=used_OG_dict, species_list=OGs.species_list)


def merge_OGs(OGs_list):

    OG_dict = {}
    species_list = []
    for ogs in OGs_list:
        species_list.extend(ogs.species_list)
        for i in ogs.OG_dict:
            OG_dict[i] = ogs.OG_dict[i]
    species_list = list(set(species_list))

    return OrthoGroups(from_OG_dict=OG_dict, species_list=species_list)


def OG_gene_rename(OG, rename_dict):
    """
    rename_dict: key: old_id, value: new_id
    """

    gene_list_new = [Gene(id=rename_dict[gene.id], species=gene.species)
                     for gene in OG.gene_list]

    return OrthoGroup(id=OG.id, from_gene_list=gene_list_new, species_list=OG.species_list)


def OGs_gene_rename(OGs, rename_dict):
    """
    rename_dict: key: old_id, value: new_id
    """

    OG_dict = {}
    for i in OGs.OG_dict:
        og = OGs.OG_dict[i]
        new_og = OG_gene_rename(og, rename_dict)
        OG_dict[i] = new_og

    return OrthoGroups(id=OGs.id, OG_tsv_file=None, from_OG_dict=OG_dict, species_list=OGs.species_list, note=OGs.note)


if __name__ == '__main__':
    # read a OG tsv file
    OGs = OrthoGroups(
        OG_tsv_file="/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/pt_file/OrthoFinder/Results_May08/Orthogroups/Orthogroups.tsv")
    OGs.get(('OG0000000', 'Ath'))

    # read a standard species info file: sp_id, taxon_id, species_name, genome_file, gff_file, pt_file, cDNA_file, cds_file
    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'
    sp_info_dict = read_species_info(ref_xlsx)

    # get orthogroups from a gene tree (and species tree)
    from toolbiox.lib.common.fileIO import tsv_file_dict_parse
    from toolbiox.lib.common.evolution.tree_operate import map_node_species_info, add_clade_name, get_rooted_tree_by_species_tree

    normal_gene_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics_old/tree/fasttree/OG0002678/tree.resolve.phb"
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

    taxonomy_level = 'Orchidaceae'
    conserved_arguments = [
        [['Gel', 'Peq', 'Dca', 'Vpl', 'Ash']],
        [3]
    ]

    og_list = get_orthogroups_from_gene_tree(
        rooted_taxon_gene_tree, species_tree, taxonomy_level=taxonomy_level, conserved_arguments=conserved_arguments)

    # get orthogroups from a nhx tree
    from toolbiox.lib.common.evolution.tree_operate import load_nhx_tree

    nhx_file = '/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/phylogenomics/tree/treebest/OG0001138/tree.nhx'
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD_redo/species.tree.txt"

    species_tree = Phylo.read(species_tree_file, 'newick')
    species_tree = add_clade_name(species_tree)

    rooted_taxon_gene_tree, clade_dict = load_nhx_tree(nhx_file)

    taxonomy_level = 'Orchidaceae'
    conserved_arguments = [
        [['Gel', 'Peq', 'Dca', 'Vpl', 'Ash']],
        [3]
    ]

    og_list = get_orthogroups_from_gene_tree(
        rooted_taxon_gene_tree, species_tree, taxonomy_level=taxonomy_level, conserved_arguments=conserved_arguments)
