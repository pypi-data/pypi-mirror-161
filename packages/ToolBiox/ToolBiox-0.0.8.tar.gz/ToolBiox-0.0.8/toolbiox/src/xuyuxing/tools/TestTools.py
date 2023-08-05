import pysam
import os
from toolbiox.lib.base.base_function import cmd_run
import time 
from toolbiox.lib.seq.seq_base import read_fastq_big
import sys
import toolbiox.lib.file_parser.sqlite_command as sc
from toolbiox.lib.file_parser.fileIO import read_list_file

__author__ = 'Yuxing Xu'


def read_fasta(fasta_file):
    fasta_dict = {}
    with open(fasta_file, 'r') as f:
        all_str = f.read()
        all_str_splited_list = all_str.split('>')
        all_str_splited_list = all_str_splited_list[1:]

        for i in all_str_splited_list:
            contig_info_list = i.split('\n')
            contig_id = contig_info_list[0].split()[0]
            seq_list = contig_info_list[1:]
            seq = ''
            for j in seq_list:
                seq = seq + j
            fasta_dict[contig_id] = seq

    return fasta_dict


# def read_fasta2(fasta_file):
#     fasta_dict = {}
#
#     for record in SeqIO.parse(fasta_file, "fasta"):
#         contig_id = record.id
#         contig_seq = str(record.seq)
#
#         fasta_dict[contig_id] = contig_seq
#
#     return fasta_dict


def read_bam(bam_file):
    bf = pysam.AlignmentFile(bam_file, 'r')
    for r in bf.fetch(until_eof=True):
        pass

        if len(read_tmp_record) == 0 or r.query_name == read_tmp_record[-1].query_name:
            read_tmp_record.append(r)
            continue
        else:
            yield read_tmp_record
            read_tmp_record = [r]
    if len(read_tmp_record) != 0:
        yield read_tmp_record
    bf.close()

def check_md5(dir_path):
    dir_path = os.path.abspath(dir_path)

    file_dir_list = os.listdir(dir_path)
    for tmp_name in file_dir_list:
        tmp_name_full_path = dir_path + "/" + tmp_name
        if os.path.isdir(tmp_name_full_path):
            check_md5(tmp_name_full_path)
        else:
            tmp_list = tmp_name.split("_")
            if len(tmp_list) > 1:
                if tmp_list[0] == 'MD5':
                    cmd_string = "md5sum -c %s" % tmp_name
                    flag, output, error = cmd_run(cmd_string, cwd=dir_path, retry_max=5, silence=True)
                    print (output)

def decompressed_gz(dir_path):
    dir_path = os.path.abspath(dir_path)

    file_dir_list = os.listdir(dir_path)
    for tmp_name in file_dir_list:
        tmp_name_full_path = dir_path + "/" + tmp_name
        if os.path.isdir(tmp_name_full_path):
            decompressed_gz(tmp_name_full_path)
        else:
            tmp_list = tmp_name.split(".")
            if len(tmp_list) > 1:
                if tmp_list[-1] == 'gz':
                    cmd_string = "gunzip %s" % tmp_name
                    flag, output, error = cmd_run(cmd_string, cwd=dir_path, retry_max=5, silence=True)

def copy_gz(dir_path,target_dir):
    dir_path = os.path.abspath(dir_path)

    file_dir_list = os.listdir(dir_path)
    for tmp_name in file_dir_list:
        tmp_name_full_path = dir_path + "/" + tmp_name
        if os.path.isdir(tmp_name_full_path):
            copy_gz(tmp_name_full_path,target_dir)
        else:
            tmp_list = tmp_name.split(".")
            if len(tmp_list) > 1:
                if tmp_list[-1] == 'gz':
                    cmd_string = "cp %s %s" % (tmp_name,target_dir)
                    flag, output, error = cmd_run(cmd_string, cwd=dir_path, retry_max=5, silence=True)

def readsID_calling(dup_id,all_id,not_dup_id):
    dup_id_dict = {}
    with open(dup_id, 'r') as f:
        for each_line in f:
            each_line = each_line.strip()
            dup_id_dict[each_line] = ""
    
    # start_time = time.time()
    # num=0
    with open(not_dup_id, 'w') as o:
        with open(all_id, 'r') as f:
            for each_line in f:
                # num = num +1

                # round_time = timr.time()
                # if round_time-start_time >2
                #    start_time= round_time 
                    #  print(num)
                each_line = each_line.strip()
                if not each_line in dup_id_dict:
                    o.write(each_line + "\n")

# valid_aln_list = [alignedsegment for alignedsegment in read_aln_list if not (alignedsegment.is_secondary or alignedsegment.is_supplementary)]
# upper code = following code 
# valid_aln_list = []
# for alignedsegment in read_aln_list:
#     if not (alignedsegment.is_secondary or alignedsegment.is_supplementary):
#          valid_aln_list.append(alignedsegment)

# get all of the reads ID from clean fastaq files


def get_read_name_list_from_fastq(fastq_file_name, output_file_name):
   
    with open(output_file_name, 'w') as f:
        for record in read_fastq_big(fastq_file_name,gzip_flag=True):
            f.write(record[0].seqname_short() + "\n")

    return output_file_name


def index_bam_file(bam_file):
    bamfile = pysam.AlignmentFile(bam_file, 'rb')
    name_indexed = pysam.IndexedReads(bamfile)
    name_indexed.build()
    header = bamfile.header.copy()
    return name_indexed, header


def extract_aln_by_reads(reads_name, name_indexed):
    output_list = []
    try:
        name_indexed.find(reads_name)
    except KeyError:
        pass
    else:
        iterator = name_indexed.find(reads_name)
        output_list = []
        for x in iterator:
            output_list.append(x)
    
    return output_list

def get_top_M_score(read_aln_list):
    top_M = 0
    
    for aln in read_aln_list:
        cigar_list = aln.cigar
        TM = sum([i[1] for i in cigar_list if i[0] == 0])
        DM = sum([i[1] for i in cigar_list if not (i[0] == 0 or i[0] == 3)])

        M = TM - DM

        if M > top_M:
            top_M = M
    
    return top_M


def get_best_alignment_match_number(read_aln_list):
    valid_aln_list = [alignedsegment for alignedsegment in read_aln_list if not (alignedsegment.is_secondary or alignedsegment.is_supplementary)]

    # get 1-end
    read1_aln_list = [alignedsegment for alignedsegment in valid_aln_list if alignedsegment.is_read1]

    # get 2-end
    read2_aln_list = [alignedsegment for alignedsegment in valid_aln_list if alignedsegment.is_read2]

    read1_top_M = get_top_M_score(read1_aln_list)
    read2_top_M = get_top_M_score(read2_aln_list)

    M_score = read1_top_M + read2_top_M

    return M_score


def get_tag(read_aln_list1, read_aln_list2, tag1, tag2):
    M1 = get_best_alignment_match_number(read_aln_list1)
    M2 = get_best_alignment_match_number(read_aln_list2)

    if M1 > M2:
        return tag1, M1, M2
    elif M2 > M1:
        return tag2, M1, M2
    else:
        return "X", M1, M2

def write_aln(read_name, name_indexed, header, sam_output_file):
    aln_list = extract_aln_by_reads(read_name, name_indexed)

    out = pysam.Samfile(sam_output_file, 'wb', header=header)
    for aln in aln_list:
        out.write(aln)

def get_tag_new(reads_id, db_file):
    table_id = sum([int(i) for i in reads_id.split(":")[-3:]]) % 100
    table_id = "table" + str(table_id)

    reads_id_get, tag_get = sc.sqlite_select(db_file, table_id, ['reads_id', 'tag'], 'reads_id', (reads_id,))[0]
    
    return tag_get

def get_tag_many(reads_id_list, db_file):

    table_reads_dict = {}
    for reads_id in reads_id_list:
        table_id = sum([int(i) for i in reads_id.split(":")[-3:]]) % 100
        table_id = "table" + str(table_id)
        if table_id not in table_reads_dict:
            table_reads_dict[table_id] = []
        table_reads_dict[table_id].append(reads_id)

    tag_dict = {}
    for table_id in table_reads_dict:
        info = sc.sqlite_select(db_file, table_id, ['reads_id', 'tag'], 'reads_id', table_reads_dict[table_id])
        for reads_id_get, tag_get in info:
            tag_dict[reads_id_get] = tag_get
    
    return tag_dict


if __name__ == '__main__':
    import argparse

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='TestTools',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for SubGenomeExtracter
    parser_a = subparsers.add_parser('SubGenomeExtracter',
                                     help='extract a genome fragment\n',
                                     description='')

    parser_a.add_argument('genome_fasta_file', type=str, help='raw genome fasta file')
    parser_a.add_argument('output_fasta_file', type=str, help='output fasta file')
    parser_a.add_argument('table_file', type=str, help='a table which include info of locals, (Chr1  1   100)')
    parser_a.add_argument("-e", "--expand_range", help="length of expand range", type=int, default=0)

    # argparse for ReadsCleanTools
    parser_a = subparsers.add_parser('ReadsCleanTools',
                                     help='Clean bad mapped reads\n',
                                     description='')

    parser_a.add_argument('reads_bam_file', type=str, help='mapping reads bam file')
    parser_a.add_argument('output_fasta_file', type=str,
                          help='a clean fasta file which exclude bad mapping qualities reads info of flower-related')
    parser_a.add_argument('threshold', type=float,
                          help='threshold')

    # argparse for CheckMD5
    parser_a = subparsers.add_parser('CheckMD5',
                                     help='check MD5 value rightness \n',
                                     description='')

    parser_a.add_argument('dir_path', type=str, help='the absolute path of dir')

    # argparse for decompressed_gz
    parser_a = subparsers.add_parser('decompressed_gz',
                                     help='decompressed all gz file \n',
                                     description='')

    parser_a.add_argument('dir_path', type=str, help='the absolute path of dir')

    # argparse for copy_gz
    parser_a = subparsers.add_parser('copy_gz',
                                     help='copy all gz file \n',
                                     description='')

    parser_a.add_argument('dir_path', type=str, help='the absolute path of dir')
    parser_a.add_argument('target_dir', type=str, help='the target stored dir')

    # argparse for rm_cleandata_file
    parser_a = subparsers.add_parser('rm_cleandata_file',
                                     help='rm all cleandata file \n',
                                     description='')

    parser_a.add_argument('dir_path', type=str, help='the absolute path of dir')

    # argparse for readsID_calling
    parser_a = subparsers.add_parser('readsID_calling',
                                     help='calling out the no duplicated reads \n',
                                     description='')

    parser_a.add_argument('dup_id', type=str, help='the duplicated reads id file')
    parser_a.add_argument('all_id', type=str, help='the all reads id file')
    parser_a.add_argument('not_dup_id', type=str, help='the no duplicated reads id file')

    # argparse for MappedReadsComparing
    parser_a = subparsers.add_parser('MappedReadsComparing',
                                     help='comparing the mapped reads CIgar from two reference genome \n',
                                     description='')

    parser_a.add_argument('fastq_file', type=str, help='the clean reads file')
    parser_a.add_argument('mapped_bam_file_1', type=str, help='the bam file 1 from reference genome A188')
    parser_a.add_argument('mapped_bam_file_2', type=str, help='the bam file 2 from reference genome B73')
    parser_a.add_argument('reads_id_file', type=str, help='the reads id list from fastq file')
    parser_a.add_argument('tag1', type=str, help='A188 flag')
    parser_a.add_argument('tag2', type=str, help='B73 flag')
    parser_a.add_argument('tag_file', type=str, help='the output tag file')
    
    # ConvertTagfileToDBfile
    parser_a = subparsers.add_parser('ConvertTagfileToDBfile',
                                     help='converting the tag files to databasefiles \n',
                                     description='')
    parser_a.add_argument('tag_file', type=str, help='the tag file')
    parser_a.add_argument('db_file', type=str, help='the database file')
    
    # ConvertReadsidfileToDBfile
    parser_a = subparsers.add_parser('ConvertReadsidfileToDBfile',
                                     help='converting the reads id files to databasefiles \n',
                                     description='')
    parser_a.add_argument('readsid_file', type=str, help='the reads id file')
    parser_a.add_argument('db_file', type=str, help='the database file')


    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # ccommand detail

    # SubGenomeExtracter
    if args_dict["subcommand_name"] == "SubGenomeExtracter":
        """
        class abc():
            pass

        args = abc()

        args.genome_fasta_file = '/lustre/home/macanrong/Work/Nicotiana_sylvestris/GCF_000393655.1_Nsyl_genomic.fna.fasta'
        args.output_fasta_file = '/lustre/home/xuyuxing/tmp.file'
        args.table_file = '/lustre/home/macanrong/Work/Nicotiana_sylvestris/Flow.gene.loci.clean'
        args.expand_range = 3000
        """

        # read table file
        table_info_dict = {}
        num = 0
        with open(args.table_file, 'r') as f:
            for each_line in f:
                num = num + 1
                info_list = each_line.split()
                table_info_dict[num] = info_list

        # read genome file
        fasta_dict = read_fasta(args.genome_fasta_file)

        # extract
        output_dict = {}
        for id in table_info_dict:
            contig_id, start_point, end_point = table_info_dict[id]
            start_point = int(start_point)
            end_point = int(end_point)

            contig_length = len(fasta_dict[contig_id])

            expand_start_point = max(1, start_point - args.expand_range)
            expand_end_point = min(contig_length, end_point + args.expand_range)

            get_sub_genome_seq = fasta_dict[contig_id][expand_start_point - 1:expand_end_point]
            get_sub_genome_seq = get_sub_genome_seq.upper()

            # output_id = contig_id + ":" + str(expand_start_point) + "-" + str(expand_end_point)
            output_id = "%s:%d-%d" % (contig_id, expand_start_point, expand_end_point)

            output_dict[output_id] = get_sub_genome_seq

        with open(args.output_fasta_file, 'w') as f:
            for output_id in output_dict:
                output_seq = output_dict[output_id]
                f.write(">%s\n%s\n" % (output_id, output_seq))

    elif args_dict["subcommand_name"] == "ReadsCleanTools":
        """
        class abc():
            pass

        args = abc()

        args.reads_bam_file = '/lustre/home/macanrong/Work/Nicotiana_sylvestris/Nsyl.m64033_200313_001421.bam'
        args.output_fasta_file = '/lustre/home/macanrong/Work/Nicotiana_sylvestris/Nsyl.m64033_200313_001421.fasta'
        args.threshold = 0.2
        """

        # read bam file

        read_appear_counter = {}

        bf = pysam.AlignmentFile(args.reads_bam_file, 'r')

        with open(args.output_fasta_file, 'w') as f:
            for r in bf.fetch(until_eof=True):
                read_name = str(r.query_name)
                aln_length = int(r.query_alignment_length)
                aln_seq = str(r.query_alignment_sequence)

                ref_name = str(r.reference_name)
                start, end = ref_name.split(":")[1].split("-")
                ref_length = int(end) - int(start) + 1

                if aln_length / ref_length > args.threshold:

                    # reads name repeat check
                    if read_name in read_appear_counter:
                        read_appear_counter[read_name] = read_appear_counter[read_name] + 1
                    else:
                        read_appear_counter[read_name] = 1

                    read_name_mod = read_name + "_" + str(read_appear_counter[read_name])

                    f.write(">%s\n%s\n" % (read_name_mod, aln_seq))

    # check_md5
    elif args_dict["subcommand_name"] == "CheckMD5":
        """
        class abc():
            pass

        args = abc()

        args.dir_path = '/lustre/home/macanrong/Database/maize_F1/1.rawdata'
        """

        # print(args.dir_path)
        # print(args.output_MD5_file)

        check_md5_list = check_md5(args.dir_path)
        print(check_md5_list)


    #decompressed_gz
    elif args_dict["subcommand_name"] == "decompressed_gz":
        """
        class abc():
            pass

        args = abc()

        args.dir_path = '/lustre/home/macanrong/Database/maize_F1/1.rawdata'
        """
        decompressed_gz(args.dir_path)

    # copy_gz
    elif args_dict["subcommand_name"] == "copy_gz":
        """
        class abc():
            pass

        args = abc()

        args.dir_path = '/lustre/home/macanrong/Database/maize_F1/1.rawdata'
        args.target_dir = '/lustre/home/macanrong/Database/maize_F1/cleandata'
        """
        copy_gz(args.dir_path,args.target_dir)

    # rm_cleandata_file
    elif args_dict["subcommand_name"] == "rm_cleandata_file":
        """
        class abc():
            pass

        args = abc()

        args.dir_path = '/lustre/home/macanrong/Database/maize_F1/1.rawdata'
        args.target_dir = '/lustre/home/macanrong/Database/maize_F1/cleandata'
        """
        rm_cleandata_file(args.dir_path)

    # readsID_calling
    elif args_dict["subcommand_name"] == "readsID_calling":
        """
        class abc():
        pass

        args = abc()

        args.dup_id = '/lustre/home/macanrong/Database/maize_F101/cleandata/deduplic_dir/M21-1.dup.id'
        args.all_id = '/lustre/home/macanrong/Database/maize_F101/cleandata/deduplic_dir/M21-1.all.id'
        args.not_dup_id = '/lustre/home/macanrong/Database/maize_F101/cleandata/deduplic_dir/M21-1.not_dup.id'
        """

        readsID_calling(args.dup_id, args.all_id, args.not_dup_id)

    # MappedReadsComparing
    elif args_dict["subcommand_name"] == "MappedReadsComparing":
        # get all of the reads ID from clean fastaq files
        """
        class abc():
        pass

        args = abc()
        args.fastq_file = '/lustre/home/macanrong/Work/maize_F1/tophat2/test/20000.fq.gz'
        args.reads_id_file = '/lustre/home/macanrong/Work/maize_F1/tophat2/test/20000.id'
        args.mapped_bam_file_1 ='/lustre/home/macanrong/Work/maize_F1/tophat2/test/accepted_hits.A188.bam'
        args.mapped_bam_file_2 ='/lustre/home/macanrong/Work/maize_F1/tophat2/test/accepted_hits.B73.bam'
        args.tag1 = "A188"
        args.tag2 = "B73"
        args.tag_file = "/lustre/home/macanrong/Work/maize_F1/tophat2/test/20000.id.tag"
        """


        def MappedReadsComparing_main(args):
            reads_id_file= get_read_name_list_from_fastq(args.fastq_file, args.reads_id_file)


            # indexed the bam file
            name_indexed_1, header1 = index_bam_file(args.mapped_bam_file_1)
            name_indexed_2, header2 = index_bam_file(args.mapped_bam_file_2)

            # remove the None element
            with open(args.tag_file, 'w') as w:
                with open(args.reads_id_file, 'r') as f:
                    for each_line in f:
                        read_name = each_line.strip()
                
                        # extracting the alignmentseqments
                        read_aln_list_1= extract_aln_by_reads(read_name, name_indexed_1)
                        read_aln_list_2= extract_aln_by_reads(read_name, name_indexed_2)
                
                        tag, M1 , M2  = get_tag(read_aln_list_1, read_aln_list_2, args.tag1, args.tag2)

                        w.write("%s\t%s\t%d\t%d\n" % (read_name, tag, M1, M2))

    # ConvertTagfileToDBfile
    elif args_dict["subcommand_name"] == "ConvertTagfileToDBfile":
        # converting the tag files into the database files
        """
        class abc():
        pass

        args = abc()
        args.tag_file = "/lustre/home/macanrong/Work/maize_F1/tophat2/M46.tag"
        args.db_file = "/lustre/home/xuyuxing/M46.db"
        """

        sys.path.append("/lustre/home/xuyuxing/python_project/Genome_work_tools")

        table_columns_dict = { "table" + str(i) : ["reads_id", "tag", "A_score", "B_score"] for i in range(0,100) }


        sc.init_sql_db_many_table(db_file, table_columns_dict, remove_old_db=True)

        # num = 0

        waitting_dict = {}

        with open(args.tag_file, "r") as f:
            for each_line in f:
                # num += 1
                # if num > 50000:
                #     break
                each_line = each_line.strip()
                info = each_line.split()
                reads_id = info[0]
                reads_tag = info[1]
                reads_sample1 = int(info[2])
                reads_sample2 = int(info[3])

                table_id = sum([int(i) for i in reads_id.split(":")[-3:]]) % 100
                table_id = "table" + str(table_id)

            if table_id not in waitting_dict:
                waitting_dict[table_id] = []
                waitting_dict[table_id].append((reads_id, reads_tag, reads_sample1, reads_sample2))

            if len(waitting_dict[table_id]) > 10000:
                sc.sqlite_write(waitting_dict[table_id], args.db_file, table_id, ["reads_id", "tag", "A_score", "B_score"])
                waitting_dict[table_id] = []

        for table_id in waitting_dict:
            if len(waitting_dict[table_id]) > 0:
                sc.sqlite_write(waitting_dict[table_id], args.db_file, table_id, ["reads_id", "tag", "A_score", "B_score"])
                waitting_dict[table_id] = []

        for table_id in table_columns_dict:
            sc.build_index(args.db_file, table_id, 'reads_id')


    # ConvertReadsidfileToDBfile
    elif args_dict["subcommand_name"] == "ConvertReadsidfileToDBfile":
        # converting the reads ID files into the database files
        """
        class abc():
        pass

        args = abc()
        args.reads_id = "/lustre/home/macanrong/Work/maize_F1/tophat2/test/M9-1.readsid.file"
        args.db_file = "/lustre/home/macanrong/Work/maize_F1/tophat2/test/M9-1.db"
        """

        reads_id_list = read_list_file(args.reads_id)

        tag_list = [get_tag_new(i, args.db_file) for i in reads_id_list]
        tag_dict = get_tag_many(reads_id_list, args.db_file)

        












