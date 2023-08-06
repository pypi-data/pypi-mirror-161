from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
from pyfaidx import Fasta
import pysam
import io
import sys


def ContigDepth_main(args):

    ref_genome = Fasta(args.ref_genome)

    depth_sum = {}
    cover_site = {}
    for contig in ref_genome.keys():
        depth_sum[contig] = 0
        cover_site[contig] = 0
        contig_length = len(ref_genome[contig])
        for i, start, end in split_sequence_to_bins(contig_length, 10000, start=1):
            fancy_name = "%s:%d-%d" % (contig, start, end)
            depth_string = pysam.depth(
                "-a", "-r", fancy_name, args.bam_file)
            for each_line in io.StringIO(depth_string):
                cover_reads = int(each_line.split()[2])
                depth_sum[contig] = depth_sum[contig] + cover_reads
                if cover_reads > 0:
                    cover_site[contig] = cover_site[contig] + 1

    with open(args.output_file, 'w') as f:
        f.write("contig\tlength\tdepth_sum\tavg_depth\tcover_base\tcoverage\n")
        for contig in ref_genome.keys():
            f.write("%s\t%d\t%d\t%.2f\t%d\t%.2f%%\n" % (
                contig, len(
                    ref_genome[contig]), depth_sum[contig], depth_sum[contig] / len(ref_genome[contig]),
                cover_site[contig], cover_site[contig] * 100 / len(ref_genome[contig])))
