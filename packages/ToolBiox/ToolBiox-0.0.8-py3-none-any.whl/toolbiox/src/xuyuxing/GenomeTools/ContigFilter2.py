"""
args = abc()

args.work_dir = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/test'
args.genome_input_fasta = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/test/short.seq'
args.threads = 56
args.GSS_fq1 = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/test/test.fq1.gz'
args.GSS_fq2 = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/test/test.fq2.gz'
args.related_chl_genome = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/organelle/Lindenbergia_philippensis.plastid.genome.fasta'
args.related_mit_genome = '/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/organelle/close.mitochondrion.genome.fasta'

"""

import os
from toolbiox.lib.common.util import logging_init
from toolbiox.src.xuyuxing.GenomeTools.rRNAFinder import rRNAFinder_main
from toolbiox.src.xuyuxing.GenomeTools.ContigDepth import ContigDepth_main
from toolbiox.lib.common.os import cmd_run, mkdir, copy_file
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.src.xuyuxing.tools.seqtools import FragmentGenome_main
from toolbiox.src.xuyuxing.tools.taxontools import DiamondTaxonAssign_main
from toolbiox.src.xuyuxing.GenomeTools.ContaminationFilter import ContaminationFilter_main
from toolbiox.config import taxon_nr_db, taxon_dump
from toolbiox.api.common.genome.blast import outfmt6_read
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import matplotlib.pyplot as plt
import numpy as np


class abc():
    pass


script_dir_path = os.path.split(os.path.realpath(__file__))[0]

ath_chl_aa = script_dir_path+"/organelle/Ath/Ath.chl.aa.fasta"
ath_chl_rRNA = script_dir_path+"/organelle/Ath/Ath.chl.rRNA.fasta"
osa_chl_aa = script_dir_path+"/organelle/Osa/Osa.chl.aa.fasta"
osa_chl_rRNA = script_dir_path+"/organelle/Osa/Osa.chl.rRNA.fasta"

ath_mit_aa = script_dir_path+"/organelle/Ath/Ath.mit.aa.fasta"
ath_mit_rRNA = script_dir_path+"/organelle/Ath/Ath.mit.rRNA.fasta"
osa_mit_aa = script_dir_path+"/organelle/Osa/Osa.mit.aa.fasta"
osa_mit_rRNA = script_dir_path+"/organelle/Osa/Osa.mit.rRNA.fasta"

ath_nucl_rRNA = script_dir_path+"/Ath_rRNA/rRNA.gene.fa"

ref_seq = {
    'chl': {
        'rRNA': {
            'Ath': ath_chl_rRNA,
            'Osa': osa_chl_rRNA,
        },
        'aa': {
            'Ath': ath_chl_aa,
            'Osa': osa_chl_aa,
        },
    },
    'mit': {
        'rRNA': {
            'Ath': ath_mit_rRNA,
            'Osa': osa_mit_rRNA,
        },
        'aa': {
            'Ath': ath_mit_aa,
            'Osa': osa_mit_aa,
        },
    },
    'nuc': {
        'rRNA': {
            'Ath': ath_nucl_rRNA,
        }
    },
}


def contig_filter_plot(contig_filter_file, output_plot_file):
    # read info
    info_dict = tsv_file_dict_parse(contig_filter_file, key_col='contig_id')

    data_dict = {
        'chl': [[], []],
        'mit': [[], []],
        'contamination': [[], []],
        'nuc': [[], []],
    }

    for i in info_dict:
        note_now = info_dict[i]['Note']
        data_dict[note_now][0].append(float(info_dict[i]['GC_ratio']))
        data_dict[note_now][1].append(
            np.log10(float(info_dict[i]['GSS_depth'])))
    #     data_dict[note_now][1].append(float(info_dict[i]['GSS_depth']))

    label_dict = {
        'nuc': ('tab:blue', 'nuclear'),
        'chl': ('tab:green', 'chloroplastidial'),
        'mit': ('tab:orange', 'mitochondrial'),
        'contamination': ('tab:gray', 'contaminated'),
    }

    # plot

    fig, ax = plt.subplots(figsize=(15, 15))

    for note in label_dict:
        scatter = ax.scatter(data_dict[note][0], data_dict[note][1],
                             c=label_dict[note][0], alpha=0.4, label=label_dict[note][1])

    ax.legend(prop={'size': 'xx-large'})
    ax.set_xlabel('GC ratio', fontsize='xx-large')
    ax.set_ylabel('GSS depth', fontsize='xx-large')
    ax.set_title('contig filter', fontsize='xx-large')
    # plt.show()
    fig.savefig(output_plot_file, format='svg',
                facecolor='none', edgecolor='none')


def get_contamination_report(genome_fasta, work_dir, threads=56, max_target_seqs=50):
    mkdir(work_dir, True)

    split_genome_fasta = work_dir + "/split.genome.fasta"
    diamond_output = work_dir + "/nr.diamond.bls"
    taxon_assign_output = work_dir + "/nr.diamond.taxon"
    contamination_report = work_dir + "/contamination_report.txt"

    # FragmentGenome
    args = abc()
    args.genome_file = genome_fasta
    args.output_file = split_genome_fasta
    args.step = 10000
    args.length = 10000
    args.shift_start = 0
    args.Consider_scaffold = True
    args.entropy_threshold = 3

    FragmentGenome_main(args)

    # diamond
    cmd_string = "diamond blastx --query %s --max-target-seqs %d --db %s --evalue 1e-5 --out %s --outfmt 6 qseqid sseqid staxids pident length mismatch gapopen qstart qend sstart send evalue bitscore --threads %s" % (
        split_genome_fasta,
        max_target_seqs,
        taxon_nr_db,
        diamond_output,
        threads
    )
    cmd_run(cmd_string, None, 1, True)

    # DiamondTaxonAssign
    args = abc()
    args.blast_results = diamond_output
    args.tax_dir = taxon_dump
    args.num_threads = threads
    args.output_file = taxon_assign_output

    DiamondTaxonAssign_main(args)

    # ContaminationFilter
    args = abc()
    args.split_genome_fasta = split_genome_fasta
    args.taxon_assign_output = taxon_assign_output
    args.tax_dir = taxon_dump
    args.output_file = contamination_report

    ContaminationFilter_main(args)


def get_best_hsp_score(bls_file):
    bls_dict = outfmt6_read(bls_file)

    max_score_dict = {}

    for q_id in bls_dict:
        query = bls_dict[q_id]
        for hit_now in query.hit:

            if not hit_now.Hit_id in max_score_dict:
                max_score_dict[hit_now.Hit_id] = 0

            for hsp_now in hit_now.hsp:
                if hsp_now.Hsp_bit_score > max_score_dict[hit_now.Hit_id]:
                    max_score_dict[hit_now.Hit_id] = hsp_now.Hsp_bit_score

    return max_score_dict


def ContigFilter_main(args):
    mkdir(args.work_dir, True)
    args.work_dir = os.path.abspath(args.work_dir)
    
    if args.GSS_fq1:
        args.GSS_fq1 = os.path.abspath(args.GSS_fq1)
    if args.GSS_fq2:
        args.GSS_fq2 = os.path.abspath(args.GSS_fq2)
    if args.related_chl_genome:
        args.related_chl_genome = os.path.abspath(args.related_chl_genome)
    if args.related_mit_genome:
        args.related_mit_genome = os.path.abspath(args.related_mit_genome)
    if args.related_nrRNA_seq:
        args.related_nrRNA_seq = os.path.abspath(args.related_nrRNA_seq)
    if args.depth_results:
        args.depth_results = os.path.abspath(args.depth_results)
    if args.contamination_report:
        args.contamination_report = os.path.abspath(args.contamination_report)
    if args.contig_filter_results:
        args.contig_filter_results = os.path.abspath(
            args.contig_filter_results)

    if not args.contig_filter_results:
        copy_file(args.genome_input_fasta,
                  args.work_dir+"/contig_genome.fasta")
        args.genome_input_fasta = os.path.abspath(
            args.work_dir+"/contig_genome.fasta")

        log_file = args.work_dir + "/log"

        logger = logging_init("ContigFilter", log_file)

        # get info
        logger.info("Step 1: get information to filter contigs")

        # 1. get rRNA
        logger.info("Step 1.1: get rRNA in contigs")

        if not args.related_nrRNA_seq:
            args_rRNA = abc()

            args_rRNA.fasta_file = args.genome_input_fasta
            args_rRNA.query_rRNA_seq = None
            args_rRNA.query_rRNA_bed = None
            args_rRNA.log_file = None
            args_rRNA.output_dir = args.work_dir + "/rRNA"

            rRNAFinder_main(args_rRNA)

            args.related_nrRNA_seq = args.work_dir + "/rRNA/rRNA.unit.fa"

        cmd_string = "makeblastdb -in %s -dbtype nucl" % args.genome_input_fasta
        cmd_run(cmd_string, args.work_dir, 1, True, None)

        cmd_string = "blastn -query %s -db %s -outfmt 6 -out vs_rRNA.bls" % (
            args.related_nrRNA_seq, args.genome_input_fasta)
        cmd_run(cmd_string, args.work_dir, 1, True, None)

        logger.info("Step 1.1: Finished")

        # 2. GSS depth
        logger.info("Step 2: get GSS depth")

        logger.info("Step 2.1: get sorted bam file")

        if not args.depth_results:
            hisat2_index = args.genome_input_fasta + ".hisat2"
            cmd_string = "hisat2-build %s %s" % (
                args.genome_input_fasta, hisat2_index)
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "hisat2 -x %s -p %d -1 %s -2 %s -S GSS.sam" % (
                hisat2_index, args.threads, args.GSS_fq1, args.GSS_fq2)
            # print(cmd_string)
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "samtools view -bS -@ %d -o GSS.bam GSS.sam" % args.threads
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "samtools sort -@ %d -o GSS.sorted.bam GSS.bam" % args.threads
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "samtools index -@ %d GSS.sorted.bam" % args.threads
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "rm GSS.sam"
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            cmd_string = "rm GSS.bam"
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            logger.info("Step 2.1: Finished")

            logger.info("Step 2.2: get depth report")
            args_GSS = abc()

            args_GSS.bam_file = args.work_dir + "/GSS.sorted.bam"
            args_GSS.ref_genome = args.genome_input_fasta
            args_GSS.output_file = args.work_dir + "/GSS.depth.txt"

            ContigDepth_main(args_GSS)

            args.depth_results = args.work_dir + "/GSS.depth.txt"

        logger.info("Step 2.2: Finished")
        logger.info("Step 2: Finished")

        # 3. GC ratio
        logger.info("Step 3: get GC ratio")

        genome_dict = read_fasta_by_faidx(args.genome_input_fasta)
        gc_dict = {i: genome_dict[i].get_GC_ratio() for i in genome_dict}

        logger.info("Step 3: Finished")

        # 4. blast to reference
        logger.info("Step 4: blast to close plant organelle genome")

        if args.related_chl_genome:
            cmd_string = "blastn -query %s -db %s -outfmt 6 -out vs_chl.bls" % (
                args.related_chl_genome, args.genome_input_fasta)
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            vs_chl_bls_path = args.work_dir + "/vs_chl.bls"
        else:
            vs_chl_bls_path = None

        if args.related_mit_genome:
            cmd_string = "blastn -query %s -db %s -outfmt 6 -out vs_mit.bls" % (
                args.related_mit_genome, args.genome_input_fasta)
            cmd_run(cmd_string, args.work_dir, 1, True, None)

            vs_mit_bls_path = args.work_dir + "/vs_mit.bls"
        else:
            vs_mit_bls_path = None

        logger.info("Step 4: Finished")

        # 5. blastx to Ath or Osa org protein
        logger.info("Step 5: blast to Ath Osa organelle genome")

        ref_org_output_dict = {}
        for org in ref_seq:
            if org == 'nuc':
                continue
            ref_org_output_dict[org] = {}
            for type_tmp in ref_seq[org]:
                ref_org_output_dict[org][type_tmp] = {}
                for sp_id in ref_seq[org][type_tmp]:
                    output_file = args.work_dir + \
                        "/%s.%s.%s.bls" % (org, type_tmp, sp_id)
                    ref_org_output_dict[org][type_tmp][sp_id] = output_file

                    if type_tmp == 'aa':
                        cmd_string = "tblastn -query %s -db %s -outfmt 6 -out %s" % (
                            ref_seq[org][type_tmp][sp_id], args.genome_input_fasta, output_file)
                    elif type_tmp == 'rRNA':
                        cmd_string = "blastn -query %s -db %s -outfmt 6 -out %s" % (
                            ref_seq[org][type_tmp][sp_id], args.genome_input_fasta, output_file)

                    cmd_run(cmd_string, args.work_dir, 1, True, None)
        logger.info("Step 5: Finished")

        # 6. diamond to ncbi, to get contamination report
        logger.info("Step 6: diamond to ncbi, to get contamination report")
        if not args.contamination_report:
            get_contamination_report(
                args.genome_input_fasta, args.work_dir, threads=args.threads, max_target_seqs=50)
            args.contamination_report = args.work_dir + "/contamination_report.txt"

        logger.info("Step 6: Finished")

        # merge info
        logger.info("Step 7: merge all information")

        # get nt_rRNA
        nt_rRNA_bls = args.work_dir + "/vs_rRNA.bls"
        contig_nt_rRNA_score_dict = get_best_hsp_score(nt_rRNA_bls)

        # get chl score
        contig_chl_score_dict = {}
        org = 'chl'
        for type_tmp in ref_org_output_dict[org]:
            for sp_id in ref_org_output_dict[org][type_tmp]:
                tmp_score_dict = get_best_hsp_score(
                    ref_org_output_dict[org][type_tmp][sp_id])
                for contig in tmp_score_dict:
                    if not contig in contig_chl_score_dict:
                        contig_chl_score_dict[contig] = 0
                    if tmp_score_dict[contig] > contig_chl_score_dict[contig]:
                        contig_chl_score_dict[contig] = tmp_score_dict[contig]

        if vs_chl_bls_path:
            tmp_score_dict = get_best_hsp_score(vs_chl_bls_path)
            for contig in tmp_score_dict:
                if not contig in contig_chl_score_dict:
                    contig_chl_score_dict[contig] = 0
                if tmp_score_dict[contig] > contig_chl_score_dict[contig]:
                    contig_chl_score_dict[contig] = tmp_score_dict[contig]

        # get mit score
        contig_mit_score_dict = {}
        org = 'mit'
        for type_tmp in ref_org_output_dict[org]:
            for sp_id in ref_org_output_dict[org][type_tmp]:
                tmp_score_dict = get_best_hsp_score(
                    ref_org_output_dict[org][type_tmp][sp_id])
                for contig in tmp_score_dict:
                    if not contig in contig_mit_score_dict:
                        contig_mit_score_dict[contig] = 0
                    if tmp_score_dict[contig] > contig_mit_score_dict[contig]:
                        contig_mit_score_dict[contig] = tmp_score_dict[contig]

        if vs_mit_bls_path:
            tmp_score_dict = get_best_hsp_score(vs_mit_bls_path)
            for contig in tmp_score_dict:
                if not contig in contig_mit_score_dict:
                    contig_mit_score_dict[contig] = 0
                if tmp_score_dict[contig] > contig_mit_score_dict[contig]:
                    contig_mit_score_dict[contig] = tmp_score_dict[contig]

        # get depth
        info_dict = tsv_file_dict_parse(args.depth_results, key_col='contig')
        depth_dict = {c_id: float(info_dict[c_id]['avg_depth'])
                      for c_id in info_dict}

        # gc
        # gc_dict

        # read contamination_report.txt
        info_dict = tsv_file_dict_parse(
            args.contamination_report, key_col='contig_id')

        contamination_dict = {}
        for c_id in info_dict:
            total_num = sum([int(info_dict[c_id][i])
                             for i in info_dict[c_id] if i != 'contig_id'])
            plant_num = sum([int(info_dict[c_id][i])
                             for i in info_dict[c_id] if i == 'Viridiplantae'])
            other_num = sum([int(info_dict[c_id][i]) for i in info_dict[c_id]
                             if i != 'contig_id' and i != 'Viridiplantae' and i != 'No_hit'])
            contamination_dict[c_id] = other_num > plant_num

        # make report
        args.contig_filter_results = args.work_dir + "/ContigFilter.txt"

        with open(args.contig_filter_results, 'w') as f:
            title_list = ["contig_id", "contig_length", "GC_ratio", "GSS_depth", "Chl_score",
                          "Mit_score", "ntrRNA_score", "NCBI_hit", "Note"]
            title_string = "\t".join(title_list)
            f.write(title_string+"\n")

            for c_id in list(genome_dict.keys()):
                c_len = genome_dict[c_id].len()
                gc_value = gc_dict[c_id] if c_id in gc_dict else 0.0
                depth_value = depth_dict[c_id] if c_id in depth_dict else 0.0
                chl_s = contig_chl_score_dict[c_id] if c_id in contig_chl_score_dict else 0.0
                mit_s = contig_mit_score_dict[c_id] if c_id in contig_mit_score_dict else 0.0
                nt_s = contig_nt_rRNA_score_dict[c_id] if c_id in contig_nt_rRNA_score_dict else 0.0
                cont_b = contamination_dict[c_id] if c_id in contamination_dict else None

                # Note
                if chl_s > 5000.0 and depth_value > 100.0 and chl_s > mit_s and chl_s > nt_s and c_len < 1000000:
                    note = 'chl'
                elif mit_s > 5000.0 and depth_value > 100.0 and chl_s < mit_s and mit_s > nt_s and c_len < 1000000:
                    note = 'mit'
                elif cont_b is True and depth_value < 10.0 and c_len < 1000000:
                    note = 'contamination'
                else:
                    note = 'nuc'

                output_list = [c_id,
                               str(c_len),
                               str(gc_value),
                               str(depth_value),
                               str(chl_s),
                               str(mit_s),
                               str(nt_s),
                               str(cont_b),
                               note
                               ]

                output_string = "\t".join(output_list)
                f.write(output_string+"\n")

    # plot
    output_plot_file = args.work_dir + "/ContigFilter.svg"
    contig_filter_plot(args.contig_filter_results, output_plot_file)
