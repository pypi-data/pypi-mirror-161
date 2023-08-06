import uuid
import pandas as pd
from itertools import combinations
import networkx as nx
from interlap import InterLap
from collections import Counter
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.os import mkdir, multiprocess_running
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, get_gf_db_meta_dict, gf_info_retrieval, write_gff_file
from toolbiox.lib.xuyuxing.math.set_operating import interval_length_sum
from toolbiox.lib.common.math.interval import section, merge_intervals, interval_minus_set, overlap_between_interval_set, \
    group_by_intervals_with_overlap_threshold
from toolbiox.api.xuyuxing.comp_genome.orthofinder import OG_tsv_file_parse
from toolbiox.lib.xuyuxing.math.stats import get_threshold

# about weight score
def get_ortho_support(OG_tsv_file):

    OG_dict = OG_tsv_file_parse(OG_tsv_file)
    seq_support_dict = {}
    for OG_id in OG_dict:
        empty_num = len([i for i in OG_dict[OG_id] if len(OG_dict[OG_id][i]) == 1 and OG_dict[OG_id][i][0] == ''])
        total_num = len(OG_dict[OG_id])
        support_num = total_num - empty_num

        for i in OG_dict[OG_id]:
            for j in OG_dict[OG_id][i]:
                if j == '':
                    continue
                seq_support_dict[j] = (support_num, total_num)

    return seq_support_dict


# def get_weight(idt_len, query_length, OG_support_num):
#     if query_length > 200:
#         length_score = 5
#     elif query_length > 150:
#         length_score = 4
#     elif query_length > 100:
#         length_score = 3
#     elif query_length > 50:
#         length_score = 2
    
#     if OG_support_num <= 2:
#         support_score = 0.2
#     else:
#         support_score = 1

#     # return (idt_len/aln_len) * (aln_len/query_length) * length_score
#     return (idt_len/query_length) * length_score * support_score

# def get_weight(pst_ratio, q_cover, q_length, OG_support_num):
#     if pst_ratio > 0.7:
#         pst_score = 10
#     elif pst_ratio > 0.6:
#         pst_score = 8
#     elif pst_ratio > 0.5:
#         pst_score = 6
#     elif pst_ratio > 0.4:
#         pst_score = 4
#     else:
#         pst_score = 1

#     if q_cover > 0.7:
#         q_cover_score = 10
#     elif q_cover > 0.6:
#         q_cover_score = 8
#     elif q_cover > 0.5:
#         q_cover_score = 6
#     elif q_cover > 0.4:
#         q_cover_score = 4
#     else:
#         q_cover_score = 1

#     if q_length > 200:
#         length_score = 10
#     elif q_length > 150:
#         length_score = 8
#     elif q_length > 100:
#         length_score = 6
#     elif q_length > 50:
#         length_score = 4
#     else:
#         length_score = 1

#     if OG_support_num > 5:
#         OG_score = 10
#     elif OG_support_num > 4:
#         OG_score = 8
#     elif OG_support_num > 3:
#         OG_score = 6
#     elif OG_support_num > 2:
#         OG_score = 4
#     else:
#         OG_score = 1

#     # return (idt_len/aln_len) * (aln_len/query_length) * length_score
#     # return (idt_len * (OG_support_num + 1))
#     return pst_score * q_cover_score * length_score * OG_score

# def get_ev_weight(gf):
#     q_cover = gf.evidence_indicator['query_coverage']
#     idt_ratio = gf.evidence_indicator['identity']

#     mRNA = gf.sub_features[0]
#     query_length = int(mRNA.qualifiers['Target_Length'][0])

#     OG_support_num = gf.OG_support[0]

#     ev_weight_value = get_weight(idt_ratio, q_cover, query_length, OG_support_num)

#     return ev_weight_value

# weight_dict = {i:get_ev_weight(evidence_dict[i]) for i in evidence_dict}

# with open("1.txt" , 'w') as f:
#     for i in weight_dict:
#         f.write(str(weight_dict[i])+"\n")

# def get_weight(idt_len, query_length, OG_support_num):

#     # return (idt_len/aln_len) * (aln_len/query_length) * length_score
#     # return (idt_len * (OG_support_num + 1))
#     return (idt_len * (OG_support_num + 1))/query_length


# def get_ev_weight(gf):

#     mRNA = gf.sub_features[0]
#     idt_len = mRNA.qualifiers['idt_len']
#     query_length = int(mRNA.qualifiers['Target_Length'][0])
#     OG_support_num = gf.OG_support[0]
#     ev_weight_value = get_weight(idt_len, query_length, OG_support_num)

#     return ev_weight_value

# weight_dict = {i:get_ev_weight(evidence_dict[i]) for i in evidence_dict}

# with open("2.txt" , 'w') as f:
#     for i in weight_dict:
#         f.write(str(weight_dict[i])+"\n")

def get_weight(idt_len, query_length, OG_support_num):

    # return (idt_len/aln_len) * (aln_len/query_length) * length_score
    # return (idt_len * (OG_support_num + 1))
    return (idt_len * (OG_support_num + 1))


def get_ev_weight(gf):

    mRNA = gf.sub_features[0]
    idt_len = mRNA.qualifiers['idt_len']
    query_length = int(mRNA.qualifiers['Target_Length'][0])
    OG_support_num = gf.OG_support[0]
    ev_weight_value = get_weight(idt_len, query_length, OG_support_num)

    return ev_weight_value

# weight_dict = {i:get_ev_weight(evidence_dict[i]) for i in evidence_dict}

# with open("3.txt" , 'w') as f:
#     for i in weight_dict:
#         f.write(str(weight_dict[i])+"\n")


def mark_ev_weight(evidence_dict):
    output_ev_dict = {}
    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]
        ev_weight_value = get_ev_weight(ev_gf)
        ev_gf.weight = ev_weight_value
        output_ev_dict[ev_id] = ev_gf
    return output_ev_dict

def make_cds_vector(evidence_dict, vector_range=(1,1)):
    cds_weight_interlap = InterLap()

    coordinate_list = [vector_range[0], vector_range[1]]
    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]
        ev_weight_value = ev_gf.weight

        mRNA = ev_gf.sub_features[0]
        for cds in mRNA.sub_features:
            cds_weight_interlap.add((cds.start, cds.end, ev_weight_value))
            coordinate_list.append(cds.start)
            coordinate_list.append(cds.end)

    coordinate_list = sorted(list(set(coordinate_list)))

    cds_vector_interlap = InterLap()
    getted_range = {}
    for i in range(0, len(coordinate_list)-1):
        start = coordinate_list[i]
        end = coordinate_list[i+1]

        if (start, start) not in getted_range:
            w_s_total = sum(
                [w for s, e, w in cds_weight_interlap.find((start, start))])
            getted_range[(start, start)] = w_s_total
            cds_vector_interlap.add((start, start, w_s_total))

        if (end, end) not in getted_range:
            w_e_total = sum(
                [w for s, e, w in cds_weight_interlap.find((end, end))])
            getted_range[(end, end)] = w_e_total
            cds_vector_interlap.add((end, end, w_e_total))

        if end - start > 2:
            interval = (start + 1, end - 1)
            if interval not in getted_range:
                w_i_total = sum(
                    [w for s, e, w in cds_weight_interlap.find(interval)])
                getted_range[interval] = w_i_total
                cds_vector_interlap.add((interval[0], interval[1], w_i_total))

    return cds_vector_interlap


def get_vector_score(vector_interlap, start, end):

    w = [w for s, e, w in vector_interlap.find((start, end))]
    if len(w) > 1:
        raise ValueError("cds error: %d, %d" % (start, end))
    elif len(w) == 0:
        w = 0.0
    else:
        w = w[0]

    return w


# def get_ev_gf_score(gf, cds_vector_interlap):

#     ev_weight_value = get_ev_weight(gf)

#     mRNA = gf.sub_features[0]
#     query_length = int(mRNA.qualifiers['Target_Length'][0])

#     sum_w = 0
#     length = 0
#     for cds in mRNA.sub_features:
#         for i in range(cds.start, cds.end+1):
#             length += 1
#             sum_w += get_vector_score(cds_vector_interlap, i, i)

#     gf_score = (sum_w / query_length / 3, ev_weight_value)

#     return gf_score

# def get_ev_gf_score(gf, cds_vector_interlap):

#     ev_weight_value = get_ev_weight(gf)

#     mRNA = gf.sub_features[0]
#     query_length = int(mRNA.qualifiers['Target_Length'][0])

#     sum_w = 0
#     length = 0
#     for cds in mRNA.sub_features:
#         for i in range(cds.start, cds.end+1):
#             length += 1
#             sum_w += get_vector_score(cds_vector_interlap, i, i)

#     gf_score = (sum_w / query_length, ev_weight_value)
#     # gf_score = (sum_w, ev_weight_value)

#     return gf_score

def get_supp_weight_score(gf, cds_vector_interlap):

    mRNA = gf.sub_features[0]
    query_length = int(mRNA.qualifiers['Target_Length'][0])

    sum_w = 0
    length = 0
    for cds in mRNA.sub_features:
        for s,e,w in cds_vector_interlap.find((cds.start, cds.end)):
            if_flag, delta = section((s,e),(cds.start, cds.end),True)
            sum_w = sum_w + (max(delta) - min(delta) + 1) * w
            length += (max(delta) - min(delta) + 1)

    support_weight = sum_w
    # gf_score = (sum_w, ev_weight_value)

    return support_weight, length

def mark_ev_supp_weight(evidence_dict, cds_vector_interlap):
    output_ev_dict = {}
    for ev_id in evidence_dict:
        ev_gf = evidence_dict[ev_id]
        ev_weight_value, cds_aln_length = get_supp_weight_score(ev_gf, cds_vector_interlap)
        ev_gf.supp_weight = ev_weight_value
        ev_gf.cds_aln_length = cds_aln_length
        output_ev_dict[ev_id] = ev_gf
    return output_ev_dict

# evidence_dict = mark_ev_supp_weight(evidence_dict, cds_vector_interlap)
# supp_weight_list = [evidence_dict[i].supp_weight for i in evidence_dict]
# with open("5.txt" , 'w') as f:
#     for i in supp_weight_list:
#         f.write(str(i)+"\n")


# import math
# log_supp_weight_list = [math.log2(evidence_dict[i].supp_weight) for i in evidence_dict]

# with open("6.txt" , 'w') as f:
#     for i in log_supp_weight_list:
#         f.write(str(i)+"\n")

# def get_ev_gf_score(gf, cds_vector_interlap):

#     ev_weight_value = get_ev_weight(gf)

#     mRNA = gf.sub_features[0]
#     query_length = int(mRNA.qualifiers['Target_Length'][0])

#     sum_w = 0
#     length = 0
#     for cds in mRNA.sub_features:
#         for s,e,w in cds_vector_interlap.find((cds.start, cds.end)):
#             if_flag, delta = section((s,e),(cds.start, cds.end),True)
#             sum_w = sum_w + (max(delta) - min(delta) + 1) * w

#     gf_score = (sum_w / query_length, ev_weight_value)
#     # gf_score = (sum_w, ev_weight_value)

#     return gf_score

# def mark_ev_score_for_gf_dict(input_gf_dict, cds_vector_interlap):
#     output_gf_dict = {}
#     args_list = []
#     args_id_list = []
#     for i in input_gf_dict:
#         gf = input_gf_dict[i]
#         args_list.append((gf, cds_vector_interlap))
#         args_id_list.append(i)

#     gf_score_out = multiprocess_running(get_ev_gf_score, args_list, 56, args_id_list=args_id_list)

#     gf_score_dict = {}
#     for i in gf_score_out:
#         gf_score_dict[i] = list(gf_score_out[i]['output'])

#     # get rank score
#     support_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][0], reverse=True)
#     self_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][1], reverse=True)

#     for i in gf_score_dict:
#         gf_score_dict[i].append((support_rank.index(i) + 1) * (self_rank.index(i) + 1))


#     output_gf_dict = {}
#     for i in gf_score_dict:
#         gf = input_gf_dict[i]
#         gf.gf_score_detail = gf_score_dict[i]
#         gf.gf_score = gf_score_dict[i][2]
#         output_gf_dict[i] = gf

#     return output_gf_dict

# def mark_ev_score_for_gf_dict(input_gf_dict, cds_vector_interlap):
#     gf_score_dict = {}
#     for i in input_gf_dict:
#         gf = input_gf_dict[i]
#         gf_score_dict[i] = list(get_ev_gf_score(gf, cds_vector_interlap))

#     # get rank score
#     support_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][0], reverse=True)
#     self_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][1], reverse=True)

#     for i in gf_score_dict:
#         gf_score_dict[i].append((support_rank.index(i) + 1) * (self_rank.index(i) + 1))


#     output_gf_dict = {}
#     for i in gf_score_dict:
#         gf = input_gf_dict[i]
#         gf.gf_score_detail = gf_score_dict[i]
#         gf.gf_score = gf_score_dict[i][2]
#         output_gf_dict[i] = gf

#     return output_gf_dict

def mark_ev_score_for_gf_dict(input_gf_dict):
    gf_score_dict = {}
    for i in input_gf_dict:
        gf = input_gf_dict[i]
        gf_score_dict[i] = [gf.supp_weight, gf.weight]

    # get rank score
    support_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][0], reverse=True)
    self_rank = sorted(list(gf_score_dict.keys()), key=lambda x:gf_score_dict[x][1], reverse=True)

    for i in gf_score_dict:
        gf_score_dict[i].append((support_rank.index(i) + 1) * (self_rank.index(i) + 1))


    output_gf_dict = {}
    for i in gf_score_dict:
        gf = input_gf_dict[i]
        gf.gf_score_detail = gf_score_dict[i]
        gf.gf_score = gf_score_dict[i][2]
        output_gf_dict[i] = gf

    return output_gf_dict

def mark_OG_support_for_gf_dict(input_gf_dict, seq_support_dict):
    output_gf_dict = {}

    for i in input_gf_dict:
        gf = input_gf_dict[i]

        q_id = gf.id.split("_")[0]
        if q_id in seq_support_dict:
            gf.OG_support = seq_support_dict[q_id]
        else:
            gf.OG_support = (0,0)

        output_gf_dict[i] = gf
    
    return output_gf_dict

# about exclusivity
def get_overlap_ratio(gf1, gf2, similarity_type):
    gf1_cds_interval = [(j.start, j.end)
                        for j in gf1.sub_features[0].sub_features]
    gf2_cds_interval = [(j.start, j.end)
                        for j in gf2.sub_features[0].sub_features]

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
        gf1_cds_interval, gf2_cds_interval, similarity_type=similarity_type)

    return overlap_ratio


def mark_exclusivity_for_gf_dict(input_gf_dict):
    ev_id_list = list(input_gf_dict.keys())

    score_pair_dict = {}
    for i, j in combinations(ev_id_list, 2):
        score_pair_dict[(i, j)] = get_overlap_ratio(
            input_gf_dict[i], input_gf_dict[j], 'shorter_overlap_coverage')
    
    output_gf_dict = {}
    for ev_id_i in ev_id_list:
        gf = input_gf_dict[ev_id_i]
        exclusivity_list = []
        for ev_id_j in ev_id_list:
            if ev_id_i == ev_id_j:
                continue
            if (ev_id_i, ev_id_j) in score_pair_dict:
                overlap_ratio = score_pair_dict[(ev_id_i, ev_id_j)]
            else:
                overlap_ratio = score_pair_dict[(ev_id_j, ev_id_i)]

            if overlap_ratio > 0.1:
                exclusivity_list.append(ev_id_j)
        gf.exclusivity = exclusivity_list
        gf.exclusivity.append(ev_id_i)
        output_gf_dict[ev_id_i] = gf

    return output_gf_dict


# about evidence get and cluster
def load_map_files(reference_genome_table, WPGmapper_dir):
    # read ref genome taxon_id
    ref_db = pd.read_excel(reference_genome_table)
    ref_taxon_id_list = []
    for index in ref_db.index:
        taxon_id = str(ref_db.loc[index]['id'])
        if not pd.isna(taxon_id):
            ref_taxon_id_list.append(taxon_id)

    # load map database
    ref_WPGmapper_dict = {}
    for taxon_id in ref_taxon_id_list:
        ref_WPGmapper_dict[taxon_id] = {}
        ref_WPGmapper_dict[taxon_id]['genblasta'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genblasta.db"
        ref_WPGmapper_dict[taxon_id]['genewise'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.db"
        ref_WPGmapper_dict[taxon_id]['pep_db'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.pep.db"
        ref_WPGmapper_dict[taxon_id]['cds_db'] = WPGmapper_dir + \
            "/WPGmapper/" + taxon_id + "/genewise.cds.db"

    return ref_WPGmapper_dict


def min_cds_start(cds_range_list):
    return min([min(i) for i in cds_range_list])


def get_overlap_ratio(gf1,gf2,similarity_type):
    gf1_cds_interval = [(j.start, j.end) for j in gf1.sub_features[0].sub_features]
    gf2_cds_interval = [(j.start, j.end) for j in gf2.sub_features[0].sub_features]

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(gf1_cds_interval, gf2_cds_interval, similarity_type=similarity_type)
    
    return overlap_ratio


def higher_in_lower_group(lower_merged_group, higher, cds_interval_dict, similarity_type, threshold):
    grouped_flag = False

    for lower in lower_merged_group:
        jaccord_score = overlap_between_interval_set(
            cds_interval_dict[lower], cds_interval_dict[higher], similarity_type)[0]
        if jaccord_score >= threshold:
            grouped_flag = True
            break

    return grouped_flag


def merge_evidence_by_cds_intervals_identity(ev_id_list, cds_interval_dict, similarity_type, threshold):

    sorted_by_lower_bound = sorted(
        ev_id_list, key=lambda x: min_cds_start(cds_interval_dict[x]))
    merged = Counter()

    num = 0
    for higher in sorted_by_lower_bound:
        if len(merged) == 0:
            merged[num] = [higher]
            num += 1
        else:
            g_id_list = list(merged.keys())
            g_id_list.reverse()

            grouped_flag = False
            for g_id in g_id_list:
                grouped_flag = higher_in_lower_group(
                    merged[g_id], higher, cds_interval_dict, similarity_type, threshold)
                if grouped_flag == True:
                    merged[g_id].append(higher)
                    break

            if not grouped_flag:
                merged[num] = [higher]
                num += 1

    return merged


def evidence_cluster(evidence_dict, similarity_type='jaccord_score', threshold=0.3):
    if len(evidence_dict) > 0:

        # CDS interval list
        cds_interval_dict = {}
        gene_interval_dict = {}
        for i in evidence_dict:
            # if not evidence_dict[i].map_quality_pass:
            #     continue

            gene_interval_dict[i] = (
                evidence_dict[i].start, evidence_dict[i].end)
            cds_interval_dict[i] = [
                (j.start, j.end) for j in evidence_dict[i].sub_features[0].sub_features]

        big_group_dict = group_by_intervals_with_overlap_threshold(
            gene_interval_dict, 0)

        # # load evidences into interlap
        # evidence_interlap = InterLap()
        # evidence_interlap.update(
        #     [(gene_interval_dict[i][0], gene_interval_dict[i][1], i) for i in gene_interval_dict])

        # merge intervals into cluster
        ev_cluster_dict = {}
        num = 0
        for bg_id in big_group_dict:
            cds_interval_dict_in_group = {
                ev_id: cds_interval_dict[ev_id] for ev_id in big_group_dict[bg_id]['list']}

            ev_cluster_dict_in_group = merge_evidence_by_cds_intervals_identity(
                list(cds_interval_dict_in_group.keys()), cds_interval_dict_in_group, similarity_type, threshold)

            for i in ev_cluster_dict_in_group:
                num += 1
                ev_cluster_dict[num] = ev_cluster_dict_in_group[i]

        # ev_cluster_range_dict = {}
        # for cl_id in ev_cluster_dict:
        #     ev_cluster_range_dict[cl_id] = merge_intervals([gene_interval_dict[i] for i in ev_cluster_dict[cl_id]])[0]

        return ev_cluster_dict

    else:
        return Counter()


def extract_evidence(contig, strand, ref_WPGmapper_dict, given_range=None):

    # get all useable evidence on the contig(strand)

    evidence_dict = {}

    for taxon_id in ref_WPGmapper_dict:
        # print(taxon_id)

        gws_db = ref_WPGmapper_dict[taxon_id]['genewise']
        meta_dict = get_gf_db_meta_dict(gws_db)

        # read mRNA info

        for table_name in meta_dict['gene'][0]:
            # print(table_name)
            if given_range is None:
                sql_cmd_string = 'SELECT * FROM %s WHERE contig_name = \"%s\" AND strand = \"%s\"' % (
                    table_name, contig, strand)
            else:
                sql_cmd_string = 'SELECT * FROM %s WHERE contig_name = \"%s\" AND strand = \"%s\" AND start <= %d AND end >= %d' % (
                    table_name, contig, strand, max(given_range), min(given_range))

            data_list = sc.sqlite_execute(sql_cmd_string, gws_db)
            for gf_db_info_tuple in data_list:
                id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers = gf_db_info_tuple
                gf = gf_info_retrieval(gf_db_info_tuple, 0, 'A', gws_db)

                mRNA_gf = gf.sub_features[0]
                qualifiers = mRNA_gf.qualifiers

                # query coverage
                coverage = min((int(qualifiers['Target_End'][0]) - int(
                    qualifiers['Target_Start'][0]) + 1) / int(qualifiers['Target_Length'][0]), 1.00)

                # aln aa
                aln_aa_len = int(
                    qualifiers['Target_End'][0]) - int(qualifiers['Target_Start'][0]) + 1

                # identity
                identity = int(qualifiers['idt_len']) / \
                    int(qualifiers['aln_len'])

                gf.evidence_indicator = {
                    "query_coverage": coverage,
                    "aln_aa_len": aln_aa_len,
                    "identity": identity,
                }

                gf.db_path = "%s.%s.%s" % (taxon_id, table_name, id_tmp)

                gf.score  = max(0.1, float(gf.sub_features[0].qualifiers['score'][0]))

                evidence_dict[gf.id] = gf

    return evidence_dict


def mark_map_quality_for_gf_dict(input_gf_dict, args):
    for ev_id in input_gf_dict:
        # quality control
        coverage = input_gf_dict[ev_id].evidence_indicator["query_coverage"]
        aln_aa_len = input_gf_dict[ev_id].evidence_indicator["aln_aa_len"]
        identity = input_gf_dict[ev_id].evidence_indicator["identity"]
        score = input_gf_dict[ev_id].score

        if coverage >= args.min_cover and aln_aa_len >= args.min_aa_len and identity >= args.min_identity and score >= args.min_score:
            input_gf_dict[ev_id].map_quality_pass = True
        else:
            input_gf_dict[ev_id].map_quality_pass = False

    return input_gf_dict


# about graph
def no_red_by_jaccord(ev_in_cluster_dict):
    no_red_ev_dict_clst = evidence_cluster(ev_in_cluster_dict, similarity_type='jaccord_score', threshold=0.9)
    no_red_ev_dict = {}
    for i in no_red_ev_dict_clst:
        gf_id = sorted([j for j in no_red_ev_dict_clst[i]], key=lambda x:ev_in_cluster_dict[x].gf_score, reverse=True)[0]
        no_red_ev_dict[gf_id] = ev_in_cluster_dict[gf_id]
    return no_red_ev_dict


def load_a_node(graph, give_node_id, remaining_selectable_ev_list, evidence_dict_range):
    # print(give_node_id)
    # print(remaining_selectable_ev_list)
    uuid_id, seq_id = give_node_id

    for i in remaining_selectable_ev_list:
        uuid_id = uuid.uuid1().hex
        node_id = (uuid_id, i)

        if seq_id == 'START':
            print(node_id)

        graph.add_edge(give_node_id, node_id, weight=evidence_dict_range[i].gf_score)

        remaining_selectable_ev_list_for_i = list(set(remaining_selectable_ev_list) - set(evidence_dict_range[i].exclusivity))
        if len(remaining_selectable_ev_list_for_i) == 0:
            graph.add_edge(node_id, 'END', weight=1)
            # print(node_id)
        else:
            load_a_node(graph, node_id, remaining_selectable_ev_list_for_i, evidence_dict_range)


def use_graph_to_get_rep(evidence_dict_range):
    
    G = nx.DiGraph()
    uuid_id = uuid.uuid1().hex
    start = (uuid_id, 'START')

    load_a_node(G, start, list(evidence_dict_range.keys()), evidence_dict_range)
    # paths = nx.johnson(G, weight="weight")
    # paths[start]["END"]

    return nx.shortest_path(G,start,"END",weight='weight')

# Brute-force
def brute_force_get_rep(ev_in_cluster_dict):
    gf_score_rank = sorted(list(ev_in_cluster_dict.keys()), key=lambda x:ev_in_cluster_dict[x].gf_score)

#todo

    return ev_in_cluster_dict


# greedy algorithm
def greedy_get_rep(ev_in_cluster_dict):
    gf_score_rank = sorted(list(ev_in_cluster_dict.keys()), key=lambda x:ev_in_cluster_dict[x].gf_score)

    rep_gf_list = []
    ex_gf_set = set()
    for i in gf_score_rank:
        if i not in ex_gf_set:
            rep_gf_list.append(i)
            ex_gf_set = ex_gf_set | set(ev_in_cluster_dict[i].exclusivity)

    for i in ev_in_cluster_dict:
        if i in rep_gf_list:
            ev_in_cluster_dict[i].is_rep = True
        else:
            ev_in_cluster_dict[i].is_rep = False

    return ev_in_cluster_dict


# def rep_gf_judge(evidence_dict_cleaned):
#     # give me cleaned evidence_dict

#     evidence_cluster_dict = evidence_cluster(evidence_dict_cleaned, similarity_type='shorter_overlap_coverage', threshold=0.1)
    
#     rep_gf_dict = {}
#     output_dict = {}
#     for cl_id in evidence_cluster_dict:
#         print(cl_id)
#         ev_id_list = evidence_cluster_dict[cl_id]
#         if len(ev_id_list) == 1:

#             gf_id = ev_id_list[0]
#             gf = evidence_dict_cleaned[gf_id]
#             gf.exclusivity = [gf_id]
#             gf.gf_score = 1
#             gf.gf_score_detail = [0,get_ev_weight(gf),1]
#             gf.is_rep = True

#             output_dict[gf_id] = gf
#         else:
#             ev_in_cluster_dict = {ev_id:evidence_dict_cleaned[ev_id] for ev_id in evidence_cluster_dict[cl_id]}
#             cds_vector_interlap = make_cds_vector(ev_in_cluster_dict)
#             ev_in_cluster_dict = mark_ev_score_for_gf_dict(ev_in_cluster_dict, cds_vector_interlap)
#             ev_in_cluster_dict = mark_exclusivity_for_gf_dict(ev_in_cluster_dict)
#             ev_in_cluster_dict = greedy_get_rep(ev_in_cluster_dict)

#             for i in ev_in_cluster_dict:
#                 output_dict[i] = ev_in_cluster_dict[i]
    
#     return output_dict

def rep_gf_cluster(ev_in_cluster_dict):

    ev_in_cluster_dict = mark_ev_score_for_gf_dict(ev_in_cluster_dict)
    ev_in_cluster_dict = mark_exclusivity_for_gf_dict(ev_in_cluster_dict)
    ev_in_cluster_dict = greedy_get_rep(ev_in_cluster_dict)

    return ev_in_cluster_dict

def rep_gf_judge(evidence_dict_cleaned):
    # give me cleaned evidence_dict

    evidence_cluster_dict = evidence_cluster(evidence_dict_cleaned, similarity_type='shorter_overlap_coverage', threshold=0.1)
    
    args_list = []
    for cl_id in evidence_cluster_dict:
        
        ev_in_cluster_dict = {ev_id:evidence_dict_cleaned[ev_id] for ev_id in evidence_cluster_dict[cl_id]}

        args_list.append((ev_in_cluster_dict, ))

    rep_gf_cluster_out = multiprocess_running(rep_gf_cluster, args_list, 56 , silence=True)

    output_dict = {}
    for i in rep_gf_cluster_out:
        ev_in_cluster_dict = rep_gf_cluster_out[i]['output']
        for i in ev_in_cluster_dict:
            output_dict[i] = ev_in_cluster_dict[i]
    
    return output_dict


#########
 

def pseudogene_main(args):
    mkdir(args.output_dir, True)

    contig_list = list(read_fasta_by_faidx(args.target_genome_fasta).keys())

    # load WPGmapper data
    ref_WPGmapper_dict = load_map_files(
        args.reference_genome_table, args.WPGmapper_dir)

    seq_support_dict = get_ortho_support(args.OG_tsv_file)

    # parse a contig
    args_list = []
    for contig in contig_list:
        args_list.append((contig, ref_WPGmapper_dict, seq_support_dict, args))

    multiprocess_running(pseudogene_by_contig, args_list,
                         args.threads, silence=True)


def pseudogene_by_contig(contig, strand, ref_WPGmapper_dict, seq_support_dict, args):

    evidence_dict = extract_evidence(contig, strand, ref_WPGmapper_dict)
    evidence_dict = mark_map_quality_for_gf_dict(evidence_dict, args)

    evidence_dict_clean = {i:evidence_dict[i] for i in evidence_dict if evidence_dict[i].map_quality_pass}

    evidence_dict_clean = mark_OG_support_for_gf_dict(evidence_dict_clean, seq_support_dict)
    evidence_dict_clean = mark_ev_weight(evidence_dict_clean)

    threshold, mu, sigma, statistic, pvalue = get_threshold([evidence_dict_clean[i].weight for i in evidence_dict_clean])

    evidence_dict_clean_weight = {i:evidence_dict[i] for i in evidence_dict if evidence_dict[i].weight >= threshold}
    cds_vector_interlap = make_cds_vector(evidence_dict_clean_weight)
    evidence_dict_clean_weight = mark_ev_supp_weight(evidence_dict_clean_weight, cds_vector_interlap)


    evidence_dict_clean_weight = rep_gf_judge(evidence_dict_clean_weight)

    return evidence_dict_clean_weight


weight_list = [evidence_dict_clean[i].weight for i in evidence_dict_clean]

with open("weight_list.txt" , 'w') as f:
    for i in weight_list:
        f.write(str(i)+"\n")

score_list = [evidence_dict_clean[i].score * evidence_dict_clean[i].OG_support[0] for i in evidence_dict_clean]

score_list = [evidence_dict_clean[i].score for i in evidence_dict_clean if evidence_dict_clean[i].score < 200]

with open("score_list.txt" , 'w') as f:
    for i in score_list:
        f.write(str(i)+"\n")

score_list = []
for i in evidence_dict_clean:
    plus_score = 1

    if evidence_dict_clean[i].OG_support[0] >= 2:
        plus_score = 10
    
    if evidence_dict_clean[i].cluster_support / evidence_dict_clean[i].score > 2:
        plus_score = 10
    
    score = evidence_dict_clean[i].score * plus_score
    score_list.append(math.log2(score))


with open("score_list.txt" , 'w') as f:
    for i in score_list:
        f.write(str(i)+"\n")

score_del_list = []
for i in evidence_dict_clean:
    plus_score = 1

    if evidence_dict_clean[i].OG_support[0] >= 2:
        plus_score = 10
    
    if evidence_dict_clean[i].cluster_support / evidence_dict_clean[i].score > 2:
        plus_score = 10

    if plus_score == 10:
        score = evidence_dict_clean[i].score
        score_del_list.append(math.log2(score))


with open("score_del_list.txt" , 'w') as f:
    for i in score_del_list:
        f.write(str(i)+"\n")


rep_gf_list = [evidence_dict_cleaned_mark_rep[gf_id] for gf_id in evidence_dict_cleaned_mark_rep if evidence_dict_cleaned_mark_rep[gf_id].is_rep is True]
write_gff_file(rep_gf_list, "/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/T267555N0C000.WPGmaper.new.skip_all/rep2.gff3")

import pickle

file_name = "/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/pseudogene/PC/T267555N0C000/T267555N0C000.WPGmaper.new.skip_all/2.tmp.py"

data_list = [(i.gf_score_detail[0],i.gf_score_detail[1]) for i in rep_gf_list]

data_list = [(evidence_dict[i].weight,evidence_dict[i].supp_weight) for i in evidence_dict]
data_list = [output_dict[i].cluster_support + output_dict[i].score for i in output_dict]

OUT = open(file_name, 'wb')
pickle.dump(data_list, OUT)
OUT.close()


TEMP = open(file_name, 'rb')
data_list = pickle.load(TEMP)
TEMP.close()

TEMP = open(file_name, 'rb')
evidence_dict = pickle.load(TEMP)
TEMP.close()

# score
score_list = [float(evidence_dict[i].sub_features[0].qualifiers['score'][0]) for i in evidence_dict]
q_len_list = [float(evidence_dict[i].sub_features[0].qualifiers['Target_Length'][0]) for i in evidence_dict]
idt_list = [float(evidence_dict[i].sub_features[0].qualifiers['idt_len']) for i in evidence_dict]
idt_ratio_list = [float(evidence_dict[i].sub_features[0].qualifiers['idt_len'])/float(evidence_dict[i].sub_features[0].qualifiers['Target_Length'][0]) for i in evidence_dict]
score_OG_list = [float(evidence_dict[i].sub_features[0].qualifiers['score'][0]) * evidence_dict[i].OG_support[0] for i in evidence_dict]

score_list = [float(evidence_dict[i].sub_features[0].qualifiers['score'][0]) for i in evidence_dict]


for i in evidence_dict:
    evidence_dict[i].score  = max(0.1, float(evidence_dict[i].sub_features[0].qualifiers['score'][0]))

def get_cluster_support(evidence_dict):
    output_dict = {}
    evidence_cluster_dict = evidence_cluster(evidence_dict, similarity_type='jaccord_score', threshold=0.5)

    for i in evidence_cluster_dict:
        print(i)
        # num = 0
        for j in evidence_cluster_dict[i]:
            # num+=1
            # print(num)
            gf_j = evidence_dict[j]
            cluster_support = 0
            for k in evidence_cluster_dict[i]:
                if j == k:
                    continue
                gf_k = evidence_dict[k]
                overlap_ratio = get_overlap_ratio(gf_j,gf_k,"jaccord_score")
                if overlap_ratio > 0.8:
                    cluster_support += gf_k.score
            gf_j.cluster_support = cluster_support
            output_dict[j] = gf_j
    
    return output_dict
                




import math
import matplotlib.pyplot as plt
import numpy as np

# x = [math.log10(i[0]+1) for i in data_list]
# y = [math.log10(i[1]+1) for i in data_list]

# x = [i[0] for i in data_list]
# y = [i[1] for i in data_list]

x = idt_list
y = score_list

# 由pyplot创建figure，并由axes等对象的方法进行绘图
fig, ax = plt.subplots(figsize=(10,10))

#绘图
ax.scatter(x, y)

#展示
plt.show()


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

x = [math.log2(i[0]+1) for i in data_list]
y = [math.log2(i[1]+1) for i in data_list]

fig, ax = plt.subplots(figsize=(15, 15))

# the scatter plot:
ax.scatter(x, y)

# Set aspect of the main axes.
ax.set_aspect(1.)

# create new axes on the right and on the top of the current axes
divider = make_axes_locatable(ax)
# below height and pad are in inches
ax_histx = divider.append_axes("top", 1.2, pad=0.1, sharex=ax)
ax_histy = divider.append_axes("right", 1.2, pad=0.1, sharey=ax)

# make some labels invisible
ax_histx.xaxis.set_tick_params(labelbottom=False)
ax_histy.yaxis.set_tick_params(labelleft=False)

# now determine nice limits by hand:
binwidth = 0.25
xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
xymin = max(np.max(np.abs(x)), np.max(np.abs(y)))
lim = (int(xymax/binwidth) + 1)*binwidth

bins = np.arange(0, lim + binwidth, binwidth)
ax_histx.hist(x, bins=bins)
ax_histy.hist(y, bins=bins, orientation='horizontal')

# the xaxis of ax_histx and yaxis of ax_histy are shared with ax,
# thus there is no need to manually adjust the xlim and ylim of these
# axis.

ax_histx.set_yticks([0, 50, 100])
ax_histy.set_xticks([0, 50, 100])

# ax.set_xlim(3, 10)
# ax.set_ylim(1, 5)

plt.show()