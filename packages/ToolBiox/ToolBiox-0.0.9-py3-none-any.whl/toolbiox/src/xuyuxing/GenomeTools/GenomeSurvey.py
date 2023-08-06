import sys

import toolbiox.lib.common.os
from toolbiox.config import gce_dir_path
from toolbiox.lib.xuyuxing.base.common_command import millify
import toolbiox.lib.xuyuxing.base.base_function as bf

def GenomeSurvey_main(args):
    kmer_freq_hash_path = gce_dir_path + "kmerfreq/kmer_freq_hash/kmer_freq_hash"
    gce_path = gce_dir_path + "gce"

    genome_size = args.genome_size
    genome_coverage = args.genome_coverage
    input_file_list = args.input_file_list
    kmer = args.kmer
    min_accuracy_rate = args.min_accuracy_rate
    quality_value = args.quality_value
    thread_number = args.thread_number
    output_prefix = args.output_prefix
    output_kmer_frequence_file = args.output_kmer_frequence_file
    print_flag = args.print_info
    maximum_read_length = args.maximum_read_length
    begin_ignore_len = args.begin_ignore_len
    end_ignore_len = args.end_ignore_len

    sequencing_error_rate = 1 - min_accuracy_rate
    F_represent = 0.75

    max_number_of_error_kmer = int(
        genome_coverage * kmer * sequencing_error_rate * genome_size)
    total_kmer_species_number = int(genome_size + max_number_of_error_kmer)
    initial_size_of_hash_table = int(
        total_kmer_species_number / thread_number / F_represent)

    peak_size_of_running_memory = int(
        initial_size_of_hash_table * thread_number * 8)

    cmd_string = "%s -a %d -d %d -k %d -L %d -l %s -c %.2f -q %d -i %d -t %d -p %s -o %d" % (
        kmer_freq_hash_path, begin_ignore_len, end_ignore_len, kmer, maximum_read_length, input_file_list, min_accuracy_rate, quality_value, initial_size_of_hash_table,
        thread_number, output_prefix, output_kmer_frequence_file)

    if print_flag is True:
        print("""
        Estimated genome size:          %s
        Coverage of sequence data:      %dX
        k-mer:                          %d
        min accuracy rate:              %f
        thread number:                  %d
        F represent:                    %f
        max number of error kmer:       %d
        total kmer species number:      %d
        initial size of hash table:     %d
        peak size of running memory:    %s
        """ % (
            millify(
                genome_size), genome_coverage, kmer, min_accuracy_rate, thread_number, F_represent,
            max_number_of_error_kmer,
            total_kmer_species_number, initial_size_of_hash_table, millify(peak_size_of_running_memory)))
        print(cmd_string)
        sys.exit(0)

    print(cmd_string)

    flag, output, error = lib.common.os.cmd_run(cmd_string)

    print(error)

    # kmer_report_string = error.decode()
    #
    #
    # for each_line in kmer_report_string.split("\n"):
    #    matchobj = re.match(r"^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+)")
    #    if matchobj:
    #        Kmer_individual_num = matchobj.group(2)