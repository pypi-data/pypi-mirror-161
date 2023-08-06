import configparser
import logging
import time
import os
import pickle
from operator import attrgetter

__author__ = 'Yuxing Xu'


def printer_list(list_input, sep="\t", head="", wrap_num=None):
    """
    make a list to a string with a given sep chara and head
    :param list_input: list you give me
    :param sep: Split character like "," or "\t"
    :param head: head for the output string
    :return: string
    """
    printer = head
    num = 0

    for i in list_input:
        printer = printer + str(i) + sep
        num = num + 1
        if wrap_num:
            if num % wrap_num == 0:
                printer = printer + "\n"

    printer = printer.rstrip(sep)
    return printer


def mulit_sort(xs, specs):
    """
    class Student:
        def __init__(self, name, grade, age):
            self.name = name
            self.grade = grade
            self.age = age
        def __repr__(self):
            return repr((self.name, self.grade, self.age))

    student_objects = [
        Student('john', 'A', 15),
        Student('jane', 'B', 12),
        Student('dave', 'B', 10),
    ]

    multisort(list(student_objects), (('grade', True), ('age', False)))
    """
    for key, reverse in reversed(specs):
        xs.sort(key=attrgetter(key), reverse=reverse)
    return xs


def logging_init(program_name, log_file=None):
    # create logger with 'program_name'
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not log_file is None:
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger


def type_check(p_name, p_value, parameter_type_dict):
    if parameter_type_dict is None or p_name not in parameter_type_dict:
        return p_name, p_value
    else:
        if parameter_type_dict[p_name] == 'str':
            return p_name, str(p_value)
        elif parameter_type_dict[p_name] == 'int':
            return p_name, int(p_value)
        elif parameter_type_dict[p_name] == 'float':
            return p_name, float(p_value)
        elif parameter_type_dict[p_name] == 'bool':
            return p_name, bool(p_value)
        else:
            raise ValueError('Unknown type %s' % parameter_type_dict[p_name])


def configure_parser(arg_obj, defaults_config_file=None, config_file=None, parameter_type_dict=None,
                     parameter_parser_block=None):
    """
    config_file should be ini file

    [Simple Values]
    key=value
    spaces in keys=allowed
    spaces in values=allowed as well
    spaces around the delimiter = obviously
    you can also use : to delimit keys from values

    [All Values Are Strings]
    values like this: 1000000
    or this: 3.14159265359
    are they treated as numbers? : no
    integers, floats and booleans are held as: strings
    can use the API to get converted values directly: true

    [Multiline Values]
    chorus: I'm a lumberjack, and I'm okay
        I sleep all night and I work all day

    [No Values]
    key_without_value
    empty string value here =

    [You can use comments]
    # like this
    ; or this

    # By default only in an empty line.
    # Inline comments can be harmful because they prevent users
    # from using the delimiting characters as parts of values.
    # That being said, this can be customized.

        [Sections Can Be Indented]
            can_values_be_as_well = True
            does_that_mean_anything_special = False
            purpose = formatting for readability
            multiline_values = are
                handled just fine as
                long as they are indented
                deeper than the first line
                of a value
            # Did I mention we can indent comments, too?

        :param arg_obj:

    args

    :param parameter_type_dict:

    parameter_type_dict = {"reference_genome": "str",
                       "work_dir": "str",
                       "db_file_fnf": "str",
                       "speci_tree_file": "str",
                       "taxonomy_dir": "str",
                       "target_speci": "str",
                       "prominence": "int",
                       "gap_limit": "int",
                       "min_ranges": "int",
                       "query_step": "int",
                       "query_length": "int",
                       "subseq_kmer_frequencies_thre": "int",
                       "threshold_node_level": "str",
                       "permutation_round": "int",
                       "seed": "int",
                       "p_value_thre": "float",
                       "evalue": "float",
                       "num_threads": "int"
                       }

    :param parameter_parser_block:

    """

    output_cfg_dict = {}

    # read defaults config
    if defaults_config_file is not None:
        def_cfg = configparser.ConfigParser()
        def_cfg.read(defaults_config_file)

        for cfg_block in def_cfg.sections():
            for key in def_cfg[cfg_block]:
                value = def_cfg[cfg_block][key]
                p_name, p_value = type_check(key, value, parameter_type_dict)
                output_cfg_dict[p_name] = p_value

    # read given config
    if config_file is not None:
        cfg = configparser.ConfigParser()
        cfg.read(config_file)

        for cfg_block in cfg.sections():
            for key in cfg[cfg_block]:
                if (parameter_parser_block is not None) and (cfg_block not in parameter_parser_block):
                    continue
                value = cfg[cfg_block][key]
                p_name, p_value = type_check(key, value, parameter_type_dict)
                # if p_name not in output_cfg_dict:
                #     raise ValueError("unknown parameter %s" % p_name)
                # else:
                #     output_cfg_dict[p_name] = p_value
                output_cfg_dict[p_name] = p_value

    # read command arg
    for p_name in output_cfg_dict:
        if hasattr(arg_obj, p_name) and (getattr(arg_obj, p_name) is not None):
            output_cfg_dict[p_name] = getattr(arg_obj, p_name)

    # output to args
    for p_name in output_cfg_dict:
        setattr(arg_obj, p_name, output_cfg_dict[p_name])

    return arg_obj


def pickle_dump(save_object, output_pickle_file):
    try:
        OUT = open(output_pickle_file, 'wb')
        pickle.dump(save_object, OUT)
        OUT.close()
        return output_pickle_file
    except:
        raise ValueError("Failed to write %s" % output_pickle_file)


def pickle_load(input_pickle_file):
    try:
        TEMP = open(input_pickle_file, 'rb')
        output_object = pickle.load(TEMP)
        TEMP.close()
        return output_object
    except:
        raise ValueError("Failed to open %s" % input_pickle_file)


def pickle_step(function, input_args_list, output_pickle_file):
    """
    Sometimes the result of a function may have already been run and saved, so I can try to read the result and run the function again if it doesn't work
    """

    if os.path.exists(output_pickle_file):
        try:
            TEMP = open(output_pickle_file, 'rb')
            output_object = pickle.load(TEMP)
            TEMP.close()
            return output_object
        except:
            pass
    output_object = function(*input_args_list)
    OUT = open(output_pickle_file, 'wb')
    pickle.dump(output_object, OUT)
    OUT.close()

    return output_object


def time_now():
    time_tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return time_tmp


def dict_key_value_transpose(dict_list):
    dict_hash = {}
    for i in dict_list:
        for j in dict_list[i]:
            if j not in dict_hash:
                dict_hash[j] = []
            dict_hash[j].append(i)
    return dict_hash
