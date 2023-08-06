"""
The script hopes to get the genome information from JGI Genome Portal

All JGI data were recorded in a file named genome_project.csv

genome-projects.csv can be download from JGI Genome Portal
login https://genome.jgi.doe.gov/portal
Advanced Search --> show all --> Report --> Download Project Overview Report

But genome-projects.csv have many other information which not about genome,
so records in genome-project.csv should be filtered. This script filter the records
by Taxonomy ID in the record, e.g. If record have Taxonomy ID and this ID is accurate than a
specific rank in NCBI Taxonomy, such as accurate than "genus" or "species", then record would be saved

Usage:
from ncbi_taxonomy import build_taxon_database
tax_record_dict = build_taxon_database(path_for_taxonomy)

from JGI import parser_of_genome_projects
species_list = parser_of_genome_projects(genome_projects_csv_file, tax_record_dict, rank="genus")


Yuxing Xu
2018.05.08  new script
"""

__author__ = 'Yuxing Xu'

import re
import xml.etree.ElementTree as ET

import toolbiox.lib.common.os
import toolbiox.api.xuyuxing.file_parser.fileIO as fr
import toolbiox.lib.xuyuxing.base.base_function as bf
import os


def Portal_ID_get(Portal_ID_raw):
    return re.findall("\"(.*)\"", Portal_ID_raw.split(",")[1])[0]


def Taxonomy_ID_get(genome_projects_record):
    """
    some of record in JGI genome_project.csv file have very long taxonomy id,
    because they are repeated by many Sequencing Project ID
    """
    seq_project_count = len(re.findall(r'(\S+)', genome_projects_record["Sequencing Project ID"]))
    tax_id_raw_len = len(genome_projects_record["Taxonomy ID"])

    if seq_project_count == 0:
        return genome_projects_record["Taxonomy ID"]

    if tax_id_raw_len % seq_project_count == 0:
        tax_id_len = int(tax_id_raw_len / seq_project_count)
        split_list = re.findall('.{%d}' % tax_id_len, genome_projects_record["Taxonomy ID"])
        if len(list(set(split_list))) == 1:
            return split_list[0]
        else:
            return genome_projects_record["Taxonomy ID"]
    return genome_projects_record["Taxonomy ID"]


def parser_of_genome_projects(genome_projects_file, tax_db_file, rank, group_taxon_id=1, keep_no_rank=True):
    from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_record_dict_db

    genome_projects_dict = fr.tsv_file_parse(genome_projects_file, seq=",")
    genome_projects_dict, col_name = fr.title_tsv_to_dict(genome_projects_dict)

    project_list = [(genome_projects_dict[i]["JGI Project Id"], Portal_ID_get(genome_projects_dict[i]["Portal ID"]),
                     Taxonomy_ID_get(genome_projects_dict[i])) for i in genome_projects_dict if i != "ID_0"]

    tax_record_dict = read_tax_record_dict_db(tax_db_file, [i[2] for i in project_list])

    species_list = []
    for Project_ID, Portal_ID, Taxonomy_ID in project_list:
        if not Taxonomy_ID == "":
            if Taxonomy_ID in tax_record_dict:
                if tax_record_dict[Taxonomy_ID].is_a(group_taxon_id):
                    # print(Taxonomy_ID)
                    if tax_record_dict[Taxonomy_ID].lower_than(rank):
                        if hasattr(tax_record_dict[Taxonomy_ID], rank):
                            taxonomic_rank_tmp = getattr(tax_record_dict[Taxonomy_ID], rank)
                            species_list.append((Project_ID, Portal_ID, Taxonomy_ID, taxonomic_rank_tmp))
                        elif keep_no_rank:
                            species_list.append((Project_ID, Portal_ID, Taxonomy_ID, Taxonomy_ID))

    return species_list


"curl 'https://signon.jgi.doe.gov/signon/create' --data-urlencode 'login=USER_NAME' --data-urlencode 'password=USER_PASSWORD' -c cookies > /dev/null"


def pull_info(user_name, passwd, cookie_path, output_xml, Portal_ID, directly_download):
    cmd_string = "curl 'https://genome.jgi.doe.gov/portal/ext-api/downloads/get-directory?organism=%s' -b %s > %s" % (
        Portal_ID, cookie_path, output_xml)

    if directly_download is False:
        return cmd_string

    lib.common.os.cmd_run(cmd_string)

    if os.path.exists(output_xml) and os.path.getsize(output_xml) != 0:
        return output_xml
    else:
        login_string = "curl 'https://signon.jgi.doe.gov/signon/create' --data-urlencode 'login=%s' --data-urlencode 'password=%s' -c %s > /dev/null" % (
            user_name, passwd, cookie_path)
        lib.common.os.cmd_run(login_string)
        lib.common.os.cmd_run(cmd_string)
        return output_xml


def pull_file(user_name, passwd, cookie_path, output_file, want_url, directly_download):
    cmd_string = "curl '%s' -b %s > %s" % (
        want_url.replace("&amp;", "&"), cookie_path, output_file)

    if directly_download is False:
        return cmd_string

    lib.common.os.cmd_run(cmd_string)

    if os.path.exists(output_file) and os.path.getsize(output_file) != 0:
        return output_file
    else:
        login_string = "curl 'https://signon.jgi.doe.gov/signon/create' --data-urlencode 'login=%s' --data-urlencode 'password=%s' -c %s > /dev/null" % (
            user_name, passwd, cookie_path)
        lib.common.os.cmd_run(login_string)
        lib.common.os.cmd_run(cmd_string)
        return output_file


def xml_complete(xml_path):
    flag = 0
    if not os.path.exists(xml_path):
        return 0
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        flag = 1
    except:
        with open(xml_path) as f:
            strings = f.read()
            if re.match(r"User \S+ does not have access to .*", strings):
                flag = 1
    return flag


def uniq_file_record(file_list):
    def good_choose(file_list_tmp):
        for file_record in file_list_tmp:
            file_url, file_name, file_md5, tag_tmp, stat, file_type, file_size = file_record
            match_url = re.match(r'.*_JAMO.*', file_url)
            if match_url:
                return file_record
        return file_list_tmp[0]

    file_dir = {}
    for file_record in file_list:
        file_url, file_name, file_md5, tag_tmp, stat, file_type, file_size = file_record
        if not file_name in file_dir:
            file_dir[file_name] = []
        file_dir[file_name].append(file_record)

    output_list = []
    for file_name in file_dir:
        file_list = file_dir[file_name]
        output_list.append(good_choose(file_list))

    return output_list


def file_stat_check(file_stat):
    from toolbiox.lib.common.os import md5sum_check
    file_url, file_path, md5_string, tag_tmp, stat, file_type_tmp, file_size = file_stat
    stat = "renew"
    if md5_string == "":
        if os.path.exists(file_path) and os.path.getsize(file_path) == int(file_size):
            stat = "ok"
    if md5sum_check(file_path, md5_string):
        stat = "ok"
    file_stat_new = (file_url, file_path, md5_string, tag_tmp, stat, file_type_tmp, file_size)
    return file_stat_new


def record_num_in_gzip_fasta(file_gz):
    import gzip
    with gzip.open(file_gz, 'rt') as f:
        num = 0
        for each_line in f:
            record_head = re.match(r"^>", each_line)
            if record_head:
                num = num + 1
    return num


def best_JGI_for_group(download_jgi_fungi):
    taxon_group_dict = {}
    for Portal_ID in download_jgi_fungi:
        JGI_record_temp = download_jgi_fungi[Portal_ID]
        portal_id, taxon_id, group_id = JGI_record_temp["taxon_id"]
        for version_tmp in JGI_record_temp["annotation"]:
            pt_file = [i for i in JGI_record_temp["annotation"][version_tmp] if i[5] == "pt_file"][0]
            if not group_id in taxon_group_dict:
                taxon_group_dict[group_id] = []
            taxon_group_dict[group_id].append((pt_file, portal_id, version_tmp))

    best_JGI_for_groups_list = {}
    for group_id in taxon_group_dict:
        if len(taxon_group_dict[group_id]) > 1:
            best_one = \
                sorted(taxon_group_dict[group_id], key=lambda x: record_num_in_gzip_fasta(x[0][1]), reverse=True)[0]
        else:
            best_one = taxon_group_dict[group_id][0]
        best_JGI_for_groups_list[group_id] = (best_one[1], best_one[2])

    return best_JGI_for_groups_list


if __name__ == '__main__':
    from toolbiox.lib.xuyuxing.evolution.taxonomy import build_taxon_database, store_tax_record_into_sqlite

    path_for_taxonomy = "/lustre/home/xuyuxing/Database/NCBI/taxonomy"
    tax_db_file = "/lustre/home/xuyuxing/Database/NCBI/taxonomy/tax_xyx.db"
    genome_projects_csv_file = "/lustre/home/xuyuxing/Database/genome/2020/JGI/genome-projects.csv"

    # you can store taxonomy database in sqlite3 file
    tax_record_dict = build_taxon_database(path_for_taxonomy)
    store_tax_record_into_sqlite(tax_record_dict, tax_db_file)

    # 4751 for fungi
    # this list will tell you how many genome project in JGI which remove reduct in genus level in fungi
    species_list = parser_of_genome_projects(genome_projects_csv_file, tax_db_file, rank="genus", group_taxon_id="4751",
                                             keep_no_rank=False)

    genus_list = list(set([i[3] for i in species_list]))

    species_list = parser_of_genome_projects(genome_projects_csv_file, tax_db_file, rank="family",
                                             group_taxon_id="4751", keep_no_rank=False)

    family_list = list(set([i[3] for i in species_list]))

    species_list = parser_of_genome_projects(genome_projects_csv_file, tax_db_file, rank="order",
                                             group_taxon_id="4751", keep_no_rank=False)

    order_list = list(set([i[3] for i in species_list]))
