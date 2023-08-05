import configparser
import logging
import math
import re
import time
from collections import OrderedDict
import json
import os
import pickle

from toolbiox.lib.common.os import *
from toolbiox.lib.common.util import *
from toolbiox.lib.xuyuxing.math.base import base_translate
from operator import attrgetter


def log_print(print_string):
    time_tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print("%s\t\t\t%s" % (time_tmp, print_string))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def num_to_chr(num, digit):
    """
    when digit is 5:
    let 0 -> AAAAA
        1 -> AAAAB
    """

    base_list = base_translate(num, 26)

    output_list = []
    for i in [0]*(digit-len(base_list)) + base_list:
        output_list.append(chr(65+i))

    return ''.join(output_list)


def get_od(ordereddict_input, index_input):
    key_list = list(ordereddict_input.keys())
    index_output = key_list[index_input]
    return ordereddict_input[index_output]


# dict common tools
def dict2class(dict_input, class_target, attribute_list, key2attr=None):
    """
    This func can trans a dict with many object which attr recorded as a list in dict value
    to a dict with many object which recorded as a given class
    :param dict_input:      As dict output from tsv_file_parse, which key is a object id and value
                            is a list that many attr are recorded with a order but no name of
                            attribute.
    :param class_target:    which class you want
    :param attribute_list:  a list including name of attributes, order is same as dict_input
                            value and length of attribute_list should short or same as value
                            of dict_input.
    :param key2attr:        if key should record as an attr in class, give me the name.
    :return:    a dict with many object which recorded as a given class.
    """
    dict_output = {}

    for i in dict_input:
        key = i
        value_list = dict_input[i]
        dict_output[i] = class_target()

        if key2attr is not None:
            setattr(dict_output[i], key2attr, key)

        for rank in range(0, len(attribute_list)):
            if rank > len(value_list) - 1:
                break
            setattr(dict_output[i], attribute_list[rank], value_list[rank])

    return dict_output


def dict_slice(target_dict, slice_used, sort_flag=False, sort_key_function=None, reverse=False):
    """
    get something in dict as slice for a list, better for a OrderedDict
    :param target_dict: a dict, if it's a OrderedDict will be better
    :param slice_used: a object from slice function output. See https://docs.python.org/3/library/functions.html#slice
    :param sort_flag: do you want to sort keys in a dict
    :param sort_key_function: key args from sorted function
    :param reverse: if reverse
    :return:
    """

    if sort_flag:
        target_dict_sorted_keys = list(
            sorted(target_dict, key=sort_key_function, reverse=reverse))
    else:
        target_dict_sorted_keys = list(target_dict.keys())

    output_dir = OrderedDict()
    for i in target_dict_sorted_keys[slice_used]:
        output_dir[i] = target_dict[i]

    return output_dir


def merge_dict(dict_list, extend_value=True):
    """
    merge some dict into one dict

    extend_value:
    if same key find in diff dict, extend value as list, if extend_value is True, all value will be list

    else, old value will be delete

    a = {1:1,2:2,3:3}
    b = {1:2,4:4,5:5}

    merge_dict([a,b])
    Out[11]: OrderedDict([(1, [1, 2]), (2, [2]), (3, [3]), (4, [4]), (5, [5])])

    merge_dict([a,b], False)
    Out[12]: OrderedDict([(1, 2), (2, 2), (3, 3), (4, 4), (5, 5)])

    """

    output_dict = OrderedDict()

    for dict_tmp in dict_list:
        for i in dict_tmp:
            if extend_value:
                if not i in output_dict:
                    output_dict[i] = []

                if isinstance(dict_tmp[i], list):
                    output_dict[i].extend(dict_tmp[i])
                else:
                    output_dict[i].append(dict_tmp[i])
            else:
                output_dict[i] = dict_tmp[i]

    return output_dict


def hash_map(dict_list):
    dict_hash = {}
    for i in dict_list:
        for j in dict_list[i]:
            if j not in dict_hash:
                dict_hash[j] = []
            dict_hash[j].append(i)
    return dict_hash


def dict_key_value_interchange(dict_input):
    """interchange key and value, value should in list and uniq"""

    dict_output = {}
    for i in dict_input:
        for j in dict_input[i]:
            dict_output[j] = i

    return dict_output


"""
Abbreviation for the month
"""
month_abbr = ["Jan", "Feb", "Mar", "Apr", "May",
              "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def flag_maker(bit_list):
    """
    input a bit list, like: [1,2,3,4,5] or [1,3,5], return a int as flag
    input int will be 1-base
    """
    flag = 0
    for i in bit_list:
        flag = flag + 2 ** (i - 1)
    return flag


def flag_parse(n):
    '''''convert denary integer n to binary string bStr, https://en.wikipedia.org/wiki/SAM_(file_format)#Bitwise_Flags'''
    bStr = ''
    if n < 0:
        raise ValueError("must be a positive integer")
    if n == 0:
        return []
    num = 0
    output = []
    while n > 0:
        num = num + 1
        if n % 2 == 1:
            output.append(num)
        n = n >> 1
    return output


def flag_filter(given_flag, need_flag, exclude_flag):
    """
    give a bitwise flags, and a flags which must have and a flag which should exclude
    :param given_flag: a int for bitwise flag
    :param need_flag: a int for need, nothing use 0
    :param exclude_flag: a int for exclude, nothing use 0
    :return: True or False
    """

    given_flag_list = set(flag_parse(given_flag))
    need_flag_list = set(flag_parse(need_flag))
    exclude_flag_list = set(flag_parse(exclude_flag))

    return (given_flag_list & need_flag_list == need_flag_list) and (given_flag_list & exclude_flag_list == set())


def millify(n):
    """
    let size in byte is easy for human, 1000 base
    :param n: 100000
    :return:  100 KB
    """
    millnames = ['', ' K', ' M', ' G', ' P']

    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.2f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


# used to save pickle

# copy from flye
class Job(object):
    """
    Describes an abstract list of jobs with persistent
    status that can be resumed
    """
    run_params = {"stage_name": ""}

    def __init__(self):
        self.name = None
        self.args = None
        self.work_dir = None
        self.out_files = {}
        self.log_file = None

    def run(self):
        self.log_file.info(">>>STAGE: %s", self.name)

    def save(self, save_file):
        Job.run_params["stage_name"] = self.name

        with open(save_file, "w") as f:
            json.dump(Job.run_params, f)

    def load(self, save_file):
        with open(save_file, "r") as f:
            data = json.load(f)

            Job.run_params = data

    def completed(self, save_file):
        with open(save_file, "r") as f:
            dummy_data = json.load(f)

            for file_path in self.out_files.values():
                if not os.path.exists(file_path):
                    return False

            return True


if __name__ == '__main__':
    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='TaxonTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for ID2Lineage
    parser_a = subparsers.add_parser('ID2Lineage',
                                     help='get taxonomy lineage by taxon ID', description='')
    parser_a.add_argument(
        "-o", "--output_dir", help="Output file name (default as $STDOUT)", default=None, type=str)
    parser_a.add_argument(
        "-c", "--contig_file", help="Output file name (default as $STDOUT)", default=None, type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # --------------------------------------------
    # command detail

    if args_dict["subcommand_name"] == "ID2Lineage":
        args = configure_parser(args,
                                "/lustre/home/xuyuxing/Database/Balanophora/Comp_genome/dongming/orthofinder_191218/output/config", args.contig_file, parameter_type_dict=None, parameter_parser_block=None)

        attrs = vars(args)

        for item in attrs.items():
            print("%s: %s" % item)
