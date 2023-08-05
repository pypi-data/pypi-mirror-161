import os
import re
from Bio import SeqIO


repbase_browse_url = "https://www.girinst.org/repbase/update/browse.php"









RepBase_merged_fasta_id_file = "/lustre/home/xuyuxing/Database/RepBase/RepBase26.02.merged.fasta.id"
RepBase_embl_dir = "/lustre/home/xuyuxing/Database/RepBase/RepBase26.02.embl"


def embl_parser(RepBase_embl_dir):
    ref_file_list = []
    file_dir_list = os.listdir(RepBase_embl_dir)
    for i in file_dir_list:
        if re.match(r'^.*\.ref$', i):
            file_name = RepBase_embl_dir + "/" + i
            ref_file_list.append(file_name)

    RepBase_appendix_embl_dir = RepBase_embl_dir + "/appendix"
    file_dir_list = os.listdir(RepBase_appendix_embl_dir)
    for i in file_dir_list:
        if re.match(r'^.*\.ref$', i):
            file_name = RepBase_appendix_embl_dir + "/" + i
            ref_file_list.append(file_name)

    ref_file_list_recode = []
    for file_name in ref_file_list:
        with open(file_name+".recode", 'w') as fo:
            with open(file_name, 'r', encoding='cp1252') as fi:
                for each_line in fi:
                    fo.write(each_line)
        ref_file_list_recode.append(file_name+".recode")


    for file_name in ref_file_list_recode:
        for record in SeqIO.parse(file_name, "embl"):
            print(record.name)











with open(RepBase_merged_fasta_id_file, 'r') as f:
    id_info_dict = {}
    group_list = []
    for each_line in f:
        each_line = each_line.strip()

        blast_rec_id = each_line.split()[0]
        
        # normal
        matchobj = re.match(r'^(.*)\t(.*)\t(.*)$', each_line)
        if matchobj:
            rec_id, group_id, sp_id = matchobj.groups()
            group_list.append(group_id)

            if blast_rec_id not in id_info_dict:
                id_info_dict[blast_rec_id] = []
            id_info_dict[blast_rec_id].append(group_id)
            id_info_dict[blast_rec_id] = list(set(id_info_dict[blast_rec_id]))
    group_list = list(set(group_list))
            

