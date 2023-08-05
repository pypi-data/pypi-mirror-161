if __name__ == '__main__':
    import argparse
    import textwrap

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='GenCompare',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for BuildScaffoldDir
    parser_a = subparsers.add_parser('BuildScaffoldDir',
                                     help='build a dir to store scaffold orthogroups for other analysis\n',
                                     description='')

    parser_a.add_argument('orthogroups_file', type=str,
                          help='path of orthogroups tsv file')
    parser_a.add_argument('species_info_file', type=str,
                          help='species_info_file need have sp_id, cds_file and pt_file')
    parser_a.add_argument('scaffold_dir', type=str, help='output scaffold dir')
    parser_a.add_argument("-t", "--num_threads",
                          help="thread number (default as 1)", default=1, type=int)
    parser_a.add_argument("-g", "--min_gene_number",
                          help="min_gene_number (default as 4)", default=4, type=int)
    parser_a.add_argument("-s", "--min_species_number",
                          help="min_species_number (default as 2)", default=2, type=int)

    # argparse for SeqClassify
    parser_a = subparsers.add_parser('SeqClassify',
                                     help='map genome proteins to builded gene family\n',
                                     description='')

    parser_a.add_argument('input_fasta', type=str,
                          help='input genome.protein.fasta file')
    parser_a.add_argument('scaffold_dir', type=str,
                          help='dir from BuildScaffoldDir')
    parser_a.add_argument('output_file', type=str, help='output dir')
    parser_a.add_argument("-w", "--work_dir",
                          help="work dir for tmp (default as tmp)", default=None, type=str)
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 1)", default=1, type=int)
    parser_a.add_argument("-s", "--strict",
                          help="strict flag: will use msa and pvalue to check False positive", action='store_true')


    # argparse for TransDeepAssembly
    parser_a = subparsers.add_parser('TransDeepAssembly',
                                     help='map transcriptome assemblies to builded orthogroup, and re-assemble, from AssemblyPostProcessor in PlantTribes\n',
                                     description='')

    parser_a.add_argument('input_fasta', type=str,
                          help='input Trinity.fasta file')
    parser_a.add_argument('output_dir', type=str, help='output dir')
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 1)", default=1, type=int)

    # argparse for FamMapStats
    parser_a = subparsers.add_parser('FamMapStats',
                                     help='check how many orthogroup can get good hit\n',
                                     description='')

    parser_a.add_argument('family_dir', type=str,
                          help='family dir from TransDeepAssembly or MapGenomeToOrthoGroups')
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 56)", default=56, type=int)

    # argparse for GetSkipFile
    parser_a = subparsers.add_parser('GetSkipFile',
                                     help='get skip file for WPGmapper')
    parser_a.add_argument(
        "gff_file", help="gene gff file", type=str)
    parser_a.add_argument(
        "repeatmasker_out", help="repeatmasker output file", type=str)
    parser_a.add_argument(
        "output_file", help="output skip file", type=str)

    # argparse for WPGmapper
    parser_a = subparsers.add_parser('WPGmapper',
                                     help='Wide Proteins To Genome Maper (genblasta and genewise)')
    parser_a.add_argument("reference_genome_table",
                          help="Path of reference genome table in excel format, must have column \"id\" and \"pt_file\"",
                          type=str)
    parser_a.add_argument("target_genome_fasta",
                          help="Path of target genome fasta file", type=str)
    parser_a.add_argument("-skip", "--skip_range_file",
                          help="Path of skip_range_file, tsv file chr start end", type=str)
    parser_a.add_argument("-d", "--work_dir", help="Path of work dir (default as ./WPG_working)",
                          default="./WPG_working", type=str)
    parser_a.add_argument(
        "-t", "--num_threads", help="threads number (default as 5)", default=5, type=int)
    parser_a.add_argument("-c", "--gene_coverage",
                          help="gene coverage (default as 0.2)", default=0.2, type=float)
    parser_a.add_argument("-n", "--genblasta_hit_num",
                          help="genblasta hit num (default as 100)", default=100, type=int)
    parser_a.add_argument("-a", "--annotated_coverage", help="annotated_coverage (default as 0.8)", default=0.8,
                          type=float)
    parser_a.add_argument("-s", "--split_seq_num", help="split big fasta file to run (default as 1000)", default=1000,
                          type=int)
    parser_a.add_argument("-r", "--force_redo",
                          help="force redo all job", action='store_true')

    # argparse for GeneLoss
    parser_a = subparsers.add_parser('GeneLoss',
                                     help='Parse gene loss from a orthofinder results, with tree check')

    parser_a.add_argument(
        "config_file", help="Path of configure file", type=str)
    parser_a.add_argument(
        "--ortho_level", help="ortho_level: orthogroups or orthologues (default:orthologues)")
    parser_a.add_argument("--num_threads", help="number of threads", type=int)
    parser_a.add_argument("--log_file", help="path of log file", type=str)
    parser_a.add_argument("--output_dir", help="path of output dir", type=str)

    # argparse for GeneLoss2
    parser_a = subparsers.add_parser('GeneLoss2',
                                     help='Parse gene loss from a given orthogroups file, check by scaffold dir')

    parser_a.add_argument(
        "--config_file", help="Path of configure file", type=str)
    parser_a.add_argument("--orthogroup_scaffold_dir",
                          help="orthogroup_scaffold_dir from BuildScaffoldDir", type=str)
    parser_a.add_argument(
        "--wpgmapper_dir", help="wpgmapper_dir from WPGmapper", type=str)
    parser_a.add_argument(
        "--target_speci", help="species id for target species", type=str)
    parser_a.add_argument("--target_speci_annotation",
                          help="target species gff file", type=str)
    parser_a.add_argument(
        "--conserved_species", help="set species need for defend conserved orthogroups, like: Ath;Ini;Llu;Cca,Sly,Oeu,Sin,Mgu,3", type=str)
    parser_a.add_argument("--work_dir", help="output dir", type=str)
    parser_a.add_argument("--log_file", help="log file", type=str)

    parser_a.add_argument(
        "--num_threads", help="number of threads default=56", type=int, default=56)
    parser_a.add_argument(
        "--top_evidence_num", help="use top_evidence_num evidences for a ref gene default=20", type=int, default=20)
    parser_a.add_argument(
        "--min_cover", help="min coverage default=0.5", type=float, default=0.5)
    parser_a.add_argument(
        "--min_aa_len", help="min protein length default=20", type=int, default=20)
    parser_a.add_argument(
        "--min_identity", help="min_identity default=0.3", type=float, default=0.3)
    parser_a.add_argument("--min_score", help="min_score default=50.0",
                          type=float, default=50.0)
    parser_a.add_argument("--target_speci_feature",
                          help="target_speci_feature in gff file default=gene", type=str, default='gene')
    parser_a.add_argument("--annotated_coverage",
                          help="annotated_coverage default=0.8", type=float, default=0.8)

    # argparse for GeneFamilyStat
    parser_a = subparsers.add_parser('GeneFamilyStat',
                                     help='parse gene family count file to get gene family expansion and contraction')

    parser_a.add_argument('orthogroups_genecount_tsv', type=str,
                          help='path of Orthogroups_GeneCount_tsv from orthofinder')
    parser_a.add_argument('species_tree', type=str,
                          help='a species tree file in newick')
    parser_a.add_argument('species_name_list', type=str,
                          help='a species name list, seq by \",\"')
    parser_a.add_argument('conserved_species_name_list', type=str,
                          help='a conserved species name list, seq by \",\"')
    parser_a.add_argument('work_dir', type=str, help='temp working dir')
    parser_a.add_argument('output_prefix', type=str, help='output_prefix')
    parser_a.add_argument("-t", "--threads", default=56, type=int)
    parser_a.add_argument('-l', '--just_load',
                          help='just_load', action='store_true')

    # argparse for EasyBadiRate
    parser_a = subparsers.add_parser('EasyBadiRate',
                                     help='Parse one gene family expansion or contraction')

    parser_a.add_argument('tag', type=str, help='a tag for this family')
    parser_a.add_argument('tree_file', type=str,
                          help='a species tree file in newick')
    parser_a.add_argument('size_tsv_file', type=str,
                          help='a gene family size file in tsv file')
    parser_a.add_argument('-l', '--label_tree', type=str,
                          help='output a labeled tree from BadiRate', default=None)
    parser_a.add_argument('-k', '--keep_tmp_dir',
                          help='keep temp running dir', action='store_true')

    # argparse for hWGDdetector
    parser_a = subparsers.add_parser('hWGDdetector',
                                     help='Detect hidden WGD in many species')

    parser_a.add_argument('sp_info_excel', type=str, help='must have sp_id (same as OG_tsv_file), pt_file, cds_file (for treebset), gff_file, genome_file (for dotplot)')
    parser_a.add_argument('sp_tree_file', type=str,
                          help='a species tree file in newick, each node should have name, branch length can be ignored')
    parser_a.add_argument('OG_tsv_file', type=str,
                          help='Orthogroups file from orthofinder')
    parser_a.add_argument('-w', '--work_dir', type=str, help='work dir', default='hWGDdetector_dir')
    parser_a.add_argument('-n', '--huge_OG_gene_num', type=int,
                          help='orthogroup with single species have gene more than h will be ignored', default=20)
    parser_a.add_argument('-t', '--threads',
                          help='number of threads', type=int, default=56)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # BuildScaffoldDir
    if args_dict["subcommand_name"] == "BuildScaffoldDir":
        from toolbiox.api.xuyuxing.comp_genome.planttribes2 import build_scaffold_main
        build_scaffold_main(args)

    # SeqClassify
    elif args_dict["subcommand_name"] == "SeqClassify":
        from toolbiox.api.xuyuxing.comp_genome.planttribes2 import seq_classify_main
        seq_classify_main(args)

    # TransDeepAssembly
    elif args_dict["subcommand_name"] == "TransDeepAssembly":
        from toolbiox.api.xuyuxing.comp_genome.planttribes import targeted_gene_family_assembly
        targeted_gene_family_assembly(args)

    # GetDeepAssemblyStats
    elif args_dict["subcommand_name"] == "GetDeepAssemblyStats":
        from toolbiox.api.xuyuxing.comp_genome.planttribes import GetDeepAssemblyStats_main
        GetDeepAssemblyStats_main(args)

    # EasyBadiRate
    elif args_dict["subcommand_name"] == "EasyBadiRate":
        import os
        import uuid
        from toolbiox.config import badirate_path
        from toolbiox.api.xuyuxing.evolution.badirate import main_pipeline

        main_pipeline(args.tag, args.size_tsv_file, args.tree_file, "/tmp/" +
                      uuid.uuid1().hex, badirate_path, args.label_tree, args.keep_tmp_dir)

    # GeneLoss
    elif args_dict["subcommand_name"] == "GeneLoss":
        from toolbiox.src.xuyuxing.GenomeTools.GeneLoss import GeneLoss_args_parser
        GeneLoss_args_parser(args)

    # GeneLoss2
    elif args_dict["subcommand_name"] == "GeneLoss2":
        from toolbiox.src.xuyuxing.GenomeTools.GeneLoss2 import GeneLoss_args_parser
        GeneLoss_args_parser(args)

    # GeneFamilyStat
    elif args_dict["subcommand_name"] == "GeneFamilyStat":
        from toolbiox.src.xuyuxing.GenomeTools.GeneFamily import gene_family_stat_main

        gene_family_stat_main(args.orthogroups_genecount_tsv, args.species_tree, args.species_name_list.split(
            ","), args.conserved_species_name_list.split(","), args.work_dir, args.threads, args.work_dir+"/log", args.output_prefix, args.just_load)

    # WideProteinToGenomeMaper
    elif args_dict["subcommand_name"] == "WPGmapper":
        from toolbiox.src.xuyuxing.GenomeTools.WPGmapper import build_WPGmapper
        build_WPGmapper(args)

    # GetSkipFile
    elif args_dict["subcommand_name"] == "GetSkipFile":
        from toolbiox.src.xuyuxing.GenomeTools.WPGmapper import get_skip_file
        get_skip_file(args.gff_file, args.repeatmasker_out, args.output_file)

    # hWGDdetector
    elif args_dict["subcommand_name"] == "hWGDdetector":
        from toolbiox.src.xuyuxing.GenomeTools.hWGDdetector import hWGDdetector_main
        args.log_file = args.work_dir + "/log"
        hWGDdetector_main(args)
