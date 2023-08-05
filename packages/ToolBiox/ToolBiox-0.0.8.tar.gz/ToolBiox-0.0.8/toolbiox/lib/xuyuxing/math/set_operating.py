import numpy as np
from interlap import InterLap
from collections import OrderedDict
import networkx as nx
from itertools import combinations

from toolbiox.lib.common.math.interval import *
from toolbiox.lib.common.math.set import *


def interval_length_sum(interval_list, int_flag=True):
    """get length sum of a list of interval"""
    length = 0

    for i in interval_list:
        if int_flag:
            length += (abs(i[1] - i[0]) + 1)
        else:
            length += abs(i[1] - i[0])

    return length


def merge_all_dimension(input_matrix):
    record_num, dimension, range_num = input_matrix.shape

    if not range_num == 2:
        raise ValueError("interval range should have 2 number")

    output_array = []
    for i in range(dimension):
        output_array.append(
            (input_matrix[:, i, :].min(), input_matrix[:, i, :].max()))

    output_array = np.array(output_array)

    return output_array


def common_intervals(input_matrix, int_flag):
    def one_step(input_matrix, int_flag):
        record_num, dimension, range_num = input_matrix.shape

        if not range_num == 2:
            raise ValueError("interval range should have 2 number")

        find_inter = 0
        for i in range(record_num):
            for j in range(record_num):
                if i == j:
                    continue
                I_array = input_matrix[i]
                J_array = input_matrix[j]
                inter_flag = 1
                for k in range(dimension):
                    flag, deta = section(I_array[k], J_array[k], int_flag)
                    if not flag:
                        inter_flag = 0
                if inter_flag == 1:
                    new_array = merge_all_dimension(
                        np.array([I_array, J_array]))
                    if not new_array.shape == (dimension, range_num):
                        raise ValueError("merged array shape error, maybe bug")
                    new_array = np.array([new_array])
                    find_inter = 1
                    break
            if find_inter == 1:
                break

        if find_inter == 1:
            new_matrix = np.delete(input_matrix, (i, j), 0)
            new_matrix = np.concatenate((new_matrix, new_array), axis=0)
            return find_inter, new_matrix
        else:
            return find_inter, input_matrix

    matrix = input_matrix
    find_inter = 1
    while (find_inter):
        find_inter, matrix = one_step(matrix, int_flag)

    return matrix


def uniqify(seq, idfun=None):
    """
    a function that will delete redundancy elements
    note: slow than list(set(*))
    :param seq:
    :param idfun:
    :return:
    """
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def overlap_with_interlap_set(target_intervals, interlap_set, int_flag=False):
    """
    target_intervals = (50,100)
    interlap_set = InterLap([(1,70),(90,120)])

    overlap is (50,70) and (90,100), when int_flag is True
    no_overlap is (71, 89) = 19

    no_overlap ratio = 19/51 = 0.37
    """

    no_overlap = interval_minus_set(
        target_intervals, list(interlap_set.find(target_intervals)))
    overlap = interval_minus_set(target_intervals, no_overlap)
    overlap_length = sum_interval_length(overlap, close_range=int_flag)

    if int_flag:
        overlap_ratio = overlap_length / \
            (max(target_intervals) - min(target_intervals) + 1)
    else:
        overlap_ratio = overlap_length / \
            (max(target_intervals) - min(target_intervals))

    return overlap_ratio, overlap_length, overlap


def site_cluster(site_list, max_gap):
    """
    a function that will find site cluster which def by max_gap on one dimensional space
    :param site_list: if on interval_mode, input should be a list of tuples
                      e.g. intervals = [(1,5),(33,35),(40,33),(10,15),(13,18),(28,23),(70,80),(22,25),(38,50),(40,60)]
                      else:
                      input should be a list of int
                      e.g. list = [1,23,4,32,34]
    :return: merged list
    """

    sorted_list = sorted(list(set(site_list)))
    cluster_list = []
    temp_cluster = []
    for temp in sorted_list:
        if not temp_cluster:
            temp_cluster.append(temp)
        else:
            lower = temp_cluster[-1]
            if temp - lower <= max_gap:
                temp_cluster.append(temp)
            else:
                cluster_list.append(tuple(temp_cluster))
                temp_cluster = []
                temp_cluster.append(temp)
    cluster_list.append(tuple(temp_cluster))
    return cluster_list


def jaccord_index(set1, set2):
    set1 = set(set1)
    set2 = set(set2)

    return (len(set1 & set2) / len(set1 | set2))


def merge_order_list(one_list, two_list):
    """merge two number list"""

    for item in two_list:
        # 先区分元素是否比列表的最大元素还要大。
        if item < one_list[-1]:
            for i in range(len(one_list)):
                # 先比较，再插入
                if item <= one_list[i]:
                    one_list.insert(i, item)
                    break
        else:
            one_list.append(item)
    return one_list


def similarity_mcl_based_cluster():
    """
    similarity cluster, just good for clean gap like 0.2 to 0.8
    """

    pass
