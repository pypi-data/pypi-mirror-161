import os
import numpy as np
from toolbiox.lib.common.fileIO import tsv_file_dict_parse_big, read_matrix_file
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.api.common.genome.blast import outfmt6_read_big, hit_CIP, hit_CALP
from toolbiox.lib.common.os import cmd_run, mkdir, rmdir
from toolbiox.api.xuyuxing.transcriptome.FPKM import get_TPM_matrix, get_FPKM_matrix


def hit_sum_hsp_aln(hit):
    aln_list = []
    for hsp in hit.hsp:
        aln_list.append(hsp.Hsp_align_len)
    return sum(aln_list)


def Denovo2RefCountMap_main(args):

    args.work_dir = os.path.abspath(args.work_dir)

    # build env
    mkdir(args.work_dir, False)

    gene_model_cds_file = args.work_dir + "/gene_model_cds.fna"
    tran_seq_file = args.work_dir + "/trans.fna"
    gene_trans_map_file = args.work_dir + "/gene_trans_map"
    os.symlink(os.path.abspath(args.gene_model_cds_file), gene_model_cds_file)
    os.symlink(os.path.abspath(args.tran_fasta_file), tran_seq_file)
    os.symlink(os.path.abspath(args.gene_trans_map), gene_trans_map_file)

    if args.tran_count_fof:
        tran_count_fof = args.work_dir + "/trans.counts.fof"
        os.symlink(os.path.abspath(args.tran_count_fof), tran_count_fof)
    else:
        tran_count_fof = None

    if args.tran_count_matrix:
        tran_count_matrix = args.work_dir + "/tran_count_matrix"
        os.symlink(os.path.abspath(args.tran_count_matrix), tran_count_matrix)
    else:
        tran_count_matrix = None

    # blast
    cmd_string = "makeblastdb -in %s -dbtype nucl" % gene_model_cds_file
    cmd_run(cmd_string, cwd=args.work_dir)

    bls_out_file = args.work_dir + "/trans_vs_cds.bls"
    cmd_string = "blastn -query %s -db %s -out %s -outfmt 6 -evalue 1e-5 -max_target_seqs 10 -num_threads %d" % (
        tran_seq_file, gene_model_cds_file, bls_out_file, args.threads)
    cmd_run(cmd_string, cwd=args.work_dir)

    # id map
    seq_dict = read_fasta_by_faidx(tran_seq_file)
    len_dict = {i: seq_dict[i].len() for i in seq_dict}

    all_tg2tt_dict = {}
    for tmp_id, tmp_dict in tsv_file_dict_parse_big(gene_trans_map_file, fieldnames=['tg', 'tt'], key_col='tt'):
        tg = tmp_dict['tg']
        all_tg2tt_dict.setdefault(tg, []).append(tmp_dict['tt'])

    tg2tt_dict = {}
    for tg in all_tg2tt_dict:
        tg2tt_dict[tg] = sorted(
            all_tg2tt_dict[tg], key=lambda x: len_dict[x], reverse=True)[0]

    tt2tg_dict = {tg2tt_dict[tg]: tg for tg in tg2tt_dict}

    # read blast
    t2g_dict = {}
    for query in outfmt6_read_big(bls_out_file):
        if query.qID not in tt2tg_dict:
            continue

        q_id = tt2tg_dict[query.qID]

        t2g_dict[q_id] = []
        query.qLen = len_dict[query.qID]
        for hit in query.hit:
            cip = hit_CIP(hit)
            calp = hit_CALP(hit)
            sum_aln = hit_sum_hsp_aln(hit)

            if cip > 0.6 and calp > 0.5 and sum_aln > 50:
                t2g_dict[q_id].append((hit.Hit_id, (cip * calp * sum_aln)))

        if len(t2g_dict[q_id]) != 0:
            t2g_dict[q_id] = sorted(
                t2g_dict[q_id], key=lambda x: x[1], reverse=True)[0][0]
        else:
            del t2g_dict[q_id]

    g2t_dict = {}
    for t in t2g_dict:
        g = t2g_dict[t]
        if g not in g2t_dict:
            g2t_dict[g] = []
        g2t_dict[g].append(t)

    # read tran count
    if tran_count_fof:
        rsem_file_dict = {}
        sample_list = []
        with open(tran_count_fof, 'r') as f:
            for l in f:
                l.strip()
                s, r_file = l.split()
                rsem_file_dict[s] = r_file
                sample_list.append(s)

        tran_count_dict = {}
        for s in rsem_file_dict:
            r_file = rsem_file_dict[s]
            for tmp_id, tmp_dict in tsv_file_dict_parse_big(r_file, key_col='gene_id'):
                tran_count_dict.setdefault(
                    tmp_id, {sd: 0 for sd in sample_list})
                tran_count_dict[tmp_id][s] = round(
                    float(tmp_dict['expected_count']))

    elif tran_count_matrix:
        ttran_count_dict = {}
        for tmp_id, tmp_dict in tsv_file_dict_parse_big(tran_count_matrix, key_col=''):
            sample_list = sorted([i for i in tmp_dict if i != ''])
            ttran_count_dict[tmp_id] = {
                s: round(float(tmp_dict[s])) for s in sample_list}

        tran_count_dict = {}
        for tg in all_tg2tt_dict:
            tran_count_dict[tg] = {s: 0 for s in sample_list}
            for tt in all_tg2tt_dict[tg]:
                if tt in ttran_count_dict:
                    for s in ttran_count_dict[tt]:
                        tran_count_dict[tg][s] += ttran_count_dict[tt][s]

    # map count to gene
    gene_count_dict = {}
    for g in g2t_dict:
        gene_count_dict[g] = {i: 0 for i in sample_list}
        for t in g2t_dict[g]:
            sample_count_dict = tran_count_dict[t]
            for s in sample_count_dict:
                gene_count_dict[g][s] += tran_count_dict[t][s]

    # output
    with open(args.output_prefix+".counts.matrix", 'w') as f:
        f.write("Gene\t" + "\t".join(sample_list) + "\n")

        for g in gene_count_dict:
            c_list = []
            for s in sample_list:
                c = gene_count_dict[g][s]
                c_list.append(str(c))
            "\t".join(c_list)

            f.write(g + "\t" + "\t".join(c_list) + "\n")

    # get TPM
    gene_list = sorted(list(gene_count_dict.keys()))
    count_matrix = []
    for g in gene_list:
        g_r = []
        for s in sample_list:
            g_r.append(gene_count_dict[g][s])
        count_matrix.append(g_r)
    count_matrix = np.array(count_matrix)

    seq_dict = read_fasta_by_faidx(gene_model_cds_file)
    cds_len_list = [seq_dict[i].len() for i in gene_list]

    tpm_matrix = get_TPM_matrix(count_matrix, cds_len_list)

    # output
    with open(args.output_prefix+".tpm.matrix", 'w') as f:
        f.write("Gene\t" + "\t".join(sample_list) + "\n")

        for g in range(len(gene_list)):
            c_list = []
            for s in range(len(sample_list)):
                c = tpm_matrix[g][s]
                c_list.append(str(c))
            "\t".join(c_list)

            g_id = gene_list[g]
            f.write(g_id + "\t" + "\t".join(c_list) + "\n")

    # get FPKM
    fpkm_matrix = get_FPKM_matrix(count_matrix, cds_len_list)

    # output
    with open(args.output_prefix+".fpkm.matrix", 'w') as f:
        f.write("Gene\t" + "\t".join(sample_list) + "\n")

        for g in range(len(gene_list)):
            c_list = []
            for s in range(len(sample_list)):
                c = fpkm_matrix[g][s]
                c_list.append(str(c))
            "\t".join(c_list)

            g_id = gene_list[g]
            f.write(g_id + "\t" + "\t".join(c_list) + "\n")


def Count2TMM_main(args):
    count_matrix, sample_list, gene_list = read_matrix_file(args.count_matrix)

    gene_length_dict = {}
    with open(args.gene_length_file, 'r') as f:
        for i in f:
            i.strip()
            g_id,length = i.split()
            gene_length_dict[g_id] = float(length)

    gene_length_list = [gene_length_dict[i] for i in gene_list]

    fpkm = get_FPKM_matrix(count_matrix, gene_length_list)
    tpm = get_TPM_matrix(count_matrix, gene_length_list)

    # output
    with open(args.output_prefix+".fpkm.matrix", 'w') as f:
        f.write("Gene\t" + "\t".join(sample_list) + "\n")

        for g in range(len(gene_list)):
            c_list = []
            for s in range(len(sample_list)):
                c = fpkm[g][s]
                c_list.append(str(c))
            "\t".join(c_list)

            g_id = gene_list[g]
            f.write(g_id + "\t" + "\t".join(c_list) + "\n")

    # output
    with open(args.output_prefix+".tpm.matrix", 'w') as f:
        f.write("Gene\t" + "\t".join(sample_list) + "\n")

        for g in range(len(gene_list)):
            c_list = []
            for s in range(len(sample_list)):
                c = tpm[g][s]
                c_list.append(str(c))
            "\t".join(c_list)

            g_id = gene_list[g]
            f.write(g_id + "\t" + "\t".join(c_list) + "\n")
                        
    tpm_file = args.output_prefix+".tpm.matrix"
    tmm_file = args.output_prefix+".TMM.matrix"

    cmd_string = "run_TMM_scale_matrix.pl --matrix %s > %s" % (tpm_file, tmm_file)
    cmd_run(cmd_string)

if __name__ == "__main__":

    class abc():
        pass

    args = abc()

    args.gene_model_cds_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Striga_asiatica/T4170N0.gene_model.cds.fasta'
    args.tran_count_fof = None
    args.tran_count_matrix = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Sas/transcript.counts.matrix'
    args.tran_fasta_file = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Sas/Trinity.fasta'
    args.gene_trans_map = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Sas/Trinity.fasta.gene_trans_map'
    args.work_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Sas/tmp'
    args.output_prefix = '/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Sas/Gene'
    args.threads = 56
