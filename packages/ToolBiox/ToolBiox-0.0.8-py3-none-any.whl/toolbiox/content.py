import argparse

__author__ = 'Yuxing Xu'

def main():

    # argument parse
    parser = argparse.ArgumentParser(
        prog='TransTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for DeepTools
    parser_a = subparsers.add_parser('DeepTools',
                                        help='Extract longest isoform from a gene in trinity output\n',
                                        description='Extract longest isoform from a gene in trinity output')

    args = parser.parse_args()
    args_dict = vars(args)

    # --------------------------------------------
    # command detail

    # TrinityGene
    if args_dict["subcommand_name"] == "DeepTools":
        from DeepTools import main_argparse
        main_argparse()

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


if __name__ == '__main__':
    main()
