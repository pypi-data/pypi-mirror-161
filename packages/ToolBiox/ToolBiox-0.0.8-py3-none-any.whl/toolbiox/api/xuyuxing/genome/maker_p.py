import os
import re
import pickle
from pyfaidx import Fasta
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.os import mkdir, copy_file, cmd_run, multiprocess_running
from toolbiox.src.xuyuxing.tools.seqtools import split_fasta
from toolbiox.lib.common.genome.seq_base import read_fasta


# maker_p repeat

def step_1_3(sh_file, trna_file, crl_dir):
    with open(sh_file, 'w') as f:
        f.write("""#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=$1
TAG=$2
tRNA_file=%s
CRL_DIR=%s

# 2.1.1. Collection of candidate elements with LTRs that are 99%% or more in similarity using LTRharvest
mkdir $TAG
cd $TAG

gt suffixerator -db $GENOME -indexname $TAG.index -tis -suf -lcp -des -ssp -dna
gt ltrharvest -index $TAG.index -out $TAG.out99 -outinner $TAG.outinner99 -gff3 $TAG.gff99 -minlenltr 100 -maxlenltr 6000 -mindistltr 1500 -maxdistltr 25000 -mintsd 5 -maxtsd 5 -motif tgca -similar 99 -vic 10  > $TAG.result99

# 2.1.2. Using LTRdigest to find elements with PPT (poly purine tract) or PBS (primer binding site)
gt gff3 -sort $TAG.gff99 > $TAG.gff99.sort
gt ltrdigest -trnas $tRNA_file $TAG.gff99.sort $TAG.index > $TAG.gff99.dgt

perl $CRL_DIR/CRL_Step1.pl --gff $TAG.gff99.dgt

# 2.1.3. Further filtering of the candidate elements
perl $CRL_DIR/CRL_Step2.pl --step1 CRL_Step1_Passed_Elements.txt --repeatfile $TAG.out99 --resultfile $TAG.result99 --sequencefile $GENOME --removed_repeats CRL_Step2_Passed_Elements.fasta

mkdir fasta_files
mv Repeat_*.fasta fasta_files
mv CRL_Step2_Passed_Elements.fasta fasta_files
cd fasta_files

perl $CRL_DIR/CRL_Step3.pl --directory ../fasta_files --step2 CRL_Step2_Passed_Elements.fasta --pidentity 60 --seq_c 25

mv  CRL_Step3_Passed_Elements.fasta  ..
cd  ..

        """ % (trna_file, crl_dir))


def step_1_3_85(sh_file, trna_file, crl_dir):
    with open(sh_file, 'w') as f:
        f.write("""#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced
# 2.2. Collection of relatively old LTR retrotransposons

source activate maker_p

GENOME=$1
TAG=$2
tRNA_file=%s
CRL_DIR=%s

# 2.1.1
mkdir ${TAG}
cd ${TAG}

gt suffixerator -db $GENOME -indexname $TAG.index -tis -suf -lcp -des -ssp -dna
gt ltrharvest -index $TAG.index -out $TAG.out85 -outinner $TAG.outinner85 -gff3 $TAG.gff85 -minlenltr 100 -maxlenltr 6000 -mindistltr 1500 -maxdistltr 25000 -mintsd 5 -maxtsd 5 -vic 10  > $TAG.result85

# 2.1.2. Using LTRdigest to find elements with PPT (poly purine tract) or PBS (primer binding site)
gt gff3 -sort $TAG.gff85 > $TAG.gff85.sort
gt ltrdigest -trnas $tRNA_file $TAG.gff85.sort $TAG.index > $TAG.gff85.dgt

perl $CRL_DIR/CRL_Step1.pl --gff $TAG.gff85.dgt

# 2.1.3. Further filtering of the candidate elements
perl $CRL_DIR/CRL_Step2.pl --step1 CRL_Step1_Passed_Elements.txt --repeatfile $TAG.out85 --resultfile $TAG.result85 --sequencefile $GENOME --removed_repeats CRL_Step2_Passed_Elements.fasta

mkdir fasta_files
mv Repeat_*.fasta fasta_files
mv CRL_Step2_Passed_Elements.fasta fasta_files
cd fasta_files

perl $CRL_DIR/CRL_Step3.pl --directory ../fasta_files --step2 CRL_Step2_Passed_Elements.fasta --pidentity 60 --seq_c 25

mv  CRL_Step3_Passed_Elements.fasta  ..
cd  ..

""" % (trna_file, crl_dir))


def step3_merge(work_dir, contig_list, out_dir, identity):
    """
    work_dir = "/lustre/home/xuyuxing/Database/Gel/other/Dca/Dca.maker_p/LTR/99"
    contig_list = ['genome']
    out_dir = "/lustre/home/xuyuxing/Database/Gel/other/Dca/Dca.maker_p/LTR/99/merge"
    identity='99'
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

    if len(contig_list) == 1 and contig_list[0] == 'genome':
        cmd_run("cp %s %s" % (contig_dir["genome"]["CRL_Step3_file"], merge_CRL_Step3_file))
        cmd_run("cp %s %s" % (contig_dir["genome"]["result99_file"], merge_result99))
        cmd_run("cp %s %s" % (contig_dir["genome"]["outinner99_file"], merge_outinner99))
    else:
        step3_f = open(merge_CRL_Step3_file, 'w')
        result99_f = open(merge_result99, 'w')
        outinner99_f = open(merge_outinner99, 'w')

        for contig in contig_dir:
            if "CRL_Step3_file" in contig_dir[contig]:
                CRL_Step3_file = contig_dir[contig]["CRL_Step3_file"]
                seqdict, seqname_list = read_fasta(CRL_Step3_file)
                for i in seqname_list:
                    new_seq_name = re.sub('dbseq-nr_0', 'dbseq-nr_%s' % contig_dir[contig]['seq-nr'], i)
                    step3_f.write('>%s\n%s\n' % (new_seq_name, seqdict[i].seq.lower()))

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
                seqdict, seqname_list = read_fasta(outinner99_file, full_name=True, upper=False)
                for i in seqname_list:
                    new_seq_name = re.sub('dbseq-nr 0', 'dbseq-nr %s' % contig_dir[contig]['seq-nr'], i)
                    seqdict[i].wrap(60)
                    outinner99_f.write('>%s\n%s' % (new_seq_name, seqdict[i].seq.lower()))

        step3_f.close()
        result99_f.close()
        outinner99_f.close()


def step_4_5(sh_file, genome, trna_file, crl_dir, mite_file, tpase_dir):
    with open(sh_file, 'w') as f:
        f.write("""#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=%s
TAG=all
tRNA_file=%s
CRL_DIR=%s
MITE_file=%s
Tpase_dir=%s

# 2.1.4. Identify elements with nested insertions

perl $CRL_DIR/ltr_library.pl --resultfile $TAG.result99 --step3 $TAG.CRL_Step3_Passed_Elements.fasta --sequencefile $GENOME
cat lLTR_Only.lib $MITE_file  > repeats_to_mask_LTR99.fasta
RepeatMasker -pa 56 -lib repeats_to_mask_LTR99.fasta -nolow -dir . $TAG.outinner99
perl $CRL_DIR/cleanRM.pl $TAG.outinner99.out $TAG.outinner99.masked > $TAG.outinner99.unmasked
perl $CRL_DIR/rmshortinner.pl $TAG.outinner99.unmasked 50 > $TAG.outinner99.clean

blastx -query $TAG.outinner99.clean -db $Tpase_dir/Tpases020812DNA -evalue 1e-10 -num_descriptions 10 -out $TAG.outinner99.clean_blastx.out.txt -num_threads 56
perl $CRL_DIR/outinner_blastx_parse.pl --blastx $TAG.outinner99.clean_blastx.out.txt --outinner $TAG.outinner99

# 2.1.5 Building examplars

perl $CRL_DIR/CRL_Step4.pl --step3 $TAG.CRL_Step3_Passed_Elements.fasta --resultfile $TAG.result99 --innerfile passed_outinner_sequence.fasta --sequencefile $GENOME

makeblastdb -in lLTRs_Seq_For_BLAST.fasta -dbtype nucl
blastn -query lLTRs_Seq_For_BLAST.fasta -db lLTRs_Seq_For_BLAST.fasta -evalue 1e-10 -num_descriptions 1000 -out lLTRs_Seq_For_BLAST.fasta.out -num_threads 56

makeblastdb -in Inner_Seq_For_BLAST.fasta -dbtype nucl
blastn -query Inner_Seq_For_BLAST.fasta -db Inner_Seq_For_BLAST.fasta  -evalue 1e-10 -num_descriptions 1000 -out  Inner_Seq_For_BLAST.fasta.out -num_threads 56

perl $CRL_DIR/CRL_Step5.pl --LTR_blast lLTRs_Seq_For_BLAST.fasta.out --inner_blast Inner_Seq_For_BLAST.fasta.out --step3 $TAG.CRL_Step3_Passed_Elements.fasta --final LTR99.lib --pcoverage 90 --pidentity 80

""" % (genome, trna_file, crl_dir, mite_file, tpase_dir))


def step_4_5_85(sh_file, genome, trna_file, crl_dir, mite_file, tpase_dir):
    with open(sh_file, 'w') as f:
        f.write("""#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=%s
TAG=all
tRNA_file=%s
CRL_DIR=%s
MITE_file=%s
Tpase_dir=%s

# 2.1.4. Identify elements with nested insertions

perl $CRL_DIR/ltr_library.pl --resultfile $TAG.result85 --step3 $TAG.CRL_Step3_Passed_Elements.fasta --sequencefile $GENOME
cat lLTR_Only.lib $MITE_file  > repeats_to_mask_LTR85.fasta
RepeatMasker -pa 56 -lib repeats_to_mask_LTR85.fasta -nolow -dir . $TAG.outinner85
perl $CRL_DIR/cleanRM.pl $TAG.outinner85.out $TAG.outinner85.masked > $TAG.outinner85.unmasked
perl $CRL_DIR/rmshortinner.pl $TAG.outinner85.unmasked 50 > $TAG.outinner85.clean

blastx -query $TAG.outinner85.clean -db $Tpase_dir/Tpases020812DNA -evalue 1e-10 -num_descriptions 10 -out $TAG.outinner85.clean_blastx.out.txt -num_threads 56
perl $CRL_DIR/outinner_blastx_parse.pl --blastx $TAG.outinner85.clean_blastx.out.txt --outinner $TAG.outinner85

# 2.1.5 Building examplars

perl $CRL_DIR/CRL_Step4.pl --step3 $TAG.CRL_Step3_Passed_Elements.fasta --resultfile $TAG.result85 --innerfile passed_outinner_sequence.fasta --sequencefile $GENOME

makeblastdb -in lLTRs_Seq_For_BLAST.fasta -dbtype nucl
blastn -query lLTRs_Seq_For_BLAST.fasta -db lLTRs_Seq_For_BLAST.fasta -evalue 1e-10 -num_descriptions 1000 -out lLTRs_Seq_For_BLAST.fasta.out -num_threads 56

makeblastdb -in Inner_Seq_For_BLAST.fasta -dbtype nucl
blastn -query Inner_Seq_For_BLAST.fasta -db Inner_Seq_For_BLAST.fasta  -evalue 1e-10 -num_descriptions 1000 -out  Inner_Seq_For_BLAST.fasta.out -num_threads 56

perl $CRL_DIR/CRL_Step5.pl --LTR_blast lLTRs_Seq_For_BLAST.fasta.out --inner_blast Inner_Seq_For_BLAST.fasta.out --step3 $TAG.CRL_Step3_Passed_Elements.fasta --final LTR85.lib --pcoverage 90 --pidentity 80

""" % (genome, trna_file, crl_dir, mite_file, tpase_dir))


def maker_p_repeat_main(args):
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
            f.write("""source activate maker_p && \\
cp %s %s/genome.fasta && \\
perl %s -i genome.fasta -g %s -c %d -n %d -S 12345678 && \\
cat *Step8_* > MITE.lib
""" % (args.genome, MITE_dir, args.mite_hunter_manager, args.tag, args.num_threads, args.num_threads))

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
    if args.split_genome:
        logger.info("   begin genome split")
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
            split_fasta(args.genome, split_genome_dir, None, contig_model=True)
        logger.info("   end genome split")
    else:
        logger.info("   skip genome split")
        split_genome_dir = args.output_dir + "/split_genome"
        mkdir(split_genome_dir, True)
        copy_file(args.genome, split_genome_dir + "/genome.fa")
        contig_list = ['genome']

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
            contig_fasta_file = os.path.abspath(split_genome_dir + "/" + contig + ".fa")
            cmd_string = "bash %s %s %s" % (step_1_3_sh, contig_fasta_file, contig)
            args_list.append((cmd_string, ltr_99_dir, 1, True, None))

        logger.info("   raw step 1-3, begin")

        tmp_out = multiprocess_running(cmd_run, args_list, args.num_threads, log_file=ltr_99_log)

        OUT = open(tmp_out_pickle, 'wb')
        pickle.dump(tmp_out, OUT)
        OUT.close()

        logger.info("   raw step 1-3, finished")

    logger.info("   merge CRL_Step3_Passed_Elements.fasta，$TAG.result99，$TAG.outinner99")
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
        step_4_5(step_4_5_sh, args.genome, args.trna_file, args.crl_dir, MITE_file, args.tpase_dir)
        code, output, error = cmd_run("bash %s" % step_4_5_sh, cwd=merge_dir)

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
            contig_fasta_file = os.path.abspath(split_genome_dir + "/" + contig + ".fa")
            cmd_string = "bash %s %s %s" % (step_1_3_85_sh, contig_fasta_file, contig)
            args_list.append((cmd_string, ltr_85_dir, 1, True, None))

        logger.info("   raw step 1-3, begin")

        tmp_out = multiprocess_running(cmd_run, args_list, args.num_threads, log_file=ltr_85_log)

        OUT = open(tmp_out_pickle, 'wb')
        pickle.dump(tmp_out, OUT)
        OUT.close()

        logger.info("   raw step 1-3, finished")

    logger.info("   merge CRL_Step3_Passed_Elements.fasta，$TAG.result85，$TAG.outinner85")
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
        step_4_5_85(step_4_5_85_sh, args.genome, args.trna_file, args.crl_dir, MITE_file, args.tpase_dir)
        code, output, error = cmd_run("bash %s" % step_4_5_85_sh, cwd=merge_dir)

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
            f.write("""source activate maker_p && \\
RepeatMasker -pa 56 -lib LTR99.lib -dir . LTR85.lib && \\
perl %s/remove_masked_sequence.pl --masked_elements LTR85.lib.masked --outfile FinalLTR85.lib && \\
cat LTR99.lib FinalLTR85.lib > allLTR.lib
""" % args.crl_dir)

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
            f.write("""#! /bin/bash

source activate maker_p

GENOME=$1
TAG=$2
all_LIB=%s
thread=$3

mkdir ${TAG}
cd ${TAG}

RepeatMasker -pa $thread -lib $all_LIB -dir . $GENOME
""" % alllib_file)

        args_list = []
        for contig in contig_list:
            contig_fasta_file = os.path.abspath(split_genome_dir + "/" + contig + ".fa")
            if contig == 'genome':
                cmd_string = "bash %s %s %s %d" % (bash_file, contig_fasta_file, contig, args.num_threads)
            else:
                cmd_string = "bash %s %s %s %d" % (bash_file, contig_fasta_file, contig, 1)
            args_list.append((cmd_string, repeat_dir, 1, True, None))

        logger.info("   RepeatMasker, begin")

        tmp_out = multiprocess_running(cmd_run, args_list, args.num_threads, log_file=ltr_99_log)

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
            f.write("""#! /bin/bash
CRL_DIR=%s
Tpase_dir=%s

source activate maker_p

cat */*.fa.masked > all.fa.masked
perl $CRL_DIR/rmaskedpart.pl all.fa.masked 50  >  all.fa.umseqfile
sed '/^$/d' all.fa.umseqfile > all.fa.fullline.umseqfile
BuildDatabase -name umseqfiledb -engine ncbi all.fa.fullline.umseqfile
RepeatModeler -pa 14 -database umseqfiledb

perl $CRL_DIR/repeatmodeler_parse.pl --fastafile RM*/consensi.fa.classified --unknowns repeatmodeler_unknowns.fasta --identities repeatmodeler_identities.fasta

# makeblastdb -in $Tpase_dir/Tpases020812  -dbtype prot
blastx -query repeatmodeler_unknowns.fasta -db $Tpase_dir/Tpases020812 -num_threads 56 -evalue 1e-10 -num_descriptions 10 -out modelerunknown_blast_results.txt
perl $CRL_DIR/transposon_blast_parse.pl --blastx modelerunknown_blast_results.txt --modelerunknown repeatmodeler_unknowns.fasta

mv  unknown_elements.txt  ModelerUnknown.lib
cat  identified_elements.txt  repeatmodeler_identities.fasta  > ModelerID.lib
""" % (args.crl_dir, args.tpase_dir))

        logger.info("   RepeatModeler, begin")
        code, output, error = cmd_run("bash %s" % bash_file, cwd=repeat_dir)

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
            f.write("""#! /bin/bash
DIR_PE=%s

source activate maker_p

$DIR_PE/ProtExcluder.pl -f 50 ModelerUnknown.lib_blast_results.txt ModelerUnknown.lib
$DIR_PE/ProtExcluder.pl -f 50 MITE.lib_blast_results.txt MITE.lib
$DIR_PE/ProtExcluder.pl -f 50 ModelerID.lib_blast_results.txt ModelerID.lib

sed 's/(//g;s/)//g' allLTR.lib > allLTR.lib.re
sed 's/_(/_/g;s/)_/_/g' allLTR.lib_blast_results.txt > allLTR.lib_re_blast_results.txt

perl $DIR_PE/ProtExcluder.pl -f 50 allLTR.lib_re_blast_results.txt allLTR.lib.re
cat MITE.libnoProtFinal allLTR.lib.renoProtFinal ModelerID.libnoProtFinal > KnownRepeats.lib
cat KnownRepeats.lib ModelerUnknown.libnoProtFinal > allRepeats.lib
""" % args.pe_dir)

        code, output, error = cmd_run("bash %s" % bash_file, cwd=no_gene_dir)

        stdout_file = no_gene_dir + "/get_final_lib.sh.o"
        with open(stdout_file, 'w') as f:
            f.write(output)

        stderr_file = no_gene_dir + "/get_final_lib.sh.e"
        with open(stderr_file, 'w') as f:
            f.write(error)

    copy_file(allRepeats_lib_file, args.output_dir)
    logger.info("Everything is finished")

def extract_maker_repeat_info():
    pass

# maker output
