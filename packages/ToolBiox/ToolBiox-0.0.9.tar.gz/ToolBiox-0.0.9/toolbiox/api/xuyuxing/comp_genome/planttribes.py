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


def build_scaffold_dir(orthogroups, species_info_dict, output_dir, num_threads):
    output_dir = os.path.abspath(output_dir)

    mkdir(output_dir, True)

    orthogroups.write_OG_tsv_file(output_dir+"/orthogroups.tsv")

    sub_dir_dict = {
        'alns': output_dir + "/alns",
        'db': output_dir + "/db",
        'fasta': output_dir + "/fasta",
        'hmms': output_dir + "/hmms",
    }

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

        args_list.append((aa_file, aln_file))

    multiprocess_running(run_clustalo, args_list, num_threads, silence=True)

    # get hmm
    hmm_dir = sub_dir_dict['hmms']
    mkdir(hmm_dir, True)

    args_list = []
    for raw_og_id in sorted_og_list:
        aln_file = aln_dir + "/%s.aln" % raw_og_id
        hmm_file = hmm_dir + "/%s.hmm" % raw_og_id

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


def mulit_build_scaffold_dir_main(args):
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
    build_scaffold_dir(orthogroups, species_info_dict,
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
    return score_dict


def read_hmm_out_get_query_id_score_dict(hmm_out_file):
    score_dict = {}
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
    cmd_string = "mafft --anysymbol --add %s %s > %s" % (
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

    i = "input_now"
    if i in pep_score_dict:
        score = pep_score_dict[i]
    else:
        score = 0.0

    # col_list = ["seq_id", "cov", "avg_cov", "sd_cov", "len", "avg_len", "sd_len", "score", "avg_score", "sd_score"]

    rmdir(work_dir)

    return protein_seq.seqname, stat_dict[i][2], avg_backbone_cov, std_backbone_cov, stat_dict[i][0], avg_backbone_len, std_backbone_len, score, avg_backbone_score, std_backbone_score


def make_seqs_stat_file(input_fasta, scaffold_hmm_file, scaffold_seq_fasta, scaffold_msa_file, work_dir, num_threads=1):
    mkdir(work_dir, True)

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
    cmd_string = "mafft --anysymbol --add %s %s > %s" % (
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


def get_pass_seq_id(stats_file, p_value=0.05):
    pass_seq_list = []

    if os.path.exists(stats_file) and os.path.getsize(stats_file) != 0:

        stats_info_dict = tsv_file_dict_parse(stats_file, key_col='seq_id')

        for seq_id in stats_info_dict:
            seq_info = stats_info_dict[seq_id]
            pass_flag = True
            for i in ['cov', 'score']:
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


def if_seq_in_ortho(protein_seq, scaffold_hmm_file, scaffold_seq_fasta, scaffold_msa_file, work_dir, clean_up=True, num_threads=1):
    scaffold_hmm_file = os.path.abspath(scaffold_hmm_file)
    scaffold_seq_fasta = os.path.abspath(scaffold_seq_fasta)
    scaffold_msa_file = os.path.abspath(scaffold_msa_file)
    work_dir = os.path.abspath(work_dir)

    mkdir(work_dir, True)

    input_fasta = work_dir + "/input.faa"

    with open(input_fasta, 'w') as f:
        f.write(">%s\n%s" % ("input_now", protein_seq.seq))

    make_seqs_stat_file(input_fasta, scaffold_hmm_file,
                        scaffold_seq_fasta, scaffold_msa_file, work_dir, num_threads=num_threads)

    stat_file = work_dir + "/stats.txt"

    pass_id_list = get_pass_seq_id(stat_file)

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
def seq_classify(protein_seq, scaffold_dir, work_dir, clean_up=True):
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

    diamond_db = scaffold_dir + "/db/diamond/diamond_db.faa.dmnd"

    diamond_out = work_dir + "/diamond.bls"

    cmd_string = "diamond blastp -q %s -k 50 -e 1e-5 -d %s -o %s -f 6 -p 1" % (
        input_fasta, diamond_db, diamond_out)

    cmd_run(cmd_string, cwd=work_dir, silence=True)

    best_ortho = get_best_ortho(
        protein_seq.seqname, hmm_results, diamond_out, scaffold_dir)

    pass_flag = False
    if best_ortho:
        scaffold_hmm_file = "%s/hmms/%s.hmm" % (scaffold_dir, best_ortho)
        scaffold_seq_fasta = "%s/fasta/%s.faa" % (scaffold_dir, best_ortho)
        scaffold_msa_file = "%s/alns/%s.aln" % (scaffold_dir, best_ortho)
        check_dir = work_dir + "/check_dir"

        pass_flag = if_seq_in_ortho(protein_seq, scaffold_hmm_file,
                                    scaffold_seq_fasta, scaffold_msa_file, check_dir, clean_up, 1)

    if clean_up:
        rmdir(work_dir)

    if best_ortho and pass_flag:
        return best_ortho
    else:
        return None


# deep assembly
def clean_assembly_dir(assembly_dir):
    results_dir_flag = False
    for i in os.listdir(assembly_dir):
        if not i in ['results_dir', "pep.fa", "cDNA.fa", "cds.fa", "stats.txt"]:
            rmdir(assembly_dir+"/"+i)
        if i == 'results_dir':
            results_dir_flag = True

    if results_dir_flag:
        for i in ["pep.fa", "cDNA.fa", "cds.fa", "stats.txt"]:
            if os.path.exists(assembly_dir+"/results_dir/"+i):
                move_file(assembly_dir+"/results_dir/"+i, assembly_dir+"/"+i)
        rmdir(assembly_dir+"/results_dir")


@retry(tries=5)
def one_family_assembly(cdna_file, tran_pep_file, hmm_file, aln_file, seq_file, out_dir, out_reads_prefix, transdecoder_id=False, num_threads=1, clean_up=True):
    """
    hmm_file = '/lustre/home/xuyuxing/Program/PlantTribes/PlantTribes_scaffolds/data/26Gv2.0/hmms/orthofinder/25.hmm'
    aln_file = '/lustre/home/xuyuxing/Program/PlantTribes/PlantTribes_scaffolds/data/26Gv2.0/alns/orthofinder/25.aln'
    seq_file = '/lustre/home/xuyuxing/Program/PlantTribes/PlantTribes_scaffolds/data/26Gv2.0/fasta/orthofinder/25.faa'
    out_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/other_species_trans/Cistanche_deserticola/AssemblyPostProcessor/assembly_dir/25'
    tran_pep_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/other_species_trans/Cistanche_deserticola/AssemblyPostProcessor/Trinity.fasta.transdecoder_dir/longest_orfs.pep'
    cdna_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/other_species_trans/Cistanche_deserticola/Cistanche_deserticola.trinity2.out3/Trinity.fasta'
    out_reads_prefix = 'planttribes_25_'
    transdecoder_id=True
    num_threads=1
    clean_up=True
    """

    already_flag = True
    for i in ["pep.fa", "cDNA.fa", "cds.fa", "stats.txt"]:
        i = out_dir + "/" + i
        if not (os.path.exists(i) and os.path.getsize(i)):
            already_flag = False

    if already_flag:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    mkdir(out_dir, False)

    # hmm run
    hmm_out_file = out_dir + "/hmm.tbl"
    hmm_log_file = out_dir + "/hmm.log"
    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, hmm_out_file, hmm_log_file, hmm_file, tran_pep_file)
    cmd_run(cmd_string, silence=True)
    subject_id_list = read_hmm_out_get_subject_id_list(hmm_out_file)

    if len(subject_id_list) == 0:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    # cap run
    subject_seq_file = out_dir + "/hmm.subject.fasta"
    seq_dict = read_fasta_by_faidx(cdna_file)

    subject_seq_dict = {}
    if transdecoder_id:
        for i in subject_id_list:
            cdna_id = i.split(".")[0]
            subject_seq_dict[cdna_id] = seq_dict[cdna_id].seq
    else:
        for i in subject_id_list:
            subject_seq_dict[i] = seq_dict[i].seq

    with open(subject_seq_file, 'w') as f:
        for s_id in subject_seq_dict:
            f.write(">%s\n%s\n" % (s_id, subject_seq_dict[s_id]))

    cmd_string = "%s %s -o 40 -p 90 >/dev/null" % (cap3_path, subject_seq_file)
    cmd_run(cmd_string, silence=True)

    cap_contig_file = out_dir + "/hmm.subject.fasta.cap.contigs"
    cap_singlet_file = out_dir + "/hmm.subject.fasta.cap.singlets"

    contig_dict = {}
    if os.path.getsize(cap_contig_file):
        contig_dict = read_fasta_by_faidx(cap_contig_file)

    singlet_dict = {}
    if os.path.getsize(cap_singlet_file):
        singlet_dict = read_fasta_by_faidx(cap_singlet_file)

    assembly_seq_file = out_dir + "/cap3.assembly.fasta"
    assembly_seq_dict = {}
    num = 0
    with open(assembly_seq_file, 'w') as f:
        for s_id in contig_dict:
            num += 1
            new_s_id = out_reads_prefix + str(num)
            f.write(">%s\n%s\n" % (new_s_id, contig_dict[s_id].seq))
            assembly_seq_dict[new_s_id] = contig_dict[s_id].seq
        for s_id in singlet_dict:
            num += 1
            new_s_id = out_reads_prefix + str(num)
            f.write(">%s\n%s\n" % (new_s_id, singlet_dict[s_id].seq))
            assembly_seq_dict[new_s_id] = singlet_dict[s_id].seq

    # transdecoder
    cmd_string = '%s -t %s >/dev/null' % (transdecoder_path, assembly_seq_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)
    longest_orfs_pep_file = out_dir + \
        "/cap3.assembly.fasta.transdecoder_dir/longest_orfs.pep"
    longest_orfs_gff_file = out_dir + \
        "/cap3.assembly.fasta.transdecoder_dir/longest_orfs.gff3"
    longest_orfs_cds_file = out_dir + \
        "/cap3.assembly.fasta.transdecoder_dir/longest_orfs.cds"

    if os.path.getsize(longest_orfs_pep_file) == 0:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    # filter low hmm pep
    filter_hmm_out_file = out_dir + \
        "/cap3.assembly.fasta.transdecoder_dir/longest_orfs.pep.hmm.tbl"
    filter_hmm_log_file = out_dir + \
        "/cap3.assembly.fasta.transdecoder_dir/longest_orfs.pep.hmm.log"

    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, filter_hmm_out_file, filter_hmm_log_file, hmm_file, longest_orfs_pep_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir +
            "/cap3.assembly.fasta.transdecoder_dir")
    good_subject_id_list = read_hmm_out_get_subject_id_list(
        filter_hmm_out_file)

    if len(good_subject_id_list) == 0:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    # get model (longest) protein sequence
    longest_orfs_pep_dict = read_fasta_by_faidx(longest_orfs_pep_file)
    longest_orfs_cds_dict = read_fasta_by_faidx(longest_orfs_cds_file)

    candi_seq_dict = {}
    for seq_id in good_subject_id_list:
        parent_id, sub_id, strand = re.findall(
            r'(.*)(\.p\d+).*\((\S+)\)$', longest_orfs_pep_dict[seq_id].seqname)[0]
        cdna_seq = assembly_seq_dict[parent_id] if strand == '+' else reverse_complement(
            assembly_seq_dict[parent_id])

        pep_seq = longest_orfs_pep_dict[seq_id].seq
        cds_seq = longest_orfs_cds_dict[seq_id].seq
        if pep_seq[-1] == '*':
            pep_seq = pep_seq[:-1]
            cds_seq = cds_seq[:-3]

        if len(cds_seq)/len(pep_seq) != 3.0:
            continue

        if not parent_id in candi_seq_dict:
            candi_seq_dict[parent_id] = {
                'cdna': cdna_seq,
                'cds': cds_seq,
                'pep': pep_seq,
            }
        elif len(longest_orfs_pep_dict[seq_id].seq) > len(candi_seq_dict[parent_id]['pep']):
            candi_seq_dict[parent_id] = {
                'cdna': cdna_seq,
                'cds': cds_seq,
                'pep': pep_seq,
            }

    if len(candi_seq_dict) == 0:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    # dereplicate
    candi_cds_file = out_dir + "/candi_cds.fa"
    with open(candi_cds_file, 'w') as f:
        for parent_id in candi_seq_dict:
            f.write(">%s\n%s\n" %
                    (parent_id, candi_seq_dict[parent_id]['cds']))

    uniq_cds_file = out_dir + "/uniq_cds.fa"
    cmd_string = "%s sequniq -force -o %s %s >/dev/null" % (
        gt_path, uniq_cds_file, candi_cds_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)
    uniq_id_list = list(read_fasta_by_faidx(uniq_cds_file).keys())

    uniq_pep_file = out_dir + "/uniq_pep.fa"
    with open(uniq_pep_file, 'w') as f:
        for parent_id in uniq_id_list:
            f.write(">%s\n%s\n" %
                    (parent_id, candi_seq_dict[parent_id]['pep']))

    # get stats
    # hmm score
    uniq_pep_hmm_out_file = out_dir + "/uniq_pep.hmm.tbl"
    uniq_pep_hmm_log_file = out_dir + "/uniq_pep.hmm.log"

    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, uniq_pep_hmm_out_file, uniq_pep_hmm_log_file, hmm_file, uniq_pep_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)

    backbone_hmm_out_file = out_dir + "/backbone.hmm.tbl"
    backbone_hmm_log_file = out_dir + "/backbone.hmm.log"

    cmd_string = '%s -E 1e-20 --cpu %d --noali --tblout %s -o %s %s %s >/dev/null' % (
        hmmsearch_path, num_threads, backbone_hmm_out_file, backbone_hmm_log_file, hmm_file, seq_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)

    backbone_score_dict = read_hmm_out_get_subject_id_score_dict(
        backbone_hmm_out_file)
    uniq_pep_score_dict = read_hmm_out_get_subject_id_score_dict(
        uniq_pep_hmm_out_file)

    backbone_score = [backbone_score_dict[i] for i in backbone_score_dict]

    avg_backbone_score = sum(backbone_score)/len(backbone_score)
    std_backbone_score = np.std(np.array(backbone_score))

    ##
    uniq_pep_aln_file = out_dir + "/uniq_pep.aln"
    cmd_string = "mafft --anysymbol --add %s %s > %s" % (
        uniq_pep_file, aln_file, uniq_pep_aln_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)

    uniq_pep_trim_aln_file = out_dir + "/uniq_pep.trim.aln"
    cmd_string = "%s -in %s -out %s -gt 0.1 >/dev/null" % (
        trimal_path, uniq_pep_aln_file, uniq_pep_trim_aln_file)
    cmd_run(cmd_string, silence=True, cwd=out_dir)

    aln_seq_dict = read_fasta_by_faidx(uniq_pep_trim_aln_file)

    if aln_seq_dict[list(aln_seq_dict.keys())[0]].len() == 0:
        if clean_up:
            clean_assembly_dir(out_dir)
        return None

    stat_dict = {}
    for seq_id in aln_seq_dict:
        aln_seq = aln_seq_dict[seq_id].seq
        aln_cov = len(aln_seq.replace("-", ""))/len(aln_seq)
        stat_dict[seq_id] = (len(aln_seq.replace("-", "")),
                             len(aln_seq), aln_cov)

    backbone_len = [stat_dict[i][0]
                    for i in stat_dict if i not in uniq_id_list]
    backbone_cov = [stat_dict[i][2]
                    for i in stat_dict if i not in uniq_id_list]

    avg_backbone_len = sum(backbone_len)/len(backbone_len)
    std_backbone_len = np.std(np.array(backbone_len))

    avg_backbone_cov = sum(backbone_cov)/len(backbone_cov)
    std_backbone_cov = np.std(np.array(backbone_cov))

    results_dir = out_dir + "/results_dir"
    mkdir(results_dir, True)

    with open(results_dir+"/pep.fa", 'w') as f:
        for i in uniq_id_list:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['pep']))

    with open(results_dir+"/cDNA.fa", 'w') as f:
        for i in uniq_id_list:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['cdna']))

    with open(results_dir+"/cds.fa", 'w') as f:
        for i in uniq_id_list:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['cds']))

    with open(results_dir+"/stats.txt", 'w') as f:
        col_list = ["seq_id", "cov", "avg_cov",
                    "sd_cov", "len", "avg_len", "sd_len", "score", "avg_score", "sd_score"]
        f.write("\t".join(col_list)+"\n")

        uniq_id_list = [i for i in uniq_id_list if i in uniq_pep_score_dict]
        sorted_uniq_id_list = sorted(
            uniq_id_list, key=lambda x: uniq_pep_score_dict[x], reverse=True)

        for i in sorted_uniq_id_list:
            write_list = [i, "%.2f" % stat_dict[i][2], "%.2f" % avg_backbone_cov, "%.2f" % std_backbone_cov,
                          "%.2f" % stat_dict[i][0], "%.2f" % avg_backbone_len, "%.2f" % std_backbone_len,
                          "%.2f" % uniq_pep_score_dict[i], "%.2f" % avg_backbone_score, "%.2f" % std_backbone_score, ]
            f.write("\t".join(write_list)+"\n")

    if clean_up:
        for i in os.listdir(out_dir):
            if i != 'results_dir':
                rmdir(out_dir+"/"+i)

        move_file(results_dir+"/pep.fa", out_dir+"/pep.fa")
        move_file(results_dir+"/cDNA.fa", out_dir+"/cDNA.fa")
        move_file(results_dir+"/cds.fa", out_dir+"/cds.fa")
        move_file(results_dir+"/stats.txt", out_dir+"/stats.txt")

        rmdir(results_dir)


def targeted_gene_family_assembly(args):
    args.output_dir = os.path.abspath(args.output_dir)
    mkdir(args.output_dir, True)

    # copy_input_file
    input_fasta = args.output_dir+"/"+get_file_name(args.input_fasta)
    if not os.path.exists(input_fasta):
        os.symlink(os.path.abspath(args.input_fasta), input_fasta)

    # transdecoder
    longest_orfs_pep_file = input_fasta + \
        ".transdecoder_dir/longest_orfs.pep"
    longest_orfs_cds_file = input_fasta + \
        ".transdecoder_dir/longest_orfs.cds"

    if not (os.path.exists(longest_orfs_pep_file) and os.path.getsize(longest_orfs_pep_file)):
        cmd_string = '%s -t %s >/dev/null' % (transdecoder_path, input_fasta)
        cmd_run(cmd_string, silence=True, cwd=args.output_dir)

    # read plant_tribes_scaffold_dir
    orthofinder_id_file = plant_tribes_scaffold_dir + "/data/" + \
        plant_tribes_default_scaffold + "/annot/orthofinder.id"
    scaffold_hmms_dir = plant_tribes_scaffold_dir + "/data/" + \
        plant_tribes_default_scaffold + "/hmms/orthofinder"
    scaffold_seqs_dir = plant_tribes_scaffold_dir + "/data/" + \
        plant_tribes_default_scaffold + "/fasta/orthofinder"
    scaffold_alns_dir = plant_tribes_scaffold_dir + "/data/" + \
        plant_tribes_default_scaffold + "/alns/orthofinder"

    og_id_list = read_list_file(orthofinder_id_file, ignore_head=1)

    # family_assembly
    family_assembly_dir = args.output_dir + "/assembly_dir"
    mkdir(family_assembly_dir, True)

    args_list = []
    args_id_list = []
    for og_id in og_id_list:
        hmm_file = "%s/%s.hmm" % (scaffold_hmms_dir, og_id)
        aln_file = "%s/%s.aln" % (scaffold_alns_dir, og_id)
        seq_file = "%s/%s.faa" % (scaffold_seqs_dir, og_id)
        out_dir = "%s/%s" % (family_assembly_dir, og_id)
        out_reads_prefix = "planttribes_%s_" % og_id
        args_list.append((input_fasta, longest_orfs_pep_file, hmm_file,
                          aln_file, seq_file, out_dir, out_reads_prefix, True))

    multiprocess_running(one_family_assembly, args_list,
                         args.thread_number, silence=False, args_id_list=args_id_list)

    # get stats
    args_list = []
    args_id_list = []
    for og_id in og_id_list:

        stats_file = "%s/%s/stats.txt" % (family_assembly_dir, og_id)

        args_list.append((stats_file,))
        args_id_list.append(og_id)

    mlt_dict = multiprocess_running(
        get_pass_seq_id, args_list, args.thread_number, args_id_list=args_id_list)

    pass_seq_dict = {}
    for og_id in mlt_dict:
        pass_seq_dict[og_id] = mlt_dict[og_id]['output']

    good_og_num = 0
    bad_og_num = 0
    for i in pass_seq_dict:
        if len(pass_seq_dict[i]) > 0:
            good_og_num += 1
        else:
            bad_og_num += 1

    print("There are %d orthogroups, %d can get good assemblies, %d failed" %
          (good_og_num + bad_og_num, good_og_num, bad_og_num))

    # get Non-redundant sequence
    nr_dict = args.output_dir + "/non_redundant"
    mkdir(nr_dict, True)

    longest_orfs_pep_dict = read_fasta_by_faidx(longest_orfs_pep_file)
    longest_orfs_cds_dict = read_fasta_by_faidx(longest_orfs_cds_file)
    input_seq_dict = read_fasta_by_faidx(input_fasta)

    all_in_one_pep_file = nr_dict + "/all_in_one.faa"

    ass_big_pt_dict = {}
    ass_big_cds_dict = {}
    ass_big_cdna_dict = {}

    with open(all_in_one_pep_file, 'w') as f:
        for seq_id in longest_orfs_pep_dict:
            f.write(">%s\n%s\n" % (seq_id, longest_orfs_pep_dict[seq_id].seq))

        num = 0
        for og_id in og_id_list:
            num += 1
            if num % 1000 == 0:
                print(num)
            pep_file = "%s/%s/pep.fa" % (family_assembly_dir, og_id)
            cdna_file = "%s/%s/cDNA.fa" % (family_assembly_dir, og_id)
            cds_file = "%s/%s/cds.fa" % (family_assembly_dir, og_id)
            if os.path.exists(pep_file):
                pep_dict, seqname_list = read_fasta(pep_file)
                for seq_id in pep_dict:
                    f.write(">%s\n%s\n" % (seq_id, pep_dict[seq_id].seq))

                cdna_dict, seqname_list = read_fasta(cdna_file)
                cds_dict, seqname_list = read_fasta(cds_file)

                ass_big_pt_dict = merge_dict(
                    [ass_big_pt_dict, pep_dict], False)
                ass_big_cds_dict = merge_dict(
                    [ass_big_cds_dict, cds_dict], False)
                ass_big_cdna_dict = merge_dict(
                    [ass_big_cdna_dict, cdna_dict], False)

    cd_hit_out = nr_dict + "/cd_hit_out.100.pep"
    cmd_string = '%s/cd-hit -i %s -o %s -c 1.0 -n 5 -M 16000 -d 0 -T 8 >/dev/null' % (
        cd_hit_dir_path, all_in_one_pep_file, cd_hit_out)
    cmd_run(cmd_string, silence=True, cwd=nr_dict)

    # get output
    cd_hit_seq_dict = read_fasta_by_faidx(cd_hit_out)

    candi_seq_dict = {}
    num = 0
    for seq_id in cd_hit_seq_dict:
        if 'planttribes' in seq_id:
            cds_seq = ass_big_cds_dict[seq_id].seq
            pep_seq = ass_big_pt_dict[seq_id].seq
            cdna_seq = ass_big_cdna_dict[seq_id].seq

            if len(cds_seq)/len(pep_seq) != 3.0:
                continue

        else:
            seq_record = longest_orfs_pep_dict[seq_id]

            parent_id, sub_id, strand = re.findall(
                r'(.*)(\.p\d+).*\((\S+)\)$', seq_record.seqname)[0]
            cdna_seq = input_seq_dict[parent_id].seq if strand == '+' else reverse_complement(
                input_seq_dict[parent_id].seq)

            pep_seq = longest_orfs_pep_dict[seq_id].seq
            cds_seq = longest_orfs_cds_dict[seq_id].seq
            if pep_seq[-1] == '*':
                pep_seq = pep_seq[:-1]
                cds_seq = cds_seq[:-3]

            if len(cds_seq)/len(pep_seq) != 3.0:
                continue

        candi_seq_dict["Uniq_" + str(num)] = {
            'pep': pep_seq,
            'cdna': cdna_seq,
            'cds': cds_seq,
        }

        num += 1

    with open(args.output_dir+"/pep.fa", 'w') as f:
        for i in candi_seq_dict:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['pep']))

    with open(args.output_dir+"/cDNA.fa", 'w') as f:
        for i in candi_seq_dict:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['cdna']))

    with open(args.output_dir+"/cds.fa", 'w') as f:
        for i in candi_seq_dict:
            f.write(">%s\n%s\n" % (i, candi_seq_dict[i]['cds']))


def GetDeepAssemblyStats_main(args):
    orthofinder_id_file = plant_tribes_scaffold_dir + "/data/" + \
        plant_tribes_default_scaffold + "/annot/orthofinder.id"
    family_assembly_dir = args.family_dir

    og_id_list = read_list_file(orthofinder_id_file, ignore_head=1)

    # get stats
    args_list = []
    args_id_list = []
    for og_id in og_id_list:

        stats_file = "%s/%s/stats.txt" % (family_assembly_dir, og_id)

        args_list.append((stats_file,))
        args_id_list.append(og_id)

    mlt_dict = multiprocess_running(
        get_pass_seq_id, args_list, args.thread_number, args_id_list=args_id_list)

    pass_seq_dict = {}
    for og_id in mlt_dict:
        pass_seq_dict[og_id] = mlt_dict[og_id]['output']

    good_og_num = 0
    bad_og_num = 0
    for i in pass_seq_dict:
        if len(pass_seq_dict[i]) > 0:
            good_og_num += 1
        else:
            bad_og_num += 1

    print("There are %d orthogroups, %d can get good assemblies, %d failed" %
          (good_og_num + bad_og_num, good_og_num, bad_og_num))


def MapGenomeToOrthoGroups_main():
    pass


if __name__ == '__main__':
    from toolbiox.lib.common.evolution.orthotools2 import read_species_info, OrthoGroups

    species_info_file = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/Oro_ref.xlsx"
    orthogroups_file = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/tree/orthologous_OGs.tsv"
    num_threads = 56

    # read orthogroups
    orthogroups = OrthoGroups(OG_tsv_file=orthogroups_file)

    og_list = []
    for i in orthogroups.OG_id_list[18000:20000]:
        og_list.append(orthogroups.OG_dict[i])

    orthogroups = OrthoGroups(from_OG_list=og_list)

    # read file of files
    species_info_dict = read_species_info(species_info_file)

    # build scaffold dir
    scaffold_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu/test2"
    build_scaffold_dir(orthogroups, species_info_dict,
                       scaffold_dir, num_threads)

    # classify a sequence
    from toolbiox.lib.common.genome.seq_base import BioSeq
    protein_seq = BioSeq("MGQCYGKTIPTGDNDGPATTITTIAAAAEDLPEQTPPRNGTPSVKNTPARSSANSPWPSPYPSAAGTPAGVSPSTARSTPRRFFKKPFPPPSPAKHIRASLRKLGQRKKPPREGPIPEDADAGESEQQQQHALDKNFGYNKNFGAKYELGKEVGRGHFGHTCCAKGRKGELKDIPLAVKIISKAQFEKRTGHHECDSDLDMSDVKLIKDHKSEEDFRLLDPNLIDIFRFGYLQSYETGSYLIKAMVFMMTTAISIEDVRREVKILKALSGHRHLASFYDACEDSNNVYIIMELCEGGELLDRILAKGGKYSEDEAKLIIVQILSVVSFCHLQGVVHRDLKPENFLFTSRSEDADLKLIDFGLSDFIRTVGCLSLCIISHVLILSDERLNDIVGSAYYVAPEVLHRSYSVEADIWSIGVIAYILLCGSRPFWARTESGIFRAVLRADPNFEDLPWPSVSLEAKDFVRRLLNKDYRKRMTAAQALTHPWLRSESHPIPLDILVYKLVKSYLHATPFKRAALKALSKALTEDELIYLRAQFMLLEPSEDGRVSLENFRKISGSSHLALSLRNNILLPNTLELCDFQLLFANTAGLLHFSIFQALARNATDALNMSRVPDILNSMAPLSFRRMDLEEFCAAAISTYQLEALENWEQIASTAFEFFEQEGNRAISVEELARELNVGPSAHPMLRDWLRRDGKLSLVGYTKFLHGLTLRSSNMRHH", seqname="T4170N0C00004G00375")
    scaffold_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu/test2"
    work_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/gene_loss/gene_loss/Ocu/test2/test"
    clean_up = True

    # improve trinity assembly
    class abc():
        pass

    args = abc()

    args.input_fasta = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/database/1kp/ERS1829209/ERS1829209.fasta"
    args.output_dir = "/lustre/home/xuyuxing/Work/Orobanchaceae/HGT/database/1kp/ERS1829209/AssemblyPostProcessor"
    args.thread_number = 56

    targeted_gene_family_assembly(args)
