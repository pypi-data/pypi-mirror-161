from toolbiox.config import gene_painter_path, clustalw_path
import uuid
from toolbiox.lib.common.os import mkdir, rmdir, cmd_run
import os
from toolbiox.lib.common.genome.genome_feature2 import write_gff_file, sub_gf_traveler, mRNA_rename, sub_gf_traveler
import re
from itertools import combinations


def read_genepainter_intron_phase_file(intron_file):
    """
    I can just read genepainter-intron-phase.txt, gene names should not be too long and have '-'
    """

    intron_dict = {}

    with open(intron_file, 'r') as f:
        for each_line in f:
            each_line = each_line.strip()
            info = each_line.split()
            g_name = re.sub('>', '', info[0])
            intron_aln = []
            for i in range(1, len(info[1]), 2):
                intron_aln.append(info[1][i])
            intron_dict[g_name] = intron_aln

    return intron_dict


def intron_map(mRNA_list, intron_dict):
    intron_mapped_dict = {}

    for mRNA_gf in mRNA_list:
        intron_mapped_dict[mRNA_gf] = []
        mRNA_gf.get_introns()
        intron_list = [i for i in sub_gf_traveler(
            mRNA_gf) if i.type == 'intron']
        sorted_intron_list = sorted(
            intron_list, key=lambda x: x.start, reverse=(mRNA_gf.strand == '-'))

        num = 0
        for i in intron_dict[mRNA_gf.id]:
            if i == '-':
                intron_mapped_dict[mRNA_gf].append(None)
            else:
                intron = sorted_intron_list[num]
                intron.phase = i
                intron_mapped_dict[mRNA_gf].append(intron)
                num += 1

    return intron_mapped_dict


def intron_aligner(mRNA_list, top_work_dir="/tmp"):
    """
    mRNA in mRNA_list should fit the object from genome_feature2, mRNA should have aa_seq
    """

    top_work_dir = os.path.abspath(top_work_dir)

    work_dir = top_work_dir + "/" + uuid.uuid1().hex
    mkdir(work_dir)

    # gene rename
    rename_dict = {}

    num = 0
    mRNA_rename_list = []
    mRNA_only_cds_list = []
    for mRNA_gf in mRNA_list:
        new_id = 'g%d' % num
        rename_dict[new_id] = mRNA_gf.id
        cds_list = [i for i in sub_gf_traveler(mRNA_gf) if i.type == 'CDS']
        mRNA_gf.sub_features = cds_list

        mRNA_only_cds_list.append(mRNA_gf)
        mRNA_gf = mRNA_rename(mRNA_gf, new_id)
        mRNA_rename_list.append(mRNA_gf)
        num += 1

    # write aa fasta
    aa_fasta_file = work_dir + "/aa.fasta"
    with open(aa_fasta_file, 'w') as f:
        for mRNA_gf in mRNA_rename_list:
            f.write(">%s\n%s\n" % (mRNA_gf.id, mRNA_gf.aa_seq))

    # running clustalw2 to get aln
    aa_aln_file = work_dir + "/aa.aln"
    cmd_string = "%s -INFILE=%s -ALIGN -OUTPUT=FASTA -OUTFILE=%s -type=protein" % (
        clustalw_path, aa_fasta_file, aa_aln_file)
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    # prepare gff dir
    gff_dir = work_dir + "/gff"
    mkdir(gff_dir)

    for mRNA_gf in mRNA_rename_list:
        write_gff_file([mRNA_gf], gff_dir+"/"+mRNA_gf.id +
                       ".gff3", source=None, sort=False)

    # run  gene_painter
    cmd_string = "%s -i aa.aln -p gff --intron-phase" % gene_painter_path
    cmd_run(cmd_string, silence=True, cwd=work_dir)

    intron_phase_file = work_dir + "/genepainter-intron-phase.txt"

    # parse intron phase
    intron_dict = read_genepainter_intron_phase_file(intron_phase_file)

    rename_intron_dict = {}
    for i in intron_dict:
        rename_intron_dict[rename_dict[i]] = intron_dict[i]

    mapped_intron_dict = intron_map(mRNA_only_cds_list, rename_intron_dict)

    rmdir(work_dir)

    return mapped_intron_dict


def intron_length_diverse_index(intron_dict_from_intron_aligner):
    """
    key: gene_gf
    value: aligned intron gf
    """
    output_dict = {}
    for a, b in combinations(list(intron_dict_from_intron_aligner.keys()), 2):
        a_intron_list = intron_dict_from_intron_aligner[a]
        b_intron_list = intron_dict_from_intron_aligner[b]

        if len(a_intron_list) != len(b_intron_list):
            raise ValueError('intron list should aligned')
        elif len(a_intron_list) == 0:
            return 1.0
        else:
            intron_diverse_value_list = []
            for i in range(len(a_intron_list)):
                ai = a_intron_list[i]
                bi = b_intron_list[i]

                if ai is None and bi is not None:
                    intron_diverse_value = 0.0
                elif not ai is None and bi is None:
                    intron_diverse_value = 0.0
                elif ai is None and bi is None:
                    continue
                else:
                    intron_diverse_value = min(
                        ai.len(), bi.len())/max(ai.len(), bi.len())

                intron_diverse_value_list.append(intron_diverse_value)

            weigthed_intron_diverse_value = sum(
                intron_diverse_value_list)/len(intron_diverse_value_list)

            output_dict[(a, b)] = weigthed_intron_diverse_value
    
    return output_dict


if __name__ == "__main__":
    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, mRNA
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx

    Aof_gff_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Asparagus_officinalis/T4686N0.genome.gff3'
    Aof_gff_dict = read_gff_file(Aof_gff_file)
    Aof_gene_dict = Aof_gff_dict['gene']

    Aof_aa_fasta_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Asparagus_officinalis/T4686N0.gene_model.protein.fasta'
    Aof_aa_dict = read_fasta_by_faidx(Aof_aa_fasta_file)

    mRNA1 = mRNA(from_gf=Aof_gene_dict['T4686N0C00001G02624'].sub_features[0])
    mRNA2 = mRNA(from_gf=Aof_gene_dict['T4686N0C00003G01631'].sub_features[0])

    mRNA1.aa_seq = Aof_aa_dict['T4686N0C00001G02624'].seq
    mRNA2.aa_seq = Aof_aa_dict['T4686N0C00003G01631'].seq

    mRNA_list = [mRNA1, mRNA2]
    top_work_dir = '/lustre/home/xuyuxing/Work/Gel/synteny/20210311/orthofinder/pt_file/OrthoFinder/Results_Jun23/MultipleSequenceAlignments/test'
    intron_dict = intron_aligner(mRNA_list, top_work_dir)

    #
    from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
    from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, mRNA
    from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx

    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'
    OG_tsv_file = '/lustre/home/xuyuxing/Work/Gel/intron/orthofinder/pt_file/OrthoFinder/Results_Jun27/Orthogroups/Orthogroups.tsv'
    work_dir = '/lustre/home/xuyuxing/Work/Gel/intron/'

    sp_info_dict = read_species_info(ref_xlsx)

    all_data_dict = {}
    for sp_id in sp_info_dict:
        sp = sp_info_dict[sp_id]

        gff_dict = read_gff_file(sp.gff_file)
        gene_dict = gff_dict['gene']

        aa_dict = read_fasta_by_faidx(sp.pt_file)
        cds_dict = read_fasta_by_faidx(sp.cds_file)

        mRNA_dict = {}
        for g_id in gene_dict:
            gf = gene_dict[g_id]
            if g_id in aa_dict:
                mRNA_gf = mRNA(from_gf=gf.sub_features[0], aa_seq=aa_dict[g_id].seq, cds_seq=cds_dict[g_id].seq)
                mRNA_dict[mRNA_gf.id] = mRNA_gf
            
        all_data_dict[sp_id] = mRNA_dict

    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file)
    aln_work_dir = work_dir + "/intron_aln"
    mkdir(aln_work_dir, True)

    og_id = 'OG0009838'
    work_dir_now = aln_work_dir + "/" + og_id
    mkdir(work_dir_now, True)
    og = OGs.OG_dict[og_id]

    mRNA_list = []
    for gene in og.gene_list:
        mRNA_list.append(all_data_dict[gene.species][gene.id])

    intron_aligner(mRNA_list, top_work_dir=work_dir_now)    
       
        


