import re
import csv
import gzip
import sqlite3
import pandas as pd
from collections import OrderedDict

from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.util import printer_list

csv.field_size_limit(100000000)


def tsv_file_parse(file_name, key_col=0, fields="all", seq="\t", prefix="ID_", ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like "1,2,3" or "3,4,1"
    :param seq:         separator for tsv-like file
    :return: a dict with given key and value, value is a list for column chosen.
    """
    dict_output = OrderedDict()
    num = 0

    with open(file_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=seq, quotechar='"')
        for info in spamreader:
            if len(info) == 0 or re.match(ignore_prefix, info[0]):
                continue
            if fields == "all":
                record = info
            else:
                field_list = fields.split(",")
                record = []
                for field in field_list:
                    record.append(info[int(field) - 1])

            record = tuple(record)

            if key_col == 0:
                dict_output[prefix + str(num)] = record
            else:
                dict_output[info[key_col - 1]] = record
            num = num + 1

    return dict_output


def tsv_file_parse_big(file_name, key_col=None, fields="all", seq="\t", prefix="ID_", gzip_flag=False,
                       fieldnames=None, ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like list("A","B","C")
    :param seq:         separator for tsv-like file
    :param prefix:      When key_col is None, we will get key as prefix write
    :param gzip_flag:   If this is a .gz file
    :param fieldnames:  if tsv file don't have title line, you should give it by list
    :return: a dict with given key and value, value is a list for column chosen.
    """
    # dict_output = OrderedDict()
    num = 0

    if gzip_flag is True:
        csvfile = gzip.open(file_name, 'rt')
    else:
        csvfile = open(file_name, 'r', newline='')

    spamreader = csv.DictReader(csvfile, delimiter=seq, quotechar='"', fieldnames=fieldnames)
    for info in spamreader:
        if len(info) == 0 or re.match(ignore_prefix, info[fieldnames[0]]):
            continue
        if fields == "all":
            record = info
        else:
            field_list = fields
            record = {}
            for i in field_list:
                record[i] = info[i]

        if key_col is None:
            ID_tmp = prefix + str(num)
        else:
            ID_tmp = info[key_col]
        num = num + 1

        # dict_output[ID_tmp] = OrderedDict.fromkeys(record)
        output_dir = OrderedDict.fromkeys(record)
        for keys in record:
            values = record[keys]
            output_dir[keys] = values
            # dict_output[ID_tmp][keys] = values

        yield output_dir

    csvfile.close()

    # return dict_output


def tsv_file_to_sqlite3(tsv_file_name, sqlite3_file_name, table_name, key_col=None, seq="\t", gzip_flag=False,
                        fieldnames=None, ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.

    :param tsv_file_name:       tsv_file_name
    :param sqlite3_file_name:   sqlite3_file_name
    :param key_col:             which column should be key for output dict
    :param fields:              which column should be value for output dict, field can be "all" or given
                                    column like list("A","B","C")
    :param seq:                 separator for tsv-like file
    :param prefix:              When key_col is None, we will get key as prefix write
    :param gzip_flag:           if this is a .gz file
    :param fieldnames:          if tsv file don't have title line, you should give it by list

    :return: a dict with given key and value, value is a list for column chosen.
    """
    import time
    from toolbiox.lib.xuyuxing.base.common_command import log_print
    import toolbiox.lib.common.sqlite_command as sc

    start_time = time.time()
    sc.init_sql_db(sqlite3_file_name, table_name, fieldnames)

    num = 0

    if gzip_flag is True:
        csvfile = gzip.open(tsv_file_name, 'rt')
    else:
        csvfile = open(tsv_file_name, 'r', newline='')

    record_tmp_dict = []
    spamreader = csv.DictReader(csvfile, delimiter=seq, quotechar='"', fieldnames=fieldnames)
    for info in spamreader:
        if len(info) == 0 or re.match(ignore_prefix, info[fieldnames[0]]):
            continue
        num = num + 1

        record_tmp = []
        for i in fieldnames:
            record_tmp.append(info[i])
        record_tmp_dict.append(record_tmp)

        if num % 1000000 == 0:
            sc.sqlite_write(record_tmp_dict, sqlite3_file_name, table_name, fieldnames)
            record_tmp_dict = []

        round_time = time.time()
        if round_time - start_time > 10:
            log_print("%d finished" % (num))
            start_time = round_time

    if len(record_tmp_dict) > 0:
        sc.sqlite_write(record_tmp_dict, sqlite3_file_name, table_name, fieldnames)
        log_print("%d finished" % (num))

    csvfile.close()

    if not key_col is None:
        conn = sqlite3.connect(sqlite3_file_name)
        conn.execute("CREATE UNIQUE INDEX key_index on %s (\"%s\")" % (table_name, key_col))
        conn.close()


def dict_to_tsv_file(two_level_dict, file_name, column_name_list='all', seq="\t", gzip_flag=False):
    """
    This func can save a dict to tsv-like file.
    """
    if gzip_flag is True:
        csvfile = gzip.open(file_name, 'wt', newline='')
    else:
        csvfile = open(file_name, 'w', newline='')

    if column_name_list == "all":
        first_record = list(two_level_dict.keys())[0]
        column_name_list = list(two_level_dict[first_record].keys())
    else:
        column_name_list = column_name_list

    writer = csv.DictWriter(csvfile, fieldnames=column_name_list, delimiter=seq)
    writer.writeheader()
    for i in two_level_dict:
        writer.writerow(two_level_dict[i])

    csvfile.close()

    # with open(file_name, 'w', newline='') as csvfile:
    #    writer = csv.DictWriter(csvfile, fieldnames=column_name_list, delimiter=seq)
    #    writer.writeheader()
    #    for i in two_level_dict:
    #        writer.writerow(two_level_dict[i])


# def dict_to_tsv_file(ordered_dict, output_file_name, fields="all", seq="\t", gzip_flag=False):
#     if gzip_flag is True:
#         outfile = gzip.open(output_file_name, 'wt')
#     else:
#         outfile = open(output_file_name, 'w', newline='')
#
#     if fields == "all":
#         first_record = list(ordered_dict.keys())[0]
#         field_list = list(ordered_dict[first_record].keys())
#     else:
#         field_list = fields
#
#     outfile.write(printer_list(field_list, seq)+"\n")
#
#     for i in ordered_dict:
#         output_list = []
#         for j in field_list:
#             output_list.append(ordered_dict[i][j])
#         outfile.write(printer_list(output_list,seq)+"\n")
#
#     outfile.close()

def title_tsv_to_dict(dict_from_tsv_file_parse):
    """
    This function used for some table file with title line, you should first load file by
        function "tsv_file_parse" by key_col = 0, so title line will be dict[0]. "title_tsv_to_dict"
        will delete dict['ID_0'] and change raw dict to a two-level dict with first level key is num from
        1 to end and second level key is column name given by title line.
    :param dict_from_tsv_file_parse: dict from function "tsv_file_parse"
    :return dict_output:
    :return column_name:
    """

    column_name = dict_from_tsv_file_parse['ID_0']
    dict_output = {}
    for i in dict_from_tsv_file_parse:
        if i == "ID_0":
            continue
        dict_output[i] = {}

        for j in range(1, len(column_name)):
            dict_output[i][column_name[j]] = dict_from_tsv_file_parse[i][j]

    return dict_output, column_name


def PAF_parse(file_name):
    fieldname = ["q_name", "q_len", "q_start", "q_end", "strand", "s_name", "s_len", "s_start", "s_end", "match",
                 "aln_len", "quality"]
    record_dict = tsv_file_dict_parse(file_name, fieldnames=fieldname)
    output_dict = {}
    for i in record_dict:
        if record_dict[i]["q_name"] not in output_dict: output_dict[record_dict[i]["q_name"]] = []
        output_dict[record_dict[i]["q_name"]].append(record_dict[i])
    return output_dict


