from toolbiox.lib.common.evolution.tree_operate import Phylo, add_clade_name, is_ancestors_of, lookup_by_names
from toolbiox.lib.common.os import have_file, cmd_run, mkdir
import os
import json
import copy

def easy_ABSREL(rooted_tree, cds_aln_file, output_prefix, tree_format='newick', threads=8):
    output_file = output_prefix + ".ABSREL.json"

    if have_file(output_file):
        print("output file already existed: %" % output_file)
    else:
        # get tree
        tree = Phylo.read(rooted_tree, tree_format)

        for clade in tree.find_clades():
            if clade.confidence:
                clade.confidence = None

        num = 0
        for clade in tree.find_clades():
            if clade.name is None:
                clade.name = "N%d" % num
                num = num + 1

        absrel_input_tree = output_prefix + ".label.tree"

        Phylo.write([tree], absrel_input_tree, 'newick')

        # 
        cmd_string = "hyphy aBSREL CPU=%s --alignment %s --tree %s --output %s" % (threads, cds_aln_file, absrel_input_tree, output_file)
        cmd_run(cmd_string)

    return output_file


rooted_tree = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/selection/tree/fasttree/test/tree.rooted.phb'
cds_aln_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/selection/tree/fasttree/test/cds.fa.aln'
output_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/selection/tree/fasttree/test/tree'
test_node=['N24']
tree_format='newick'
threads = 20

def easy_RELAX(rooted_tree, cds_aln_file, output_dir, test_node=[], tree_format='newick', threads=8):
    mkdir(output_dir, True)

    tree = Phylo.read(rooted_tree, tree_format)
    tree = add_clade_name(tree)

    for clade in tree.find_clades():
        if clade.confidence:
            clade.confidence = None

    num = 0
    for clade in tree.find_clades():
        if clade.name is None:
            clade.name = "N%d" % num
            num = num + 1

    input_tree = output_dir + "/input.tre"
    Phylo.write([tree], input_tree, 'newick')            

    input_aln = output_dir + "/input.cds.aln"
    if not have_file(input_aln):
        if os.path.exists(input_aln):
            os.remove(input_aln)
        os.symlink(os.path.abspath(cds_aln_file), input_aln)

    raw_tree = Phylo.read(input_tree, tree_format)
    tree_dict = lookup_by_names(raw_tree)

    if len(test_node) == 0:
        # need global descriptive
        global_output_file = output_dir + "/global.json"

        if have_file(global_output_file):
            print("output file already existed: %s" % global_output_file)
        else:
            used_tree = copy.deepcopy(raw_tree)

            for i in used_tree.get_terminals():
                i.name = i.name + "{TEST}"
                break

            relax_input_tree = output_dir + "/global.tre"

            Phylo.write([used_tree], relax_input_tree, 'newick')

            cmd_string = "hyphy relax CPU=%d --alignment %s --tree %s --output %s --test TEST" % (threads, cds_aln_file, relax_input_tree, global_output_file)
            cmd_run(cmd_string)

        # k_dict = {}
        # with open(global_output_file, "r") as f:
        #     dummy_data = json.load(f)
        #     for clade_id in dummy_data['branch attributes']['0']:
        #         k_value = dummy_data['branch attributes']['0'][clade_id]['k (general descriptive)']
        #         k_dict[clade_id] = k_value

        # small_k_list = set([i for i in k_dict if k_dict[i] < 1])

        # # get node with all subnode is small k
        # test_cand_list = []
        # for c_id in small_k_list:
        #     c = tree_dict[c_id]
        #     sc_list = set([sc.name for sc in c.find_clades()])
        #     if sc_list & small_k_list == sc_list:
        #         test_cand_list.append(c_id)

        # no_cover_test = []
        # for i in test_cand_list:
        #     no_cover = True
        #     for j in test_cand_list:
        #         if is_ancestors_of(tree_dict[j], tree_dict[i], raw_tree):
        #             no_cover = False
        #     if no_cover:
        #         no_cover_test.append(i)

        # test_node = no_cover_test

    else:

        for node_id in test_node:
            used_tree = copy.deepcopy(raw_tree)
            used_tree_dict = lookup_by_names(used_tree)
            for c in used_tree_dict[node_id].find_clades():
                c.name = c.name + "{TEST}"

            relax_input_tree = output_dir + "/test.%s.tre" % (node_id)
            relax_output_tree = output_dir + "/test.%s.json" % (node_id)

            if not (have_file(relax_input_tree) and have_file(relax_output_tree)):

                Phylo.write([used_tree], relax_input_tree, 'newick')

                cmd_string = "hyphy relax CPU=%d --alignment %s --tree %s --output %s --test TEST --models Minimal" % (threads, cds_aln_file, relax_input_tree, relax_output_tree)
                # print(cmd_string)
                cmd_run(cmd_string)




