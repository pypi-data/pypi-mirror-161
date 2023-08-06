if __name__ == '__main__':
    import argparse
    import textwrap

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='GenomeTools',
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for GenomeSurvey
    parser_a = subparsers.add_parser('GenomeSurvey',
                                     help='easy tools for Genome Survey\n',
                                     description='')

    parser_a.add_argument(
        "genome_size", help="Estimated genome size (based on bp), such as 100000000", type=int)
    parser_a.add_argument("genome_coverage",
                          help="coverage of sequence data of estimated genome size (based on bp), such as 40", type=int)
    parser_a.add_argument(
        "input_file_list", help="a list file containing all fastq file path of input", type=str)
    parser_a.add_argument(
        "-k", "--kmer", help="k-mer for survey (default as 17)", default=17, type=int)
    parser_a.add_argument("-c", "--min_accuracy_rate",
                          help="set min accuracy rate of k-mer, set between 0~0.99, or -1 for unrestrained (default as 0.99)",
                          default=0.99, type=float)
    parser_a.add_argument("-q", "--quality_value",
                          help="set Quality value ascii shift, generally 64 or 33, (default as 33)", default=33,
                          type=int)
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 1)", default=1, type=int)
    parser_a.add_argument("-p", "--output_prefix", help="set output prefix (default as output)", default="output",
                          type=str)
    parser_a.add_argument("-o", "--output_kmer_frequence_file",
                          help="set whether ouput k-mer frequence file, 0 for no, 1 for yes, default as 0", default=0,
                          type=int)
    parser_a.add_argument("-L", "--maximum_read_length",
                          help="maximum read length, default=150", default=150, type=int)
    parser_a.add_argument("-a", "--begin_ignore_len",
                          help="ignored length of the beginning of a read, default=0", default=0, type=int)
    parser_a.add_argument("-d", "--end_ignore_len",
                          help="ignored length of the end of a read, default=0", default=0, type=int)
    parser_a.add_argument("-print", "--print_info",
                          help="just print parameters for process not running", action='store_true')

    # argparse for AssemblyEvaluator
    parser_a = subparsers.add_parser('AssemblyEvaluator',
                                     help='make a report for assembly accurate by map NGS data\n',
                                     description='')

    parser_a.add_argument('target_assembly_fasta',
                          type=str, help='a fasta file')
    parser_a.add_argument('ngs_1', type=str, help='NGS fastq 1')
    parser_a.add_argument('ngs_2', type=str, help='NGS fastq 2')
    parser_a.add_argument('-o', '--output_file', type=str,
                          help='output file (default: AssemblyEvaluator.txt)', default='AssemblyEvaluator.txt')
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 1)", default=1, type=int)
    parser_a.add_argument("-d", "--tmp_dir",
                          help="tmp dir for working", default="./", type=str)

    # argparse for ContigDepth
    parser_a = subparsers.add_parser('ContigDepth',
                                     help='get average depth and coverage for each contig\n',
                                     description='')

    parser_a.add_argument('bam_file', type=str, help='sorted bam file')
    parser_a.add_argument('ref_genome', type=str,
                          help='reference genome fasta file')
    parser_a.add_argument(
        "-o", "--output_file", help="the output file (default:ContigDepth.txt)", default="ContigDepth.txt", type=str)

    # argparse for ContaminationFilter
    parser_a = subparsers.add_parser('ContaminationFilter',
                                     help='find contamination contig from genome assembly\n',
                                     description='')

    parser_a.add_argument('split_genome_fasta', type=str,
                          help='blast from organelle hit')
    parser_a.add_argument('taxon_assign_output', type=str,
                          help='survey genome depth results')
    parser_a.add_argument('tax_dir', type=str,
                          help='ncbi taxonomy dir')
    parser_a.add_argument('output_file', type=str, help='output file')

    # argparse for ContigFilter
    parser_a = subparsers.add_parser('ContigFilter',
                                     help='find organelle contig from genome assembly\n',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                    example:
                                    -----------------------------------------------
                                    all in one:   
                                    ContigFilter -t 56 -c related_chl_genome.fasta -m related_mit_genome.fasta -g genome.fasta -1 GSS_1.fq.gz -2 GSS_2.fq.gz
                                    
                                    use given rRNA seq
                                    ContigFilter -t 56 -c related_chl_genome.fasta -m related_mit_genome.fasta -r rRNA.unit.seq -g genome.fasta -1 GSS_1.fq.gz -2 GSS_2.fq.gz

                                    use given depth report
                                    ContigFilter -t 56 -c related_chl_genome.fasta -m related_mit_genome.fasta -r rRNA.unit.seq -g genome.fasta -d ContigDepth.txt

                                    use given contamination report
                                    ContigFilter -t 56 -c related_chl_genome.fasta -m related_mit_genome.fasta -r rRNA.unit.seq -g genome.fasta -d ContigDepth.txt

                                    just make plot
                                    ContigFilter -f ContigFilter.txt

                                    '''))

    parser_a.add_argument('-g', '--genome_input_fasta', type=str,
                          help='contig genome fasta file')
    parser_a.add_argument('-1', '--GSS_fq1', type=str,
                          help='genome survey sequence fastq1 file, to get depth value')
    parser_a.add_argument('-2', '--GSS_fq2', type=str,
                          help='genome survey sequence fastq2 file, to get depth value')
    parser_a.add_argument("-t", "--threads",
                          help="thread number (default as 1)", default=1, type=int)
    parser_a.add_argument('-c', '--related_chl_genome', type=str, help='give me a relative species chloroplast genome fasta file. (default: None)',
                          default=None)
    parser_a.add_argument('-m', '--related_mit_genome', type=str, help='give me a relative species mitochondrion genome fasta file. (default: None)',
                          default=None)
    parser_a.add_argument('-r', '--related_nrRNA_seq', type=str, help='give me a relative species nuclear rRNA fasta (unit seq) file. (default: None, will annotated from Ath)',
                          default=None)
    parser_a.add_argument('-d', '--depth_results', type=str, help='give me a results file from ContigDepth',
                          default=None)
    parser_a.add_argument('-p', '--contamination_report', type=str, help='give me a results file from ContaminationFilter',
                          default=None)
    parser_a.add_argument('-f', '--contig_filter_results', type=str, help='give me a results file from ContigFilter, just plot now',
                          default=None)
    parser_a.add_argument('-o', '--work_dir', type=str, help='output dir. (default: ContigFilter)',
                          default='ContigFilter')

    # argparse for FilterAssemblyFile
    parser_a = subparsers.add_parser('FilterAssemblyFile',
                                     help='only keep some contig fragments from assembly file (from juicer)\n',
                                     description='')

    parser_a.add_argument('assembly', type=str, help='assembly file')
    parser_a.add_argument('contig_list', type=str,
                          help='file containing the name of the contig to be keeped')
    parser_a.add_argument('-o', '--output_file', type=str, help='output file (default: new_assembly.txt)',
                          default='new_assembly.txt')

    # argparse for HiC2Fasta
    parser_a = subparsers.add_parser('HiC2Fasta',
                                     help='get chromesome fasta from assembly file (from juicer)\n',
                                     description='')

    parser_a.add_argument('final_fasta', type=str,
                          help='final fasta from 3d-dna, which have contig fragment fasta')
    parser_a.add_argument('assembly', type=str, help='assembly file')
    parser_a.add_argument('output_fasta', type=str, help='output fasta file')

    # argparse for MergeUnanchored
    parser_a = subparsers.add_parser('MergeUnanchored',
                                     help='merge unanchored sequence in a fasta file\n',
                                     description='')

    parser_a.add_argument('merge_info', type=str,
                          help='merge information in a tsv file: 1st col: merged id (chr1), 2ed col: raw id (seq1,seq2,seq3)')
    parser_a.add_argument('input_fasta', type=str, help='input fasta file')
    parser_a.add_argument('output_fasta', type=str, help='output fasta file')

    # argparse for EasyAssemblyPostProcessor
    parser_a = subparsers.add_parser('EasyAssemblyPostProcessor',
                                     help='Easy to use AssemblyPostProcessor tool from PlantTribes\n',
                                     description='')

    parser_a.add_argument('input_fasta', type=str, help='input Trinity.fasta file')
    parser_a.add_argument('output_dir', type=str, help='output dir')
    parser_a.add_argument("-t", "--thread_number",
                          help="thread number (default as 1)", default=1, type=int)



    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # GenomeSurvey
    if args_dict["subcommand_name"] == "GenomeSurvey":
        from toolbiox.src.xuyuxing.GenomeTools.GenomeSurvey import GenomeSurvey_main
        GenomeSurvey_main(args)

    # AssemblyEvaluator
    elif args_dict["subcommand_name"] == "AssemblyEvaluator":
        from toolbiox.src.xuyuxing.GenomeTools.AssemblyEvaluator import assembly_evaluator_main

        assembly_evaluator_main(args.target_assembly_fasta, args.ngs_1,
                                args.ngs_2, args.output_file, args.thread_number, args.tmp_dir)

    # ContigDepth
    elif args_dict["subcommand_name"] == "ContigDepth":
        """
        qx -pe smp 56 -l h=cn01 bash get_depth.sh nextpolish2_canu.final.rename.fasta Llv ../../../survey/clean/32_lvchun/all.1.cut.fq.trim.pe.gz ../../../survey/clean/32_lvchun/all.2.cut.fq.trim.pe.gz 56

        --bash
        ref_genome=$1
        tag=$2
        fq1=$3
        fq2=$4
        thread=$5

        hisat2-build $ref_genome $ref_genome.hisat2
        hisat2 -x $ref_genome.hisat2 -p $thread -1 $fq1 -2 $fq2 -S $tag.sam

        samtools view -bS -@ $thread -o $tag.bam $tag.sam
        samtools sort -@ $thread -o $tag.sorted.bam $tag.bam
        samtools index -@ $thread $tag.sorted.bam
        rm $tag.sam
        rm $tag.bam

        python ~/python_project/Genome_work_tools/GenAssembly.py ContigDepth -o $tag.GSS.depth $tag.sorted.bam $ref_genome
        --

        class abc():
            pass

        args = abc()
        args.bam_file = '/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/GSS_vs_Gel.sorted.bam'
        args.ref_genome = '/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/Gel.genome.v1.0.fasta'
        args.output_file = 
        """

        from toolbiox.src.xuyuxing.GenomeTools.ContigDepth import ContigDepth_main
        ContigDepth_main(args)

    # ContigFilter
    elif args_dict["subcommand_name"] == "ContigFilter":
        from toolbiox.src.xuyuxing.GenomeTools.ContigFilter2 import ContigFilter_main
        ContigFilter_main(args)

    # ContaminationFilter
    elif args_dict["subcommand_name"] == "ContaminationFilter":
        from toolbiox.src.xuyuxing.GenomeTools.ContaminationFilter import ContaminationFilter_main
        ContaminationFilter_main(args)

    # HiC2Fasta
    elif args_dict["subcommand_name"] == "HiC2Fasta":
        from toolbiox.api.xuyuxing.genome.juicer import assembly_to_fasta
        assembly_to_fasta(args.final_fasta, args.assembly, args.output_fasta)

    # AssFileRemove
    elif args_dict["subcommand_name"] == "FilterAssemblyFile":
        from toolbiox.api.xuyuxing.genome.juicer import read_assembly, write_assembly
        from toolbiox.lib.common.fileIO import read_list_file

        # args.contig_list = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/filtered.id'
        # args.assembly = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/Llv.reviewed.rename.assembly.test'
        # args.output_file = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/Llv.reviewed.rename.assembly.test.filter'

        raw_scaffold_dict = read_assembly(args.assembly)
        contig_list = set(read_list_file(args.contig_list))

        filterd_scaffold_dict = {}
        for i in raw_scaffold_dict:
            if len([j for j in raw_scaffold_dict[i]['contig_list'] if j in contig_list]) > 0:
                filterd_scaffold_dict[i] = {'contig_list': [],
                                            'contig_length': [], 'contig_strand': []}
                for c_id, length, strand in zip(raw_scaffold_dict[i]['contig_list'], raw_scaffold_dict[i]['contig_length'], raw_scaffold_dict[i]['contig_strand']):
                    if c_id in contig_list:
                        filterd_scaffold_dict[i]['contig_list'].append(c_id)
                        filterd_scaffold_dict[i]['contig_length'].append(
                            length)
                        filterd_scaffold_dict[i]['contig_strand'].append(
                            strand)

        write_assembly(filterd_scaffold_dict, args.output_file)

    # MergeUnanchored
    elif args_dict["subcommand_name"] == "MergeUnanchored":
        from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, FastaRecord, write_fasta
        from toolbiox.lib.common.fileIO import tsv_file_dict_parse

        input_seq_dict = read_fasta_by_faidx(args.input_fasta)
        merge_dict = tsv_file_dict_parse(args.merge_info, fieldnames=[
                                         'new_id', 'raw_id_list'])

        fasta_list = []
        for i in merge_dict:
            new_id = merge_dict[i]['new_id']
            raw_id_list = merge_dict[i]['raw_id_list'].split(",")

            new_seq = ""

            for raw_id in raw_id_list:
                r_rec = input_seq_dict[raw_id]
                r_seq = r_rec.seq

                if not new_seq == "":
                    new_seq = new_seq + "N" * 500

                new_seq = new_seq + r_seq

            fasta_list.append(FastaRecord(seqname=new_id, seq=new_seq))

        write_fasta(fasta_list, args.output_fasta)

    # EasyAssemblyPostProcessor
    elif args_dict["subcommand_name"] == "EasyAssemblyPostProcessor":
        from toolbiox.src.xuyuxing.GenomeTools.EasyPlantTribes import easy_AssemblyPostProcessor_main
        easy_AssemblyPostProcessor_main(args)
