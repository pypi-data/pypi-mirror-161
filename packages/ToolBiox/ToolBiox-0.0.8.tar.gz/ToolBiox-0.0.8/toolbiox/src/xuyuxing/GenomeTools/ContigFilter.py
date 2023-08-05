import re
import os
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.api.common.genome.blast import outfmt5_read
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.math.interval import merge_intervals
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.os import mkdir, cmd_run
from toolbiox.config import taxon_nr_db, taxon_dump
from toolbiox.src.xuyuxing.tools.seqtools import FragmentGenome_main
from toolbiox.src.xuyuxing.tools.taxontools import DiamondTaxonAssign_main
from toolbiox.src.xuyuxing.GenomeTools.ContaminationFilter import ContaminationFilter_main


class args_tmp():
    pass    


script_dir_path = os.path.split(os.path.realpath(__file__))[0]

ath_chl_aa = script_dir_path+"/organelle/Ath/Ath.chl.aa.fasta"
ath_chl_rRNA = script_dir_path+"/organelle/Ath/Ath.chl.rRNA.fasta"
osa_chl_aa = script_dir_path+"/organelle/Osa/Osa.chl.aa.fasta"
osa_chl_rRNA = script_dir_path+"/organelle/Osa/Osa.chl.rRNA.fasta"

ath_mit_aa = script_dir_path+"/organelle/Ath/Ath.mit.aa.fasta"
ath_mit_rRNA = script_dir_path+"/organelle/Ath/Ath.mit.rRNA.fasta"
osa_mit_aa = script_dir_path+"/organelle/Osa/Osa.mit.aa.fasta"
osa_mit_rRNA = script_dir_path+"/organelle/Osa/Osa.mit.rRNA.fasta"

ath_nucl_rRNA = script_dir_path+"/Ath_rRNA/rRNA.gene.fa"

ref_seq = {
    'chl': {
        'rRNA': {
            'Ath': ath_chl_rRNA,
            'Osa': osa_chl_rRNA,
        },
        'aa': {
            'Ath': ath_chl_aa,
            'Osa': osa_chl_aa,
        },
    },
    'mit': {
        'rRNA': {
            'Ath': ath_mit_rRNA,
            'Osa': osa_mit_rRNA,
        },
        'aa': {
            'Ath': ath_mit_aa,
            'Osa': osa_mit_aa,
        },
    },
    'nuc': {
        'rRNA': {
            'Ath': ath_nucl_rRNA,
        }
    },
}


def get_contamination_report(genome_fasta, work_dir, threads=56, max_target_seqs=50):
    mkdir(work_dir, True)

    split_genome_fasta = work_dir + "/split.genome.fasta"
    diamond_output = work_dir + "/nr.diamond.bls"
    taxon_assign_output = work_dir + "/nr.diamond.taxon"
    contamination_report = work_dir + "/contamination_report.txt"

    # FragmentGenome
    args = args_tmp()
    args.genome_file = genome_fasta
    args.output_file = split_genome_fasta
    args.step = 10000
    args.length = 10000
    args.shift_start = 0
    args.Consider_scaffold = True
    args.entropy_threshold = 3

    FragmentGenome_main(args)

    # diamond
    cmd_string = "diamond blastx --query %s --max-target-seqs %d --db %s --evalue 1e-5 --out %s --outfmt 6 qseqid sseqid staxids pident length mismatch gapopen qstart qend sstart send evalue bitscore --threads %s" % (
        split_genome_fasta,
        max_target_seqs,
        taxon_nr_db,
        diamond_output,
        threads
    )
    cmd_run(cmd_string, None, 1, True)

    # DiamondTaxonAssign
    args = args_tmp()
    args.blast_results = diamond_output
    args.tax_dir = taxon_dump
    args.num_threads = threads
    args.output_file = taxon_assign_output

    DiamondTaxonAssign_main(args)

    # ContaminationFilter
    args = args_tmp()
    args.split_genome_fasta = split_genome_fasta
    args.taxon_assign_output = taxon_assign_output
    args.tax_dir = taxon_dump
    args.output_file = taxon_assign_output

    ContaminationFilter_main(args)


def read_assembly(assembly_file):
    """
    assembly_file = '/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/Gel.genome.v1.0.final.assembly'
    """

    contig_dict = {}
    scaffold_dict = {}
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
                scaf_contig_length_sum = 0
                for contig_id in scaf_info:
                    contig_id = re.sub(r'-', '', contig_id)
                    scaf_contig_id_list.append(contig_dict[contig_id][0])
                    scaf_contig_length_sum += int(contig_dict[contig_id][2])

                scaffold_dict['scaf_%d' % scaf_id] = {
                    "contig_list": scaf_contig_id_list,
                    "contig_length": scaf_contig_length_sum
                }
                scaf_id += 1

    return scaffold_dict


def filter_polt():
    pass

    """
    % matplotlib inline
    import matplotlib
    import numpy as np
    import matplotlib.pyplot as plt

    avg_depth_list = [float(genome_depth_dict[i]['avg_depth']) for i in genome_depth_dict]

    from toolbiox.lib.common.fileIO import tsv_file_dict_parse
    from toolbiox.api.common.genome.blast import outfmt6_read

    org_bls_dict = outfmt6_read(args.organelle_blast)

    genome_depth_dict = tsv_file_dict_parse(args.genome_seq_depth)

    avg_depth_list = [float(genome_depth_dict[i]['avg_depth']) for i in genome_depth_dict]

    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.patches as patches
    import matplotlib.path as path

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Fixing random state for reproducibility
    # np.random.seed(19680801)

    # histogram our data with numpy
    # data = np.random.randn(1000)
    n, bins = np.histogram(avg_depth_list, bins='auto')

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n
    nrects = len(left)

    nverts = nrects * (1 + 3 + 1)
    verts = np.zeros((nverts, 2))
    codes = np.ones(nverts, int) * path.Path.LINETO
    codes[0::5] = path.Path.MOVETO
    codes[4::5] = path.Path.CLOSEPOLY
    verts[0::5, 0] = left
    verts[0::5, 1] = bottom
    verts[1::5, 0] = left
    verts[1::5, 1] = top
    verts[2::5, 0] = right
    verts[2::5, 1] = top
    verts[3::5, 0] = right
    verts[3::5, 1] = bottom

    barpath = path.Path(verts, codes)
    # patch = patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)
    patch = patches.PathPatch(barpath, facecolor='blue', edgecolor="blue", linewidth=0.0)
    ax.add_patch(patch)

    ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())

    plt.show()"""


def ContigFilter_main(args):

    genome_fasta = read_fasta_by_faidx(args.genome_file)
    contig_list = list(genome_fasta.keys())

    # GSS depth
    info_dict = tsv_file_dict_parse(args.genome_seq_depth)
    genome_depth_dict = {}

    for i in info_dict:
        genome_depth_dict[info_dict[i]['contig']
                          ] = float(info_dict[i]['avg_depth'])

    # GC ratio
    gc_dict = {}
    for contig_id in contig_list:
        gc_now = (genome_fasta[contig_id].seq.count('C') + genome_fasta[contig_id].seq.count('G') +
                  genome_fasta[contig_id].seq.count('c') + genome_fasta[contig_id].seq.count('g'))/genome_fasta[contig_id].len()
        gc_dict[contig_id] = gc_now

    # Contig in Hi-C scaffold
    scaffold_dict = read_assembly(args.hic_assembly)
    contig_in_huge_scaffold = []
    for scaf_id in scaffold_dict:
        if scaffold_dict[scaf_id]['contig_length'] > 1000000:
            contig_in_huge_scaffold.extend(
                scaffold_dict[scaf_id]['contig_list'])

    # rRNA hit
    rRNA_bls_dict = outfmt5_read(args.rRNA_blast)

    rRNA_identity_dict = {}

    for query_id in ['18S', '25S']:
        rRNA_identity_dict[query_id] = {}
        query_record = rRNA_bls_dict[query_id]
        for hit_record in query_record.hit:
            hit_max_identity = 0
            for hsp_record in hit_record.hsp:
                identity = hsp_record.Hsp_identity / int(query_record.qLen)
                if identity > hit_max_identity:
                    hit_max_identity = identity
            rRNA_identity_dict[query_id][hit_record.Hit_def] = hit_max_identity

    contig_rRNA_ident_dict = {}
    for contig_id in contig_list:
        info_tuple = []
        for rRNA_id in ['18S', '25S']:
            if contig_id in rRNA_identity_dict[rRNA_id]:
                info_tuple.append(rRNA_identity_dict[rRNA_id][contig_id])
            else:
                info_tuple.append(0.0)
        contig_rRNA_ident_dict[contig_id] = tuple(info_tuple)

    # Organelle
    org_bls_dict = outfmt5_read(args.organelle_blast)

    subject_contig_dict = {}
    for query_id in org_bls_dict:
        query_record = org_bls_dict[query_id]
        for hit_record in query_record.hit:
            if hit_record.Hit_def not in subject_contig_dict:
                subject_contig_dict[hit_record.Hit_def] = {
                    "all_range": [],
                    "hit_list": [],
                    "contig_length": 0
                }
            for hsp_record in hit_record.hsp:
                subject_contig_dict[hit_record.Hit_def]["all_range"].append(
                    (hsp_record.Hsp_hit_from, hsp_record.Hsp_hit_to))
            subject_contig_dict[hit_record.Hit_def]["hit_list"].append(
                hit_record)
            subject_contig_dict[hit_record.Hit_def]["contig_length"] = int(
                hit_record.Hit_len)
            subject_contig_dict[hit_record.Hit_def]["contig_ratio"] = int(
                hit_record.Hit_len)

    for contig in subject_contig_dict:
        subject_contig_dict[contig]["all_range"] = merge_intervals(
            subject_contig_dict[contig]["all_range"], True)
        subject_range_length = 0
        for i in subject_contig_dict[contig]["all_range"]:
            subject_range_length += max(i) - min(i) + 1
        subject_contig_dict[contig]["subject_range_length"] = subject_range_length
        subject_contig_dict[contig]["contig_ratio"] = subject_range_length / subject_contig_dict[contig][
            "contig_length"]

        subject_contig_dict[contig]["query_info"] = {}
        for hit_record in subject_contig_dict[contig]["hit_list"]:
            query_range = []
            for hsp_record in hit_record.hsp:
                query_range.append(
                    (hsp_record.Hsp_query_from, hsp_record.Hsp_query_to))
            query_range = merge_intervals(query_range)

            range_length = 0
            for i in query_range:
                range_length += max(i) - min(i) + 1

            short_qDef = re.search('^(\S+)', hit_record.query.qDef).group(1)
            subject_contig_dict[contig]["query_info"][short_qDef] = {
                'query_range': query_range,
                'query_length': int(hit_record.query.qLen),
                'query_range_length': int(range_length),
                'query_ratio': int(range_length) / int(hit_record.query.qLen),
            }

    organelle_judge_dict = {}
    organelle_query_info = {}

    for contig_id in contig_list:
        if contig_id in subject_contig_dict and subject_contig_dict[contig_id]['contig_length'] < 1000000 and subject_contig_dict[contig_id]["contig_ratio"] > 0.5 and not (contig_id in contig_in_huge_scaffold) and genome_depth_dict[contig_id] > 100:
            organelle_judge_dict[contig_id] = True

            query_info = []
            query_id_list = sorted(subject_contig_dict[contig_id]['query_info'],
                                   key=lambda x: subject_contig_dict[contig_id]['query_info'][x]['query_ratio'],
                                   reverse=True)

            for query_id in query_id_list:
                query_length = subject_contig_dict[contig_id]['query_info'][query_id]["query_length"]
                query_range_length = subject_contig_dict[contig_id]['query_info'][query_id][
                    "query_range_length"]
                query_ratio = subject_contig_dict[contig_id]['query_info'][query_id]["query_ratio"]
                string_tmp = "%s:%d/%d(%.2f)" % (query_id,
                                                 query_range_length, query_length, query_ratio)
                query_info.append(string_tmp)

            query_info_str = printer_list(query_info, sep=",")

            organelle_query_info[contig_id] = query_info_str

        else:
            organelle_judge_dict[contig_id] = False

    # Contamination hit

    # note

        # is a organelle

    # write report
    with open(args.output_file, 'w') as f:
        header_list = ["Contig_id", "Contig_length", "GSS_depth", "GC_content",
                       "In_HiC_huge_scaf", "Organelle_hit", "nrRNA_hit", "Contamination_hit", "Note"]
        header_str = printer_list(header_list, sep='\t')
        f.write(header_str + "\n")

        for contig_id in contig_list:
            info_list = [contig_id, genome_fasta[contig_id].len(),
                         genome_depth_dict[contig_id], gc_dict[contig_id], (contig_id in contig_in_huge_scaffold)]
            if contig_id not in subject_contig_dict:
                info_list = [contig_id,
                             genome_fasta[contig_id].len(),
                             "0", "0", str(
                                 contig_id in contig_in_huge_scaffold),
                             genome_depth_dict[contig_id], "False", ""
                             ]
                info_str = printer_list(info_list, sep='\t')
                f.write(info_str + "\n")
            else:
                info_list = [contig_id,
                             subject_contig_dict[contig_id]['contig_length'],
                             subject_contig_dict[contig_id]['subject_range_length'],
                             "%.2f" % subject_contig_dict[contig_id]["contig_ratio"],
                             str(contig_id in contig_in_huge_scaffold),
                             genome_depth_dict[contig_id]
                             ]

                query_info = []
                query_id_list = sorted(subject_contig_dict[contig_id]['query_info'],
                                       key=lambda x: subject_contig_dict[contig_id]['query_info'][x]['query_ratio'],
                                       reverse=True)

                for query_id in query_id_list:
                    query_length = subject_contig_dict[contig_id]['query_info'][query_id]["query_length"]
                    query_range_length = subject_contig_dict[contig_id]['query_info'][query_id][
                        "query_range_length"]
                    query_ratio = subject_contig_dict[contig_id]['query_info'][query_id]["query_ratio"]
                    string_tmp = "%s:%d/%d(%.2f)" % (query_id,
                                                     query_range_length, query_length, query_ratio)
                    query_info.append(string_tmp)

                query_info_str = printer_list(query_info, sep=",")

                if subject_contig_dict[contig_id]['contig_length'] < 1000000 and subject_contig_dict[contig_id][
                        "contig_ratio"] > 0.5 and not (contig_id in contig_in_huge_scaffold) and genome_depth_dict[
                        contig_id] > 100:
                    info_list.append('True')
                else:
                    info_list.append('False')

                info_list.append(query_info_str)

                info_str = printer_list(info_list, sep='\t')

                f.write(info_str + "\n")


if __name__ == "__main__":
    class abc(object):
        pass

    args = abc()

    args.genome_file = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/nextpolish2_canu.final.rename.fasta"
    args.hic_assembly = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/Llv.reviewed.rename.assembly"
    args.genome_seq_depth = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/Llv.GSS.depth"
    args.contamination_results = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/contamination_report.txt"
    args.output_dir = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/hic_canu/filter/Llv"

    ContigFilter_main(args)
