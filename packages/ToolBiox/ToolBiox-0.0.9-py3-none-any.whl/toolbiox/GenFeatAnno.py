if __name__ == '__main__':
    import argparse

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='GenFeatAnno',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for Telomere
    parser_a = subparsers.add_parser('Telomere',
                                     help='find telomeres in an assembly\n',
                                     description='')

    parser_a.add_argument('fasta_file', type=str, help='a fasta file')
    parser_a.add_argument('-d', '--dat', type=str,
                          help='if you already have a data file, you can input it with -d', default=None)
    parser_a.add_argument('-trf', '--trf_path', type=str,
                          help='path for trf program (default: trf)', default="trf")
    parser_a.add_argument('-l', '--log_file', type=str,
                          help='path for log file (default: None)', default=None)
    parser_a.add_argument('-o', '--output_prefix', type=str,
                          help='output prefix (default: output_)', default='output_')

    # argparse for Centromere
    parser_a = subparsers.add_parser('Centromere',
                                     help='find centromeres in an assembly\n',
                                     description='')

    parser_a.add_argument('-f', '--fasta_file', type=str, help='a fasta file')
    parser_a.add_argument('-d', '--trf_dat', type=str,
                          help='if you already have a data file, you can input it with -d', default=None)
    parser_a.add_argument('-o', '--work_dir', type=str,
                          help='output dir (default: centromeres)', default='centromeres')
    parser_a.add_argument("-t", "--threads", help="num of threads (default:56)", default=56, type=int)                          

    # argparse for rRNAFinder
    parser_a = subparsers.add_parser('rRNAFinder',
                                     help='find rRNA unit and all rRNA in genome\n',
                                     description='')

    parser_a.add_argument('fasta_file', type=str, help='a fasta file')
    parser_a.add_argument('-s', '--query_rRNA_seq', type=str, default=None,
                          help='a known rRNA unit seq from close species')
    parser_a.add_argument('-b', '--query_rRNA_bed', type=str, default=None,
                          help='bed file for close rRNA unit seq')
    parser_a.add_argument('-l', '--log_file', type=str,
                          help='path for log file (default: None)', default=None)
    parser_a.add_argument('-o', '--output_dir', type=str, help='output prefix (default: rRNA_finder)',
                          default='rRNA_finder')

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # Telomere
    if args_dict["subcommand_name"] == "Telomere":
        from toolbiox.src.xuyuxing.GenomeTools.Telomere import Telomere_main
        Telomere_main(args)

    # Centromere
    elif args_dict["subcommand_name"] == "Centromere":
        from toolbiox.src.xuyuxing.GenomeTools.CentromereSeed import CentromereSeed_main
        CentromereSeed_main(args)

    # rRNAFinder
    elif args_dict["subcommand_name"] == "rRNAFinder":
        from toolbiox.src.xuyuxing.GenomeTools.rRNAFinder import rRNAFinder_main
        rRNAFinder_main(args)
