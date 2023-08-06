from Bio.Phylo.BaseTree import Tree, Clade
from itertools import combinations
from mlxtend.evaluate import permutation_test
from scipy import stats
from toolbiox.lib.common.evolution.tree_operate import Clade, Phylo, reroot_by_outgroup_clade, add_clade_name, lookup_by_names, get_MRCA, remove_given_node_from_tree, remove_pass_node, get_offspring, draw_ascii, get_parent, get_ancestors, get_sons
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.math.set import merge_subset
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.xuyuxing.math.stats import get_qvalue
import copy
import numpy as np
import re
import sqlite3
import toolbiox.lib.common.sqlite_command as sc


class Taxon(object):
    """
    Taxon is a class for each taxon in taxonomy database.
    """

    def __init__(self):
        pass

    # this list is from https://en.wikipedia.org/wiki/Taxonomic_rank
    rank_list = ["superkingdom", "kingdom", "subkingdom", "superphylum", "phylum", "subphylum", "superclass", "class",
                 "subclass", "infraclass", "cohort", "subcohort", "superorder", "order", "suborder", "infraorder",
                 "parvorder", "superfamily", "family", "subfamily", "tribe", "subtribe", "genus", "subgenus", "section",
                 "subsection", "series", "species group", "species subgroup", "species", "subspecies", "varietas",
                 "forma", "strain"]

    def __str__(self):
        return "ID: %s Sci_Name: %s (%s)" % (self.tax_id, self.sci_name, self.rank)

    def get_lineage(self, taxon_dict):
        """
        Get all lineage information from root to given taxon
        :param taxon_dict: The output from func "build_taxon_database"
        :return: a lineage list from root to given taxon
        """
        lineage_list = [(self.tax_id, self.rank)]
        iter_taxon = self
        while not iter_taxon.tax_id == iter_taxon.parent_tax_id:
            iter_taxon = taxon_dict[iter_taxon.parent_tax_id]
            lineage_list.append((iter_taxon.tax_id, iter_taxon.rank))

        return lineage_list[::-1]

    def check_rank(self, tax_record_dict):
        from toolbiox.lib.xuyuxing.math.set_operating import uniqify
        from toolbiox.lib.xuyuxing.math.lcs import lcs
        for i in tax_record_dict:
            temp_list = tuple(
                uniqify([j[1] for j in tax_record_dict[i].get_lineage(tax_record_dict) if
                         j[1] != 'no rank' and j[1] != 'clade']))
            LCS_list = tuple(lcs(temp_list, Taxon.rank_list)[0])
            if not temp_list == LCS_list:
                print(temp_list)
                raise ValueError

    def lower_than(self, rank, tax_record_dict):
        temp_list = tuple([j[1] for j in self.get_lineage(
            tax_record_dict) if j[1] != 'no rank' and j[1] != 'clade'])

        if len(temp_list) == 0:  # Other sequence
            return False

        max_index = max(Taxon.rank_list.index(i) for i in temp_list)

        if max_index >= Taxon.rank_list.index(rank):
            return True
        else:
            return False

    def is_child_of(self, tax_id, tax_record_dict=None):
        if isinstance(self.get_lineage, list):
            parent_list = self.get_lineage
        else:
            parent_list = self.get_lineage(tax_record_dict)

        if tax_id in [i[0] for i in parent_list]:
            return True
        else:
            return False

    def is_ancestor_of(self, tax_id, tax_record_dict):
        taget_tax = tax_record_dict[tax_id]
        if isinstance(taget_tax.get_lineage, list):
            parent_list = tax_record_dict[tax_id].get_lineage
        else:
            parent_list = tax_record_dict[tax_id].get_lineage(tax_record_dict)
        if self.tax_id in [i[0] for i in parent_list]:
            return True
        else:
            return False

    def get_sons(self, tax_record_dict):
        sons_id_list = []
        for i in tax_record_dict:
            i = tax_record_dict[i]
            if self.tax_id == i.parent_tax_id:
                sons_id_list.append(i.tax_id)
        return sons_id_list


def build_taxon_database(taxonomy_dir, full_name_class=False):
    """
    NCBI taxonomy database can be download from: ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
    In the dir a "names.dmp" and a "nodes.dmp" can be found, this func work for parse this two file to fit the class Ta\
    xon.
    :param taxonomy_dir: file path for uncompressed taxdump.tar.gz
    :return: a dict whose key is tax_id and value is a Taxon with attributes named "tax_id", "sci_name", "parent_tax_id\
    ", "rank" and "lineage" (Big memory)
    """
    names_dmp_file = taxonomy_dir + "/names.dmp"
    nodes_dmp_file = taxonomy_dir + "/nodes.dmp"

    tax_record = {}
    with open(names_dmp_file, 'r') as f:
        for each_line in f.readlines():
            each_line = each_line.strip()
            info = each_line.split("|")
            tax_id = re.sub('\t', '', info[0])
            name = re.sub('\t', '', info[1])
            # unique_name = re.sub('\t', '', info[2])
            name_class = re.sub('\t', '', info[3])

            if not tax_id in tax_record:
                tax_record[tax_id] = Taxon()
                tax_record[tax_id].tax_id = tax_id

            if name_class == "scientific name":
                tax_record[tax_id].sci_name = name
            elif full_name_class:
                if not hasattr(tax_record[tax_id], 'other_name'):
                    tax_record[tax_id].other_name = []
                tax_record[tax_id].other_name.append(name)

    with open(nodes_dmp_file, 'r') as f:
        for each_line in f.readlines():
            each_line = each_line.strip()
            info = each_line.split("|")
            tax_id = re.sub('\t', '', info[0])
            parent_tax_id = re.sub('\t', '', info[1])
            rank = re.sub('\t', '', info[2])
            tax_record[tax_id].parent_tax_id = parent_tax_id
            tax_record[tax_id].rank = rank

    for tax_id in tax_record:
        taxon = tax_record[tax_id]
        lineage_list = taxon.get_lineage(tax_record)
        # taxon.lineage = lineage_list
        for i in lineage_list:
            tax_id_tmp, rank_tmp = i
            if not (rank_tmp == 'no rank' or rank_tmp == 'clade'):
                setattr(taxon, rank_tmp, tax_id_tmp)

    merged_dmp = taxonomy_dir + "/merged.dmp"

    merged_record = {}
    with open(merged_dmp, 'r') as f:
        for each_line in f.readlines():
            each_line = each_line.strip()
            info = each_line.split("|")
            merged_id = re.sub('\t', '', info[0])
            new_id = re.sub('\t', '', info[1])
            merged_record[merged_id] = new_id

    for i in merged_record:
        tax_record[i] = copy.deepcopy(tax_record[merged_record[i]])
        tax_record[i].older = True

    return tax_record


def get_MRCA_taxon_id(taxon_id_list, tax_record_dict):
    if len(taxon_id_list) == 1:
        return taxon_id_list[0]

    lineage_sum_list = []
    for tax_id in taxon_id_list:
        tax_tmp = tax_record_dict[tax_id]
        try:
            lineage_list = tax_tmp.get_lineage(tax_record_dict)
        except:
            lineage_list = tax_tmp.get_lineage
        lineage_sum_list.append(lineage_list)

    range_num = min([len(i) for i in lineage_sum_list])

    MRCA = None
    for i in range(0, range_num):
        tmp_taxon_list = [j[i] for j in lineage_sum_list]
        if len(set(tmp_taxon_list)) == 1:
            MRCA = tmp_taxon_list[0]

    return MRCA[0]


def store_tax_record_into_sqlite(tax_record_dict, db_file):
    import time
    from toolbiox.lib.xuyuxing.base.common_command import log_print
    log_print("\t\tBegin: convert NCBI taxonomy database to sqlite3 file")
    start_time = time.time()
    column_name = ["tax_id", "sci_name", "parent_tax_id",
                   "rank", "merged_new_id", "lineage"]
    sc.init_sql_db(db_file, "tax_record", column_name)
    num = 0
    record_tmp_dict = []
    for tax_id in tax_record_dict:
        record_tmp = []
        record_tmp.append(tax_id)
        taxon_tmp = tax_record_dict[tax_id]

        if hasattr(taxon_tmp, "sci_name"):
            record_tmp.append(getattr(taxon_tmp, "sci_name").replace("\"", ""))
        else:
            record_tmp.append("")

        if hasattr(taxon_tmp, "parent_tax_id"):
            record_tmp.append(getattr(taxon_tmp, "parent_tax_id"))
        else:
            record_tmp.append("")

        if hasattr(taxon_tmp, "rank"):
            record_tmp.append(getattr(taxon_tmp, "rank"))
        else:
            record_tmp.append("")

        if hasattr(taxon_tmp, "older"):
            record_tmp.append(getattr(taxon_tmp, "tax_id"))
        else:
            record_tmp.append("")

        lineage_list = taxon_tmp.get_lineage(tax_record_dict)
        lineage_string = ""
        for tax_id_rank, rank in lineage_list:
            lineage_string = lineage_string + "%s:%s;" % (tax_id_rank, rank)
        lineage_string = lineage_string.rstrip(";")
        record_tmp.append(lineage_string)

        num = num + 1
        record_tmp_dict.append(record_tmp)
        # sc.insert_one_record_to_sql_table(tuple(record_tmp), tuple(column_name), db_file, "tax_record")

        if num % 10000 == 0:
            sc.sqlite_write(record_tmp_dict, db_file,
                            "tax_record", column_name)
            record_tmp_dict = []

        round_time = time.time()
        if round_time - start_time > 10:
            log_print("\t\t\t%d/%d" % (num, len(tax_record_dict)))
            start_time = round_time

    if len(record_tmp_dict) > 0:
        sc.sqlite_write(record_tmp_dict, db_file, "tax_record", column_name)
        record_tmp_dict = []
        log_print("\t\t\t%d/%d" % (num, len(tax_record_dict)))

    conn = sqlite3.connect(db_file)
    conn.execute("CREATE UNIQUE INDEX tax_id_index on tax_record (tax_id)")
    conn.close()

    log_print("\t\tEnd: convert NCBI taxonomy database to sqlite3 file")


class Taxon_db(Taxon):
    def lower_than(self, rank):
        temp_list = tuple(
            [j[1] for j in self.get_lineage if j[1] != 'no rank' and j[1] != 'clade'])

        if len(temp_list) == 0:  # Other sequence
            return False

        max_index = max(Taxon.rank_list.index(i) for i in temp_list)

        if max_index >= Taxon.rank_list.index(rank):
            return True
        else:
            return False

    def is_a(self, taxon_id):
        if taxon_id in [i[0] for i in self.get_lineage]:
            return True
        else:
            return False


def read_tax_record_dict_db(db_file, tax_id_list=[]):
    column_name = ["tax_id", "sci_name", "parent_tax_id",
                   "rank", "merged_new_id", "lineage"]

    record_tuple_list = sc.sqlite_select_by_a_key(
        db_file, "tax_record", "tax_id", tuple(tax_id_list))

    record_dict = {}
    for record_tuple in record_tuple_list:
        record = Taxon_db()
        record.tax_id = record_tuple[0]
        if not record_tuple[1] == "":
            record.sci_name = record_tuple[1]
        if not record_tuple[2] == "":
            record.parent_tax_id = record_tuple[2]
        if not record_tuple[3] == "":
            record.rank = record_tuple[3]
        if not record_tuple[4] == "":
            record.tax_id = record_tuple[4]
            record.older = True

        record.get_lineage = [tuple(i.split(":"))
                              for i in record_tuple[5].split(";")]

        lineage_list = record.get_lineage
        # taxon.lineage = lineage_list
        for i in lineage_list:
            tax_id_tmp, rank_tmp = i
            if not (rank_tmp == 'no rank' or rank_tmp == 'clade'):
                setattr(record, rank_tmp, tax_id_tmp)
        record_dict[record_tuple[0]] = record

    return record_dict


def read_tax_name_record_dict_db(db_file, tax_name_list):
    column_name = ["tax_id", "sci_name", "parent_tax_id",
                   "rank", "merged_new_id", "lineage"]

    record_tuple_list = sc.sqlite_select_by_a_key(
        db_file, "tax_record", "sci_name", tuple(tax_name_list))

    record_dict = {}
    for record_tuple in record_tuple_list:
        record = Taxon_db()
        record.tax_id = record_tuple[0]
        if not record_tuple[1] == "":
            record.sci_name = record_tuple[1]
        if not record_tuple[2] == "":
            record.parent_tax_id = record_tuple[2]
        if not record_tuple[3] == "":
            record.rank = record_tuple[3]
        if not record_tuple[4] == "":
            record.tax_id = record_tuple[4]
            record.older = True

        record.get_lineage = [tuple(i.split(":"))
                              for i in record_tuple[5].split(";")]

        lineage_list = record.get_lineage
        # taxon.lineage = lineage_list
        for i in lineage_list:
            tax_id_tmp, rank_tmp = i
            if not (rank_tmp == 'no rank' or rank_tmp == 'clade'):
                setattr(record, rank_tmp, tax_id_tmp)
        record_dict[record_tuple[1]] = record

    return record_dict


def tax_id_list(db_file):
    conn = sqlite3.connect(db_file)
    record_tuple = [i[0] for i in conn.execute(
        "select tax_id from tax_record").fetchall()]
    conn.close()
    return record_tuple


def get_common_tree(taxon_id_list, taxon_dict):
    MRCA = get_MRCA_taxon_id(taxon_id_list, taxon_dict)
    clade_MRCA = Clade(branch_length=None, name=MRCA,
                       clades=None, confidence=None, color=None, width=None)
    clade_dict = {
        MRCA: clade_MRCA
    }

    for taxon_id in taxon_id_list:
        try:
            lineage = [i[0]
                       for i in taxon_dict[taxon_id].get_lineage(taxon_dict)]
        except:
            lineage = [i[0] for i in taxon_dict[taxon_id].get_lineage]

        for taxon_id_tmp in lineage:
            taxon_id_tmp_index = lineage.index(taxon_id_tmp)
            # old than MRCA
            if taxon_id_tmp_index < lineage.index(MRCA):
                continue
            # leaf taxon
            if taxon_id_tmp_index + 1 >= len(lineage):
                continue
            # good now add son to dict
            my_clade = clade_dict[taxon_id_tmp]
            son_taxon_id = lineage[taxon_id_tmp_index + 1]
            if my_clade.clades is None:
                my_clade.clades = []
            already_have_son = [i.name for i in my_clade.clades]
            if not son_taxon_id in already_have_son:
                son_clade = Clade(name=son_taxon_id)
                my_clade.clades.append(son_clade)
                clade_dict[son_taxon_id] = son_clade

    tree = Tree.from_clade(clade_MRCA)

    return tree


def blast_taxon_assign(taxon_score_list, common_tree, silence=True):
    """
    Give me blast score results of a seq, I will tell you the taxon of this sequence
    :param taxon_blast_score_dict: [("3702",100.00)]
    :param taxon_dict: build_taxon_database(taxon_dir)
    :return:
    """
    if not silence:
        print("# begin analysis:")

    # get the highest score for each taxon
    taxon_hash = {}
    for taxon_id, score in taxon_score_list:
        if not taxon_id in taxon_hash or taxon_hash[taxon_id] <= score:
            taxon_hash[taxon_id] = score

    if not silence:
        print("## get %d taxon\n" % len(taxon_hash))

    # build common_tree
    if not silence:
        print("# build common_tree:")

    taxon_id_list = list(taxon_hash.keys())
    # common_tree = get_common_tree(taxon_id_list, taxon_dict)
    common_tree = remove_pass_node(common_tree)
    common_tree = add_clade_name(common_tree)

    MRCA = common_tree.root.name
    if not silence:
        print("## get common_tree, MRCA: %s\n" % taxon_dict[MRCA].sci_name)

    leaf = common_tree.get_terminals()

    tree_dict = lookup_by_names(common_tree)

    # based on rank and fisher exact test
    if not silence:
        print("# based on rank and fisher exact test:")

    taxon_score_rank = sorted(
        taxon_hash, key=lambda x: taxon_hash[x], reverse=True)
    taxon_score_rank = [i for i in taxon_score_rank if i in tree_dict]

    fisher_p_dict = {}

    for clade in common_tree.find_clades(order='preorder'):
        all_sub_clade_id = [i.name for i in get_offspring(clade) + [clade]]
        all_sub_clade_have_hit = list(
            set(all_sub_clade_id) & set(taxon_id_list))

        top_hit_num = 0
        for i in all_sub_clade_have_hit:
            if taxon_score_rank.index(i) + 1 <= len(all_sub_clade_have_hit):
                top_hit_num += 1

        a = top_hit_num
        b = len(all_sub_clade_have_hit) - a
        c = b
        d = len(taxon_score_rank) - b

        oddsratio, pvalue = stats.fisher_exact([[a, b], [c, d]])
        clade.confidence = pvalue
        # print(pvalue)

        fisher_p_dict[clade.name] = pvalue

    fisher_qvalue_dict = get_qvalue(fisher_p_dict)

    good_clade_name = [i for i in sorted(fisher_qvalue_dict, key=lambda x: fisher_qvalue_dict[x]) if
                       fisher_qvalue_dict[i] <= 0.05]

    if not silence:
        print("# There are %d taxon have q_value <= 0.05" %
              len(good_clade_name))

    # based on score value to say how
    # compared between brother score
    if not silence:
        permutation_p_value = {}
        for clade_name in good_clade_name:
            clade_tmp = tree_dict[clade_name]
            parent_tmp = get_parent(clade_tmp, common_tree)

            if len(parent_tmp) != 0:
                clade_leaf = clade_tmp.get_terminals()
                brother_leaf = [
                    i for i in parent_tmp.get_terminals() if i not in clade_leaf]

                clade_score = [taxon_hash[i.name]
                               for i in clade_leaf if i.name in taxon_hash]
                brother_score = [taxon_hash[i.name]
                                 for i in brother_leaf if i.name in taxon_hash]

                p_value = permutation_test(clade_score, brother_score,
                                           method='approximate',
                                           func=lambda x, y: np.mean(
                                               x) - np.mean(y),
                                           seed=0)

                permutation_p_value[clade_name] = p_value

            else:
                permutation_p_value[clade_name] = 0

        print("Taxon_SciName\tTaxon_id\tFisher\tFDR\tPermutation")
        for i in good_clade_name:
            print("%s\t%s\t%.5e\t%.5e\t%.5f" % (
                taxon_dict[i].sci_name, i, fisher_p_dict[i], fisher_qvalue_dict[i], permutation_p_value[i]))
        # print(taxon_dict[i].sci_name, fisher_p_dict[i], fisher_qvalue_dict[i], permutation_p_value[i])

    # get full_supported_list
    if not silence:
        print("\n# based on node to find fully supported lineage:\n")

    full_supported_list = []
    for clade_name in good_clade_name:
        lineage_list = [i.name for i in get_ancestors(
            clade_name, common_tree)] + [clade_name]
        if set(lineage_list) & set(good_clade_name) == set(lineage_list):
            full_supported_list.append(clade_name)

    # full_supported_list = good_clade_name

    # get best lineage
    good_clade_lineage_list = []
    for clade_name in full_supported_list:
        lineage_list = [i.name for i in get_ancestors(
            clade_name, common_tree)] + [clade_name]
        good_clade_lineage_list.append(lineage_list)

    # if have two good lineage, use vote way
    merge_set_list = merge_subset(good_clade_lineage_list)

    vote_dict = {tuple(i): 0 for i in good_clade_lineage_list if set(
        i) in merge_set_list}

    for i in good_clade_lineage_list:
        for j in vote_dict:
            if set(i) & set(j) == set(i):
                vote_dict[j] += 1

    if not silence:
        num = 0
        for i in sorted(vote_dict, key=lambda x: vote_dict[x], reverse=True):
            print("#( %d ):" % num)
            lineage_txt = printer_list(
                [taxon_dict[j].sci_name for j in i], head="\t", sep=";")
            print(lineage_txt)
            print("Vote num: %d\n" % (vote_dict[i]))
            num = num + 1

    good_lineage_list = list(vote_dict.keys())

    # use score compare
    # find conflict point
    # get full_supported_list
    if not silence:
        print("\n# get final results:")

    while len(good_lineage_list) > 1:
        for comp_pair in combinations(good_lineage_list, 2):
            if not silence:
                print("\tcompare with %s vs %s:" %
                      (comp_pair[0][-1], comp_pair[1][-1]))

            A_clade = tree_dict[comp_pair[0][-1]]
            B_clade = tree_dict[comp_pair[1][-1]]
            mrca_clade = get_MRCA(A_clade, B_clade, common_tree)
            A_conflict_clade = [i for i in get_sons(
                mrca_clade) if i.name in comp_pair[0]][0]
            B_conflict_clade = [i for i in get_sons(
                mrca_clade) if i.name in comp_pair[1]][0]

            A_conflict_score = [taxon_hash[i.name] for i in A_conflict_clade.get_terminals() if
                                i.name in taxon_hash]
            B_conflict_score = [taxon_hash[i.name] for i in B_conflict_clade.get_terminals() if
                                i.name in taxon_hash]

            p_value = permutation_test(A_conflict_score, B_conflict_score,
                                       method='approximate',
                                       func=lambda x, y: np.mean(
                                           x) - np.mean(y),
                                       seed=0)
            if not silence:
                print("\tp_value: %f" % p_value)

            # A > B
            if p_value <= 0.05:
                good_lineage_list.remove(comp_pair[1])
                if not silence:
                    print("\tremove %s" % comp_pair[1][-1])
            # A < B
            elif p_value >= 0.95:
                good_lineage_list.remove(comp_pair[0])
                if not silence:
                    print("\tremove %s" % comp_pair[0][-1])
            else:
                good_lineage_list.remove(comp_pair[0])
                good_lineage_list.remove(comp_pair[1])

                mrca_lineage = tuple(
                    [i.name for i in get_ancestors(mrca_clade.name, common_tree)] + [mrca_clade.name])
                good_lineage_list.append(mrca_lineage)
                if not silence:
                    print("\tremove %s and %s, change to %s\n" %
                          (comp_pair[0][-1], comp_pair[1][-1], mrca_clade.name))

            merge_set_list = merge_subset(good_lineage_list)

            good_lineage_list = [
                tuple(i) for i in good_clade_lineage_list if set(i) in merge_set_list]

            break

    if not silence:
        lineage_txt = printer_list([taxon_dict[j].sci_name for j in good_lineage_list[0]],
                                   head="Results:\t", sep="; ")

        print("\n" + lineage_txt + "\n")

        rename_dict = {}
        for i in tree_dict:
            sci_name = taxon_dict[i].sci_name
            if tree_dict[i].is_terminal() and i in taxon_hash:
                sci_name = sci_name + ": %.1f" % taxon_hash[i]

            rename_dict[i] = sci_name

        draw_ascii(common_tree, column_width=160,
                   clade_name=True, rename_dict=rename_dict)

    if good_lineage_list == []:
        recommand_taxon = MRCA
        recommand_taxon_fisher = 1.0
    else:
        recommand_taxon = good_lineage_list[0][-1]
        recommand_taxon_fisher = fisher_qvalue_dict[good_lineage_list[0][-1]]

    return MRCA, recommand_taxon, recommand_taxon_fisher


# use 1kp

def load_one_kp_tree(one_kp_tree_file, acc_to_taxon_map):
    acc_map_dict = tsv_file_dict_parse(acc_to_taxon_map, fieldnames=[
                                       'acc', 'tax_id', 'lineage'], key_col='acc')

    one_kp_tree = Phylo.read(one_kp_tree_file, 'newick')
    one_kp_tree = add_clade_name(one_kp_tree)
    one_kp_node_dict = lookup_by_names(one_kp_tree)

    outgroup = ['DZPJ', 'RAWF']
    out_clade = get_MRCA(
        one_kp_node_dict[outgroup[0]], one_kp_node_dict[outgroup[1]], one_kp_tree)

    one_kp_rooted_tree, one_kp_rooted_node_dict = reroot_by_outgroup_clade(
        one_kp_tree, one_kp_node_dict, out_clade.name, False)

    return one_kp_rooted_tree, one_kp_rooted_node_dict, acc_map_dict


def extract_common_tree(one_kp_tree, keep_leave_list):

    node_name_list = [i.name for i in one_kp_tree.get_terminals()]
    valid_keep_leave_list = list(set(keep_leave_list) & set(node_name_list))
    removed_node_list = list(set(node_name_list) - set(valid_keep_leave_list))

    removed_tree = remove_given_node_from_tree(one_kp_tree, removed_node_list)

    for c in removed_tree.find_clades():
        if c.branch_length:
            c.branch_length = None

    return removed_tree


def get_best_1kp_represent(input_taxon_id_list, acc_map_dict, taxon_db_file):

    acc_taxon_list = list(set([acc_map_dict[i]['tax_id']
                               for i in acc_map_dict]))
    taxon_dict = read_tax_record_dict_db(
        taxon_db_file, tax_id_list=input_taxon_id_list + acc_taxon_list)

    rep_dict = {}
    for i in input_taxon_id_list:

        if i in set(acc_taxon_list):
            rep_dict[i] = i
        else:
            it = taxon_dict[i]
            it_lineage = set([j[0] for j in it.get_lineage])

            ca_dict = {}
            for a in acc_taxon_list:
                at = taxon_dict[a]
                at_lineage = set([j[0] for j in at.get_lineage])
                ca_dict[a] = list(it_lineage & at_lineage)

            best_rep_ca_num = len(
                ca_dict[sorted(acc_taxon_list, key=lambda x:len(ca_dict[x]), reverse=True)[0]])
            best_rep = sorted([j for j in acc_taxon_list if len(
                ca_dict[j]) == best_rep_ca_num])[0]
            rep_dict[i] = best_rep

    for i in rep_dict:
        rep_dict[i] = sorted(
            [j for j in acc_map_dict if acc_map_dict[j]['tax_id'] == rep_dict[i]])[0]

    return rep_dict


def get_common_tree_by_1kp(input_taxon_id_list, one_kp_tree_file, acc_to_taxon_map, taxon_db_file):

    one_kp_rooted_tree, one_kp_rooted_node_dict, acc_map_dict = load_one_kp_tree(
        one_kp_tree_file, acc_to_taxon_map)
    rep_dict = get_best_1kp_represent(
        input_taxon_id_list, acc_map_dict, taxon_db_file)

    removed_tree = extract_common_tree(
        one_kp_rooted_tree, set([rep_dict[i] for i in rep_dict]))
    removed_tree = add_clade_name(removed_tree)
    removed_tree_dict = lookup_by_names(removed_tree)

    okp2input_dict = {}
    for i in rep_dict:
        okp2input_dict.setdefault(rep_dict[i], []).append(i)

    for okp in okp2input_dict:
        input_it_list = okp2input_dict[okp]
        if len(input_it_list) > 1:
            clade_list = [Clade(name=i, clades=[]) for i in input_it_list]
            removed_tree_dict[okp].clades = clade_list
        else:
            removed_tree_dict[okp].name = input_it_list[0]

    return removed_tree
