# pysam for sam or bam file
import pysam
import time
import copy
from toolbiox.lib.common.os import remove_file_name_suffix, cmd_run, multiprocess_running
from toolbiox.lib.xuyuxing.base.common_command import flag_maker, flag_parse, flag_filter
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.genome.seq_base import read_fastq_big, read_fasta_by_faidx
from pysam import VariantFile
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
import pickle
import numpy as np

# for bam or sam file

"""
bam_file = '/lustre/home/xuyuxing/Work/Other/saif/Meth/Con_1.bsmap.bam'

sam file flag:    
1:   read paired
2:   read mapped in proper pair
3:   read unmapped
4:   mate unmapped
5:   read reverse strand
6:   mate reverse strand
7:   first in pair
8:   second in pair
9:   not primary alignment (secondary alignment)
10:  read fails platform/vendor quality checks
11:  read is PCR or optical duplicate
12:  supplementary alignment
"""
# good flag have two filter, need and exclude, used as: flag_filter(83, *good_pair_flag)
good_pair_flag = (flag_maker([1, 2]), flag_maker([3, 4, 10, 12]))
just_pair_flag = (flag_maker([1]), 0)


def parse_bam_by_reads(bam_file):
    """
    parse a bam file, and yield all hit for a read one time
    The bam file should sorted by reads name (samtools sort -n), yield one read one time
    """
    bf = pysam.AlignmentFile(bam_file, 'r')
    read_tmp_record = []
    for r in bf.fetch(until_eof=True):
        if len(read_tmp_record) == 0 or r.query_name == read_tmp_record[-1].query_name:
            read_tmp_record.append(r)
            continue
        else:
            yield read_tmp_record
            read_tmp_record = [r]
    if len(read_tmp_record) != 0:
        yield read_tmp_record
    bf.close()


def pair_read_hit(read_hit_list):
    """
    given a list for hits from same read, get tuple for same template pairs, and return a tuple list
    """

    tmp_id = 0
    read_hit_dir = {}
    for read_hit in read_hit_list:
        read_hit_dir[tmp_id] = read_hit
        tmp_id = tmp_id + 1

    used_hit = []
    output_pair_list = []
    for hit_id in range(0, len(read_hit_list)):
        if hit_id in used_hit:
            continue
        used_hit.append(hit_id)
        hit_tmp = read_hit_dir[hit_id]
        # find good read pair
        if flag_filter(hit_tmp.flag, *good_pair_flag):
            pair_chr = hit_tmp.reference_name
            pair_site = hit_tmp.mpos
            pair_hit_id_list = [j for j in read_hit_dir if
                                (j not in used_hit) and flag_filter(read_hit_dir[j].flag, *good_pair_flag) and
                                read_hit_dir[
                                    j].reference_name == pair_chr and read_hit_dir[j].pos == pair_site]

            if len(pair_hit_id_list) == 0:
                if hit_tmp.is_read1:
                    output_pair_list.append((hit_tmp, None))
                else:
                    output_pair_list.append((None, hit_tmp))
            else:
                pair_hit_id = pair_hit_id_list[0]
                pair_hit_tmp = read_hit_dir[pair_hit_id]
                used_hit.append(pair_hit_id)
                if hit_tmp.is_read1:
                    output_pair_list.append((hit_tmp, pair_hit_tmp))
                else:
                    output_pair_list.append((pair_hit_tmp, hit_tmp))
        elif flag_filter(hit_tmp.flag, *just_pair_flag):
            if hit_tmp.is_read1:
                output_pair_list.append((hit_tmp, None))
            else:
                output_pair_list.append((None, hit_tmp))
        else:
            raise ValueError("Flag should not happen!")

    return output_pair_list


def split_read_sorted_bam(bam_file, reads_number_per_file=10000000, log_file=None):
    module_log = logging_init("split_read_sorted_bam", log_file)
    module_log.info('received a call to "split_read_sorted_bam"')

    with pysam.AlignmentFile(bam_file, "rb") as bf:
        raw_bf_header_dict = bf.header.as_dict()

    output_prefix = remove_file_name_suffix(bam_file, 1) + ".split"

    output_file_list = []

    output_file_id = 0
    output_file_name_tmp = "%s.%d.bam" % (output_prefix, output_file_id)
    module_log.info('begin write %s' % output_file_name_tmp)
    output_file_list.append(output_file_name_tmp)
    tmp_header = raw_bf_header_dict
    tmp_header['CO'] = ['split file %d' % output_file_id]
    bam_out = pysam.AlignmentFile(
        output_file_name_tmp, "wb", header=tmp_header)

    read_num = 0
    start_time = time.time()
    for read_hit_list in parse_bam_by_reads(bam_file):
        read_num = read_num + 1
        for read_hit in read_hit_list:
            bam_out.write(read_hit)

        round_time = time.time()
        if round_time - start_time > 10:
            module_log.info("\tparsed reads: %d" % (read_num))
            start_time = round_time

        if read_num % reads_number_per_file == 0:
            bam_out.close()
            output_file_id = output_file_id + 1
            output_file_name_tmp = "%s.%d.bam" % (
                output_prefix, output_file_id)
            module_log.info('begin write %s' % output_file_name_tmp)
            tmp_header['CO'] = ['split file %d' % output_file_id]
            bam_out = pysam.AlignmentFile(
                output_file_name_tmp, "wb", header=tmp_header)
            output_file_list.append(output_file_name_tmp)

    if not bam_out.is_closed:
        bam_out.close()

    del module_log.handlers[:]
    return output_file_list


def hit_counter(bam_file, log_file=None):
    """
    parse a bam file and return the hit counter for every reads
    The bam file should sorted by read name (samtools sort -n)

    """
    module_log = logging_init("hit_counter", log_file)
    module_log.info('received a call to "hit_counter"')

    read_num = 0
    start_time = time.time()
    hit_count_dist = {}
    for read_hit_list in parse_bam_by_reads(bam_file):
        read_num = read_num + 1

        round_time = time.time()
        if round_time - start_time > 10:
            module_log.info("\tparsed reads: %d" % (read_num))
            start_time = round_time

        read_hit_list = pair_read_hit(read_hit_list)
        good_pair_hit_num = len(
            [i for i in read_hit_list if
             (not i[0] is None) and (not i[1] is None) and flag_filter(i[0].flag, *good_pair_flag) and flag_filter(
                 i[1].flag, *good_pair_flag)])

        if good_pair_hit_num not in hit_count_dist:
            hit_count_dist[good_pair_hit_num] = 0

        hit_count_dist[good_pair_hit_num] = hit_count_dist[good_pair_hit_num] + 1

    module_log.info('finished parser"')
    del module_log.handlers[:]
    return hit_count_dist


def split_sorted_bam_by_contig(bam_file, log_file=None, change_header=True):
    module_log = logging_init("split_sorted_bam_by_contig", log_file)
    module_log.info('received a call to "split_sorted_bam_by_contig"')

    output_prefix = remove_file_name_suffix(bam_file, 1)

    with pysam.AlignmentFile(bam_file, "rb") as bf:
        raw_bf_header_dict = bf.header.as_dict()

    contig_list = [i['SN'] for i in raw_bf_header_dict['SQ']]
    contig_file_dict = {}

    for i in raw_bf_header_dict['SQ']:
        contig = i['SN']
        contig_length = i['LN']
        contig_file_dict[contig] = {}
        contig_file_dict[contig]['file'] = output_prefix + \
            "." + contig + ".bam"
        contig_file_dict[contig]['head'] = {}
        for j in raw_bf_header_dict:
            if j == 'SQ':
                contig_file_dict[contig]['head']['SQ'] = [
                    {'SN': contig, 'LN': contig_length}]
            else:
                contig_file_dict[contig]['head'][j] = raw_bf_header_dict[j]

    bf = pysam.AlignmentFile(bam_file, 'r')
    for contig in contig_list:
        output_file = contig_file_dict[contig]['file']
        module_log.info('begin write %s' % output_file)
        tmp_header = contig_file_dict[contig]['head']
        tmp_header['CO'] = ['split file %s' % output_file]
        # print(tmp_header)
        if change_header:
            bam_out = pysam.AlignmentFile(output_file, "wb", header=tmp_header)
        else:
            bam_out = pysam.AlignmentFile(
                output_file, "wb", header=raw_bf_header_dict)

        for r in bf.fetch(contig):
            bam_out.write(r)

        bam_out.close()

    bf.close()

    del module_log.handlers[:]
    return contig_file_dict


def get_read_name_list_from_fastq(fastq_file_name, output_file_name):
    """
    get_read_name_list_from_fastq
    """
    with open(output_file_name, 'w') as f:
        for record in read_fastq_big(fastq_file_name, gzip_flag=True):
            f.write(record[0].seqname_short() + "\n")

    return output_file_name


def index_bam_file(bam_file):
    """
    samtools index bam_file
    """
    bamfile = pysam.AlignmentFile(bam_file, 'rb')
    name_indexed = pysam.IndexedReads(bamfile)
    name_indexed.build()
    return name_indexed


def extract_aln_by_reads(reads_name, name_indexed):
    output_list = []
    try:
        name_indexed.find(reads_name)
    except KeyError:
        pass
    else:
        iterator = name_indexed.find(reads_name)
        output_list = []
        for x in iterator:
            output_list.append(x)

    return output_list


def get_best_alignment_match_number(read_aln_list):
    valid_aln_list = [alignedsegment for alignedsegment in read_aln_list if not (
        alignedsegment.is_secondary or alignedsegment.is_supplementary)]

    # TODO


def extract_reads_from_bam_file(reads_name_list, input_bam_file, output_bam_file):

    bamfile = pysam.AlignmentFile(input_bam_file, 'rb')
    name_indexed = pysam.IndexedReads(bamfile)
    name_indexed.build()
    header = bamfile.header.copy()
    out = pysam.Samfile(output_bam_file, 'wb', header=header)

    for name in reads_name_list:
        try:
            name_indexed.find(name)
        except KeyError:
            pass
        else:
            iterator = name_indexed.find(name)
            for x in iterator:
                out.write(x)


# for bcf or vcf file


def compare_two_bcf_file(A_bcf_file, B_bcf_file):

    A_bcf = VariantFile(A_bcf_file)
    A_site_dict = {}
    for rec in A_bcf.fetch():
        A_site_dict[(rec.contig, rec.pos)] = rec

    B_bcf = VariantFile(B_bcf_file)
    B_site_dict = {}
    for rec in B_bcf.fetch():
        B_site_dict[(rec.contig, rec.pos)] = rec

    onlyA_site = set(A_site_dict.keys()) - set(B_site_dict.keys())
    onlyB_site = set(B_site_dict.keys()) - set(A_site_dict.keys())
    AB_site = set(A_site_dict.keys()) & set(B_site_dict.keys())

    return list(onlyA_site), list(onlyB_site), list(AB_site), A_site_dict, B_site_dict


def filter_EMS_snp(rec):
    return rec.alleles == ('G', 'A') or rec.alleles == ('C', 'T')


def get_AD_dict(vcf_line):
    vs = vcf_line.strip()

    v_info = vs.split("\t")
    g_type = [v_info[3]] + v_info[4].split(",")

    info_dict = dict(zip(v_info[8].split(":"), v_info[9].split(":")))

    if 'AD' in info_dict:
        AD_tuple = [int(i) for i in info_dict['AD'].split(",")]
        output = {i: j for i, j in zip(g_type, AD_tuple) if i != '<NON_REF>'}
        output = {i:output[i] for i in output if output[i] != 0}
        return output
    else:
        if 'DP' in info_dict:
            DP_value = int(info_dict['DP'])
            return {g_type[0]: DP_value}
        else:
            return None

def get_AD_dict_more_sample(vcf_line, sample_num=1):
    vs = vcf_line.strip()

    v_info = vs.split("\t")
    g_type = [v_info[3]] + v_info[4].split(",")

    output_list = []
    for rank in range(1,sample_num+1):
        info_dict = dict(zip(v_info[8].split(":"), v_info[8+rank].split(":")))

        if 'AD' in info_dict:
            AD_tuple = [int(i) for i in info_dict['AD'].split(",")]
            output = {i: j for i, j in zip(g_type, AD_tuple) if i != '<NON_REF>'}
            output = {i:output[i] for i in output if output[i] != 0}
        else:
            if 'DP' in info_dict:
                DP_value = int(info_dict['DP'])
                output = {g_type[0]: DP_value}

        output_list.append(output)

    return output_list


def BSA_eu_dist(g1_AD_dict, g2_AD_dict, min_depth=8, max_depth=250):
    c = ['A', 'T', 'C', 'G']

    sum1 = sum([g1_AD_dict[i] for i in c if i in g1_AD_dict])
    sum2 = sum([g2_AD_dict[i] for i in c if i in g2_AD_dict])

    if sum1 < min_depth or sum2 < min_depth or sum1 > max_depth or sum2 > max_depth:
        return 0.0

    g1 = {}
    for i in c:
        if sum1 == 0 or i not in g1_AD_dict:
            g1[i] = 0.0
        else:
            g1[i] = g1_AD_dict[i]/sum1

    g2 = {}
    for i in c:
        if sum2 == 0 or i not in g2_AD_dict:
            g2[i] = 0.0
        else:
            g2[i] = g2_AD_dict[i]/sum2

    return(np.sqrt(sum([np.square(g1[i] - g2[i]) for i in c])))



def BSA_ED_in_one_range(chr_id, start, end, group1_g_bcf, group2_g_bcf, min_depth=8, max_depth=250):
    g1_bcf = VariantFile(group1_g_bcf)
    g2_bcf = VariantFile(group2_g_bcf)

    output_dict = {}
    output_dict[chr_id] = {}

    g1s_dict = {i.pos:i for i in g1_bcf.fetch(chr_id, start, end)}
    g2s_dict = {i.pos:i for i in g2_bcf.fetch(chr_id, start, end)}

    for i in range(start, end + 1):
        site = i + 1

        if site in g1s_dict and site in g2s_dict:


            g1s = g1s_dict[site]
            g2s = g2s_dict[site]

            g1_AD_dict = get_AD_dict(g1s.__str__())
            g2_AD_dict = get_AD_dict(g2s.__str__())

            if g1_AD_dict is None or g2_AD_dict is None:
                continue

            ED = BSA_eu_dist(g1_AD_dict, g2_AD_dict, min_depth, max_depth)

            if ED > 0.0:
                output_dict[chr_id][site] = ED

    return output_dict

def BSA_ED_filter(group1_g_bcf, group2_g_bcf, genome_file, min_depth=8, max_depth=250, bin_length=1000000, threads=10):
    """
    # bcf should have index
    bcftools view -O b -o SGJ-R.g.bcf SGJ-R.g.vcf
    bcftools index SGJ-R.g.bcf
    """
    fasta_dict = read_fasta_by_faidx(genome_file)

    args_list = []
    output_dict = {}
    for chr_id in fasta_dict:
        output_dict[chr_id] = {}
        length = fasta_dict[chr_id].len()
        for i, s, e in split_sequence_to_bins(length, bin_length):
            args_list.append((chr_id, s, e, group1_g_bcf, group2_g_bcf, min_depth, max_depth))

    mp_out_dict = multiprocess_running(
        BSA_ED_in_one_range, args_list, threads, silence=False)

    for i in mp_out_dict:
        tmp_dict = mp_out_dict[i]['output']
        for j in tmp_dict:
            for k in tmp_dict[j]:
                output_dict[j][k] = tmp_dict[j][k]

    return output_dict

def BSA_mutmap_in_one_range(chr_id, start, end, mutmap_vcf, min_depth=8, max_depth=250):
    bcf = VariantFile(mutmap_vcf)

    output_dict = {}
    output_dict[chr_id] = {}

    gs_dict = {i.pos:i for i in bcf.fetch(chr_id, start, end)}

    for i in range(start, end + 1):
        site = i + 1

        if site in gs_dict:

            gs = gs_dict[site]

            g1_AD_dict, g2_AD_dict = get_AD_dict_more_sample(gs.__str__(), sample_num=2)

            if g1_AD_dict == {} or g2_AD_dict == {}:
                continue

            ED = BSA_eu_dist(g1_AD_dict, g2_AD_dict, min_depth, max_depth)

            # print(chr_id, site, g1_AD_dict, g2_AD_dict, ED)

            if ED > 0.0:
                output_dict[chr_id][site] = ED

    return output_dict

def BSA_mutmap_filter(mutmap_vcf, genome_file, min_depth=8, max_depth=250, bin_length=1000000, threads=10):
    """
    # bcf should have index
    bcftools view -O b -o SGJ-R.g.bcf SGJ-R.g.vcf
    bcftools index SGJ-R.g.bcf
    """
    fasta_dict = read_fasta_by_faidx(genome_file)

    args_list = []
    output_dict = {}
    for chr_id in fasta_dict:
        output_dict[chr_id] = {}
        length = fasta_dict[chr_id].len()
        for i, s, e in split_sequence_to_bins(length, bin_length):
            args_list.append((chr_id, s, e, mutmap_vcf, min_depth, max_depth))

    mp_out_dict = multiprocess_running(
        BSA_mutmap_in_one_range, args_list, threads, silence=False)

    for i in mp_out_dict:
        tmp_dict = mp_out_dict[i]['output']
        for j in tmp_dict:
            for k in tmp_dict[j]:
                output_dict[j][k] = tmp_dict[j][k]

    return output_dict


if __name__ == "__main__":

    for i in ["ZJXA5242", "ZJXA5243", "ZJXA5244", "ZJXA5245", "ZJXA5246"]:
        A_bcf_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/SURVEY.vcf.gz'
        B_bcf_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/%s.snp.filter.vcf.gz' % i
        output_B_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/%s.snp.filter.again.vcf' % i

        onlyA_site, onlyB_site, AB_site, A_site_dict, B_site_dict = compare_two_bcf_file(
            A_bcf_file, B_bcf_file)

        bcf_in = VariantFile(B_bcf_file)  # auto-detect input format
        bcf_out = VariantFile(output_B_file, 'w', header=bcf_in.header)
        num = 0
        for i in onlyB_site:
            rec = B_site_dict[i]
            print(rec.alleles)
            if filter_EMS_snp(rec):
                print('True')
                num += 1
                bcf_out.write(rec)
        bcf_out.close()

    for i in ["ZJXA5242", "ZJXA5243", "ZJXA5244", "ZJXA5245", "ZJXA5246"]:
        good_vcf_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/%s.snp.filter.again.vcf' % i
        output_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/%s.snp.top30.txt' % i

        B_bcf = VariantFile(good_vcf_file)
        B_site_dict = {}
        for rec in B_bcf.fetch():
            B_site_dict[(rec.contig, rec.pos)] = rec

        with open(output_file, 'w') as f:
            for id_now in sorted(B_site_dict.keys(), key=lambda x: B_site_dict[x].qual, reverse=True)[0:30]:
                chr_id, site = id_now
                rec = B_site_dict[id_now]

                f.write(rec.__str__())

                cmd_string = "samtools faidx /lustre/home/xuyuxing/Database/Cuscuta/Cau/raw_data/mutant_reseq2_202010/Cuscuta.genome.v1.1.fasta %s:%d-%d" % (
                    chr_id, site-200, site+200)
                fl, o, e = cmd_run(cmd_string)
                f.write(o+"\n")

    # BSA
    import os
    import pickle

    group1_g_bcf = '/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/SGJ-R.g.bcf'
    group2_g_bcf = '/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/SGJ-S.g.bcf'
    genome_file = '/lustre/home/xuyuxing/Work/Other/Guojin/tomato_collinear/genome_data/Sly/S_lycopersicum_chromosomes.4.00.fa'
    
    ED_dict_pickle = '/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/BSA_ED.pyb'

    if not os.path.exists(ED_dict_pickle):

        ED_dict = BSA_ED_filter(group1_g_bcf, group2_g_bcf, genome_file, min_depth=8, max_depth=250, bin_length=1000000, threads=56)

        OUT = open(ED_dict_pickle, 'wb')
        pickle.dump(ED_dict, OUT)
        OUT.close()
    
    else:
        TEMP = open(ED_dict_pickle, 'rb')
        ED_dict = pickle.load(TEMP)
        TEMP.close()

    g1_bcf = VariantFile(group1_g_bcf)
    g2_bcf = VariantFile(group2_g_bcf)


    def ems_mutant(WT_like_AD_dict, mutant_like_AD_dict, A='WT', more_strict=False):
        True_flag = False
        strict_flag = False

        if A == 'WT':
            # WT_like_AD_dict vs mutant_like_AD_dict: G/A, GA/A, C/T, CT/T
            if len(mutant_like_AD_dict) == 1:
                if 'A' in mutant_like_AD_dict:
                    if len(WT_like_AD_dict) == 1 and 'G' in WT_like_AD_dict:
                        True_flag = True

                    if len(WT_like_AD_dict) == 2 and 'G' in WT_like_AD_dict and 'A' in WT_like_AD_dict:
                        True_flag = True
                        if WT_like_AD_dict['G'] > WT_like_AD_dict['A']:
                            strict_flag = True

                elif 'T' in mutant_like_AD_dict:
                    if len(WT_like_AD_dict) == 1 and 'C' in WT_like_AD_dict:
                        True_flag = True

                    if len(WT_like_AD_dict) == 2 and 'C' in WT_like_AD_dict and 'T' in WT_like_AD_dict:
                        True_flag = True
                        if WT_like_AD_dict['C'] > WT_like_AD_dict['T']:
                            strict_flag = True

        elif A == 'MT':
            # WT_like_AD_dict vs mutant_like_AD_dict: G/A, G/GA, C/T, C/CT
            if len(WT_like_AD_dict) == 1:
                if 'G' in WT_like_AD_dict:
                    if len(mutant_like_AD_dict) == 1 and 'A' in mutant_like_AD_dict:
                        True_flag = True

                    if len(mutant_like_AD_dict) == 2 and 'G' in mutant_like_AD_dict and 'A' in mutant_like_AD_dict:
                        True_flag = True
                        if mutant_like_AD_dict['A'] > mutant_like_AD_dict['G']:
                            strict_flag = True

                elif 'C' in WT_like_AD_dict:
                    if len(mutant_like_AD_dict) == 1 and 'T' in mutant_like_AD_dict:
                        True_flag = True

                    if len(mutant_like_AD_dict) == 2 and 'C' in mutant_like_AD_dict and 'T' in mutant_like_AD_dict:
                        True_flag = True
                        if mutant_like_AD_dict['T'] > mutant_like_AD_dict['C']:
                            strict_flag = True

        if more_strict:
            return strict_flag
        else:
            return True_flag


    from toolbiox.lib.xuyuxing.math.stats import fisher_enrichment

    def heterozygote_pvalue(AD_dict, ratio_dict):
        """
        ratio_dict = {'G':2,'A':1}
        """
        
        for i in ratio_dict:
            if i not in AD_dict:
                return None
        
        key_list = list(ratio_dict.keys())

        sum_obs = sum([AD_dict[i] for i in key_list])
        sum_ratio = sum([ratio_dict[i] for i in key_list])

        Contingency_table = [[(ratio_dict[i] / sum_ratio) * sum_obs for i in key_list], [AD_dict[i] for i in key_list]]

        # print(Contingency_table)

        oddsratio, pvalue = fisher_enrichment(Contingency_table)

        return pvalue

    num = 0 
    bsa_output_dict = {}
    for chr_id in ED_dict:
        for site in ED_dict[chr_id]:
            if ED_dict[chr_id][site] > 0.8:

                g1s_dict = {i.pos:i for i in g1_bcf.fetch(chr_id, site-100, site+100)}
                g2s_dict = {i.pos:i for i in g2_bcf.fetch(chr_id, site-100, site+100)}

                g1s = g1s_dict[site]
                g2s = g2s_dict[site]

                g1_AD_dict = get_AD_dict(g1s.__str__())
                g2_AD_dict = get_AD_dict(g2s.__str__())

                if ems_mutant(g1_AD_dict, g2_AD_dict, A='WT', more_strict=True):
                    num += 1

                    ratio_dict1 = {'G':2,'A':1}
                    ratio_dict2 = {'C':2,'T':1}

                    pvalue = heterozygote_pvalue(g1_AD_dict, ratio_dict1) or heterozygote_pvalue(g1_AD_dict, ratio_dict2)

                    bsa_output_dict[(chr_id,site)] = ED_dict[chr_id][site],pvalue,g1_AD_dict,g2_AD_dict

    gff_file = '/lustre/home/xuyuxing/Work/Other/Guojin/tomato_collinear/genome_data/Sly/ITAG4.1_gene_models.gff'

    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file

    gf_dict = read_gff_file(gff_file)
    gene_dict = gf_dict['gene']

    from interlap import InterLap
    cds_interlap = {}
    for g_id in gene_dict:
        gene = gene_dict[g_id]
        chr_id = gene.chr_id
        if chr_id not in cds_interlap:
            cds_interlap[chr_id] = {
                "+":InterLap(),
                "-":InterLap(),
            }

        for mRNA in gene.sub_features:
            for cds in mRNA.sub_features:
                if cds.type == 'CDS':
                    cds_interlap[chr_id][cds.strand].add((cds.start, cds.end, cds))

    gene_interlap = {}
    for g_id in gene_dict:
        gene = gene_dict[g_id]
        chr_id = gene.chr_id
        if chr_id not in gene_interlap:
            gene_interlap[chr_id] = {
                "+":InterLap(),
                "-":InterLap(),
            }

        gene_interlap[chr_id][gene.strand].add((gene.start, gene.end, gene))

    bas_cds_dict = {}
    for chr_id, site in bsa_output_dict:
        over_cds_list = list(cds_interlap[chr_id]['+'].find((site, site))) + list(cds_interlap[chr_id]['-'].find((site, site)))
        if len(over_cds_list) > 0:
            print(chr_id, site, bsa_output_dict[(chr_id, site)])
            bas_cds_dict[(chr_id, site)] = over_cds_list

    bas_gene_dict = {}
    for chr_id, site in bsa_output_dict:
        over_gene_list = list(gene_interlap[chr_id]['+'].find((site, site))) + list(gene_interlap[chr_id]['-'].find((site, site)))
        if len(over_gene_list) > 0:
            print(chr_id, site, bsa_output_dict[(chr_id, site)], over_gene_list[0][2].id)
            bas_gene_dict[(chr_id, site)] = over_gene_list


    cds = bas_cds_dict[('SL4.0ch10',28051333)][0][2]
    vars(cds)

    cds = bas_cds_dict[('SL4.0ch00', 166925)][0][2]
    vars(cds)                

    cds = bas_cds_dict[('SL4.0ch07', 8202167)][0][2]
    vars(cds)          

    with open("/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/all.site.txt", 'w') as f:
        for i in bsa_output_dict:
            a=bsa_output_dict[i]
            f.write("%s\t%s\t%s\t%s\t%s, %s\n" % (i[0],i[1],a[0],a[1],a[2].__str__(),a[3].__str__()))

    # BSA2
    import os
    import pickle

    mutmap_vcf = '/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/mutmap_dir/30_vcf/mutmap.vcf.gz'
    genome_file = '/lustre/home/xuyuxing/Work/Other/Guojin/tomato_collinear/genome_data/Sly/S_lycopersicum_chromosomes.4.00.fa'
    
    ED_dict_pickle = '/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/mutmap_dir/BSA_ED.pyb'

    if not os.path.exists(ED_dict_pickle):
        ED_dict = BSA_mutmap_filter(mutmap_vcf, genome_file, min_depth=8, max_depth=250, bin_length=1000000, threads=56)

        OUT = open(ED_dict_pickle, 'wb')
        pickle.dump(ED_dict, OUT)
        OUT.close()
    
    else:
        TEMP = open(ED_dict_pickle, 'rb')
        ED_dict = pickle.load(TEMP)
        TEMP.close()

    mm_bcf = VariantFile(mutmap_vcf)

    num = 0 
    bsa_output_dict = {}
    for chr_id in ED_dict:
        for site in ED_dict[chr_id]:
            if ED_dict[chr_id][site] > 0.5:
                

                mm_dict = {i.pos:i for i in mm_bcf.fetch(chr_id, site-100, site+100)}
                
                gs = mm_dict[site]

                g1_AD_dict, g2_AD_dict = get_AD_dict_more_sample(gs.__str__(), sample_num=2)

                if ems_mutant(g1_AD_dict, g2_AD_dict, A='WT', more_strict=True):
                    num += 1

                    ratio_dict1 = {'G':2,'A':1}
                    ratio_dict2 = {'C':2,'T':1}

                    pvalue = heterozygote_pvalue(g1_AD_dict, ratio_dict1) or heterozygote_pvalue(g1_AD_dict, ratio_dict2)

                    bsa_output_dict[(chr_id,site)] = ED_dict[chr_id][site],pvalue,g1_AD_dict,g2_AD_dict

    gff_file = '/lustre/home/xuyuxing/Work/Other/Guojin/tomato_collinear/genome_data/Sly/ITAG4.1_gene_models.gff'

    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file

    gf_dict = read_gff_file(gff_file)
    gene_dict = gf_dict['gene']

    from interlap import InterLap
    cds_interlap = {}
    for g_id in gene_dict:
        gene = gene_dict[g_id]
        chr_id = gene.chr_id
        if chr_id not in cds_interlap:
            cds_interlap[chr_id] = {
                "+":InterLap(),
                "-":InterLap(),
            }

        for mRNA in gene.sub_features:
            for cds in mRNA.sub_features:
                if cds.type == 'CDS':
                    cds_interlap[chr_id][cds.strand].add((cds.start, cds.end, cds))

    gene_interlap = {}
    for g_id in gene_dict:
        gene = gene_dict[g_id]
        chr_id = gene.chr_id
        if chr_id not in gene_interlap:
            gene_interlap[chr_id] = {
                "+":InterLap(),
                "-":InterLap(),
            }

        gene_interlap[chr_id][gene.strand].add((gene.start, gene.end, gene))

    bas_cds_dict = {}
    for chr_id, site in bsa_output_dict:
        over_cds_list = list(cds_interlap[chr_id]['+'].find((site, site))) + list(cds_interlap[chr_id]['-'].find((site, site)))
        if len(over_cds_list) > 0:
            print(chr_id, site, bsa_output_dict[(chr_id, site)])
            bas_cds_dict[(chr_id, site)] = over_cds_list

    bas_gene_dict = {}
    for chr_id, site in bsa_output_dict:
        over_gene_list = list(gene_interlap[chr_id]['+'].find((site, site))) + list(gene_interlap[chr_id]['-'].find((site, site)))
        if len(over_gene_list) > 0:
            print(chr_id, site, bsa_output_dict[(chr_id, site)], over_gene_list[0][2].id)
            bas_gene_dict[(chr_id, site)] = over_gene_list


    cds = bas_cds_dict[('SL4.0ch10',28051333)][0][2]
    vars(cds)

    cds = bas_cds_dict[('SL4.0ch00', 166925)][0][2]
    vars(cds)                

    cds = bas_cds_dict[('SL4.0ch07', 8202167)][0][2]
    vars(cds)          

    with open("/lustre/home/xuyuxing/Work/Other/Guojin/BSA/tomato_def1/all.site.txt", 'w') as f:
        for i in bsa_output_dict:
            a=bsa_output_dict[i]
            f.write("%s\t%s\t%s\t%s\t%s, %s\n" % (i[0],i[1],a[0],a[1],a[2].__str__(),a[3].__str__()))