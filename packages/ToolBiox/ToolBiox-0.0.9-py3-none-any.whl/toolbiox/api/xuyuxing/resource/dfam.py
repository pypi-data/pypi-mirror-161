from Bio.Phylo.BaseTree import Tree, Clade
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import os
import pickle
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.util import logging_init
import time
import sqlite3
import re

try:
    script_dir_path = os.path.split(os.path.realpath(__file__))[0]
    dfam_TE_classes_file = script_dir_path + "/../config_file/TEClasses.txt"
except:
    dfam_TE_classes_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/lib/config_file/TEClasses.txt"


class TE_Class(Clade):
    """
    dfam TE class from https://dfam.org/classification/tree
    """

    def __init__(self,
                 full_name=None,
                 title=None,
                 description=None,
                 hyperlink=None,
                 repeatmasker_equiv=None,
                 repbase_equiv=None,
                 wicker_equiv=None,
                 curcio_derbyshire_equiv=None,
                 piegu_equiv=None,
                 ):

        name = full_name.split(";")[-1]

        super(TE_Class, self).__init__(
            branch_length=None,
            name=name,
            clades=None,
            confidence=None,
            color=None,
            width=None,
        )

        self.info = {
            "full_name": full_name,
            "title": title,
            "description": description,
            "hyperlink": hyperlink,
        }

        self.lineage = tuple(full_name.split(";"))

        self.db_id_map = {
            "repeatmasker": repeatmasker_equiv,
            "repbase": repbase_equiv,
            "wicker": wicker_equiv,
            "curcio_derbyshire": curcio_derbyshire_equiv,
            "piegu": piegu_equiv,
        }

        if len(self.lineage) > 1:
            self.parent = self.lineage[-2]
        else:
            self.parent = None


def build_TE_class_tree(new_dfam_TE_classes_file=None):
    if new_dfam_TE_classes_file:
        file_info_dict = tsv_file_dict_parse(new_dfam_TE_classes_file)
    else:
        file_info_dict = tsv_file_dict_parse(dfam_TE_classes_file)

    clade_dict = {}
    for i in file_info_dict:
        repeatmasker_equiv = (
            file_info_dict[i]['repeatmasker_type'], file_info_dict[i]['repeatmasker_subtype'])

        tc = TE_Class(
            full_name=file_info_dict[i]['full_name'],
            title=file_info_dict[i]['title'],
            description=file_info_dict[i]['description'],
            hyperlink=file_info_dict[i]['hyperlink'],
            repeatmasker_equiv=repeatmasker_equiv,
            repbase_equiv=file_info_dict[i]['repbase_equiv'],
            wicker_equiv=file_info_dict[i]['wicker_equiv'],
            curcio_derbyshire_equiv=file_info_dict[i]['curcio_derbyshire_equiv'],
            piegu_equiv=file_info_dict[i]['piegu_equiv']
        )

        clade_dict[tc.lineage] = tc

    # add clade relationship

    for i in clade_dict:
        tc = clade_dict[i]

        if tc.parent:
            parent_lineage = tc.lineage[:-1]
            p_tc = clade_dict[parent_lineage]
            if p_tc.clades is None:
                p_tc.clades = []
            p_tc.clades.append(tc)

    top_clade = [clade_dict[i]
                 for i in clade_dict if clade_dict[i].parent is None]
    for i in top_clade:
        i.parent = 'root'

    root_clade = Clade(name='root', clades=top_clade)

    te_class_tree = Tree(root_clade, True)

    return te_class_tree


def parse_dfam_hmm_file(dfam_hmm_file):

    f = open(dfam_hmm_file, 'r')

    record_info_dict = {}

    for each_line in f:
        each_line = re.sub(r'\n', '', each_line)

        if re.match(r'^#', each_line):
            continue

        # skip HMM
        match = re.match(r'^ .*', each_line)
        if match:
            continue

        match_list = re.findall(r'^(\S+)\s+(.*)$', each_line)
        if len(match_list) > 0:
            match_list = match_list[0]
            k, v = match_list
            if k not in record_info_dict:
                record_info_dict[k] = []
            record_info_dict[k].append(v)

        if each_line == "//":
            yield record_info_dict
            record_info_dict = {}

    f.close()

    if len(record_info_dict) > 0:
        yield record_info_dict


def load_dfam_info_to_sqlite(dfam_hmm_file, db_name, log_file=None):
    module_log = logging_init("load_dfam_info_to_sqlite", log_file)
    module_log.info(
        'received a call to "lib.resource.dfam.load_dfam_info_to_sqlite"')

    # making a new sql database for store info'
    table_columns_dict = {
        "record": ["acc", "pickle_string"]
    }
    sc.init_sql_db_many_table(db_name, table_columns_dict)
    module_log.info('made a new sql database for store info')

    # loading fasta file and store to sqlite
    module_log.info('loading dfam hmm file and storing in sqlite')
    start_time = time.time()
    num = 0
    record_tmp_list = []
    for record in parse_dfam_hmm_file(dfam_hmm_file):
        accession = record['ACC'][0]
        record_pickle = pickle.dumps(record)
        record_tmp_list.append((accession, record_pickle))

        num = num + 1

        if num % 10000 == 0:
            sc.sqlite_write(record_tmp_list, db_name, "record",
                            table_columns_dict["record"])
            record_tmp_list = []

        round_time = time.time()
        if round_time - start_time > 10:
            module_log.info("\tparsed: %d" % (num))
            start_time = round_time

    if len(record_tmp_list) > 0:
        sc.sqlite_write(record_tmp_list, db_name, "record",
                        table_columns_dict["record"])
        record_tmp_list = []
        module_log.info("\tparsed: %d" % (num))

    module_log.info('loaded dfam file and stored in sqlite ')

    conn = sqlite3.connect(db_name)
    conn.execute("CREATE UNIQUE INDEX access_index on %s (\"%s\")" %
                 ("record", "acc"))
    conn.close()

    del module_log.handlers[:]


def get_dfam_info(dfam_accession_list, db_name):
    db_out_list = sc.sqlite_select(
        db_name, 'record', key_name='acc', value_tuple=tuple(dfam_accession_list))
    output_dict = {}
    for acc, info_pickle in db_out_list:
        info = pickle.loads(info_pickle)
        output_dict[acc] = info
    return output_dict


def get_seq_anntation(dfamtblout, db_name, dfam_TE_classes_file=None, e_value_thr=1e-5, cover=0.6):
    """
    nhmmscan --noali --dfamtblout new_9.dfamtblout --cpu=10 /lustre/home/xuyuxing/Database/Dfam/Dfam.hmm new_9.fa
    """
    hmm_out_dict = {}
    with open(dfamtblout, 'r') as f:
        for each_line in f:
            each_line = re.sub(r'\n', '', each_line)
            if re.match(r'^#', each_line):
                continue

            info = each_line.split()
            target_name, acc, q_name, bits, e_value, bias, hmm_st, hmm_en, strand, ali_st, ali_en, env_st, env_en, modlen = info[
                0:14]
            target_name, acc, q_name, bits, e_value, bias, hmm_st, hmm_en, strand, ali_st, ali_en, env_st, env_en, modlen = target_name, acc, q_name, float(
                bits), float(e_value), float(bias), int(hmm_st), int(hmm_en), strand, int(ali_st), int(ali_en), int(env_st), int(env_en), int(modlen)

            if e_value <= e_value_thr and (abs(env_en - env_st) + 1 / modlen) >= cover:
                if q_name not in hmm_out_dict:
                    hmm_out_dict[q_name] = []
                hmm_out_dict[q_name].append((target_name, acc, q_name, bits, e_value,
                                             bias, hmm_st, hmm_en, strand, ali_st, ali_en, env_st, env_en, modlen))

    dfam_acc_list = []
    for i in hmm_out_dict:
        for j in hmm_out_dict[i]:
            dfam_acc_list.append(j[1])

    dfam_acc_list = list(set(dfam_acc_list))
    dfam_acc_info = get_dfam_info(dfam_acc_list, db_name)

    dfam_lineage_dict = {}
    for i in dfam_acc_info:
        lineage = tuple(dfam_acc_info[i]['CT'][0].split(";"))

        # if 'Retrotransposed_Element' in lineage:
        #     lineage_new = []
        #     for j in lineage:
        #         if j == 'Retrotransposed_Element':
        #             lineage_new.append('Class_I_Retrotransposition')
        #         else:
        #             lineage_new.append(j)
        #     lineage = tuple(lineage_new)

        # if 'DNA_Transposon' in lineage:
        #     lineage_new = []
        #     for j in lineage:
        #         if j == 'DNA_Transposon':
        #             lineage_new.append('Class_II_DNA_Transposition')
        #         else:
        #             lineage_new.append(j)
        #     lineage = tuple(lineage_new)

        dfam_lineage_dict[i] = lineage

    te_tree = build_TE_class_tree()

    te_dict = {}
    for clade in te_tree.find_clades(order='preorder'):
        if hasattr(clade, "lineage"):
            te_dict[clade.lineage] = clade
            # print(clade.lineage)

    for i in dfam_lineage_dict:
        j = dfam_lineage_dict[i]
        if not j in te_dict:
            raise ValueError("unknown dfam linage: %s" % ";".join(j))

    #
    query_lineage_dict = {}
    for q_name in hmm_out_dict:
        if len(hmm_out_dict[q_name]) > 0:
            for i in hmm_out_dict[q_name]:
                dfam_acc = i[1]
                if dfam_acc in dfam_lineage_dict:
                    lineage = dfam_lineage_dict[dfam_acc]
                    if len(lineage) > 0:
                        query_lineage_dict[q_name] = lineage
                        break

    return query_lineage_dict


if __name__ == '__main__':
    dfam_hmm_file = "/lustre/home/xuyuxing/Database/Dfam/Dfam.hmm"
    db_name = "/lustre/home/xuyuxing/Database/Dfam/Dfam.info.db"
    log_file = "/lustre/home/xuyuxing/Database/Dfam/log"

    load_dfam_info_to_sqlite(dfam_hmm_file, db_name, log_file=log_file)
