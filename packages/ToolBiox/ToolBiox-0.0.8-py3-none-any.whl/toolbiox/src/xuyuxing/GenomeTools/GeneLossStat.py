from collections import OrderedDict
import pickle
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse


ortho_table = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Orthogroups.tsv'
ol_dir = '/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ortho/protein/OrthoFinder/Results_Nov17/Orthologues'

gene_loss_table_dict = OrderedDict([
    ('Ash', ['T1088818N0.gene_model.protein', '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Ash/4.table_report.txt']),
    ('Dca', ['T906689N0.gene_model.protein', '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Dca/4.table_report.txt']),
    ('Peq', ['T78828N0.gene_model.protein', '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Peq/4.table_report.txt']),
    ('Gel', ['Gel.gene_model.protein', '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Gel/4.table_report.txt']),
    ('Cau', ['T267555N0.gene_model.protein', '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Cau/4.table_report.txt'])]
)


reference_genome = {
    'Ath' : ["T3702N0.gene_model.protein", "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/all_annotation.pyb"],
    'Osa': ["T4530N0.gene_model.protein", "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function/all_annotation.pyb"]
}

orthogroup_dict = tsv_file_dict_parse(ortho_table,key_col='Orthogroup')

for spec in gene_loss_table_dict:
    table_report_file = gene_loss_table_dict[spec][1]
    tmp_info = tsv_file_parse(table_report_file, key_col=1, fields="1,2,3,4")
    gene_loss_table_dict[spec].append(tmp_info)

# Ath

TEMP = open(reference_genome['Ath'][1], 'rb')
Ath_annotation_dict = pickle.load(TEMP)
TEMP.close()

ath_gene_hash = {}
for OG_id in orthogroup_dict:
    ath_gene_id_list = orthogroup_dict[OG_id][reference_genome['Ath'][0]].split(", ")
    for g_id in ath_gene_id_list:
        ath_gene_hash[g_id] = [OG_id]

for g_id in ath_gene_hash:
    OG_id = ath_gene_hash[g_id][0]
    loss_flag_list = []
    for spec in gene_loss_table_dict:
        gene_loss_dict = gene_loss_table_dict[spec][2]

        if OG_id in gene_loss_dict:
            Conserved='yes'
            if gene_loss_dict[OG_id][2] == 'True':
                loss_flag_list.append('yes')
            else:
                loss_flag_list.append('no')
        else:
            loss_flag_list.append('no')
            Conserved='no'
    ath_gene_hash[g_id].append(Conserved)
    ath_gene_hash[g_id].extend(loss_flag_list)

# ol
ath_gene_ol_dict = {}
for spec in gene_loss_table_dict:
    ol_file = ol_dir + "/Orthologues_" + reference_genome['Ath'][0] + "/" + reference_genome['Ath'][0] + "__v__" + gene_loss_table_dict[spec][0] + ".tsv"
    ath_gene_ol_hash = {}
    tmp_info = tsv_file_parse(ol_file)
    for i in tmp_info:
        ath_gene_list = tmp_info[i][1].split(", ")
        for j in ath_gene_list:
            ath_gene_ol_hash[j] = tmp_info[i][2].split(",")
    ath_gene_ol_dict[spec] = ath_gene_ol_hash

    print(spec,max([len(ath_gene_ol_hash[i]) for i in ath_gene_ol_hash]))


ath_gene_og_dict = {}
for spec in gene_loss_table_dict:
    ath_gene_og_dict[spec] = {}
    for OG_id in orthogroup_dict:
        ath_gene_id_list = orthogroup_dict[OG_id][reference_genome['Ath'][0]].split(", ")
        spec_gene_id_list = orthogroup_dict[OG_id][gene_loss_table_dict[spec][0]].split(", ")
        for i in ath_gene_id_list:
            ath_gene_og_dict[spec][i] = spec_gene_id_list
    print(spec,max([len(ath_gene_og_dict[spec][i]) for i in ath_gene_og_dict[spec]]))


# output
from toolbiox.lib.common.util import printer_list

with open("/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Ath.ref.gene_loss.tsv", 'w') as f:
    head_list = ["ref_id", "OrthoGroup_ID","Conserved", "Lossed_in_Ash","Lossed_in_Dca","Lossed_in_Peq","Lossed_in_Gel","Lossed_in_Cau","Gene_ID_in_Ash","Gene_ID_in_Dca","Gene_ID_in_Peq","Gene_ID_in_Gel","Gene_ID_in_Cau","Gene Name", "Alias", "Full Name", "key_words", "Computational Description", "PubMed_number",
                     "KEGG pathway(id)", "KEGG pathway", "KEGG module(id)", "KEGG module",  "KEGG KO(id)", "KEGG KO", "GO(id)", "GO_parent", "GO", "Plantcyc(id)", "Plantcyc",  "clean_id"]

    f.write(printer_list(head_list)+"\n")

    for g_id in Ath_annotation_dict:
        anno_list = Ath_annotation_dict[g_id]
        insert_info = []
        if g_id in ath_gene_hash:
            insert_info = ath_gene_hash[g_id]
        else:
            insert_info = ["-"] * 7

        for spec in gene_loss_table_dict:

            if g_id in ath_gene_ol_dict[spec]:
                ol_gene_list = ath_gene_ol_dict[spec][g_id]
            elif g_id in ath_gene_og_dict[spec]:
                ol_gene_list = ath_gene_og_dict[spec][g_id]
            else:
                ol_gene_list = []

            ol_gene_string = printer_list(ol_gene_list,';')

            insert_info.append(ol_gene_string)


        output_list = [anno_list[0]] + insert_info + list(anno_list[1:])

        f.write(printer_list(output_list)+"\n")



# Osa

TEMP = open(reference_genome['Osa'][1], 'rb')
Ath_annotation_dict = pickle.load(TEMP)
TEMP.close()

ath_gene_hash = {}
for OG_id in orthogroup_dict:
    ath_gene_id_list = orthogroup_dict[OG_id][reference_genome['Osa'][0]].split(", ")
    for g_id in ath_gene_id_list:
        ath_gene_hash[g_id] = [OG_id]

for g_id in ath_gene_hash:
    OG_id = ath_gene_hash[g_id][0]
    loss_flag_list = []
    for spec in gene_loss_table_dict:
        gene_loss_dict = gene_loss_table_dict[spec][2]

        if OG_id in gene_loss_dict:
            Conserved='yes'
            if gene_loss_dict[OG_id][2] == 'True':
                loss_flag_list.append('yes')
            else:
                loss_flag_list.append('no')
        else:
            loss_flag_list.append('no')
            Conserved='no'
    ath_gene_hash[g_id].append(Conserved)
    ath_gene_hash[g_id].extend(loss_flag_list)

# ol
ath_gene_ol_dict = {}
for spec in gene_loss_table_dict:
    ol_file = ol_dir + "/Orthologues_" + reference_genome['Osa'][0] + "/" + reference_genome['Osa'][0] + "__v__" + gene_loss_table_dict[spec][0] + ".tsv"
    ath_gene_ol_hash = {}
    tmp_info = tsv_file_parse(ol_file)
    for i in tmp_info:
        ath_gene_list = tmp_info[i][1].split(", ")
        for j in ath_gene_list:
            ath_gene_ol_hash[j] = tmp_info[i][2].split(",")
    ath_gene_ol_dict[spec] = ath_gene_ol_hash

    print(spec,max([len(ath_gene_ol_hash[i]) for i in ath_gene_ol_hash]))


ath_gene_og_dict = {}
for spec in gene_loss_table_dict:
    ath_gene_og_dict[spec] = {}
    for OG_id in orthogroup_dict:
        ath_gene_id_list = orthogroup_dict[OG_id][reference_genome['Ath'][0]].split(", ")
        spec_gene_id_list = orthogroup_dict[OG_id][gene_loss_table_dict[spec][0]].split(", ")
        for i in ath_gene_id_list:
            ath_gene_og_dict[spec][i] = spec_gene_id_list
    print(spec,max([len(ath_gene_og_dict[spec][i]) for i in ath_gene_og_dict[spec]]))


# output
from toolbiox.lib.common.util import printer_list

with open("/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44/Osa.ref.gene_loss.tsv", 'w') as f:
    head_list = ["ref_id", "OrthoGroup_ID","Conserved", "Lossed_in_Ash","Lossed_in_Dca","Lossed_in_Peq","Lossed_in_Gel","Lossed_in_Cau","Gene_ID_in_Ash","Gene_ID_in_Dca","Gene_ID_in_Peq","Gene_ID_in_Gel","Gene_ID_in_Cau"] + ["Gene Name", "Alias", "Full Name", "key_words", "Computational Description", "PubMed_number",
                     "KEGG pathway(id)", "KEGG pathway", "KEGG module(id)", "KEGG module",  "KEGG KO(id)", "KEGG KO", "GO(id)", "GO_parent", "GO", "Plantcyc(id)", "Plantcyc",  "clean_id"]


    f.write(printer_list(head_list)+"\n")

    for g_id in Ath_annotation_dict:
        anno_list = Ath_annotation_dict[g_id]
        insert_info = []
        if g_id in ath_gene_hash:
            insert_info = ath_gene_hash[g_id]
        else:
            insert_info = ["-"] * 7

        for spec in gene_loss_table_dict:

            if g_id in ath_gene_ol_dict[spec]:
                ol_gene_list = ath_gene_ol_dict[spec][g_id]
            elif g_id in ath_gene_og_dict[spec]:
                ol_gene_list = ath_gene_og_dict[spec][g_id]
            else:
                ol_gene_list = []

            ol_gene_string = printer_list(ol_gene_list,';')

            insert_info.append(ol_gene_string)


        output_list = [anno_list[0]] + insert_info + list(anno_list[1:])

        f.write(printer_list(output_list)+"\n")


