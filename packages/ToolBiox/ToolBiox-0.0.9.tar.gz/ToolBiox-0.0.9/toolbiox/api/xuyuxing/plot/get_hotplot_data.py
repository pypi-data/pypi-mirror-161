import sys

sys.path.append("/lustre/home/xuyuxing/python_project/Genome_work_tools/")
import re

raw_tab_dir = "/lustre/home/xuyuxing/Work/Other/Pseudouracil/raw_tab/"

output_col_1 = ["Gene_id", "site"]
output_col_2 = ["S02_S01", "S06_S05", "S10_S26", "S25_S09", "S04_S03", "S08_S07", "S12_S11", "S28_S27"]
output_col_3 = ["S02", "S01", "S06", "S05", "S10", "S26", "S25", "S09", "S04", "S03", "S08", "S07", "S12", "S11", "S28",
                "S27"]

gene_dir = {
    "Chr2_18S": ('Chr2', 3706, 5781, '+'),
    "Chr2_5.5S": ('Chr2', 5782, 6133, '+'),
    "Chr2_25S": ('Chr2', 6134, 9608, '+'),
    "Chr3_18S": ('Chr3', 14197677, 14199752, '+'),
    "Chr3_5.5S": ('Chr3', 14199753, 14200104, '+'),
    "Chr3_25S": ('Chr3', 14200105, 14203579, '+')
}

coverage_dir = {}
for i in output_col_3:
    file_name = raw_tab_dir + i + ".tab"
    mapped_read_num = 0
    with open(file_name, 'r') as f:
        for each_line in f:
            each_line = re.sub('\n', '', each_line)
            line_data = re.split('\t', each_line)
            line_chr = line_data[0]
            line_site = int(line_data[1])
            line_p_e = int(line_data[2])
            line_p_p = int(line_data[3])
            line_n_e = int(line_data[4])
            line_n_p = int(line_data[5])
            mapped_read_num = mapped_read_num + line_p_e + line_n_e
            for gene_id in gene_dir:
                gene_info = gene_dir[gene_id]
                gene_chr = gene_info[0]
                gene_s = gene_info[1]
                gene_e = gene_info[2]
                gene_strand = gene_info[3]
                if line_chr == gene_chr:
                    if line_site in list(range(gene_s, gene_e)):
                        if gene_strand == "+":
                            coverage = line_p_e
                        else:
                            coverage = line_n_e
                        if not gene_id in coverage_dir:
                            coverage_dir[gene_id] = {}
                        if not i in coverage_dir[gene_id]:
                            coverage_dir[gene_id][i] = {}
                        coverage_dir[gene_id][i][line_site] = coverage
    print(i, mapped_read_num)
    for gene_id in coverage_dir:
        for site in coverage_dir[gene_id][i]:
            coverage_dir[gene_id][i][site] = coverage_dir[gene_id][i][site] * 1000000 / mapped_read_num

tran_dir = '/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/'

peak_dir = {}
for i in output_col_2:
    file_name = tran_dir + i + ".all_transcript.tab"
    with open(file_name, 'r') as f:
        for each_line in f:
            each_line = re.sub('\n', '', each_line)
            line_data = re.split('\t', each_line)
            line_chr = line_data[0]
            line_gene_id = line_data[1]
            line_site = int(line_data[2])
            line_peak_p = float(line_data[3])
            line_peak_n = float(line_data[4])
            for gene_id in gene_dir:
                gene_info = gene_dir[gene_id]
                gene_chr = gene_info[0]
                gene_s = gene_info[1]
                gene_e = gene_info[2]
                gene_strand = gene_info[3]
                if line_chr == gene_chr:
                    if line_site in list(range(gene_s, gene_e)):
                        peak = line_peak_p
                        if not gene_id in peak_dir:
                            peak_dir[gene_id] = {}
                        if not i in peak_dir[gene_id]:
                            peak_dir[gene_id][i] = {}
                        peak_dir[gene_id][i][line_site] = peak
    print(i)

with open("output.txt", 'w') as f:
    for gene_id in gene_dir:
        gene_chr, gene_s, gene_e, gene_strand = gene_dir[gene_id]
        for i in range(gene_s, gene_e + 1):
            printer = gene_id + "\t" + str(i) + "\t"
            for j in output_col_2:
                if i in peak_dir[gene_id][j]:
                    printer = printer + str(peak_dir[gene_id][j][i]) + "\t"
                else:
                    printer = printer + "0.0\t"
            for j in output_col_3:
                if i in coverage_dir[gene_id][j]:
                    printer = printer + str(coverage_dir[gene_id][j][i]) + "\t"
                else:
                    printer = printer + "0.0\t"
            printer.rstrip("\t")
            f.write(printer + "\n")
