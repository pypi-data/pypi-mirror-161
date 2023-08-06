from toolbiox.api.xuyuxing.genome.repeatmasker import repeatmasker_parser
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, sequence_entropy
from toolbiox.lib.common.math.interval import merge_intervals, interval_minus_set
import os
import re
import random
from toolbiox.lib.common.os import mkdir, multiprocess_running
from toolbiox.lib.xuyuxing.math.stats import get_threshold
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins

def format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50):
    # read
    repeatmasker_info = repeatmasker_parser(repeatmasker_out)
    repeat_unit = read_fasta_by_faidx(repeat_lib)
    repeat_unit = {i.split("#")[0]:str(repeat_unit[i].seq) for i in repeat_unit}
    genome_seq = read_fasta_by_faidx(genome_file)
    genome_seq = {i: str(genome_seq[i].seq) for i in genome_seq}

    # get unmasked range
    pass_repeat_feature = ['Simple_repeat', 'Low_complexity', 'rRNA']

    genome_range = {}
    for i in genome_seq:
        genome_range[i] = (1,len(genome_seq[i]))

    masked_range = {}
    for i in genome_seq:
        masked_range[i] = []

    repeat_seq_length = 0
    used_repeat_id = []
    for feature_type in repeatmasker_info:
        for repeat_id in repeatmasker_info[feature_type]:
            if not repeat_id in repeat_unit and feature_type not in pass_repeat_feature:
                raise ValueError("repeatmasker out file have repeat seq not in repeat lib fasta!")
            
            if feature_type not in pass_repeat_feature:
                used_repeat_id.append(repeat_id)
                repeat_seq_length += len(repeat_unit[repeat_id])

            for case in repeatmasker_info[feature_type][repeat_id].case_list:
                masked_range[case.q_name].append((case.q_start, case.q_end))

    for i in genome_seq:
        masked_range[i] = merge_intervals(masked_range[i])

    unmasked_range = {}
    for i in genome_seq:
        unmasked_range[i] = interval_minus_set(genome_range[i], masked_range[i])

    unmasked_length = 0
    for i in unmasked_range:
        for range_tmp in unmasked_range[i]:
            unmasked_length += (range_tmp[1] - range_tmp[0])

    genome_length = 0
    for i in genome_seq:
        genome_length += len(genome_seq[i])

    # output fasta and map file
    fragment_map = {}
    num = 0
    with open(prefix+".fragment.fasta", 'w') as f:

        for contig in unmasked_range:
            print(contig)
            for range_tmp in unmasked_range[contig]:
                for index, start, end in split_sequence_to_bins(range_tmp[1], start=range_tmp[0] ,bin_length=bin_length):
                    frag_id = "F" + str(num)
                    fragment_map[frag_id] = (contig, start, end, 'unmask')
                    
                    seq_in_range = genome_seq[contig][start - 1: end].upper()
                    
                    if len(seq_in_range) >= min_fragment_length and sequence_entropy(seq_in_range, 3) > entropy_threshold:
                        f.write(">%s\n%s\n" % (frag_id, seq_in_range))

                        num += 1

        for repeat_id in used_repeat_id:
            print(repeat_id)
            for index, start, end in split_sequence_to_bins(len(repeat_unit[repeat_id]), start=1 ,bin_length=bin_length):
                frag_id = "F" + str(num)
                fragment_map[frag_id] = (repeat_id, start, end, 'mask')

                seq_in_range = repeat_unit[repeat_id][start - 1: end].upper()

                if len(seq_in_range) >= min_fragment_length and sequence_entropy(seq_in_range, 3) > entropy_threshold:
                    f.write(">%s\n%s\n" % (frag_id, seq_in_range))

                    num += 1

    with open(prefix+".fragment.map", 'w') as f:
        for frag_id in fragment_map:
            contig, start, end, type_now = fragment_map[frag_id]
            f.write("%s\t%s\t%d\t%d\t%s\n" % (frag_id, contig, start, end, type_now))

    print(genome_length, unmasked_length, repeat_seq_length, (unmasked_length+repeat_seq_length)/genome_length)



if __name__ == "__main__":
    genome_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/T267555N0.genome.fasta'
    repeat_lib = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/T267555N0.repeat/allRepeats.clean.lib'
    repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Cuscuta_australis/RepeatMasker.out/T267555N0.genome.fasta.out'
    prefix = '/lustre/home/xuyuxing/Work/Big_HGT2/Cau'
    bin_length = 100
    entropy_threshold=3
    min_fragment_length=50

    format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50)


    genome_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phaseolus_vulgaris/T3885N0.genome.fasta'
    repeat_lib = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phaseolus_vulgaris/T3885N0.repeat/allRepeats.clean.lib'
    repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Phaseolus_vulgaris/RepeatMasker.out/T3885N0.genome.fasta.out'
    prefix = '/lustre/home/xuyuxing/Work/Big_HGT2/Pvu'
    bin_length = 100
    entropy_threshold=3
    min_fragment_length=50

    format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50)

    genome_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Helianthus_annuus/T4232N0.genome.fasta'
    repeat_lib = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Helianthus_annuus/T4232N0.repeat/allRepeats.clean.lib'
    repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Helianthus_annuus/RepeatMasker.out/T4232N0.genome.fasta.out'
    prefix = '/lustre/home/xuyuxing/Work/Big_HGT2/Han'
    bin_length = 100
    entropy_threshold=3
    min_fragment_length=50

    format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50)

    genome_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Ipomoea_nil/T35883N0.genome.fasta'
    repeat_lib = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Ipomoea_nil/T35883N0.repeat/allRepeats.clean.lib'
    repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Ipomoea_nil/RepeatMasker.out/T35883N0.genome.fasta.out'
    prefix = '/lustre/home/xuyuxing/Work/Big_HGT2/Ini'
    bin_length = 100
    entropy_threshold=3
    min_fragment_length=50

    format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50)

    genome_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/T91201N0.genome.fasta'
    repeat_lib = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.repeat/allRepeats.clean.lib'
    repeatmasker_out = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/RepeatMasker.out/Gel.genome.v2.0.fasta.out'
    prefix = '/lustre/home/xuyuxing/Work/Big_HGT2/Gel'
    bin_length = 100
    entropy_threshold=3
    min_fragment_length=50

    format_hgt_sequence_database(prefix, genome_file, repeat_lib, repeatmasker_out, bin_length, entropy_threshold=3, min_fragment_length=50)