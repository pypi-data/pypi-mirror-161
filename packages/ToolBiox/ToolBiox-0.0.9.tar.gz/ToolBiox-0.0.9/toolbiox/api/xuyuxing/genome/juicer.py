import re
from collections import OrderedDict
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, FastaRecord, write_fasta


def read_assembly(assembly_file):
    """
    assembly_file = '/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/Gel.genome.v1.0.final.assembly'
    """

    contig_dict = OrderedDict()
    scaffold_dict = OrderedDict()
    scaf_id = 0
    with open(assembly_file, 'r') as f:
        for each_line in f:
            each_line = each_line.strip()
            matchObj = re.match('^>(\S+) (\d+) (\d+)$', each_line)
            if matchObj:
                contig_name, ID_num, contig_length = matchObj.groups()

                contig_name = re.sub(r':::debris', '', contig_name)
                contig_name = re.sub(r':::', '_', contig_name)

                contig_dict[ID_num] = (contig_name, ID_num, contig_length)
            else:
                scaf_info = each_line.split()

                scaf_contig_id_list = []
                scaf_contig_length_list = []
                scaf_contig_strand_list = []
                for contig_id in scaf_info:
                    if '-' in contig_id:
                        scaf_contig_strand_list.append('-')
                    else:
                        scaf_contig_strand_list.append('+')
                    contig_id = re.sub(r'-', '', contig_id)
                    scaf_contig_id_list.append(contig_dict[contig_id][0])
                    scaf_contig_length_list.append(
                        int(contig_dict[contig_id][2]))

                scaffold_dict['scaf_%d' % scaf_id] = {
                    "contig_list": scaf_contig_id_list,
                    "contig_length": scaf_contig_length_list,
                    "contig_strand": scaf_contig_strand_list
                }
                scaf_id += 1

    return scaffold_dict


def write_assembly(scaffold_dict, assembly_file):
    """
    scaffold_dict['scaf_%d' % scaf_id] = {
        "contig_list": scaf_contig_id_list,
        "contig_length": scaf_contig_length_list,
        "contig_strand": scaf_contig_strand_list
    }  
    """

    contig_id_dict = {}
    contig_len_dict = {}
    contig_strand_dict = {}
    num = 1
    for i in scaffold_dict:
        for c_id, length, strand in zip(scaffold_dict[i]['contig_list'], scaffold_dict[i]['contig_length'], scaffold_dict[i]['contig_strand']):
            contig_id_dict[c_id] = num
            contig_len_dict[c_id] = length
            contig_strand_dict[c_id] = strand
            num += 1

    with open(assembly_file, 'w') as f:
        for i in contig_id_dict:
            f.write(">%s %d %d\n" % (i, contig_id_dict[i], contig_len_dict[i]))

        for i in scaffold_dict:
            print_list = []
            for c_id in scaffold_dict[i]['contig_list']:
                if contig_strand_dict[c_id] == '-':
                    print_list.append('-'+str(contig_id_dict[c_id]))
                else:
                    print_list.append(str(contig_id_dict[c_id]))

            f.write(" ".join(print_list)+"\n")


def assembly_to_fasta(contig_fasta, assembly_file, output_fasta):
    scaffold_dict = read_assembly(assembly_file)
    contig_fasta_dict = read_fasta_by_faidx(contig_fasta)

    num = 0
    fasta_record_list = []
    for i in scaffold_dict:

        scaffold_name = "HiC_scaffold_%d" % num
        scaffold_seq = ""

        for c_id, length, strand in zip(scaffold_dict[i]['contig_list'], scaffold_dict[i]['contig_length'], scaffold_dict[i]['contig_strand']):
            c_rec = contig_fasta_dict[c_id]
            if strand == '-':
                c_seq = c_rec.reverse_complement()
            else:
                c_seq = c_rec.seq

            if not scaffold_seq == "":
                scaffold_seq = scaffold_seq + "N" * 500

            scaffold_seq = scaffold_seq + c_seq

        fasta_record_list.append(FastaRecord(
            seqname=scaffold_name, seq=scaffold_seq))

        num += 1

    write_fasta(fasta_record_list, output_fasta, wrap_length=75, upper=True)
