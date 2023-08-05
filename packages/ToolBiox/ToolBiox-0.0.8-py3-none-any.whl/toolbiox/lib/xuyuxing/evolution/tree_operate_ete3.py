
###

import ete3



def subtree(tree_file, leaf1, leaf2, root_leaf):
    t = ete3.Tree(tree_file)
    if not root_leaf is None:
        t.set_outgroup(root_leaf)
    node = t.get_common_ancestor(leaf1, leaf2)
    return node


def phyloxml_read_ete(phyloxml_file):
    project = ete3.Phyloxml()
    project.build_from_file(phyloxml_file)
    tree = project.get_phylogeny()[0]
    return tree


def phyloxml_write_ete(tree, phyloxml_file):
    project = ete3.Phyloxml()
    project.add_phylogeny(tree)
    with open(phyloxml_file,'w') as f:
        project.export(f)
    return phyloxml_file

#####




#
# """
# Jupyter
# t.render("%%inline")
# """
#
# from pyvirtualdisplay import Display
# from ete3 import Tree
# display = Display(visible=False, size=(1024, 768), color_depth=24)
# display.start()
#
# t = Tree("/lustre/home/xuyuxing/Work/Cau_HGT/tmp/phyout/phyout.phb")
#
# t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);', format=1)
#
#
# len(t)
#
# print(t.get_ascii(show_internal=True))
#
# #include root
# for i in t.traverse("postorder"):
#     print(i.name)
#
# #no root
# for i in t.iter_descendants("postorder"):
#     print(i.name)
#
# # Browse the tree from a specific leaf to the root
# node = t.search_nodes(name="H")[0]
# while node:
#    print(node)
#    node = node.up
#
# abs()
#
# t.set_outgroup(t&"H")
#
# display.stop()