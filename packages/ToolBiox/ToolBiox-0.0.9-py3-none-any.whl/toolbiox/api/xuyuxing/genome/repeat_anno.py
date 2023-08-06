import re
from collections import OrderedDict
from toolbiox.lib.common.os import cmd_run
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.math.interval import merge_intervals, interval_minus_set
from interlap import InterLap


def hmmscan_output_reader(hmmscan_output):
    """http://eddylab.org/software/hmmer/Userguide.pdf"""
    col_name = [
        "target_name", "target_accession", "target_len", "query_name", "query_accession", 'query_len',
        "full_seq_e_value", "full_seq_score", "full_seq_bias", "domain_rank", "total_domain",
        "c_Evalue", "i_Evalue", "domain_score", "domain_bias", "hmm_from", "hmm_to", "ali_from", "ali_to",
        "env_from", "env_to", "acc", "target_description"
    ]

    output_dir = OrderedDict()
    num = 0
    with open(hmmscan_output, 'r') as f:
        for each_line in f:
            if re.match(r'^#', each_line):
                continue
            each_line = re.sub('\n', '', each_line)
            info = each_line.split()
            output_dir["ID_" + str(num)] = {}
            for i in range(0, len(col_name)):
                output_dir["ID_" + str(num)][col_name[i]] = info[i]
            num = num + 1

    return output_dir


def seq_split_by_star(sequence):
    range_list = []
    start = 0
    end = 0
    for i in range(0, len(sequence)):
        if sequence[i] == '*':
            end = i - 1
            if i == start:
                start = i + 1
                continue
            range_list.append((start, end))
            start = i + 1
            end = i + 1
        if sequence[i] != '*' and i == len(sequence) - 1:
            range_list.append((start, i))

    output_list = []
    for i in range_list:
        output_list.append((i[0] + 1, i[1] + 1))

    return output_list


def get_aa_seq(genome_seq_file, transeq_output, hmmscan_output):
    transeq_dict = read_fasta_by_faidx(transeq_output)
    hmmscan_dict = hmmscan_output_reader(hmmscan_output)

    split_star_dict = {}
    for seq_name in transeq_dict:
        split_star_dict[seq_name] = InterLap()
        split_star_dict[seq_name].update(seq_split_by_star(str(transeq_dict[seq_name].seq)))

    output_dir = {}
    for seq_name in read_fasta_by_faidx(genome_seq_file):
        seq_trans = {
            "+": [seq_name + "_1", seq_name + "_2", seq_name + "_3"],
            "-": [seq_name + "_4", seq_name + "_5", seq_name + "_6"]
        }

        seq_trans_hmm = {"+": [],
                         "-": []}

        for i in hmmscan_dict:
            q_name = hmmscan_dict[i]['query_name']
            if q_name in seq_trans['+']:
                seq_trans_hmm["+"].append((int(hmmscan_dict[i]['env_from']), int(hmmscan_dict[i]['env_to']), q_name))
            if q_name in seq_trans['-']:
                seq_trans_hmm["-"].append((int(hmmscan_dict[i]['env_from']), int(hmmscan_dict[i]['env_to']), q_name))

        output_seq = {}
        for strand in ["+", "-"]:
            used_list = []
            for start, end, info in seq_trans_hmm[strand]:
                range_tmp = (start, end)
                get_range_list = interval_minus_set(range_tmp, merge_intervals([(i, j) for i, j, k in used_list], True))
                for i in get_range_list:
                    used_list.append((i[0], i[1], info))

            expand_list = []
            for s, e, q_name in used_list:
                expand_list.append((list(split_star_dict[q_name].find((s, e))), q_name))

            # add expand
            for expand_list_now, q_name in expand_list:
                for range_tmp in expand_list_now:
                    get_range_list = interval_minus_set(range_tmp,
                                                        merge_intervals([(i, j) for i, j, k in used_list], True))
                    for i in get_range_list:
                        used_list.append((i[0], i[1], q_name))

            # print(used_list)

            seq = ""
            for i in sorted(used_list, key=lambda x: x[0]):
                seq = seq + str(transeq_dict[i[2]].seq)[i[0] - 1:i[1]]

            seq = re.sub('\*', '', seq)
            output_seq[strand] = seq

        output_dir[seq_name] = output_seq

    return output_dir

#
# # input
# genome_seq_file = '/lustre/home/xuyuxing/Work/Cuscuta_HGT/HGT_Nt/parse/reblast/OneStep/Cau/tmp/supergroup_gap200_len900_cover0.5/SG_4/tmp/SG_4_R_84.fa'
# pfam_db_file = '/lustre/home/xuyuxing/Database/Interpro/interproscan-5.39-77.0/data/pfam/32.0/pfam_a.hmm'
# output_file = '/lustre/home/xuyuxing/Work/Cuscuta_HGT/HGT_Nt/parse/reblast/OneStep/Cau/tmp/supergroup_gap200_len900_cover0.5/SG_4/tmp/SG_4_R_84.pfam.aa'
#
# # output
# transeq_output = genome_seq_file + ".transeq"
# hmmscan_output = transeq_output + ".hmmscan"
#
# transeq_cmd_string = 'transeq -frame 6 -sequence %s -outseq %s' % (genome_seq_file, transeq_output)
# cmd_run(transeq_cmd_string)
#
# hmmscan_cmd_string = 'hmmscan --domtblout %s %s %s' % (hmmscan_output, pfam_db_file, transeq_output)
# cmd_run(hmmscan_cmd_string)
#
# output_dir = get_aa_seq(genome_seq_file, transeq_output, hmmscan_output)
#
# with open(output_file, 'w') as f:
#     for seq in output_dir:
#         for strand in output_dir[seq]:
#             if not output_dir[seq][strand] == "":
#                 if strand == "+":
#                     f.write(">%s_p\n%s\n" % (seq, output_dir[seq][strand]))
#                 elif strand == "-":
#                     f.write(">%s_n\n%s\n" % (seq, output_dir[seq][strand]))
