import toolbiox.lib.common.os
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_record_dict_db
import toolbiox.lib.xuyuxing.base.base_function as bf
import xml.etree.ElementTree as ET
import re
import os
import time
from ftplib import FTP


class GenomeRecord(object):
    """
    Genome_record is a class for each record in genome database.
    """

    def __init__(self, db_access_id, taxon_id, download_info=None, db_name=None, other_info=None):
        self.db_access_id = db_access_id
        self.taxon_id = taxon_id
        self.db_name = db_name
        self.other_info = other_info
        self.download_info = download_info


def jgi_Portal_ID_get(Portal_ID_raw):
    return re.findall("\"(.*)\"", Portal_ID_raw.split(",")[1])[0]


def jgi_Taxonomy_ID_get(genome_projects_record):
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


def jgi_pull_info(user_name, passwd, cookie_path, output_xml, Portal_ID, directly_download):
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


def jgi_pull_file(user_name, passwd, cookie_path, output_file, want_url, directly_download):
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


def jgi_files_download(ftp_list, output_list, user_name, passwd, cookie_path):
    for tmp_index in range(len(ftp_list)):
        ftp_url = ftp_list[tmp_index]
        output_file = output_list[tmp_index]

        jgi_pull_file(user_name, passwd, cookie_path, output_file, ftp_url, True)


def jgi_uniq_file_record(file_list):
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


def jgi_metadata_xml_read(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    file_info_dict = {}
    md5_info_dict = {}
    url_info_dict = {}
    for file_tmp in root.iter("file"):
        if "filename" in file_tmp.attrib:
            file_name = file_tmp.attrib["filename"]
        else:
            continue

        if "url" in file_tmp.attrib:
            match_url = re.match(r'.*&url=(.*)', file_tmp.attrib["url"])
            if match_url:
                file_url = "https://genome.jgi.doe.gov/portal" + match_url.group(1)
            else:
                file_url = "https://genome.jgi.doe.gov" + file_tmp.attrib["url"]
            url_info_dict[file_name] = file_url
        else:
            continue

        if "md5" in file_tmp.attrib:
            file_md5 = file_tmp.attrib["md5"]
            md5_info_dict[file_name] = file_md5
        else:
            file_md5 = ""

        if "sizeInBytes" in file_tmp.attrib:
            file_size = file_tmp.attrib["sizeInBytes"]
        else:
            file_size = ""

        file_type = ""
        match_gff = re.match(r"^(\S+)_GeneCatalog_genes_(\d+)\.gff.gz", file_name)
        if match_gff:
            tag_tmp = match_gff.groups(1)[0]
            version_tmp = match_gff.groups(1)[1]
            file_type = "gff_file"
        match_cds = re.match(r"^(\S+)_GeneCatalog_CDS_(\d+)\.fasta.gz", file_name)
        if match_cds:
            tag_tmp = match_cds.groups(1)[0]
            version_tmp = match_cds.groups(1)[1]
            file_type = "cds_file"
        match_pt = re.match(r"^(\S+)_GeneCatalog_proteins_(\d+)\.aa.fasta.gz", file_name)
        if match_pt:
            tag_tmp = match_pt.groups(1)[0]
            version_tmp = match_pt.groups(1)[1]
            file_type = "pt_file"
        match_genome = re.match(r"^(\S+)_AssemblyScaffolds.fasta.gz", file_name)
        if match_genome:
            tag_tmp = match_genome.groups(1)[0]
            file_type = "genome_file"

        if file_type == "":
            continue

        if tag_tmp not in file_info_dict:
            file_info_dict[tag_tmp] = {}
            file_info_dict[tag_tmp]["genome_file"] = None
            file_info_dict[tag_tmp]["annotation"] = {}
        if file_type == "genome_file":
            file_info_dict[tag_tmp]["genome_file"] = (
                file_url, file_name, file_md5, tag_tmp, "", "genome_file", file_size)
        else:
            if version_tmp not in file_info_dict[tag_tmp]["annotation"]:
                file_info_dict[tag_tmp]["annotation"][version_tmp] = []
            file_info_dict[tag_tmp]["annotation"][version_tmp].append(
                (file_url, file_name, file_md5, tag_tmp, "", file_type, file_size))
            file_info_dict[tag_tmp]["annotation"][version_tmp] = jgi_uniq_file_record(
                file_info_dict[tag_tmp]["annotation"][version_tmp])

    # choose newest version

    for tag_tmp in file_info_dict:
        file_info = {
            "genome_file": None,
            "gff_file": None,
            "cds_file": None,
            "pt_file": None
        }

        genome_file_info = file_info_dict[tag_tmp]["genome_file"]
        if not genome_file_info is None:

            g_file_name = genome_file_info[1]

            if g_file_name in md5_info_dict:
                g_file_md5 = md5_info_dict[g_file_name]
            else:
                g_file_md5 = None

            if g_file_name in url_info_dict:
                g_file_url = url_info_dict[g_file_name]
            else:
                g_file_url = None

            file_info["genome_file"] = (g_file_name, g_file_url, g_file_md5)

        version_keys = list(file_info_dict[tag_tmp]['annotation'].keys())

        if len(version_keys) != 0:

            version_keys = [int(i) for i in version_keys]
            newest_version = str(sorted(version_keys, reverse=True)[0])

            for i in file_info_dict[tag_tmp]["annotation"][newest_version]:
                file_name = i[1]

                if file_name in md5_info_dict:
                    file_md5 = md5_info_dict[file_name]
                else:
                    file_md5 = None

                if file_name in url_info_dict:
                    file_url = url_info_dict[file_name]
                else:
                    file_url = None

                file_info[i[5]] = (file_name, file_url, file_md5)

        file_info_dict[tag_tmp] = file_info

    return file_info_dict


def get_ncbi_md5_list(ftp_dir, tmp_file="/tmp/tmp_md5.txt"):
    """
    ftp_dir = '/genomes/all/GCA/000/001/215/GCA_000001215.4_Release_6_plus_ISO1_MT'
    """

    ftp_dir = re.sub(r'ftp://ftp.ncbi.nlm.nih.gov', '', ftp_dir)

    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect("ftp.ncbi.nlm.nih.gov")
    ftp.login()

    try:
        fp = open(tmp_file, 'wb')
        bufsize = 1024
        ftp.retrbinary('RETR ' + ftp_dir + "/md5checksums.txt", fp.write, bufsize)
        fp.close()

        md5_info_dict = {}
        with open(tmp_file, 'r') as f:
            for each_line in f:
                each_line = each_line.strip()
                info = each_line.split()
                file_name = re.sub(r'^\./', '', info[1])
                md5_string = info[0]
                md5_info_dict[file_name] = md5_string

        os.remove(tmp_file)

        return md5_info_dict
    except:
        return "error"


def get_many_ncbi_md5_list(ftp_dir_list, md5sum_huge_file, tmp_dir="/tmp/tmp_md5"):
    import time
    from toolbiox.lib.xuyuxing.base.common_command import log_print

    lib.common.os.mkdir(tmp_dir)
    #
    # with open(tmp_dir + "/ftp_md5_file.txt", 'w') as f:
    #     num = 0
    #     for i in ftp_dir_list:
    #         num = num + 1
    #         rename_md5 = tmp_dir + "/md5_%d.txt" % (num)
    #         f.write("wget -O %s %s/md5checksums.txt\n" % (rename_md5, i))

    log_print("\t\tBegin: download md5sum file for %d ncbi genome record" % len(ftp_dir_list))
    start_time = time.time()

    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect("ftp.ncbi.nlm.nih.gov")
    ftp.login()

    num = 0
    rename_md5_list = []
    for ftp_dir in ftp_dir_list:

        round_time = time.time()
        if round_time - start_time > 10:
            log_print("\t\t\t%d/%d" % (num, len(ftp_dir_list)))
            start_time = round_time

        ftp_dir = re.sub(r'ftp://ftp.ncbi.nlm.nih.gov', '', ftp_dir)
        num += 1
        rename_md5 = tmp_dir + "/md5_%d.txt" % (num)
        failed_flag = True
        retry = 0
        while failed_flag and retry < 5:
            try:
                fp = open(rename_md5, 'wb')
                bufsize = 1024
                ftp.retrbinary('RETR ' + ftp_dir + "/md5checksums.txt", fp.write, bufsize)
                fp.close()
                if os.path.exists(rename_md5) and os.path.getsize(rename_md5) != 0:
                    rename_md5_list.append(rename_md5)
                    failed_flag = False
            except:
                ftp = FTP()
                # ftp.set_debuglevel(2)
                ftp.connect("ftp.ncbi.nlm.nih.gov")
                ftp.login()
                failed_flag = True
            retry += 1

    ftp.close()

    log_print("\t\tEnd: download all md5sum file for %d ncbi genome record" % len(ftp_dir_list))

    with open(md5sum_huge_file, 'w') as fo:
        for file_tmp in rename_md5_list:
            with open(file_tmp, 'r') as fi:
                for each_line in fi:
                    fo.write(each_line)

    return md5sum_huge_file


def ncbi_files_download(ftp_list, output_list):
    import time
    from toolbiox.lib.xuyuxing.base.common_command import log_print

    log_print("\t\tBegin: download %d files from ncbi database" % len(ftp_list))
    start_time = time.time()

    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect("ftp.ncbi.nlm.nih.gov")
    ftp.login()

    num = 0
    rename_md5_list = []
    for tmp_index in range(len(ftp_list)):
        ftp_url = ftp_list[tmp_index]
        output_file = output_list[tmp_index]

        round_time = time.time()
        num += 1
        if round_time - start_time > 10:
            log_print("\t\t\t%d/%d" % (num, len(ftp_list)))
            start_time = round_time

        ftp_url = re.sub(r'ftp://ftp.ncbi.nlm.nih.gov', '', ftp_url)

        failed_flag = True
        retry = 0
        while failed_flag and retry < 5:
            try:
                fp = open(output_file, 'wb')
                bufsize = 1024
                ftp.retrbinary('RETR ' + ftp_url, fp.write, bufsize)
                fp.close()
                if os.path.exists(output_file) and os.path.getsize(output_file) != 0:
                    rename_md5_list.append(output_file)
                    failed_flag = False
            except:
                ftp = FTP()
                # ftp.set_debuglevel(2)
                ftp.connect("ftp.ncbi.nlm.nih.gov")
                ftp.login()
                failed_flag = True
            retry += 1

    ftp.close()

    log_print("\t\tEnd: download all md5sum file for %d ncbi genome record" % len(ftp_list))


def genome_record_exclude_by_taxon(record_dict, tax_sqldb_file, taxon_filter):
    # exclude taxon by filter
    used_taxon_id_list = list(set([record_dict[i].taxon_id for i in record_dict]))
    tax_record_db = read_tax_record_dict_db(tax_sqldb_file, tuple(used_taxon_id_list))

    rec_id_list = list(record_dict.keys())
    for i in rec_id_list:
        if record_dict[i].taxon_id not in tax_record_db:
            del record_dict[i]
        else:
            lineage_id_list = [i[0] for i in tax_record_db[record_dict[i].taxon_id].get_lineage]
            if len(set(lineage_id_list) & set(taxon_filter)) == 0:
                del record_dict[i]

    return record_dict


def build_data_index(input_info_list, database_name, tax_sqldb_file, taxon_filter):
    """
    most database will give a index file to tell me, how many genome they have
    """

    if database_name == 'ncbi':
        """
        "assembly_summary_refseq_file" and "assembly_summary_genbank_file" as input
        """

        assembly_summary_refseq_file, assembly_summary_genbank_file, md5sum_huge_file = input_info_list

        col_name = ["assembly_accession", "bioproject", "biosample", "wgs_master", "refseq_category", "taxid",
                    "species_taxid", "organism_name", "infraspecific_name", "isolate", "version_status",
                    "assembly_level", "release_type", "genome_rep", "seq_rel_date", "asm_name", "submitter",
                    "gbrs_paired_asm", "paired_asm_comp", "ftp_path", "excluded_from_refseq",
                    "relation_to_type_material"]

        record_dict = {}

        parse_file_db = tsv_file_dict_parse(assembly_summary_refseq_file, fieldnames=col_name)
        for i in parse_file_db:
            parse_file_db[i]['group'] = "refseq"
            gr_tmp = GenomeRecord(parse_file_db[i]['assembly_accession'], parse_file_db[i]["species_taxid"],
                                  None, "ncbi", parse_file_db[i])
            record_dict[parse_file_db[i]['assembly_accession']] = gr_tmp

        parse_file_db = tsv_file_dict_parse(assembly_summary_genbank_file, fieldnames=col_name)
        for i in parse_file_db:
            if parse_file_db[i]['paired_asm_comp'] == "na" and parse_file_db[i]['excluded_from_refseq'] == "" and \
                    parse_file_db[i]['ftp_path'] != "na":
                parse_file_db[i]['group'] = "genbank"
                gr_tmp = GenomeRecord(parse_file_db[i]['assembly_accession'], parse_file_db[i]["species_taxid"],
                                      None, "ncbi", parse_file_db[i])
                record_dict[parse_file_db[i]['assembly_accession']] = gr_tmp

        # exclude taxon by filter
        record_dict = genome_record_exclude_by_taxon(record_dict, tax_sqldb_file, taxon_filter)

        # add download info
        if not os.path.exists(md5sum_huge_file):
            ftp_dir_list = [record_dict[i].other_info['ftp_path'] for i in record_dict]
            # ftp_dir_list = ftp_dir_list[0:100]
            get_many_ncbi_md5_list(ftp_dir_list, md5sum_huge_file, tmp_dir="/tmp/tmp_md5")

        md5_info_dict = {}
        with open(md5sum_huge_file, 'r') as f:
            for each_line in f:
                each_line = each_line.strip()
                info = each_line.split()
                file_name = re.sub(r'^\./', '', info[1])
                md5_string = info[0]
                md5_info_dict[file_name] = md5_string

        good_num = 0
        bad_num = 0
        for rec_id in record_dict:
            long_acc = record_dict[rec_id].other_info['ftp_path'].split('/')[-1]

            ftp_path = record_dict[rec_id].other_info['ftp_path']

            file_info = {
                "genome_file": long_acc + "_genomic.fna.gz",
                "gff_file": long_acc + "_genomic.gff.gz",
                "cds_file": long_acc + "_cds_from_genomic.fna.gz",
                "pt_file": long_acc + "_translated_cds.faa.gz"
            }

            for i in file_info:
                if file_info[i] in md5_info_dict:
                    file_tuple = (file_info[i], ftp_path + "/" + file_info[i], md5_info_dict[file_info[i]])
                    file_info[i] = file_tuple
                    good_num += 1
                else:
                    file_info[i] = None
                    bad_num += 1

            record_dict[rec_id].download_info = file_info

        return record_dict

    elif database_name == 'jgi':
        """
        "genome-projects.csv" and xml file like "fungi.xml" as input
        """

        # read "fungi.xml" like file for record download info
        metadata_xml_path = input_info_list[1]
        file_info_dict = jgi_metadata_xml_read(metadata_xml_path)

        # read "genome-projects.csv" for record speci info

        col_name = ["Project Name", "Principal Investigator", "Scientific Program", "Product Name", "Status",
                    "Status Date", "User Program", "Proposal", "JGI Project Id", "Taxonomy ID", "NCBI Project Id",
                    "Genbank", "ENA", "SRA", "Sequencing Project ID", "Analysis project ID", "Project Manager",
                    "Portal ID", "IMG Portal", "Mycocosm Portal", "Phytozome Portal"]

        genome_projects_csv_file = input_info_list[0]

        record_dict = {}

        parse_file_db = tsv_file_dict_parse(genome_projects_csv_file, fieldnames=col_name, seq=",", ignore_head_num=1)
        for i in parse_file_db:
            record_id = jgi_Portal_ID_get(parse_file_db[i]["Portal ID"])
            record_species_taxid = jgi_Taxonomy_ID_get(parse_file_db[i])

            if record_species_taxid == "":
                continue

            if record_id not in file_info_dict:
                continue

            gr_tmp = GenomeRecord(record_id, record_species_taxid, file_info_dict[record_id], 'jgi', parse_file_db[i])
            record_dict[record_id] = gr_tmp

        # exclude taxon by filter
        record_dict = genome_record_exclude_by_taxon(record_dict, tax_sqldb_file, taxon_filter)

        return record_dict


def class_genome_record_by_rank(record_dict, taxon_rank, tax_sqldb_file):
    used_taxon_id_list = list(set([record_dict[i].taxon_id for i in record_dict]))
    tax_record_db = read_tax_record_dict_db(tax_sqldb_file, tuple(used_taxon_id_list))

    record_in_rank = {}
    record_in_rank['other'] = []
    for gr_id in record_dict:
        gr_tmp = record_dict[gr_id]
        gr_taxon = tax_record_db[gr_tmp.taxon_id]
        if hasattr(gr_taxon, taxon_rank):
            taxonomic_rank_tmp = getattr(gr_taxon, taxon_rank)
            if taxonomic_rank_tmp not in record_in_rank:
                record_in_rank[taxonomic_rank_tmp] = []
            record_in_rank[taxonomic_rank_tmp].append(gr_tmp)
        else:
            record_in_rank['other'].append(gr_tmp)

    return record_in_rank


if __name__ == '__main__':
    from toolbiox.lib.common.os import mkdir
    from toolbiox.lib.xuyuxing.evolution.taxonomy import build_taxon_database, store_tax_record_into_sqlite

    # normal
    work_dir = "/lustre/home/xuyuxing/Work/Gel/HGT"
    mkdir(work_dir, True)

    path_for_taxonomy = "/lustre/home/xuyuxing/Work/Gel/HGT/taxdump"
    tax_db_file = "/lustre/home/xuyuxing/Work/Gel/HGT/taxdump/tax_xyx.db"

    tax_record_dict = build_taxon_database(path_for_taxonomy)
    store_tax_record_into_sqlite(tax_record_dict, tax_db_file)

    # build record index
    # ncbi
    """
    assembly_summary file ("assembly_summary_genbank.txt" and "assembly_summary_refseq.txt") and genome size file from NCBI.
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
    ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz (need decompressed)
    ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/species_genome_size.txt.gz (need decompressed)
    """

    assembly_summary_refseq_file = '/lustre/home/xuyuxing/Work/Gel/HGT/assembly_summary_refseq.txt'
    assembly_summary_genbank_file = '/lustre/home/xuyuxing/Work/Gel/HGT/assembly_summary_genbank.txt'
    md5sum_huge_file = '/lustre/home/xuyuxing/Work/Gel/HGT/md5sum_huge_file.txt'

    ncbi_fungi_record_dict = build_data_index(
        [assembly_summary_refseq_file, assembly_summary_genbank_file, md5sum_huge_file], 'ncbi', tax_db_file, ['4751'])

    # jgi
    jgi_user_name = "xuyuxing14@mails.ucas.ac.cn"
    jgi_passwd = "HGTrunning123"
    metadata_key_words = "fungal-program-all"
    genome_projects_csv_file = "/lustre/home/xuyuxing/Work/Gel/HGT/genome-projects.csv"

    jgi_dir = work_dir + "/jgi"
    mkdir(jgi_dir, True)
    cookie_path = work_dir + "/jgi/cookies"
    # metadata_xml_path = work_dir + "/jgi/fungi.xml"
    metadata_xml_path = "/lustre/home/xuyuxing/Work/Gel/HGT/jgi/fungal-program-all.xml"

    # get fungi.xml
    jgi_pull_info(jgi_user_name, jgi_passwd, cookie_path, metadata_xml_path, "fungal-program-all", True)

    # build index
    jgi_fungi_record_dict = build_data_index([genome_projects_csv_file, metadata_xml_path], 'jgi', tax_db_file,
                                             ['4751'])

    # merge ncbi and jgi database
    from toolbiox.lib.xuyuxing.base.common_command import merge_dict

    record_dict = merge_dict([ncbi_fungi_record_dict, jgi_fungi_record_dict], False)

    record_in_genus = class_genome_record_by_rank(record_dict, 'genus', tax_db_file)

    # download files
    Am_list = record_in_genus['47424']

    Am_jgi_data = {i.db_access_id: i.download_info['pt_file'] for i in Am_list if
                   i.db_name == 'jgi' and not i.download_info['pt_file'] is None}
    Am_ncbi_data = {i.db_access_id: i.download_info['pt_file'] for i in Am_list if
                    i.db_name == 'ncbi' and not i.download_info['pt_file'] is None}

    ## download ncbi data
    ncbi_data_dir = "/lustre/home/xuyuxing/Work/Gel/HGT/ncbi_am"
    for i in Am_ncbi_data:
        file_name, download_url, md5sum = Am_ncbi_data[i]
        store_file = ncbi_data_dir + "/" + file_name
        Am_ncbi_data[i] = (file_name, download_url, md5sum, store_file)

    Am_ncbi_url_list = [Am_ncbi_data[i][1] for i in Am_ncbi_data]
    Am_ncbi_file_list = [Am_ncbi_data[i][3] for i in Am_ncbi_data]

    ncbi_files_download(Am_ncbi_url_list, Am_ncbi_file_list)

    ## download jgi data
    jgi_data_dir = "/lustre/home/xuyuxing/Work/Gel/HGT/jgi_am"
    for i in Am_jgi_data:
        file_name, download_url, md5sum = Am_jgi_data[i]
        store_file = jgi_data_dir + "/" + file_name
        Am_jgi_data[i] = (file_name, download_url, md5sum, store_file)

    Am_jgi_url_list = [Am_jgi_data[i][1] for i in Am_jgi_data]
    Am_jgi_file_list = [Am_jgi_data[i][3] for i in Am_jgi_data]

    jgi_user_name = "xuyuxing14@mails.ucas.ac.cn"
    jgi_passwd = "HGTrunning123"
    cookie_path = "/lustre/home/xuyuxing/Work/Gel/HGT/jgi/cookies"
    jgi_files_download(Am_jgi_url_list, Am_jgi_file_list, jgi_user_name, jgi_passwd, cookie_path)
