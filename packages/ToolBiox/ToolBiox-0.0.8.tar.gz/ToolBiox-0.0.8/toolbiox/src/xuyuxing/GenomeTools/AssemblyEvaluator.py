from toolbiox.lib.common.os import mkdir, rmdir, cmd_run
import os
import re
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
import uuid


def running_samtools_and_bcftools_for_assembly_evaluator(assembly_fasta_file, ngs_r1, ngs_r2, threads, tmp_dir):
    cmd_run("hisat2-build %s %s.hisat2" % (assembly_fasta_file,
                                           assembly_fasta_file), cwd=tmp_dir, retry_max=1, silence=True)
    hisat_out = cmd_run("hisat2 -p %d -x %s.hisat2 -1 %s -2 %s -S ngs.sam" %
                        (threads, assembly_fasta_file, ngs_r1, ngs_r2), cwd=tmp_dir, retry_max=1, silence=True)
    # hisat_out = hisat_out[2]
    # hisat_map_ratio = float(hisat_out.split("\n")[-2].split(" ")[0].split("%")[0])/100

    cmd_run("samtools view -bS -@ %d -o ngs.bam ngs.sam" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools fixmate -@ %d -m ngs.bam ngs.fixmate.bam" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools sort -@ %d -o ngs.fixmate.sorted.bam ngs.fixmate.bam" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools markdup -@ %d -r ngs.fixmate.sorted.bam ngs.fixmate.sorted.undup.bam" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools index -@ %d ngs.fixmate.sorted.undup.bam" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools stats -@ %d -c 3,200,50 ngs.fixmate.sorted.undup.bam > ngs.fixmate.sorted.undup.stat" %
            threads, cwd=tmp_dir, retry_max=1, silence=True)

    cmd_run("samtools faidx %s" % assembly_fasta_file,
            cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("samtools mpileup -g -f %s ngs.fixmate.sorted.undup.bam > ngs.bcf" %
            assembly_fasta_file, cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("bcftools call -mv -Ov ngs.bcf > ngs.var.bcf",
            cwd=tmp_dir, retry_max=1, silence=True)
    cmd_run("bcftools view ngs.var.bcf | vcfutils.pl varFilter - > ngs.var.final.vcf",
            cwd=tmp_dir, retry_max=1, silence=True)


def assembly_evaluator_main(target_assembly_fasta, given_short_reads_fastq1, given_short_reads_fastq2, output_file, threads=56, tmp_dir=None):
    """
    target_assembly_fasta = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/nextpolish2/01_rundir/00.lgs_polish/input.genome.fasta"
    given_short_reads_fastq1 = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/tmp.1.fq.gz"
    given_short_reads_fastq2 = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/tmp.2.fq.gz"
    threads = 56
    tmp_dir = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/tmp"
    """

    if not tmp_dir:
        tmp_dir = "/tmp/%s" % uuid.uuid1().hex
    else:
        tmp_dir = tmp_dir + "/" + uuid.uuid1().hex
        tmp_dir = os.path.abspath(tmp_dir)

    mkdir(tmp_dir, False)
    assembly_fasta_file = tmp_dir + "/assembly.fasta"
    ngs_r1 = tmp_dir + "/ngs_r1.fq.gz"
    ngs_r2 = tmp_dir + "/ngs_r2.fq.gz"

    os.symlink(os.path.abspath(target_assembly_fasta), assembly_fasta_file)
    os.symlink(os.path.abspath(given_short_reads_fastq1), ngs_r1)
    os.symlink(os.path.abspath(given_short_reads_fastq2), ngs_r2)

    # sum_length
    assembly_seq_dict = read_fasta_by_faidx(tmp_dir + "/assembly.fasta")
    sum_length = sum([assembly_seq_dict[i].len() for i in assembly_seq_dict])

    running_samtools_and_bcftools_for_assembly_evaluator(
        assembly_fasta_file, ngs_r1, ngs_r2, threads, tmp_dir)

    # reads, mapped_reads, paired_mapped_reads, base_error_rate, bases_mapped, uncovered_base
    with open(tmp_dir+"/ngs.fixmate.sorted.undup.stat", 'r') as f:
        covered_base = 0
        for each_line in f:
            mObj = re.match('^SN\treads paired:\t(\S+)', each_line)
            if mObj:
                reads = int(mObj.groups()[0])

            mObj = re.match('^SN\treads mapped:\t(\S+)', each_line)
            if mObj:
                mapped_reads = int(mObj.groups()[0])

            mObj = re.match('^SN\treads mapped and paired:\t(\S+)', each_line)
            if mObj:
                paired_mapped_reads = int(mObj.groups()[0])

            mObj = re.match('^SN\terror rate:\t(\S+)', each_line)
            if mObj:
                base_error_rate = float(mObj.groups()[0])

            mObj = re.match('^COV\t\[\d+-\d+\]\t(\S+)\t(\S+)', each_line)
            if mObj:
                covered_base += int(mObj.groups()[1])

        print(reads, mapped_reads, paired_mapped_reads,
              base_error_rate, covered_base)

    # snp
    hete = int(cmd_run("grep \"^#\" -P ngs.var.final.vcf -v |grep \"1/1\" -c",
                       cwd=tmp_dir, retry_max=1, silence=True)[1].strip())
    error = int(cmd_run("grep \"^#\" -P ngs.var.bcf -v |grep \"1/1\" -c -v",
                        cwd=tmp_dir, retry_max=1, silence=True)[1].strip())

    #
    with open(output_file, 'w') as f:
        f.write("""
#### Assembly Evaluator Report:

Assembly_sum_length:\t\t\t%d
NGS_reads_number:\t\t\t%d
Total_mapped_reads_number:\t\t%d (%.2f%%)
Paired_mapped_reads_number:\t\t%d (%.2f%%)
Base_error_rate:\t\t\t%.5f%%\t\t\t\t\t\t# error rate from samtools stat, for reads error include sequence error
Assembly_covered_by_reads (bp):\t\t%d (%.2f%%)\t\t\t\t\t# at least more than 3 depth
Heterozygosity:\t\t\t\t%d (%.5f%%)\t\t\t\t\t# strict 1/1 SNP, Indel vs assembly covered length
Pure_error_bases:\t\t\t%d (%.5f%%)\t\t\t\t\t\t# no strict 0/1 SNP, Indel vs assembly covered length
""" % (
            sum_length,
            reads,
            mapped_reads, mapped_reads/reads * 100,
            paired_mapped_reads, paired_mapped_reads/reads * 100,
            base_error_rate * 100,
            covered_base, covered_base/sum_length * 100,
            hete, hete/covered_base * 100,
            error, error/covered_base * 100,
        ))

    # remove
#     rmdir(tmp_dir)
