from toolbiox.api.xuyuxing.resource.kegg.kegg_config import *
import urllib.request
import os
import errno
import sys
from toolbiox.lib.common.os import mkdir
from toolbiox.lib.common.fileIO import tsv_file_dict_parse, read_list_file, tsv_file_dict_parse_big
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins

# Do not change!

TAX_URL = 'http://rest.kegg.jp/list/organism'
MODULE_URL = 'http://rest.kegg.jp/list/module'
PATHWAY_URL = 'http://rest.kegg.jp/list/pathway'
KO_URL = "http://rest.kegg.jp/list/ko"

GENOME_LINK_URL = "http://rest.kegg.jp/link/genome/"
PATHWAY_LINK_URL = 'http://rest.kegg.jp/link/pathway/'
MODULE_LINK_URL = 'http://rest.kegg.jp/link/module/'
KO_LINK_URL = "http://rest.kegg.jp/link/ko/"


def get_url_into_file(url_input, output_file_name):
    try:
        os.remove(output_file_name)
    except:
        pass

    urllib.request.urlretrieve(url_input, output_file_name)

    return output_file_name


def get_url_into_string(url_input):
    tmp_file, tmp_out = urllib.request.urlretrieve(url_input)

    with open(tmp_file, 'r') as f:
        string_output = f.read()

    os.remove(tmp_file)

    return string_output


def get_module_list(output_file_name):
    """
    Get module detail info file with all organism codes from KEGG.
    http://rest.kegg.jp/list/module
    """
    get_url_into_file(MODULE_URL, output_file_name + ".tmp")

    try:
        os.remove(output_file_name)
    except:
        pass

    with open(output_file_name + '.tmp', 'r') as fin, open(
        output_file_name, 'w') as fout:
        for line in fin.readlines():
            module = line.split('\t')[0].split(':')[1]
            name = line.split('\t')[1]
            fout.write(module + '\t' + name)

    os.remove(output_file_name + '.tmp')

    return output_file_name


def get_pathway_list(output_file_name):
    """
    Get pathway detail info file with all organism codes from KEGG.
    http://rest.kegg.jp/list/pathway
    """
    get_url_into_file(PATHWAY_URL, output_file_name + ".tmp")

    try:
        os.remove(output_file_name)
    except:
        pass

    with open(output_file_name + '.tmp', 'r') as fin, open(
        output_file_name, 'w') as fout:
        for line in fin.readlines():
            module = line.split('\t')[0].split(':')[1]
            name = line.split('\t')[1]
            fout.write(module + '\t' + name)

    os.remove(output_file_name + '.tmp')

    return output_file_name


def get_taxonomy_code(output_file_name):
    """
    Get taxonomy file with all organism codes from KEGG.
    http://rest.kegg.jp/list/organism
    """
    return get_url_into_file(TAX_URL, output_file_name)
    


def parse_taxon_file(taxon_file):
    taxon_dict = tsv_file_dict_parse(taxon_file,key_col='id',fieldnames=['id','code','species','taxonomy'])
    return taxon_dict


def get_species_gene_list(species_code, output_file_name):
    """
    Get gene list of one species from KEGG.
    http://rest.kegg.jp/link/genome/ath
    """
    get_url_into_file(GENOME_LINK_URL + species_code, output_file_name + ".tmp")

    try:
        os.remove(output_file_name)
    except:
        pass

    with open(output_file_name + '.tmp', 'r') as fin, open(
        output_file_name, 'w') as fout:
        for line in fin.readlines():
            gene_name = line.split('\t')[0]
            fout.write(gene_name + '\n')

    os.remove(output_file_name + '.tmp')

    return output_file_name


def parse_gene_list(gene_list_file):
    return read_list_file(gene_list_file)


def get_species_gene_pathway(species_code,output_file_name):

    get_url_into_file(PATHWAY_LINK_URL + species_code, output_file_name + ".pathway_link")
    get_url_into_file(PATHWAY_URL + "/" + species_code, output_file_name + ".pathway_list")
    
    pathway_info = tsv_file_dict_parse(output_file_name + ".pathway_list", fieldnames=['p_id','info'], key_col='p_id')
    pathway_link = tsv_file_dict_parse(output_file_name + ".pathway_link", fieldnames=['id','p_id'], key_col='id')

    with open(output_file_name, 'w') as f:
        for i in pathway_link:
            g_id  = i
            p_id = pathway_link[i]['p_id']
            p_info = pathway_info[p_id]['info']
            f.write("%s\t%s\t%s\n" % (g_id, p_id, p_info))
    
    os.remove(output_file_name + ".pathway_list")
    os.remove(output_file_name + ".pathway_link")

    return output_file_name


def get_species_gene_module(species_code,output_file_name):

    get_url_into_file(MODULE_LINK_URL + species_code, output_file_name + ".module_link")
    get_url_into_file(MODULE_URL, output_file_name + ".module_list")
    
    module_info = tsv_file_dict_parse(output_file_name + ".module_list", fieldnames=['m_id','info'], key_col='m_id')
    module_link = tsv_file_dict_parse(output_file_name + ".module_link", fieldnames=['id','m_id'], key_col='id')

    with open(output_file_name, 'w') as f:
        for i in module_link:
            g_id  = i
            m_id = module_link[i]['m_id']
            m_id = "md:" + m_id.split(":")[1].split("_")[1]
            m_info = module_info[m_id]['info']
            f.write("%s\t%s\t%s\n" % (g_id, m_id, m_info))
    
    os.remove(output_file_name + ".module_list")
    os.remove(output_file_name + ".module_link")

    return output_file_name



def get_species_gene_ko(species_code,output_file_name):

    get_url_into_file(KO_LINK_URL + species_code, output_file_name + ".ko_link")
    get_url_into_file(KO_URL, output_file_name + ".ko_list")
    
    ko_info = tsv_file_dict_parse(output_file_name + ".ko_list", fieldnames=['k_id','info'], key_col='k_id')
    ko_link = tsv_file_dict_parse(output_file_name + ".ko_link", fieldnames=['id','k_id'], key_col='id')

    with open(output_file_name, 'w') as f:
        for i in ko_link:
            g_id  = i
            k_id = ko_link[i]['k_id']
            if k_id in ko_info:
                k_info = ko_info[k_id]['info']
                f.write("%s\t%s\t%s\n" % (g_id, k_id, k_info))
            else:
                f.write("%s\t%s\t%s\n" % (g_id, k_id, 'None'))
            
    
    os.remove(output_file_name + ".ko_list")
    os.remove(output_file_name + ".ko_link")

    return output_file_name



def aa_seq_url(gene_list):
    gene_string = printer_list(gene_list,sep='+')
    url_string = "http://rest.kegg.jp/get/"+gene_string+"/aaseq"
    return url_string

def covert_url(gene_list):
    gene_string = printer_list(gene_list,sep='+')
    url_string = "http://rest.kegg.jp/conv/ncbi-geneid/"+gene_string
    return url_string

def covert_url_p(gene_list):
    gene_string = printer_list(gene_list,sep='+')
    url_string = "http://rest.kegg.jp/conv/ncbi-proteinid/"+gene_string
    return url_string

def ncbi_gene_id_vs_protein_accession_map(gene2accession_file, silence=True):
    protein_id_vs_gene_id_map = {}
    
    num = 0
    for id_tmp, info_dict in tsv_file_dict_parse_big(gene2accession_file, gzip_flag=True):
        
        p_id = info_dict['protein_accession.version']
        gi = info_dict['GeneID']
        protein_id_vs_gene_id_map[p_id] = gi

        num += 1
        if num % 100000 == 0 and not silence:
            print(num)

    return protein_id_vs_gene_id_map


def gene_id_convert(gene_list,function,step=100,silence=True):
    gene_id_map = {}

    for i in range(0,len(gene_list),step):
        if not silence:
            print(i)
        sub_gene_list = gene_list[i:i+step]
        url_string = function(sub_gene_list)
        try:
            output_string = get_url_into_string(url_string)
            for line in output_string.split("\n"):
                raw_id, new_id = line.split("\t")
                new_id = new_id.split(":")[1]

                gene_id_map[raw_id] = new_id

        except:
            pass

    return gene_id_map


def get_species_gene_aa(species_code,output_file_name,step=100):

    get_species_gene_list(species_code, output_file_name+".id")
    gene_list = parse_gene_list(output_file_name+".id")

    try:
        os.remove(output_file_name)
    except:
        pass

    for i in range(0,len(gene_list),step):
        sub_gene_list = gene_list[i:i+step]
        url_string = aa_seq_url(sub_gene_list)
        try:
            get_url_into_file(url_string, output_file_name+".tmp.aa")

            with open(output_file_name + '.tmp.aa', 'r') as fin, open(
                output_file_name, 'a') as fout:
                for line in fin.readlines():
                    fout.write(line)

            os.remove(output_file_name+".tmp.aa")

        except:
            pass

    os.remove(output_file_name+".id")

    return output_file_name
    

# Main
if __name__ == '__main__':

    from toolbiox.lib.xuyuxing.base.base_function import mkdir
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx

    species_code = 'ath'
    work_dir = '/lustre/home/xuyuxing/Database/kegg/ath'
    ncbi_aa_fasta = '/lustre/home/xuyuxing/Database/kegg/GCF_000001735.4_TAIR10.1_protein.faa'
    gene2accession_file = '/lustre/home/xuyuxing/Database/NCBI/gene/2020/gene2accession.gz'
    
    mkdir(work_dir, True)
    kegg_gene_id_file = work_dir + "/" + species_code + ".kegg_gene_id.txt"
    get_species_gene_list(species_code, kegg_gene_id_file)
    gene_list = parse_gene_list(kegg_gene_id_file)

    # get pathway
    kegg_pathway_file = work_dir + "/" + species_code + ".kegg_pathway.txt"
    get_species_gene_pathway(species_code, kegg_pathway_file)
    pathway_dict = tsv_file_dict_parse(kegg_pathway_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get module
    kegg_module_file = work_dir + "/" + species_code + ".kegg_module.txt"
    get_species_gene_module(species_code, kegg_module_file)
    module_dict = tsv_file_dict_parse(kegg_module_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get ko
    kegg_ko_file = work_dir + "/" + species_code + ".kegg_ko.txt"
    get_species_gene_ko(species_code, kegg_ko_file)
    ko_dict = tsv_file_dict_parse(kegg_ko_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get seq
    ## get ncbi gi
    ncbi_gi_map = gene_id_convert(gene_list,covert_url,step=100,silence=False)
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
    fasta_record_dict = read_fasta_by_faidx(ncbi_aa_fasta)
    protein_id_vs_gene_id_map = ncbi_gene_id_vs_protein_accession_map(gene2accession_file, silence=True)
    
    gi_seq_dict = {}
    for ncbi_p_id in fasta_record_dict:
        if ncbi_p_id in protein_id_vs_gene_id_map:
            gi = protein_id_vs_gene_id_map[ncbi_p_id]
            if not gi in gi_seq_dict:
                gi_seq_dict[gi] = fasta_record_dict[ncbi_p_id]
            else:
                if fasta_record_dict[ncbi_p_id].len() > gi_seq_dict[gi].len():
                    gi_seq_dict[gi] = fasta_record_dict[ncbi_p_id]


    # merge info
    kegg_gene_dict = {}
    for kg_id in ncbi_gi_map:
        if kg_id in pathway_dict:
            pw_id = pathway_dict[kg_id]['id']
            pw_info = pathway_dict[kg_id]['des']
        else:
            pw_id = None
            pw_info = None

        if kg_id in module_dict:
            md_id = module_dict[kg_id]['id']
            md_info = module_dict[kg_id]['des']
        else:
            md_id = None
            md_info = None

        if kg_id in ko_dict:
            ko_id = ko_dict[kg_id]['id']
            ko_info = ko_dict[kg_id]['des']
        else:
            ko_id = None
            ko_info = None

        gi = ncbi_gi_map[kg_id]
        
        if gi in gi_seq_dict:
            seq = gi_seq_dict[gi]
            ncbi_id = gi_seq_dict[gi].seqname.split()[0]
        else:
            seq = None
            ncbi_id = None
        
        kegg_gene_dict[kg_id] = (kg_id,ncbi_id,pw_id,pw_info,md_id,md_info,ko_id,ko_info)
        
    kegg_overview_table = work_dir + "/" + species_code + ".overview.tsv"
    with open(kegg_overview_table, 'w') as f:
        for kg_id in kegg_gene_dict:
            f.write(printer_list(kegg_gene_dict[kg_id])+"\n")



    ## osa

    species_code = 'osa'
    work_dir = '/lustre/home/xuyuxing/Database/kegg/osa'
    ncbi_aa_fasta = '/lustre/home/xuyuxing/Database/kegg/GCF_000005425.2_Build_4.0_protein.faa'
    gene2accession_file = '/lustre/home/xuyuxing/Database/NCBI/gene/2020/gene2accession.gz'
    
    mkdir(work_dir, True)
    kegg_gene_id_file = work_dir + "/" + species_code + ".kegg_gene_id.txt"
    get_species_gene_list(species_code, kegg_gene_id_file)
    gene_list = parse_gene_list(kegg_gene_id_file)

    # get pathway
    kegg_pathway_file = work_dir + "/" + species_code + ".kegg_pathway.txt"
    get_species_gene_pathway(species_code, kegg_pathway_file)
    pathway_dict = tsv_file_dict_parse(kegg_pathway_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get module
    kegg_module_file = work_dir + "/" + species_code + ".kegg_module.txt"
    get_species_gene_module(species_code, kegg_module_file)
    module_dict = tsv_file_dict_parse(kegg_module_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get ko
    kegg_ko_file = work_dir + "/" + species_code + ".kegg_ko.txt"
    get_species_gene_ko(species_code, kegg_ko_file)
    ko_dict = tsv_file_dict_parse(kegg_ko_file,fieldnames=['gene_id','id','des'],key_col='gene_id')

    # get seq
    ## get ncbi gi
    ncbi_gi_map = gene_id_convert(gene_list,covert_url_p,step=100,silence=False)
    
    # merge info
    kegg_gene_dict = {}
    for kg_id in gene_list:
        if kg_id in pathway_dict:
            pw_id = pathway_dict[kg_id]['id']
            pw_info = pathway_dict[kg_id]['des']
        else:
            pw_id = None
            pw_info = None

        if kg_id in module_dict:
            md_id = module_dict[kg_id]['id']
            md_info = module_dict[kg_id]['des']
        else:
            md_id = None
            md_info = None

        if kg_id in ko_dict:
            ko_id = ko_dict[kg_id]['id']
            ko_info = ko_dict[kg_id]['des']
        else:
            ko_id = None
            ko_info = None

        if kg_id in ncbi_gi_map:
            ncbi_pid = ncbi_gi_map[kg_id]
        else:
            ncbi_pid = None
        
        kegg_gene_dict[kg_id] = (kg_id,ncbi_pid,pw_id,pw_info,md_id,md_info,ko_id,ko_info)
    
    kegg_overview_table = work_dir + "/" + species_code + ".overview.tsv"
    with open(kegg_overview_table, 'w') as f:
        for kg_id in kegg_gene_dict:
            f.write(printer_list(kegg_gene_dict[kg_id])+"\n")


    

