from toolbiox.config import esearch_path, efetch_path
from toolbiox.lib.common.os import cmd_run
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from collections import Counter
import re


def search_sra_data(query_string, output_runinfo_csv):
    """
    query_string = 'Dendrobium'
    output_runinfo_csv = '/lustre/home/xuyuxing/Database/Gel/other/Dca/sra_data/runinfo.csv'
    """

    cmd_string = "%s -db sra -query \"%s\" | %s -format runinfo > %s" % (
        esearch_path, query_string, efetch_path, output_runinfo_csv)
    # print(cmd_string)
    cmd_run(cmd_string)

    return output_runinfo_csv


def runinfo_csv_parser(runinfo_csv_file):
    """
    runinfo_csv_file = '/lustre/home/xuyuxing/Database/Gel/other/Dca/sra_data/runinfo.csv'
    """
    info_dict = tsv_file_dict_parse(runinfo_csv_file, seq=',')

    sra_dict = {}
    for i in info_dict:
        if not info_dict[i]['Run'] == 'Run':
            sra_dict[info_dict[i]['Run']] = info_dict[i]

    return sra_dict


def get_rna_seq_from_sra(keys_word, tmp_runinfo_file):
    """
    keys_word = 'Dendrobium'
    tmp_runinfo_file = '/lustre/home/xuyuxing/Database/Gel/other/Dca/sra_data/runinfo.csv'
    """

    search_sra_data(keys_word, tmp_runinfo_file)
    sra_dict = runinfo_csv_parser(tmp_runinfo_file)

    good_rna_seq_id = []
    for sra_id in sra_dict:
        if not sra_dict[sra_id]['LibraryStrategy'] == 'RNA-Seq':
            continue
        if not sra_dict[sra_id]['LibrarySource'] == 'TRANSCRIPTOMIC':
            continue
        if int(sra_dict[sra_id]['avgLength']) < 50 and int(sra_dict[sra_id]['avgLength']) > 1000:
            continue
        good_rna_seq_id.append(sra_id)

    print("%d in %d is good sra rna_seq" % (len(good_rna_seq_id), len(sra_dict)))

    good_rna_seq = {i: sra_dict[i] for i in good_rna_seq_id}

    return good_rna_seq
