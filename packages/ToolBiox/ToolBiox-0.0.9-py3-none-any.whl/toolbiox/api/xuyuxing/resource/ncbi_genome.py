"""
The script hopes to get the genomes which can represent all sequenced species for HGT study by analyzing
assembly_summary file ("assembly_summary_genbank.txt" and "assembly_summary_refseq.txt") and genome size file from NCBI.
ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/species_genome_size.txt.gz (need decompressed)
"""

__author__ = 'Yuxing Xu'

import re

import toolbiox.lib.common.os
import toolbiox.lib.xuyuxing.base.base_function as bf
from toolbiox.lib.xuyuxing.base.common_command import log_print
import time
import toolbiox.lib.common.sqlite_command as sc
import sqlite3
from functools import cmp_to_key
from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_record_dict_db, read_tax_name_record_dict_db


class GenomeRecord(object):
    """
    Genome_record is a class for each record in NCBI genome database.
    """

    def __init__(self):
        pass


col_name = ["assembly_accession", "bioproject", "biosample", "wgs_master", "refseq_category", "taxid",
            "species_taxid", "organism_name", "infraspecific_name", "isolate", "version_status", "assembly_level",
            "release_type", "genome_rep", "seq_rel_date", "asm_name", "submitter", "gbrs_paired_asm",
            "paired_asm_comp", "ftp_path", "excluded_from_refseq", "relation_to_type_material"]


def build_ncbi_genome_database(assembly_summary_genbank_file, assembly_summary_refseq_file):
    """
    This func parse assembly_summary file and store data as dict which assembly_accession is keys
    and GenomeRecord class with column as attr is value.
    assembly_summary_genbank and assembly_summary_refseq have no overlap in level of assembly_accession
    :param assembly_summary_genbank_file:
    :param assembly_summary_refseq_file:
    :return: a dict
    """

    from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
    from toolbiox.lib.xuyuxing.base.common_command import dict2class
    parse_file_db = tsv_file_parse(assembly_summary_genbank_file)
    genbank_record_dict = dict2class(parse_file_db, GenomeRecord, col_name)
    parse_file_db = tsv_file_parse(assembly_summary_refseq_file)
    refseq_record_dict = dict2class(parse_file_db, GenomeRecord, col_name)

    record_dict = {}

    for i in genbank_record_dict.keys():
        record = genbank_record_dict[i]
        record.group = "genbank"
        record_dict[record.assembly_accession] = record

    for i in refseq_record_dict.keys():
        record = refseq_record_dict[i]
        record.group = "refseq"
        record_dict[record.assembly_accession] = record

    return record_dict


def genome_chooser(record_dict, tax_db_file, taxonomic_rank="genus", keep_no_rank=True, top_taxon=None):

    # step 1: Based on "gbrs_paired_asm" and "paired_asm_comp", I remove genbank assembly which paired with a refseq.
    #        Remove bad assembly that excluded_from_refseq is not empty.
    log_print("\t\tBegin: mark bad assembly record")
    for record in record_dict.keys():
        del_flag = 0
        if record_dict[record].group == "genbank" and record_dict[record].paired_asm_comp != "na":
            del_flag = 1
        if not record_dict[record].excluded_from_refseq == "":
            del_flag = 1
        if record_dict[record].ftp_path == "na":
            del_flag = 1
        if del_flag == 1:
            record_dict[record].del_flag = "Bad Record"
        else:
            record_dict[record].del_flag = "Good Record"
    log_print("\t\tEnd: mark bad assembly record")

    # step 2: Choose a best assembly to represent a given taxonomic_rank (like a genus)
    log_print("\t\tBegin: cluster assembly record to taxonomic rank")
    # classified assemblies by taxonomic_rank or lower rank(when given rank not in a record)
    class_taxon_rank_dict = {}
    num_genus = 0
    num_no_genus = 0
    if top_taxon:
        top_taxon_list = list(read_tax_name_record_dict_db(tax_db_file, [top_taxon]).values())
        if len(top_taxon_list) > 0:
            top_taxon_id = top_taxon_list[0].tax_id
        else:
            ValueError("Top taxon found nothing!")

    tax_record_db = read_tax_record_dict_db(tax_db_file,
                                            tuple([record_dict[accession_id].taxid for accession_id in record_dict]))
    num = 0
    start_time = time.time()
    for accession_id in record_dict.keys():
        record = record_dict[accession_id]
        if record.taxid in tax_record_db:
            taxid_taxon = tax_record_db[record.taxid]

            if top_taxon:
                if not top_taxon_id in set([i[0] for i in taxid_taxon.get_lineage]):
                    continue

            if hasattr(taxid_taxon, taxonomic_rank):
                num_genus = num_genus + 1
                taxonomic_rank_tmp = getattr(taxid_taxon, taxonomic_rank)
                setattr(record, taxonomic_rank, taxonomic_rank_tmp)
                if not taxonomic_rank_tmp in class_taxon_rank_dict:
                    class_taxon_rank_dict[taxonomic_rank_tmp] = []
                class_taxon_rank_dict[taxonomic_rank_tmp].append(record)
            else:
                if keep_no_rank:
                    num_no_genus = num_no_genus + 1
                    setattr(record, taxonomic_rank, "None")
                    if not record.taxid in class_taxon_rank_dict:
                        class_taxon_rank_dict[record.taxid] = []
                    class_taxon_rank_dict[record.taxid].append(record)

        num = num + 1
        round_time = time.time()
        if round_time - start_time > 10:
            log_print("\t\t\t%d/%d" % (num, len(record_dict)))
            start_time = round_time

    # sort by sort_dict
    def cmp_tmp(x, y):
        key_rank = ["del_flag", "group", "refseq_category",
                    "assembly_level", "genome_rep"]

        sort_dict = {
            "del_flag": {"Good Record": 1, "Bad Record": 2},
            "group": {"refseq": 1, "genbank": 2},
            "refseq_category": {"reference genome": 1, "representative genome": 2, "na": 3},
            "assembly_level": {"Chromosome": 1, "Complete Genome": 2, "Scaffold": 3, "Contig": 4},
            "genome_rep": {"Full": 1, "Partial": 2},
        }

        compara_flag = 0
        for key_tmp in key_rank:
            x_key_tmp = getattr(x, key_tmp)
            y_key_tmp = getattr(y, key_tmp)
            if x_key_tmp == y_key_tmp:
                continue
            elif sort_dict[key_tmp][x_key_tmp] > sort_dict[key_tmp][y_key_tmp]:
                compara_flag = 1
                break
            elif sort_dict[key_tmp][x_key_tmp] < sort_dict[key_tmp][y_key_tmp]:
                compara_flag = -1
                break

        return compara_flag

    sorted_class_taxon_rank_dict = {}
    for each_taxon in class_taxon_rank_dict:
        assembly_list = class_taxon_rank_dict[each_taxon]
        sorted_assembly_list = sorted(assembly_list, key=cmp_to_key(cmp_tmp))
        sorted_class_taxon_rank_dict[each_taxon] = sorted_assembly_list

    # def print_assembly_list(assembly_list,tax_id):
    #    key_rank = ["group", "refseq_category", "assembly_level", "genome_rep"]
    #    for i in assembly_list:
    #        printer = tax_id+"\t"
    #        for j in key_rank:
    #            printer = printer + getattr(i, j) + ";"
    #        print printer
    #
    # for each_taxon in sorted_class_taxon_rank_dict:
    #    print_assembly_list(sorted_class_taxon_rank_dict[each_taxon],each_taxon)

    log_print("\t\tEnd: cluster assembly record to taxonomic rank")

    return sorted_class_taxon_rank_dict


def store_sorted_class_taxon_rank_dict_into_sqlite(sorted_class_taxon_rank_dict, db_file, taxonomic_rank):
    column_name = ["taxon_group_id", "grouped", "Rank", "del_flag"] + col_name
    sc.init_sql_db(db_file, "ncbi_assembly", column_name)
    record_tmp_list = []
    num = 0
    for each_taxon in sorted_class_taxon_rank_dict:
        assembly_list = sorted_class_taxon_rank_dict[each_taxon]
        rank_num = 0
        for record in assembly_list:
            record_tmp = []
            num = num + 1
            # print(num)
            rank_num = rank_num + 1
            # taxon_group_id
            record_tmp.append(each_taxon)
            # grouped
            if not getattr(record, taxonomic_rank) == "None":
                record_tmp.append("Yes")
            else:
                record_tmp.append("No")
            # Rank
            record_tmp.append(rank_num)
            # del_flag
            record_tmp.append(record.del_flag)
            # other
            for i in col_name:
                record_tmp.append(getattr(record, i).replace("\"", ""))
            record_tmp_list.append(tuple(record_tmp))

            if len(record_tmp_list) % 10000 == 0:
                sc.sqlite_write(record_tmp_list, db_file,
                                "ncbi_assembly", column_name)
                record_tmp_list = []

    if len(record_tmp_list) > 0:
        sc.sqlite_write(record_tmp_list, db_file, "ncbi_assembly", column_name)
        record_tmp_list = []

    conn = sqlite3.connect(db_file)
    conn.execute(
        "CREATE UNIQUE INDEX assembly_accession_index on ncbi_assembly (assembly_accession)")
    conn.close()


def read_choosed_GenomeRecord_from_sqlite(db_file, taxonomic_rank):
    column_name = ["taxon_group_id", "grouped", "Rank", "del_flag"] + col_name

    conn = sqlite3.connect(db_file)
    table_name = "ncbi_assembly"
    record_list = conn.execute(
        "select * from ncbi_assembly WHERE Rank = 1 AND del_flag = \"Good Record\"").fetchall()
    conn.close()

    record_dict = {}
    for record in record_list:
        record_tmp = GenomeRecord()
        if record[1] == "Yes":
            setattr(record_tmp, taxonomic_rank, record[0])
        else:
            setattr(record_tmp, taxonomic_rank, "None")

        record_tmp.del_flag = record[3]

        num = 0
        for i in record[4:]:
            setattr(record_tmp, col_name[num], i)
            num = num + 1

        record_dict[record[0]] = record_tmp

    return record_dict


def print_sorted_class_taxon_rank_dict_from_sqlite(db_file, txt_file):
    import csv

    column_name = ["taxon_group_id", "grouped", "Rank", "del_flag"] + col_name

    with open(txt_file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(column_name)

        conn = sqlite3.connect(db_file)
        table_name = "ncbi_assembly"
        record_list = conn.execute("select * from ncbi_assembly").fetchall()
        conn.close()

        for record in record_list:
            spamwriter.writerow(record)


def ascp_download(online_path, down_path, printer=False):
    from toolbiox.config import ascp_path
    cmd_string = ascp_path + " -v -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh -k 1 -T -l 200m anonftp@ftp-private.ncbi.nlm.nih.gov:%s %s" % (
        online_path, down_path)

    if printer is True:
        return cmd_string

    flag, output, error = lib.common.os.cmd_run(cmd_string)
    # print(flag, output, error)
    if re.match(".*Completed.*", str(output)):
        return True
    else:
        return False


def wget_download(online_path, down_path, printer=False):
    from toolbiox.config import wget_path
    # cmd_string = wget_path + " -t 0 -O %s ftp://ftp.ncbi.nlm.nih.gov%s" % (
    #     down_path, online_path)
    cmd_string = wget_path + " -t 0 -O %s %s" % (
        down_path, online_path)

    print(cmd_string)

    if printer is True:
        return cmd_string

    flag, output, error = lib.common.os.cmd_run(cmd_string, silence=True)

    return True


def md5checksums_checker(para_dict_tmp, ncbi_record_md5_renew_flag, download_way='ascp'):
    import os

    if download_way == 'ascp':
        download_function = ascp_download
    elif download_way == 'wget':
        download_function = wget_download

    # search exist file
    if not os.path.exists(para_dict_tmp["data_dir_tmp"]):
        lib.common.os.cmd_run(
            "mkdir " + para_dict_tmp["data_dir_tmp"], silence=True)

    # print(record_tmp.assembly_accession)
    md5_file_url, md5_file_path = para_dict_tmp["files"]["md5_file"]
    if ncbi_record_md5_renew_flag is False:
        if os.path.exists(md5_file_path) and os.path.getsize(md5_file_path) != 0:
            return os.path.getsize(md5_file_path)
        else:
            if download_function(md5_file_url, md5_file_path):
                return os.path.getsize(md5_file_path)
            else:
                raise EnvironmentError("Check network!")

    if ncbi_record_md5_renew_flag is True:
        if os.path.exists(md5_file_path):
            lib.common.os.cmd_run("rm " + md5_file_path, silence=True)
        if download_function(md5_file_url, md5_file_path):
            return os.path.getsize(md5_file_path)
        else:
            raise EnvironmentError("Check network!")

    raise EnvironmentError("Unknown error!")


def genome_download(record_tmp, root_dir, want_download):
    """
    want_download = ["gff_file", "pt_file", "cds_file", "genome_file"]
    :param record_tmp:
    :param root_dir:
    :param want_download:
    :return:
    """
    from toolbiox.lib.common.os import md5sum_check
    from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
    data_dir = root_dir + "/data/NCBI"

    # parameter access
    ftp_path = record_tmp.ftp_path
    ftp_dir_path = ftp_path.replace("ftp://ftp.ncbi.nlm.nih.gov", "")
    data_dir_tmp = data_dir + "/" + \
        re.search("(^\S+\_\d+)\.\d+", record_tmp.assembly_accession).group(1)
    para_dict = {
        "speci_accession": re.search("(^\S+\_\d+)\.\d+", record_tmp.assembly_accession).group(1),
        "assembly_accession": record_tmp.assembly_accession,
        "full_accession": ftp_path.split("/")[-1],
        "gff_file": (ftp_dir_path + "/" + ftp_path.split("/")[-1] + "_genomic.gff.gz",
                     data_dir_tmp + "/" + ftp_path.split("/")[-1] + "_genomic.gff.gz"),
        "pt_file": (ftp_dir_path + "/" + ftp_path.split("/")[-1] + "_translated_cds.faa.gz",
                    data_dir_tmp + "/" + ftp_path.split("/")[-1] + "_translated_cds.faa.gz"),
        "cds_file": (ftp_dir_path + "/" + ftp_path.split("/")[-1] + "_cds_from_genomic.fna.gz",
                     data_dir_tmp + "/" + ftp_path.split("/")[-1] + "_cds_from_genomic.fna.gz"),
        "genome_file": (ftp_dir_path + "/" + ftp_path.split("/")[-1] + "_genomic.fna.gz",
                        data_dir_tmp + "/" + ftp_path.split("/")[-1] + "_genomic.fna.gz"),
        "md5_file": (ftp_dir_path + "/" + "md5checksums.txt", data_dir_tmp + "/" + "md5checksums.txt")
    }

    # # add md5 info
    md5_list = tsv_file_parse(para_dict["md5_file"][1], seq=r' ')
    for i in want_download:
        for j in md5_list:
            md5_string, nothing, file_name = md5_list[j]
            if para_dict[i][0].split("/")[-1] == file_name.split("/")[-1]:
                para_dict[i] = (para_dict[i][0], para_dict[i][1], md5_string)

    # # find uncompleted file
    log_dict = {}
    for i in want_download:
        if len(para_dict[i]) == 3:
            online_path, file_path, md5_string = para_dict[i]
            if not md5sum_check(file_path, md5_string):
                log_dict[i] = "renew"
            else:
                log_dict[i] = "ok"
        else:
            log_dict[i] = "miss"

    # # download
    for i in log_dict:
        if log_dict[i] == "renew":
            online_path, file_path, md5_string = para_dict[i]
            if ascp_download(online_path, file_path) and md5sum_check(file_path, md5_string):
                print("Renew %s" % i)
                log_dict[i] = "ok"

    related_path = "/data/NCBI"
    for i in log_dict:
        if log_dict[i] == "ok":
            online_path, file_path, md5_string = para_dict[i]
            log_dict[i] = related_path + "/" + \
                para_dict["speci_accession"] + "/" + file_path.split("/")[-1]

    return log_dict


if __name__ == '__main__':
    """
    The script hopes to get the genomes which can represent all sequenced species for HGT study by analyzing
    assembly_summary file ("assembly_summary_genbank.txt" and "assembly_summary_refseq.txt") and genome size file from NCBI.
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/species_genome_size.txt.gz (need decompressed)
    """
    from toolbiox.lib.xuyuxing.evolution.taxonomy import build_taxon_database, store_tax_record_into_sqlite

    work_dir = '/lustre/home/xuyuxing/Database/NCBI/genome'

    # input file
    assembly_summary_genbank_file = work_dir + '/assembly_summary_genbank.txt'
    assembly_summary_refseq_file = work_dir + '/assembly_summary_refseq.txt'

    # taxonomy
    path_for_taxonomy = "/lustre/home/xuyuxing/Database/NCBI/taxonomy"
    tax_db_file = path_for_taxonomy + "/tax_xyx.db"
    # tax_record_dict = build_taxon_database(path_for_taxonomy)
    # store_tax_record_into_sqlite(tax_record_dict, tax_db_file)

    # output file
    ncbi_choosed_record_txt_file = work_dir + "/assembly_choosed.csv"

    # parse ncbi
    record_dict = build_ncbi_genome_database(
        assembly_summary_genbank_file, assembly_summary_refseq_file)
    ncbi_genus_record = genome_chooser(
        record_dict, tax_db_file, taxonomic_rank='genus')
