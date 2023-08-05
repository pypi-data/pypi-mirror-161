from toolbiox.lib.common.os import mkdir, copy_file, cmd_run, multiprocess_running
import pandas as pd
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from collections import OrderedDict
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init


def OG_tsv_file_parse(file_name):
    file_info = tsv_file_dict_parse(file_name)

    OG_dict = OrderedDict()
    for i in file_info:
        OG_id = file_info[i]['Orthogroup']
        OG_dict[OG_id] = {}
        for j in file_info[i]:
            if j == 'Orthogroup':
                continue
            if file_info[i][j]:
                OG_dict[OG_id][j] = file_info[i][j].split(", ")
            else:
                OG_dict[OG_id][j] = ""

    return OG_dict


def write_OG_tsv_file(OG_dict, output_file, species_list=None):
    if not species_list:
        species_list = list(OG_dict[list(OG_dict.keys())[0]].keys())

    with open(output_file, 'w') as f:
        f.write(printer_list(species_list, head='Orthogroup\t')+"\n")

        for OG_id in OG_dict:
            string_list = []
            for sp_id in species_list:
                string_list.append(printer_list(
                    OG_dict[OG_id][sp_id], sep=', '))
            output_string = printer_list(string_list, head=OG_id+"\t")
            f.write(output_string+"\n")

    return output_file


def read_species_info(species_info_table):
    species_info_df = pd.read_excel(species_info_table)
    species_info_dict = {}
    for index in species_info_df.index:
        sp_id = str(species_info_df.loc[index]['sp_id'])
        species_info_dict[sp_id] = {}
        species_info_dict[sp_id]['pt_file'] = str(
            species_info_df.loc[index]['pt_file'])

        if 'cds_file' in species_info_df.loc[index]:
            species_info_dict[sp_id]['cds_file'] = str(
                species_info_df.loc[index]['cds_file'])

    return species_info_dict


def prepare_OG_work_dir(OG_dict, species_info_dict, top_work_dir):
    mkdir(top_work_dir, True)

    # if have cds
    if 'cds_file' in species_info_dict[list(species_info_dict.keys())[0]]:
        cds_flag = True
    else:
        cds_flag = False

    huge_pt_dict = {}
    if cds_flag:
        huge_cds_dict = {}
    huge_rename_map = {}

    # read fasta

    for i in species_info_dict:
        pt_fa_dict = read_fasta_by_faidx(species_info_dict[i]['pt_file'])
        if cds_flag:
            cds_fa_dict = read_fasta_by_faidx(species_info_dict[i]['cds_file'])

        pt_dict = {}
        if cds_flag:
            cds_dict = {}
        rename_map = {}

        num = 0
        for j in pt_fa_dict:
            pt_dict[num] = pt_fa_dict[j].seq
            if cds_flag:
                cds_dict[num] = cds_fa_dict[j].seq
            rename_map[j] = num
            num += 1

        huge_pt_dict[i] = pt_dict
        if cds_flag:
            huge_cds_dict[i] = cds_dict
        huge_rename_map[i] = rename_map

    # write seq to each OG
    for OG_id in OG_dict:
        OG_work = top_work_dir + "/" + OG_id
        mkdir(OG_work, True)

        # pt_file
        pt_fa = OG_work + "/pt.fa"
        with open(pt_fa, 'w') as f:
            for sp_id in OG_dict[OG_id]:
                for g_id in OG_dict[OG_id][sp_id]:
                    if g_id != '':
                        pt_seq = huge_pt_dict[sp_id][huge_rename_map[sp_id][g_id]]
                        f.write(">%s\n%s\n" % (
                            str(huge_rename_map[sp_id][g_id])+"_"+sp_id, pt_seq))

        # cds_file
        if cds_flag:
            cds_fa = OG_work + "/cds.fa"
            with open(cds_fa, 'w') as f:
                for sp_id in OG_dict[OG_id]:
                    for g_id in OG_dict[OG_id][sp_id]:
                        if g_id != '':
                            cds_seq = huge_cds_dict[sp_id][huge_rename_map[sp_id][g_id]]
                            f.write(">%s\n%s\n" % (
                                str(huge_rename_map[sp_id][g_id])+"_"+sp_id, cds_seq))

        # rename_map
        rename_map = OG_work + "/rename.map"
        with open(rename_map, 'w') as f:
            for sp_id in OG_dict[OG_id]:
                for g_id in OG_dict[OG_id][sp_id]:
                    if g_id != '':
                        f.write("%s\t%s\t%s\n" %
                                (huge_rename_map[sp_id][g_id], g_id, sp_id))

    # write rename file
    all_rename_map = top_work_dir + "/rename.map"
    with open(all_rename_map, 'w') as f:
        for sp_id in huge_rename_map:
            for g_id in huge_rename_map[sp_id]:
                if g_id != '':
                    f.write("%s\t%s\t%s\n" %
                            (huge_rename_map[sp_id][g_id], g_id, sp_id))


def fasttree_one(OG_work_dir):
    pt_fa = OG_work_dir + "/pt.fa"

    aa_aln_file = pt_fa+".aln"
    aa_dnd_file = pt_fa+".dnd"
    #cmd_string = "t_coffee "+aa_file+" -method mafftgins_msa muscle_msa kalign_msa t_coffee_msa -output=fasta_aln -outfile="+aa_aln_file+" -newtree "+aa_dnd_file
    cmd_string = "clustalw2 -INFILE="+pt_fa + \
        " -ALIGN -OUTPUT=FASTA -OUTFILE="+aa_aln_file+" -type=protein"
    cmd_run(cmd_string, silence=True)

    tree_file = OG_work_dir+"/fasttree.phb"
    cmd_string = "FastTree -wag -gamma -out %s %s >/dev/null" % (
        tree_file, aa_aln_file)
    cmd_run(cmd_string, silence=True)

    return pt_fa, aa_aln_file, tree_file


def fasttree_many(OG_tsv_file, species_info_dict, work_dir, num_threads):
    mkdir(work_dir, True)
    log_file = work_dir + "/log"

    module_log = logging_init("FastTree pipeline", log_file)

    # load orthofinder group
    module_log.info('load orthofinder group')
    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    # prepare OG work dir
    module_log.info('prepare OG work dir')
    prepare_OG_work_dir(OG_dict, species_info_dict, work_dir)

    # running treebest
    module_log.info('running fasttree')
    args_list = []

    for OG_id in OG_dict:
        OG_work_dir = work_dir + "/" + OG_id
        args_list.append((OG_work_dir,))

    multiprocess_running(fasttree_one, args_list,
                         num_threads, log_file=log_file)

    return work_dir


def orthofinder_running(work_dir, species_info_dict, sp_list=None, only_on_orthogroup=True, only_print=False):
    of_dir = work_dir
    of_pt_dir = of_dir + "/pt_file"
    mkdir(of_dir, True)
    mkdir(of_pt_dir, True)

    if not sp_list:
        sp_list = list(species_info_dict.keys())

    for sp_id in sp_list:
        pt_file = species_info_dict[sp_id]['pt_file']
        copy_file(pt_file, of_pt_dir+"/%s.fasta" % sp_id)

    if only_print:
        print("source activate orthofinder")
        print("cd %s" % of_dir)
        if only_on_orthogroup:
            print("qx -pe smp 56 orthofinder -f pt_file -t 56 -a 56 -S diamond -og")


if __name__ == '__main__':
    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'
    sp_list = ["Ini", "Cau", "Sly", "Mgu", "Cca", "Ath", "Aco", "Gel", "Vpl", "Ash", "Aof", "Osa", "Acom", "Cnu", "Eve", "Xvi", "Pni", "Atr"]
    orthofinder_dir = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline'

    species_info_dict = read_species_info(ref_xlsx)
    species_info_dict = {i:species_info_dict[i] for i in species_info_dict if i in sp_list}

    orthofinder_running(orthofinder_dir, species_info_dict, sp_list=None, only_on_orthogroup=True, only_print=True)

    #
    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/pt_file/OrthoFinder/Results_Apr13/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/new_pipeline/fasttree"

    fasttree_many(OG_tsv_file, species_info_dict, fasttree_dir, 160)


    # for canrong

    ref_xlsx = '/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/seq_info.xlsx'
    sp_list = ["Osa", "Zma", "Acom", "Xvi", "Aco", "Ath", "Mdo", "Sly", "Pni", "Atr"]

    species_info_dict = read_species_info(ref_xlsx)
    species_info_dict = {i:species_info_dict[i] for i in species_info_dict if i in sp_list}

    #
    OG_tsv_file = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/pt_file/OrthoFinder/Results_May08/Orthogroups/Orthogroups.tsv"
    fasttree_dir = "/lustre/home/xuyuxing/Work/Other/Canrong/orthofinder/fasttree"

    fasttree_many(OG_tsv_file, species_info_dict, fasttree_dir, 56)
