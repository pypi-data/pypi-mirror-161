from toolbiox.config import plant_tribes_scaffold_dir, plant_tribes_default_scaffold, hmmsearch_path, cap3_path, transdecoder_path, gt_path, trimal_path, cd_hit_dir_path, diamond_path, hmmpress_path, hmmbuild_path, clustalo_path
from toolbiox.lib.common.evolution.orthotools2 import read_species_info, OrthoGroups
from toolbiox.lib.common.fileIO import read_list_file, tsv_file_dict_parse
from toolbiox.lib.common.genome.seq_base import BioSeq, read_fasta_by_faidx, reverse_complement, read_fasta
from toolbiox.lib.common.os import cmd_run, mkdir, multiprocess_running, rmdir, move_file, get_file_name, get_file_dir
from toolbiox.lib.xuyuxing.base.base_function import merge_file
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from retry import retry
from scipy import stats
import numpy as np
import os
import re
import pickle

# build scafflod dir


def run_clustalo(in_file, aln_file, cpu_num=1):
    in_file = os.path.abspath(in_file)
    aln_file = os.path.abspath(aln_file)
    work_dir = get_file_dir(aln_file)

    if not(os.path.exists(aln_file) and os.path.getsize(aln_file) != 0):
        cmd_string = clustalo_path + " -i %s -o %s -t Protein --force --auto --threads=%d" % (
            in_file, aln_file, cpu_num)
        cmd_run(cmd_string, cwd=work_dir, silence=True)


def run_hmmbuild(in_file, hmm_file):
    in_file = os.path.abspath(in_file)
    hmm_file = os.path.abspath(hmm_file)
    work_dir = get_file_dir(hmm_file)

    if not(os.path.exists(hmm_file) and os.path.getsize(hmm_file) != 0):
        cmd_string = hmmbuild_path + " %s %s" % (hmm_file, in_file)
        cmd_run(cmd_string, cwd=work_dir, silence=True)


def build_scaffold_orthogroups(orthogroups, species_info_dict, output_dir, num_threads):
    output_dir = os.path.abspath(output_dir)

    mkdir(output_dir, True)

    orthogroups.scaffold_dir = output_dir

    orthogroups.write_OG_tsv_file(output_dir+"/orthogroups.tsv")

    orthogroups.OG_tsv_file = output_dir+"/orthogroups.tsv"

    sub_dir_dict = {
        'alns': output_dir + "/alns",
        'db': output_dir + "/db",
        'fasta': output_dir + "/fasta",
        'hmms': output_dir + "/hmms",
    }

    orthogroups.scaffold_sub_dir = sub_dir_dict

    for i in sub_dir_dict:
        mkdir(sub_dir_dict[i], True)

    sorted_og_list = sorted(orthogroups.OG_id_list, key=lambda x: len(
        orthogroups.OG_dict[x].gene_list), reverse=True)

    # write fasta
    input_aa_fasta_dict = {}
    for sp_id in species_info_dict:
        input_aa_fasta_dict[sp_id] = read_fasta_by_faidx(
            species_info_dict[sp_id].pt_file)

    input_cds_fasta_dict = {}
    for sp_id in species_info_dict:
        if species_info_dict[sp_id].cds_file:
            input_cds_fasta_dict[sp_id] = read_fasta_by_faidx(
                species_info_dict[sp_id].cds_file)

    seq_dir = sub_dir_dict['fasta']
    mkdir(seq_dir, True)

    for raw_og_id in sorted_og_list:
        cds_file = seq_dir + "/%s.fna" % raw_og_id
        aa_file = seq_dir + "/%s.faa" % raw_og_id

        og = orthogroups.OG_dict[raw_og_id]
        og.aa_seq_file = aa_file
        og.cds_seq_file = cds_file

        if not(os.path.exists(aa_file) and os.path.getsize(aa_file) != 0):

            cds_f = open(cds_file, 'w')
            aa_f = open(aa_file, 'w')

            og = orthogroups.OG_dict[raw_og_id]
            for sp_id in og.gene_dict:
                gene_list = og.gene_dict[sp_id]
                for gene in gene_list:
                    if sp_id in input_cds_fasta_dict:
                        cds_f.write(">%s\n%s\n" %
                                    (gene.id, input_cds_fasta_dict[sp_id][gene.id].seq))
                    aa_f.write(">%s\n%s\n" %
                               (gene.id, input_aa_fasta_dict[sp_id][gene.id].seq))

            cds_f.close()
            aa_f.close()

    # get aln
    aln_dir = sub_dir_dict['alns']
    mkdir(aln_dir, True)

    args_list = []
    for raw_og_id in sorted_og_list:
        aa_file = seq_dir + "/%s.faa" % raw_og_id
        aln_file = aln_dir + "/%s.aln" % raw_og_id

        og = orthogroups.OG_dict[raw_og_id]
        og.aa_aln_file = aln_file

        args_list.append((aa_file, aln_file))

    multiprocess_running(run_clustalo, args_list, num_threads, silence=True)

    # get hmm
    hmm_dir = sub_dir_dict['hmms']
    mkdir(hmm_dir, True)

    args_list = []
    for raw_og_id in sorted_og_list:
        aln_file = aln_dir + "/%s.aln" % raw_og_id
        hmm_file = hmm_dir + "/%s.hmm" % raw_og_id

        og = orthogroups.OG_dict[raw_og_id]
        og.hmm_file = hmm_file

        args_list.append((aln_file, hmm_file))

    multiprocess_running(run_hmmbuild, args_list, num_threads, silence=True)

    # get db
    # hmm
    hmm_file_list = [hmm_dir + "/%s.hmm" % raw_og_id
                     for raw_og_id in sorted_og_list if os.path.exists(hmm_dir + "/%s.hmm" % raw_og_id)]

    hmm_db_dir = sub_dir_dict['db'] + "/hmm"
    mkdir(hmm_db_dir, True)

    hmm_db_file = hmm_db_dir + "/hmm_db.hmm"
    merge_file(hmm_file_list, hmm_db_file)

    cmd_string = hmmpress_path + " " + hmm_db_file
    cmd_run(cmd_string, cwd=hmm_db_dir, silence=True)

    orthogroups.hmm_db = hmm_db_file

    # diamond
    aa_file_list = [seq_dir + "/%s.faa" % raw_og_id
                    for raw_og_id in sorted_og_list if os.path.exists(seq_dir + "/%s.faa" % raw_og_id)]

    diamond_db_dir = sub_dir_dict['db'] + "/diamond"
    mkdir(diamond_db_dir, True)

    diamond_db_file = diamond_db_dir + "/diamond_db.faa"
    merge_file(aa_file_list, diamond_db_file)

    cmd_string = "%s makedb --in %s --db %s" % (
        diamond_path, diamond_db_file, diamond_db_file)
    cmd_run(cmd_string, cwd=diamond_db_dir, silence=True)

    orthogroups.hmm_db = diamond_db_file+".dmnd"

    orthogroups.pickle_file = orthogroups.scaffold_dir + "/OG_pickle.py"

    OUT = open(orthogroups.pickle_file, 'wb')
    pickle.dump(orthogroups, OUT)
    OUT.close()

    return orthogroups


def build_scaffold_main(args):
    # read orthogroups
    orthogroups = OrthoGroups(OG_tsv_file=args.orthogroups_file)

    og_list = []
    for og_id in orthogroups.OG_id_list:
        og = orthogroups.OG_dict[og_id]
        g_num = len(og.gene_list)
        s_num = len([i for i in og.species_stat if og.species_stat[i] != 0])
        if g_num >= args.min_gene_number and s_num >= args.min_species_number:
            og_list.append(og)

    orthogroups = OrthoGroups(from_OG_list=og_list)

    # read file of files
    species_info_dict = read_species_info(args.species_info_file)

    # build scaffold dir
    build_scaffold_orthogroups(orthogroups, species_info_dict,
                               args.scaffold_dir, args.num_threads)


# seq_classify
def read_hmm_out_get_subject_id_list(hmm_out_file):
    subject_id_list = []
    with open(hmm_out_file, 'r') as f:
        for each_line in f:
            if not re.match(r'^#', each_line):
                s_id = each_line.split()[0]
                subject_id_list.append(s_id)
    return list(set(subject_id_list))


def read_hmm_out_get_subject_id_score_dict(hmm_out_file):
    score_dict = {}
    num = 0
    with open(hmm_out_file, 'r') as f:
        for each_line in f:
            if not re.match(r'^#', each_line):
                s_id = each_line.split()[0]
                score = float(each_line.split()[5])
                if s_id in score_dict:
                    if score > score_dict[s_id]:
                        score_dict[s_id] = score
                else:
                    score_dict[s_id] = score
            num += 1
            if num % 1000000 == 0:
                print(num)
    return score_dict


def read_hmm_out_get_query_id_score_dict(hmm_out_file):
    score_dict = {}
    num = 0
    with open(hmm_out_file, 'r') as f:
        for each_line in f:
            if not re.match(r'^#', each_line):
                q_id = each_line.split()[2]
                score = float(each_line.split()[5])
                if q_id in score_dict:
                    if score > score_dict[q_id]:
                        score_dict[q_id] = score
                else:
                    score_dict[q_id] = score
            num += 1
            if num % 1000000 == 0:
                print(num)
    return score_dict


def seq_in_ortho_stat(protein_seq, scaffold_hmm_file, scaffold_seq_fasta, scaffold_msa_file, work_dir, num_threads=1):
    mkdir(work_dir, True)

    input_fasta = work_dir + "/input.faa"

    with open(input_fasta, 'w') as f:
        f.write(">%s\n%s" % ("input_now", protein_seq.seq))

    # get stats
    # hmm score
    hmm_out_file = work_dir + "/pep.hmm.tbl"
    hmm_log_file = work_dir + "/pep.hmm.log"

    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, hmm_out_file, hmm_log_file, scaffold_hmm_file, input_fasta)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    backbone_hmm_out_file = work_dir + "/backbone.hmm.tbl"
    backbone_hmm_log_file = work_dir + "/backbone.hmm.log"

    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, backbone_hmm_out_file, backbone_hmm_log_file, scaffold_hmm_file, scaffold_seq_fasta)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    backbone_score_dict = read_hmm_out_get_subject_id_score_dict(
        backbone_hmm_out_file)
    pep_score_dict = read_hmm_out_get_subject_id_score_dict(
        hmm_out_file)

    backbone_score = [backbone_score_dict[i] for i in backbone_score_dict]

    avg_backbone_score = sum(backbone_score)/len(backbone_score)
    std_backbone_score = np.std(np.array(backbone_score))

    # aln
    pep_aln_file = work_dir + "/pep.aln"
    cmd_string = "mafft --add %s %s > %s" % (
        input_fasta, scaffold_msa_file, pep_aln_file)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    pep_trim_aln_file = work_dir + "/pep.trim.aln"
    cmd_string = "%s -in %s -out %s -gt 0.1 >/dev/null" % (
        trimal_path, pep_aln_file, pep_trim_aln_file)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    backbone_seq_id_list = list(read_fasta_by_faidx(scaffold_seq_fasta).keys())
    input_seq_id_list = list(read_fasta_by_faidx(input_fasta).keys())

    aln_seq_dict = read_fasta_by_faidx(pep_trim_aln_file)

    if not (aln_seq_dict[list(aln_seq_dict.keys())[0]].len() == 0):
        stat_dict = {}
        for seq_id in aln_seq_dict:
            aln_seq = aln_seq_dict[seq_id].seq
            aln_cov = len(aln_seq.replace("-", ""))/len(aln_seq)
            stat_dict[seq_id] = (len(aln_seq.replace("-", "")),
                                 len(aln_seq), aln_cov)

        backbone_len = [stat_dict[i][0]
                        for i in stat_dict if i in backbone_seq_id_list]
        backbone_cov = [stat_dict[i][2]
                        for i in stat_dict if i in backbone_seq_id_list]

        if len(backbone_len):
            avg_backbone_len = sum(backbone_len)/len(backbone_len)
        else:
            avg_backbone_len = 0
        std_backbone_len = np.std(np.array(backbone_len))

        avg_backbone_cov = sum(backbone_cov)/len(backbone_cov)
        std_backbone_cov = np.std(np.array(backbone_cov))

    else:
        avg_backbone_len = 0.0
        std_backbone_len = 0.0
        avg_backbone_cov = 0.0
        std_backbone_cov = 0.0
        stat_dict = {i: (0, 0, 0.0) for i in input_seq_id_list}

    i = "input_now"
    if i in pep_score_dict:
        score = pep_score_dict[i]
    else:
        score = 0.0

    # col_list = ["seq_id", "cov", "avg_cov", "sd_cov", "len", "avg_len", "sd_len", "score", "avg_score", "sd_score"]

    rmdir(work_dir)

    return protein_seq.seqname, stat_dict[i][2], avg_backbone_cov, std_backbone_cov, stat_dict[i][0], avg_backbone_len, std_backbone_len, score, avg_backbone_score, std_backbone_score


def make_seqs_stat_file(input_fasta, scaffold_hmm_file=None, scaffold_seq_fasta=None, scaffold_msa_file=None, work_dir=None, num_threads=1):
    mkdir(work_dir, True)

    # get stats
    # hmm score
    if scaffold_hmm_file:
        hmm_out_file = work_dir + "/pep.hmm.tbl"
        hmm_log_file = work_dir + "/pep.hmm.log"

        cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
            hmmsearch_path, num_threads, hmm_out_file, hmm_log_file, scaffold_hmm_file, input_fasta)
        cmd_run(cmd_string, silence=True, cwd=work_dir)

        backbone_hmm_out_file = work_dir + "/backbone.hmm.tbl"
        backbone_hmm_log_file = work_dir + "/backbone.hmm.log"

        cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
            hmmsearch_path, num_threads, backbone_hmm_out_file, backbone_hmm_log_file, scaffold_hmm_file, scaffold_seq_fasta)
        cmd_run(cmd_string, silence=True, cwd=work_dir)

        backbone_score_dict = read_hmm_out_get_subject_id_score_dict(
            backbone_hmm_out_file)
        pep_score_dict = read_hmm_out_get_subject_id_score_dict(
            hmm_out_file)

        backbone_score = [backbone_score_dict[i] for i in backbone_score_dict]

        avg_backbone_score = sum(backbone_score)/len(backbone_score)
        std_backbone_score = np.std(np.array(backbone_score))
    else:
        pep_score_dict = {}
        avg_backbone_score = 0.0
        std_backbone_score = 0.0

    # aln
    pep_aln_file = work_dir + "/pep.aln"
    cmd_string = "mafft --add %s %s > %s" % (
        input_fasta, scaffold_msa_file, pep_aln_file)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    pep_trim_aln_file = work_dir + "/pep.trim.aln"
    cmd_string = "%s -in %s -out %s -gt 0.1 >/dev/null" % (
        trimal_path, pep_aln_file, pep_trim_aln_file)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    backbone_seq_id_list = list(read_fasta_by_faidx(scaffold_seq_fasta).keys())
    input_seq_id_list = list(read_fasta_by_faidx(input_fasta).keys())

    aln_seq_dict = read_fasta_by_faidx(pep_trim_aln_file)

    if not (aln_seq_dict[list(aln_seq_dict.keys())[0]].len() == 0):
        stat_dict = {}
        for seq_id in aln_seq_dict:
            aln_seq = aln_seq_dict[seq_id].seq
            aln_cov = len(aln_seq.replace("-", ""))/len(aln_seq)
            stat_dict[seq_id] = (len(aln_seq.replace("-", "")),
                                 len(aln_seq), aln_cov)

        backbone_len = [stat_dict[i][0]
                        for i in stat_dict if i in backbone_seq_id_list]
        backbone_cov = [stat_dict[i][2]
                        for i in stat_dict if i in backbone_seq_id_list]

        if len(backbone_len):
            avg_backbone_len = sum(backbone_len)/len(backbone_len)
            std_backbone_len = np.std(np.array(backbone_len))

            avg_backbone_cov = sum(backbone_cov)/len(backbone_cov)
            std_backbone_cov = np.std(np.array(backbone_cov))
        else:
            avg_backbone_len = 0.0
            std_backbone_len = 0.0
            avg_backbone_cov = 0.0
            std_backbone_cov = 0.0
            stat_dict = {i: (0, 0, 0.0) for i in input_seq_id_list}

    else:
        avg_backbone_len = 0.0
        std_backbone_len = 0.0
        avg_backbone_cov = 0.0
        std_backbone_cov = 0.0
        stat_dict = {i: (0, 0, 0.0) for i in input_seq_id_list}

    with open(work_dir+"/stats.txt", 'w') as f:
        col_list = ["seq_id", "cov", "avg_cov",
                    "sd_cov", "len", "avg_len", "sd_len", "score", "avg_score", "sd_score"]
        f.write("\t".join(col_list)+"\n")

        for i in input_seq_id_list:
            if i in pep_score_dict:
                score = pep_score_dict[i]
            else:
                score = 0.0

            write_list = [i, "%.2f" % stat_dict[i][2], "%.2f" % avg_backbone_cov, "%.2f" % std_backbone_cov,
                          "%.2f" % stat_dict[i][0], "%.2f" % avg_backbone_len, "%.2f" % std_backbone_len,
                          "%.2f" % score, "%.2f" % avg_backbone_score, "%.2f" % std_backbone_score, ]
            f.write("\t".join(write_list)+"\n")


def get_pass_seq_id(stats_file, p_value=0.05, only_cov=False):
    pass_seq_list = []

    if only_cov:
        judge_list = ['cov']
    else:
        judge_list = ['cov', 'score']

    if os.path.exists(stats_file) and os.path.getsize(stats_file) != 0:

        stats_info_dict = tsv_file_dict_parse(stats_file, key_col='seq_id')

        for seq_id in stats_info_dict:
            seq_info = stats_info_dict[seq_id]
            pass_flag = True
            for i in judge_list:
                seq_value = float(seq_info[i])
                avg_value = float(seq_info['avg_'+i])
                sd_value = float(seq_info['sd_'+i])

                if avg_value > 0.0:
                    distn = stats.norm(avg_value, sd_value)
                    if seq_value < distn.ppf(p_value):
                        pass_flag = False
                else:
                    pass_flag = False

            if pass_flag:
                pass_seq_list.append(seq_id)

    return pass_seq_list


def if_seq_in_ortho(protein_seq, scaffold_hmm_file, scaffold_seq_fasta, scaffold_msa_file, work_dir, clean_up=True, num_threads=1, only_cov=False):
    scaffold_hmm_file = os.path.abspath(scaffold_hmm_file)
    scaffold_seq_fasta = os.path.abspath(scaffold_seq_fasta)
    scaffold_msa_file = os.path.abspath(scaffold_msa_file)
    work_dir = os.path.abspath(work_dir)

    mkdir(work_dir, True)

    input_fasta = work_dir + "/input.faa"

    with open(input_fasta, 'w') as f:
        f.write(">%s\n%s" % ("input_now", protein_seq.seq))

    if only_cov:
        make_seqs_stat_file(input_fasta, None,
                        scaffold_seq_fasta, scaffold_msa_file, work_dir, num_threads=num_threads)
    else:
        make_seqs_stat_file(input_fasta, scaffold_hmm_file,
                        scaffold_seq_fasta, scaffold_msa_file, work_dir, num_threads=num_threads)

    stat_file = work_dir + "/stats.txt"

    pass_id_list = get_pass_seq_id(stat_file, p_value=0.05, only_cov=only_cov)

    if clean_up:
        rmdir(work_dir)

    if len(pass_id_list) > 0:
        return True
    else:
        return False


def get_best_ortho(seqname, hmm_results, diamond_out, scaffold_dir):
    hmm_score_dict = read_hmm_out_get_query_id_score_dict(hmm_results)

    if len(hmm_score_dict) > 0:
        hmm_top_og_id = sorted(
            hmm_score_dict, key=lambda x: hmm_score_dict[x], reverse=True)[0]
    else:
        hmm_top_og_id = None

    diamond_top_gene_id = None
    if diamond_out:
        with open(diamond_out, 'r') as f:
            all_info = f.read()
            if len(all_info) > 0:
                diamond_top_gene_id = all_info.split("\t")[1]

    if diamond_top_gene_id:
        og_tsv = scaffold_dir + "/orthogroups.tsv"
        with open(og_tsv, 'r') as f:
            for each_line in f:
                if diamond_top_gene_id in each_line:
                    diamond_top_og_id = each_line.split("\t")[0]
    else:
        diamond_top_og_id = None

    if hmm_top_og_id:
        top_og_id = hmm_top_og_id
    elif hmm_top_og_id is None:
        top_og_id = diamond_top_og_id

    return top_og_id


@retry(tries=5)
def seq_classify(protein_seq, scaffold_dir, work_dir, strict=True, clean_up=True):
    mkdir(work_dir, True)
    input_fasta = work_dir + "/input.faa"

    with open(input_fasta, 'w') as f:
        f.write(">%s\n%s" % (protein_seq.seqname, protein_seq.seq))

    # get best ortho
    hmm_db = scaffold_dir + "/db/hmm/hmm_db.hmm"

    hmm_results = work_dir + "/hmm.tbl"
    hmm_log = work_dir + "/hmm.log"

    cmd_string = '%s -E 1e-20 --cpu 1 --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, hmm_results, hmm_log, hmm_db, input_fasta)
    cmd_run(cmd_string, cwd=work_dir, silence=True)

    if strict:
        diamond_db = scaffold_dir + "/db/diamond/diamond_db.faa.dmnd"

        diamond_out = work_dir + "/diamond.bls"

        cmd_string = "diamond blastp -q %s -k 50 -e 1e-5 -d %s -o %s -f 6 -p 1" % (
            input_fasta, diamond_db, diamond_out)

        cmd_run(cmd_string, cwd=work_dir, silence=True)
    else:
        diamond_out = None

    best_ortho = get_best_ortho(
        protein_seq.seqname, hmm_results, diamond_out, scaffold_dir)

    if strict:
        pass_flag = False
        if best_ortho:
            scaffold_hmm_file = "%s/hmms/%s.hmm" % (scaffold_dir, best_ortho)
            scaffold_seq_fasta = "%s/fasta/%s.faa" % (scaffold_dir, best_ortho)
            scaffold_msa_file = "%s/alns/%s.aln" % (scaffold_dir, best_ortho)
            check_dir = work_dir + "/check_dir"

            pass_flag = if_seq_in_ortho(protein_seq, scaffold_hmm_file,
                                        scaffold_seq_fasta, scaffold_msa_file, check_dir, clean_up, 1)
    else:
        pass_flag = True

    if clean_up:
        rmdir(work_dir)

    if best_ortho and pass_flag:
        return best_ortho
    else:
        return None


def seq_classify_main(args):
    args.scaffold_dir = os.path.abspath(args.scaffold_dir)
    args.input_fasta = os.path.abspath(args.input_fasta)
    args.output_file = os.path.abspath(args.output_file)

    if not args.work_dir:
        args.work_dir = get_file_dir(args.input_fasta) + "/tmp"
    else:
        args.work_dir = os.path.abspath(args.work_dir)

    mkdir(args.work_dir, True)

    seq_dict = read_fasta_by_faidx(args.input_fasta)

    args_list = []
    args_id_list = []
    for seq_id in seq_dict:
        work_dir = args.work_dir + "/" + seq_id
        seq_record = seq_dict[seq_id]
        seq_record = BioSeq(seq_record.seq, seq_record.seqname)
        args_list.append((seq_record, args.scaffold_dir, work_dir, args.strict, True))
        args_id_list.append(seq_id)

    mlt_out = multiprocess_running(
        seq_classify, args_list, args.thread_number, None, False, args_id_list)

    with open(args.output_file, 'w') as f:
        for seq_id in mlt_out:
            best_ortho = mlt_out[seq_id]['output']
            if best_ortho:
                f.write("%s\t%s\n" % (seq_id, best_ortho))

    rmdir(args.work_dir)


if __name__ == '__main__':
    from toolbiox.lib.common.evolution.orthotools2 import read_species_info, OrthoGroups

    species_info_file = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/Oro_ref.xlsx"
    orthogroups_file = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/tree/orthologous_OGs.tsv"
    num_threads = 56

    # read orthogroups
    orthogroups = OrthoGroups(OG_tsv_file=orthogroups_file)

    og_list = []
    for i in orthogroups.OG_id_list[18000:19000]:
        og_list.append(orthogroups.OG_dict[i])

    orthogroups = OrthoGroups(from_OG_list=og_list)

    # read file of files
    species_info_dict = read_species_info(species_info_file)

    # build scaffold dir
    scaffold_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu/test2"
    scaf_OGs = build_scaffold_orthogroups(orthogroups, species_info_dict,
                                          scaffold_dir, num_threads)

    # big seq_classify
    "hmmsearch -E 1e-20 --cpu 1 --noali --tblout all.input.fasta.tbl -o all.input.fasta.log hmm_db.hmm all.input.fasta"

    import os
    import re
    from toolbiox.lib.common.genome.seq_base import read_fasta
    from toolbiox.api.xuyuxing.comp_genome.planttribes2 import if_seq_in_ortho
    from toolbiox.lib.common.os import multiprocess_running

    hmm_out_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/hmm/all.input.fasta.tbl'

    score_dict = {}
    num = 0
    with open(hmm_out_file, 'r') as f:
        for each_line in f:
            if not re.match(r'^#', each_line):
                q_id = each_line.split()[2]
                s_id = each_line.split()[0]
                score = float(each_line.split()[5])

                score_dict.setdefault(s_id,(q_id, score))
                
                if score > score_dict[s_id][1]:
                    score_dict[s_id] = (q_id, score)

            num += 1
            if num % 1000000 == 0:
                print(num)

    sp_seq_dict = {}
    for seq_id in score_dict:
        sp_id = seq_id.split("_")[0] + "_" +seq_id.split("_")[1]
        sp_seq_dict.setdefault(sp_id, {})
        sp_seq_dict[sp_id][seq_id] = score_dict[seq_id]

    seqclassify_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify"

    for sp_id in sp_seq_dict:
        output_file = seqclassify_dir + "/" + sp_id + "/output.txt"
        with open(output_file, 'w') as f:
            for seq_id in sp_seq_dict[sp_id]:
                og_id, score = sp_seq_dict[sp_id][seq_id]
                f.write("%s\t%s\n" % (seq_id, og_id))

    Tri_ver_output = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/Reh_glu/output.txt"
    Tri_ver_filter_output = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/Reh_glu/output.filter.txt"
    Tri_ver_ctm = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/Reh_glu/no.ctm.id"

    from toolbiox.lib.common.fileIO import read_list_file
    from toolbiox.lib.common.fileIO import tsv_file_dict_parse

    Tri_ver_ctm_list = set(read_list_file(Tri_ver_ctm))

    raw_dict = tsv_file_dict_parse(Tri_ver_output, fieldnames=['g_id', 'og_id'], key_col='g_id')
    with open(Tri_ver_filter_output, 'w') as f:
        for g_id in raw_dict:
            if g_id in Tri_ver_ctm_list:
                f.write("%s\t%s\n" % (g_id, raw_dict[g_id]['og_id']))




    ##

    seq_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/1.clean_data/renamed_data'

    seq_dict = {}
    for i in os.listdir(seq_dir):
        f_name = re.findall(r'.*\.pt\.faa$', i)
        if len(f_name):
            f_name = f_name[0]
            sp_id = f_name.split(".")[0]
            print(sp_id)
            f_name = seq_dir + "/" + f_name
            seq_dict[sp_id] = read_fasta(f_name)[0]

    ##
    scaffold_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/2.scaffold/scaffold"
    work_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/hmm/tmp"

    args_list = []
    args_id_list = []

    for seq_id in score_dict:
        og_id, score = score_dict[seq_id]
        sp_id = seq_id.split("_")[0] + "_" +seq_id.split("_")[1]

        best_ortho = score_dict[seq_id][0]

        scaffold_hmm_file = "%s/hmms/%s.hmm" % (scaffold_dir, best_ortho)
        scaffold_seq_fasta = "%s/fasta/%s.faa" % (scaffold_dir, best_ortho)
        scaffold_msa_file = "%s/alns/%s.aln" % (scaffold_dir, best_ortho)

        protein_seq = seq_dict[sp_id][seq_id]

        work_dir_tmp = work_dir + "/" + seq_id

        args_list.append((protein_seq, scaffold_hmm_file, scaffold_seq_fasta, scaffold_msa_file, work_dir_tmp, True, 1, True))
        args_id_list.append(seq_id)

    mlt_out = multiprocess_running(if_seq_in_ortho, args_list, 80, None, False, args_id_list)

    with open("/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/3.init_filter/3.1.seqclassify/hmm/output.txt", 'w') as f:
        for seq_id in mlt_out:
            if mlt_out[seq_id]['output']:
                f.write("%s\t%s\n" % (seq_id, score_dict[seq_id][0]))