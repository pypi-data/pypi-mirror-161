__author__ = 'Yuxing Xu'


if __name__ == '__main__':
    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='TransTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for TrinityGene
    parser_a = subparsers.add_parser('TrinityGene',
                                     help='Extract longest isoform from a gene in trinity output\n',
                                     description='Extract longest isoform from a gene in trinity output')

    parser_a.add_argument('Trinity_output', type=str,
                          help='a fasta file from trinity output')
    parser_a.add_argument('Trinity_gene', type=str,
                          help='a fasta file from this script')

    # argparse for GenerateTrinityGeneTransMap
    parser_a = subparsers.add_parser('GenerateTrinityGeneTransMap',
                                     help='Generate Trinity Gene Trans Map file from trinity fasta\n'
                                     )

    parser_a.add_argument('Trinity_output', type=str,
                          help='a fasta file from trinity output')
    parser_a.add_argument('gene_map_file', type=str,
                          help='a tab file for gene_map')

    # argparse for Denovo2RefCountMap
    parser_a = subparsers.add_parser('Denovo2RefCountMap',
                                     help='Use denovo trinity make gene count, and map it to a genome\n'
                                     )

    parser_a.add_argument('gene_model_cds_file', type=str,
                          help='cds file from reference genome')
    parser_a.add_argument('tran_fasta_file', type=str,
                          help='a fasta file from trinity output')
    parser_a.add_argument('gene_trans_map', type=str,
                          help='a gene_trans_map file from trinity output')
    parser_a.add_argument('-f', '--tran_count_fof', type=str, default=None,
                          help='a list of rsem genes.results file: (sampleid rsem_count_file)')
    parser_a.add_argument('-c', '--tran_count_matrix', type=str, default=None,
                          help='a count matrix')
    parser_a.add_argument('-w', '--work_dir', type=str, default='tmp',
                          help='tmp work dir')
    parser_a.add_argument('-o', '--output_prefix', type=str, default='Gene',
                          help='output prefix')
    parser_a.add_argument('-t', '--threads', type=int, default=56,
                          help='number of threads: defaults 56')

    # argparse for Count2TMM
    parser_a = subparsers.add_parser('Count2TMM',
                                     help='from count matrix 2 TMM matrix, FPKM and TPM will give to\n'
                                     )

    parser_a.add_argument('count_matrix', type=str,
                          help='a count matrix')
    parser_a.add_argument('gene_length_file', type=str,
                          help='gene length file')
    parser_a.add_argument('output_prefix', type=str,
                          help='output prefix')


    # argparse for ContaminationDetector
    parser_a = subparsers.add_parser('ContaminationDetector',
                                     help='find contamination from diamond output: diamond blastp --query Trinity.model.faa --max-target-seqs 10 --db /lustre/home/xuyuxing/Database/NCBI/nr/2020/nr.taxon.dmnd --evalue 1e-5 --out Trinity.model.faa.bls --outfmt 6 qseqid sseqid staxids pident length mismatch gapopen qstart qend sstart send evalue bitscore --threads 56\n'
                                     )

    parser_a.add_argument('bls_results_file', type=str,
                          help='diamond blast output')
    parser_a.add_argument('taxon_db_file', type=str,
                          help='taxon_db_file, from ncbi taxonomy parsed by TaxonTools')
    parser_a.add_argument('target_taxon', type=str,
                          help='can be taxon sciname or taxon id')

    args = parser.parse_args()
    args_dict = vars(args)

    # --------------------------------------------
    # command detail

    # TrinityGene
    if args_dict["subcommand_name"] == "TrinityGene":
        from toolbiox.src.xuyuxing.tools.seqtools import TrinityGene_main
        TrinityGene_main(args)

    # GenerateTrinityGeneTransMap
    elif args_dict["subcommand_name"] == "GenerateTrinityGeneTransMap":
        from toolbiox.src.xuyuxing.tools.seqtools import GenerateTrinityGeneTransMap_main
        GenerateTrinityGeneTransMap_main(args)

    # Denovo2RefCountMap
    elif args_dict["subcommand_name"] == "Denovo2RefCountMap":
        from toolbiox.src.xuyuxing.Transcriptome.Denovo2RefCountMap import Denovo2RefCountMap_main
        Denovo2RefCountMap_main(args)

    # Count2TMM
    elif args_dict["subcommand_name"] == "Count2TMM":
        from toolbiox.src.xuyuxing.Transcriptome.Denovo2RefCountMap import Count2TMM_main
        Count2TMM_main(args)

    # ContaminationDetector
    elif args_dict["subcommand_name"] == "ContaminationDetector":
        from toolbiox.src.xuyuxing.Transcriptome.contamination import detect_contaminate_from_diamond
        detect_contaminate_from_diamond(args.bls_results_file, args.taxon_db_file, args.target_taxon)
