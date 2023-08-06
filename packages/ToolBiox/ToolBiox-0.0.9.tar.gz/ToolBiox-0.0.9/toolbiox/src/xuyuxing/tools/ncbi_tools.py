import os
from collections import OrderedDict
from toolbiox.api.xuyuxing.resource.ncbi_genome import build_ncbi_genome_database, md5checksums_checker, ascp_download, wget_download, genome_chooser
from toolbiox.lib.common.fileIO import read_list_file
import re
from toolbiox.lib.xuyuxing.evolution.taxonomy import build_taxon_database, read_tax_record_dict_db, store_tax_record_into_sqlite
from toolbiox.lib.xuyuxing.base.common_command import log_print
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_dict_parse, tsv_file_parse
from toolbiox.lib.common.os import md5sum_check
import time
from toolbiox.config import taxon_dump
import sys
from ftplib import FTP
from retry import retry


def ncbi_genome_downloader(args):

    if args.download_way == 'ascp':
        download_function = ascp_download
    elif args.download_way == 'wget':
        download_function = wget_download

    if args.assembly_summary_refseq_file is None:
        args.assembly_summary_refseq_file = args.ncbi_genome_dir + \
            "/assembly_summary_refseq.txt"
        args.assembly_summary_genbank_file = args.ncbi_genome_dir + \
            "/assembly_summary_genbank.txt"

    # download list
    log_print("Read download accession list")
    acc_list = read_list_file(args.list_of_accession_ID)

    if args.download_type:
        download_type = args.download_type.split(",")
    else:
        download_type = ["gff_file", "pt_file", "cds_file", "genome_file"]

    log_print("There are %d accesion will be download, will download their: %s" % (
        len(acc_list), ", ".join(download_type)))

    # parse metadata
    log_print("Read metadata from NCBI")
    record_dict = build_ncbi_genome_database(
        args.assembly_summary_genbank_file, args.assembly_summary_refseq_file)
    record_dict = {i: record_dict[i] for i in acc_list}

    # prepare
    log_print("Prepare download information")
    data_dir = args.ncbi_genome_dir
    for acc_id in record_dict:
        record_tmp = record_dict[acc_id]
        ftp_path = record_tmp.ftp_path
        ftp_dir_path = ftp_path.replace("ftp://ftp.ncbi.nlm.nih.gov", "")
        data_dir_tmp = data_dir + "/" + record_tmp.assembly_accession
        file_path = {
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
        para_dict_tmp = {
            "speci_accession": re.search("(^\S+\_\d+)\.\d+", record_tmp.assembly_accession).group(1),
            "assembly_accession": record_tmp.assembly_accession,
            "full_accession": ftp_path.split("/")[-1],
            "files": file_path,
            "ftp_dir_path": ftp_dir_path,
            "data_dir_tmp": data_dir_tmp
        }
        record_tmp.para_dict = para_dict_tmp

    # md5file
    log_print("Check NCBI md5checksums")

    if args.renew_md5_flag is True:
        log_print("\t\tRenew all md5checksums")
    else:
        log_print("\t\tCheck missing md5checksums")

    for acc_id in record_dict:
        record_tmp = record_dict[acc_id]
        md5checksums_checker(record_tmp.para_dict,
                             args.renew_md5_flag, download_way=args.download_way)

    log_print("Add md5 string to file")

    for acc_id in record_dict:
        para_dict_tmp = record_dict[acc_id].para_dict
        md5_file = para_dict_tmp["files"]["md5_file"][1]
        md5_list = tsv_file_parse(md5_file, seq=r' ')
        for i in para_dict_tmp["files"]:
            for j in md5_list:
                md5_string, nothing, file_name = md5_list[j]
                if para_dict_tmp["files"][i][0].split("/")[-1] == file_name.split("/")[-1]:
                    record_dict[acc_id].para_dict["files"][i] = tuple(
                        list(record_dict[acc_id].para_dict["files"][i]) + [md5_string])

    # check if downloaded
    log_print("Check the completed download file")
    start_time = time.time()
    num = 0
    ok_file_num = 0
    renew_file_num = 0
    miss_file_num = 0
    for acc_id in record_dict:
        num = num + 1
        para_dict_tmp = record_dict[acc_id].para_dict
        for file_type in para_dict_tmp["files"]:
            if len(para_dict_tmp["files"][file_type]) == 3:
                online_path, file_path, md5_string = para_dict_tmp["files"][file_type]
                if md5sum_check(file_path, md5_string):
                    log_tmp = "ok"
                    if file_type in download_type:
                        ok_file_num += 1
                else:
                    log_tmp = "renew"
                    if file_type in download_type:
                        renew_file_num += 1
                record_dict[acc_id].para_dict["files"][file_type] = tuple(
                    list(record_dict[acc_id].para_dict["files"][file_type]) + [log_tmp])
            else:
                log_tmp = "miss"
                if file_type in download_type:
                    miss_file_num += 1
                record_dict[acc_id].para_dict["files"][file_type] = tuple(
                    list(record_dict[acc_id].para_dict["files"][file_type]) + ["", log_tmp])
        round_time = time.time()
        if round_time - start_time > 10:
            log_print("\t\t%d/%d" % (num, len(record_dict)))
            start_time = round_time

    log_print("Total: %d, %d is downloaded, %d need download now, %d are missed in NCBI" % (
        ok_file_num+renew_file_num+miss_file_num, ok_file_num, renew_file_num, miss_file_num))

    # Download uncompleted file
    log_print("Download uncompleted file")

    for acc_id in record_dict:
        for i in record_dict[acc_id].para_dict["files"]:
            if i in download_type:
                url_path, file_path, md5_string, log_tmp = record_dict[acc_id].para_dict["files"][i]
                if log_tmp == "renew":
                    if download_function(url_path, file_path):
                        record_dict[acc_id].para_dict["files"][i] = list(
                            record_dict[acc_id].para_dict["files"][i][:3]) + ["ok"]
                    else:
                        raise EnvironmentError("Check network!")

    # make report
    col_name_list = ["assembly_accession", "species_taxid", "kingdom", "order", "family", "genus", "organism_name", "refseq_category", "group", "gff_file", "gff_file_md5",
                     "gff_file_status", "pt_file", "pt_file_md5", "pt_file_status", "cds_file", "cds_file_md5", "cds_file_status", "genome_file", "genome_file_md5", "genome_file_status", "ftp_path"]

    report_file = args.ncbi_genome_dir + "/downloaded_genome.txt"

    output_dict = OrderedDict()
    if os.path.exists(report_file):
        info_dict = tsv_file_dict_parse(report_file, key_col="assembly_accession")
        for i in info_dict:
            output_dict[i] = [info_dict[i][j] for j in col_name_list]

    if args.taxonomy_dir:
        tax_record_dict = build_taxon_database(args.taxonomy_dir)
    else:
        tax_record_dict = read_tax_record_dict_db(taxon_dump+"/taxdump_xyx.db")

    for acc_id in record_dict:
        record_tmp = record_dict[acc_id]

        taxon_info_list = [record_tmp.species_taxid, "None",
                           "None", "None", "None", record_tmp.organism_name]
        if record_tmp.species_taxid in tax_record_dict:
            taxon_tmp = tax_record_dict[record_tmp.species_taxid]
            kingdom = tax_record_dict[taxon_tmp.kingdom].sci_name if hasattr(
                taxon_tmp, 'kingdom') else "None"
            order = tax_record_dict[taxon_tmp.order].sci_name if hasattr(
                taxon_tmp, 'order') else "None"
            family = tax_record_dict[taxon_tmp.family].sci_name if hasattr(
                taxon_tmp, 'family') else "None"
            genus = tax_record_dict[taxon_tmp.genus].sci_name if hasattr(
                taxon_tmp, 'genus') else "None"
            taxon_info_list = [record_tmp.species_taxid, kingdom,
                               order, family, genus, record_tmp.organism_name]

        file_info_list = []
        for file_type in ["gff_file", "pt_file", "cds_file", "genome_file"]:
            url_str, file_path, md5_string, status = record_tmp.para_dict['files'][file_type]
            file_info_list.extend([file_path, md5_string, status])

        output_dict[acc_id] = [record_tmp.assembly_accession] + \
            taxon_info_list + file_info_list + [record_tmp.ftp_path]

    with open(args.ncbi_genome_dir + "/downloaded_genome.txt", 'w') as f:
        f.write("\t".join(col_name_list)+"\n")
        for acc_id in output_dict:
            info_list = []
            for i in output_dict[acc_id]:
                if i is None:
                    info_list.append('None')
                else:
                    str(i)
            f.write("\t".join(info_list)+"\n")

    renew_num = 0
    for acc_id in record_dict:
        for i in record_dict[acc_id].para_dict["files"]:
            if i in download_type:
                url_path, file_path, md5_string, log_tmp = record_dict[acc_id].para_dict["files"][i]
                if log_tmp == "renew":
                    renew_num = renew_num + 1

    if not renew_num == 0:
        raise ValueError(
            "Not all NCBI data have been download! Please check! ")


@retry(tries=5)
def if_assembly_annotated(genome_record):
    ftp_path = genome_record.ftp_path
    ftp_dir_path = ftp_path.replace("ftp://ftp.ncbi.nlm.nih.gov", "")
    pt_file_url = ftp_dir_path + "/" + \
        ftp_path.split("/")[-1] + "_translated_cds.faa.gz"

    annotated_flag = True
    try:
        ftp = FTP('ftp.ncbi.nlm.nih.gov')
        ftp.login()
        ftp.dir(pt_file_url)
    except:
        error_mess = sys.exc_info()[1].args[0]

        if 'timeout' in error_mess:
            raise EnvironmentError("Check your network")
        elif 'No such file or directory' in error_mess:
            annotated_flag = False

    return annotated_flag


def ncbi_genome_chooser(args):

    log_print("Read metadata")

    if args.assembly_summary_refseq_file is None:
        args.assembly_summary_refseq_file = args.ncbi_genome_dir + \
            "/assembly_summary_refseq.txt"
        args.assembly_summary_genbank_file = args.ncbi_genome_dir + \
            "/assembly_summary_genbank.txt"

    record_dict = build_ncbi_genome_database(
        args.assembly_summary_genbank_file, args.assembly_summary_refseq_file)

    if args.taxonomy_dir:
        tax_db_file = args.taxonomy_dir+"/taxdump_xyx.db"
        if not os.path.exists(tax_db_file):
            tax_record_dict = build_taxon_database(args.taxonomy_dir)
            store_tax_record_into_sqlite(tax_record_dict, tax_db_file)
    else:
        tax_db_file = taxon_dump+"/taxdump_xyx.db"

    log_print("%d record in metadata" % len(record_dict))

    log_print("Choose by metadata")
    ncbi_rank_record = genome_chooser(record_dict, tax_db_file, taxonomic_rank=args.taxonomic_rank,
                                      keep_no_rank=(not args.remove_no_rank), top_taxon=args.top_taxon)
    log_print("%d used in from choose in metadata" % len(ncbi_rank_record))

    for tax_id in ncbi_rank_record:
        good_record = []
        for record_tmp in ncbi_rank_record[tax_id]:
            if record_tmp.del_flag == 'Good Record':
                good_record.append(record_tmp)
        ncbi_rank_record[tax_id] = good_record

    log_print("Choose by annotation")
    if not args.allow_no_annotation:
        for tax_id in ncbi_rank_record:
            for record_tmp in ncbi_rank_record[tax_id]:
                ftp_path = record_tmp.ftp_path
                ftp_dir_path = ftp_path.replace(
                    "ftp://ftp.ncbi.nlm.nih.gov", "")
                data_dir_tmp = args.ncbi_genome_dir + "/" + record_tmp.assembly_accession
                file_path = {
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
                para_dict_tmp = {
                    "speci_accession": re.search("(^\S+\_\d+)\.\d+", record_tmp.assembly_accession).group(1),
                    "assembly_accession": record_tmp.assembly_accession,
                    "full_accession": ftp_path.split("/")[-1],
                    "files": file_path,
                    "ftp_dir_path": ftp_dir_path,
                    "data_dir_tmp": data_dir_tmp
                }
                record_tmp.para_dict = para_dict_tmp

                md5_file_path = file_path["md5_file"][1]

                if os.path.exists(md5_file_path) and os.path.getsize(md5_file_path) != 0:
                    if len(record_tmp.para_dict["files"]['pt_file']) > 2:
                        record_tmp.annotated = True
                    else:
                        record_tmp.annotated = False
                else:
                    if if_assembly_annotated(record_tmp):
                        record_tmp.annotated = True

                        md5checksums_checker(record_tmp.para_dict,
                                             args.renew_md5_flag, download_way=args.download_way)

                        para_dict_tmp = record_tmp.para_dict
                        md5_file = para_dict_tmp["files"]["md5_file"][1]
                        md5_list = tsv_file_parse(md5_file, seq=r' ')
                        for i in para_dict_tmp["files"]:
                            for j in md5_list:
                                md5_string, nothing, file_name = md5_list[j]
                                if para_dict_tmp["files"][i][0].split("/")[-1] == file_name.split("/")[-1]:
                                    record_tmp.para_dict["files"][i] = tuple(
                                        list(record_tmp.para_dict["files"][i]) + [md5_string])
                    else:
                        record_tmp.annotated = False

    log_print("Make report")

    # make report
    col_name_list = ["assembly_accession", "species_taxid", "kingdom", "order",
                     "family", "genus", "organism_name", "refseq_category", "group", "ftp_path"]

    report_file = "chosen.genome.txt"

    tax_record_dict = read_tax_record_dict_db(tax_db_file)

    with open(report_file, 'w') as f:
        f.write("\t".join(col_name_list) + "\n")

        for tax_id in ncbi_rank_record:
            choose_record = []
            for record_tmp in ncbi_rank_record[tax_id]:
                if record_tmp.del_flag == 'Good Record':
                    if len(choose_record) < args.top_num:
                        if args.allow_no_annotation is True:
                            choose_record.append(record_tmp)
                        elif args.allow_no_annotation is False:
                            if record_tmp.annotated:
                                choose_record.append(record_tmp)
                        
            for record_tmp in choose_record:

                if record_tmp.species_taxid in tax_record_dict:

                    taxon_tmp = tax_record_dict[record_tmp.species_taxid]
                    kingdom = tax_record_dict[taxon_tmp.kingdom].sci_name if hasattr(
                        taxon_tmp, 'kingdom') else "None"
                    order = tax_record_dict[taxon_tmp.order].sci_name if hasattr(
                        taxon_tmp, 'order') else "None"
                    family = tax_record_dict[taxon_tmp.family].sci_name if hasattr(
                        taxon_tmp, 'family') else "None"
                    genus = tax_record_dict[taxon_tmp.genus].sci_name if hasattr(
                        taxon_tmp, 'genus') else "None"

                f.write("\t".join([record_tmp.assembly_accession, record_tmp.species_taxid, kingdom, order, family, genus,
                                   record_tmp.organism_name, record_tmp.refseq_category, record_tmp.group, record_tmp.ftp_path]) + "\n")


if __name__ == "__main__":

    # Download some genome from NCBI

    class abc():
        pass

    args = abc()

    args.ncbi_genome_dir = "/lustre/home/xuyuxing/Database/NCBI/genome"
    args.list_of_accession_ID = "/lustre/home/xuyuxing/Database/NCBI/genome/download.list"
    args.taxonomy_dir = None
    args.assembly_summary_refseq_file = None
    args.assembly_summary_genbank_file = None
    args.download_type = "pt_file,gff_file"
    args.renew_md5_flag = False
    args.download_way = "wget"

    ncbi_genome_downloader(args)

    # Download some genome from NCBI

    class abc():
        pass

    args = abc()

    args.ncbi_genome_dir = "/lustre/home/xuyuxing/Database/NCBI/genome"
    args.assembly_summary_refseq_file = None
    args.assembly_summary_genbank_file = None
    args.taxonomy_dir = None
    args.taxonomic_rank = 'family'
    args.top_taxon = 'Magnoliopsida'
    args.remove_no_rank = False
    args.allow_no_annotation = False
    args.renew_md5_flag = False
    args.download_way = 'wget'
    args.top_num = 2

    ncbi_genome_chooser(args)
