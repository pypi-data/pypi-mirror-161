import networkx as nx
from itertools import combinations
from toolbiox.lib.common.util import dict_key_value_transpose

__author__ = 'Yuxing Xu'

def merge_same_element_set_with_group_id(input_dict):
    """
    merge sets which have at least one same element
    :param input_dict:
            input_dict = {
                "a" : [1,2,3,4,5],
                "b" : [10,2,30,40,50],
                "c" : [100,200,300,40,500],
                "d" : [900,1000]
                }
    :return: output_list = [(a,b),(c)]
    """

    def one_step(input_dict):
        input_hash = dict_key_value_transpose(input_dict)
        change_flag = 0
        for element in input_hash:
            if len(input_hash[element]) > 1:
                all_group_not_deleted_flag = 1
                for group in input_hash[element]:
                    if group not in input_dict:
                        all_group_not_deleted_flag = 0
                        break

                if all_group_not_deleted_flag:

                    change_flag = 1

                    temp_group_id = []
                    for i in input_hash[element]:
                        if isinstance(i, tuple):
                            for j in i:
                                temp_group_id.append(j)
                        else:
                            temp_group_id.append(i)
                    temp_group_id = tuple(set(temp_group_id))

                    temp_group_element = []
                    for group in input_hash[element]:
                        temp_group_element.extend(input_dict[group])
                    temp_group_element = list(set(temp_group_element))

                    for group in input_hash[element]:
                        del input_dict[group]

                    input_dict[temp_group_id] = temp_group_element

                else:
                    continue

        return change_flag, input_dict

    change_flag = 1
    while change_flag:
        change_flag, input_dict = one_step(input_dict)
        print(len(input_dict))

    return input_dict


def merge_same_element_set_with_group_id_by_graphs(input_dict):
    """
    merge sets which have at least one same element
    based on Connected component in graphs
    :param input_dict:
            input_dict = {
                "a" : [1,2,3,4,5],
                "b" : [10,2,30,40,50],
                "c" : [100,200,300,40,500],
                "d" : [900,1000]
                }
    :return: output_list = [(a,b,c),(d)]
    """
    G = nx.Graph()
    G.add_nodes_from(input_dict.keys())
    input_hash = dict_key_value_transpose(input_dict)
    for element in input_hash:
        if len(input_hash[element]) > 1:
            G.add_edges_from(combinations(input_hash[element], 2))

    output_list = []
    for sub_graph in (G.subgraph(c) for c in nx.connected_components(G)):
        output_list.append(tuple(list(sub_graph.nodes)))

    output_dir = {}
    for i in output_list:
        element_list = []
        for j in i:
            element_list.extend(input_dict[j])
        output_dir[i] = list(set(element_list))

    return output_dir


def merge_same_element_set(input_lol):
    """
    merge sets which have at least one same element
    :param input_lol:
            input_lol = [[1,2,3,4,5],[10,2,30,40,50],[100,200,300,40,500],[900,1000]]
    :return: output_list = [[1,2,3,4,5,10,30,40,50,100,200,300,500],[900,1000]]
    """
    num = 0
    input_dict = {}
    for i in input_lol:
        input_dict[num] = i
        num = num + 1

    # output_dict = merge_same_element_set_with_group_id(input_dict)
    output_dict = merge_same_element_set_with_group_id_by_graphs(input_dict)

    output_list = []
    for i in output_dict:
        output_list.append(output_dict[i])

    return output_list


def merge_subset(set_list):
    """
    remove set which is subset of other set

    :param set_list: [{1,2},{1,2,3},{1,2},{1,2,4},{1,2,3},{1,2},{1,4},{1,2,3},{1,2,3,5}]
    :return: [{1,2,3,5},{1,2,4}]
    """

    set_list = [set(i) for i in set_list]

    want_remove = []
    for i in range(len(set_list)):
        set_i = set_list[i]
        for j in range(i, len(set_list)):
            set_j = set_list[j]
            if i == j:
                continue
            if set_i & set_j == set_i:
                want_remove.append(i)
            elif set_i & set_j == set_j:
                want_remove.append(j)

    want_remove = list(set(want_remove))

    return [set_list[i] for i in range(len(set_list)) if not i in want_remove]


def point_break(all_list, point_list):
    """
    point_list = [260, 264, 267, 281, 282, 289, 272, 290, 291, 292, 293, 294]
    all_list = [260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294]
    """

    output_lol = []
    last_range = []
    for i in all_list:
        if i in point_list:
            if len(last_range) != 0:
                output_lol.append(last_range)
            last_range = []
        else:
            last_range.append(i)
    if len(last_range) != 0:
        output_lol.append(last_range)

    return output_lol    