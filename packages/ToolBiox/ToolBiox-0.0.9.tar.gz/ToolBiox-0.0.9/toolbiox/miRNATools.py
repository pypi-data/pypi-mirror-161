import toolbiox.lib.common.os
import toolbiox.lib.xuyuxing.base.base_function as bf
from toolbiox.lib.common.genome.seq_base import read_fasta_big, sub_seq
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.math.interval import section, group_by_intervals
from toolbiox.config import *
from collections import Counter
import re
import os
import pysam


def get_lr(brax):
    hash = {}
    lefts = []
    i = 0
    for ch in brax:
        i = i + 1
        if ch == "(":
            lefts.append(i)
        elif ch == ")":
            left = lefts.pop()
            hash[left] = i
    return hash


def get_rl(brax):
    lr = get_lr(brax)
    rl = {}
    for left in lr:
        right = lr[left]
        rl[right] = left
    return rl


def check_mir_star(brax, strand, fold_start, fold_stop, mirkey_start, mirlen):
    if strand == "+":
        offset = mirkey_start - fold_start
    else:
        offset = fold_stop - mirkey_start - mirlen + 1

    if not (offset + mirlen) < len(brax):
        return ("N10",)

    mir_brax = brax[offset:offset + mirlen]
    n_mir_up = mir_brax.count(".")

    # print(n_mir_up)

    if n_mir_up > 5:
        return ("N11",)

    n_bulges = 0
    bulged_nts = 0
    last_right = 0
    last_left = 0

    if re.match(r'^[\.\(]+$', mir_brax):
        # find star of a 5p miRNA
        left_right = get_lr(brax)

        # get one-based start and stop of the mature miRNA, relative to brax
        mir_brax_start = offset + 1
        mir_brax_end = mir_brax_start + mirlen - 1

        # March through the mature miRNA until the last 2 bases (3' overhang),
        # tracking bulges, and getting the star 5p and 3p
        for left in range(mir_brax_start, mir_brax_end - 2):
            if left in left_right:
                if last_right and last_left:  # was it a bulge?
                    left_delta = left - last_left
                    right_delta = last_right - left_right[left]
                    if abs(left_delta - right_delta):
                        n_bulges = n_bulges + 1
                        bulged_nts = bulged_nts + abs(left_delta - right_delta)
                    else:
                        # This is the first pair found in the duplex
                        # Infer the 3p end of the miRNA* .. 2nt offset
                        star_brax_end = left_right[left] + 2 + (left - mir_brax_start)
                last_left = left
                last_right = left_right[left]
        if n_bulges > 2 or bulged_nts > 3:
            return ("N13",)
        else:
            if not last_left:
                return ("N10",)
            # Calculate the star 5p position, relative to brax
            star_brax_start = left_right[last_left] - ((mir_brax_end - 2) - last_left)
            # above, the right-hand term is 0 if the last position analyzed of the mature miRNA was paired.
        ## encode and return (below)
    elif re.match(r'^[\.\)]+$', mir_brax):
        # find star of a 3p miRNA
        right_left = get_rl(brax)
        # get one-based start and stop of the mature miRNA, relative to brax
        mir_brax_start = offset + 1
        mir_brax_end = mir_brax_start + mirlen - 1

        # March through the mature miRNA until the last 2 bases (3' overhang),
        # tracking bulges, and getting the star 5p and 3p
        for right in range(mir_brax_start, mir_brax_end - 2):
            if right in right_left:
                if last_right and last_left:
                    # was it a bulge?
                    left_delta = right_left[right] - last_left
                    right_delta = last_right - right
                    if abs(left_delta - right_delta):
                        n_bulges = n_bulges + 1
                        bulged_nts = bulged_nts + abs(left_delta - right_delta)
                else:
                    # This is the first pair found in the duplex
                    # Infer the 3p end of the miRNA* .. 2nt offset
                    star_brax_end = right_left[right] + (right - mir_brax_start) + 2
                last_left = right_left[right]
                last_right = right
        if n_bulges > 2 or bulged_nts > 3:
            return ("N13",)
        else:
            if not last_right:
                return ("N10",)
            # Calculate the star 5p position, relative to brax
            star_brax_start = right_left[last_right] - ((mir_brax_end - 2) - last_right)
    else:
        return ("N12",)

    if star_brax_start and star_brax_end:
        if star_brax_start >= star_brax_end:
            return ("N10",)
        else:
            if strand == "+":
                star_left = star_brax_start + fold_start - 1
            else:
                star_left = fold_stop - star_brax_end + 1
            mdz = star_brax_end - star_brax_start + 1
            return star_left, strand, mdz
    else:
        return ("N10",)


def mistar_get(mirkey_start, mirlen, refseq, strand, local_start, local_end, foldsize, mir_seq=""):
    loc_center = int(local_start) + int(0.5 * (int(local_end) - int(local_start) + 1))
    fold_start = max(1, loc_center - (int(0.5 * foldsize)))
    fold_stop = min(loc_center + (int(0.5 * foldsize)), len(refseq))

    fold_seq = sub_seq(refseq, fold_start, fold_stop, strand, True)

    cmd_string = "echo %s | %s --noPS " % (fold_seq, RNAfold_path)
    flag_tmp, output, error = lib.common.os.cmd_run(cmd_string, silence=True)
    output = output.decode()
    brax = output.split("\n")[1].split(" ")[0]

    check_mir_star_output = check_mir_star(brax, strand, fold_start, fold_stop, mirkey_start, mirlen)

    if len(check_mir_star_output) == 1:
        return check_mir_star_output

    mirkey_end = mirkey_start + mirlen - 1
    if mir_seq == "":
        mir_seq = sub_seq(refseq, mirkey_start, mirkey_end, strand, True)

    star_left, strand, mdz = check_mir_star_output
    mistar_start = star_left
    mistar_end = star_left + mdz - 1
    mistar_seq = sub_seq(refseq, mistar_start, mistar_end, strand, True)

    return (mirkey_start, mirkey_end, mir_seq, mistar_start, mistar_end, mistar_seq)


def blast_and_hit_parse(query_file, db_file, bls_file, aln_ratio, min_len, foldsize, num_threads):
    # load query fasta file
    record_dict = {}
    for record in read_fasta_big(query_file):
        record_dict[record.seqname_short()] = record

    # load db fasta file
    record_db_dict = {}
    for record in read_fasta_big(db_file):
        record_db_dict[record.seqname_short()] = record

    # make blast
    cmd_string = blast_path + "blastn -query %s -db %s -out %s -word_size 4 -gapopen 5 -gapextend 2 -reward 1 -penalty -3 -evalue 10 -outfmt 6 -num_threads %d" % (
        query_file, db_file, bls_file, num_threads)
    lib.common.os.cmd_run(cmd_string, silence=True)

    # load blast results
    outfmt6_title = (
        "query", "subject", "identity", "aln_len", "miss", "gap", "qstart", "qend", "sstart", "send", "evalue", "score")
    hit_dict = tsv_file_dict_parse(bls_file, fieldnames=outfmt6_title)

    # drop_short_hit
    def drop_short_aln(aln_len, query_len):
        aln_len_limit = max(min_len, query_len * aln_ratio)
        if aln_len >= aln_len_limit:
            return 1
        else:
            return 0

    candi_hit_id = [ID for ID in hit_dict if
                    drop_short_aln(abs(int(hit_dict[ID]["sstart"]) - int(hit_dict[ID]["send"])),
                                   len(record_dict[hit_dict[ID]["query"]].seqs))]

    output_list = []
    for ID in candi_hit_id:
        loc_range = (int(hit_dict[ID]["send"]), int(hit_dict[ID]["sstart"]))
        mirkey_start = min(loc_range)
        mirkey_end = max(loc_range)
        loc_delta = int(hit_dict[ID]["send"]) - int(hit_dict[ID]["sstart"])
        mirlen = abs(loc_delta) + 1

        if loc_delta > 0:
            strand = "+"
        else:
            strand = "-"

        loc_center = min(loc_range) + int(0.5 * mirlen)
        fold_start = max(1, loc_center - (int(0.5 * foldsize)))
        fold_stop = min(loc_center + (int(0.5 * foldsize)), len(record_db_dict[hit_dict[ID]["subject"]].seqs))

        fold_seq = sub_seq(record_db_dict[hit_dict[ID]["subject"]].seqs, fold_start, fold_stop, strand, True)

        cmd_string = "echo %s | %s --noPS " % (fold_seq, RNAfold_path)
        flag_tmp, output, error = lib.common.os.cmd_run(cmd_string, silence=True)
        output = output.decode()
        brax = output.split("\n")[1].split(" ")[0]

        check_mir_star_output = check_mir_star(brax, strand, fold_start, fold_stop, mirkey_start, mirlen)

        if len(check_mir_star_output) == 1:
            continue

        star_left, strand, mdz = check_mir_star_output

        query = hit_dict[ID]["query"]
        chr = hit_dict[ID]["subject"]
        mirkey_start = mirkey_start
        mirkey_end = mirkey_end
        strand = strand
        mir_seq = sub_seq(record_db_dict[hit_dict[ID]["subject"]].seqs, mirkey_start, mirkey_end, strand, True)
        mistar_start = star_left
        mistar_end = star_left + mdz - 1
        mistar_seq = sub_seq(record_db_dict[hit_dict[ID]["subject"]].seqs, mistar_start, mistar_end, strand, True)
        display_start = max(1, min(mistar_start, mistar_end, mirkey_start, mirkey_end) - 10)
        display_end = min(len(record_db_dict[hit_dict[ID]["subject"]].seqs),
                          max(mistar_start, mistar_end, mirkey_start, mirkey_end) + 10)
        display_fold_seq = sub_seq(record_db_dict[hit_dict[ID]["subject"]].seqs, display_start, display_end, strand,
                                   True)

        cmd_string = "echo %s | %s --noPS " % (display_fold_seq, RNAfold_path)
        flag_tmp, output, error = lib.common.os.cmd_run(cmd_string, silence=True)
        output = output.decode()
        display_fold_brax = output.split("\n")[1].split(" ")[0]

        output_list.append((query, chr, strand, mirkey_start, mirkey_end, mir_seq, mistar_start, mistar_end, mistar_seq,
                            display_start, display_end, display_fold_seq, display_fold_brax))
    return output_list


def SSRead_parse(input_file):
    with open(input_file, 'r') as f:
        for each_line in f:
            matchObj = re.match(
                r'^(Cluster_\d+) Original Location: (\S+):(\d+)-(\d+) Displayed Location: (\S+):(\d+)-(\d+) Strand: (\S).*',
                each_line)
            if matchObj:
                ID, Ori_Loc_chr, Ori_Loc_start, Ori_Loc_end, Dis_Loc_chr, Dis_Loc_start, Dis_Loc_end, strand = matchObj.groups()
                continue

            matchObj = re.match(r"^(\.*)([^\.]+)(\.*) miRNA l=(\d+) a=(\d+).*", each_line)
            if matchObj:
                miRNA_seq_l, miRNA_seq, miRNA_seq_r, miRNA_len, miRNA_aln = matchObj.groups()
                miRNA_seq = miRNA_seq.upper()
                left_len = len(miRNA_seq_l)
                right_len = len(miRNA_seq_r)
                if strand == "+":
                    miRNA_start = int(Dis_Loc_start) + int(left_len)
                    miRNA_end = int(Dis_Loc_end) - int(right_len)
                else:
                    miRNA_start = int(Dis_Loc_start) + int(right_len)
                    miRNA_end = int(Dis_Loc_end) - int(left_len)
                continue

            matchObj = re.match(r"^(\.*)([^\.]+)(\.*) miRNA-star l=(\d+) a=(\d+).*", each_line)
            if matchObj:
                miRNA_star_seq_l, miRNA_star_seq, miRNA_star_seq_r, miRNA_star_len, miRNA_star_aln = matchObj.groups()
                miRNA_star_seq = miRNA_star_seq.upper()
                left_len = len(miRNA_star_seq_l)
                right_len = len(miRNA_star_seq_r)
                if strand == "+":
                    miRNA_star_start = int(Dis_Loc_start) + int(left_len)
                    miRNA_star_end = int(Dis_Loc_end) - int(right_len)
                else:
                    miRNA_star_start = int(Dis_Loc_start) + int(right_len)
                    miRNA_star_end = int(Dis_Loc_end) - int(left_len)
                continue

    output_list = (
        input_file, ID, Ori_Loc_chr, Ori_Loc_start, Ori_Loc_end, Dis_Loc_chr, Dis_Loc_start, Dis_Loc_end, strand,
        miRNA_start, miRNA_end, miRNA_seq, miRNA_len, miRNA_aln, miRNA_star_start, miRNA_star_end, miRNA_star_seq,
        miRNA_star_len, miRNA_star_aln)

    return output_list


def bam_support(bam_file, contig, start, end, strand, sequence="", rpmm=False):
    """
    :bam_file = "/lustre/home/xuyuxing/Work/miRNA/Cau_two_assembly/ShortStack/Cau_map/de_novo_map/A3130.SS/A3130.filtered.10-42.bam"
    :contig = "C063N"
    :start = 26963
    :end = 26986
    :strand = "-"
    :sequence = 'CGCUUGUUAGAUCUUGCGUUCCUU'
    :return: 67
    """
    bam_file_object = pysam.AlignmentFile(bam_file, "rb")

    match_count = 0
    read_seq_raw = ""
    iter = bam_file_object.fetch(contig, start, end)
    all_read_seq = []
    for x in iter:
        if strand == "-" and x.is_reverse:
            read_seq_raw = x.get_forward_sequence()
        elif strand == "+" and not x.is_reverse:
            read_seq_raw = x.seq

        read_seq = re.sub('T', 'U', read_seq_raw)
        all_read_seq.append(read_seq)

        if not sequence == "":
            if read_seq == sequence:
                match_count = match_count + 1
    mapped_reads = bam_file_object.mapped
    bam_file_object.close()

    if not sequence == "":
        if not rpmm:
            return match_count
        else:
            rpmm_value = match_count / mapped_reads * 1000000
            return (match_count, rpmm_value)
    else:
        return Counter(all_read_seq)


def bam_support_block(bam_file, contig, start, end, strand, sequence):
    if not os.path.exists(bam_file + ".bai"):
        cmd_string = "samtools index %s" % bam_file
        flag_tmp, output, error = lib.common.os.cmd_run(cmd_string, silence=True)

    bam_file_object = pysam.AlignmentFile(bam_file, "rb")
    start = int(start)
    end = int(end)
    read_seq_raw = ""
    iter = bam_file_object.fetch(contig, start, end)
    blocks = []
    for x in iter:
        if strand == "-" and x.is_reverse:
            read_seq_raw = x.get_forward_sequence()
        elif strand == "+" and not x.is_reverse:
            read_seq_raw = x.seq
        read_seq = re.sub('T', 'U', read_seq_raw)
        if read_seq == sequence:
            blocks.append(tuple(x.blocks[0]))
    bam_file_object.close()

    blocks = Counter(blocks)
    blocks = sorted(blocks, key=lambda x: blocks[x], reverse=True)

    return (blocks[0][0] + 1, blocks[0][1])


def unique_miRNA_type(input_list, input_dir, contig, data_type):
    # choose miRNA type
    miRNA_type_list = {}
    for sample, cluster_id in input_list:
        miRNA_type = tuple([input_dir[sample][data_type][cluster_id][i] for i in (3, 4, 2, 5)])
        if not miRNA_type in miRNA_type_list: miRNA_type_list[miRNA_type] = []
        miRNA_type_list[miRNA_type].append((sample, cluster_id))

    miRNA_type_support = []
    for miRNA_type in miRNA_type_list:
        total_support = 0
        for sample, cluster_id in miRNA_type_list[miRNA_type]:
            bam_file = input_dir[sample]["bam"]
            start, end, strand, sequence = miRNA_type
            # print(bam_file, contig, start, end, strand, sequence)
            tmp_support = bam_support(bam_file, contig, start, end, strand, sequence)
            total_support = total_support + tmp_support
        if total_support == 0:
            continue
        miRNA_type_support.append((miRNA_type, total_support))

    miRNA_type_support = sorted(miRNA_type_support, key=lambda x: x[1], reverse=True)

    keep_miRNA_type = []
    for i in range(len(miRNA_type_support)):
        if i + 2 > len(miRNA_type_support):
            keep_miRNA_type.append(miRNA_type_support[i][0])
            break
        if miRNA_type_support[i][1] / miRNA_type_support[i + 1][1] > 2.0:
            keep_miRNA_type.append(miRNA_type_support[i][0])
            break
        else:
            keep_miRNA_type.append(miRNA_type_support[i][0])

    # choose miRNA star type
    all_output = []

    miRNA_star_type_dict = {}
    for sample, cluster_id in input_list:
        miRNA_type = tuple([input_dir[sample][data_type][cluster_id][i] for i in (3, 4, 2, 5)])
        if not miRNA_type in keep_miRNA_type: continue
        if not miRNA_type in miRNA_star_type_dict: miRNA_star_type_dict[miRNA_type] = {}
        miRNA_star_type = tuple([input_dir[sample][data_type][cluster_id][i] for i in (6, 7, 2, 8)])
        if not miRNA_star_type in miRNA_star_type_dict[miRNA_type]: miRNA_star_type_dict[miRNA_type][
            miRNA_star_type] = []
        miRNA_star_type_dict[miRNA_type][miRNA_star_type].append((sample, cluster_id))

    miRNA_star_type_support = {}
    for miRNA_type in miRNA_star_type_dict:
        miRNA_star_type_support[miRNA_type] = []
        for miRNA_star_type in miRNA_star_type_dict[miRNA_type]:
            total_support = 0
            for sample, cluster_id in miRNA_star_type_dict[miRNA_type][miRNA_star_type]:
                bam_file = input_dir[sample]["bam"]
                start, end, strand, sequence = miRNA_star_type
                # print(bam_file, contig, start, end, strand, sequence)
                tmp_support = bam_support(bam_file, contig, start, end, strand, sequence)
                total_support = total_support + tmp_support
            miRNA_star_type_support[miRNA_type].append((miRNA_star_type, total_support))

        miRNA_star_type_support[miRNA_type] = sorted(miRNA_star_type_support[miRNA_type], key=lambda x: x[1],
                                                     reverse=True)

        keep_miRNA_star_type = miRNA_star_type_support[miRNA_type][0][0]
        all_output.append(tuple(list(miRNA_type) + list(keep_miRNA_star_type)))

    return all_output


def block_to_miRNA_seq(contig, strand, start, end, input_dir, reference_genome_dict, support_read_rpmm=1,
                       orgin_seq=False):
    """
    :param contig="C017N"
    :param strand="+"
    :param start=4098941
    :param end=4098961
    :param input_dir:
    :return:
    """
    if not orgin_seq:
        read_sample_dict = {}
        for sample in input_dir:
            if sample == "homo_SS": continue
            candi = bam_support(input_dir[sample]["bam"], contig, start, end, strand)
            for i in candi:
                if candi[i] < 10:
                    continue
                if i not in read_sample_dict: read_sample_dict[i] = {}
                read_sample_dict[i][sample] = candi[i]

        sort_list_tmp = []
        for i in read_sample_dict:
            for sample in read_sample_dict[i]:
                sort_list_tmp.append((i, sample, read_sample_dict[i][sample]))

        if len(sort_list_tmp) == 0:
            return ""

        sort_list_tmp = sorted(sort_list_tmp, key=lambda x: x[2], reverse=True)

        best_miRNA_mature = sort_list_tmp[0][0]

        return best_miRNA_mature
    else:
        best_miRNA_mature = reference_genome_dict[contig].sub(start, end, strand, True)
        flag = 0
        for sample in input_dir:
            if sample == "homo_SS": continue
            rpmm = bam_support(input_dir[sample]["bam"], contig, start, end, strand, sequence=best_miRNA_mature,
                               rpmm=True)
            # print(rpmm)
            if rpmm >= support_read_rpmm:
                flag = 1
        if flag == 1:
            return best_miRNA_mature
        else:
            return ""


def miRNA_name(miRNA_seq, mirbase_fasta, temp_file):
    with open(temp_file, "w") as f:
        f.write(">%s\n%s\n" % ("temp", miRNA_seq))
    cmd_string = "%s -3 -m 8CD -n -Q -f -16 -r +15/0 -g -16 -w 25 -W 25 -E 10000 -U %s %s" % (
        ssearch_path, temp_file, mirbase_fasta)
    flag_tmp, output, error = lib.common.os.cmd_run(cmd_string, silence=True)
    output = output.decode()
    miRNA_name_dict = {}
    for each_line in output.split("\n"):
        if re.match(r'^#', each_line):
            continue
        info = each_line.split("\t")
        if len(info) == 1:
            continue
        name = info[1]
        aln_code = info[12]
        matches_num = 0
        for i in re.findall(r'(\d+)M', aln_code):
            matches_num = matches_num + int(i)
        if len(miRNA_seq) - matches_num > 2:
            continue
        else:
            # print(record, name)
            name_space = name.split("-")
            speci = name_space[0]
            miRNA_name = name_space[1]
            matchObj = re.match(r'^(miR\d+).*', miRNA_name)
            if matchObj:
                miRNA_name = re.findall(r'^(miR\d+).*', miRNA_name)[0]
                if miRNA_name not in miRNA_name_dict: miRNA_name_dict[miRNA_name] = []
                miRNA_name_dict[miRNA_name].append(speci)
                miRNA_name_dict[miRNA_name] = list(set(miRNA_name_dict[miRNA_name]))
    if len(miRNA_name_dict) == 0:
        best_name = "Unknown"
    else:
        best_name = sorted(miRNA_name_dict, key=lambda x: len(miRNA_name_dict[x]), reverse=True)[0]

    return best_name


if __name__ == '__main__':

    import argparse

    # argument parse
    # ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog='miRNA',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for miRNAblast
    parser_a = subparsers.add_parser('miRNAblast',
                                     help='use mature miRNA to blast a genome and fold subject to find new homo miRNA\n',
                                     description='use mature miRNA to blast a genome and fold subject to find new homo miRNA')
    parser_a.add_argument("query_file", help="Path for query mature miRNA fasta", type=str)
    parser_a.add_argument("db_file", help="Path for genome assembly fasta", type=str)
    parser_a.add_argument("output_file", help="Path for output tab file", type=str)
    parser_a.add_argument("-r", "--aln_ratio",
                          help="the blast hit which length small than aln_ratio * query length will not be use. (default as 0.8)",
                          default=0.8, type=float)
    parser_a.add_argument("-l", "--min_len",
                          help="the blast hit which length small than min_len will not be use. (default as 18)",
                          default=18, type=int)
    parser_a.add_argument("-s", "--foldsize", help="sequence length which used in RNAfold (default as 300)",
                          default=300,
                          type=str)
    parser_a.add_argument("-p", "--num_threads", help="num of threads for blastn", default=1, type=int)

    # argparse for uniqMiRNA
    parser_a = subparsers.add_parser('uniqMiRNA',
                                     help='union blast miRNA subject to unique annotation\n',
                                     description='')

    parser_a.add_argument("input_file", help="output file from miRNAblast", type=str)
    parser_a.add_argument('output_file', type=str, help='unique miRNA annotation')

    # argparse for SSRead
    parser_a = subparsers.add_parser('SSRead',
                                     help='Read the ShortStack output in MIRNAs\n',
                                     description='')

    parser_a.add_argument("input_file", help="ShortStack output in MIRNAs", type=str)
    # parser_a.add_argument('output_file', type=str, help='unique miRNA annotation')

    # argparse for SSBamStat
    parser_a = subparsers.add_parser('SSBamStat',
                                     help='Read ShortStack bam output and stat the mapped and unmapped length distribution\n',
                                     description='')

    parser_a.add_argument("input_file", help="ShortStack bam output", type=str)
    parser_a.add_argument('output_file', type=str, help='output file')

    # argparse for SSResultsLen
    parser_a = subparsers.add_parser('SSResultsLen',
                                     help='ShortStack Results 20 21 22 23 24 在每个cluster中的比例与对应reads个数的分布\n',
                                     description='')

    parser_a.add_argument("input_file", help="ShortStack Results.txtt", type=str)
    parser_a.add_argument('output_file', type=str, help='output file')

    # argparse for SSResultsMerge
    parser_a = subparsers.add_parser('SSResultsMerge',
                                     help='Merge diff ShortStack Results to one annotation\n',
                                     description='')

    parser_a.add_argument("input_file_list",
                          help="a tab file include all ShortStack Results, first column is sample name and second column is ShortStack output dir.",
                          type=str)
    parser_a.add_argument('reference', type=str, help='reference genome file')
    parser_a.add_argument('mirbase_fasta', type=str, help='a fasta file included mature seq from mirbase')
    parser_a.add_argument('output_prefix', type=str, help='output prefix')
    parser_a.add_argument("-t", "--temp_dir",
                          help="temp dir which will be use for store some temp file. (default as ./)",
                          default="./", type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    # miRNAblast
    if args_dict["subcommand_name"] == "miRNAblast":
        query_file = args.query_file
        db_file = args.db_file
        output_file = args.output_file
        aln_ratio = args.aln_ratio
        min_len = args.min_len
        foldsize = args.foldsize
        num_threads = args.num_threads

        bls_file = os.path.dirname(os.path.abspath(output_file)) + "/" + str(os.getpid()) + ".tmp.bls"
        output = blast_and_hit_parse(query_file, db_file, bls_file, aln_ratio, min_len, foldsize, num_threads)

        with open(output_file, "w") as f:
            f.write(
                "query\tchr\tstrand\tmirna_start\tmirna_end\tmir_seq\tmistar_start\tmistar_end\tmistar_seq\tdisplay_start\tdisplay_end\tdisplay_fold_seq\tdisplay_fold_brax\n")
            for i in output:
                printer = ""
                for j in i:
                    printer = printer + str(j) + "\t"
                printer = printer.rstrip("\t")
                f.write(printer + "\n")

    # uniqMiRNA
    elif args_dict["subcommand_name"] == "uniqMiRNA":
        input_file = args.input_file
        output_file = args.output_file

        record_dict = tsv_file_dict_parse(input_file)

        ref_dict = {}
        for ID in record_dict:
            chr = record_dict[ID]['chr']
            strand = record_dict[ID]['strand']
            if not chr in ref_dict:
                ref_dict[chr] = {}
                ref_dict[chr]["+"] = {}
                ref_dict[chr]["+"]["ID"] = []
                ref_dict[chr]["-"] = {}
                ref_dict[chr]["-"]["ID"] = []
            ref_dict[chr][strand]["ID"].append(ID)

        num = 0
        group_dict = {}
        for chr in ref_dict:
            for strand in ref_dict[chr]:
                group_dict_tmp = group_by_intervals(
                    [(ID, int(record_dict[ID]["display_start"]), int(record_dict[ID]["display_end"])) for ID in
                     ref_dict[chr][strand]["ID"]], int=True)
                for range_key in group_dict_tmp:
                    group_dict["group_" + str(num)] = (chr, strand, range_key, tuple(group_dict_tmp[range_key]))
                    num = num + 1
        output_list = []
        for group_id in group_dict:
            chr, strand, range_key, record_list = group_dict[group_id]

            group_dict_tmp = group_by_intervals(
                [(ID, int(record_dict[ID]["mirna_start"]), int(record_dict[ID]["mirna_end"])) for ID in record_list],
                int=True)
            mirna_range = sorted(group_dict_tmp, key=lambda x: len(group_dict_tmp[x]), reverse=True)[0]

            group_dict_tmp = group_by_intervals(
                [(ID, int(record_dict[ID]["mistar_start"]), int(record_dict[ID]["mistar_end"])) for ID in record_list],
                int=True)
            mistar_range = sorted(group_dict_tmp, key=lambda x: len(group_dict_tmp[x]), reverse=True)[0]

            family_ID = []
            for ID in record_list:
                query_name = record_dict[ID]['query']
                for i in query_name.split("-"):
                    matchObj = re.match(r'(miR\d+).*', i)
                    if matchObj:
                        family_ID.append(matchObj.group(1))

            family_ID = Counter(family_ID)
            family_ID = sorted(family_ID, key=lambda x: family_ID[x], reverse=True)
            family_ID_best = family_ID[0]

            output_list.append((family_ID_best, chr, strand, mirna_range[0], mirna_range[1], mistar_range[0],
                                mistar_range[1], range_key[0], range_key[1]))

        with open(output_file, "w") as f:
            f.write(
                "family_name\tchr\tstrand\tmirna_start\tmirna_end\tmistar_start\tmistar_end\tdisplay_start\tdisplay_end\n")
            for i in output_list:
                printer = ""
                for j in i:
                    printer = printer + str(j) + "\t"
                printer = printer.rstrip("\t")
                f.write(printer + "\n")

    # SSRead
    elif args_dict["subcommand_name"] == "SSRead":
        input_file = args.input_file
        # output_file = args.output_file

        output_list = SSRead_parse(input_file)

        printer = ""
        for j in output_list:
            printer = printer + str(j) + "\t"
        printer = printer.rstrip("\t")
        print(printer)

    # SSBamStat
    elif args_dict["subcommand_name"] == "SSBamStat":
        from collections import Counter

        input_file = args.input_file
        output_file = args.output_file

        # input_file = "/lustre/home/xuyuxing/Work/miRNA/Cau/bam/Cau/test.bam"

        map_type_dict = {}
        min_len = float("inf")
        max_len = float("-inf")
        for each_line in bf.cmd_open(samtools_path + " view " + input_file):
            each_line = re.sub(r'\n', '', each_line)
            if each_line == "": continue
            info = each_line.split("\t")
            seqname = info[0]
            seqs_len = len(info[9])
            if seqs_len < min_len: min_len = seqs_len
            if seqs_len > max_len: max_len = seqs_len
            contig = info[2]
            if contig == "*":
                if not "unmapped" in map_type_dict: map_type_dict["unmapped"] = []
                map_type_dict["unmapped"].append(seqs_len)
                continue
            XY_Z = info[17]
            if not XY_Z in map_type_dict: map_type_dict[XY_Z] = []
            map_type_dict[XY_Z].append(seqs_len)

        map_type_dict_key = list(map_type_dict.keys())
        for XY_Z in map_type_dict_key:
            map_type_dict[XY_Z] = Counter(map_type_dict[XY_Z])

        with open(output_file, "w") as f:
            print_head = "\t"
            for XY_Z in map_type_dict_key:
                print_head = print_head + XY_Z + "\t"
            print_head = print_head.rstrip("\t")
            f.write(print_head + "\n")

            for i in range(min_len, max_len + 1):
                printer = "%d\t" % i
                for XY_Z in map_type_dict_key:
                    printer = printer + str(map_type_dict[XY_Z][i]) + "\t"
                printer = printer.rstrip("\t")
                f.write(printer + "\n")


    # SSResultsLen
    elif args_dict["subcommand_name"] == "SSResultsLen":
        from collections import Counter

        input_file = args.input_file
        output_file = args.output_file

        dict_load = tsv_file_dict_parse(input_file)

        reads_len = ["20", "21", "22", "23", "24"]

        reads_ratio_list = {}
        for len_tmp in reads_len:
            reads_ratio_list[len_tmp] = []
            for ID in dict_load:
                all_counts = 0
                for i in reads_len:
                    all_counts = all_counts + int(dict_load[ID][i])
                if all_counts == 0: continue
                ratio = (int(dict_load[ID][len_tmp]) / all_counts) * 100
                reads_ratio_list[len_tmp].append((ratio, int(dict_load[ID][len_tmp])))

        output_dict = {}
        for len_tmp in reads_len:
            output_dict[len_tmp] = {}
            for i in range(0, 100):
                output_dict[len_tmp][i] = 0
                for ratio, reads in reads_ratio_list[len_tmp]:
                    if ratio >= i and ratio < i + 1:
                        output_dict[len_tmp][i] = output_dict[len_tmp][i] + reads

    # SSResultsMerge
    elif args_dict["subcommand_name"] == "SSResultsMerge":
        input_file_list = args.input_file_list
        reference_file = args.reference
        output_prefix = args.output_prefix
        mirbase_fasta = args.mirbase_fasta
        temp_dir = args.temp_dir

        # Read all information from SS

        input_dir = tsv_file_dict_parse(input_file_list, seq=",", fieldnames=("key", "dir"), key_col="key",
                                        fields=["dir"])

        reference_genome_dict = {}
        for record in read_fasta_big(reference_file):
            reference_genome_dict[record.seqname] = record

        for sample in input_dir:
            dir_tmp = input_dir[sample]["dir"]
            for file in os.listdir(dir_tmp):
                if re.match(r'.*\.bam$', file):
                    input_dir[sample]["bam"] = os.path.join(dir_tmp, file)
                if file == "Results.txt":
                    file_path = os.path.join(dir_tmp, file)
                    input_dir[sample]["results"] = tsv_file_dict_parse(file_path, key_col="Name")

            input_dir[sample]["de_novo"] = {}
            for file in os.listdir(dir_tmp + "/MIRNAs"):
                file_path = os.path.join(dir_tmp + "/MIRNAs", file)
                output_list = SSRead_parse(file_path)
                input_dir[sample]["de_novo"][output_list[1]] = tuple(
                    [output_list[i] for i in (1, 2, 8, 9, 10, 11, 14, 15, 16)])

            input_dir[sample]["N15"] = {}
            for cluster_id in input_dir[sample]["results"]:
                if input_dir[sample]["results"][cluster_id]['MIRNA'] == 'N15':
                    strand = input_dir[sample]["results"][cluster_id]['Strand']
                    if strand == ".":
                        # print("Strand Error", sample, cluster_id)
                        continue
                    DicerCall = int(input_dir[sample]["results"][cluster_id]['DicerCall'])
                    if DicerCall < 20 or DicerCall > 24:
                        # print("DicerCall Error", sample, cluster_id)
                        continue

                    contig, raw_start, raw_end = re.findall(r"(\S+):(\d+)-(\d+)",
                                                            input_dir[sample]["results"][cluster_id]['#Locus'])[0]
                    MajorRNA = input_dir[sample]["results"][cluster_id]['MajorRNA']

                    block_accurate = bam_support_block(input_dir[sample]["bam"], contig, raw_start, raw_end, strand,
                                                       MajorRNA)

                    refseq = reference_genome_dict[contig].seqs

                    output_mistar = mistar_get(block_accurate[0], block_accurate[1] - block_accurate[0] + 1, refseq,
                                               strand, raw_start, raw_end, 300, mir_seq=MajorRNA)

                    if len(output_mistar) == 1:
                        # print(output_mistar, sample, cluster_id)
                        continue
                    else:
                        (mirkey_start, mirkey_end, mir_seq, mistar_start, mistar_end, mistar_seq) = output_mistar

                    if not (mirkey_start, mirkey_end) == block_accurate:
                        # print("Error2", sample, cluster_id)
                        continue
                    else:
                        input_dir[sample]["N15"][cluster_id] = (
                            cluster_id, contig, strand, mirkey_start, mirkey_end, mir_seq, mistar_start, mistar_end,
                            mistar_seq)

        # Load all sample de novo miRNA and merge them

        de_novo_dict = {}
        for sample in input_dir:
            for cluster_id in input_dir[sample]["de_novo"]:
                record_tuple = input_dir[sample]["de_novo"][cluster_id]
                if not record_tuple[1] in de_novo_dict: de_novo_dict[record_tuple[1]] = {"+": {}, "-": {}}
                index_miRNA = (sample, record_tuple[0])
                de_novo_dict[record_tuple[1]][record_tuple[2]][index_miRNA] = record_tuple

        good_miRNA = {}
        for contig in de_novo_dict:
            if contig not in good_miRNA: good_miRNA[contig] = {"+": [], "-": []}
            for strand in de_novo_dict[contig]:
                interval_finder_input = []
                for index_miRNA in de_novo_dict[contig][strand]:
                    interval_finder_input.append((index_miRNA, de_novo_dict[contig][strand][index_miRNA][3],
                                                  de_novo_dict[contig][strand][index_miRNA][4]))
                grouped_intervals = group_by_intervals(interval_finder_input, int=True)

                for group in grouped_intervals:
                    input_tmp = grouped_intervals[group]
                    uniq_miRNA = unique_miRNA_type(input_tmp, input_dir, contig, "de_novo")
                    for tmp_info in uniq_miRNA:
                        miRNA_info = [contig, strand] + [tmp_info[i] for i in (0, 1, 3, 4, 5, 7)]
                        good_miRNA[contig][strand].append(miRNA_info)

        # Load all sample N15 miRNA and del de novo one and merge them

        N15_dict = {}
        for sample in input_dir:
            if sample == "homo_SS":
                continue
            for cluster_id in input_dir[sample]["N15"]:
                record_tuple = input_dir[sample]["N15"][cluster_id]
                if not record_tuple[1] in N15_dict: N15_dict[record_tuple[1]] = {"+": {}, "-": {}}
                index_miRNA = (sample, record_tuple[0])
                N15_dict[record_tuple[1]][record_tuple[2]][index_miRNA] = record_tuple

        good_N15 = {}
        for contig in N15_dict:
            if contig not in good_N15: good_N15[contig] = {"+": [], "-": []}
            for strand in N15_dict[contig]:
                interval_finder_input = []
                for index_miRNA in N15_dict[contig][strand]:
                    interval_finder_input.append((index_miRNA, N15_dict[contig][strand][index_miRNA][3],
                                                  N15_dict[contig][strand][index_miRNA][4]))
                grouped_intervals = group_by_intervals(interval_finder_input, int=True)

                for group in grouped_intervals:
                    input_tmp = grouped_intervals[group]
                    uniq_miRNA = unique_miRNA_type(input_tmp, input_dir, contig, "N15")
                    for tmp_info in uniq_miRNA:
                        miRNA_info = [contig, strand] + [tmp_info[i] for i in (0, 1, 3, 4, 5, 7)]
                        de_novo_flag = 0
                        if contig in good_miRNA:
                            for good_miRNA_info in good_miRNA[contig][strand]:
                                a, b = section((good_miRNA_info[2], good_miRNA_info[3]), (miRNA_info[2], miRNA_info[3]))
                                if a:
                                    # print("Founded", miRNA_info)
                                    de_novo_flag = 1
                        if de_novo_flag == 0:
                            good_N15[contig][strand].append(miRNA_info)

        # Name miRNA

        temp_file = temp_dir + "/temp.fa"
        for contig in good_miRNA:
            for strand in good_miRNA[contig]:
                named_list = []
                for record in good_miRNA[contig][strand]:
                    miRNA_seq = record[4]
                    best_name = miRNA_name(miRNA_seq, mirbase_fasta, temp_file)
                    record.append(best_name)
                    # print(record)
                    named_list.append(record)
                good_miRNA[contig][strand] = named_list

        for contig in good_N15:
            for strand in good_N15[contig]:
                named_list = []
                for record in good_N15[contig][strand]:
                    miRNA_seq = record[4]
                    best_name = miRNA_name(miRNA_seq, mirbase_fasta, temp_file)
                    if best_name == "Unknown":
                        continue
                    record.append(best_name)
                    # print(record)
                    named_list.append(record)
                good_N15[contig][strand] = named_list

        # Count and rpmm

        sample_list = input_dir.keys()
        count_rpmm_dict = {}
        for contig in good_miRNA:
            for strand in good_miRNA[contig]:
                for record in good_miRNA[contig][strand]:
                    record.append("de_novo")
                    record = tuple(record)
                    count_rpmm_dict[record] = {}
                    start = record[2]
                    end = record[3]
                    seqs = record[4]
                    for i in sample_list:
                        bam_file = input_dir[i]['bam']
                        count, rpmm = bam_support(bam_file, contig, start, end, strand, seqs, True)
                        count_rpmm_dict[record][i] = (count, rpmm)

        for contig in good_N15:
            for strand in good_N15[contig]:
                for record in good_N15[contig][strand]:
                    record.append("N15")
                    record = tuple(record)
                    count_rpmm_dict[record] = {}
                    start = record[2]
                    end = record[3]
                    seqs = record[4]
                    for i in sample_list:
                        bam_file = input_dir[i]['bam']
                        count, rpmm = bam_support(bam_file, contig, start, end, strand, seqs, True)
                        count_rpmm_dict[record][i] = (count, rpmm)

        # output
        counts_file = output_prefix + ".counts.tsv"
        with open(counts_file, "w") as f:
            header = "contig\tstrand\tmiRNA_start\tmiRNA_end\tmiRNA_seq\tmistar_start\tmistar_end\tmistar_seq\tmiRNA_family\tsource\t"
            for i in sample_list:
                header = header + i + "\t"
            header = header.rstrip("\t")
            f.write(header + "\n")

            for record in count_rpmm_dict:
                printer = ""
                for i in record:
                    printer = printer + str(i) + "\t"

                for i in sample_list:
                    printer = printer + str(count_rpmm_dict[record][i][0]) + "\t"
                printer.rstrip("\t")

                f.write(printer + "\n")

        rpmm_file = output_prefix + ".rpmm.tsv"
        with open(rpmm_file, "w") as f:
            header = "contig\tstrand\tmiRNA_start\tmiRNA_end\tmiRNA_seq\tmistar_start\tmistar_end\tmistar_seq\tmiRNA_family\tsource\t"
            for i in sample_list:
                header = header + i + "\t"
            header = header.rstrip("\t")
            f.write(header + "\n")

            for record in count_rpmm_dict:
                printer = ""
                for i in record:
                    printer = printer + str(i) + "\t"

                for i in sample_list:
                    printer = printer + str(count_rpmm_dict[record][i][1]) + "\t"
                printer.rstrip("\t")

                f.write(printer + "\n")

    # test
    # 24nt_source
    elif args_dict["subcommand_name"] == "24nt_source":
        # Todo
        input_file_list = args.input_file_list
        reference_file = args.reference
        output_prefix = args.output_prefix
        mirbase_fasta = args.mirbase_fasta
        temp_dir = args.temp_dir

        # Read all information from SS

        """
        input_file_list = "/lustre/home/xuyuxing/Work/miRNA/Cau_two_assembly/ShortStack/Cau_map/merge/SS.list"
        """

        input_dir = tsv_file_dict_parse(input_file_list, seq=",", fieldnames=("key", "dir"), key_col="key",
                                        fields=["dir"])

        for sample in input_dir:
            dir_tmp = input_dir[sample]["dir"]
            for file in os.listdir(dir_tmp):
                if re.match(r'.*\.bam$', file):
                    input_dir[sample]["bam"] = os.path.join(dir_tmp, file)
                if file == "Results.txt":
                    file_path = os.path.join(dir_tmp, file)
                    input_dir[sample]["results"] = file_path


        def deep_analy(file_path, relate_threshold_reads_num=3, relate_threshold_complexity=0.98):
            import numpy as np
            """
            file_path = "/lustre/home/xuyuxing/Work/miRNA/Cau_two_assembly/ShortStack/Cau_map/de_novo_map/A2427.SS/Results.txt"
            relate_threshold_reads_num = 10
            relate_threshold_complexity= 0.6
            """
            reads_len = ["20", "21", "22", "23", "24"]
            result_dict = tsv_file_dict_parse(file_path, key_col="Name")
            total_sum_dict = {"DicerCall_reads_sum": {"20": 0, "21": 0, "22": 0, "23": 0, "24": 0}}

            for cluster_id in result_dict:
                # print(cluster_id)
                cluster_tmp = result_dict[cluster_id]

                DicerCall_reads = 0
                for i in reads_len:
                    DicerCall_reads = DicerCall_reads + int(cluster_tmp[i])
                    total_sum_dict["DicerCall_reads_sum"][i] = total_sum_dict["DicerCall_reads_sum"][i] + int(
                        cluster_tmp[i])
                result_dict[cluster_id]["DicerCall_reads"] = DicerCall_reads

                for i in reads_len:
                    if DicerCall_reads == 0:
                        ratio = 0.0
                    else:
                        ratio = float(cluster_tmp[i]) / float(DicerCall_reads)
                    result_dict[cluster_id][i + "_ratio"] = ratio

            total_sum_dict["DicerCall_length_ratio_his"] = {}
            for i in reads_len:
                ratio_list = [result_dict[cluster_id][i + "_ratio"] for cluster_id in result_dict]
                total_sum_dict["DicerCall_length_ratio_his"][i] = np.histogram(ratio_list, bins=np.arange(101) / 100)

            total_sum_dict["DicerCall_length_related_cluster"] = {}
            for i in reads_len:
                filterd_len_cluster = []
                for cluster_id in result_dict:
                    cluster_tmp = result_dict[cluster_id]
                    if cluster_tmp["DicerCall"] == i and int(cluster_tmp[i]) >= relate_threshold_reads_num and float(
                            cluster_tmp["Complexity"]) <= relate_threshold_complexity:
                        filterd_len_cluster.append(cluster_id)

                filterd_len_cluster_reads = 0
                for cluster_id in filterd_len_cluster:
                    filterd_len_cluster_reads = filterd_len_cluster_reads + int(result_dict[cluster_id][i])

                print(i, filterd_len_cluster_reads, total_sum_dict["DicerCall_reads_sum"][i],
                      filterd_len_cluster_reads / total_sum_dict["DicerCall_reads_sum"][i])

                total_sum_dict["DicerCall_length_related_cluster"][i] = filterd_len_cluster


        for i in [3, 5, 10, 15]:
            for j in [0.6, 0.8, 0.9, 0.95]:
                print(i, j)
                # deep_analy("/lustre/home/xuyuxing/Work/miRNA/Cau_two_assembly/ShortStack/Cau_map/de_novo_map/A2427.SS/Results.txt",i,j)
                deep_analy(
                    "/lustre/home/xuyuxing/Work/miRNA/Cau_pacbio_genome/ShortStack/2018/test_Ath/TEST_DATA/test1/Results.txt",
                    i, j)

        with open("temp.txt", "w") as f:
            for i in total_sum_dict["DicerCall_length_related_cluster"]["24"]:
                f.write(i + "\n")
