import argparse

def main_argparse():

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='DeepTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for CleanFastq
    parser_a = subparsers.add_parser('CleanFastq',
                                        help='clean fastq files\n',
                                        description='')

    parser_a.add_argument('raw_fastq1', type=str, help='raw fastq file 1')
    parser_a.add_argument('raw_fastq2', type=str, help='raw fastq file 2')
    parser_a.add_argument('tag', type=str, help='tag for fastq')
    parser_a.add_argument("-a", "--adapter", help="clean adapter ('illumina' or 'mgi_seq' or sequence)",
                            type=str, default='illumina')

    # argparse for BamSplit
    parser_a = subparsers.add_parser('BamSplit',
                                        help='split a big read sorted bam file by reads number\n',
                                        description='')

    parser_a.add_argument('input_bam_file', type=str, help='raw bam file')
    parser_a.add_argument("-r", "--reads_per_file", help="how many reads should in one bam file (default:1000000)",
                            type=int, default=1000000)
    parser_a.add_argument('-c', "--by_contig",
                            help='split bam by contig', action='store_true')
    parser_a.add_argument('-l', "--log_file", type=str,
                            help='path for log file (default:None)', default=None)
    parser_a.add_argument('-k', "--keep_head",
                            help='keep raw head', action='store_true')

    # argparse for MappedReadsComparing
    parser_a = subparsers.add_parser('MappedReadsComparing',
                                        help='comparing the mapped reads CIgar from two reference genome \n',
                                        description='')

    parser_a.add_argument('fastq_file', type=str, help='the clean reads file')
    parser_a.add_argument('mapped_bam_file_1', type=str, help='the bam file 1 from reference genome A')
    parser_a.add_argument('mapped_bam_file_2', type=str, help='the bam file 2 from reference genome B')
    parser_a.add_argument('reads_id_file', type=str, help='the reads id list from fastq file')
    parser_a.add_argument('tag1', type=str, help='A flag')
    parser_a.add_argument('tag2', type=str, help='B flag')
    parser_a.add_argument('tag_file', type=str, help='the output tag file')


    # argparse for ReadMapStats
    parser_a = subparsers.add_parser('ReadMapStats',
                                        help='stats the reads mapping hits for a bam file\n',
                                        description='')

    parser_a.add_argument('input_bam_file', type=str, help='raw bam file')
    parser_a.add_argument('-l', "--log_file", type=str,
                            help='path for log file (default:None)', default=None)
    parser_a.add_argument(
        "-t", "--threads", help="cpu num, (default:20)", default=20, type=int)
    parser_a.add_argument("-r", "--reads_per_file", help="how many reads should in one bam file (default:1000000)",
                            type=int, default=1000000)

    # argparse for Fastq2pbbam
    parser_a = subparsers.add_parser('Fastq2pbbam',
                                        help="""
                                        use subread fastq data to maker a pacbio bam file to cheat ccs program in pacbio github
                                        
                                        $ dnapi.py 20190627.Gelata-red1_iso.cell1.subreads.fastq
                                        GTATCAACGCAGAGTAC
                                        
                                        $ cutadapt -g GTATCAACGCAGAGTAC -e 0.3 --action lowercase -o left.cut.fq 20190627.Gelata-red1_iso.cell1.subreads.fastq
                                        $ cutadapt -a GTACTCTGCGTTGATAC -e 0.3 --action lowercase -o right.cut.fq 20190627.Gelata-red1_iso.cell1.subreads.fastq
                                        """,
                                        description="""
                                        use subread fastq data to maker a pacbio bam file to cheat ccs program in pacbio github\n
                                        
                                        $ dnapi.py 20190627.Gelata-red1_iso.cell1.subreads.fastq\n
                                        GTATCAACGCAGAGTAC\n
                                        
                                        $ cutadapt -g GTATCAACGCAGAGTAC -e 0.3 --action lowercase -o left.cut.fq 20190627.Gelata-red1_iso.cell1.subreads.fastq\n
                                        $ cutadapt -a GTACTCTGCGTTGATAC -e 0.3 --action lowercase -o right.cut.fq 20190627.Gelata-red1_iso.cell1.subreads.fastq\n
                                        """)

    parser_a.add_argument('fastq_file', type=str,
                            help='input fastq file, maybe from ncbi')
    parser_a.add_argument('leaf_cut_fastq', type=str, help='leaf cutadapt')
    parser_a.add_argument('right_cut_fastq', type=str, help='right cutadapt')
    parser_a.add_argument('bam_file', type=str, help='output bam file')

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # BamSplit
    if args_dict["subcommand_name"] == "BamSplit":
        from toolbiox.src.xuyuxing.tools.deeptools import BamSplit_main
        BamSplit_main(args)

    # ReadMapStats
    elif args_dict["subcommand_name"] == "ReadMapStats":
        """
        class abc(object):
            pass

        args = abc()

        args.log_file = '/lustre/home/xuyuxing/Work/Other/saif/Meth/test/log'
        args.input_bam_file = '/lustre/home/xuyuxing/Work/Other/saif/Meth/test/test.bam'
        args.reads_per_file = 10000
        args.threads = 50
        """
        from toolbiox.src.xuyuxing.tools.deeptools import ReadMapStats_main
        ReadMapStats_main(args)

    # Fastq2pbbam
    elif args_dict["subcommand_name"] == "Fastq2pbbam":
        """
        class abc():
            pass

        args = abc()
        args.fastq_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/trans/full_length/bam_file/20190627.Gelata-red1_iso.cell1.subreads.fastq'
        args.leaf_cut_fastq = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/trans/full_length/bam_file/left.cut.fq'
        args.right_cut_fastq = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/trans/full_length/bam_file/right.cut.fq'
        args.bam_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/trans/full_length/bam_file/new.subreads.bam'
        """
        from toolbiox.src.xuyuxing.tools.deeptools import Fastq2pbbam_main
        Fastq2pbbam_main(args)

    # CleanFastq
    elif args_dict["subcommand_name"] == "CleanFastq":
        from toolbiox.src.xuyuxing.tools.deeptools import clean_fastq_main
        clean_fastq_main(args.tag, args.raw_fastq1,
                            args.raw_fastq2, args.adapter)

    # MappedReadsComparing
    elif args_dict["subcommand_name"] == "MappedReadsComparing":
        from toolbiox.src.xuyuxing.tools.MappedReadsComparing import MappedReadsComparing_main
        MappedReadsComparing_main(args)

if __name__ == '__main__':
    main_argparse()