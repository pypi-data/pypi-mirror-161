if __name__ == '__main__':
    import argparse

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='GenomeTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for GenomeFormater
    parser_a = subparsers.add_parser('GenomeFormater',
                                     help='make genome info to a strandard fromat\n',
                                     description='')

    parser_a.add_argument('gff_file', type=str,
                          help='Path of genome feature gff file')
    parser_a.add_argument('rename_prefix', type=str,
                          help='prefix of rename, like: Ath')
    parser_a.add_argument('output_dir', type=str, help='Path of output dir')
    parser_a.add_argument('-g', '--genome_fasta_file', type=str,
                          help='Path of genome fasta file', default=None)
    parser_a.add_argument('-p', '--protein_fasta_file', type=str,
                          help='Path of protein fasta file', default=None)
    parser_a.add_argument('-c', '--cds_fasta_file', type=str,
                          help='Path of CDS fasta file', default=None)
    parser_a.add_argument("-m", "--mode", help='raw data mode, which related to source of data',
                          default="normal", choices=['normal', 'phytozome', 'ncbi'])
    parser_a.add_argument("-k", "--keep_raw_contig_id", help="keep raw contig id, just change gene name",
                          action='store_true')

    # argparse for FragmentGenome
    parser_a = subparsers.add_parser('FragmentGenome',
                                     help='cut genome to fragment')
    parser_a.add_argument(
        "genome_file", help="Path of genome file with fasta format", type=str)
    parser_a.add_argument(
        "output_file", help="Path of cutted genome file", type=str)
    parser_a.add_argument("step", help="step of genome cutting", type=int)
    parser_a.add_argument(
        "length", help="length of sequence of cutted genome", type=int)

    parser_a.add_argument("-s", "--Consider_scaffold", help="If consider scaffold in the genome (default as True)",
                          default=True)

    # argparse for ReGetContig
    parser_a = subparsers.add_parser('ReGetContig',
                                     help='cut scaffold to contig')
    parser_a.add_argument(
        "scaff_file", help="Path of scaffold version to contig again", type=str)
    parser_a.add_argument(
        "output_gff3", help="Path of cutted contig gff file", type=str)
    parser_a.add_argument(
        "output_fasta", help="Path of cutted contig fasta file", type=str)
    parser_a.add_argument(
        "-t", "--threads", help="threads number (default as 5)", default=5, type=int)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # FragmentGenome
    if args_dict["subcommand_name"] == "FragmentGenome":
        import toolbiox.lib.common.genome.seq_base as fa

        genome_file = args.genome_file
        output_file = args.output_file
        step = args.step
        length = args.length
        Consider_scaffold = args.Consider_scaffold

        with open(output_file, 'w') as f:
            for i in fa.read_fasta_big(genome_file):
                record_tmp = i
                seq_name = record_tmp.seqname_short()
                sequence = record_tmp.seq
                for start, sub_seq in fa.scaffold_cutting(sequence, step=step, length=length,
                                                          Consider_scaffold=Consider_scaffold):
                    end = len(sub_seq) + start - 1
                    sub_seq_name = seq_name + "_" + str(start) + "-" + str(end)
                    f.write(">%s\n%s\n" % (sub_seq_name, sub_seq))

    # ReGetContig
    elif args_dict["subcommand_name"] == "ReGetContig":
        from toolbiox.src.xuyuxing.GenomeTools.ReGetContig import ReGetContig_main
        ReGetContig_main(args)

    # GenomeFormater
    elif args_dict["subcommand_name"] == "GenomeFormater":
        from toolbiox.src.xuyuxing.GenomeTools.GenomeFormater import GenomeFormater_main
        GenomeFormater_main(args)


