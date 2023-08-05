import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def plot_graph(G, pos, figsize=(20, 20), save_file=None, node_color_dict=None, node_size_dict=None, node_label_list=None):
    fig, ax = plt.subplots(figsize=figsize)

    if node_color_dict:
        node_color = [node_color_dict[node_id] for node_id in pos]
    else:
        node_color = '#1f78b4'

    if node_size_dict:
        node_size = [node_size_dict[node_id] for node_id in pos]
    else:
        node_size = 600

    nx.draw_networkx_nodes(G, pos, edgecolors='k', linewidths=1,
                           node_size=node_size, node_color=node_color)

    if node_label_list:
        labels_dict = dict((n, n)
                           for n in G.nodes() if n in set(node_label_list))
        nx.draw_networkx_labels(
            G, pos, labels=labels_dict, font_size=10, font_weight='bold', font_color='k')
    else:
        nx.draw_networkx_labels(G, pos, font_size=10,
                                font_weight='bold', font_color='k')
    nx.draw_networkx_edges(G, pos, edge_color="#8D8D8D", width=0.5)

    # nx.draw_networkx(G, ax=ax)
    print(len(G.nodes), len(G.edges))

    plt.show()

    if save_file:
        fig.savefig(save_file, format='pdf', facecolor='none',
                    edgecolor='none', bbox_inches='tight')


def remove_overmuch_degree(G, max_degree):
    all_overmuch_edge_list = []
    for node in G.nodes:
        nb_list = list(G.neighbors(node))
        sorted_nb_list = sorted(nb_list, key=lambda x: G.get_edge_data(x, node)[
                                'weight'], reverse=True)
        if len(sorted_nb_list) > max_degree:
            overmuch_edge_list = [tuple(sorted([node, nb]))
                                  for nb in sorted_nb_list[max_degree:]]
            all_overmuch_edge_list.extend(overmuch_edge_list)

    G.remove_edges_from(all_overmuch_edge_list)

    return G


def remove_low_weight_edges(G, min_weight):
    low_weight_edge_list = [e for e in G.edges if G.get_edge_data(e[0], e[1])[
        'weight'] < min_weight]
    G.remove_edges_from(low_weight_edge_list)

    return G


def remove_low_degree_node(G, min_degree):

    low_degree_nodes = []
    for node in G.nodes:
        if G.degree(node) <= min_degree:
            low_degree_nodes.append(node)

    G.remove_nodes_from(low_degree_nodes)

    return G


def get_subGraph(G):
    sub_Gs = [G.subgraph(c) for c in nx.connected_components(G)]
    return sub_Gs


def get_plot_pos(G):
    pos = nx.drawing.spring_layout(G)
    return pos


if __name__ == '__main__':

    G = nx.Graph()
    G.add_nodes_from(node_list)
    G.add_weighted_edges_from(edge_list)

