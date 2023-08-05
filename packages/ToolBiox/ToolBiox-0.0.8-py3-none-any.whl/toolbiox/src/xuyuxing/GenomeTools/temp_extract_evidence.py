import time
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
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins


def extract_one_evidences(id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers, gws_db, OG_support, taxon_id, table_name):
    gf = gf_info_retrieval((id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers), 0, 'A', gws_db)

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

    q_id = gf_name.split("_")[0]

    gf.evidence_indicator = {
        "query_id": q_id,
        "query_coverage": coverage,
        "aln_aa_len": aln_aa_len,
        "identity": identity,
        "query_length": int(qualifiers['Target_Length'][0]),
        "score": max(0.1, float(gf.sub_features[0].qualifiers['score'][0])),
        "OG_support": OG_support
    }

    gf.score_dict = {
        "score": max(0.1, float(gf.sub_features[0].qualifiers['score'][0]))
    }

    gf.db_path = "%s.%s.%s" % (taxon_id, table_name, id_tmp)

    return gf


def extract_evidences(contig, strand, ref_WPGmapper_dict, seq_support_dict, given_range, num_thread):

    # get all useable evidence on the contig(strand)

    evidence_dict = {}
    args_list = []
    args_id_list = []

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

                q_id = gf_name.split("_")[0]
                if q_id in seq_support_dict:
                    OG_support = seq_support_dict[q_id]
                else:
                    OG_support = (0, 0)

                args_list.append((id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers, gws_db, OG_support, taxon_id, table_name))
                args_id_list.append(gf_name)

    ev_output = multiprocess_running(extract_one_evidences, args_list, num_thread, silence=True, args_id_list=args_id_list)

    for i in ev_output:
        evidence_dict[i] = ev_output[i]['output']
    
    return evidence_dict
