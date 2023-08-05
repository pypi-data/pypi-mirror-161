from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
from toolbiox.api.xuyuxing.genome.repeatmasker import repeatmasker_parser
from toolbiox.lib.common.math.interval import merge_intervals, overlap_between_interval_set, sum_interval_length
from toolbiox.lib.common.genome.seq_base import sequence_entropy, read_fasta_by_faidx
from interlap import InterLap


def AnnoCleaner_main(args):
    gene_info = read_gff_file(args.gene_gff)
    gene_info = gene_info['gene']

    # entropy, nr and interpro
    nr_info = {}
    if args.nr_bls is not None:
        nr_info_raw = tsv_file_parse(args.nr_bls)
        for i in nr_info_raw:
            nr_info[nr_info_raw[i][0]] = 0

    interpro_info = {}
    if args.interpro_tsv is not None:
        interpro_info_raw = tsv_file_parse(args.interpro_tsv)
        for i in interpro_info_raw:
            interpro_info[interpro_info_raw[i][0]] = 0

    entropy_info = {}
    if args.entropy_tsv is not None:
        entropy_raw = tsv_file_parse(args.entropy_tsv)
        for i in entropy_raw:
            gene_id = entropy_raw[i][0]
            entropy = float(entropy_raw[i][1])
            entropy_info[gene_id] = entropy

    # bad repeat
    bad_repeat_dict = {}
    if args.repeat_gff_file is not None:
        for gene_id in gene_info:
            gf = gene_info[gene_id]
            bad_repeat_dict[(gf.chr_loci.chr_id, gf.chr_loci.strand)] = []

        repeat_gff = read_gff_file(args.repeat_gff_file)
        for i in repeat_gff.keys():
            for gf_id in repeat_gff[i]:
                gf = repeat_gff[i][gf_id]
                if gf.strand is None:
                    for strand_now in ['+', '-']:
                        if (gf.chr_id, strand_now) in bad_repeat_dict:
                            bad_repeat_dict[(gf.chr_id, strand_now)].append(
                                (gf.start, gf.end))
                else:
                    if (gf.chr_id, gf.strand) in bad_repeat_dict:
                        bad_repeat_dict[(gf.chr_id, gf.strand)].append(
                            (gf.start, gf.end))

        for i in bad_repeat_dict:
            merged_intervals = merge_intervals(bad_repeat_dict[i], True)
            bad_repeat_dict[i] = InterLap()
            if len(merged_intervals) > 0:
                bad_repeat_dict[i].update(merged_intervals)

    # tran
    tran_evidence_dict = {}
    if args.tran_evidence_gff is not None:
        for gene_id in gene_info:
            gf = gene_info[gene_id]
            tran_evidence_dict[(gf.chr_loci.chr_id, gf.chr_loci.strand)] = []

        # tran
        tran_info_raw = tsv_file_parse(args.tran_evidence_gff)
        for i in tran_info_raw:
            q_name, strand, start, end = tran_info_raw[i][0], tran_info_raw[i][6], int(
                tran_info_raw[i][3]), int(tran_info_raw[i][4])
            if (q_name, strand) in bad_repeat_dict:
                tran_evidence_dict[(q_name, strand)].append((start, end))

        for i in tran_evidence_dict:
            merged_intervals = merge_intervals(tran_evidence_dict[i], True)
            tran_evidence_dict[i] = InterLap()
            if len(merged_intervals) > 0:
                tran_evidence_dict[i].update(merged_intervals)

    # judge

    with open(args.output_file, 'w') as f:
        f.write(
            "gene_id\tmRNA_id\ttran_ratio\tbad_repeat_ratio\tentropy\tnr_anno\tinterpro_anno\tgood_gene\n")
        for gene_id in gene_info:
            gf = gene_info[gene_id]
            contig = (gf.chr_loci.chr_id, gf.chr_loci.strand)

            for mRNA in gf.sub_features:

                exon_intervals = [(i.start, i.end)
                                  for i in mRNA.sub_features if i.type == 'exon']
                if len(exon_intervals) == 0:
                    exon_intervals = [(i.start, i.end)
                                      for i in mRNA.sub_features if i.type == 'CDS']

                if contig in tran_evidence_dict:
                    tran_intervals = list(
                        tran_evidence_dict[contig].find((gf.start, gf.end)))
                else:
                    tran_intervals = []
                overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
                    exon_intervals, tran_intervals)
                tran_overlap_ratio = overlap_length / \
                    sum_interval_length(exon_intervals)

                if contig in bad_repeat_dict:
                    bad_repeat_intervals = list(
                        bad_repeat_dict[contig].find((gf.start, gf.end)))
                else:
                    bad_repeat_intervals = []
                overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
                    exon_intervals, bad_repeat_intervals)
                bad_repeat_overlap_ratio = overlap_length / \
                    sum_interval_length(exon_intervals)

                nr_anno = gene_id in nr_info or mRNA.id in nr_info
                interpro_anno = gene_id in interpro_info or mRNA.id in interpro_info

                if gene_id in entropy_info:
                    entropy = entropy_info[gene_id]
                elif mRNA.id in entropy_info:
                    entropy = entropy_info[mRNA.id]
                else:
                    continue

                good_gene = False
                if tran_overlap_ratio >= args.tran_threshold or nr_anno or interpro_anno:
                    good_gene = True
                if bad_repeat_overlap_ratio >= args.repeat_threshold:
                    good_gene = False
                if entropy <= args.entropy_threshold:
                    good_gene = False

                if good_gene:
                    f.write("%s\t%s\t%.2f\t%.2f\t%.4f\t%s\t%s\t%s\n" % (gene_id, mRNA.id, tran_overlap_ratio,
                                                                        bad_repeat_overlap_ratio, entropy, str(nr_anno), str(interpro_anno), str(good_gene)))


if __name__ == "__main__":
    # for Ocu
    class abc():
        pass

    args = abc()

    args.gene_gff = '/lustre/home/xuyuxing/Database/Orobanche/annotation/pasa/sample_mydb_pasa.gene_structures_post_PASA_updates.9505.gff3'
    # qx -pe smp 56 diamond blastp -q Gel.gene_model.v3.0.protein.fasta -k 50 -d ~/Database/NCBI/nr/2020/nr.dmnd -o Gel.gene_model.v3.0.protein.nr.bls -f 6 -p 56
    args.nr_bls = '/lustre/home/xuyuxing/Database/Orobanche/annotation/filter/pasa.aa.nr.bls'
    # qx -pe smp 20 -l h=cn01 /lustre/home/xuyuxing/Database/Interpro/interproscan-5.45-80.0/interproscan.sh -i Gel.gene_model.v3.0.protein.fasta -f tsv -b Gel.gene_model.v3.0.protein.interpro -iprlookup --goterms --pathways -dp
    args.interpro_tsv = '/lustre/home/xuyuxing/Database/Orobanche/annotation/filter/pasa.aa.interpro.tsv'
    args.repeat_gff_file = '/lustre/home/xuyuxing/Database/Orobanche/annotation/EDTA/Ocu.genome.nt.1.0.fasta.mod.MAKER.masked.gff3'
    args.tran_evidence_gff = '/lustre/home/xuyuxing/Database/Orobanche/annotation/evm/T.gff3'
    # python ~/python_project/Genome_work_tools/SeqParser.py SeqEntropy Gel.gene_model.protein.fasta Gel.gene_model.protein.entropy.txt
    args.entropy_tsv = '/lustre/home/xuyuxing/Database/Orobanche/annotation/filter/pasa.aa.entropy.txt'
    args.output_file = '/lustre/home/xuyuxing/Database/Orobanche/annotation/filter/pasa.AnnoCleaner.out'

    args.tran_threshold = 0.5
    args.repeat_threshold = 0.5
    args.entropy_threshold = 3.9

    # for Gel

    class abc():
        pass

    args = abc()

    args.gene_gff = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/T99112N0.genome.gff3'
    # qx -pe smp 56 diamond blastp -q Gel.gene_model.v3.0.protein.fasta -k 50 -d ~/Database/NCBI/nr/2020/nr.dmnd -o Gel.gene_model.v3.0.protein.nr.bls -f 6 -p 56
    args.nr_bls = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/T99112N0.gene_model.protein.nr.bls'
    # qx -pe smp 20 -l h=cn01 /lustre/home/xuyuxing/Database/Interpro/interproscan-5.45-80.0/interproscan.sh -i Gel.gene_model.v3.0.protein.fasta -f tsv -b Gel.gene_model.v3.0.protein.interpro -iprlookup --goterms --pathways -dp
    args.interpro_tsv = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/T99112N0.gene_model.protein.interpro.tsv'
    args.repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/RepeatMasker.out/T99112N0.genome.fasta.out'
    args.tran_evidence_gff = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/T.gff3'
    # python ~/python_project/Genome_work_tools/SeqParser.py SeqEntropy Gel.gene_model.protein.fasta Gel.gene_model.protein.entropy.txt
    args.entropy_tsv = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/T99112N0.gene_model.entropy.txt'
    args.output_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/no_clean/gene.clean.txt'

    args.tran_threshold = 0.5
    args.repeat_threshold = 0.5
    args.entropy_threshold = 3.9

    AnnoCleaner_main(args)

    # retry
    Gelv2_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/jbrowse/data/Gel.genome.gff3'
    Yuan_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/yuan_pt_vs_xu/WPG_working/WPGmapper/yuan/genewise.best.gff'

    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, get_mRNA_overlap, Gene, gene_compare, convert_dict_structure

    Gelv2_dict = read_gff_file(Gelv2_gff)
    Yuan_dict = read_gff_file(Yuan_gff)

    Gelv2_gene_dict, Gelv2_chr_dict = convert_dict_structure(Gelv2_dict)
    Yuan_gene_dict, Yuan_chr_dict = convert_dict_structure(Yuan_dict)

    compare_chr_dict = gene_compare(
        Gelv2_chr_dict, Yuan_chr_dict, similarity_type='shorter_overlap_coverage', threshold=0.5)

    gelv2_list = []
    yuan_list = []
    for chr_id in compare_chr_dict:
        for strand in compare_chr_dict[chr_id]:
            for a, b in compare_chr_dict[chr_id][strand]:
                gelv2_list.append(a)
                yuan_list.append(b)

    gelv2_list = list(set(gelv2_list))
    yuan_list = list(set(yuan_list))

    # species job for merge Gel gene annotation

    Gelv2_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/jbrowse/data/Gel.genome.gff3'
    Yuan_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/yuan_pt_vs_xu/WPG_working/WPGmapper/yuan/genewise.best.gff'
    identity_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/identity.id'
    Gel_Pseudo_gff = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/Gel.Pseudo.gff3'
    tran_evidence_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v2.0/annotation_run/evm/T.gff3'

    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, get_mRNA_overlap, Gene
    from interlap import InterLap
    from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
    from toolbiox.lib.xuyuxing.math.set_operating import merge_intervals, overlap_between_interval_set, sum_interval_length

    tmp_info = tsv_file_parse(identity_file)

    skip_gene_list = {}
    skip_gene_x = {}
    for i in tmp_info:
        g_id = tmp_info[i][0]
        y_id = tmp_info[i][1]
        skip_gene_list[g_id] = None
        skip_gene_list[y_id] = None
        skip_gene_x[g_id] = None

    Gelv2_dict = read_gff_file(Gelv2_gff)
    Yuan_dict = read_gff_file(Yuan_gff)

    Gelv2_chr_dict = {}
    Gelv2_gene_dict = {}
    for i in Gelv2_dict:
        for gf_id in Gelv2_dict[i]:
            gf = Gelv2_dict[i][gf_id]
            gene = Gene(from_gf=gf)
            gene.build_gene_seq()

            if gene.chr_id not in Gelv2_chr_dict:
                Gelv2_chr_dict[gene.chr_id] = {"+": {}, "-": {}}

            Gelv2_chr_dict[gene.chr_id][gene.strand][gf_id] = gene
            Gelv2_gene_dict[gf_id] = gene

    Yuan_gene_dict = {}
    Yuan_chr_dict = {}
    for i in Yuan_dict:
        for gf_id in Yuan_dict[i]:
            gf = Yuan_dict[i][gf_id]
            gene = Gene(from_gf=gf)
            gene.build_gene_seq()

            if gene.chr_id not in Yuan_chr_dict:
                Yuan_chr_dict[gene.chr_id] = {"+": {}, "-": {}}

            Yuan_chr_dict[gene.chr_id][gene.strand][gf_id] = gene
            Yuan_gene_dict[gf_id] = gene

    gene_id_pair = []

    for chr_id in Gelv2_chr_dict:
        for strand in Gelv2_chr_dict[chr_id]:
            if chr_id in Yuan_chr_dict and strand in Yuan_chr_dict[chr_id]:
                num = 0
                for gf1_id in Gelv2_chr_dict[chr_id][strand]:
                    num += 1
                    print(chr_id, strand, num, len(
                        Gelv2_chr_dict[chr_id][strand]))
                    if gf1_id in skip_gene_list:
                        continue
                    for gf2_id in Yuan_chr_dict[chr_id][strand]:
                        gf2 = Yuan_gene_dict[gf2_id]
                        query_gf2 = gf2.qualifiers['query'][0]
                        if query_gf2 in skip_gene_list:
                            continue
                        overlap_flag = False
                        for m1 in Gelv2_chr_dict[chr_id][strand][gf1_id].sub_features:
                            if overlap_flag:
                                break
                            for m2 in Yuan_chr_dict[chr_id][strand][gf2_id].sub_features:
                                if overlap_flag:
                                    break
                                if get_mRNA_overlap(m1, m2, 'shorter_overlap_coverage') > 0.5:
                                    overlap_flag = True
                        if overlap_flag:
                            gene_id_pair.append((gf1_id, gf2_id))

    # tran
    tran_evidence_dict = {}
    tran_info_raw = tsv_file_parse(tran_evidence_gff)
    for i in tran_info_raw:
        q_name, strand, start, end = tran_info_raw[i][0], tran_info_raw[i][6], int(
            tran_info_raw[i][3]), int(tran_info_raw[i][4])
        if (q_name, strand) not in tran_evidence_dict:
            tran_evidence_dict[(q_name, strand)] = []
        tran_evidence_dict[(q_name, strand)].append((start, end))

    for i in tran_evidence_dict:
        merged_intervals = merge_intervals(tran_evidence_dict[i], True)
        tran_evidence_dict[i] = InterLap()
        if len(merged_intervals) > 0:
            tran_evidence_dict[i].update(merged_intervals)

    def get_tran_ratio(gf, tran_evidence_dict, type_exon='exon'):
        contig = gf.chr_id
        strand = gf.strand

        exon_intervals = [(i.start, i.end)
                          for i in gf.sub_features if i.type == type_exon]

        tran_intervals = list(
            tran_evidence_dict[(contig, strand)].find((gf.start, gf.end)))
        overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
            exon_intervals, tran_intervals)
        tran_overlap_ratio = overlap_length / \
            sum_interval_length(exon_intervals)

        return tran_overlap_ratio

    keep_x = []
    keep_y = []
    for x_id, y_id in gene_id_pair:
        x_gf = Gelv2_gene_dict[x_id]
        y_gf = Yuan_gene_dict[y_id]

        x_ratio = get_tran_ratio(
            x_gf.model_mRNA, tran_evidence_dict, type_exon='exon')
        y_ratio = get_tran_ratio(
            y_gf.sub_features[0], tran_evidence_dict, type_exon='CDS')

        print(x_ratio, y_ratio)

        if y_ratio - x_ratio > 0.2:
            keep_y.append(y_id)
        else:
            keep_x.append(x_id)

    keep_x = set(keep_x)
    keep_y = set(keep_y)

    for x_id, y_id in gene_id_pair:
        if x_id in keep_x and y_id in keep_y:
            keep_y.remove(y_id)

    all_compare_x = set([i[0] for i in gene_id_pair])
    remove_x = all_compare_x - keep_x
    not_compare_x = (set(list(Gelv2_gene_dict.keys())) - all_compare_x)

    all_compare_y = set([i[1] for i in gene_id_pair])
    not_compare_y = (set(list(Yuan_gene_dict.keys())) - all_compare_y)

    add_keep_y = []
    for i in not_compare_y:
        gf = Yuan_gene_dict[i]
        if not gf.qualifiers['query'][0] in skip_gene_list:
            add_keep_y.append(i)

    add_keep_x = []
    for i in not_compare_x:
        if not i in skip_gene_list:
            add_keep_x.append(i)

    good_gf_list = []

    for i in skip_gene_x:
        good_gf_list.append(Gelv2_gene_dict[i])
    for i in keep_x:
        good_gf_list.append(Gelv2_gene_dict[i])
    for i in keep_y:
        good_gf_list.append(Yuan_gene_dict[i])
    for i in add_keep_y:
        good_gf_list.append(Yuan_gene_dict[i])
    for i in add_keep_x:
        good_gf_list.append(Gelv2_gene_dict[i])

    ###

    Gel_Pseudo_dict = read_gff_file(Gel_Pseudo_gff)

    Gel_Pseudo_gene_dict = {}
    Gel_Pseudo_chr_dict = {}
    for i in Gel_Pseudo_dict:
        for gf_id in Gel_Pseudo_dict[i]:
            gf = Gel_Pseudo_dict[i][gf_id]
            gene = Gene(from_gf=gf)
            gene.build_gene_seq()

            if gene.chr_id not in Gel_Pseudo_chr_dict:
                Gel_Pseudo_chr_dict[gene.chr_id] = {"+": {}, "-": {}}

            Gel_Pseudo_chr_dict[gene.chr_id][gene.strand][gf_id] = gene
            Gel_Pseudo_gene_dict[gf_id] = gene

    good_gene_dict = {}
    good_chr_dict = {}
    for gf in good_gf_list:
        gene = Gene(from_gf=gf)
        gene.build_gene_seq()

        if gene.chr_id not in good_chr_dict:
            good_chr_dict[gene.chr_id] = {"+": {}, "-": {}}

        good_chr_dict[gene.chr_id][gene.strand][gf.id] = gene
        good_gene_dict[gf.id] = gene

    gene_id_pair = []

    for chr_id in Gel_Pseudo_chr_dict:
        for strand in Gel_Pseudo_chr_dict[chr_id]:
            if chr_id in good_chr_dict and strand in good_chr_dict[chr_id]:
                num = 0
                for gf1_id in Gel_Pseudo_chr_dict[chr_id][strand]:
                    num += 1
                    print(chr_id, strand, num, len(
                        Gel_Pseudo_chr_dict[chr_id][strand]))

                    for gf2_id in good_chr_dict[chr_id][strand]:

                        overlap_flag = False
                        for m1 in Gel_Pseudo_chr_dict[chr_id][strand][gf1_id].sub_features:
                            if overlap_flag:
                                break
                            for m2 in good_chr_dict[chr_id][strand][gf2_id].sub_features:
                                if overlap_flag:
                                    break
                                if get_mRNA_overlap(m1, m2, 'shorter_overlap_coverage') > 0.5:
                                    overlap_flag = True
                        if overlap_flag:
                            gene_id_pair.append((gf1_id, gf2_id))

    pass_pseudo_gene_list = set(
        Gel_Pseudo_gene_dict.keys()) - set([i[0] for i in gene_id_pair])

    # merge

    import re
    from toolbiox.lib.xuyuxing.base.common_command import merge_dict
    from toolbiox.lib.common.genome.genome_feature2 import gene_rename, write_gff_file
    import copy

    all_gf_list = []
    num = 0
    for contig in good_chr_dict:
        gf_dict = merge_dict(
            [good_chr_dict[contig]['+'], good_chr_dict[contig]['-']], False)
        sorted_gf_list = sorted(list(gf_dict.keys()),
                                key=lambda x: gf_dict[x].start)

        for i in sorted_gf_list:
            if i in Gelv2_gene_dict:
                all_gf_list.append(Gelv2_gene_dict[i])
            else:
                gf = Yuan_gene_dict[i]
                pseudo = 'Note' in gf.sub_features[0].qualifiers

                if pseudo:
                    new_gf_name = "GelREAP%05d" % num
                else:
                    new_gf_name = "GelREAG%05d" % num

                num = num + 1

                new_gf = gene_rename(gf, new_gf_name, gf.chr_id)

                if not pseudo:

                    cds_list = [
                        cds for cds in new_gf.sub_features[0].sub_features]

                    exon_list = []
                    for j in cds_list:
                        i = copy.deepcopy(j)
                        i.id = re.sub('cds', 'exon', i.id)
                        del i.qualifiers['phase']
                        i.qualifiers['ID'] = i.id
                        i.qualifiers['Name'] = i.id
                        i.type = 'exon'
                        exon_list.append(i)

                    new_gf.sub_features[0].sub_features.extend(exon_list)
                else:
                    new_gf.qualifiers['Note'] = 'pseudogene'

                all_gf_list.append(new_gf)

    for i in pass_pseudo_gene_list:
        gf = Gel_Pseudo_gene_dict[i]
        gf.qualifiers['Note'] = 'pseudogene'
        all_gf_list.append(gf)

    write_gff_file(
        all_gf_list, '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/merged.gff')

    # add fungi_pseudo_gene
    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, convert_dict_structure, get_mRNA_overlap

    fungi_pseudo_gff = "/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/Gel.rep.gff3"
    Gelv3_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/v3.1/Gel.genome.v3.0.gff'

    fungi_pseudo_dict = read_gff_file(fungi_pseudo_gff)
    Gelv3_dict = read_gff_file(Gelv3_gff)

    fp_gene_dict, fp_chr_dict = convert_dict_structure(fungi_pseudo_dict)
    v3_gene_dict, v3_chr_dict = convert_dict_structure(Gelv3_dict)

    keep_fp_list = []
    num = 0
    for chr_id in fp_chr_dict:
        for strand in fp_chr_dict[chr_id]:
            if chr_id in v3_chr_dict and strand in v3_chr_dict[chr_id]:
                for fq_gf_id in fp_chr_dict[chr_id][strand]:
                    num += 1
                    print(num)
                    overlap_flag = False
                    for v3_gf_id in v3_chr_dict[chr_id][strand]:
                        if overlap_flag:
                            break
                        for m1 in fp_chr_dict[chr_id][strand][fq_gf_id].sub_features:
                            if overlap_flag:
                                break
                            for m2 in v3_chr_dict[chr_id][strand][v3_gf_id].sub_features:
                                if overlap_flag:
                                    break
                                if get_mRNA_overlap(m1, m2, 'shorter_overlap_coverage') > 0.5:
                                    overlap_flag = True
                    if not overlap_flag:
                        keep_fp_list.append(fq_gf_id)
            else:
                for fq_gf_id in fp_chr_dict[chr_id][strand]:
                    keep_fp_list.append(fq_gf_id)

    #
    import re
    from toolbiox.lib.common.genome.genome_feature2 import gene_rename, write_gff_file

    gf_list = []
    for i in v3_gene_dict:
        gf = v3_gene_dict[i]
        gf_list.append(gf)

    num = 1
    for i in keep_fp_list:
        gf = fp_gene_dict[i]
        new_gf_name = 'GelFGPS%05d' % num
        num += 1
        new_gf = gene_rename(gf, new_gf_name, gf.chr_id)
        new_gf.qualifiers['Note'] = 'pseudogene'
        gf_list.append(new_gf)

    Gelv3_1_gff = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/v3.1/Gel.genome.v3.1.gff'
    write_gff_file(gf_list, Gelv3_1_gff, "GelGenome", True)

    # test
    gff_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/v3.0/v3.1/Gel.genome.v3.1.gff'

    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, get_mRNA_overlap, Gene, gene_compare, convert_dict_structure

    Gelv31_dict = read_gff_file(gff_file)

    gene_dict, chr_dict = convert_dict_structure(Gelv31_dict)

    compare_chr_dict = gene_compare(
        chr_dict, chr_dict, similarity_type='shorter_overlap_coverage', threshold=0.5)

    pair_list = []
    for chr_id in compare_chr_dict:
        for strand in compare_chr_dict[chr_id]:
            for a, b in compare_chr_dict[chr_id][strand]:
                if a == b:
                    continue
                else:
                    pair_list.append((a, b))
