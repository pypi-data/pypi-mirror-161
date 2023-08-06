import os
import re
import pickle
from pyfaidx import Fasta
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init, configure_parser
from toolbiox.lib.common.os import mkdir, copy_file, cmd_run, multiprocess_running
from toolbiox.src.xuyuxing.tools.seqtools import split_fasta
from toolbiox.lib.common.genome.seq_base import read_fasta
from argparse import Namespace
from toolbiox.api.xuyuxing.genome.annotation_shell_code import *
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
from toolbiox.api.xuyuxing.resource.dfam import build_TE_class_tree
from toolbiox.api.xuyuxing.resource.dfam import dfam_TE_classes_file as defaults_dfam_file
from toolbiox.lib.common.evolution.tree_operate import lookup_by_names


class Maker_P_Job(object):
    def __init__(self, genome_fasta_file, output_dir, config_file=None, tag='Genome', num_threads=56):
        # parse argument

        args = Namespace(genome=genome_fasta_file, output_dir=output_dir,
                         config_file=config_file, tag=tag, num_threads=num_threads)

        try:
            script_dir_path = os.path.split(os.path.realpath(__file__))[0]
            defaults_config_file = script_dir_path + \
                "/lib/config_file/Maker_p_defaults.ini"
        except:
            defaults_config_file = "/lustre/home/xuyuxing/python_project/Genome_work_tools/lib/config_file/Maker_p_defaults.ini"

        args_type = {
            # Parameter
            "num_threads": "int",
            "tag": "str",

            # Paths
            "genome": "str",
            "trna_file": "str",
            "crl_dir": "str",
            "tpase_dir": "str",
            "pe_dir": "str",
            "old_blastx": "str",
            "protein_db": "str"
        }

        args = configure_parser(
            args, defaults_config_file, args.config_file, args_type, None)
        self.args = args

        # running maker p
        self.maker_p_repeat_main()

    def step_1_3(sh_file, trna_file, crl_dir):
        with open(sh_file, 'w') as f:
            f.write(step_1_3_shell % (trna_file, crl_dir))

    def step_1_3_85(sh_file, trna_file, crl_dir):
        with open(sh_file, 'w') as f:
            f.write(step_1_3_85_shell % (trna_file, crl_dir))

    def step3_merge(work_dir, contig_list, out_dir, identity):
        """
        work_dir = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/repeat/LTR"
        list_file = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/repeat/LTR/list"
        out_dir = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/repeat/LTR/merge85"
        """

        identity = str(identity)

        contig_dir = {}
        num = 0
        for i in contig_list:
            contig_dir[i] = {}
            contig_dir[i]['seq-nr'] = str(num)
            contig_main_dir = work_dir + "/" + i
            if os.path.exists(contig_main_dir):
                CRL_Step3_file = contig_main_dir + "/CRL_Step3_Passed_Elements.fasta"
                result99_file = contig_main_dir + "/" + i + ".result%s" % identity
                outinner99_file = contig_main_dir + "/" + i + ".outinner%s" % identity

                if os.path.exists(CRL_Step3_file):
                    contig_dir[i]["CRL_Step3_file"] = CRL_Step3_file
                # else:
                #     print("%s miss CRL_Step3_file" % i)

                if os.path.exists(result99_file):
                    contig_dir[i]["result99_file"] = result99_file
                # else:
                #     print("%s miss result99_file" % i)

                if os.path.exists(outinner99_file):
                    contig_dir[i]["outinner99_file"] = outinner99_file
                # else:
                #     print("%s miss outinner99_file" % i)
            # else:
            #     print("%s miss main dir" % i)
            num = num + 1

        mkdir(out_dir, True)
        merge_CRL_Step3_file = out_dir + "/all.CRL_Step3_Passed_Elements.fasta"
        merge_result99 = out_dir + "/all.result%s" % identity
        merge_outinner99 = out_dir + "/all.outinner%s" % identity

        step3_f = open(merge_CRL_Step3_file, 'w')
        result99_f = open(merge_result99, 'w')
        outinner99_f = open(merge_outinner99, 'w')

        for contig in contig_dir:
            if "CRL_Step3_file" in contig_dir[contig]:
                CRL_Step3_file = contig_dir[contig]["CRL_Step3_file"]
                seqdict, seqname_list = read_fasta(CRL_Step3_file)
                for i in seqname_list:
                    new_seq_name = re.sub(
                        'dbseq-nr_0', 'dbseq-nr_%s' % contig_dir[contig]['seq-nr'], i)
                    step3_f.write('>%s\n%s\n' %
                                  (new_seq_name, seqdict[i].seq.lower()))

            if "result99_file" in contig_dir[contig]:
                result99_file = contig_dir[contig]["result99_file"]
                with open(result99_file, 'r') as f:
                    for each_line in f:
                        if re.match(r'^#', each_line):
                            continue
                        each_line = re.sub('\n', '', each_line)
                        info = each_line.split()
                        info[-1] = str(contig_dir[contig]['seq-nr'])
                        result99_f.write(printer_list(info, sep="  ") + "\n")

            if "outinner99_file" in contig_dir[contig]:
                outinner99_file = contig_dir[contig]["outinner99_file"]
                seqdict, seqname_list = read_fasta(
                    outinner99_file, full_name=True, upper=False)
                for i in seqname_list:
                    new_seq_name = re.sub(
                        'dbseq-nr 0', 'dbseq-nr %s' % contig_dir[contig]['seq-nr'], i)
                    seqdict[i].wrap(60)
                    outinner99_f.write('>%s\n%s' %
                                       (new_seq_name, seqdict[i].seq.lower()))

        step3_f.close()
        result99_f.close()
        outinner99_f.close()

    def step_4_5(sh_file, genome, trna_file, crl_dir, mite_file, tpase_dir):
        with open(sh_file, 'w') as f:
            f.write(step_4_5_shell %
                    (genome, trna_file, crl_dir, mite_file, tpase_dir))

    def step_4_5_85(sh_file, genome, trna_file, crl_dir, mite_file, tpase_dir):
        with open(sh_file, 'w') as f:
            f.write(step_4_5_85_shell %
                    (genome, trna_file, crl_dir, mite_file, tpase_dir))

    def maker_p_repeat_main(self):
        args = self.args

        mkdir(args.output_dir, True)
        log_file = args.output_dir + "/log.txt"
        args.genome = os.path.abspath(args.genome)
        args.output_dir = os.path.abspath(args.output_dir)

        logger = logging_init("maker_p repeat build", log_file)

        args_info_string = "Argument list:\n"
        attrs = vars(args)

        for item in attrs.items():
            args_info_string = args_info_string + ("%s: %s\n" % item)

        logger.info(args_info_string)

        logger.info("Step1: MITE find")

        MITE_dir = args.output_dir + "/MITE"
        MITE_pass_flag_file = MITE_dir + "/MITE.ok"

        if not os.path.exists(MITE_pass_flag_file):
            logger.info("   MITE find, begin")

            bash_file = MITE_dir + "/MITE.sh"
            mkdir(MITE_dir, True)

            with open(bash_file, 'w') as f:
                f.write(MITE_shell % (args.genome, MITE_dir, args.mite_hunter_manager,
                                      args.tag, args.num_threads, args.num_threads))

            code, output, error = cmd_run("bash %s" % bash_file, cwd=MITE_dir)

            stdout_file = MITE_dir + "/MITE.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = MITE_dir + "/MITE.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            MITE_file = MITE_dir + "/MITE.lib"

            if code and os.path.getsize(MITE_file) != 0:
                MITE_pass_flag_file = MITE_dir + "/MITE.ok"
                cmd_run("touch %s" % MITE_pass_flag_file, cwd=MITE_dir)
                logger.info("   MITE find, finished")
            else:
                logger.info("   MITE find, failed, please check")
                raise ValueError("MITE failed, please check")

        else:
            logger.info("   MITE find, already finished, skip step")
            MITE_file = MITE_dir + "/MITE.lib"

        logger.info("Step2: genome split")
        split_genome_dir = args.output_dir + "/split_genome"
        mkdir(split_genome_dir, True)

        genome_ref = Fasta(args.genome)
        contig_list = list(genome_ref.keys())
        split_ok = True
        for i in contig_list:
            contig_file = split_genome_dir + "/" + i + ".fa"
            if not (os.path.exists(contig_file) and os.path.getsize(contig_file) != 0):
                split_ok = False

        if not split_ok:
            mkdir(split_genome_dir, True)
            split_fasta(args.genome, split_genome_dir, None, True)

        logger.info("Step3: LTRs find")
        ltr_dir = args.output_dir + "/LTR"
        mkdir(ltr_dir, True)

        logger.info("Step3.1: LTRs that are 99% or more in similarity")
        ltr_99_dir = ltr_dir + "/99"
        ltr_99_log = ltr_99_dir + "/log.txt"
        mkdir(ltr_99_dir, True)
        step_1_3_sh = ltr_99_dir + "/step_1_3.sh"
        step_1_3(step_1_3_sh, args.trna_file, args.crl_dir)
        tmp_out_pickle = ltr_99_dir + "/shell_para_out.pyb"

        logger.info("   raw step 2.1.1 - 2.1.3")

        step_1_3_flag = False
        if os.path.exists(tmp_out_pickle):
            # TEMP = open(tmp_out_pickle, 'rb')
            # tmp_out = pickle.load(TEMP)
            # TEMP.close()

            crl_step_file_num = {
                'step1': [0, 0],
                'step2': [0, 0],
                'step3': [0, 0],
                'dgt': [0, 0],
                'result99': [0, 0]
            }

            for contig in contig_list:
                crl_step_file = {
                    'step1': "%s/%s/CRL_Step1_Passed_Elements.txt" % (ltr_99_dir, contig),
                    'step2': "%s/%s/fasta_files/CRL_Step2_Passed_Elements.fasta" % (ltr_99_dir, contig),
                    'step3': "%s/%s/CRL_Step3_Passed_Elements.fasta" % (ltr_99_dir, contig),
                    'dgt': "%s/%s/%s.gff99.dgt" % (ltr_99_dir, contig, contig),
                    'result99': "%s/%s/%s.result99" % (ltr_99_dir, contig, contig),
                }

                for step in list(crl_step_file.keys()):
                    if os.path.exists(crl_step_file[step]):
                        crl_step_file_num[step][0] += 1
                        if os.path.getsize(crl_step_file[step]) != 0:
                            crl_step_file_num[step][1] += 1

            if crl_step_file_num['step1'][0] == crl_step_file_num['step2'][0] == crl_step_file_num['dgt'][0] == \
                    crl_step_file_num['result99'][1] == len(contig_list):
                if crl_step_file_num['step1'][1] != 0 and crl_step_file_num['step2'][1] != 0 and crl_step_file_num['step3'][
                        1] != 0:
                    step_1_3_flag = True
                    logger.info("   raw step 1-3, already finished, skip step")

        if not step_1_3_flag:

            args_list = []
            for contig in contig_list:
                contig_fasta_file = os.path.abspath(
                    split_genome_dir + "/" + contig + ".fa")
                cmd_string = "bash %s %s %s" % (
                    step_1_3_sh, contig_fasta_file, contig)
                args_list.append((cmd_string, ltr_99_dir, 1, True, None))

            logger.info("   raw step 1-3, begin")

            tmp_out = multiprocess_running(
                cmd_run, args_list, args.num_threads, log_file=ltr_99_log)

            OUT = open(tmp_out_pickle, 'wb')
            pickle.dump(tmp_out, OUT)
            OUT.close()

            logger.info("   raw step 1-3, finished")

        logger.info(
            "   merge CRL_Step3_Passed_Elements.fasta，$TAG.result99，$TAG.outinner99")
        merge_dir = ltr_99_dir + "/merge"
        mkdir(merge_dir, True)
        step3_merge(ltr_99_dir, contig_list, merge_dir, 99)

        logger.info("   raw step 2.1.4 - 2.1.5")

        LTR99_lib_file = merge_dir + "/LTR99.lib"
        if os.path.exists(LTR99_lib_file):
            logger.info("   raw step 4-5, already finished, skip step")
        else:
            logger.info("   raw step 4-5, begin")
            step_4_5_sh = merge_dir + "/step_4_5.sh"
            step_4_5(step_4_5_sh, args.genome, args.trna_file,
                     args.crl_dir, MITE_file, args.tpase_dir)
            code, output, error = cmd_run(
                "bash %s" % step_4_5_sh, cwd=merge_dir)

            stdout_file = merge_dir + "/step_4_5.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = merge_dir + "/step_4_5.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   raw step 4-5, finished")

        logger.info("Step3.2: LTRs that are 85% or more in similarity")
        ltr_85_dir = ltr_dir + "/85"
        ltr_85_log = ltr_85_dir + "/log.txt"
        mkdir(ltr_85_dir, True)
        step_1_3_85_sh = ltr_85_dir + "/step_1_3.sh"
        step_1_3_85(step_1_3_85_sh, args.trna_file, args.crl_dir)
        tmp_out_pickle = ltr_85_dir + "/shell_para_out.pyb"

        logger.info("   raw step 2.1.1 - 2.1.3")

        step_1_3_85_flag = False
        if os.path.exists(tmp_out_pickle):
            # TEMP = open(tmp_out_pickle, 'rb')
            # tmp_out = pickle.load(TEMP)
            # TEMP.close()

            crl_step_file_num = {
                'step1': [0, 0],
                'step2': [0, 0],
                'step3': [0, 0],
                'dgt': [0, 0],
                'result85': [0, 0]
            }

            for contig in contig_list:
                crl_step_file = {
                    'step1': "%s/%s/CRL_Step1_Passed_Elements.txt" % (ltr_85_dir, contig),
                    'step2': "%s/%s/fasta_files/CRL_Step2_Passed_Elements.fasta" % (ltr_85_dir, contig),
                    'step3': "%s/%s/CRL_Step3_Passed_Elements.fasta" % (ltr_85_dir, contig),
                    'dgt': "%s/%s/%s.gff85.dgt" % (ltr_85_dir, contig, contig),
                    'result85': "%s/%s/%s.result85" % (ltr_85_dir, contig, contig),
                }

                for step in list(crl_step_file.keys()):
                    if os.path.exists(crl_step_file[step]):
                        crl_step_file_num[step][0] += 1
                        if os.path.getsize(crl_step_file[step]) != 0:
                            crl_step_file_num[step][1] += 1

            if crl_step_file_num['step1'][0] == crl_step_file_num['step2'][0] == crl_step_file_num['dgt'][0] == \
                    crl_step_file_num['result85'][1] == len(contig_list):
                if crl_step_file_num['step1'][1] != 0 and crl_step_file_num['step2'][1] != 0 and crl_step_file_num['step3'][
                        1] != 0:
                    step_1_3_85_flag = True
                    logger.info("   raw step 1-3, already finished, skip step")

        if not step_1_3_85_flag:

            args_list = []
            for contig in contig_list:
                contig_fasta_file = os.path.abspath(
                    split_genome_dir + "/" + contig + ".fa")
                cmd_string = "bash %s %s %s" % (
                    step_1_3_85_sh, contig_fasta_file, contig)
                args_list.append((cmd_string, ltr_85_dir, 1, True, None))

            logger.info("   raw step 1-3, begin")

            tmp_out = multiprocess_running(
                cmd_run, args_list, args.num_threads, log_file=ltr_85_log)

            OUT = open(tmp_out_pickle, 'wb')
            pickle.dump(tmp_out, OUT)
            OUT.close()

            logger.info("   raw step 1-3, finished")

        logger.info(
            "   merge CRL_Step3_Passed_Elements.fasta，$TAG.result85，$TAG.outinner85")
        merge_dir = ltr_85_dir + "/merge"
        mkdir(merge_dir, True)
        step3_merge(ltr_85_dir, contig_list, merge_dir, 85)

        logger.info("   raw step 2.1.4 - 2.1.5")

        LTR85_lib_file = merge_dir + "/LTR85.lib"
        if os.path.exists(LTR85_lib_file):
            logger.info("   raw step 4-5, already finished, skip step")
        else:
            logger.info("   raw step 4-5, begin")
            step_4_5_85_sh = merge_dir + "/step_4_5.sh"
            step_4_5_85(step_4_5_85_sh, args.genome, args.trna_file,
                        args.crl_dir, MITE_file, args.tpase_dir)
            code, output, error = cmd_run(
                "bash %s" % step_4_5_85_sh, cwd=merge_dir)

            stdout_file = merge_dir + "/step_4_5.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = merge_dir + "/step_4_5.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   raw step 4-5, finished")

        logger.info("Step3.3: merge 85 and 99 lib")

        allLTR_file = merge_dir + "/allLTR.lib"
        if os.path.exists(allLTR_file):
            logger.info("   already finished, skip step")
        else:
            logger.info("   begin")
            copy_file(LTR99_lib_file, merge_dir)

            bash_file = merge_dir + "/merge85_99.sh"

            with open(bash_file, 'w') as f:
                f.write(merge85_99_shell % args.crl_dir)

            code, output, error = cmd_run("bash %s" % bash_file, cwd=merge_dir)

            stdout_file = merge_dir + "/merge85_99.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = merge_dir + "/merge85_99.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            allLTR_file = merge_dir + "/allLTR.lib"

            logger.info("   finished")

        logger.info("Step4: Collecting repetitive sequences by RepeatModeler")

        repeat_dir = args.output_dir + "/Repeat"
        mkdir(repeat_dir, True)
        copy_file(allLTR_file, repeat_dir)
        copy_file(MITE_file, repeat_dir)

        cmd_run("cat allLTR.lib MITE.lib > allMITE_LTR.lib", cwd=repeat_dir)
        alllib_file = os.path.abspath(repeat_dir + "/allMITE_LTR.lib")

        logger.info("   RepeatMasker")

        tmp_out_pickle = repeat_dir + "/RepeatMasker.pyb"

        if os.path.exists(tmp_out_pickle):
            logger.info("   RepeatMasker, finished, skip step")
        else:
            bash_file = repeat_dir + "/RepeatMasker.sh"
            with open(bash_file, 'w') as f:
                f.write(RepeatMasker_shell % alllib_file)

            args_list = []
            for contig in contig_list:
                contig_fasta_file = os.path.abspath(
                    split_genome_dir + "/" + contig + ".fa")
                cmd_string = "bash %s %s %s" % (
                    bash_file, contig_fasta_file, contig)
                args_list.append((cmd_string, repeat_dir, 1, True, None))

            logger.info("   RepeatMasker, begin")

            tmp_out = multiprocess_running(
                cmd_run, args_list, args.num_threads, log_file=ltr_99_log)

            OUT = open(tmp_out_pickle, 'wb')
            pickle.dump(tmp_out, OUT)
            OUT.close()

            logger.info("   RepeatMasker, finished")

        logger.info("   RepeatModeler")

        ModelerID_lib_file = repeat_dir + "/ModelerID.lib"
        ModelerUnknown_lib_file = repeat_dir + "/ModelerUnknown.lib"

        if os.path.exists(ModelerID_lib_file):
            logger.info("   RepeatModeler, finished, skip step")
        else:
            bash_file = repeat_dir + "/RepeatModeler.sh"
            with open(bash_file, 'w') as f:
                f.write(RepeatModeler_shell % (args.crl_dir, args.tpase_dir))

            logger.info("   RepeatModeler, begin")
            code, output, error = cmd_run(
                "bash %s" % bash_file, cwd=repeat_dir)

            stdout_file = repeat_dir + "/RepeatModeler.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = repeat_dir + "/RepeatModeler.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   RepeatModeler, finished")

        logger.info("Step5: Exclusion of gene fragments")

        no_gene_dir = args.output_dir + "/NoGeneFrag"
        mkdir(no_gene_dir, True)
        allRepeats_lib_file = no_gene_dir + "/allRepeats.lib"

        if os.path.exists(allRepeats_lib_file):
            logger.info("   Step5, finished, skip step")
        else:
            copy_file(allLTR_file, no_gene_dir)
            copy_file(MITE_file, no_gene_dir)
            copy_file(ModelerUnknown_lib_file, no_gene_dir)
            copy_file(ModelerID_lib_file, no_gene_dir)

            logger.info("   Blastx, round 1")
            code, output, error = cmd_run(
                "%s -num_threads 56 -query ModelerUnknown.lib -db %s -evalue 1e-10 -num_descriptions 10 -out ModelerUnknown.lib_blast_results.txt" % (
                    args.old_blastx,
                    args.protein_db
                ), cwd=no_gene_dir)

            stdout_file = no_gene_dir + "/blastx.r1.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = no_gene_dir + "/blastx.r1.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   Blastx, round 2")
            code, output, error = cmd_run(
                "%s -num_threads 56 -query MITE.lib -db %s -evalue 1e-10 -num_descriptions 10 -out MITE.lib_blast_results.txt" % (
                    args.old_blastx,
                    args.protein_db
                ), cwd=no_gene_dir)

            stdout_file = no_gene_dir + "/blastx.r2.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = no_gene_dir + "/blastx.r2.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   Blastx, round 3")
            code, output, error = cmd_run(
                "%s -num_threads 56 -query allLTR.lib -db %s -evalue 1e-10 -num_descriptions 10 -out allLTR.lib_blast_results.txt" % (
                    args.old_blastx,
                    args.protein_db
                ), cwd=no_gene_dir)

            stdout_file = no_gene_dir + "/blastx.r3.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = no_gene_dir + "/blastx.r3.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   Blastx, round 4")
            code, output, error = cmd_run(
                "%s -num_threads 56 -query ModelerID.lib -db %s -evalue 1e-10 -num_descriptions 10 -out ModelerID.lib_blast_results.txt" % (
                    args.old_blastx,
                    args.protein_db
                ), cwd=no_gene_dir)

            stdout_file = no_gene_dir + "/blastx.r4.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = no_gene_dir + "/blastx.r4.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

            logger.info("   get final lib")
            bash_file = no_gene_dir + "/get_final_lib.sh"
            with open(bash_file, 'w') as f:
                f.write(get_final_lib_shell % args.pe_dir)

            code, output, error = cmd_run(
                "bash %s" % bash_file, cwd=no_gene_dir)

            stdout_file = no_gene_dir + "/get_final_lib.sh.o"
            with open(stdout_file, 'w') as f:
                f.write(output)

            stderr_file = no_gene_dir + "/get_final_lib.sh.e"
            with open(stderr_file, 'w') as f:
                f.write(error)

        copy_file(allRepeats_lib_file, args.output_dir)
        logger.info("Everything is finished")

    def results_gather(self):
        work_dir = self.args.output_dir

        genome_ref = Fasta(self.args.genome)
        contig_list = list(genome_ref.keys())

        self.raw_results = {
            "MITE": work_dir + "/MITE/MITE.lib",
            "ltrharvest_99_result": work_dir + "/99/merge/all.result99",
            "MITE": work_dir + "/MITE/MITE.lib",
            "MITE": work_dir + "/MITE/MITE.lib",
            "MITE": work_dir + "/MITE/MITE.lib",
            "MITE": work_dir + "/MITE/MITE.lib",
        }


class LTR_retriever_Job(object):
    pass


def parse_maker_repeat_results(results_gff_file, te_tree, add_map_dict=None, query_lineage_dict=None, MITE_seq_id_list=None, de_novo_LTR_id_list=None):
    results_gff_info_dict = read_gff_file(results_gff_file)

    def if_coding(gf):
        if len(gf.sub_features) > 0:
            if gf.sub_features[0].type == 'mRNA':
                return True
        return False

    def if_snoRNA(gf):
        if len(gf.sub_features) > 0:
            if gf.sub_features[0].type == 'snoRNA':
                return True
        return False

    def if_tRNA(gf):
        if len(gf.sub_features) > 0:
            if gf.sub_features[0].type == 'tRNA':
                return True
        return False

    def if_repeat(gf):
        if gf.qualifiers['source'][0] == 'repeatmasker' or gf.qualifiers['source'][0] == 'repeatrunner':
            return True
        return False

    # build tc tree to save 

    tc_dict = {}
    for tc in te_tree.find_clades(order='preorder'):
        if hasattr(tc, 'lineage'):
            tc_dict[tc.lineage] = tc

   # reads maker output

    coding_gene_dict = {}
    snoRNA_gene_dict = {}
    tRNA_gene_dict = {}
    repeat_dict = {}

    for top_type in results_gff_info_dict:
        top_dict = results_gff_info_dict[top_type]

        for gf_id in top_dict:
            gf = top_dict[gf_id]

            # coding gene
            if if_coding(gf):
                coding_gene_dict[gf_id] = gf

            # snoRNA gene
            if if_snoRNA(gf):
                snoRNA_gene_dict[gf_id] = gf

            # tRNA gene
            if if_tRNA(gf):
                tRNA_gene_dict[gf_id] = gf

            # repeat
            if if_repeat(gf):
                repeat_dict[gf_id] = gf

    # repeatmasker results
    repeatmasker_tc_map = {}
    for i in tc_dict:
        tc = tc_dict[i]
        repeatmasker_equiv = tc.db_id_map['repeatmasker']
        if not repeatmasker_equiv == ("", ""):
            repeatmasker_tc_map[repeatmasker_equiv] = i

    if add_map_dict:
        for i in add_map_dict:
            repeatmasker_tc_map[i] = add_map_dict[i]

    genus_results_dict = {}
    MITE_dict = {}
    repeatmasker_unknown_gf_dict = {}
    failed_gf = []
    all_species_list = []
    all_genus_list = []
    for gf_id in repeat_dict:
        gf = repeat_dict[gf_id]

        if gf.qualifiers['source'][0] == 'repeatmasker':
            gf_Name = gf.qualifiers['Name'][0]
            repeat_name_dict = {}
            for i in gf_Name.split("|"):
                repeat_name_dict[i.split(":")[0]] = i.split(":")[1]

            try:
                genus = repeat_name_dict['genus']
                species = repeat_name_dict['species']

                all_species_list.append(species)
                all_genus_list.append(genus)

                # MITE
                if MITE_seq_id_list and species in set(MITE_seq_id_list):
                    if species not in MITE_dict:
                        MITE_dict[species] = []
                    MITE_dict[species].append(gf)    
                    continue

                if genus == 'Unknown' or genus == 'Unspecified':
                    if species not in repeatmasker_unknown_gf_dict:
                        repeatmasker_unknown_gf_dict[species] = []
                    repeatmasker_unknown_gf_dict[species].append(gf)    
                    continue

                if genus not in genus_results_dict:
                    genus_results_dict[genus] = {}

                if species not in genus_results_dict[genus]:
                    genus_results_dict[genus][species] = []

                genus_results_dict[genus][species].append(gf)

            except:
                failed_gf.append(gf)

    for genus_word in genus_results_dict:
        repeatmasker_k1 = genus_word.split("/")[0].split("?")[0]
        if "/" in genus_word:
            repeatmasker_k2 = genus_word.split("/")[-1].split("?")[0]
        else:
            repeatmasker_k2 = ""

        repeatmasker_equiv = (repeatmasker_k1, repeatmasker_k2)

        if repeatmasker_equiv in repeatmasker_tc_map:
            tc_lineage = repeatmasker_tc_map[repeatmasker_equiv]
            tc = tc_dict[tc_lineage]

            if hasattr(tc, 'repeat_case_dict'):
                for i in genus_results_dict[genus_word]:
                    tc.repeat_case_dict[i] = genus_results_dict[genus_word][i]
            else:
                tc.repeat_case_dict = genus_results_dict[genus_word]

        else:
            raise ValueError("Unknown repeatmasker_equiv: %s %s" %
                             (repeatmasker_equiv[0], repeatmasker_equiv[1]))

    # add query_lineage_dict info
    used_species = []
    for species in repeatmasker_unknown_gf_dict:
        if species in query_lineage_dict:
            anno_lineage = query_lineage_dict[species]
            
            tc = tc_dict[anno_lineage]

            if hasattr(tc, 'repeat_case_dict'):
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]
            else:
                tc.repeat_case_dict = {}
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]

            used_species.append(species)

    # add unknown de novo LTR
    ltr_lineage = ('Interspersed_Repeat', 'Transposable_Element', 'Retrotransposed_Element', 'Retrotransposon', 'Long_Terminal_Repeat_Element')
    tc = tc_dict[ltr_lineage]
    for species in repeatmasker_unknown_gf_dict:
        if species in set(de_novo_LTR_id_list) and species not in set(used_species):
            if hasattr(tc, 'repeat_case_dict'):
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]
            else:
                tc.repeat_case_dict = {}
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]
            used_species.append(species)

    # add other unknown to tc
    ltr_lineage = ('Interspersed_Repeat', 'Unknown')
    tc = tc_dict[ltr_lineage]
    for species in repeatmasker_unknown_gf_dict:
        if species not in set(used_species):
            if hasattr(tc, 'repeat_case_dict'):
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]
            else:
                tc.repeat_case_dict = {}
                tc.repeat_case_dict[species] = repeatmasker_unknown_gf_dict[species]
            # used_species.append(species)    


    # repeatrunner results
    # pass

    # tRNA
    tRNA_family_dict = {}
    for tRNA_id in tRNA_gene_dict:
        match = re.findall("trnascan-.*-noncoding-(\S+)_(\S+)-gene-.*", tRNA_id)
        if len(match) > 0:
            aa, code = match[0]
            if not (aa, code) in tRNA_family_dict:
                tRNA_family_dict[(aa, code)] = []
            tRNA_family_dict[(aa, code)].append(tRNA_gene_dict[tRNA_id])
        else:
            raise ValueError("Unknown tRNA id: %s" % tRNA_id)
    
    tRNA_lineage = ('Interspersed_Repeat', 'Pseudogene', 'RNA', 'tRNA')
    tc = tc_dict[tRNA_lineage]
    tc.repeat_case_dict = tRNA_family_dict

    return te_tree, MITE_dict


if __name__ == '__main__':
    from toolbiox.api.xuyuxing.resource.dfam import get_seq_anntation, build_TE_class_tree
    from toolbiox.lib.common.fileIO import read_list_file

    add_map_dict = {
        ('Satellite', 'subtelo'): ('Tandem_Repeat', 'Satellite', 'Subtelomeric'),
        ('Satellite', 'acro'): ('Tandem_Repeat', 'Satellite', 'Acromeric'),
        ('Satellite', 'centr'): ('Tandem_Repeat', 'Satellite', 'Centromeric'),
        ('Unspecified', ''): ('Other',),
    }


    results_gff_file = '/lustre/home/xuyuxing/Work/Gel/GenomeStat/Gel.genome.v2.0.results.gff'
    dfamtblout = "/lustre/home/xuyuxing/Work/Gel/GenomeStat/allRepeats.vs.dfam/nhmmscan.dfamtblout"
    dfam_db = "/lustre/home/xuyuxing/Database/Dfam/Dfam.info.db"
    MITE_id_file = "/lustre/home/xuyuxing/Work/Gel/GenomeStat/MITE.id"
    denovo_LTR_file = "/lustre/home/xuyuxing/Work/Gel/GenomeStat/denovo_LTR.id"

    te_tree = build_TE_class_tree()

    query_lineage_dict_raw = get_seq_anntation(dfamtblout, dfam_db, e_value_thr=1e-5, cover=0.6)
    query_lineage_dict = {}
    for i in query_lineage_dict_raw:
        query_lineage_dict[i.split("#")[0]] = query_lineage_dict_raw[i]

    MITE_seq_id_list = read_list_file(MITE_id_file)
    de_novo_LTR_id_list = read_list_file(denovo_LTR_file)

    te_tree, MITE_dict = parse_maker_repeat_results(
        results_gff_file, te_tree, add_map_dict=add_map_dict, query_lineage_dict=query_lineage_dict, MITE_seq_id_list=MITE_seq_id_list, de_novo_LTR_id_list=de_novo_LTR_id_list)

    #

    from toolbiox.lib.common.math.interval import merge_intervals, sum_interval_length


    def gf_sum_length(gf_list):
        chr_dict = {}
        for gf in gf_list:
            if not gf.chr_id in chr_dict:
                chr_dict[gf.chr_id] = []
            chr_dict[gf.chr_id].append(gf.range)
        
        sum_length = 0
        for i in chr_dict:
            merged_range = merge_intervals(chr_dict[i])
            length_now = sum_interval_length(merged_range)
            sum_length += length_now
        
        return sum_length
        
    tc_dict = {}
    for tc in te_tree.find_clades(order='preorder'):
        if hasattr(tc, 'lineage'):
            lineage = tc.lineage
            tc_dict[lineage] = tc
            if hasattr(tc, 'repeat_case_dict'):
                sum_gf_list = []
                for i in tc.repeat_case_dict:
                    gf_list = tc.repeat_case_dict[i]
                    sum_gf_list.extend(gf_list)
                print(lineage, gf_sum_length(sum_gf_list))                