from toolbiox.api.xuyuxing.genome.repeat_anno import get_aa_seq
from toolbiox.lib.common.os import cmd_run, get_file_dir, mkdir, multiprocess_running, rmdir
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.src.xuyuxing.tools.seqtools import split_fasta
import os
import re
from toolbiox.lib.xuyuxing.base.base_function import merge_file

def ProteinByPfam_main(args):
    """
    class abc():
        pass

    args = abc()
    args.genome_seq_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Lindenbergia_luchunensis/repeat_by_EDTA/test/test/LTR.Copia.fasta.cd_hit'
    args.pfam_db_file = '/lustre/home/xuyuxing/Database/Pfam/20200516/Pfam-A.hmm'
    args.output_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Lindenbergia_luchunensis/repeat_by_EDTA/test/test/LTR.Copia.fasta.cd_hit.2'
    args.tmp_work_dir = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Lindenbergia_luchunensis/repeat_by_EDTA/test/test/tmp2'
    args.clean_flag = False
    args.threads = 56
    """

    # mkdir
    if args.tmp_work_dir is None:
        args.tmp_work_dir = get_file_dir(args.genome_seq_file) + "/tmp"
    
    mkdir(args.tmp_work_dir, True)

    rename_input_fasta = args.tmp_work_dir + "/input.fasta"
    rename_dict = {}
    
    with open(rename_input_fasta, 'w') as f:
        num = 0
        seq_dict = read_fasta_by_faidx(args.genome_seq_file)
        for i in seq_dict:
            num += 1
            new_seq_id = 'seq' + str(num)
            rename_dict[new_seq_id] = i
            f.write(">%s\n%s\n" % (new_seq_id, seq_dict[i].seq))
        
    
    # input
    if args.output_file is None:
        args.output_file = args.genome_seq_file + ".pfam.aa"

    # output
    transeq_output = rename_input_fasta + ".transeq"
    hmmscan_output = rename_input_fasta + ".hmmscan"

    transeq_cmd_string = 'transeq -frame 6 -sequence %s -outseq %s' % (rename_input_fasta, transeq_output)
    cmd_run(transeq_cmd_string)

    if args.threads <= 1:
        hmmscan_cmd_string = 'hmmscan --cpu 8 --domtblout %s %s %s' % (hmmscan_output, args.pfam_db_file, transeq_output)
        cmd_run(hmmscan_cmd_string)
    else:
        split_dir = args.tmp_work_dir + "/split"
        mkdir(split_dir, True)

        split_fasta(transeq_output, split_dir, 'split', contig_model=False, unit_num=6, file_size=None)

        args_list = []
        hmmscan_file_list = []
        for i in os.listdir(split_dir):
            if re.match('^split.*\.fa$', i):
                transeq_split_file = split_dir+"/"+i
                hmmscan_split_output = split_dir+"/"+i+".hmmscan"
                hmmscan_cmd_string = 'hmmscan --domtblout %s %s %s' % (hmmscan_split_output, args.pfam_db_file, transeq_split_file)
                args_list.append((hmmscan_cmd_string, None, 1, True))
                hmmscan_file_list.append(hmmscan_split_output)
        
        multiprocess_running(cmd_run, args_list, args.threads, silence=False)

        merge_file(hmmscan_file_list, hmmscan_output)

    output_dir = get_aa_seq(rename_input_fasta , transeq_output, hmmscan_output)

    for i in output_dir:
        strand = sorted(output_dir[i], key=lambda x:len(output_dir[i][x]), reverse=True)[0]
        output_dir[i] = output_dir[i][strand]

    with open(args.output_file, 'w') as f:
        for seq_id in output_dir:
            if len(output_dir[seq_id]) > 0:
                f.write(">%s\n%s\n" % (rename_dict[seq_id], output_dir[seq_id]))

    if args.clean_flag:
        rmdir(args.tmp_work_dir)
