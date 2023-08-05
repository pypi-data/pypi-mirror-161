from Bio import Phylo
from toolbiox.lib.common.evolution.tree_operate import add_clade_name

tree_file = "/Users/yuxingxu/Job/Work/HGT/treeplot/tree.phb"
tree = Phylo.read(tree_file, 'newick')
tree = add_clade_name(tree)

tree_dir = {}
for clade in tree.find_clades():
    tree_dir[clade.name] = clade

clade_N6 = tree_dir['N6']
clade_N7 = tree_dir['N7']

from Bio.Phylo.BaseTree import Tree, Clade


class CladePlot(object):

    def __init__(self, Clade, **kwargs):
        self.clade = Clade
        self.input_setting = kwargs

        # change attr in clade
        for k, v in self.input_setting:
            if k == 'color':
                self.clade = v

def is_offspring_of(A, B):
    """
    A is offspring of B
    A can not be son of B
    """
    return B in A.get_ancestors()








def tree_plot


class abc(object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def print_abc(self):
        print(self.a, self.b, self.c)


class abc_with_d(abc):
    def __init__(self, abc, d):
        self = abc
        self.d = d

    def print_abcd(self):
        print(self.a, self.b, self.c, self.d)


def add_d(abc, d):


ABC = abc(1, 2, 3)
ABCD = abc_with_d(ABC, 4)
