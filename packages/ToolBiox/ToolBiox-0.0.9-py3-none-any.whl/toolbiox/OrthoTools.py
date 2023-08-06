if __name__ == '__main__':
    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='OrthoTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for EasyHcluster
    parser_a = subparsers.add_parser('EasyHcluster',
                                     help='Easy tool for Hcluster pipeline')
    parser_a.add_argument(
        "proteins_dir", help="just like orthofinder input, make all species protein in one dir", type=str)
    parser_a.add_argument("-o", "--work_dir",
                          help="output work dir", type=str, default="hcluster")
    parser_a.add_argument("-t", "--num_threads",
                          help="output file", type=int, default=56)
    parser_a.add_argument("-op", "--option_string",
                          help="option for hcluster, defaults: -m 750 -w 0 -s 0.34 -O", type=str, default="-m 750 -w 0 -s 0.34 -O")

    # argparse for treebestAllGO
    parser_a = subparsers.add_parser('treebestAllGO',
                                     help='TreeBeST pipeline from a orthogroups file')
    parser_a.add_argument(
        "OG_tsv_file", help="orthofinder orthogroups tsv file", type=str)
    parser_a.add_argument(
        "species_info_table", help="species info table excel file, should have: sp_id, OG_species_id, pt_file, cds_file", type=str)
    parser_a.add_argument("SpeciesTree_rooted_file",
                          help="can use orthofinder SpeciesTree_rooted.txt file", type=str)
    parser_a.add_argument("-o", "--work_dir",
                          help="output work dir", type=str, default=".")
    parser_a.add_argument("-t", "--num_threads",
                          help="num_threads", type=int, default=10)

    # argparse for fasttreeAllGO
    parser_a = subparsers.add_parser('fasttreeAllGO',
                                     help='get fasttree for an orthogroups file')
    parser_a.add_argument(
        "OG_tsv_file", help="orthofinder orthogroups tsv file", type=str)
    parser_a.add_argument(
        "species_info_table", help="species info table excel file, should have: sp_id, OG_species_id, pt_file", type=str)
    parser_a.add_argument("-s", "--species_tree",
                          help="can use orthofinder SpeciesTree_rooted.txt file", type=str)
    parser_a.add_argument("-o", "--work_dir",
                          help="output work dir", type=str, default=".")
    parser_a.add_argument("-t", "--num_threads",
                          help="num_threads", type=int, default=10)

    # argparse for GetOrthogroupsFromTreebest
    parser_a = subparsers.add_parser('GetOrthogroupsFromTreebest',
                                     help='get orthologous tsv file from TreeBeST with a given taxonomy level')
    parser_a.add_argument(
        "treebest_work_dir", help="path of treebest work dir", type=str)
    parser_a.add_argument("SpeciesTree_rooted_file",
                          help="can use orthofinder SpeciesTree_rooted.txt file", type=str)
    parser_a.add_argument(
        "taxonomy_level", help="taxonomy level in species tree", type=str)
    parser_a.add_argument(
        "-o", "--output_file", help="path of output file", type=str, default="orthologous.tsv")
    parser_a.add_argument(
        "-k", "--used_OG_list_file", help="give me a OG id list file to use, and skip other OG, if not have file will use all OG in treebest dir", type=str)

    # argparse for GetOrthogenesFromTreebest
    parser_a = subparsers.add_parser('GetOrthogenesFromTreebest',
                                     help='get species pairs orthogenes tsv file from TreeBeST with a given species pair, its will be more good for gene loss, it based on most ')
    parser_a.add_argument(
        "treebest_work_dir", help="path of treebest work dir", type=str)
    parser_a.add_argument("SpeciesTree_rooted_file",
                          help="can use orthofinder SpeciesTree_rooted.txt file", type=str)
    parser_a.add_argument(
        "-o", "--output_file", help="path of output file", type=str, default="orthologous.tsv")

    # argparse for OrthofinderGroup
    parser_a = subparsers.add_parser('OrthofinderGroup',
                                     help='get orthogroups from Orthofinder output')
    parser_a.add_argument(
        "orthologues_dir", help="Path of Orthologues dir from orthofinder output", type=str)
    parser_a.add_argument("output_file", help="Path of output file", type=str)

    # argparse for Orthologues pair
    parser_a = subparsers.add_parser('OrthoPair',
                                     help='Orthologues pair')
    parser_a.add_argument(
        "orthologues_tsv", help="orthologues tsv file", type=str)
    parser_a.add_argument("species1", help="species1", type=str)
    parser_a.add_argument("-sp2", "--species2", help="species2", type=str)
    parser_a.add_argument("output_file", help="output file", type=str)

    # argparse for mcscanxGO
    parser_a = subparsers.add_parser('mcscanxGO',
                                     help='Running MCScanX')
    parser_a.add_argument("sp1_gff", help="species1 gff3 file", type=str)
    parser_a.add_argument("-sp2_gff", "--sp2_gff",
                          help="species2 gff3 file", type=str)
    parser_a.add_argument("-sp1", "--sp1_prefix",
                          help="species 1 prefix in mcscanx running", default="aa", type=str)
    parser_a.add_argument("-sp2", "--sp2_prefix",
                          help="species 2 prefix in mcscanx running", default="bb", type=str)
    parser_a.add_argument("-sp1_aa", "--sp1_aa_fasta",
                          help="species 1 protein fasta file", type=str)
    parser_a.add_argument("-sp2_aa", "--sp2_aa_fasta",
                          help="species 2 protein fasta file", type=str)
    parser_a.add_argument("-bls", "--blast_results_file",
                          help="blast results file", type=str)
    parser_a.add_argument("-s", "--skip_gene_list_file",
                          help="skip gene list file", type=str)
    parser_a.add_argument("-w", "--work_dir",
                          help="work dir defaults .", default=".", type=str)
    parser_a.add_argument("-o", "--mcscanx_options",
                          help="mcscanx options defaults: '-k 50 -g -1 -s 5 -e 1e-30 -m 25' ", default="-k 50 -g -1 -s 5 -e 1e-30 -m 25", type=str)
    parser_a.add_argument("-c", "--c_score_threshold",
                          help="c_score_threshold defaults: 0", default=0, type=float)

    # argparse for mcscanxhGO
    parser_a = subparsers.add_parser('mcscanxhGO',
                                     help='Running MCScanX_h')
    parser_a.add_argument("sp1_gff", help="species1 gff3 file", type=str)
    parser_a.add_argument(
        "orthologues_tsv", help="orthologues tsv file", type=str)
    parser_a.add_argument("-sp2_gff", "--sp2_gff",
                          help="species2 gff3 file", type=str)
    parser_a.add_argument("-sp1", "--sp1_prefix",
                          help="species 1 prefix in mcscanx running", default="aa", type=str)
    parser_a.add_argument("-sp2", "--sp2_prefix",
                          help="species 2 prefix in mcscanx running", default="bb", type=str)
    parser_a.add_argument("-w", "--work_dir",
                          help="work dir defaults .", default=".", type=str)
    parser_a.add_argument("-f", "--huge_gene_family_filter",
                          help="filter huge gene family, for self comparion", default=50, type=int)
    parser_a.add_argument("-o", "--mcscanx_options",
                          help="mcscanx options defaults: '-k 30 -g 0 -s 5 -e 1e-05 -m 25' ", default="-k 30 -g 0 -s 5 -e 1e-05 -m 25", type=str)

    # argparse for ConvertCollinearity
    parser_a = subparsers.add_parser('ConvertCollinearity',
                                     help='Convert Collinearity File to csv')
    parser_a.add_argument("query_id", help="query id", type=str)
    parser_a.add_argument("query_gff", help="query gff file", type=str)
    parser_a.add_argument("subject_id", help="subject id", type=str)
    parser_a.add_argument("subject_gff", help="subject gff file", type=str)
    parser_a.add_argument("mcscanx_collinearity_file",
                          help="mcscanx_collinearity_file", type=str)
    parser_a.add_argument("csv_file", help="csv_file", type=str)

    # argparse for countWGD
    parser_a = subparsers.add_parser('countWGD',
                                     help='count WGD from mcscanx.collinearity')
    parser_a.add_argument("sp1", help="sp1_prefix", type=str)
    parser_a.add_argument("sp2", help="sp2_prefix", type=str)
    parser_a.add_argument("sp1_gff", help="species1 gff3 file", type=str)
    parser_a.add_argument("sp2_gff", help="species2 gff3 file", type=str)
    parser_a.add_argument("mcscanx_collinearity_file",
                          help="path of mcscanx_collinearity_file", type=str)
    parser_a.add_argument("-o", "--OG_tsv_file",
                          help="path of OG_tsv_file", type=str)
    parser_a.add_argument("-t", "--OG_filter",
                          help="OG_filter threshold", default=0.3, type=float)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    if args_dict["subcommand_name"] == "OrthofinderGroup":
        # pre
        """
        class abc(object):
            pass

        args = abc()
        args.orthologues_dir = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Aof/orthofinder2/OrthoFinder/Results_Nov21/Orthologues'
        args.output_file = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Aof/orthofinder2/OrthoFinder/Results_Nov21/Orthologues/Orthologues.tsv'
        """

        from toolbiox.api.xuyuxing.comp_genome.orthofinder import get_orthologues
        get_orthologues(args.orthologues_dir, args.output_file)

    elif args_dict["subcommand_name"] == "OrthoPair":
        from toolbiox.api.xuyuxing.comp_genome.orthofinder import tsv_to_gene_pair
        tsv_to_gene_pair(args.orthologues_tsv, args.species1,
                         args.species2, args.output_file)

    elif args_dict["subcommand_name"] == "mcscanxGO":

        from toolbiox.api.xuyuxing.comp_genome.mcscan import running_mcscanx
        from toolbiox.lib.common.fileIO import read_list_file
        import os

        work_dir = os.path.abspath(args.work_dir)
        if args.skip_gene_list_file:
            skip_gene_list = read_list_file(args.skip_gene_list_file)
        else:
            skip_gene_list = []

        if not args.sp2_gff is None:
            running_mcscanx(args.sp1_gff, args.sp2_gff, work_dir, species1_prefix=args.sp1_prefix, species1_aa_fasta=args.sp1_aa_fasta,
                            species2_prefix=args.sp2_prefix, species2_aa_fasta=args.sp2_aa_fasta, skip_gene_list=skip_gene_list, give_bls_file=args.blast_results_file, mcscanx_options=args.mcscanx_options, c_score_threshold=args.c_score_threshold)
        else:
            running_mcscanx(args.sp1_gff, None, work_dir, species1_prefix=args.sp1_prefix, species1_aa_fasta=args.sp1_aa_fasta,
                            species2_prefix=None, species2_aa_fasta=None, skip_gene_list=skip_gene_list, give_bls_file=args.blast_results_file, mcscanx_options=args.mcscanx_options + " -b 1", c_score_threshold=args.c_score_threshold)

    elif args_dict["subcommand_name"] == "mcscanxhGO":

        from toolbiox.api.xuyuxing.comp_genome.mcscan import running_mcscanxh
        import os

        work_dir = os.path.abspath(args.work_dir)

        if not args.sp2_gff is None:
            running_mcscanxh(args.sp1_gff, args.sp2_gff, args.orthologues_tsv, work_dir,
                             species1_prefix=args.sp1_prefix, species2_prefix=args.sp2_prefix, mcscanx_options=args.mcscanx_options)
        else:
            running_mcscanxh(args.sp1_gff, None, args.orthologues_tsv, work_dir, species1_prefix=args.sp1_prefix,
                             species2_prefix=None, mcscanx_options=args.mcscanx_options + " -b 1", huge_gene_family_filter=args.huge_gene_family_filter)

    elif args_dict["subcommand_name"] == "treebestGO":
        pass

    elif args_dict["subcommand_name"] == "treebestAllGO":
        from toolbiox.api.xuyuxing.comp_genome.treebest import treebest_many
        treebest_many(args.OG_tsv_file, args.species_info_table,
                      args.SpeciesTree_rooted_file, args.work_dir, args.num_threads)

    elif args_dict["subcommand_name"] == "fasttreeAllGO":
        from toolbiox.api.xuyuxing.comp_genome.fasttree import fasttree_many
        from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
        from toolbiox.lib.common.evolution.tree_operate import get_root_by_species, add_clade_name, lookup_by_names
        from Bio import Phylo

        OGs = OrthoGroups(OG_tsv_file=args.OG_tsv_file)
        species_info_dict = read_species_info(args.species_info_table)

        fasttree_many(OGs, species_info_dict, args.work_dir, args.num_threads)

        if args.species_tree:
            species_tree = Phylo.read(args.species_tree, 'newick')
            species_tree = add_clade_name(species_tree)
            species_tree_dict = lookup_by_names(species_tree)

        get_root_by_species

        get_root_by_species(gene_tree, species_rooted_tree,
                            gene_to_species_map)

    elif args_dict["subcommand_name"] == "countWGD":
        from toolbiox.api.xuyuxing.comp_genome.mcscan import WGD_check_pipeline
        from collections import Counter

        if args.sp1 == sorted([args.sp1, args.sp2])[0]:
            q = args.sp1
            s = args.sp2
            q_gff = args.sp1_gff
            s_gff = args.sp2_gff
        else:
            q = args.sp2
            s = args.sp1
            q_gff = args.sp2_gff
            s_gff = args.sp1_gff

        q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = WGD_check_pipeline(
            args.mcscanx_collinearity_file, q, q_gff, None, s, s_gff, None)

        print(args.sp2+": ")
        print(Counter([q_gene_covered_dict[i] for i in q_gene_covered_dict]))

        print(args.sp1+": ")
        print(Counter([s_gene_covered_dict[i] for i in s_gene_covered_dict]))

    elif args_dict["subcommand_name"] == "GetOrthogroupsFromTreebest":
        from toolbiox.api.xuyuxing.comp_genome.treebest import get_orthologous_from_treebest
        from toolbiox.lib.common.evolution.orthotools2 import write_OG_tsv_file
        from toolbiox.lib.common.fileIO import read_list_file

        if args.used_OG_list_file:
            used_OG_list = read_list_file(args.used_OG_list_file)
        else:
            used_OG_list = None

        OL_dict = get_orthologous_from_treebest(
            args.treebest_work_dir, args.SpeciesTree_rooted_file, taxonomy_level=args.taxonomy_level, used_OG_list=used_OG_list)

        write_OG_tsv_file(OL_dict, args.output_file)

    elif args_dict["subcommand_name"] == "ConvertCollinearity":
        from toolbiox.api.xuyuxing.comp_genome.mcscan import collinearity_file_to_synteny_block_range_csv
        collinearity_file_to_synteny_block_range_csv(
            args.query_id, args.query_gff, args.subject_id, args.subject_gff, args.mcscanx_collinearity_file, args.csv_file)

    elif args_dict["subcommand_name"] == "EasyHcluster":
        from toolbiox.src.xuyuxing.OrthoTools.EasyHcluster import hcluster_pipeline
        hcluster_pipeline(args.proteins_dir, args.work_dir,
                          args.num_threads, args.option_string)
