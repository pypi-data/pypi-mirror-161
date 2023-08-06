if __name__ == '__main__':
    import argparse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='ResourceTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for RNAseqFromSRA
    parser_a = subparsers.add_parser('RNAseqFromSRA',
                                     help='get RNA seq sra record id from sra database')
    parser_a.add_argument("key_word", help="key_word", type=str)
    parser_a.add_argument(
        "tmp_runinfo_file", help="I will make a tmp file, where can I save it", type=str)
    parser_a.add_argument("output_file", help="path for output_file", type=str)

    # argparse for DownloadGenomeFromNCBI
    parser_a = subparsers.add_parser('DownloadGenomeFromNCBI',
                                     help='get genome sequence from NCBI')
    parser_a.add_argument("list_of_accession_ID",
                          help="give me a list of accession id like GCA_009837245.1", type=str)
    parser_a.add_argument("ncbi_genome_dir", 
                          help="ncbi_genome_dir: dir store ncbi download sequence", type=str)
    parser_a.add_argument("-r", "--assembly_summary_refseq_file", help="assembly_summary_refseq from NCBI, download from ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt (default:in work_dir)", default=None,
                          type=str)
    parser_a.add_argument("-g", "--assembly_summary_genbank_file", help="assembly_summary_genbank from NCBI, download from ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt (default:in work_dir)", default=None,
                          type=str)
    parser_a.add_argument("-t", "--taxonomy_dir",
                          help="taxonomy dump database, download from ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz (default:use value from toolbiox.config file", default=None, type=str)
    parser_a.add_argument("-d", "--download_type",
                          help="what file you want download (default: gff_file,pt_file,cds_file,genome_file)", default=None, type=str)
    parser_a.add_argument("-m", "--renew_md5_flag",
                          help="renew all md5 file", action='store_true')
    parser_a.add_argument("-w", "--download_way", help="what download way you want? (default:wget)",
                          default="wget", choices=['wget', 'ascp'])

    # argparse for ChooseGoodGenomeFromNCBI
    parser_a = subparsers.add_parser('ChooseGoodGenomeFromNCBI',
                                     help='Choose Good Genome From NCBI')
    parser_a.add_argument("ncbi_genome_dir", 
                          help="ncbi_genome_dir: dir store ncbi download sequence", type=str)
    parser_a.add_argument("-r", "--assembly_summary_refseq_file", help="assembly_summary_refseq from NCBI, download from ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt (default:in work_dir)", default=None,
                          type=str)
    parser_a.add_argument("-g", "--assembly_summary_genbank_file", help="assembly_summary_genbank from NCBI, download from ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt (default:in work_dir)", default=None,
                          type=str)
    parser_a.add_argument("-t", "--taxonomy_dir",
                          help="taxonomy dump database, download from ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz (default:use value from toolbiox.config file", default=None, type=str)
    parser_a.add_argument("-tr", "--taxonomic_rank",
                          help=" Compare genomic data between taxonomic_rank classification levels", default='family', type=str)
    parser_a.add_argument("-tt", "--top_taxon",
                          help="The selected genomic source species should all belong to top_taxon", default='Magnoliopsida', type=str)
    parser_a.add_argument("-kr", "--remove_no_rank",
                          help="For those species without taxonomic_rank information in the taxonomic information will deleted (default:False)", action='store_true')
    parser_a.add_argument("-na", "--allow_no_annotation",
                          help="Genomes without annotation information will be allowed to be retained (default:False)", action='store_true')
    parser_a.add_argument("-m", "--renew_md5_flag",
                          help="renew all md5 file", action='store_true')
    parser_a.add_argument("-tn", "--top_num",
                          help="keep top_num genome assemblies in each taxonomic_rank (default:2)", default=2, type=int)
    parser_a.add_argument("-w", "--download_way", help="what download way you want? (default:wget)",
                          default="wget", choices=['wget', 'ascp'])


    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # ccommand detail

    # RNAseqFromSRA
    if args_dict["subcommand_name"] == "RNAseqFromSRA":
        from toolbiox.api.xuyuxing.resource.ncbi_sra import get_rna_seq_from_sra

        sra_dict = get_rna_seq_from_sra(args.key_word, args.tmp_runinfo_file)

        with open(args.output_file, 'w') as f:
            for i in sra_dict:
                f.write(i + "\n")

    # DownloadGenomeFromNCBI
    elif args_dict["subcommand_name"] == "DownloadGenomeFromNCBI":
        from toolbiox.src.xuyuxing.tools.ncbi_tools import ncbi_genome_downloader
        ncbi_genome_downloader(args)

    # ChooseGoodGenomeFromNCBI
    elif args_dict["subcommand_name"] == "ChooseGoodGenomeFromNCBI":
        from toolbiox.src.xuyuxing.tools.ncbi_tools import ncbi_genome_chooser
        ncbi_genome_chooser(args)
