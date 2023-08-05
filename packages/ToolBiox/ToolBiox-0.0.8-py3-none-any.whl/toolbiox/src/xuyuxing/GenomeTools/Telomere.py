from pyfaidx import Fasta
from collections import OrderedDict
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from BCBio import GFF
from toolbiox.lib.common.genome.seq_base import reverse_complement, read_fasta_by_faidx, get_seq_index_ignore_gap
from toolbiox.lib.common.os import rmdir, cmd_run
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.util import logging_init
from toolbiox.api.xuyuxing.genome.trf import trf_dat_to_dict
from toolbiox.lib.common.math.set import merge_same_element_set
from toolbiox.lib.common.math.interval import section, merge_intervals
from itertools import combinations
from toolbiox.api.common.genome.blast import outfmt5_read_big, blastn_running, outfmt5_read
from toolbiox.api.xuyuxing.genome.genblasta import GenBlastAJob
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import os


def repeat_unit_face(one_of_unit_face):
    #    one_of_unit_face = "CCCTAAA"
    double_unit = one_of_unit_face + one_of_unit_face
    unit_len = len(one_of_unit_face)

    all_face = []
    for i in range(unit_len):
        face_tmp = double_unit[i:i + unit_len]
        all_face.append(face_tmp)
        all_face.append(reverse_complement(face_tmp))

    all_face = sorted(list(set(all_face)))

    return all_face

def Telomere_main(args):

    fasta_file = args.fasta_file
    trf_dat = args.dat
    trf_path = args.trf_path
    log_file = args.log_file
    output_prefix = args.output_prefix

    """
    fasta_file = "/lustre/home/xuyuxing/Database/Other_genome/Ath/Tair10/TAIR10_Chr.all.fasta"
    trf_dat = "/lustre/home/xuyuxing/Database/Other_genome/Ath/Tair10/TAIR10_Chr.all.fasta.2.7.7.80.10.20.10.dat"
    log_file = "/lustre/home/xuyuxing/Database/Other_genome/Ath/Tair10/log"
    output_prefix =  "/lustre/home/xuyuxing/Database/Other_genome/Ath/Tair10/Ath_"
    """

    logger = logging_init("Telomere", log_file)

    logger.info("Find telomeres in an assembly")
    logger.info("Step1: get the data file from trf program")
    if trf_dat is None:
        logger.info("do not have a dat file, running trf now")
        cmd_string = "%s %s 2 7 7 80 10 20 10 -d -h" % (trf_path, fasta_file)
        a = cmd_run(cmd_string, silence=True, log_file=log_file)
        fasta_file_name = fasta_file.split("/")[-1]
        trf_dat = fasta_file_name + ".2.7.7.80.10.20.10.dat"
    else:
        logger.info("have a dat file already, pass step1")
    logger.info("Step1: finished")

    logger.info("Step2: parse trf dat file")
    trf_dict = trf_dat_to_dict(trf_dat)
    logger.info("Step2: finished")

    logger.info("Step3: find telomere unit")
    reference_dict = Fasta(fasta_file)
    telomere_dict = {}
    for chrome in reference_dict.keys():
        for trf_record in trf_dict[chrome]:
            start = min(int(trf_record["start"]), int(trf_record["end"]))
            end = max(int(trf_record["start"]), int(trf_record["end"]))
            if start <= 10 or len(reference_dict[chrome]) - end <= 10:
                uniq_rep_face = repeat_unit_face(trf_record["unit"])[0]
                if not uniq_rep_face in telomere_dict:
                    telomere_dict[uniq_rep_face] = []
                telomere_dict[uniq_rep_face].append(trf_record)
    logger.info("Step3: finished")

    logger.info("Step4: output")
    num = 0
    for i in sorted(telomere_dict, key=lambda x: len(telomere_dict[x]), reverse=True):
        with open(output_prefix + "telomere_" + str(num), "w") as f:
            for j in telomere_dict[i]:
                output_list = [i, j['chr'], j['start'], j['end'], j['unit'], j['period_size'], j['copy_num']]
                printer = printer_list(output_list)
                f.write(printer + "\n")
        num = num + 1
    logger.info("Step4: finished")