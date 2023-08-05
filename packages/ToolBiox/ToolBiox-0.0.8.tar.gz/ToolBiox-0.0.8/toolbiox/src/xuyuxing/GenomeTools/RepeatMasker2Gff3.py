from toolbiox.lib.common.genome.genome_feature2 import GenomeFeature, ChrLoci, write_gff_file
from toolbiox.api.xuyuxing.genome.repeatmasker import repeatmasker_parser


def RepeatMasker2Gff3_main(args):
    repeat_info = repeatmasker_parser(args.repeatmasker_out)

    gf_list = []
    for i in repeat_info:
        for j in repeat_info[i]:
            for k in repeat_info[i][j].case_list:
                gf = GenomeFeature(id="repeatmasked_%s" % k.ID,
                                   type=k.repeat_class,
                                   chr_loci=ChrLoci(
                                       chr_id=k.q_name, start=k.q_start, end=k.q_end, strand=k.strand),
                                   qualifiers={
                                       'SW_score': k.SW_score,
                                       'perc_div': k.perc_div,
                                       'perc_del': k.perc_del,
                                       'perc_ins': k.perc_ins,
                                       'repeat_name': k.repeat_name,
                                       'repeat_class': k.repeat_class,
                                       'r_start': k.r_start,
                                       'r_end': k.r_end,
                                       'r_length': k.r_length,
                                       'star': k.star,
                                   })
                gf_list.append(gf)

    write_gff_file(gf_list, args.output_gff, sort=True)


if __name__ == '__main__':
    class abc():
        pass

    args = abc()
    args.repeatmasker_out = "/lustre/home/xuyuxing/Database/Orobanche/annotation/repeat/RepeatMasker.out/Ocu.genome.nt.1.0.fasta.out"
    args.output_gff = "/lustre/home/xuyuxing/Database/Orobanche/annotation/repeat/RepeatMasker.out/Ocu.genome.nt.1.0.fasta.gff3"
