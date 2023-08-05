from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import re
from toolbiox.api.xuyuxing.comp_genome.orthofinder import OG_tsv_file_parse

class InterproRecord(object):
    def __init__(self, seqID, domain_list):
        self.seqID = seqID
        self.domain_list = domain_list

    def all_analysis(self):
        all_analysis_list = []
        for i in self.domain_list:
            all_analysis_list.append(i["Analysis"])
        all_analysis_list = list(set(all_analysis_list))
        return all_analysis_list

    def domain_from_analysis(self, analysis_name):
        select_domain_list = []
        for i in self.domain_list:
            if i["Analysis"] == analysis_name:
                select_domain_list.append(i)
        return select_domain_list

    def get_go(self):
        GO_list = []
        for domain in self.domain_list:
            if domain['GO'] is None or domain['GO'] == '':
                continue
            GO_list.extend(domain['GO'].split("|"))

        GO_list = list(set(GO_list))

        self.go = GO_list

        return GO_list




column_list = ["query", "MD5", "Length", "Analysis", "Accession", "Description", "Start", "Stop", "Score", "Status",
               "Date", "InterPro_accession", "InterPro_annotations", "GO", "Pathways"]


def interproscan_results_parser(tsv_file):
    output = tsv_file_dict_parse(tsv_file, fieldnames=column_list)
    query_dict = {}
    for id_tmp in output:
        info = output[id_tmp]
        if info["query"] not in query_dict:
            query_dict[info["query"]] = InterproRecord(info["query"], [])
        query_dict[info["query"]].domain_list.append(info)
    return query_dict


def parse_entry_file(entry_file):

    tmp_dict = tsv_file_dict_parse(entry_file, key_col='ENTRY_AC')
    output_dict = {}
    for i in tmp_dict:
        if tmp_dict[i]['ENTRY_TYPE'] not in output_dict:
            output_dict[tmp_dict[i]['ENTRY_TYPE']] = {}
        output_dict[tmp_dict[i]['ENTRY_TYPE']][tmp_dict[i]
                                               ['ENTRY_AC']] = tmp_dict[i]['ENTRY_NAME']

    return output_dict


def parse_interpro2go(interpro2go_file):
    ip2go_dict = []
    with open(interpro2go_file, 'r') as f:
        for each_line in f:
            each_line = each_line.strip()
            ip = re.findall('IPR\d\d\d\d\d\d', each_line)[0]
            go = re.findall('GO:\d\d\d\d\d\d\d', each_line)[0]

            if ip not in ip2go_dict:
                ip2go_dict[ip] = []

            ip2go_dict[ip].append(go)

            ip2go_dict[ip] = list(set(ip2go_dict[ip]))

    return ip2go_dict


def get_orthogroup_GO(Orthogroups_tsv, gene_interpro_tsv):
    OG_dict = OG_tsv_file_parse(Orthogroups_tsv)
    gene_interpro_dict = interproscan_results_parser(gene_interpro_tsv)
    
    GO_dict = {}
    for OG_id in OG_dict:
        GO_list = []
        for speci in OG_dict[OG_id]:
            for gene in OG_dict[OG_id][speci]:
                if gene == '':
                    continue
                if gene in gene_interpro_dict:
                    GO_list.extend(gene_interpro_dict[gene].get_go())
        GO_list = list(set(GO_list))
        GO_dict[OG_id] = GO_list
        
    return GO_dict    



if __name__ == "__main__":

    # %%
    # make interpro family report


    # wget ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list
    interpro_entry_file = '/lustre/home/xuyuxing/Database/Interpro/entry.list'
    entry_dict = parse_entry_file(interpro_entry_file)

    # wget ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go
    interpro2go_file = '/lustre/home/xuyuxing/Database/Interpro/interpro2go'

    reference_genome_table = '/lustre/home/xuyuxing/Work/Gel/WPGmapper/Gel_ref.xlsx'
    specie_list = ["T55571N0", "T90708N0", "T1088818N0", "T4686N0", "T906689N0", "T91201N0", "T78828N0", "T13894N0", "T51953N0", "T4530N0", "T4577N0", "T4641N0"]

    import pandas as pd

    query_db = pd.read_excel(reference_genome_table)
    interpro_file_dict = {}
    for index in query_db.index:
        query_id = str(query_db.loc[index]['id'])
        interpro_file = str(query_db.loc[index]['function_anno'])

        if not pd.isna(query_id) and not pd.isna(interpro_file) and query_id in specie_list:
            interpro_file_dict[query_id] = interpro_file

    ip_gene_dict = {}

    for query_id in interpro_file_dict:
        print(query_id)

        interpro_file = interpro_file_dict[query_id]
        interpro_dict = interproscan_results_parser(interpro_file)

        ip_gene = {}

        for g_id in interpro_dict:
            for domain_dict in interpro_dict[g_id].domain_list:
                ip = domain_dict['InterPro_accession']
                if ip not in ip_gene:
                    ip_gene[ip] = []
                ip_gene[ip].append(g_id)
                ip_gene[ip] = list(set(ip_gene[ip]))
        
        ip_gene_dict[query_id] = ip_gene

    # ip_gene_count

    ip_list = []

    for query_id in ip_gene_dict:
        ip_list.extend(ip_gene_dict[query_id])

    ip_list = list(set(ip_list))

    ip_count_dict = {}

    for ip in ip_list:
        count_list = []
        for sp in specie_list:
            if ip in ip_gene_dict[sp]:
                count_list.append(len(ip_gene_dict[sp][ip]))
            else:
                count_list.append(0)
            ip_count_dict[ip] = count_list

    # output
    from toolbiox.lib.common.util import printer_list
    from toolbiox.api.xuyuxing.evolution.badirate import F_index


    entry_info_dict = {}
    for ip_type in entry_dict:
        for ip in entry_dict[ip_type]:
            entry_info_dict[ip] = (ip_type, entry_dict[ip_type][ip])

    with open("/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S12/Interpro.family.tsv", 'w') as f:

        header_list = ["Interpro AC", "Interpro Type", "Description"]
        header_list.extend(specie_list+specie_list)
        f.write(printer_list(header_list)+"\n")

        for ip in ip_count_dict:
            if ip not in entry_info_dict:
                continue

            f_index_tuple = F_index(ip_count_dict[ip])
            output_list = [ip, entry_info_dict[ip][0], entry_info_dict[ip][1]]
            output_list.extend(ip_count_dict[ip])
            output_list.extend(f_index_tuple)
            f.write(printer_list(output_list)+"\n")
    
    # %%
    # make orthogroup GO annotation

    # 
    Orthogroups_tsv = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S12/Orthogroups.tsv'
    gene_interpro_tsv = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S12/gene.interpro.tsv'
    output_file = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S12/Orthogroups.interpro.tsv'

    GO_dict = get_orthogroup_GO(Orthogroups_tsv, gene_interpro_tsv)

    from toolbiox.lib.common.util import printer_list
    with open(output_file,'w') as f:
        for i in GO_dict:
            GO_list = GO_dict[i]
            if len(GO_list) == 0:
                continue
            GO_string = printer_list(GO_list,', ')
            f.write("%s\t%s\n" % (i,GO_string))

