from toolbiox.lib.common.evolution.tree_operate import get_sons
from Bio import Phylo
from toolbiox.config import badirate_path
from toolbiox.lib.common.os import mkdir, rmdir, cmd_run, multiprocess_running
from toolbiox.lib.common.util import logging_init
import copy
import os
import re
from io import StringIO
import math


def F_index(gene_family_size_tuple):
    S = len(gene_family_size_tuple)
    a = (S * S - 2 * S) / 2
    N = sum(gene_family_size_tuple)

    F = [(math.log2(a*c/N + 0.5) + 1) / (math.log2(a + 0.5) + 1)
         for c in gene_family_size_tuple]

    return F


def run_badirate_one(ctl_file, badirate_path):
    cmd_run("perl %s %s" % (badirate_path, ctl_file), silence=True)


def run_badirate(ctl_list, output_list, badirate_path, just_load=False):
    if just_load:
        output_file_dict = {}

        for output_file in output_list:
            output_file_dict[output_file] = 0
            if os.path.exists(output_file):
                output_file_dict[output_file] = os.path.getsize(output_file)
    else:
        # list_run=[ctl_file1,ctl_file2,..]
        for file_tmp in output_list:
            if os.path.exists(file_tmp):
                os.remove(file_tmp)

        for ctl_file in ctl_list:
            run_badirate_one(ctl_file, badirate_path)

        output_file_dict = {}

        for output_file in output_list:
            output_file_dict[output_file] = 0
            if os.path.exists(output_file):
                output_file_dict[output_file] = os.path.getsize(output_file)

    return output_file_dict


def get_K(bmodel_string):
    return 2*(len(re.findall(r'_', bmodel_string))+1)


def two_better_than_one_significance(k1, Likelihood1, k2, Likelihood2):
    AIC1 = 2*float(k1)-2*float(Likelihood1)
    AIC2 = 2*float(k2)-2*float(Likelihood2)

    if max([AIC1, AIC2])-min([AIC1, AIC2]) > 2:
        if AIC1 > AIC2:
            return 1, AIC1, AIC2
        elif AIC1 < AIC2:
            return -1, AIC1, AIC2
    else:
        return 0, AIC1, AIC2


def get_branch_name(badirate_tree, size_file, badirate_path):
    """
    perl ~/Program/badirate/badirate-master/BadiRate.pl -sizefile 1 -print_ids -treefile species_tree.tre > species_tree.badirate.tre
    """

    cmd_string = "perl %s -sizefile %s -print_ids -treefile %s" % (
        badirate_path, size_file, badirate_tree)
    flag, output, error = cmd_run(cmd_string, silence=True)

    labeled_tree_string = output.split('\n')[1]
    labeled_tree = StringIO(labeled_tree_string)

    tree = Phylo.read(labeled_tree, 'newick')

    all_branch = []
    
    for clade in tree.find_clades(order='level'):
        if clade.is_terminal():
            continue
        else:
            for son in get_sons(clade):
                clade_name = clade.confidence
                if son.is_terminal():
                    son_name = son.name.split("_")[-1]
                else:
                    son_name = son.confidence

                all_branch.append("%s->%s" % (clade_name, son_name))

    return all_branch, labeled_tree_string


def make_bmodel_string(all_branch, known="", new_ratio=0, GR=0, FR=0):
    """
    all_branch = ["17->15","15->11","11->9","9->3","3->1","3->2","9->8","8->6","6->4","6->5","8->7","11->10","15->14","14->12","14->13","17->16"]
    """
    all_string = {}

    if GR == 1:
        output = ""
        for i in all_branch:
            output = output+i+":"
        output = output.rstrip(":")
        return output

    if FR == 1:
        output = ""
        for i in all_branch:
            output = output+i+"_"
        output = output.rstrip("_")
        return output

    if known == "":
        head_string = known
        remain_branch = copy.deepcopy(all_branch)
    else:
        if new_ratio == 1:
            head_string = known+"_"
        elif new_ratio == 0:
            head_string = known+":"
        known_branchs = []
        ratios = known.split("_")
        for ratio in ratios:
            branchs = ratio.split(":")
            for branch in branchs:
                known_branchs.append(branch)

        remain_branch = copy.deepcopy(all_branch)
        for branch in known_branchs:
            remain_branch.remove(branch)

    output = {}
    for branch in remain_branch:
        output_string = head_string+branch+"_"
        for branch_other in remain_branch:
            if branch == branch_other:
                continue
            output_string = output_string + branch_other + ":"
        output_string = output_string.rstrip(":")
        output[branch] = output_string
    return head_string, output, new_ratio


def make_control_file(bmodel_string, size_file, treefile, work_dir, num, just_load=False):

    clt_0_file = "%s/%s.0.ctl" % (work_dir, str(num))
    out_0_file = "%s/%s.0.out" % (work_dir, str(num))

    if not just_load:

        with open(clt_0_file, 'w') as f:
            f.write(
                """
root_dist = 1
sizefile = %s
treefile = %s
n_max_int = 10
priorfile = 0
outlier = 0
seed = 587347092
unobs = 1
rmodel = GD
ep = ML
help = 0
out = %s
anc = 1
version = 0
print_ids = 0
bmodel = %s
start_val = 0
family = 0
    """ % (size_file, treefile, out_0_file, bmodel_string))

    clt_1_file = "%s/%s.1.ctl" % (work_dir, str(num))
    out_1_file = "%s/%s.1.out" % (work_dir, str(num))

    if not just_load:

        with open(clt_1_file, 'w') as f:
            f.write(
                """
root_dist = 1
sizefile = %s
treefile = %s
n_max_int = 10
priorfile = 0
outlier = 0
seed = 1
unobs = 1
rmodel = GD
ep = ML
help = 0
out = %s
anc = 1
version = 0
print_ids = 0
bmodel = %s
start_val = 1
family = 0
    """ % (size_file, treefile, out_1_file, bmodel_string))

    return [[clt_0_file, out_0_file], [clt_1_file, out_1_file]]


def get_ancestral_size(file_name):
    F1 = open(file_name)
    # print file_name
    all_text = F1.read()
    info = all_text.split('--------------------\n')

    label_tree_string = info[0].split("\n")[1]

    for i in info[2].split('\n'):
        match = re.match(r'\t\tTotal Ancestral Size\t(\S+)', i)
        if match:
            ancestral_size_string = match.group(1)

    
    ancestral_size_tree = Phylo.read(StringIO(ancestral_size_string), 'newick')

    ancestral_size_tuple = []
    for i in ancestral_size_tree.find_clades(order='preorder'):
        if i.is_terminal():
            node_num = int(i.name.split("_")[-1])
        else:
            node_num = int(i.confidence)
        ancestral_size_tuple.append(node_num)
    ancestral_size_tuple = tuple(ancestral_size_tuple)

    label_tree_tree = Phylo.read(StringIO(label_tree_string), 'newick')

    label_tuple = []
    for i in label_tree_tree.find_clades(order='preorder'):
        if i.is_terminal():
            node_num = str(i.name.split("_")[-1])
        else:
            node_num = str(i.confidence)
        label_tuple.append(node_num)
    label_tuple = tuple(label_tuple)

    ancestral_size_dict = {}

    for i in range(len(label_tuple)):
        ancestral_size_dict[label_tuple[i]] = int(ancestral_size_tuple[i])

    F1.close()

    return ancestral_size_dict



def detect_pure_gain_and_loss(ancestral_size_dict, all_branch):
    gain_list = []
    loss_list = []
    for branch in all_branch:
        node_f, node_t = branch.split('->')
        if ancestral_size_dict[node_f] == 0 and ancestral_size_dict[node_t] > 0:
            gain_list.append(branch)
        elif ancestral_size_dict[node_f] > 0 and ancestral_size_dict[node_t] == 0:
            loss_list.append(branch)

    return gain_list, loss_list


def badirate_output_parse(file_name):
    F1 = open(file_name)
    # print file_name
    all_text = F1.read()
    info = all_text.split('--------------------\n')
    # print info
    while '' in info:
        info.remove('')
    INTERNAL_ID_TREE = info[0]
    INPUT = info[1]
    OUTPUT = info[2]
    info_output = OUTPUT.split('\n')
    for i in info_output:
        match = re.match(r'\t\t#Likelihood: (\S+)', i)
        if match:
            Likelihood = match.group(1)
    # print Likelihood
    info_output = OUTPUT.split('##')
    flag = 0
    mini_dict = {}
    for i in info_output:
        match = re.match(r'Minimum number of gains and losses per branch', i)
        if match:
            min_num = i.split('\n')
            for line in min_num:
                match2 = re.match(r'\t\t(\d+\->\d+)\t(\d+)\t(\d+)', line)
                if match2:
                    mini_dict[match2.group(1)] = [int(
                        match2.group(2)), int(match2.group(3))]

    F1.close()

    return INPUT, mini_dict, float(Likelihood)


def get_best_start_value(input_list):
    [like1, like2] = input_list
    if like1 == '-inf':
        like1 = -99999999999999999999
    else:
        like1 = float(like1)

    if like2 == '-inf':
        like2 = -99999999999999999999
    else:
        like2 = float(like2)

    temp_list = [like1, like2]
    best = max(temp_list)
    if best == -99999999999999999999:
        return "-inf"
    else:
        return temp_list.index(best)


def main_pipeline(tag, size_file, species_tree, work_dir, badirate_path, label_tree_path=None, keep_tmp_dir=False, just_load=False):
    log_file = work_dir + "/log"

    if just_load:

        all_branch, label_tree = get_branch_name(
            species_tree, size_file, badirate_path)


        FR_string = make_bmodel_string(all_branch, FR=1)
        out_list = make_control_file(
            FR_string, size_file, species_tree, work_dir, "FR", just_load)

        a = [out_list[0][0], out_list[1][0]]
        b = [out_list[0][1], out_list[1][1]]

        output_file_dict = run_badirate(a, b, badirate_path, just_load)

        output_file_list = list(output_file_dict)

        like_FR = [badirate_output_parse(file)[2] for file in output_file_list]

        best_like_FR_index = get_best_start_value(like_FR)

        if best_like_FR_index == "-inf":
            raise
        else:
            best_like_FR = like_FR[best_like_FR_index]

        FR_output_file = output_file_list[best_like_FR_index]

        ancestral_size = get_ancestral_size(FR_output_file)
        pure_gain, pure_loss = detect_pure_gain_and_loss(ancestral_size, all_branch)

        INPUT, mini_dict, Likelihood = badirate_output_parse(FR_output_file)
        back_branch = []
        test_branch = []
        for i in mini_dict:
            gains, losses = mini_dict[i]
            if gains == losses and gains == 0:
                back_branch.append(i)
            else:
                test_branch.append(i)

        # not branch changed
        if len(back_branch) == len(all_branch):
            # return [tag, [], [], Likelihood]
            print([tag, [], [], Likelihood])
            raise

        like_FR = sorted(like_FR, reverse=True)

        eFR_model_string = ""
        for i in back_branch:
            eFR_model_string = eFR_model_string+i+":"
        eFR_model_string = eFR_model_string.rstrip(":")
        back_branch_string = eFR_model_string
        eFR_model_string = eFR_model_string+"_"

        for i in all_branch:
            if i in back_branch:
                continue
            eFR_model_string = eFR_model_string+i+"_"
        eFR_model_string = eFR_model_string.rstrip("_")

        out_list = make_control_file(
            eFR_model_string, size_file, species_tree, work_dir, "eFR", just_load)

        a = [out_list[0][0], out_list[1][0]]
        b = [out_list[0][1], out_list[1][1]]

        output_file_dict = run_badirate(a, b, badirate_path, just_load)

        output_file_list = list(output_file_dict)

        like_eFR = [badirate_output_parse(file)[2] for file in output_file_list]

        best_like_eFR_index = get_best_start_value(like_eFR)
        if best_like_eFR_index == "-inf":
            raise
        else:
            best_like_eFR = like_eFR[best_like_eFR_index]

        eFR_output_file = output_file_list[get_best_start_value(like_eFR)]

        INPUT, mini_dict, Likelihood = badirate_output_parse(eFR_output_file)

        output_dict = {}
        output_dict["family_id"] = tag
        output_dict["FR"] = FR_output_file
        output_dict["eFR"] = {}
        output_dict["tsv_file"] = size_file
        output_dict["eFR"]['Likelihood'] = Likelihood
        output_dict["eFR"]['K'] = get_K(eFR_model_string)
        output_dict["eFR"]['output_file'] = eFR_output_file

        # begin test

        good_branch = []
        for branch_now in test_branch:

            num = re.sub("->", '_', branch_now)
            output_dict[num] = {}
            output_dict[num]['branch'] = branch_now
            test_branch_string = back_branch_string+":"+branch_now+"_"
            for j in test_branch:
                if not j == branch_now:
                    test_branch_string = test_branch_string+j+"_"
            test_branch_string = test_branch_string.rstrip("_")

            out_list = make_control_file(
                test_branch_string, size_file, species_tree, work_dir, num, just_load)

            a = [out_list[0][0], out_list[1][0]]
            b = [out_list[0][1], out_list[1][1]]

            output_file_dict = run_badirate(a, b, badirate_path, just_load)

            like_now = [(badirate_output_parse(file[1])[2], file)
                        for file in out_list]
            like_now = sorted(like_now, reverse=True)
            best_eFR = like_now[0]

            if best_eFR[0] == '-inf':
                output_dict[num]['out_file'] = best_eFR[1][1]
                output_dict[num]['Likelihood'] = '-99999999999999999999'
                output_dict[num]['bmodel_string'] = test_branch_string
                output_dict[num]['K'] = get_K(test_branch_string)
            else:
                output_dict[num]['out_file'] = best_eFR[1][1]
                output_dict[num]['Likelihood'] = best_eFR[0]
                output_dict[num]['bmodel_string'] = test_branch_string
                output_dict[num]['K'] = get_K(test_branch_string)

            flag, AIC1, AIC2 = two_better_than_one_significance(
                output_dict[num]['K'], output_dict[num]['Likelihood'], output_dict["eFR"]['K'], output_dict["eFR"]['Likelihood'])

            if flag == 1:
                output_dict[num]['significative'] = 1
                good_branch.append(branch_now)
            else:
                output_dict[num]['significative'] = 0

    else:

        mkdir(work_dir, False)

        logger = logging_init("badirate_exp_con", log_file)
        logger.info("Build work dir")

        all_branch, label_tree = get_branch_name(
            species_tree, size_file, badirate_path)

        if not label_tree_path is None:
            with open(label_tree_path, 'w') as f:
                f.write(label_tree)

        # cal free branch model
        logger.info("cal free branch model")

        FR_string = make_bmodel_string(all_branch, FR=1)
        out_list = make_control_file(
            FR_string, size_file, species_tree, work_dir, "FR")

        a = [out_list[0][0], out_list[1][0]]
        b = [out_list[0][1], out_list[1][1]]

        output_file_dict = run_badirate(a, b, badirate_path)
        logger.info("cal free branch model, done!")

        output_file_list = list(output_file_dict)

        like_FR = [badirate_output_parse(file)[2] for file in output_file_list]

        best_like_FR_index = get_best_start_value(like_FR)

        if best_like_FR_index == "-inf":
            logger.info("%s can't get information from free model, failed!" % tag)
            # return None
            raise
        else:
            best_like_FR = like_FR[best_like_FR_index]

        FR_output_file = output_file_list[best_like_FR_index]

        ancestral_size = get_ancestral_size(FR_output_file)
        pure_gain, pure_loss = detect_pure_gain_and_loss(ancestral_size, all_branch)

        INPUT, mini_dict, Likelihood = badirate_output_parse(FR_output_file)
        back_branch = []
        test_branch = []
        for i in mini_dict:
            gains, losses = mini_dict[i]
            if gains == losses and gains == 0:
                back_branch.append(i)
            else:
                test_branch.append(i)

        logger.info("free branch model get likelihood: %.5f, and %d branch have change" % (
            Likelihood, len(all_branch) - len(back_branch)))
        # not branch changed
        if len(back_branch) == len(all_branch):
            logger.info("No exp & con")
            # return [tag, [], [], Likelihood]
            print([tag, [], [], Likelihood])
            raise

        like_FR = sorted(like_FR, reverse=True)

        logger.info("cal Null hypothesis branch model")

        eFR_model_string = ""
        for i in back_branch:
            eFR_model_string = eFR_model_string+i+":"
        eFR_model_string = eFR_model_string.rstrip(":")
        back_branch_string = eFR_model_string
        eFR_model_string = eFR_model_string+"_"

        for i in all_branch:
            if i in back_branch:
                continue
            eFR_model_string = eFR_model_string+i+"_"
        eFR_model_string = eFR_model_string.rstrip("_")

        logger.info("get eFR model string: %s" % eFR_model_string)
        out_list = make_control_file(
            eFR_model_string, size_file, species_tree, work_dir, "eFR")

        a = [out_list[0][0], out_list[1][0]]
        b = [out_list[0][1], out_list[1][1]]

        output_file_dict = run_badirate(a, b, badirate_path)
        logger.info("cal Null hypothesis branch model, done!")

        output_file_list = list(output_file_dict)

        like_eFR = [badirate_output_parse(file)[2] for file in output_file_list]

        best_like_eFR_index = get_best_start_value(like_eFR)
        if best_like_eFR_index == "-inf":
            logger.info(
                "%s can't get information from null hypothesis free model, failed!" % tag)
            # return None
            raise
        else:
            best_like_eFR = like_eFR[best_like_eFR_index]

        eFR_output_file = output_file_list[get_best_start_value(like_eFR)]

        INPUT, mini_dict, Likelihood = badirate_output_parse(eFR_output_file)

        output_dict = {}
        output_dict["family_id"] = tag
        output_dict["FR"] = FR_output_file
        output_dict["eFR"] = {}
        output_dict["tsv_file"] = size_file
        output_dict["eFR"]['Likelihood'] = Likelihood
        output_dict["eFR"]['K'] = get_K(eFR_model_string)
        output_dict["eFR"]['output_file'] = eFR_output_file

        logger.info("null hypothesis branch model get likelihood: %.5f, K is %d" % (
            Likelihood, output_dict["eFR"]['K']))

        # begin test

        good_branch = []
        for branch_now in test_branch:

            logger.info("test %s %s now:" % (branch_now, mini_dict[branch_now]))

            logger.info("cal test branch model")
            num = re.sub("->", '_', branch_now)
            output_dict[num] = {}
            output_dict[num]['branch'] = branch_now
            test_branch_string = back_branch_string+":"+branch_now+"_"
            for j in test_branch:
                if not j == branch_now:
                    test_branch_string = test_branch_string+j+"_"
            test_branch_string = test_branch_string.rstrip("_")

            logger.info("get test branch model string: %s" % test_branch_string)

            out_list = make_control_file(
                test_branch_string, size_file, species_tree, work_dir, num)

            a = [out_list[0][0], out_list[1][0]]
            b = [out_list[0][1], out_list[1][1]]

            output_file_dict = run_badirate(a, b, badirate_path)
            logger.info("cal test branch model, done!")

            like_now = [(badirate_output_parse(file[1])[2], file)
                        for file in out_list]
            like_now = sorted(like_now, reverse=True)
            best_eFR = like_now[0]

            if best_eFR[0] == '-inf':
                output_dict[num]['out_file'] = best_eFR[1][1]
                output_dict[num]['Likelihood'] = '-99999999999999999999'
                output_dict[num]['bmodel_string'] = test_branch_string
                output_dict[num]['K'] = get_K(test_branch_string)
            else:
                output_dict[num]['out_file'] = best_eFR[1][1]
                output_dict[num]['Likelihood'] = best_eFR[0]
                output_dict[num]['bmodel_string'] = test_branch_string
                output_dict[num]['K'] = get_K(test_branch_string)

            logger.info("comp %s (%.5f, %d) and eFR (%.5f, %d)" % (
                branch_now, output_dict[num]['Likelihood'], output_dict[num]['K'], output_dict["eFR"]['Likelihood'], output_dict["eFR"]['K']))

            flag, AIC1, AIC2 = two_better_than_one_significance(
                output_dict[num]['K'], output_dict[num]['Likelihood'], output_dict["eFR"]['K'], output_dict["eFR"]['Likelihood'])

            logger.info("AIC: %.5f vs %.5f flag: %d" % (AIC1, AIC2, flag))

            if flag == 1:
                output_dict[num]['significative'] = 1
                good_branch.append(branch_now)
            else:
                output_dict[num]['significative'] = 0

    up_down = {}
    up_down['up'] = []
    up_down['down'] = []
    for i in good_branch:
        if mini_dict[i][0] > 0:
            up_down['up'].append(i)
        elif mini_dict[i][1] > 0:
            up_down['down'].append(i)

    up_down['up'] = list(set(up_down['up'] + pure_gain))
    up_down['down'] = list(set(up_down['down'] + pure_loss))

    up_down['up'] = list(set(up_down['up']) - set(pure_gain))
    up_down['down'] = list(set(up_down['down']) - set(pure_loss))

    printer = ""
    for i in up_down['up']:
        printer = printer+i+","
    printer = printer.rstrip(",")
    printer = printer+"\t"
    for i in up_down['down']:
        printer = printer+i+","
    printer = printer.rstrip(",")
    printer = printer + "\t" + str(output_dict["eFR"]['Likelihood'])
    printer = tag + "\t" + printer

    print("Tag\tGain\tLoss\tExpansion\tContraction\tLikelihood")
    print(tag, pure_gain, pure_loss, up_down['up'], up_down['down'],
        output_dict["eFR"]['Likelihood'])

    if keep_tmp_dir:
        print("temp_dir is : %s" % work_dir)
    else:
        rmdir(work_dir)

    return tag, pure_gain, pure_loss, up_down['up'], up_down['down'], output_dict["eFR"]['Likelihood'], label_tree


def EasyBadiRate_main():
    pass


if __name__ == "__main__":

    species_tree = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/hcluster/test/tre2'
    label_tree_path = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/hcluster/test/label.tre'
    size_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/hcluster/test/tsv'
    work_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/gene_family/hcluster/test/out'
    log_file = work_dir + "/log"
    tag = "gene1"

    output = main_pipeline(tag, size_file, species_tree,
                           work_dir, badirate_path, label_tree_path, True)

    if output:
        tag, up_list, down_list, ll, label_tree = output


    tag="C1194"
    size_file="/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/GeneFamilyStat/C1194/size_file"
    species_tree="/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/species_time.tre"
    work_dir="/lustre/home/xuyuxing/Work/Orobanchaceae/publish/3.gene_family/2.expansion_contract/GeneFamilyStat/C1194/run"
    badirate_path="/lustre/home/xuyuxing/Program/badirate/badirate-master/BadiRate.pl"
    label_tree_path=None
    keep_tmp_dir=True
    just_load=True

    output = main_pipeline(tag, size_file, species_tree, work_dir, badirate_path, label_tree_path, keep_tmp_dir, just_load)