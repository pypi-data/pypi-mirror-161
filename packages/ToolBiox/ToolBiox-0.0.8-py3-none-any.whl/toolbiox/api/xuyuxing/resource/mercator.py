"""
This file work for Mercator output

Mercator4 v2.0 x (July 2019)

https://www.plabipd.de/portal/web/guest/mercator4
"""
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import re
from collections import OrderedDict
import copy


class MapmanFunction(object):
    def __init__(self, bin_code, name=None, terminal=None, sons=None):
        self.bin_code = bin_code
        self.name = name
        # self.description = description
        self.terminal = terminal
        self.sons = sons

        self.depth = len(get_ancestors_id_list(bin_code)) + 1
        self.ancestors = get_ancestors_id_list(bin_code)
        self.parent = get_parent_id(bin_code)

    def __str__(self):
        return '%s: %s (%d)' % (self.bin_code, self.name, self.depth)

    __repr__ = __str__


class MapmanTree(object):
    def __init__(self, mercator_results_file):
        mercator_info_dict = tsv_file_dict_parse(mercator_results_file)

        mercator_dict = {}
        parent_dict = {}
        for i in mercator_info_dict:
            bin_code = re.sub("'", "", mercator_info_dict[i]['BINCODE'])
            name = re.sub(
                "'", "", mercator_info_dict[i]['NAME'].split(".")[-1])
            # description = re.sub("'","",mercator_info_dict[i]['DESCRIPTION'])
            mercator_dict[bin_code] = MapmanFunction(bin_code, name=name)
            parent_dict[bin_code] = mercator_dict[bin_code].parent

        parent_hash_dict = {}
        for i in parent_dict:
            j = parent_dict[i]
            if j:
                if j not in parent_hash_dict:
                    parent_hash_dict[j] = []
                parent_hash_dict[j].append(i)

        for bin_code in mercator_dict:
            if bin_code not in parent_hash_dict:
                mercator_dict[bin_code].terminal = True
                mercator_dict[bin_code].sons = []
            else:
                mercator_dict[bin_code].terminal = False
                mercator_dict[bin_code].sons = sorted(
                    parent_hash_dict[bin_code])

        self.mercator_results_file = mercator_results_file

        for bin_code in mercator_dict:
            mercator_dict[bin_code].sons = [mercator_dict[i]
                                            for i in mercator_dict[bin_code].sons]
            mercator_dict[bin_code].ancestors = [mercator_dict[i]
                                                 for i in mercator_dict[bin_code].ancestors]
            if mercator_dict[bin_code].parent:
                mercator_dict[bin_code].parent = mercator_dict[mercator_dict[bin_code].parent]

        self.mercator_dict = OrderedDict()
        for i in sorted(list(mercator_dict.keys())):
            self.mercator_dict[i] = mercator_dict[i]

    def get(self, bin_code):
        return self.mercator_dict[bin_code]

    def browse(self, depth=None):
        for i in self.mercator_dict:
            if depth:
                if self.get(i).depth == depth:
                    yield self.mercator_dict[i]
            else:
                yield self.mercator_dict[i]

    def load_annotation(self, gene_bincode_map):
        for i in self.mercator_dict:
            self.mercator_dict[i].genes = []

        for g_id, bin_code in gene_bincode_map:
            self.mercator_dict[bin_code].genes.append(g_id)

    def get_genes(self, bin_code):
        gene_list = self.mercator_dict[bin_code].genes
        for son in self.mercator_dict[bin_code].sons:
            son_bin_code = son.bin_code
            gene_list.extend(self.get_genes(son_bin_code))

        gene_list = list(set(gene_list))

        if '' in gene_list:
            gene_list.remove('')

        return gene_list


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


def get_gene_bincode_map(mercator_results_file):
    mercator_info_dict = tsv_file_dict_parse(mercator_results_file)
    gene_bincode_map = []
    for i in mercator_info_dict:
        bin_code = re.sub("'", "", mercator_info_dict[i]['BINCODE'])
        gene_id = re.sub(
            "'", "", mercator_info_dict[i]['IDENTIFIER'])
        gene_bincode_map.append((gene_id, bin_code))
    return gene_bincode_map


def load_annotation(mapman, gene_bincode_map):
    output_mapman = copy.deepcopy(mapman)
    output_mapman.load_annotation(gene_bincode_map)
    return output_mapman


if __name__ == "__main__":
    mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Dendrobium_catenatum/T906689N0.gene_model.protein.Mercator.results.txt'

    mapman = MapmanTree(mercator_results_file)

    Dca_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Dendrobium_catenatum/T906689N0.gene_model.protein.Mercator.results.txt'
    Gel_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/T91201N0.gene_model.protein.Mercator.results.txt'
    Cau_mercator_results_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/T267555N0.gene_model.protein.Mercator.results.txt'

    Dca_mapman = load_annotation(
        mapman, get_gene_bincode_map(Dca_mercator_results_file))
    Gel_mapman = load_annotation(
        mapman, get_gene_bincode_map(Gel_mercator_results_file))
    Cau_mapman = load_annotation(
        mapman, get_gene_bincode_map(Cau_mercator_results_file))
