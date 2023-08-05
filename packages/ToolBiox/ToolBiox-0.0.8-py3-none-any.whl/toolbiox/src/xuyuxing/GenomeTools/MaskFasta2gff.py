import re
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.genome.genome_feature2 import GenomeFeature, ChrLoci, write_gff_file
from toolbiox.lib.common.math.interval import merge_intervals

def MaskFasta2Gff_main(args):
    seq_dict = read_fasta_by_faidx(args.masked_file)

    gf_list = []
    for seq_id in seq_dict:
        print(seq_id)
        seq_now = seq_dict[seq_id].seq
        range_tmp_list = []
        for i in re.finditer('N', seq_now):
            range_tmp_list.append((i.end(), i.end()))
        range_list = merge_intervals(range_tmp_list, True)

        num = 0
        for i in range_list:
            gf = GenomeFeature(id="%s_masked_range_%d" % (seq_id, num), type='masked_range', chr_loci=ChrLoci(chr_id=seq_id, start=i[0], end=i[1]))
            gf_list.append(gf)
            num += 1

    write_gff_file(gf_list, args.output_gff, sort=True)

if __name__ == '__main__':
    class abc():
        pass

    args = abc()
    args.masked_file = "/lustre/home/xuyuxing/Database/Orobanche/annotation/EDTA/Ocu.genome.nt.1.0.fasta.mod.MAKER.masked.test"
    args.output_gff = "/lustre/home/xuyuxing/Database/Orobanche/annotation/EDTA/Ocu.genome.nt.1.0.fasta.mod.MAKER.masked.gff3"
