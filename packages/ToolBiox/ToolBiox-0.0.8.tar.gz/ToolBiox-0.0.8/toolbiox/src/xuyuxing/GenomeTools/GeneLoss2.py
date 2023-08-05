from toolbiox.api.xuyuxing.comp_genome.planttribes import seq_classify
from BCBio import GFF
from interlap import InterLap
from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, OrthoGroup
from toolbiox.lib.common.genome.genome_feature2 import Gene, HomoPredictResults
from toolbiox.lib.common.math.interval import overlap_between_interval_set, group_by_intervals_with_overlap_threshold, sum_interval_length
from toolbiox.lib.common.os import mkdir, multiprocess_running
from toolbiox.lib.common.util import logging_init, configure_parser
from toolbiox.src.xuyuxing.GenomeTools.WPGmapper import load_map_files, extract_all_evidences
import configparser
import os
import pickle


def mark_map_quality_for_gf_dict(input_gf_dict, args):
    for ev_id in input_gf_dict:
        # quality control
        coverage_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= args.min_cover
        aln_aa_len_flag = input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= args.min_aa_len
        identity_flag = input_gf_dict[ev_id].evidence_indicator["identity"] >= args.min_identity
        score_flag = input_gf_dict[ev_id].evidence_indicator["score"] >= args.min_score
        # parent_evalue_flag = input_gf_dict[ev_id].parent_blast["evalue"] <= args.evalue
        # parent_blast_identity_flag = input_gf_dict[ev_id].parent_blast["identity"] >= args.min_identity

        # Special arrow
        # special_arrow_flag = input_gf_dict[ev_id].evidence_indicator["query_coverage"] >= 0.8 and input_gf_dict[ev_id].evidence_indicator["identity"] >= 0.9 and input_gf_dict[
        #     ev_id].parent_blast["identity"] >= 0.9 and input_gf_dict[ev_id].evidence_indicator["aln_aa_len"] >= 200 and input_gf_dict[ev_id].parent_blast["evalue"] <= 1e-30

        # if coverage_flag and aln_aa_len_flag and identity_flag and score_flag and parent_evalue_flag and parent_blast_identity_flag:
        if coverage_flag and aln_aa_len_flag and identity_flag and score_flag:
            input_gf_dict[ev_id].map_quality_pass = True
        # elif score_flag and special_arrow_flag:
        #     input_gf_dict[ev_id].map_quality_pass = True
        else:
            input_gf_dict[ev_id].map_quality_pass = False

    return input_gf_dict


def parse_conserved_species_string(conserved_species_string):
    conserved_arguments = [[], []]

    for group_string in conserved_species_string.split(";"):
        group_info = group_string.split(",")
        if len(group_info) == 1:
            conserved_arguments[0].append(group_info)
            conserved_arguments[1].append(1)
        else:
            conserved_arguments[0].append(group_info[:-1])
            min_num = int(group_info[-1])
            conserved_arguments[1].append(min_num)

    return conserved_arguments


def get_HPR_from_evidence_dict(query_gene_list, evidence_dict, subject_species=None):
    query_gene_dict = {i.id: i for i in query_gene_list}

    hit_gene_dir = {}
    for gf_id in evidence_dict:
        gf = evidence_dict[gf_id]
        query_id = gf.evidence_indicator['query_id']

        if not query_id in hit_gene_dir:
            hit_gene_dir[query_id] = []
        hit_gene_dir[query_id].append(gf)

    output_list = []
    for query_id in hit_gene_dir:
        query_gene = query_gene_dict[query_id]
        output_list.append(
            HomoPredictResults(query_gene, subject_species=subject_species, hit_gene_list=hit_gene_dir[query_id]))

    return output_list


def merge_patch_hits(patch_hits):
    # merge as site
    site_dict = {}
    for gf in patch_hits:
        if not gf.chr_id in site_dict:
            site_dict[gf.chr_id] = {
                "+": InterLap(),
                "-": InterLap(),
            }
        site_dict[gf.chr_id][gf.strand].add((gf.start, gf.end, gf))

    output_gf_list = []
    for i in site_dict:
        for j in site_dict[i]:
            merge_groups = group_by_intervals_with_overlap_threshold(
                {k[2]: (k[0], k[1]) for k in site_dict[i][j]}, 0.8)

            for gp_id in merge_groups:
                hit_list = merge_groups[gp_id]['list']
                model_hit = sorted(hit_list, key=lambda x: len(
                    x.model_aa_seq.seq), reverse=True)[0]
                output_gf_list.append(model_hit)

    return output_gf_list


def GeneLoss_main(args):
    mkdir(args.work_dir, True)

    logger = logging_init("GeneLoss", args.log_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    # step1
    logger.info("Step1: read orthogroups file")
    orthogroups_tsv_file = args.orthogroup_scaffold_dir + "/orthogroups.tsv"
    OGs = OrthoGroups(OG_tsv_file=orthogroups_tsv_file)
    conserved_arguments = parse_conserved_species_string(
        args.conserved_species)
    conserved_og_id_list = OGs.get_conserved_OG_list(conserved_arguments)
    csv_OGs = OrthoGroups(from_OG_list=[OGs.OG_dict[i]
                                        for i in conserved_og_id_list])
    logger.info("       there are %d species, %d orthogroups, %d are conserved" % (
        len(OGs.species_list), len(OGs.OG_id_list), len(csv_OGs.OG_id_list)))

    # step2
    logger.info("Step2: get candidate gene loss orthologues in %s" %
                args.target_speci)
    candi_loss_list = [og_id for og_id in csv_OGs.OG_dict if len(
        csv_OGs.OG_dict[og_id].gene_dict[args.target_speci]) == 0]
    logger.info("       there are %d (%.2f%%) orthogroups don't have gene in %s" % (len(
        candi_loss_list), len(candi_loss_list)/len(csv_OGs.OG_id_list)*100, args.target_speci))
    cand_loss_OGs = OrthoGroups(
        from_OG_list=[OGs.OG_dict[i] for i in candi_loss_list])
    cand_loss_OGs.write_OG_tsv_file(
        args.work_dir + "/1.candidate_gene_loss.txt")

    # step3
    logger.info("Step3: get ref gene mapping results from WPGmapper")
    genewise_dict_file = args.work_dir + "/2.genewise_dict.pyb"

    ref_sp_list = []
    for i in conserved_arguments[0]:
        for j in i:
            ref_sp_list.append(j)
    ref_sp_list = list(set(ref_sp_list))

    if not os.path.exists(genewise_dict_file):
        logger.info("Step3.1: load data from WPGmapper")

        ref_gene_list = []
        for og_id in candi_loss_list:
            og = csv_OGs.OG_dict[og_id]
            for sp_id in ref_sp_list:
                for gene in og.gene_dict[sp_id]:
                    ref_gene_list.append(gene)

        evidence_id_list = []
        for gene in ref_gene_list:
            evidence_id_list.extend([gene.id+"_"+str(i)
                                     for i in range(args.top_evidence_num)])

        ref_WPGmapper_dict = load_map_files(
            ref_sp_list, args.wpgmapper_dir)

        evidence_dict = extract_all_evidences(
            ref_WPGmapper_dict, evidence_id_list=evidence_id_list, log_file=args.log_file)

        evidence_dict = mark_map_quality_for_gf_dict(evidence_dict, args)

        logger.info("Step3.1: begin compare")
        # load genewise output
        genewise_out = get_HPR_from_evidence_dict(
            ref_gene_list, evidence_dict, subject_species=args.target_speci)

        # load annotated range
        annotated_range_dict = {}
        gene_cds_intervals_dict = {}
        with open(args.target_speci_annotation, 'r') as in_handle:
            for rec in GFF.parse(in_handle):
                if rec.id not in annotated_range_dict:
                    annotated_range_dict[rec.id] = {}
                    annotated_range_dict[rec.id]["+"] = InterLap()
                    annotated_range_dict[rec.id]["-"] = InterLap()
                for gene in rec.features:
                    if args.target_speci_feature == 'None' or gene.type == args.target_speci_feature:
                        start_tmp = gene.location.start.position + 1
                        end_tmp = gene.location.end.position
                        if gene.id == "":
                            gene.id = list(
                                set(gene.qualifiers.keys()) - {'source'})[0]
                        if gene.strand == 1:
                            annotated_range_dict[rec.id]["+"].add(
                                (start_tmp, end_tmp, gene.id))
                        else:
                            annotated_range_dict[rec.id]["-"].add(
                                (start_tmp, end_tmp, gene.id))

                        gene_cds_intervals_dict[gene.id] = [(int(i.location.start)+1, int(
                            i.location.end)) for i in gene.sub_features[0].sub_features if i.type == 'CDS']

        # mark new range which not in annotated range and have good coverage
        for query_HPR in genewise_out:
            for hit_gene in query_HPR.hit_gene_list:
                cds_range = [(i.start, i.end)
                             for i in hit_gene.sub_features[0].sub_features if i.type == 'CDS']
                cds_length = sum_interval_length(cds_range)

                mRNA_qual = hit_gene.sub_features[0].qualifiers

                # test if have been annotated
                loci_tmp = hit_gene.chr_loci
                hit_gene.new_anno = (True, None, 0.0)

                overlaped_gene_id = []

                if loci_tmp.chr_id in annotated_range_dict:
                    for annotated_range in annotated_range_dict[loci_tmp.chr_id][loci_tmp.strand].find(
                            (loci_tmp.start, loci_tmp.end)):
                        anno_s = annotated_range[0]
                        anno_e = annotated_range[1]
                        known_gene_id = annotated_range[2]
                        overlaped_gene_id.append(known_gene_id)

                overlaped_gene_id = list(set(overlaped_gene_id))

                for gene_id in overlaped_gene_id:
                    gene_cds_range = gene_cds_intervals_dict[gene_id]
                    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
                        cds_range, gene_cds_range)
                    overlap_ratio = overlap_length/cds_length

                    if overlap_ratio >= args.annotated_coverage:
                        hit_gene.new_anno = (
                            False, known_gene_id, overlap_ratio)
                    else:
                        hit_gene.new_anno = (
                            True, known_gene_id, overlap_ratio)

        # turn genewise_out to a dict, key is query_name
        genewise_dict = {}
        for query_HPR in genewise_out:
            genewise_dict[query_HPR.query_gene.id] = query_HPR

        OUT = open(genewise_dict_file, 'wb')
        pickle.dump(genewise_dict, OUT)
        OUT.close()
    else:
        logger.info("comparsion already finished")
        TEMP = open(genewise_dict_file, 'rb')
        genewise_dict = pickle.load(TEMP)
        TEMP.close()

    logger.info(
        "%d query seq get %d genewise hit, %d can pass coverage test, %d are on the known gene loci, %d are good new hit" % (
            len(genewise_dict),
            sum([len(genewise_dict[i].hit_gene_list) for i in genewise_dict]),
            sum([len([j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass]) for i in
                 genewise_dict]),
            sum([len([j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass and not j.new_anno[0]])
                 for i in genewise_dict]),
            sum([len(
                [j for j in genewise_dict[i].hit_gene_list if j.map_quality_pass and j.new_anno[0]])
                for i in genewise_dict])
        ))

    # step4 use seq_classify to check if new hit's gene family
    logger.info("Step4: use seq_classify to check if new hit's gene family")

    seq_classify_dict_file = args.work_dir + "/3.seq_classify_dict.pyb"

    if not os.path.exists(seq_classify_dict_file):
        seq_classify_dir = args.work_dir + "/seq_classify"
        mkdir(seq_classify_dir, True)

        good_hit_list = []
        for og_id in candi_loss_list:
            og = csv_OGs.OG_dict[og_id]
            for sp_id in ref_sp_list:
                for gene in og.gene_dict[sp_id]:
                    if gene.id in genewise_dict:
                        for hit in genewise_dict[gene.id].hit_gene_list:
                            if hit.new_anno[0]:
                                good_hit_list.append(hit)

        args_list = []
        args_id_list = []
        for hit in good_hit_list:
            sub_work_dir = seq_classify_dir + "/" + hit.id
            args_list.append(
                (hit.model_aa_seq, args.orthogroup_scaffold_dir, sub_work_dir, True))
            args_id_list.append(hit.id)

        mlt_out = multiprocess_running(
            seq_classify, args_list, args.num_threads, args_id_list=args_id_list, log_file=args.log_file)

        seq_classify_dict = {}
        for i in mlt_out:
            seq_classify_dict[i] = mlt_out[i]['output']
            # seq_classify_dict[mlt_out[i]['args'][2].split("/")[-1]] = mlt_out[i]['output']

        OUT = open(seq_classify_dict_file, 'wb')
        pickle.dump(seq_classify_dict, OUT)
        OUT.close()

    else:
        TEMP = open(seq_classify_dict_file, 'rb')
        seq_classify_dict = pickle.load(TEMP)
        TEMP.close()

    # step5 decide if orthogroups lost in target
    logger.info("Step5: decide if orthogroups lost in target")

    reanno_og_dict = {}
    for og_id in candi_loss_list:
        og = csv_OGs.OG_dict[og_id]

        patch_hits = []
        for sp_id in ref_sp_list:
            for gene in og.gene_dict[sp_id]:
                if gene.id in genewise_dict:
                    for hit in genewise_dict[gene.id].hit_gene_list:
                        if hit.new_anno[0]:
                            if hit.id in seq_classify_dict:
                                if seq_classify_dict[hit.id] == og_id:
                                    patch_hits.append(hit)

        if len(patch_hits) > 0:
            reanno_og_dict[og_id] = merge_patch_hits(patch_hits)

    # step6 output
    logger.info("Step6: make output")

    new_csv_og_list = []
    for og_id in csv_OGs.OG_dict:
        og = csv_OGs.OG_dict[og_id]

        if og_id in reanno_og_dict:
            gene_list = og.gene_list
            for hit in reanno_og_dict[og_id]:
                gene_list.append(Gene(id=hit.id, species=args.target_speci))

            og = OrthoGroup(id=og.id, from_gene_list=gene_list,
                            species_list=og.species_list)

        new_csv_og_list.append(og)

    new_csv_OGs = OrthoGroups(from_OG_list=new_csv_og_list)
    new_csv_OGs.write_OG_tsv_file(args.work_dir + "/4.gene_loss.tsv")

    logger.info("In %d conserved orthogroups, %d (%.2f%%) orthogroups don't have gene in %s, %d can find back, %d (%.2f%%) are truly lost" % (len(csv_OGs.OG_id_list), len(candi_loss_list), len(
        candi_loss_list)/len(csv_OGs.OG_id_list)*100, args.target_speci, len(reanno_og_dict), len(candi_loss_list) - len(reanno_og_dict), (len(candi_loss_list) - len(reanno_og_dict))/len(csv_OGs.OG_id_list)*100))


def GeneLoss_args_parser(args):

    # configure file argument parse

    try:
        script_dir_path = os.path.split(os.path.realpath(__file__))[0]
        defaults_config_file = script_dir_path + \
            "/GeneLoss2_defaults.ini"
    except:
        defaults_config_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/src/xuyuxing/GenomeTools/GeneLoss2_defaults.ini"
    # print(defaults_config_file)

    args_type = {
        # str
        "config_file": "str",
        "conserved_species": "str",
        "orthogroup_scaffold_dir": "str",
        "wpgmapper_dir": "str",
        "target_speci": "str",
        "target_speci_annotation": "str",
        "work_dir": "str",
        "log_file": "str",
        "target_speci_feature": "str",

        # float
        "min_cover": "float",
        "min_identity": "float",
        "annotated_coverage": "float",

        # int
        "num_threads": "int",
        "top_evidence_num": "int",
        "min_aa_len": "int",
        "min_score": "int",
    }

    args = configure_parser(args, defaults_config_file,
                            args.config_file, args_type, None)

    # Modify_dict parse
    cfg = configparser.ConfigParser()
    cfg.read(args.config_file)

    # geneloss running

    if args.log_file is None:
        args.log_file = args.work_dir + "/log"

    GeneLoss_main(args)


if __name__ == '__main__':
    # command argument parse
    class abc(object):
        pass

    args = abc()

    args.conserved_species = "Ath;Ini;Llu;Cca,Sly,Oeu,Sin,Mgu,3"
    args.orthogroup_scaffold_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/orthologous_scaffold"
    args.wpgmapper_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/WPGmapper/Ocu_WPGmapper"
    args.target_speci = "Ocu"
    args.target_speci_annotation = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Orobanche_cumana/T78542N0.genome.gff3"
    args.work_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu"
    args.log_file = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu/log"
    args.num_threads = 56

    args.top_evidence_num = 20
    args.min_cover = 0.5
    args.min_aa_len = 50
    args.min_identity = 0.3
    args.min_score = 50
    args.target_speci_feature = 'gene'
    args.annotated_coverage = 0.8

    GeneLoss_main(args)
