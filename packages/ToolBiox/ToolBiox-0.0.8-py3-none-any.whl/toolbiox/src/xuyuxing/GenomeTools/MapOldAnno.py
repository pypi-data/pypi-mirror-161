import os
import re
from copy import deepcopy
from toolbiox.lib.common.genome.genome_feature2 import ChrLoci, GenomeFeature, read_gff_file, cds_judgment, cluster_of_chr_loci, write_gff_file
from toolbiox.lib.common.genome.seq_base import read_fasta
from toolbiox.lib.common.os import mkdir, multiprocess_running
from toolbiox.api.common.genome.blast import blastn_pair_running
from toolbiox.lib.common.math.interval import merge_intervals
from interlap import InterLap
import pickle

def cDNA_coord_shift(give_site, direction, sub_feature_list):
    """
    give_site = 100
    direction = 'cDNA_to_Genome'
    sub_feature_list = mRNA.sub_features
    """

    strand = sub_feature_list[0].strand

    if strand == 1 or strand == "+":
        GC = sorted([(exon.start, exon.end) for exon in sub_feature_list if
                     exon.type == 'exon' or exon.type == 'match_part'])
    else:
        GC = sorted([(exon.end, exon.start) for exon in sub_feature_list if
                     exon.type == 'exon' or exon.type == 'match_part'], reverse=True)

    start = 0
    CC = []
    for i in GC:
        i_len = abs(i[1] - i[0]) + 1
        CC.append((start + 1, start + i_len))
        start = start + i_len

    if direction == 'cDNA_to_Genome':
        block_index = None
        for i in CC:
            if min(i) <= give_site <= max(i):
                block_index = CC.index(i)

        if block_index is None:
            raise ValueError("give_site is out of gene range")

        dela_len = give_site - CC[block_index][0]

        if strand == 1 or strand == "+":
            return GC[block_index][0] + dela_len
        else:
            return GC[block_index][0] - dela_len

    elif direction == 'Genome_to_cDNA':
        block_index = None
        for i in GC:
            if min(i) <= give_site <= max(i):
                block_index = GC.index(i)

        if block_index is None:
            raise ValueError("give_site is out of gene range")

        if strand == 1 or strand == "+":
            dela_len = give_site - GC[block_index][0]
        else:
            dela_len = GC[block_index][0] - give_site

        return CC[block_index][0] + dela_len

def cDNA_feature_coord(mRNA):
    output_list = []
    for ft in mRNA.sub_features:
        if ft.type == 'exon':
            continue

        ft_cDNA_start_tmp = cDNA_coord_shift(
            ft.start, "Genome_to_cDNA", mRNA.sub_features)
        ft_cDNA_end_tmp = cDNA_coord_shift(
            ft.end, "Genome_to_cDNA", mRNA.sub_features)

        ft_cDNA_start = min(ft_cDNA_start_tmp, ft_cDNA_end_tmp)
        ft_cDNA_end = max(ft_cDNA_start_tmp, ft_cDNA_end_tmp)

        output_list.append((ft.type, (ft_cDNA_start, ft_cDNA_end)))

    return output_list

def adjust_cds_phaes(cDNA_feature_list, phase):
    """
    cDNA_feature_list = [('five_prime_UTR',(1,20)),('CDS',(21,40)),('three_prime_UTR',(41,50))]
    cDNA_feature_list = [('five_prime_UTR',(1,10)),('CDS',(21,40)),('three_prime_UTR',(41,50))]
    phase = 1
    """

    for i in range(len(cDNA_feature_list)):
        type_tmp, range_tmp = cDNA_feature_list[i]
        if type_tmp == 'CDS':
            old_start = cDNA_feature_list[i][1][0]

            new_start = old_start + phase
            cDNA_feature_list[i] = (
                'CDS', (new_start, cDNA_feature_list[i][1][1]))

            if i > 0 and old_start - cDNA_feature_list[i - 1][1][1] == 1:
                new_end = new_start - 1
                cDNA_feature_list[i - 1] = (
                    cDNA_feature_list[i - 1][0], (cDNA_feature_list[i - 1][1][0], new_end))

            break

    return cDNA_feature_list

def no_gap_index(seq, gap_chr='-'):
    """0-base"""
    ind_list = []
    for i in range(len(seq)):
        c = seq[i]
        if i > 0:
            lc = seq[i - 1]

        # block start
        if i == 0 and c != gap_chr:
            blocking_start = 0
        if i != 0 and c != gap_chr and lc == gap_chr:
            blocking_start = i

        # block end
        if i != 0 and c == gap_chr and lc != gap_chr:
            blocking_end = i - 1
            ind_list.append((blocking_start, blocking_end))
        if i + 1 == len(seq):
            blocking_end = i
            ind_list.append((blocking_start, blocking_end))

    seq_index_interlap = InterLap()

    no_gap_end_index = -1

    for i in ind_list:
        seq_index_interlap.add(
            (no_gap_end_index + 1, i[1] - i[0] + 1 + no_gap_end_index, i))
        no_gap_end_index = i[1] - i[0] + 1 + no_gap_end_index

    return seq_index_interlap

def blast_hit_coord_shift(give_site, direction, blast_hsp):
    """
    give_site = 100 (1-base)
    direction = 'query_to_subject'
    blast_hsp = BlastHsp by xuyuxing
    """

    q_seq = blast_hsp.Hsp_qseq
    s_seq = blast_hsp.Hsp_hseq
    midline = blast_hsp.Hsp_midline

    q_from = blast_hsp.Hsp_query_from
    q_to = blast_hsp.Hsp_query_to
    s_from = blast_hsp.Hsp_hit_from
    s_to = blast_hsp.Hsp_hit_to

    q_iterlap = no_gap_index(q_seq)
    s_iterlap = no_gap_index(s_seq)

    if direction == 'query_to_subject':
        if give_site < q_from:
            give_site = q_from
        if give_site > q_to:
            give_site = q_to

        give_site_index = give_site - q_from

        s_start, s_end, (a_start, a_end) = list(
            q_iterlap.find((give_site_index, give_site_index)))[0]
        aln_site = give_site_index - s_start + a_start

        output_site = len(
            s_seq[0:aln_site + 1].replace("-", "")) + s_from - 1
    elif direction == 'subject_to_query':
        if give_site < s_from:
            give_site = s_from
        if give_site > s_to:
            give_site = s_to

        give_site_index = give_site - s_from

        s_start, s_end, (a_start, a_end) = list(
            s_iterlap.find((give_site_index, give_site_index)))[0]
        aln_site = give_site_index - s_start + a_start

        output_site = len(
            q_seq[0:aln_site + 1].replace("-", "")) + q_from - 1

    return output_site

def generate_new_feature(mRNA, phase, blat_cdna_seq, best_hsp, blat_hit):
    # read old cDNA structure
    feature_list = cDNA_feature_coord(mRNA)

    # adjust phase
    feature_list = adjust_cds_phaes(feature_list, phase)

    # map old cDNA to new cDNA
    new_cDNA_feature_list = []
    for type_tmp, range_tmp in feature_list:
        start_tmp = blast_hit_coord_shift(
            range_tmp[0], 'query_to_subject', best_hsp)
        end_tmp = blast_hit_coord_shift(
            range_tmp[1], 'query_to_subject', best_hsp)

        new_cDNA_feature_list.append((type_tmp, (start_tmp, end_tmp)))

    # remove bad feature
    new_cDNA_feature_filterd_list = []
    for type_tmp, range_tmp in new_cDNA_feature_list:
        if range_tmp[1] - range_tmp[0] == 0:
            continue
        new_cDNA_feature_filterd_list.append((type_tmp, range_tmp))

    # test cds is good
    cds_seq = ""
    for type_tmp, range_tmp in new_cDNA_feature_filterd_list:
        if not type_tmp == 'CDS':
            continue

        cds_seq += blat_cdna_seq[range_tmp[0] - 1:range_tmp[1]]

    good_orf, phase, aa_seq = cds_judgment(cds_seq)

    if good_orf:

        new_cDNA_feature_filterd_phased_list = adjust_cds_phaes(
            new_cDNA_feature_filterd_list, phase)

        # get new genome feature
        genome_feature_list = []
        for type_tmp, range_tmp in new_cDNA_feature_filterd_phased_list:
            start_tmp = cDNA_coord_shift(
                range_tmp[0], 'cDNA_to_Genome', blat_hit.sub_features)
            end_tmp = cDNA_coord_shift(
                range_tmp[1], 'cDNA_to_Genome', blat_hit.sub_features)

            # print(range_tmp,(start_tmp, end_tmp))

            genome_feature_list.append(
                (type_tmp, (start_tmp, end_tmp)))

        # exon get
        exon_range = []
        for type_tmp, range_tmp in genome_feature_list:
            exon_range.append(range_tmp)

        exon_range = merge_intervals(exon_range, True)

        for i in exon_range:
            genome_feature_list.append(('exon', i))

        # change to GenomeFeature
        named_genome_feature_list = []
        for type_name, type_tag in [('CDS', 'cds'), ('exon', 'exon'), ('five_prime_UTR', 'utr5p'),
                                    ('three_prime_UTR', 'utr3p')]:
            type_list = sorted(
                [i for i in genome_feature_list if i[0] == type_name], key=lambda x: x[1][0])
            for i in range(len(type_list)):
                named_genome_feature_list.append(
                    ("%s.%s%d" % (blat_hit.id, type_tag, i + 1), type_list[i][0], type_list[i][1]))

        sub_feature = []
        site_list = []
        for sub_gf_id, type_tmp, range_tmp in named_genome_feature_list:
            site_list.extend(list(range_tmp))
            sub_feature.append(GenomeFeature(id=sub_gf_id, type=type_tmp, chr_loci=ChrLoci(chr_id=blat_hit.chr_id, strand=blat_hit.strand, start=range_tmp[0], end=range_tmp[1])))

        # add cds phase
        cds_len_sum = 0
        if blat_hit.strand == '+' or blat_hit.strand == 1:
            for sub_gf in sorted(sub_feature, key=lambda x: x.start, reverse=False):
                if sub_gf.type == 'CDS':
                    if cds_len_sum % 3 == 0:
                        phase_tmp = 0
                    else:
                        phase_tmp = 3 - (cds_len_sum % 3)
                    sub_gf.phase = phase_tmp
                    sub_gf.qualifiers["phase"] = [sub_gf.phase]
                    sub_gf.qualifiers["phase2"] = phase_tmp
                    sub_gf.phase2 = sub_gf.phase
                    cds_len_sum += abs(sub_gf.start - sub_gf.end) + 1
        elif blat_hit.strand == '-' or blat_hit.strand == -1:
            for sub_gf in sorted(sub_feature, key=lambda x: x.start, reverse=True):
                if sub_gf.type == 'CDS':
                    plus_phase = 3 - (cds_len_sum % 3)
                    if plus_phase == 0:
                        phase_tmp = 0
                    else:
                        phase_tmp = 3 - plus_phase
                    sub_gf.phase = phase_tmp
                    # sub_gf.qualifiers["phase"] = [sub_gf.phase]
                    # sub_gf.qualifiers["phase2"] = phase_tmp
                    # sub_gf.phase2 = sub_gf.phase
                    cds_len_sum += abs(sub_gf.start - sub_gf.end) + 1

        mRNA_start = min(site_list)
        mRNA_end = max(site_list)

        blat_mRNA = GenomeFeature(id=blat_hit.id, type="mRNA", chr_loci=ChrLoci(chr_id=blat_hit.chr_id, strand=blat_hit.strand, start=mRNA_start, end=mRNA_end), sub_features=sub_feature)

        blat_mRNA.blat_hit = blat_hit
        blat_mRNA.good_cds = True

    else:
        blat_mRNA = GenomeFeature(id=blat_hit.id, type="mRNA", chr_loci=ChrLoci(chr_id=blat_hit.chr_id, strand=blat_hit.strand, start=0, end=0), sub_features=None)
        blat_mRNA.good_cds = False
        blat_mRNA.blat_hit = blat_hit

    return blat_mRNA


def hsp_judgment(blast_hsp):
    q_len = int(blast_hsp.query.qLen)
    s_len = int(blast_hsp.subject.Hit_len)

    if blast_hsp.Hsp_query_from == 1 and blast_hsp.Hsp_hit_from == 1 and q_len == blast_hsp.Hsp_query_to and s_len == blast_hsp.Hsp_hit_to and blast_hsp.Hsp_align_len == blast_hsp.Hsp_query_to and blast_hsp.Hsp_identical_site == blast_hsp.Hsp_query_to and blast_hsp.Hsp_gaps == 0:
        return True, 0, "perfect hit"

    elif blast_hsp.Hsp_identical_ratio < 0.95 or (
            blast_hsp.Hsp_query_to - blast_hsp.Hsp_query_from + 1) / q_len < 0.9:
        return False, 2, "low identity or coverage"

    else:
        return True, 1, "good hit"

def blat_hit_judgment(blat_cdna_seq, old_cdna_seq, tmp_dir):
    # print(blat_hit)

    blast_results = blastn_pair_running(('query', old_cdna_seq), ('subject', blat_cdna_seq),
                                        tmp_dir, False)

    if len(blast_results['query'].hit) < 1:
        return False, None, "No blast hit"

    good_hsp = []
    for hsp in blast_results['query'].hit[0].hsp:
        good_hsp_flag, note_code, note_hsp = hsp_judgment(hsp)
        if good_hsp_flag:
            good_hsp.append((hsp, note_code, note_hsp))

    if len(good_hsp) < 1:
        return False, None, "No good hit"

    best_hsp = sorted(good_hsp, key=lambda x: x[1])[0]

    return True, best_hsp[0], best_hsp[2]

def extract_give_feature_seq(give_type, sub_features_list, strand, genome_file=None, genome_dict=None):
    get_seq = ''

    if strand == 1 or strand == "+":
        feature_list = sorted([ft for ft in sub_features_list if ft.type == give_type],
                              key=lambda x: int(x.start), reverse=False)
    else:
        feature_list = sorted([ft for ft in sub_features_list if ft.type == give_type],
                              key=lambda x: int(x.start), reverse=True)

    for ft in feature_list:
        if genome_dict:
            get_seq += ft.get_sequence_quick(genome_dict).seq
        else:
            get_seq += ft.get_sequence(genome_file).seq

    return get_seq

# def map_old_gene_to_new_assembly(mRNA, blat_hit_list, old_chr_id, old_genome_fasta_file, new_genome_fasta_file,
#                                  tmp_dir, load_genome_into_mem=False):
def map_old_gene_to_new_assembly(mRNA, blat_hit_list, old_chr_id, tmp_dir):

    mRNA_tmp_dir = tmp_dir + "/" + mRNA.id
    mkdir(mRNA_tmp_dir, True)

    pyb_file = mRNA_tmp_dir + "/blat_mRNA.pyb"
    if not os.path.exists(pyb_file):

        # make sure old gene model is good, means cds is real ORF
        # if load_genome_into_mem:
        #     cds_seq = extract_give_feature_seq('CDS', mRNA.sub_features, mRNA.strand, genome_dict=old_genome_dict)
        # else:
        #     cds_seq = extract_give_feature_seq('CDS', mRNA.sub_features, mRNA.strand, genome_file=old_genome_fasta_file)
        cds_seq = mRNA.cds_seq

        good_orf, phase, aa_seq = cds_judgment(cds_seq)
        mRNA.good_cds = good_orf

        if good_orf:
            # get good blat hit
            # if load_genome_into_mem:
            #     old_cdna_seq = extract_give_feature_seq('exon', mRNA.sub_features, mRNA.strand, genome_dict=old_genome_dict)
            # else:
            #     old_cdna_seq = extract_give_feature_seq('exon', mRNA.sub_features, mRNA.strand, genome_file=old_genome_fasta_file)
            old_cdna_seq = mRNA.cdna_seq

            good_blat = []
            for blat_hit in blat_hit_list[:10]:
                # if load_genome_into_mem:
                #     blat_cdna_seq = extract_give_feature_seq("match_part", blat_hit.sub_features, blat_hit.strand, genome_dict=new_genome_dict)
                # else:
                #     blat_cdna_seq = extract_give_feature_seq("match_part", blat_hit.sub_features, blat_hit.strand, genome_file=new_genome_fasta_file)
                blat_cdna_seq = blat_hit.cdna_seq

                good_blat_flag, best_hsp, best_hsp_note = blat_hit_judgment(blat_cdna_seq,
                                                                            old_cdna_seq,
                                                                            mRNA_tmp_dir)

                blat_hit.hsp_note = best_hsp_note

                # print(best_hsp_note)

                if good_blat_flag:
                    good_blat.append(
                        (blat_hit, best_hsp, blat_cdna_seq))

            blat_mRNA_list = []
            for blat_hit, best_hsp, blat_cdna_seq in good_blat:
                blat_mRNA = generate_new_feature(
                    mRNA, phase, blat_cdna_seq, best_hsp, blat_hit)
                mRNA.chr_id = old_chr_id
                blat_mRNA.old_mRNA = mRNA
                blat_mRNA.best_hsp = best_hsp
                blat_mRNA_list.append(blat_mRNA)
        else:
            blat_mRNA_list = None

        OUT = open(pyb_file, 'wb')
        pickle.dump(blat_mRNA_list, OUT)
        OUT.close()

    else:
        TEMP = open(pyb_file, 'rb')
        blat_mRNA_list = pickle.load(TEMP)
        TEMP.close()

    return blat_mRNA_list

def blat_hit_load(blat_gff_file, feature_type):
    
    dict_tmp = {}

    gff_dict = read_gff_file(blat_gff_file)

    for type in gff_dict:
        for gf_id in gff_dict[type]:
            gf = gff_dict[type][gf_id]
            
            # single exon
            if gf.type != 'inferred_parent':
                new_gf = GenomeFeature(id=gf.qualifiers['Parent'][0], type='inferred_parent', chr_loci=gf.chr_loci, qualifiers={'ID': gf.qualifiers['Parent']}, sub_features=[gf])
                gf = new_gf

            # add new attr            
            gf.target = gf.sub_features[0].qualifiers['Target'][0].split()[0]
            gf.score = float(gf.sub_features[0].qualifiers['score'][0])
            gf.query_type = feature_type

            # parse sub_feature
            q_site_range = []
            for sf in gf.sub_features:
                target_info = sf.qualifiers['Target'][0].split()
                query_range = [int(target_info[1]), int(target_info[2])]
                sf.target = target_info[0]
                sf.q_start = min(query_range)
                sf.q_end = max(query_range)
                q_site_range.append(sf.q_start)
                q_site_range.append(sf.q_end)

            gf.q_start = min(q_site_range)
            gf.q_end = max(q_site_range)

            if gf.target not in dict_tmp:
                dict_tmp[gf.target] = []

            dict_tmp[gf.target].append(gf)

    for i in dict_tmp:
        dict_tmp[i] = sorted(
            dict_tmp[i], key=lambda x: x.score, reverse=True)

    # print(blat_gff_file + ".OK")
    return dict_tmp

def split_blat_gff(blat_gff_file, split_prefix, target_per_file):
    file_num = 0
    file_list = []
    with open(blat_gff_file, 'r') as f:
        last_t_id = ''
        save_target = 0
        for each_line in f:
            mbj = re.findall('Target=(\S+)', each_line)
            if len(mbj) == 0:
                continue
            t_id = mbj[0]
            if t_id != last_t_id:
                save_target += 1
                if save_target == target_per_file or file_num == 0:
                    if file_num > 0:
                        F1.close()
                    F1 = open("%s_%d.gff" % (split_prefix, file_num), 'w')
                    file_list.append("%s_%d.gff" % (split_prefix, file_num))
                    file_num += 1
                    save_target = 0
                last_t_id = t_id
            F1.write(each_line)
    return file_list

def split_and_load_blat_hit(raw_blat_gff_file, feature_type, split_dir, threads=80, target_per_file=1):
    mkdir(split_dir, False)

    split_file_list = split_blat_gff(raw_blat_gff_file, split_dir+"/split", target_per_file=target_per_file)
    # print('finished split')

    args_list = []
    for split_file in split_file_list:
        args_list.append((split_file, feature_type))

    mlt_out = multiprocess_running(blat_hit_load, args_list, threads, silence=False)

    dict_tmp = {}
    for i in mlt_out:
        for j in mlt_out[i]['output']:
            dict_tmp[j] = mlt_out[i]['output'][j]

    return dict_tmp

def get_cds_phase(gf):
    if gf.type == 'CDS':
        gf.qualifiers["phase"] = gf.phase
    if gf.sub_features and len(gf.sub_features) > 0:
        for sf in gf.sub_features:
            get_cds_phase(sf)

def MapOldAnno_main(args):

    if args.tmp_dir is None:
        args.tmp_dir = os.getcwd() + '/tmp'

    
    mkdir(args.tmp_dir, True)
    print("tmp dir is : %s" % args.tmp_dir)

    pyb_file = args.tmp_dir + "/data_load.pyb"
    if not os.path.exists(pyb_file):
        # read old gff file

        old_gff_dict = read_gff_file(args.old_gff)
        old_gene_gff = old_gff_dict['gene']

        # read cds and cDNA blat results
        split_dir = args.tmp_dir + "/split"
        cdna_dict = split_and_load_blat_hit(args.cDNA_gff, 'cDNA', split_dir, threads=args.num_threads, target_per_file=1)
        # cdna_dict = blat_hit_load(args.cDNA_gff, 'cDNA')

        for old_mRNA_id in cdna_dict:
            for i in range(len(cdna_dict[old_mRNA_id])):
                cdna_dict[old_mRNA_id][i].rank = i

        # cds_dict = blat_hit_load(args.CDS_gff, 'CDS')

        OUT = open(pyb_file, 'wb')
        pickle.dump((old_gene_gff, cdna_dict), OUT)
        OUT.close()
    else:
        TEMP = open(pyb_file, 'rb')
        old_gene_gff, cdna_dict = pickle.load(TEMP)
        TEMP.close()

    # just use cDNA and old gff
    blat_mRNA_dir = args.tmp_dir + "/blat_mRNA"
    mkdir(blat_mRNA_dir, True)

    old_genome_dict = read_fasta(args.old_genome)[0]
    new_genome_dict = read_fasta(args.new_genome)[0]

    # extract need seq:
    args_list = []
    for old_gene_id in old_gene_gff:
        # print(old_gene_id)
        gene = old_gene_gff[old_gene_id]
        for mRNA in gene.sub_features:
            if not mRNA.id in cdna_dict:
                continue

            cds_seq = extract_give_feature_seq('CDS', mRNA.sub_features, mRNA.strand, genome_dict=old_genome_dict)
            cdna_seq = extract_give_feature_seq('exon', mRNA.sub_features, mRNA.strand, genome_dict=old_genome_dict)
            mRNA.cds_seq = cds_seq
            mRNA.cdna_seq = cdna_seq

            blat_hit_list = []
            for blat_hit in cdna_dict[mRNA.id]:
                blat_cdna_seq = extract_give_feature_seq("match_part", blat_hit.sub_features, blat_hit.strand, genome_dict=new_genome_dict)
                blat_hit.cdna_seq = blat_cdna_seq
                blat_hit_list.append(blat_hit)

            args_list.append((mRNA, blat_hit_list, gene.chr_id, blat_mRNA_dir))

    map_output = multiprocess_running(
        map_old_gene_to_new_assembly, args_list, args.num_threads, silence=False)

    huge_blat_mRNA_list = []
    for i in map_output:
        if map_output[i]['output'] is None:
            continue
        for j in map_output[i]['output']:
            if j.good_cds:
                huge_blat_mRNA_list.append(j)

    blat_mRNA_cluster = cluster_of_chr_loci(huge_blat_mRNA_list, 0.5)

    write_blat_mRNA = []
    for contig in blat_mRNA_cluster:
        for strand in blat_mRNA_cluster[contig]:
            group_dict = blat_mRNA_cluster[contig][strand]
            for group_id in group_dict:
                gf_list = group_dict[group_id]['list']
                best_gf = sorted(
                    gf_list, key=lambda x: x.best_hsp.Hsp_score, reverse=True)[0]
                best_gf.used = True
                write_blat_mRNA.append(best_gf)

    write_blat_gene = []
    for mRNA in write_blat_mRNA:
        old_name = mRNA.id
        gene_name = old_name + ".gene"
        mRNA_name = old_name + ".mRNA"

        gene = GenomeFeature(id=gene_name, type='gene', chr_loci=mRNA.chr_loci)

        mRNA_sub_features = []
        for sub_mrna in mRNA.sub_features:
            sub_mrna2 = deepcopy(sub_mrna)
            if sub_mrna.type == 'CDS':
                sub_mrna2.qualifiers["phase"] = sub_mrna.phase
            mRNA_sub_features.append(sub_mrna2)

        # for sub_mrna in mRNA_sub_features:
        #     if sub_mrna.type == 'CDS':
        #         print(sub_mrna.qualifiers["phase"], sub_mrna.phase)

        mRNA.sub_features = mRNA_sub_features
        gene.sub_features = [mRNA]

        write_blat_gene.append(gene)

    write_gff_file(write_blat_gene, args.output_gff, source="blat", sort=True)
    # write_GenomeFeature_to_GFF(
    #     write_blat_gene, args.output_gff, source="blat")
    #
    # # write report
    # blat_mRNA_cluster_hash = {}
    # for contig in blat_mRNA_cluster:
    #     for strand in blat_mRNA_cluster[contig]:
    #         group_dict = blat_mRNA_cluster[contig][strand]
    #         for group_id in group_dict:
    #             group_range = group_dict[group_id]['range'][0]
    #             group_loci = ChrLoci(chr_id=contig, strand=strand, start=group_range[0], end=group_range[1])
    #             gf_list = group_dict[group_id]['list']
    #             for i in gf_list:
    #                 blat_mRNA_cluster_hash[i] = group_loci
    #
    # for i in map_output:
    #     mRNA, blat_hit_list, tmp1, tmp2, tmp3, tmp4 = map_output[i]['args']
    #     blat_mRNA_list = map_output[i]['output']
    #
    #     # old mRNA info
    #     if blat_mRNA_list is None:
    #         # old mRNA is not good cds
    #         old_cds_good = False
    #         blat_hit_passed_num = None
    #         blat_hit_total_num = len(cdna_dict[mRNA.id])
    #     else:
    #         old_cds_good = True
    #         blat_hit_passed_num = len(blat_mRNA_list)
    #         blat_hit_total_num = len(cdna_dict[mRNA.id])
    #
    #     # blat hit info
    #     if old_cds_good and blat_hit_passed_num > 0:
    #         mRNA = blat_mRNA_list[0].old_mRNA
    #         for blat_mRNA in blat_mRNA_list:
    #             blat_hit = blat_mRNA.blat_hit
    #             blat_hit_rank = blat_hit.rank
    #             blat_hit_note = blat_hit.hsp_note
    #             blat_cds_good = blat_mRNA.good_cds
    #             if hasattr(blat_mRNA, 'used'):
    #                 blat_used = blat_mRNA.used
    #             else:
    #                 blat_used = False
    #
    #             print(mRNA.id, old_cds_good, blat_hit_total_num, blat_hit_passed_num, blat_hit.name,blat_hit.get_fancy_name(),
    #                   blat_hit_rank, blat_hit_note, blat_cds_good, blat_used)


if __name__ == '__main__':
    ###
    class abc():
        pass

    args = abc()
    args.cDNA_gff = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca2/purge/MapOldAnno/all.cDNA.c1.0.gff"
    # args.cDNA_gff = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca2/purge/MapOldAnno/head.cDNA.c0.9.gff"
    args.old_gff = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/T99112N0.genome.gff3"
    args.old_genome = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca/T99112N0.genome.fasta"
    args.new_genome = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca2/purge/purge_haplotigs/curated.fasta"
    args.tmp_dir = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca2/purge/MapOldAnno/tmp"
    args.num_threads = 160
    args.output_gff = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phelipanche_aegyptiaca2/purge/MapOldAnno/MapOldAnno.gff"

    MapOldAnno_main(args)