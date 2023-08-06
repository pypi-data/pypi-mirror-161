outfmt6_fieldnames = ["query_id", "subject_id", "identity", "alignment_length", "mismatches", "gap_openings",
                        "q_start", "q_end", "s_start", "s_end", "e_value", "bit_score"]


if __name__ == '__main__':
    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='FormatTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for outfmt5To6
    parser_a = subparsers.add_parser('outfmt5To6',
                                     help='convert blast results from outfmt 5 to 6',
                                     description='convert blast results from outfmt 5 to 6')

    parser_a.add_argument('input_file', type=str,
                          help='input file with outfmt 5')
    parser_a.add_argument('output_file', type=str, help='output file path')

    # argparse for outfmt5complete
    parser_a = subparsers.add_parser('outfmt5complete',
                                     help='check if outfmt5 is complete')

    parser_a.add_argument('input_file', type=str,
                          help='input file with outfmt 5')

    # argparse for genblasta2BED
    parser_a = subparsers.add_parser('genblasta2BED',
                                     help='convert genblasta output to bed file')

    parser_a.add_argument('input_file', type=str,
                          help='input file with outfmt 5')
    parser_a.add_argument('output_file', type=str, help='output file path')
    parser_a.add_argument('-p', "--ID_prefix", type=str, default='subject_',
                          help='gene output name prefix defaults: subject_')

    # argparse for blast2DB
    parser_a = subparsers.add_parser('blast2DB',
                                     help='save blast results into sqlite db')

    parser_a.add_argument('input_bls', type=str,
                          help='input file with outfmt 6')
    parser_a.add_argument('db_fasta', type=str, help='output database file')
    parser_a.add_argument('-g', "--gzip_flag",
                          help='if bls is gzipped', action='store_true')

    # argparse for outfmt6ToFasta
    parser_a = subparsers.add_parser('outfmt6ToFasta',
                                     help='extract subject sequence by blast outfmt6 results')

    parser_a.add_argument('outfmt6', type=str, help='input file with outfmt 6')
    parser_a.add_argument('db_fasta', type=str,
                          help='input file with database fasta file')
    parser_a.add_argument('output_fasta', type=str, help='output file path')

    # argparse for TrinotateOK
    parser_a = subparsers.add_parser('TrinotateOK',
                                     help='test if a trinotate pipeline is good')

    parser_a.add_argument('transcripts_file', type=str,
                          help='path of transcripts file')
    parser_a.add_argument('-o', "--output_file",
                          type=str, help='output file path')

    # argparse for MD5Checker
    parser_a = subparsers.add_parser('MD5Checker',
                                     help='check md5 files in whole dir')

    parser_a.add_argument('dir_path', type=str, help='path of dir to check')

    # argparse for Count2FPKM
    parser_a = subparsers.add_parser('Count2FPKM',
                                     help='convert featurecount to fpkm')

    parser_a.add_argument('count_file', type=str, help='path of count.txt file')
    parser_a.add_argument('count_summary', type=str, help='path of count.txt.summary file')
    parser_a.add_argument('output_file', type=str, help='path of output file')



    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # outfmt5to6
    if args_dict["subcommand_name"] == "outfmt5To6":

        from toolbiox.lib.common.util import printer_list
        from toolbiox.api.common.genome.blast import outfmt5_read_big, keep_outfmt6_info

        input_file = args.input_file
        output_file = args.output_file

        output_dict = outfmt5_read_big(input_file, False)
        with open(output_file, 'w') as f:
            for query in output_dict:
                for hsp in keep_outfmt6_info(query):
                    f.write(printer_list(hsp) + "\n")

    elif args_dict["subcommand_name"] == "outfmt5complete":
        from toolbiox.api.common.genome.blast import outfmt5_complete

        if outfmt5_complete(args.input_file):
            print("%s is complete" % args.input_file)
        else:
            print("%s is not complete" % args.input_file)

    elif args_dict["subcommand_name"] == "genblasta2BED":
        import re
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        """
        class abc(object):
            pass

        args = abc()

        args.input_file = '/lustre/home/xuyuxing/Work/Csp/ITS/Cau.rRNA'
        args.output_file = '/lustre/home/xuyuxing/Work/Csp/ITS/Cau.rRNA.bed'
        args.ID_prefix = 'Cau_ITS_'
        """

        def fancy_name_parse(input_string):
            contig_name, c_start, c_end = re.search(
                r'^(\S+):(\d+)\.\.(\d+)$', input_string).groups()
            return contig_name, int(c_start), int(c_end)

        gb_file = tsv_file_dict_parse(args.input_file, seq="|",
                                      fieldnames=['query_name', 'subject_name', 'strand', 'gene_cover', 'score',
                                                  'rank'])

        with open(args.output_file, 'w') as f:
            num = 0
            for i in gb_file:
                if gb_file[i]['rank'] is not None and re.match(r'rank:\d+', gb_file[i]['rank']):
                    num = num + 1

                    score = float(
                        re.search(r'score:(.*)', gb_file[i]['score']).group(1))

                    contig_name, c_start, c_end = fancy_name_parse(
                        gb_file[i]['subject_name'])

                    f.write("%s\t%d\t%d\t%s\t%f\t%s\n" % (
                        contig_name, c_start, c_end, args.ID_prefix + str(num), score, gb_file[i]['strand']))

    elif args_dict["subcommand_name"] == "outfmt6ToFasta":
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        from pyfaidx import Fasta
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        """
        class abc(object):
            pass

        args = abc()

        args.outfmt6 = '/lustre/home/xuyuxing/Work/Csp/Cleistogrammica/Cau.ITS.bls'
        args.db_fasta = '/lustre/home/xuyuxing/Work/Csp/ITS/Cuscuta.genome.v1.1.fasta'
        args.output_fasta = '/lustre/home/xuyuxing/Work/Csp/Cleistogrammica/Cau.ITS.seq'
        """

        blast_file = tsv_file_dict_parse(
            args.outfmt6, fieldnames=outfmt6_fieldnames)

        ref_dict = Fasta(args.db_fasta)

        with open(args.output_fasta, 'w') as f:
            for ID in blast_file:
                s_name = blast_file[ID]['subject_id']
                s_start = int(blast_file[ID]['s_start'])
                s_end = int(blast_file[ID]['s_end'])

                if s_end > s_start:
                    neg_strand = False
                    strand = "+"
                else:
                    neg_strand = True
                    strand = "-"
                    tmp = s_start
                    s_start = s_end
                    s_end = tmp

                a = ref_dict.get_seq(s_name, s_start, s_end, rc=neg_strand)
                fancy_name = "%s:%d-%d:%s" % (s_name, s_start, s_end, strand)

                contig_record = SeqRecord(
                    Seq(a.seq), id=ID, description=fancy_name)

                f.write(contig_record.format("fasta"))

    elif args_dict["subcommand_name"] == "TrinotateOK":
        import re
        import os
        from BCBio import GFF
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        from pyfaidx import Fasta
        """
        class abc(object):
            pass

        args = abc()

        args.transcripts_file = '/lustre/home/xuyuxing/Database/1kp/annotation/ERS631159/ERS631159.fasta'
        """
        work_dir = os.path.dirname(args.transcripts_file)

        check_list_dir = {
            "TransDecoder": {
                "bed_file": "uncheck",
                "cds_file": "uncheck",
                "gff3_file": "uncheck",
                "pep_file": "uncheck"
            },
            "blast": {
                "blastx": "uncheck",
                "blastp": "uncheck"
            },
            "pfam": {
                "pfam_log": "uncheck",
                "pfam_tab": "uncheck"
            },
            "signalp": {
                "signalp": "uncheck"
            },

            "tmhmm": {
                "tmhmm": "uncheck"
            },
            "rnammer": {
                "rnammer_out": "uncheck",
                "rnammer_gff": "uncheck",
            },
            "trinotate": {
                "trinotate_tab": "uncheck",
                "trinotate_go": "uncheck",
            }
        }

        # TransDecoder
        transdecoder_files = {
            "bed_file": args.transcripts_file + ".transdecoder.bed",
            "cds_file": args.transcripts_file + ".transdecoder.cds",
            "gff3_file": args.transcripts_file + ".transdecoder.gff3",
            "pep_file": args.transcripts_file + ".transdecoder.pep"
        }

        for i in transdecoder_files:
            file_name = transdecoder_files[i]
            if os.path.exists(file_name):
                if i == 'bed_file':
                    tran_id_list = []
                    with open(file_name, 'r') as f:
                        for each_line in f:
                            if re.match(r'^track name=', each_line):
                                continue
                            each_line = re.sub('\n', '', each_line)
                            tran_id = each_line.split('\t')[0]
                            tran_id_list.append(tran_id)
                    check_list_dir["TransDecoder"][i] = len(
                        list(set(tran_id_list)))
                elif i == "gff3_file":
                    num = 0
                    with open(file_name, 'r') as f:
                        for rec in GFF.parse(f):
                            num = num + 1
                    check_list_dir["TransDecoder"][i] = num
                else:
                    check_list_dir["TransDecoder"][i] = len(
                        Fasta(file_name).keys())
            else:
                check_list_dir["TransDecoder"][i] = 'failed'

        # Blast/diamond
        blast_files = {
            "blastx": work_dir + "/swissprot.blastx.outfmt6",
            "blastp": work_dir + "/swissprot.blastp.outfmt6"
        }

        for i in blast_files:
            file_name = blast_files[i]
            if os.path.exists(file_name):
                tran_id_list = []
                with open(file_name, 'r') as f:
                    for each_line in f:
                        each_line = re.sub('\n', '', each_line)
                        tran_id = each_line.split('\t')[0]
                        tran_id_list.append(tran_id)
                check_list_dir["blast"][i] = len(list(set(tran_id_list)))
            else:
                check_list_dir["blast"][i] = 'failed'

        # pfam
        pfam_files = {
            "pfam_log": work_dir + "/pfam.log",
            "pfam_tab": work_dir + "/TrinotatePFAM.out"
        }

        for i in pfam_files:
            file_name = pfam_files[i]
            if os.path.exists(file_name):
                if i == "pfam_log":
                    tran_id_list = []
                    with open(file_name, 'r') as f:
                        for each_line in f:
                            each_line = re.sub('\n', '', each_line)
                            match_list = re.findall(
                                r'^Query:\s+(\S+)\s+\S+$', each_line)
                            if len(match_list) != 0:
                                tran_id = match_list[0]
                                tran_id_list.append(tran_id)
                    check_list_dir["pfam"][i] = len(list(set(tran_id_list)))
                elif i == "pfam_tab":
                    tran_id_list = []
                    with open(file_name, 'r') as f:
                        for each_line in f:
                            if re.match(r'^#', each_line):
                                continue
                            each_line = re.sub('\n', '', each_line)
                            tran_id = each_line.split()[3]
                            tran_id_list.append(tran_id)
                    check_list_dir["pfam"][i] = len(list(set(tran_id_list)))
            else:
                check_list_dir["pfam"][i] = 'failed'

        # SIGNALP
        signalp_files = {
            "signalp": work_dir + "/signalp.out_summary.signalp5"
        }

        for i in signalp_files:
            file_name = signalp_files[i]
            if os.path.exists(file_name):
                tran_id_list = []
                with open(file_name, 'r') as f:
                    for each_line in f:
                        if re.match(r'^#', each_line):
                            continue
                        each_line = re.sub('\n', '', each_line)
                        tran_id = each_line.split()[0]
                        tran_id_list.append(tran_id)
                check_list_dir["signalp"][i] = len(list(set(tran_id_list)))
            else:
                check_list_dir["signalp"][i] = 'failed'

        # TMHMM
        tmhmm_files = {
            "tmhmm": work_dir + "/tmhmm.out"
        }

        for i in tmhmm_files:
            file_name = tmhmm_files[i]
            if os.path.exists(file_name):
                tran_id_list = []
                with open(file_name, 'r') as f:
                    for each_line in f:
                        if re.match(r'^#', each_line):
                            continue
                        each_line = re.sub('\n', '', each_line)
                        tran_id = each_line.split()[0]
                        tran_id_list.append(tran_id)
                check_list_dir["tmhmm"][i] = len(list(set(tran_id_list)))
            else:
                check_list_dir["tmhmm"][i] = 'failed'

        # RNAMMER
        rnammer_files = {
            "rnammer_out": work_dir + "/tmp.superscaff.rnammer.gff",
            "rnammer_gff": args.transcripts_file + ".rnammer.gff",
        }

        for i in rnammer_files:
            file_name = rnammer_files[i]
            if os.path.exists(file_name):
                tran_id_list = []
                num = 0
                with open(file_name, 'r') as f:
                    for rec in GFF.parse(f):
                        for gene in rec.features:
                            num = num + 1
                check_list_dir["rnammer"][i] = num
            else:
                check_list_dir["rnammer"][i] = 'failed'

        # TRINOTATE report
        trinotate_files = {
            "trinotate_tab": work_dir + "/Trinotate.xls",
            "trinotate_go": work_dir + "/Trinotate.xls.gene_ontology"
        }

        col_name = ['sprot_Top_BLASTX_hit',
                    'RNAMMER',
                    'prot_id',
                    'prot_coords',
                    'sprot_Top_BLASTP_hit',
                    'Pfam',
                    'SignalP',
                    'TmHMM',
                    'eggnog',
                    'Kegg',
                    'gene_ontology_blast',
                    'gene_ontology_pfam',
                    'transcript',
                    'peptide']

        for i in trinotate_files:
            file_name = trinotate_files[i]
            if os.path.exists(file_name):
                if i == "trinotate_tab":

                    col_hit_num_dir = {}

                    file_dict = tsv_file_dict_parse(file_name)

                    for j in col_name:
                        gene_num = len(
                            list(set([file_dict[k]['#gene_id'] for k in file_dict if file_dict[k][j] != '.'])))
                        transcript_num = len(
                            list(set([file_dict[k]['transcript_id'] for k in file_dict if file_dict[k][j] != '.'])))
                        col_hit_num_dir[j] = (gene_num, transcript_num)

                    check_list_dir["trinotate"][i] = col_hit_num_dir
                elif i == "trinotate_go":
                    tran_id_list = []
                    with open(file_name, 'r') as f:
                        for each_line in f:
                            if re.match(r'^#', each_line):
                                continue
                            each_line = re.sub('\n', '', each_line)
                            tran_id = each_line.split()[0]
                            tran_id_list.append(tran_id)
                    check_list_dir["trinotate"][i] = len(tran_id_list)
            else:
                check_list_dir["trinotate"][i] = 'failed'

        if args.output_file is not None:
            import json

            with open(args.output_file, 'w') as f:
                json.dump(check_list_dir, f)

        # make output
        if check_list_dir["trinotate"]["trinotate_tab"] == 'failed':
            print("FAILED: complete failed")
        else:
            num = 0
            for i in col_name:
                if check_list_dir["trinotate"]["trinotate_tab"][i] == (0, 0):
                    num = num + 1
            if num > 4:
                print("FAILED: too many field failed")
            else:
                print("OK: with %d bad" % num)

    elif args_dict["subcommand_name"] == "MD5Checker":
        import os
        from toolbiox.lib.common.os import cmd_run


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
                            # print(dir_path)
                            # print(cmd_string)
                            flag, output, error = cmd_run(cmd_string, cwd=dir_path, retry_max=5, silence=True,
                                                          log_file=None)
                            print(output)

        check_md5(args.dir_path)

    elif args_dict["subcommand_name"] == "blast2DB":
        from toolbiox.api.common.genome.blast import blast_to_sqlite

        blast_to_sqlite(args.db_fasta, args.input_bls, None,
                        None, 6, None, None, None, False, args.gzip_flag)

    elif args_dict["subcommand_name"] == "Count2FPKM":
        """
        class abc(object):
            pass

        args = abc()
        args.count_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/transcriptome/count.txt'
        args.count_summary = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/transcriptome/count.txt.summary'
        args.gff_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/transcriptome/Gel.gene_pseudogene.gff3'
        args.output_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/transcriptome/FPKM.txt'
        """

        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        from toolbiox.lib.common.util import printer_list
        from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, Gene


        def fpkm(count,length,mapped_count):
            return count/((length/1000)*(mapped_count/1000000))

        count_dict = tsv_file_dict_parse(args.count_file, seq='\t', ignore_head_num=1)
        count_summary_dict = tsv_file_dict_parse(args.count_summary, seq='\t')

        mapped_count = {}
        for i in count_summary_dict['ID_0']:
            if i != 'Status':
                mapped_count[i] = int(count_summary_dict['ID_0'][i])

        gff_dict = read_gff_file(args.gff_file)

        gene_length_dict = {}
        for i in gff_dict:
            for j in gff_dict[i]:
                gene_tmp = Gene(from_gf=gff_dict[i][j])
                gene_max_length = 0
                for mRNA_tmp in gene_tmp.sub_features:
                    mRNA_tmp.sgf_len()
                    if 'exon' in mRNA_tmp.sgf_len_dir:
                        gene_length = mRNA_tmp.sgf_len_dir['exon']
                    else:
                        gene_length = mRNA_tmp.sgf_len_dir['CDS']
                    if gene_length > gene_max_length:
                        gene_max_length = gene_length
                gene_length_dict[j] = gene_max_length
                
        with open(args.output_file, 'w') as f:
            header = list(count_dict['ID_0'].keys())
            sample_list = header[6:]
            g_info_list = header[:6]

            f.write(printer_list(header)+"\n")

            for i in count_dict:
                data_info = count_dict[i]
                g_id = data_info['Geneid']
                g_len = gene_length_dict[g_id]
                data_info['Length'] = g_len

                fpkm_list = [fpkm(int(data_info[i]),g_len,mapped_count[i]) for i in sample_list]

                output_list = [data_info[i] for i in g_info_list] + fpkm_list

                f.write(printer_list(output_list)+"\n")

    elif args_dict["subcommand_name"] == "id_replace":
        import re
        import sys

        target_file = sys.argv[1]
        map_file = sys.argv[2]
        output_file = sys.argv[3]

        replace_dict = {}
        with open(map_file, 'r') as f:
            for each_line in f:
                each_line.strip()
                a,b = each_line.split()
                replace_dict[a] = b

        with open(output_file, 'w') as fo:
            with open(target_file, 'r') as f:
                for each_line in f:
                    each_line.strip()
                    get_list = list(set(re.findall(r'[a-zA-Z]+_\d+', each_line)))
                    num = 0
                    
                    from_string = None
                    for i in get_list:
                        if i in replace_dict:
                            num += 1
                            from_string = i

                    if num > 1:
                        raise ValueError('two more match %s' % each_line)
                    elif num == 1:
                        to_string = replace_dict[from_string]
                        each_line = each_line.replace(from_string, to_string)

                    fo.write(each_line)



