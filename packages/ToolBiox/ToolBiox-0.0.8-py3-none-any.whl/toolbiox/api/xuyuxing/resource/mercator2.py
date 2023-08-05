"""
This file work for Mercator output

Mercator4 v2.0 x (July 2019)

https://www.plabipd.de/portal/web/guest/mercator4
"""
from Bio.Phylo.BaseTree import Tree, Clade
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import re
from collections import OrderedDict
import copy


def get_parent_id(bincode):
    parent_id = ".".join(bincode.split(".")[:-1])
    if parent_id == '':
        return None
    else:
        return parent_id


def get_ancestors_id_list(bincode):
    ancestors_id_list = []
    lastcode = bincode
    flag = True
    while flag:
        parent_id = get_parent_id(lastcode)
        if parent_id:
            ancestors_id_list.append(parent_id)
            lastcode = parent_id
        else:
            flag = False
    return sorted(ancestors_id_list)


class MapmanFunction(Clade):
    def __init__(
        self,
        bin_code,
        name=None,
    ):
        super(MapmanFunction, self).__init__(
            branch_length=None,
            name=name,
            clades=None,
            confidence=None,
            color=None,
            width=None,
        )

        self.bin_code = bin_code
        self.depth = len(get_ancestors_id_list(bin_code)) + 1

    def __str__(self):
        return '%s: %s (%d)' % (self.bin_code, self.name, self.depth)

    __repr__ = __str__


class MapmanTree(Tree):
    def __init__(self, mercator_results_file):
        mercator_info_dict = tsv_file_dict_parse(mercator_results_file)

        # add node
        mercator_dict = OrderedDict()
        for i in mercator_info_dict:
            bin_code = re.sub("'", "", mercator_info_dict[i]['BINCODE'])
            name = re.sub(
                "'", "", mercator_info_dict[i]['NAME'].split(".")[-1])
            # description = re.sub("'","",mercator_info_dict[i]['DESCRIPTION'])
            mercator_dict[bin_code] = MapmanFunction(bin_code, name=name)

        # add clade relationship
        top_bin_code = []
        for bin_code in mercator_dict:
            if get_parent_id(bin_code):
                parent_id = get_parent_id(bin_code)
                if mercator_dict[parent_id].clades is None:
                    mercator_dict[parent_id].clades = []
                mercator_dict[parent_id].clades.append(mercator_dict[bin_code])
            else:
                top_bin_code.append(mercator_dict[bin_code])

        root_clade = Clade(clades=top_bin_code, name='root')
        root_clade.bin_code = "0"
        root_clade.depth = 0

        super(MapmanTree, self).__init__(
            root=root_clade,
            rooted=True,
            id=None,
            name=None
        )

    def load_gene_annotation(self, mercator_results_file, sp_id='default_sp_id'):
        mercator_info_dict = tsv_file_dict_parse(mercator_results_file)
        gene_bincode_map = {}
        for i in mercator_info_dict:
            bin_code = re.sub("'", "", mercator_info_dict[i]['BINCODE'])
            gene_id = re.sub(
                "'", "", mercator_info_dict[i]['IDENTIFIER'])
            if bin_code not in gene_bincode_map:
                gene_bincode_map[bin_code] = []
            gene_bincode_map[bin_code].append(gene_id)

        for leaf in self.get_terminals():
            if not hasattr(leaf, 'genes'):
                leaf.genes = {}
            leaf.genes[sp_id] = []

        for leaf in self.get_terminals():
            gene_list_tmp = list(set(leaf.genes[sp_id] + gene_bincode_map[leaf.bin_code]))
            try:
                gene_list_tmp.remove('')
            except:
                pass

            leaf.genes[sp_id] = gene_list_tmp

        self.sp_list = list(set(leaf.genes.keys()))

    def get_genes(self, bin_code, sp_id='default_sp_id'):
        target_clade = None
        for clade in self.find_clades(order='preorder'):
            if clade.bin_code == bin_code:
                target_clade = clade
                break

        gene_list = []
        if target_clade:
            for leaf in target_clade.get_terminals():
                gene_list += leaf.genes[sp_id]

        gene_list = list(set(gene_list))
        gene_list.remove('')

        return gene_list


if __name__ == "__main__":
    mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Dendrobium_catenatum/T906689N0.gene_model.protein.Mercator.results.txt'

    mtree = MapmanTree(mercator_results_file)

    # mtree can work as Bio Tree and Clade

    Dca_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Dendrobium_catenatum/T906689N0.gene_model.protein.Mercator.results.txt'
    Gel_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/T91201N0.gene_model.protein.Mercator.results.txt'
    Cau_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/T267555N0.gene_model.protein.Mercator.results.txt'

    mtree.load_gene_annotation(Dca_mercator_results_file, 'Dca')
    mtree.load_gene_annotation(Gel_mercator_results_file, 'Gel')
    mtree.load_gene_annotation(Cau_mercator_results_file, 'Cau')