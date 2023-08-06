import os

if __name__ == '__main__':
    """
    genome annotation tools:

    MakerPlantRepeat
    MergeMaker
    MakerParser
    MapOldAnno
    GeneStruComp
    WiseAnno
    FamilyAnno
    FunctAnno
    AnnoEval
    """

    import argparse
    import configparser

    # command argument parse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='GenomeAnnotation', description='tools help to get genome annotation more easy\n'
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for MakerPlantRepeat
    parser_a = subparsers.add_parser('MakerPlantRepeat',
                                     help='easy tools for running maker_p full repeat annotation pipeline',
                                     description='rewrite from http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced')

    parser_a.add_argument("-c", "--config_file",
                          help="Path of configure file", type=str)
    parser_a.add_argument("-g", "--genome", help="genome fasta file", type=str)
    parser_a.add_argument(
        "-t", "--tag", help="tag for name, default as genome", default="genome", type=str)
    parser_a.add_argument("-n", "--num_threads",
                          help="num of threads", type=int)
    parser_a.add_argument("-s", "--split_genome",
                          help="split genome to contig to run, defaults will not", action='store_true')
    parser_a.add_argument("-o", "--output_dir",
                          help="path of output_dir, defaults as pwd", type=str)

    # argparse for EasyMaker
    parser_a = subparsers.add_parser('EasyMaker',
                                     help='easy tools for running maker',
                                     description='rewrite from https://weatherby.genetics.utah.edu/MAKER/wiki/index.php/MAKER_Tutorial_for_WGS_Assembly_and_Annotation_Winter_School_2018')

    parser_a.add_argument("-j", "--job", help="what job you want do? (default:first_anno)",
                          default="first_anno", choices=['first_anno', 'to_next_round', 'improve_anno', 'evaluate_anno'])
    parser_a.add_argument("-c", "--config_file",
                          help="Path of configure file", type=str)
    parser_a.add_argument("-g", "--genome_file",
                          help="genome fasta file", type=str)
    parser_a.add_argument(
        "-t", "--tag", help="tag for name, default as genome", type=str)
    parser_a.add_argument("-n", "--num_threads",
                          help="num of threads", type=int)
    parser_a.add_argument("-s", "--split_genome",
                          help="split genome to contig to run, defaults will not", action='store_true')
    parser_a.add_argument("-d", "--work_dir",
                          help="path of output_dir, defaults as maker_dir", default="maker_dir", type=str)

    # argparse for Protein2Genome
    parser_a = subparsers.add_parser('Protein2Genome',
                                     help='get gene structure from homo protein',
                                     description='get gene structure from homo protein')

    parser_a.add_argument('genome_file', type=str,
                          help='Path of target geonome fasta file')
    parser_a.add_argument('protein_fasta', type=str,
                          help='Path of query protein fasta file')
    parser_a.add_argument("-o", "--output_prefix", help="Output prefix name (default as Protein2Genome)",
                          default="Protein2Genome.gff3", type=str)
    parser_a.add_argument("-l", "--log_file",
                          help="path for log file (default as None)", type=str)
    parser_a.add_argument("-t", "--tmp_path", help="path for tmp dir (default in dir which have genome file)",
                          default=None, type=str)
    parser_a.add_argument(
        "-n", "--num_threads", help="cpu number (default as 10)", default=10, type=int)
    parser_a.add_argument("-c", "--gene_coverage", help="lowest gene coverage for genblasta hit use (default as 0.5)",
                          default=0.5, type=float)
    parser_a.add_argument("-a", "--genblasta_hit_num", help="geneblasta hit number (default as 20)", default=20,
                          type=int)
    parser_a.add_argument("-f", "--flank_range", help="flank range for genewise (default as 1000)", default=1000,
                          type=int)

    # argparse for GeneStruComp
    parser_a = subparsers.add_parser('GeneStruComp',
                                     help='Compare two different genetic structure annotations',
                                     description='Compare two different genetic structure annotations')

    parser_a.add_argument("gff_file1", help="gff file 1", type=str)
    parser_a.add_argument("gff_file2", help="gff file 2", type=str)
    parser_a.add_argument("-1", "--gene_list_1", help="List of genes intended for comparison 1, separated by commas",
                          type=str)
    parser_a.add_argument("-2", "--gene_list_2", help="List of genes intended for comparison 2, separated by commas",
                          type=str)

    # argparse for AnnoCleaner
    parser_a = subparsers.add_parser('AnnoCleaner',
                                     help='clean low annotated gene model\n',
                                     description='')

    parser_a.add_argument('gene_gff', type=str,
                          help='Path of genome feature gff file')
    parser_a.add_argument('output_file', type=str, help='Path of output file')
    parser_a.add_argument('-n', '--nr_bls', type=str,
                          help='Path of genes nr blast results outfmt6')
    parser_a.add_argument('-i', '--interpro_tsv', type=str,
                          help='Path of interpro results tsv file')
    parser_a.add_argument('-r', '--repeat_gff_file', type=str,
                          help='Path of repeat feature gff3 file')
    parser_a.add_argument('-e', '--entropy_tsv', type=str,
                          help='Path of entropy_tsv out file')
    parser_a.add_argument('-t', '--tran_evidence_gff', type=str,
                          help='Path of transcriptome map results gff file from pasa and cufflinks')
    parser_a.add_argument('-tt', '--tran_threshold', type=float,
                          help='high than this threshold will be think have rna evidence', default=0.5)
    parser_a.add_argument('-rt', '--repeat_threshold', type=float,
                          help='high than this threshold will be think a repeat range', default=0.5)
    parser_a.add_argument('-et', '--entropy_threshold', type=float,
                          help='small than this threshold will be think a low information sequence', default=3.9)

    # argparse for MapOldAnno
    parser_a = subparsers.add_parser('MapOldAnno',
                                     help='Move annotation results from one assembled version to another')

    parser_a.add_argument("old_genome", help="old genome fasta file", type=str)
    parser_a.add_argument("old_gff", help="old genome gene gff file", type=str)
    parser_a.add_argument("new_genome", help="new genome fasta file", type=str)
    parser_a.add_argument(
        "cDNA_gff", help="blat2gff.pl < Gel.yuan.cDNA.psl > Gel.yuan.cDNA.gff", type=str)
    parser_a.add_argument("output_gff", help="output gff file", type=str)
    parser_a.add_argument(
        "-t", "--tmp_dir", help="path of temp dir", type=str, default=None)
    parser_a.add_argument("-n", "--num_threads",
                          help="number of threads n=10", type=int, default=10)

    # argparse for MergeMaker
    parser_a = subparsers.add_parser('MergeMaker',
                                     help='merge maker output (for genome which split to 1M)')

    parser_a.add_argument(
        "maker_gff1", help="maker output gff (no seq) 1", type=str)
    parser_a.add_argument(
        "maker_gff2", help="maker output gff (no seq) 2", type=str)
    parser_a.add_argument("results_gff", help="merged results gff", type=str)
    parser_a.add_argument("evidence_gff", help="merged evidence gff", type=str)
    parser_a.add_argument(
        "ref_genome", help="reference genome fasta file", type=str)
    parser_a.add_argument(
        "-t", "--tmp_dir", help="path of temp dir", type=str, default=None)
    parser_a.add_argument("-n", "--num_threads",
                          help="cpu numbers", type=int, default=None)

    # argparse for MaskFromMaker
    parser_a = subparsers.add_parser('MaskFromMaker',
                                     help='get masked genome from maker gff file')

    parser_a.add_argument(
        "maker_gff", help="maker output gff (no seq) 1", type=str)
    parser_a.add_argument(
        "ref_genome", help="reference genome fasta file", type=str)
    parser_a.add_argument("masked_ref_genome",
                          help="output masked genome", type=str)
    parser_a.add_argument("-hm", "--hard_mask", help="use hard mask (defaults will running soft mask",
                          action='store_true')

    # argparse for MaskFasta2Gff
    parser_a = subparsers.add_parser('MaskFasta2Gff',
                                     help='get gff file from masked genome fasta file')

    parser_a.add_argument(
        "masked_file", help="masked gff file, N should upper", type=str)
    parser_a.add_argument(
        "output_gff", help="output_gff_file", type=str)

    # argparse for RepeatMasker2Gff3
    parser_a = subparsers.add_parser('RepeatMasker2Gff3',
                                     help='convert repeatmasker out file to gff3')

    parser_a.add_argument(
        "repeatmasker_out", help="repeatmasker out file", type=str)
    parser_a.add_argument(
        "output_gff", help="output_gff_file", type=str)

    # argparse for GeneBank2Gff3
    parser_a = subparsers.add_parser('GeneBank2Gff3',
                                     help='convert GeneBank file to gff3 and fasta file')

    parser_a.add_argument(
        "GeneBank_file", help="genebank file", type=str)
    parser_a.add_argument(
        "output_gff3", help="output_gff3", type=str)

    # argparse for Wise2EVM
    parser_a = subparsers.add_parser('Wise2EVM',
                                     help='convert genewise output gff3 (from xyx output) to EVM need gff3')

    parser_a.add_argument(
        "genewise_gff3", help="path of genewise gff3", type=str)
    parser_a.add_argument(
        "evm_gff3_output", help="path of evm output gff3", type=str)

    # argparse for ProteinByPfam
    parser_a = subparsers.add_parser('ProteinByPfam',
                                     help='give me a genome seq, by hmmscan to get protein seq, dont care stop and frameshift\n',
                                     description='')

    parser_a.add_argument('genome_seq_file', type=str, help='raw genome fasta file')
    parser_a.add_argument("pfam_db_file", help="give me pfam db", type=str)
    parser_a.add_argument("-o", "--output_file", help="output file name, default: *.pfam.aa")
    parser_a.add_argument("-w", "--tmp_work_dir", help="temp work dir, default: ./tmp")
    parser_a.add_argument("-c", "--clean_flag",
                          help="clean temp work dir", action='store_true')
    parser_a.add_argument("-t", "--threads", default=56, type=int)


    # argparse for PseudoGene
    parser_a = subparsers.add_parser('PseudoGene',
                                     help='Get pseudogene from WPGmapper results')
    parser_a.add_argument("WPGmapper_dir",
                          help="Path of WPGmapper dir",
                          type=str)
    parser_a.add_argument("reference_genome_table",
                          help="Path of reference genome table in excel format, must have column \"id\" and \"pt_file\"",
                          type=str)
    parser_a.add_argument("target_genome_fasta",
                          help="Path of target genome fasta file", type=str)
    parser_a.add_argument("known_gene_gff",
                          help="Path of known gene gff file", type=str)
    parser_a.add_argument("OG_tsv_file",
                          help="Path of orthofinder orthogroup tsv file", type=str)
    parser_a.add_argument("output_prefix",
                          help="Path of output prefix", type=str)

    parser_a.add_argument("-c", "--min_cover", help="A valid evidence alignment region needs to account for at least min_cover of the reference gene default=0.5",
                          default=0.5, type=float)
    parser_a.add_argument("-l", "--min_aa_len", help="A valid evidence alignment region needs at least min_aa_len in reference gene default=50",
                          default=50, type=int)
    parser_a.add_argument("-i", "--min_identity", help="A valid evidence alignment region needs at least min_identity in genewise indentity default=0.2",
                          default=0.2, type=float)
    parser_a.add_argument("-e", "--evalue", help="A valid evidence alignment region needs at least max evalue in blastp default=1e-10",
                          default=1e-10, type=float)
    parser_a.add_argument("-s", "--min_score", help="A valid evidence alignment region needs at least min_score in genewise score default=50",
                          default=50, type=int)
    parser_a.add_argument("-og", "--min_OG_support", help="A valid evidence alignment region needs at least query sequence have min_OG_support orthology from orthofinder default=2",
                          default=2, type=int)
    parser_a.add_argument("-cl", "--min_cluster_supp", help="A valid evidence alignment region needs at least min_cluster_supp in jaccord cluster default=2",
                          default=2, type=int)
    parser_a.add_argument("-t", "--threads", default=56, type=int)

    # argparse for AnnotationMerge
    parser_a = subparsers.add_parser('AnnotationMerge',
                                     help='merge function annotation from interpro, nr et al',
                                     description='merge function annotation from interpro, nr')

    parser_a.add_argument('protein_name_list', type=str,
                          help='Path of protein name list')
    parser_a.add_argument("-i", "--interproscan_output_tsv",
                          help="output from: ./interproscan.sh -i Cuscuta/100.seq -f tsv -b Cuscuta/100.seq.out -iprlookup --goterms --pathways -dp",
                          type=str)
    parser_a.add_argument("-n", "--nr_output_xml",
                          help="output from: diamond blastp -q gene_in_case.seq -k 50 -d ~/Database/NCBI/nr/nr -o gene_in_case.nr.bls -f 5 -p 15",
                          type=str)
    parser_a.add_argument(
        "-o", "--output_file", help="the output file (default:phyout)", default=None, type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # MakerPlantRepeat
    if args_dict["subcommand_name"] == "MakerPlantRepeat":
        from toolbiox.api.xuyuxing.genome.maker_p import maker_p_repeat_main
        from toolbiox.lib.common.util import configure_parser

        # configure file argument parse

        """
        class abc():
            pass

        args = abc()
        args.genome = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/repeat2/Gel.genome.v1.0.fasta'
        args.tag = 'Gel'
        args.config_file = None
        args.output_dir = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/repeat2'
        """

        try:
            script_dir_path = os.path.split(os.path.realpath(__file__))[0]
            defaults_config_file = script_dir_path + \
                "/api/xuyuxing/config_file/Maker_p_defaults.ini"
        except:
            defaults_config_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/api/xuyuxing/config_file/Maker_p_defaults.ini"
        # print(defaults_config_file)

        args_type = {

            # Parameter
            "num_threads": "int",

            # Paths
            "genome": "str",
            "tag": "str",
            "trna_file": "str",
            "crl_dir": "str",
            "tpase_dir": "str",
            "pe_dir": "str",
            "old_blastx": "str",
            "protein_db": "str"

        }

        args = configure_parser(
            args, defaults_config_file, args.config_file, args_type, None)

        # Modify_dict parse
        cfg = configparser.ConfigParser()
        if args.config_file is not None:
            cfg.read(args.config_file)

        # if "Modify_dict" in cfg.sections():
        #     args.modify_dict = {}
        #     for key in cfg["Modify_dict"]:
        #         value = cfg["Modify_dict"][key]
        #         args.modify_dict[key] = value

        # output dir
        if args.output_dir is None:
            args.output_dir = os.getcwd()

        maker_p_repeat_main(args)

    # GeneStruComp
    elif args_dict["subcommand_name"] == "GeneStruComp":
        pass

    # MapOldAnno
    elif args_dict["subcommand_name"] == "MapOldAnno":

        """
        blat Gel.genome.v1.0.fasta /dev/null /dev/null -tileSize=11 -makeOoc=11.ooc -repMatch=1024

        blat Gel.genome.v1.0.fasta Gel.yuan.cDNA.fa -q=rna -dots=100  -maxIntron=500000 -out=psl -ooc=11.ooc Gel.yuan.cDNA.psl
        blat Gel.genome.v1.0.fasta Gel.yuan.CDS.fa -q=rna -dots=100  -maxIntron=500000 -out=psl -ooc=11.ooc Gel.yuan.CDS.psl

        blat2gff.pl < Gel.yuan.cDNA.psl > Gel.yuan.cDNA.gff
        blat2gff.pl < Gel.yuan.CDS.psl > Gel.yuan.CDS.gff

        class abc():
            pass

        args = abc()
        args.cDNA_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/Gel.yuan.cDNA.gff"
        args.cDNA_fasta = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/Gel.yuan.cDNA.fa"
        args.old_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/GWHAAEX00000000.rename.gff"
        args.old_genome = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/GWHAAEX00000000.genome.fasta"
        args.new_genome = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/Gel.genome.v1.0.fasta"
        args.tmp_dir = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/tmp"
        args.num_threads = 10
        args.output_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/blat.output.gff"
        """

        from toolbiox.src.xuyuxing.GenomeTools.Gene2Genome import cDNA2Genome_main
        cDNA2Genome_main(args)

    # MergeMaker
    elif args_dict["subcommand_name"] == "MergeMaker":
        """
        class abc():
            pass

        args = abc()
        args.maker_gff1 = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.frag.1.maker.output/Gel.frag.1.all.noseq.gff"
        args.maker_gff2 = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.frag.2.maker.output/Gel.frag.2.all.noseq.gff"
        args.ref_genome = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/Gel.genome.v1.0.fasta"
        args.tmp_dir = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/merge_tmp"
        args.results_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.all.noseq.results.gff"
        args.evidence_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.all.noseq.evidence.gff"
        args.num_threads = 10
        """

        import re
        from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
        from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, ChrLoci, GenomeFeature, cluster_of_chr_loci, write_gff_file
        from toolbiox.lib.xuyuxing.base.base_function import multiprocess_running, mkdir

        def fancy_name_parse(input_string):
            match_obj = re.match(r'^(\S+)_(\d+)-(\d+)$', input_string)
            contig_name, c_start, c_end = match_obj.groups()

            start = min(int(c_start), int(c_end))
            end = max(int(c_start), int(c_end))

            return contig_name, start, end

        def extract_line(input_file, output_prefix, contig_list):
            """
            input_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.frag.1.maker.output/Gel.frag.1.all.noseq.gff'
            output_prefix = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/merge_tmp/maker1_'
            contig_list = chr_list
            """

            # open contig file
            out_handle = {}
            out_file = {}
            for contig in contig_list:
                out_file[contig] = output_prefix + "%s.gff" % contig
                out_handle[contig] = open(out_file[contig], "w")

            # split write
            with open(input_file, 'r') as f:
                for each_line in f:
                    if re.match(r'^#', each_line):
                        continue
                    each_line = re.sub('\n', '', each_line)
                    info = each_line.split("\t")
                    if len(info) > 0:
                        match_list = re.findall(r'^(\S+)_\d+-\d+$', info[0])
                        if len(match_list) > 0:
                            contig = match_list[0]
                            out_handle[contig].write(each_line + "\n")

            # close handle
            for contig in contig_list:
                out_handle[contig].close()

            return out_file

        def coord_shift(give_site, base_site):
            return base_site + give_site - 1

        def feature_coord_shift(feature):
            """
            shift feature coord with contig name
            """
            c_name, c_start, c_end = fancy_name_parse(feature.chr_id)

            new_cl = ChrLoci(chr_id=c_name, strand=feature.strand, start=coord_shift(feature.start, c_start),
                             end=coord_shift(feature.end, c_start))

            new_gf = GenomeFeature(
                id=feature.id, type=feature.type, chr_loci=new_cl)
            new_gf.qualifiers = feature.qualifiers
            new_gf.old_chr_id = feature.chr_id

            # parse sub_feature
            if hasattr(feature, 'sub_features') and (not feature.sub_features is None) and len(
                    feature.sub_features) != 0:
                new_gf.sub_features = []
                for sub_sf in feature.sub_features:
                    new_gf.sub_features.append(feature_coord_shift(sub_sf))

            return new_gf

        def read_maker_gff(maker_gff_file):
            """
            maker_gff_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/merge_tmp/maker2_G031N.gff'
            """
            feature_dict = read_gff_file(maker_gff_file)
            for type_tmp in feature_dict:
                for gf_id in feature_dict[type_tmp]:
                    gf = feature_dict[type_tmp][gf_id]
                    gf_coord_shift = feature_coord_shift(gf)
                    feature_dict[type_tmp][gf_id] = gf_coord_shift

            # change type class to source class
            new_feature_dict = {}
            for type_tmp in feature_dict:
                for gf_id in feature_dict[type_tmp]:
                    gf = feature_dict[type_tmp][gf_id]
                    if 'source' not in gf.qualifiers and gf.type == 'contig':
                        continue
                    source_tmp = gf.qualifiers['source'][0]
                    if source_tmp not in new_feature_dict:
                        new_feature_dict[source_tmp] = {}
                    new_feature_dict[source_tmp][gf_id] = gf

            return new_feature_dict

        def distance_between_boundary_and_cluster(cluster_range, contig_range_fancy_name):
            contig_name, start, end = fancy_name_parse(contig_range_fancy_name)
            mid_site = (cluster_range[1] + cluster_range[0]) / 2
            return min(abs(start - mid_site), abs(end - mid_site))

        def merge_maker_gff(gff1_file, gff2_file):
            """
            gff1_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/merge_tmp/maker1_G031N.gff'
            gff2_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/merge_tmp/maker2_G031N.gff'
            """

            # read gff file and change coord
            # print("read gff file")
            gff1 = read_maker_gff(gff1_file)
            gff2 = read_maker_gff(gff2_file)

            results_source = ['maker', 'augustus_masked',
                              'snap_masked', 'repeatmasker', 'repeatrunner']

            # print("merge results feature: ")
            results_feature_dict = {'maker': {}, 'augustus_masked': {}, 'snap_masked': {}, 'repeatmasker': {},
                                    'repeatrunner': {}}
            for source_tmp in results_source:
                # print(source_tmp)

                huge_gf_list = []

                if source_tmp in gff1:
                    for gf_id in gff1[source_tmp]:
                        huge_gf_list.append(gff1[source_tmp][gf_id])

                if source_tmp in gff2:
                    for gf_id in gff2[source_tmp]:
                        huge_gf_list.append(gff2[source_tmp][gf_id])

                cluster_dict = cluster_of_chr_loci(
                    huge_gf_list, overlap_threshold=0.5)

                for contig_id in cluster_dict:
                    for strand in cluster_dict[contig_id]:
                        for group_id in cluster_dict[contig_id][strand]:
                            cl_range = cluster_dict[contig_id][strand][group_id]['range'][0]
                            gf_in_range = cluster_dict[contig_id][strand][group_id]['list']
                            good_gf = \
                                sorted(gf_in_range,
                                       key=lambda x: distance_between_boundary_and_cluster(
                                           cl_range, x.old_chr_id),
                                       reverse=True)[0]
                            results_feature_dict[source_tmp][good_gf.id] = good_gf

            evidence_source = ['blastn', 'blastx',
                               'est2genome', 'protein2genome']

            # print("merge results feature: ")
            evidence_feature_dict = {'blastn': {}, 'blastx': {
            }, 'est2genome': {}, 'protein2genome': {}}
            for source_tmp in evidence_source:
                # print(source_tmp)

                # grouped by Name
                name_dict = {}

                if source_tmp in gff1:
                    for gf_id in gff1[source_tmp]:
                        gf = gff1[source_tmp][gf_id]
                        evidence_name = gf.qualifiers['Name'][0]
                        if not evidence_name in name_dict:
                            name_dict[evidence_name] = []
                        name_dict[evidence_name].append(gf)

                if source_tmp in gff2:
                    for gf_id in gff2[source_tmp]:
                        gf = gff2[source_tmp][gf_id]
                        evidence_name = gf.qualifiers['Name'][0]
                        if not evidence_name in name_dict:
                            name_dict[evidence_name] = []
                        name_dict[evidence_name].append(gf)

                for evidence_name in name_dict:
                    gf_list = name_dict[evidence_name]
                    cluster_dict = cluster_of_chr_loci(
                        gf_list, overlap_threshold=0.5)

                    for contig_id in cluster_dict:
                        for strand in cluster_dict[contig_id]:
                            for group_id in cluster_dict[contig_id][strand]:
                                cl_range = cluster_dict[contig_id][strand][group_id]['range'][0]
                                gf_in_range = cluster_dict[contig_id][strand][group_id]['list']
                                good_gf = \
                                    sorted(gf_in_range,
                                           key=lambda x: distance_between_boundary_and_cluster(
                                               cl_range, x.old_chr_id),
                                           reverse=True)[0]
                                evidence_feature_dict[source_tmp][good_gf.id] = good_gf

            return results_feature_dict, evidence_feature_dict

        if args.tmp_dir is None:
            args.tmp_dir = os.getcwd() + '/tmp'

        mkdir(args.tmp_dir, True)
        print("tmp dir is : %s" % args.tmp_dir)

        ref_dict = read_fasta_by_faidx(args.ref_genome)
        chr_list = list(ref_dict.keys())

        maker_out = {
            "ID1": {'raw_file': args.maker_gff1, 'split_gff_prefix': args.tmp_dir + "/maker1_"},
            "ID2": {'raw_file': args.maker_gff2, 'split_gff_prefix': args.tmp_dir + "/maker2_"},
        }

        # extract contig line in a tmp file to read
        for id in maker_out:
            maker_out[id]['gff'] = extract_line(
                maker_out[id]['raw_file'], maker_out[id]['split_gff_prefix'], chr_list)

        # merge anno for each contig
        args_list = []
        for contig in chr_list:
            # print(contig)

            gff1_file = maker_out['ID1']['gff'][contig]
            gff2_file = maker_out['ID2']['gff'][contig]

            # results_feature_dict, evidence_feature_dict = merge_maker_gff(gff1_file, gff2_file)
            args_list.append((gff1_file, gff2_file))

        merge_output = multiprocess_running(
            merge_maker_gff, args_list, args.num_threads)

        huge_results_feature_list = []
        huge_evidence_feature_list = []

        for i in merge_output:

            results_feature_dict, evidence_feature_dict = merge_output[i]['output']

            for source_tmp in results_feature_dict:
                for gf_id in results_feature_dict[source_tmp]:
                    gf = results_feature_dict[source_tmp][gf_id]
                    huge_results_feature_list.append(gf)

            for source_tmp in evidence_feature_dict:
                for gf_id in evidence_feature_dict[source_tmp]:
                    gf = evidence_feature_dict[source_tmp][gf_id]
                    huge_evidence_feature_list.append(gf)

        write_gff_file(huge_results_feature_list, args.results_gff)
        write_gff_file(huge_evidence_feature_list, args.evidence_gff)

    # Wise2EVM
    elif args_dict["subcommand_name"] == "Wise2EVM":
        """
        class abc():
            pass

        args = abc()
        args.genewise_gff3 = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/pasa/protein/genewise.gff3"
        args.evm_gff3_output = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/pasa/protein/genewise.evm.gff3"
        """

        from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
        from toolbiox.lib.common.util import printer_list

        gf_dict = read_gff_file(args.genewise_gff3)

        with open(args.evm_gff3_output, 'w') as f:
            for source_tmp in gf_dict:
                for gf_id in gf_dict[source_tmp]:
                    gf = gf_dict[source_tmp][gf_id]
                    mRNA = gf.sub_features[0]
                    target = mRNA.qualifiers['Target'][0]
                    cds_list = mRNA.sub_features

                    cds_list = sorted(cds_list, key=lambda x: int(
                        x.qualifiers['Target_Start'][0]))

                    for cds in cds_list:
                        target_start = int(cds.qualifiers['Target_Start'][0])
                        target_end = int(cds.qualifiers['Target_End'][0])

                        printer_string = printer_list(
                            [mRNA.chr_id, 'genewise', 'match', cds.start, cds.end, '.', cds.strand, '.',
                             'ID=%s;Target=%s %d %d' % (mRNA.id, target, target_start, target_end)])

                        f.write(printer_string + "\n")

    # MaskFromMaker
    elif args_dict["subcommand_name"] == "MaskFromMaker":
        """
        class abc():
            pass

        args = abc()
        args.maker_gff = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.results.gff"
        args.ref_genome = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/Gel.genome.v1.0.fasta"
        args.masked_ref_genome = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.genome.v1.0.masked.fasta"
        args.hard_mask = False
        """

        from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
        from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, BioSeq
        from toolbiox.lib.xuyuxing.math.set_operating import merge_intervals, interval_minus_set

        def get_seq(seq, get_range, mask):
            if mask == 'hard':
                return 'N' * (abs(get_range[1] - get_range[0]) + 1)
            elif mask == 'soft':
                return seq[get_range[0] - 1:get_range[1]].lower()
            else:
                return seq[get_range[0] - 1:get_range[1]].upper()

        def seq_masker(seq, mask_range_list, hard_mask=False):
            """
            seq = 'ATGCATGCATCGTA'
            mask_range_list = [(1,14)]
            hard_mask = False
            """
            if len(mask_range_list) == 0:
                return seq

            all_range = (1, len(seq))
            mask_range_list = merge_intervals(mask_range_list, True)
            unmask_range_list = interval_minus_set(all_range, mask_range_list)
            unmask_range_list = merge_intervals(unmask_range_list, True)

            if hard_mask:
                mask = 'hard'
            else:
                mask = 'soft'

            if len(mask_range_list) == 1 and mask_range_list[0] == all_range:
                return get_seq(seq, mask_range_list[0], mask)

            output_seq = ""

            if mask_range_list[0][0] < unmask_range_list[0][1]:
                for i in range(len(mask_range_list)):
                    output_seq += get_seq(seq, mask_range_list[i], mask)
                    if i <= len(unmask_range_list) - 1:
                        output_seq += get_seq(seq,
                                              unmask_range_list[i], 'no mask')
            else:
                for i in range(len(unmask_range_list)):
                    output_seq += get_seq(seq, unmask_range_list[i], 'no mask')
                    if i <= len(mask_range_list) - 1:
                        output_seq += get_seq(seq, mask_range_list[i], mask)

            return output_seq

        gf_dict = read_gff_file(args.maker_gff)
        genome_dict = read_fasta_by_faidx(args.ref_genome)

        repeat_source = ['repeatmasker', 'repeatrunner']

        repeat_gf_by_contig = {}
        for source_tmp in repeat_source:
            for type_tmp in gf_dict:
                for gf_id in gf_dict[type_tmp]:
                    gf = gf_dict[type_tmp][gf_id]
                    source_tmp = gf.qualifiers['source'][0]
                    if source_tmp not in repeat_source:
                        continue
                    if gf.chr_id not in repeat_gf_by_contig:
                        repeat_gf_by_contig[gf.chr_id] = {}
                    repeat_gf_by_contig[gf.chr_id][gf.id] = gf

        # todo make a repeat genus report

        contig_mask_range_dict = {}
        for contig_id in repeat_gf_by_contig:
            range_list = [repeat_gf_by_contig[contig_id]
                          [gf_id].range for gf_id in repeat_gf_by_contig[contig_id]]
            range_list = merge_intervals(range_list, True)
            contig_mask_range_dict[contig_id] = range_list

        mask_site = 0
        for contig_id in contig_mask_range_dict:
            for range_tmp in contig_mask_range_dict[contig_id]:
                mask_site += abs(range_tmp[1] - range_tmp[0]) + 1

        total_len = 0
        for contig_id in genome_dict:
            contig_seq = genome_dict[contig_id]
            total_len += contig_seq.len()

        print("%d in %d bp (%.2f%%) will be masked" %
              (mask_site, total_len, mask_site / total_len * 100))

        for contig_id in sorted(list(genome_dict.keys())):
            contig_seq = genome_dict[contig_id]
            seq_str = contig_seq.seq.upper()

            if contig_id in contig_mask_range_dict:
                seq_str = seq_masker(
                    seq_str, contig_mask_range_dict[contig_id], hard_mask=args.hard_mask)

            new_contig_seq = BioSeq(seq=seq_str, seqname=contig_seq.seqname)
            # new_contig_seq.wrap()
            new_contig_seq.write_to_file(args.masked_ref_genome)

    # AnnotationMerge
    elif args_dict["subcommand_name"] == "AnnotationMerge":

        import sys
        from toolbiox.api.xuyuxing.file_parser.interproscan_results import interproscan_results_parser
        from toolbiox.api.common.genome.blast import NR_blast_annotation_extractor
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse
        from toolbiox.lib.common.util import printer_list

        """
        class abc():
            pass
        
        args = abc()
        args.protein_name_list = "/lustre/home/xuyuxing/Work/Other/songjuan/gene.list"
        args.interproscan_output_tsv = "/lustre/home/xuyuxing/Work/Other/songjuan/interproscan.out.tsv"
        args.nr_output_xml = "/lustre/home/xuyuxing/Work/Other/songjuan/nr.bls"
        args.output_file = "/lustre/home/xuyuxing/Work/Other/songjuan/gene.anno.txt"
        """

        protein_name_list = args.protein_name_list
        interproscan_output_tsv = args.interproscan_output_tsv
        nr_output_xml = args.nr_output_xml
        output_file = args.output_file

        if not output_file is None:
            F1 = open(output_file, "w")
            sys.stdout = F1

        protein_name_list = list(tsv_file_dict_parse(
            protein_name_list, key_col="ID", fieldnames=["ID"]).keys())
        interpro_dict = interproscan_results_parser(interproscan_output_tsv)
        nr_dict = NR_blast_annotation_extractor(nr_output_xml)

        for i in protein_name_list:
            if i in interpro_dict:
                interpro_anno = [
                    j["Description"] for j in interpro_dict[i].domain_list if j["Analysis"] == "Pfam"]
                interpro_anno = list(set(interpro_anno))
                interpro_anno_txt = printer_list(interpro_anno, ";", "")
                go_anno = []
                for j in interpro_dict[i].domain_list:
                    if not j["GO"] is None and not j['GO'] == '':
                        go_anno.extend(j["GO"].split("|"))
                go_anno = list(set(go_anno))
                go_anno_txt = printer_list(go_anno, ";", "")
            else:
                interpro_anno_txt = ""
            if i in nr_dict:
                nr_anno = nr_dict[i]
                nr_anno = list(set(nr_anno))
                nr_anno_txt = printer_list(nr_anno, ";", "")
            else:
                nr_anno_txt = ""

            print("%s\t%s\t%s\t%s" %
                  (i, interpro_anno_txt, go_anno_txt, nr_anno_txt))

        if not output_file is None:
            F1.close()

    # PseudoGene
    elif args_dict["subcommand_name"] == "PseudoGene":
        from toolbiox.src.xuyuxing.GenomeTools.PseudoGene import pseudogene_main
        pseudogene_main(args)

    # AnnoCleaner
    elif args_dict["subcommand_name"] == "AnnoCleaner":
        from toolbiox.src.xuyuxing.GenomeTools.AnnoCleaner import AnnoCleaner_main
        AnnoCleaner_main(args)

    # EasyMaker
    elif args_dict["subcommand_name"] == "EasyMaker":
        from toolbiox.lib.common.util import configure_parser
        from toolbiox.api.xuyuxing.genome.maker import maker_main

        # configure file argument parse

        """
        class abc():
            pass

        args = abc()
        args.genome = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/repeat2/Gel.genome.v1.0.fasta'
        args.tag = 'Gel'
        args.config_file = None
        args.output_dir = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/repeat2'
        """

        try:
            script_dir_path = os.path.split(os.path.realpath(__file__))[0]
            defaults_config_file = script_dir_path + \
                "/api/xuyuxing/config_file/Maker_defaults.ini"
        except:
            defaults_config_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/api/xuyuxing/config_file/Maker_defaults.ini"
        # print(defaults_config_file)

        args_type = {

            # Parameter
            "num_threads": "int",

            # Paths
            "tag": "str",
            "genome_file": "str",
            "repeat_file": "str",
            "est_file": "str",
            "protein_file": "str",
            "rrna_file": "str",
            "augustus_species": "str",
            "repeat_protein": "str",
            "work_dir": "str",
            "est_gff": "str",
            "protein_gff": "str",
            "rm_gff": "str",
            "snaphmm": "str",
        }

        args = configure_parser(
            args, defaults_config_file, args.config_file, args_type, None)

        # Modify_dict parse
        cfg = configparser.ConfigParser()
        if args.config_file is not None:
            cfg.read(args.config_file)

        # if "Modify_dict" in cfg.sections():
        #     args.modify_dict = {}
        #     for key in cfg["Modify_dict"]:
        #         value = cfg["Modify_dict"][key]
        #         args.modify_dict[key] = value

        args.work_dir = os.path.abspath(args.work_dir)

        # print(vars(args))
        maker_main(args)

    # Protein2Genome
    elif args_dict["subcommand_name"] == "Protein2Genome":
        from toolbiox.src.xuyuxing.GenomeTools.Gene2Genome import Protein2Genome_main
        Protein2Genome_main(args)

    # MaskFasta2Gff
    elif args_dict["subcommand_name"] == "MaskFasta2Gff":
        from toolbiox.src.xuyuxing.GenomeTools.MaskFasta2gff import MaskFasta2Gff_main
        MaskFasta2Gff_main(args)

    # RepeatMasker2Gff3
    elif args_dict["subcommand_name"] == "RepeatMasker2Gff3":
        from toolbiox.src.xuyuxing.GenomeTools.RepeatMasker2Gff3 import RepeatMasker2Gff3_main
        RepeatMasker2Gff3_main(args)

    # GeneBank2Gff3
    elif args_dict["subcommand_name"] == "GeneBank2Gff3":
        from toolbiox.src.xuyuxing.GenomeTools.GeneBank2Gff3 import GeneBank2Gff3_main
        GeneBank2Gff3_main(args)

    # GeneBank2Gff3
    elif args_dict["subcommand_name"] == "ProteinByPfam":
        from toolbiox.src.xuyuxing.GenomeTools.ProteinByPfam import ProteinByPfam_main
        ProteinByPfam_main(args)