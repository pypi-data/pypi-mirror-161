import networkx as nx
from itertools import combinations
from toolbiox.lib.common.util import dict_key_value_transpose


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


def find_longest_path(G, nodeA, nodeB):
    """
    heaviest_path = max((path for path in nx.all_simple_paths(G, nodeA, nodeB)),
                        key=lambda path: get_weight(path))

    """

    """
    DG = nx.DiGraph()
    DG.add_edge('S', 'a', weight=-1)
    DG.add_edge('a', 'b', weight=-1)
    DG.add_edge('a', 'c', weight=-2)
    DG.add_edge('b', 'd', weight=-1)
    DG.add_edge('b', 'e', weight=-2)
    DG.add_edge('c', 'e', weight=-3)
    DG.add_edge('c', 'f', weight=-2)
    DG.add_edge('d', 'T', weight=-1)
    DG.add_edge('e', 'T', weight=-1)
    DG.add_edge('f', 'T', weight=-1)
    
    p2 = nx.johnson(G, weight='weight')
    print('johnson: {0}'.format(p2['S']['T']))
    """

    pass
