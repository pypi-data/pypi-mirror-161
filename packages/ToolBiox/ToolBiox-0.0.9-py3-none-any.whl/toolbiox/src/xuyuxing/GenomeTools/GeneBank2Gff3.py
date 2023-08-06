from Bio import GenBank
from toolbiox.lib.common.genome.genome_feature2 import GenomeFeature, ChrLoci, write_gff_file
import re


def parse_location_string(location_string):
    if re.match(r'^complement.*', location_string):
        mobj = re.match(r'^complement\((.*)\)', location_string)
        range_string = mobj.groups()[0]
        range_list = parse_location_string(range_string)
        range_list = [(i[0], '-') for i in range_list]

    elif re.match(r'^join.*', location_string):
        mobj = re.match(r'^join\((.*)\)', location_string)
        range_list = []
        for sub_string in mobj.groups()[0].split(","):
            sub_range_list = parse_location_string(sub_string)
            range_list.extend(sub_range_list)

    elif re.match(r'(\d+)\.\.(\d+)', location_string):
        strand = '+'
        mobj = re.match(r'(\d+)\.\.(\d+)', location_string)
        range_now = tuple(
            [tuple(sorted([int(i) for i in mobj.groups()])), strand])
        range_list = [range_now]

    return range_list


def GeneBank2Gff3_main(args):
    gene_name_prefix = 'GNPREF'
    gene_feautre_dict = {}

    with open(args.GeneBank_file) as handle:
        for record in GenBank.parse(handle):
            record_id = record.accession[0]
            record_seq = record.sequence

            gene = None

            num = 0
            for feature in record.features:
                ft_qual_dict = {}

                for i in feature.qualifiers:
                    key_now = i.key.replace('/', '').replace('=', '')
                    ft_qual_dict[key_now] = i.value

                    if 'translation' in ft_qual_dict:
                        del ft_qual_dict['translation']
                    if 'annotator' in ft_qual_dict:
                        del ft_qual_dict['annotator']

                if feature.key == 'gene':
                    if not gene is None:
                        gene_feautre_dict[g_id] = gene

                    g_id = "%s_%s_%05d" % (gene_name_prefix, record_id, num)

                    location = feature.location
                    loc_list = parse_location_string(location)
                    gf_range = (min([i[0][0] for i in loc_list]),
                                max([i[0][1] for i in loc_list]))
                    strand = loc_list[0][1]

                    gene = GenomeFeature(id=g_id, type='gene', chr_loci=ChrLoci(chr_id=record_id, strand=strand, start=gf_range[0], end=gf_range[1]),
                                         qualifiers=ft_qual_dict, sub_features=[])

                    num += 1

                elif feature.key in ['CDS', 'tRNA', 'rRNA']:
                    m_id = gene.id + "." + str(len(gene.sub_features))
                    location = feature.location
                    loc_list = parse_location_string(location)
                    gf_range = (min([i[0][0] for i in loc_list]),
                                max([i[0][1] for i in loc_list]))
                    strand = loc_list[0][1]

                    if feature.key == 'CDS':
                        gf = GenomeFeature(id=m_id, type='mRNA', chr_loci=ChrLoci(chr_id=record_id, strand=strand, start=gf_range[0], end=gf_range[1]),
                                           qualifiers=ft_qual_dict, sub_features=[])
                    else:
                        gf = GenomeFeature(id=m_id, type=feature.key, chr_loci=ChrLoci(chr_id=record_id, strand=strand, start=gf_range[0], end=gf_range[1]),
                                           qualifiers=ft_qual_dict, sub_features=[])

                    exon_num = 0
                    for exon_range, strand in loc_list:
                        e_id = gf.id + ".exon." + str(exon_num)
                        exon = GenomeFeature(id=e_id, type='exon', chr_loci=ChrLoci(
                            chr_id=record_id, strand=strand, start=exon_range[0], end=exon_range[1]))
                        gf.sub_features.append(exon)

                        if feature.key == 'CDS':
                            c_id = gf.id + ".cds." + str(exon_num)
                            cds = GenomeFeature(id=c_id, type='CDS', chr_loci=ChrLoci(
                                chr_id=record_id, strand=strand, start=exon_range[0], end=exon_range[1]))
                            gf.sub_features.append(cds)

                        exon_num += 1

                    gene.sub_features.append(gf)

    write_gff_file([gene_feautre_dict[i] for i in gene_feautre_dict],
                   args.output_gff3, source="GeneBank", sort=True)


if __name__ == '__main__':
    class abc():
        pass

    args = abc()
    args.GeneBank_file = '/lustre/home/xuyuxing/Database/Orobanche/hic/filter/Ocu_organelle_genome/Chl_annotation/GeSeqJob-20210802-95230_tig00121106_debris_2581-92462_GenBank.txt'
    args.output_gff3 = '/lustre/home/xuyuxing/Database/Orobanche/hic/filter/Ocu_organelle_genome/Chl_annotation/ChrC'
