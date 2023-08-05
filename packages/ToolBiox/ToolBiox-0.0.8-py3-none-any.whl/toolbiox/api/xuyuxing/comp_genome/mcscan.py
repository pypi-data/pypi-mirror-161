from toolbiox.lib.common.genome.genome_feature2 import Gene, read_gff_file
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx, write_fasta
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.os import mkdir, cmd_run
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import re
from toolbiox.api.xuyuxing.comp_genome.orthofinder import OG_tsv_file_parse
from interlap import InterLap
from toolbiox.lib.common.math.set import merge_same_element_set
from toolbiox.lib.common.math.interval import section, merge_intervals
from collections import OrderedDict
from toolbiox.api.xuyuxing.comp_genome.orthofinder import tsv_to_gene_pair
import numpy as np
from toolbiox.api.common.genome.blast import outfmt6_read_big
from toolbiox.api.xuyuxing.plot.geneplot import add_box
import matplotlib.pyplot as plt

# running mcscanx


def get_chr_rename_map(chr_list, prefix):
    num = 1
    rename_map = {}
    rename_map_hash = {}
    for i in chr_list:
        num += 1
        rename_map[i] = prefix + str(num)
        rename_map_hash[prefix + str(num)] = i

    return rename_map, rename_map_hash


def write_mcscanx_gff(gf_dict, chr_rename_map, output_gff):
    with open(output_gff, 'w') as f:
        for gf_id in gf_dict:
            gf = gf_dict[gf_id]
            f.write("%s\t%s\t%d\t%d\n" %
                    (chr_rename_map[gf.chr_id], gf.id, gf.start, gf.end))


def blast_c_score_filter(blast_file, output_blast_file, c_score_threshold=0.5):
    """
    c_score=0.5 indicating their BLASTP bit-scores were below 50% of the bit-scores of the best matches
    only outfmt6
    """
    with open(output_blast_file, 'w') as f:
        for q_record in outfmt6_read_big(blast_file):
            best_bit_score = q_record.hit[0].hsp[0].Hsp_bit_score
            keep_hit = []
            for hit_tmp in q_record.hit:
                now_bit_score = hit_tmp.hsp[0].Hsp_bit_score
                c_score = now_bit_score / best_bit_score

                if c_score >= c_score_threshold:
                    keep_hit.append(hit_tmp)

            for hit_tmp in keep_hit:
                q_id = hit_tmp.query.qDef
                s_id = hit_tmp.Hit_def
                for hsp_tmp in hit_tmp.hsp:
                    identity = hsp_tmp.Hsp_identity
                    aln_len = hsp_tmp.Hsp_align_len
                    mis = hsp_tmp.Hsp_mismatch
                    gap = hsp_tmp.Hsp_gaps
                    q_start = hsp_tmp.Hsp_query_from
                    q_end = hsp_tmp.Hsp_query_to
                    s_start = hsp_tmp.Hsp_hit_from
                    s_end = hsp_tmp.Hsp_hit_to
                    e_value = hsp_tmp.Hsp_evalue
                    score = hsp_tmp.Hsp_bit_score

                prt = printer_list([q_id, s_id, identity, aln_len, mis,
                                    gap, q_start, q_end, s_start, s_end, e_value, score])
                f.write(prt+"\n")


def running_mcscanx(species1_gff3, species2_gff3, work_dir, species1_prefix='aa', species1_aa_fasta=None, species2_prefix='bb', species2_aa_fasta=None, skip_gene_list=[], give_bls_file=None, mcscanx_options='-k 50 -g -1 -s 5 -e 1e-05 -m 25 -a', c_score_threshold=0.5):
    # prepare gff file
    mkdir(work_dir, True)

    sp1_gff_dict = read_gff_file(species1_gff3)
    sp1_gf_dict = {}
    for gf_type in sp1_gff_dict:
        for i in sp1_gff_dict[gf_type]:
            if i not in skip_gene_list:
                sp1_gf_dict[i] = sp1_gff_dict[gf_type][i]

    sp2_gf_dict = {}
    if species2_gff3:
        sp2_gff_dict = read_gff_file(species2_gff3)
        for gf_type in sp2_gff_dict:
            for i in sp2_gff_dict[gf_type]:
                if i not in skip_gene_list:
                    sp2_gf_dict[i] = sp2_gff_dict[gf_type][i]

    sp1_chr_list = list(
        set([sp1_gf_dict[gf_id].chr_id for gf_id in sp1_gf_dict]))
    sp1_chr_map, sp1_chr_map_hash = get_chr_rename_map(
        sp1_chr_list, species1_prefix)

    sp2_chr_list = list(
        set([sp2_gf_dict[gf_id].chr_id for gf_id in sp2_gf_dict]))
    sp2_chr_map, sp2_chr_map_hash = get_chr_rename_map(
        sp2_chr_list, species2_prefix)

    merge_chr_map = merge_dict([sp1_chr_map, sp2_chr_map], extend_value=False)
    merge_gf_dict = merge_dict([sp1_gf_dict, sp2_gf_dict], extend_value=False)

    mcscanx_gff = work_dir + "/mcscanx.gff"
    write_mcscanx_gff(merge_gf_dict, merge_chr_map, mcscanx_gff)

    # prepare fasta file
    if give_bls_file is not None:
        bls_flag = True
    elif species1_aa_fasta is None:
        raise ValueError("Must have fasta or bls results!")
    else:
        bls_flag = False

    bls_raw_file = work_dir + "/raw_blast.bls"
    bls_file = work_dir + "/mcscanx.blast"

    if bls_flag:
        cmd_string = "cp %s %s" % (give_bls_file, bls_file)
        cmd_run(cmd_string)
    else:
        fasta_file = work_dir + "/mcscanx.fasta"
        sp1_aa_dict = read_fasta_by_faidx(species1_aa_fasta)
        sp2_aa_dict = {}
        if species2_aa_fasta:
            sp2_aa_dict = read_fasta_by_faidx(species2_aa_fasta)
        aa_dict = merge_dict([sp1_aa_dict, sp2_aa_dict], False)
        aa_list = [aa_dict[i] for i in aa_dict if i not in skip_gene_list]
        write_fasta(aa_list, fasta_file)

        cmd_string = "makeblastdb -in %s -dbtype prot" % fasta_file
        cmd_run(cmd_string)

        cmd_string = "blastp -query %s -db %s -out %s -outfmt 6 -evalue 1e-10 -num_threads 56" % (
            fasta_file, fasta_file, bls_raw_file)
        cmd_run(cmd_string)

        blast_c_score_filter(bls_raw_file, bls_file,
                             c_score_threshold=c_score_threshold)

    # run mcscanx
    cmd_string = "MCScanX mcscanx " + mcscanx_options
    cmd_run(cmd_string, cwd=work_dir)

    # write map file
    sp1_map_file = work_dir + "/" + species1_prefix + ".map"

    with open(sp1_map_file, 'w') as f:
        for i in sp1_chr_map:
            f.write("%s\t%s\n" % (i, sp1_chr_map[i]))

    if species2_gff3:
        sp2_map_file = work_dir + "/" + species2_prefix + ".map"

        with open(sp2_map_file, 'w') as f:
            for i in sp2_chr_map:
                f.write("%s\t%s\n" % (i, sp2_chr_map[i]))


def running_mcscanxh(species1_gff3, species2_gff3, OG_tsv_file, work_dir, species1_prefix='aa', species2_prefix='bb', mcscanx_options='-k 50 -g -1 -s 5 -e 1e-05 -m 25 -a', huge_gene_family_filter=None):
    # prepare gff file
    mkdir(work_dir, True)

    sp1_gff_dict = read_gff_file(species1_gff3)
    sp1_gf_dict = {}
    for gf_type in sp1_gff_dict:
        for i in sp1_gff_dict[gf_type]:
            sp1_gf_dict[i] = sp1_gff_dict[gf_type][i]

    sp2_gf_dict = {}
    if species2_gff3:
        sp2_gff_dict = read_gff_file(species2_gff3)
        for gf_type in sp2_gff_dict:
            for i in sp2_gff_dict[gf_type]:
                sp2_gf_dict[i] = sp2_gff_dict[gf_type][i]

    sp1_chr_list = list(
        set([sp1_gf_dict[gf_id].chr_id for gf_id in sp1_gf_dict]))
    sp1_chr_map, sp1_chr_map_hash = get_chr_rename_map(
        sp1_chr_list, species1_prefix)

    sp2_chr_list = list(
        set([sp2_gf_dict[gf_id].chr_id for gf_id in sp2_gf_dict]))
    sp2_chr_map, sp2_chr_map_hash = get_chr_rename_map(
        sp2_chr_list, species2_prefix)

    merge_chr_map = merge_dict([sp1_chr_map, sp2_chr_map], extend_value=False)
    merge_gf_dict = merge_dict([sp1_gf_dict, sp2_gf_dict], extend_value=False)

    mcscanx_gff = work_dir + "/mcscanx.gff"
    write_mcscanx_gff(merge_gf_dict, merge_chr_map, mcscanx_gff)

    # prepare homology
    tsv_to_gene_pair(OG_tsv_file, species1_prefix,
                     species2_prefix, work_dir + "/mcscanx.homology", huge_gene_family_filter=huge_gene_family_filter)

    # run mcscanxh
    cmd_string = "MCScanX_h mcscanx " + mcscanx_options
    cmd_run(cmd_string, cwd=work_dir)

    # write map file
    sp1_map_file = work_dir + "/" + species1_prefix + ".map"

    with open(sp1_map_file, 'w') as f:
        for i in sp1_chr_map:
            f.write("%s\t%s\n" % (i, sp1_chr_map[i]))

    if species2_gff3:
        sp2_map_file = work_dir + "/" + species2_prefix + ".map"

        with open(sp2_map_file, 'w') as f:
            for i in sp2_chr_map:
                f.write("%s\t%s\n" % (i, sp2_chr_map[i]))


# results parser
class GeneLoci(object):
    def __init__(self, gene_id, chr_id, loci, species, gf):
        self.species = species
        self.id = gene_id
        self.loci = loci
        self.chr_id = chr_id
        self.gf = gf

    def __str__(self):
        return "%s: No. %d gene on %s from %s" % (self.id, self.loci, self.chr_id, self.species)


class Genome(object):
    def __init__(self, species_prefix, gff3_file=None, fasta_file=None):
        self.chr_dict = {}
        self.gene_dict = {}
        self.chr_length_dict = {}
        self.id = species_prefix

        if gff3_file:
            gff_dict = read_gff_file(gff3_file)

            chr_dict = {}
            gene_dict = {}
            for i in gff_dict['gene']:
                gf = gff_dict['gene'][i]
                if not gf.chr_id in chr_dict:
                    chr_dict[gf.chr_id] = []
                chr_dict[gf.chr_id].append(gf)
                gene_dict[gf.id] = gf

            for chr_id in chr_dict:
                chr_dict[chr_id] = sorted(
                    chr_dict[chr_id], key=lambda x: x.start)

            chr_gene_id_dict = {}
            for chr_id in chr_dict:
                chr_gene_id_dict[chr_id] = [i.id for i in chr_dict[chr_id]]

            self.chr_dict = {}
            self.gene_dict = {}
            for chr_id in chr_gene_id_dict:
                num = 0
                self.chr_dict[chr_id] = OrderedDict()
                for gene_id in chr_gene_id_dict[chr_id]:
                    gene = GeneLoci(gene_id, chr_id, num,
                                    species_prefix, gene_dict[gene_id])
                    self.chr_dict[chr_id][num] = gene
                    self.gene_dict[gene_id] = gene
                    num += 1

            self.chr_length_dict = {}
            if fasta_file:
                fa_dict = read_fasta_by_faidx(fasta_file)
                self.chr_length_dict = {i: fa_dict[i].len() for i in fa_dict}


class GenePair(object):
    def __init__(self, q_gene, s_gene, property_dict):
        self.q_gene = q_gene
        self.s_gene = s_gene
        self.property = property_dict

    def __str__(self):
        return "%s vs %s" % (self.q_gene, self.s_gene)

    def reverse_myself(self):
        new_GP = GenePair(self.s_gene, self.q_gene, self.property)
        return new_GP


class SyntenyBlock(object):
    def __init__(self, sb_id, q_sp, s_sp, strand, gene_pair_dict, property_dict, parameter_dict):
        self.id = sb_id
        self.property = property_dict
        self.parameter = parameter_dict
        self.strand = strand
        self.q_sp = q_sp
        self.s_sp = s_sp
        self.gene_pair_dict = gene_pair_dict

    def get_full_info(self, q_genome, s_genome):
        self.q_chr = self.gene_pair_dict[0].q_gene.chr_id
        self.s_chr = self.gene_pair_dict[0].s_gene.chr_id

        first_q_gene_loci = min(
            [self.gene_pair_dict[i].q_gene.loci for i in self.gene_pair_dict])
        last_q_gene_loci = max(
            [self.gene_pair_dict[i].q_gene.loci for i in self.gene_pair_dict])
        first_s_gene_loci = min(
            [self.gene_pair_dict[i].s_gene.loci for i in self.gene_pair_dict])
        last_s_gene_loci = max(
            [self.gene_pair_dict[i].s_gene.loci for i in self.gene_pair_dict])

        self.query_gene_list = []
        for i in range(first_q_gene_loci, last_q_gene_loci + 1):
            self.query_gene_list.append(q_genome.chr_dict[self.q_chr][i])

        self.subject_gene_list = []
        for i in range(first_s_gene_loci, last_s_gene_loci + 1):
            self.subject_gene_list.append(s_genome.chr_dict[self.s_chr][i])

        self.first_q_gene = q_genome.chr_dict[self.q_chr][min(
            [i.loci for i in self.query_gene_list])]
        self.last_q_gene = q_genome.chr_dict[self.q_chr][max(
            [i.loci for i in self.query_gene_list])]
        self.first_s_gene = s_genome.chr_dict[self.s_chr][min(
            [i.loci for i in self.subject_gene_list])]
        self.last_s_gene = s_genome.chr_dict[self.s_chr][max(
            [i.loci for i in self.subject_gene_list])]

        self.first_q_gene_loci = self.first_q_gene.loci
        self.last_q_gene_loci = self.last_q_gene.loci
        self.first_s_gene_loci = self.first_s_gene.loci
        self.last_s_gene_loci = self.last_s_gene.loci

        self.query_from = min([q_genome.gene_dict[self.first_q_gene.id].gf.start, q_genome.gene_dict[self.first_q_gene.id].gf.end,
                               q_genome.gene_dict[self.last_q_gene.id].gf.start, q_genome.gene_dict[self.last_q_gene.id].gf.end])
        self.query_to = max([q_genome.gene_dict[self.first_q_gene.id].gf.start, q_genome.gene_dict[self.first_q_gene.id].gf.end,
                             q_genome.gene_dict[self.last_q_gene.id].gf.start, q_genome.gene_dict[self.last_q_gene.id].gf.end])
        self.subject_from = min([s_genome.gene_dict[self.first_s_gene.id].gf.start, s_genome.gene_dict[self.first_s_gene.id].gf.end,
                                 s_genome.gene_dict[self.last_s_gene.id].gf.start, s_genome.gene_dict[self.last_s_gene.id].gf.end])
        self.subject_to = max([s_genome.gene_dict[self.first_s_gene.id].gf.start, s_genome.gene_dict[self.first_s_gene.id].gf.end,
                               s_genome.gene_dict[self.last_s_gene.id].gf.start, s_genome.gene_dict[self.last_s_gene.id].gf.end])

    def reverse_myself(self, new_sb_id=None):
        gene_pair_dict = {
            i: self.gene_pair_dict[i].reverse_myself() for i in self.gene_pair_dict}
        if new_sb_id is None:
            new_sb_id = self.id

        new_sb = SyntenyBlock(new_sb_id, self.s_sp, self.q_sp,
                              self.strand, gene_pair_dict, self.property, self.parameter)

        new_sb.q_chr = new_sb.gene_pair_dict[0].q_gene.chr_id
        new_sb.s_chr = new_sb.gene_pair_dict[0].s_gene.chr_id

        new_sb.query_gene_list = self.subject_gene_list
        new_sb.subject_gene_list = self.query_gene_list

        new_sb.first_q_gene = self.first_s_gene
        new_sb.last_q_gene = self.last_s_gene
        new_sb.first_s_gene = self.first_q_gene
        new_sb.last_s_gene = self.last_q_gene

        new_sb.first_q_gene_loci = new_sb.first_q_gene.loci
        new_sb.last_q_gene_loci = new_sb.last_q_gene.loci
        new_sb.first_s_gene_loci = new_sb.first_s_gene.loci
        new_sb.last_s_gene_loci = new_sb.last_s_gene.loci

        new_sb.query_from = self.subject_from
        new_sb.query_to = self.subject_to
        new_sb.subject_from = self.query_from
        new_sb.subject_to = self.query_to

        return new_sb

    def __str__(self):
        return "Q = %s:%s gene: %d-%d (%d) base: %d-%d (%d) vs S = %s:%s gene: %d-%d (%d) base: %d-%d (%d), %s, have %d gene pair" % (self.q_sp, self.q_chr, self.first_q_gene_loci, self.last_q_gene_loci, self.last_q_gene_loci - self.first_q_gene_loci + 1,  self.query_from, self.query_to, self.query_to - self.query_from + 1, self.s_sp, self.s_chr, self.first_s_gene_loci, self.last_s_gene_loci, self.last_s_gene_loci - self.first_s_gene_loci + 1,   self.subject_from, self.subject_to, self.subject_to - self.subject_from + 1, self.strand, len(self.gene_pair_dict))

    __repr__ = __str__


def sb_plot(sb):

    all_q_list = sb.query_gene_list
    all_s_list = sb.subject_gene_list

    fig, ax = plt.subplots(figsize=(10,20))

    vertical = -3
    start_site = 1
    ax.text(vertical, start_site-2, all_q_list[0].chr_id, ha='center', va='center')
    for q_gf in all_q_list:
        add_box(ax, start_site, start_site+1, vertical=vertical)
        q_gf.fig_site = (vertical, start_site)
        ax.text(vertical-1, start_site+1, q_gf.loci, ha='center', va='center')
        start_site += 3
    q_max_s = start_site

    vertical = 3
    start_site = 1
    ax.text(vertical, start_site-2, all_s_list[0].chr_id, ha='center', va='center')
    for s_gf in all_s_list:
        add_box(ax, start_site, start_site+1, vertical=vertical)
        s_gf.fig_site = (vertical, start_site)
        ax.text(vertical+1, start_site+1, s_gf.loci, ha='center', va='center')
        start_site += 3
    s_max_s = start_site    

    for gp_id in sb.gene_pair_dict:
        gp = sb.gene_pair_dict[gp_id]
        q_s = gp.q_gene.fig_site
        s_s = gp.s_gene.fig_site
        ax.plot([q_s[0], s_s[0]], [q_s[1], s_s[1]], color='k', alpha=0.8)

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, max(q_max_s, s_max_s)+2)    

    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.show()    


def get_mcscan_parameter(mcscanx_collinearity_file):

    with open(mcscanx_collinearity_file, 'r') as f:
        for each_line in f:
            # statistics
            mobj = re.match(
                r"# Number of collinear genes: (\d+), Percentage: (\d+\.\d+)", each_line)
            if mobj:
                gene_in_coll, percentage = mobj.groups()
                gene_in_coll, percentage = int(gene_in_coll), float(percentage)

            mobj = re.match(r"# Number of all genes: (\d+)", each_line)
            if mobj:
                all_gene = mobj.groups()[0]
                all_gene = int(all_gene)

            # Parameters
            mobj = re.match(r"# MATCH_SCORE: (\S+)$", each_line)
            if mobj:
                MATCH_SCORE = mobj.groups()[0]
                MATCH_SCORE = int(MATCH_SCORE)

            mobj = re.match(r"# MATCH_SIZE: (\S+)$", each_line)
            if mobj:
                MATCH_SIZE = mobj.groups()[0]
                MATCH_SIZE = int(MATCH_SIZE)

            mobj = re.match(r"# GAP_PENALTY: (\S+)$", each_line)
            if mobj:
                GAP_PENALTY = mobj.groups()[0]
                GAP_PENALTY = int(GAP_PENALTY)

            mobj = re.match(r"# OVERLAP_WINDOW: (\S+)$", each_line)
            if mobj:
                OVERLAP_WINDOW = mobj.groups()[0]
                OVERLAP_WINDOW = int(OVERLAP_WINDOW)

            mobj = re.match(r"# E_VALUE: (\S+)$", each_line)
            if mobj:
                E_VALUE = mobj.groups()[0]
                E_VALUE = float(E_VALUE)

            mobj = re.match(r"# MAX GAPS: (\S+)$", each_line)
            if mobj:
                MAX_GAPS = mobj.groups()[0]
                MAX_GAPS = int(MAX_GAPS)

    parameter_dict = {
        "gene_in_coll": gene_in_coll,
        "percentage": percentage,
        "all_gene": all_gene,
        "match_score": MATCH_SCORE,
        "match_size": MATCH_SIZE,
        "gap_penalty": GAP_PENALTY,
        "overlap_window": OVERLAP_WINDOW,
        "e_value": E_VALUE,
        "max_gaps": MAX_GAPS
    }

    return parameter_dict


def collinearity_parser(mcscanx_collinearity_file, query_species, q_genome, subject_species, s_genome):
    mcscan_parameter = get_mcscan_parameter(mcscanx_collinearity_file)

    synteny_block_dict = {}

    with open(mcscanx_collinearity_file, 'r') as f:
        for each_line in f:
            # Block title
            mobj = re.match(
                r"## Alignment (\S+): score=(\S+) e_value=(\S+) N=(\S+) (\S+)&(\S+) (\S+)", each_line)
            if mobj:
                align_id, score, e_value, gene_pair_num, q_chr, s_chr, strand = mobj.groups()

                q_sp = re.sub(r'\d+', '', q_chr)
                s_sp = re.sub(r'\d+', '', s_chr)

                if q_sp != query_species or s_sp != subject_species:
                    continue

                align_id, score, e_value, gene_pair_num, q_chr, s_chr, strand = align_id, float(
                    score), float(e_value), int(gene_pair_num), q_chr, s_chr, strand
                if strand == 'plus':
                    strand = "+"
                elif strand == 'minus':
                    strand = "-"
                else:
                    raise

                property_dict = {
                    'score': score,
                    'e_value': e_value,
                    'gene_pair_num': gene_pair_num,
                }

                synteny_block_dict[align_id] = SyntenyBlock(
                    align_id, q_sp, s_sp, strand, {}, property_dict, mcscan_parameter)

            # block line
            if re.match("^#", each_line):
                continue
            else:
                if align_id not in synteny_block_dict:
                    continue

                align_id = each_line.split("-", 1)[0]
                pair_id = each_line.split("-", 1)[1].split(":", 1)[0]

                align_id = re.sub(r'\s+', '', align_id)
                pair_id = int(re.sub(r'\s+', '', pair_id))

                q_gene_id, s_gene_id, e_value = each_line.split(
                    "-", 1)[1].split(":", 1)[1].split()
                align_id, pair_id, q_gene_id, s_gene_id, e_value = align_id, pair_id, q_gene_id, s_gene_id, float(
                    e_value)

                q_gene = q_genome.gene_dict[q_gene_id]
                s_gene = s_genome.gene_dict[s_gene_id]

                property_dict = {'e_value': e_value}

                synteny_block_dict[align_id].gene_pair_dict[pair_id] = GenePair(
                    q_gene, s_gene, property_dict)

    for align_id in synteny_block_dict:
        synteny_block_dict[align_id].get_full_info(q_genome, s_genome)

    return synteny_block_dict


def pair_self_synteny_block_dict(synteny_block_dict, genome):
    full_synteny_block_dict = {
        i: synteny_block_dict[i] for i in synteny_block_dict}
    num = max(synteny_block_dict.keys())
    for i in synteny_block_dict:
        num += 1
        new_sb = synteny_block_dict[i].reverse_myself(num)
        new_sb.get_full_info(genome, genome)

        full_synteny_block_dict[num] = new_sb

    return full_synteny_block_dict


def get_OG_pair_set(OG_tsv_file, sp1, sp2=None):
    OG_dict = OG_tsv_file_parse(OG_tsv_file)

    OG_pair = []
    for OG_id in OG_dict:
        if sp2:
            sp1_list = OG_dict[OG_id][sp1]
            sp2_list = OG_dict[OG_id][sp2]

            if sp1_list == '' or sp2_list == '':
                continue

            for i in sp1_list:
                for j in sp2_list:
                    OG_pair.append((i, j))
        else:
            sp1_list = OG_dict[OG_id][sp1]

            if sp1_list == '':
                continue

            for i in sp1_list:
                for j in sp1_list:
                    if i == j:
                        continue
                    OG_pair.append((i, j))

    OG_pair = set(OG_pair)

    return OG_pair


def map_ortho_to_block(synteny_block, OG_pair_set):
    OG_pair_list = []

    for gp_id in synteny_block.gene_pair_dict:
        q_id = synteny_block.gene_pair_dict[gp_id].q_gene.id
        s_id = synteny_block.gene_pair_dict[gp_id].s_gene.id
        if (q_id, s_id) in OG_pair_set or (s_id, q_id) in OG_pair_set:
            OG_pair_list.append(gp_id)

    synteny_block.property['OG_pair_list'] = OG_pair_list

    return synteny_block


def get_synteny_block_interlap(synteny_block_dict):
    query_synteny_block_chr_interlap_dict = {}
    subject_synteny_block_chr_interlap_dict = {}
    for sb_id in synteny_block_dict:
        sb = synteny_block_dict[sb_id]
        q_chr = sb.q_chr
        s_chr = sb.s_chr
        query_synteny_block_chr_interlap_dict[q_chr] = InterLap()
        subject_synteny_block_chr_interlap_dict[s_chr] = InterLap()

    for sb_id in synteny_block_dict:
        sb = synteny_block_dict[sb_id]
        q_chr = sb.q_chr
        s_chr = sb.s_chr

        query_synteny_block_chr_interlap_dict[q_chr].add(
            (sb.first_q_gene_loci, sb.last_q_gene_loci, sb_id))
        subject_synteny_block_chr_interlap_dict[s_chr].add(
            (sb.first_s_gene_loci, sb.last_s_gene_loci, sb_id))

    return query_synteny_block_chr_interlap_dict, subject_synteny_block_chr_interlap_dict


def get_synteny_block_genome_range_interlap(synteny_block_dict):
    query_synteny_block_chr_interlap_dict = {}
    subject_synteny_block_chr_interlap_dict = {}
    for sb_id in synteny_block_dict:
        sb = synteny_block_dict[sb_id]
        q_chr = sb.q_chr
        s_chr = sb.s_chr
        query_synteny_block_chr_interlap_dict[q_chr] = InterLap()
        subject_synteny_block_chr_interlap_dict[s_chr] = InterLap()

    for sb_id in synteny_block_dict:
        sb = synteny_block_dict[sb_id]
        q_chr = sb.q_chr
        s_chr = sb.s_chr

        query_synteny_block_chr_interlap_dict[q_chr].add(
            (sb.first_q_gene.gf.start, sb.last_q_gene.gf.end, sb_id))
        subject_synteny_block_chr_interlap_dict[s_chr].add(
            (sb.first_s_gene.gf.start, sb.last_s_gene.gf.end, sb_id))

    return query_synteny_block_chr_interlap_dict, subject_synteny_block_chr_interlap_dict


def get_overlaped_block_group(synteny_block_dict):
    q_sb_interlap, s_sb_interlap = get_synteny_block_interlap(
        synteny_block_dict)

    group_list = []
    for sb_id in synteny_block_dict:
        group_list.append([sb_id])
        sb = synteny_block_dict[sb_id]

        q_over_list = [i[2] for i in q_sb_interlap[sb.q_chr].find(
            (sb.first_q_gene_loci, sb.last_q_gene_loci))]
        s_over_list = [i[2] for i in s_sb_interlap[sb.s_chr].find(
            (sb.first_s_gene_loci, sb.last_s_gene_loci))]

        overlap_list = list(set(q_over_list) & set(s_over_list))

        if len(overlap_list) > 0:
            # print(overlap_list)
            group_list.append(overlap_list)

    merged_group_list = merge_same_element_set(group_list)

    return merged_group_list


def get_merged_block(merge_id, group_list, synteny_block_dict, q_genome, s_genome):
    tmp_sb = synteny_block_dict[sorted(group_list, key=lambda x:(abs(
        synteny_block_dict[x].query_to - synteny_block_dict[x].query_from)), reverse=True)[0]]
    q_sp = tmp_sb.q_sp
    s_sp = tmp_sb.s_sp
    strand = tmp_sb.strand
    parameter_dict = tmp_sb.parameter

    gene_pair_dict = {}
    num = 0
    for i in group_list:
        for j in synteny_block_dict[i].gene_pair_dict:
            gene_pair_dict[num] = synteny_block_dict[i].gene_pair_dict[j]
            num += 1

    super_sb = SyntenyBlock(merge_id, q_sp, s_sp, strand,
                            gene_pair_dict, {}, parameter_dict)

    super_sb.get_full_info(q_genome, s_genome)

    return super_sb


def merge_blocks(synteny_block_dict, q_genome, s_genome):
    merged_group_list = get_overlaped_block_group(synteny_block_dict)
    num = 0
    merged_synteny_block_dict = {}
    for group_list in merged_group_list:
        merged_synteny_block_dict[num] = get_merged_block(
            num, group_list, synteny_block_dict, q_genome, s_genome)
        num += 1
    return merged_synteny_block_dict


def gene_cover_depth_stat(synteny_block_dict, query_or_subject, covered_genome):
    q_sb_interlap, s_sb_interlap = get_synteny_block_interlap(
        synteny_block_dict)

    if query_or_subject == 'query':
        sb_interlap = q_sb_interlap
    elif query_or_subject == 'subject':
        sb_interlap = s_sb_interlap

    # gene cover dict
    gene_cover_depth_dict = {}
    for g_id in covered_genome.gene_dict:
        gene = covered_genome.gene_dict[g_id]
        if gene.chr_id in sb_interlap:
            gene_cover_depth_dict[g_id] = len(
                list(sb_interlap[gene.chr_id].find((gene.loci, gene.loci))))
        else:
            gene_cover_depth_dict[g_id] = 0

    # range cover
    range_loci_cover_chr_dict = {}
    for chr_id in covered_genome.chr_dict:
        range_loci_cover_chr_dict[chr_id] = {}
        for gene_num in covered_genome.chr_dict[chr_id]:
            g = covered_genome.chr_dict[chr_id][gene_num]
            g_depth = gene_cover_depth_dict[g.id]
            if g_depth == 0:
                continue
            if g_depth not in range_loci_cover_chr_dict[chr_id]:
                range_loci_cover_chr_dict[chr_id][g_depth] = []
            range_loci_cover_chr_dict[chr_id][g_depth].append(
                (gene_num, gene_num))
            range_loci_cover_chr_dict[chr_id][g_depth] = merge_intervals(
                range_loci_cover_chr_dict[chr_id][g_depth], True)

    range_base_cover_chr_dict = {}
    for chr_id in range_loci_cover_chr_dict:
        range_base_cover_chr_dict[chr_id] = {}
        for depth in range_loci_cover_chr_dict[chr_id]:
            if depth == 0:
                continue
            range_base_cover_chr_dict[chr_id][depth] = []

            for s, e in range_loci_cover_chr_dict[chr_id][depth]:
                start = covered_genome.chr_dict[chr_id][s].gf.start
                end = covered_genome.chr_dict[chr_id][e].gf.end
                range_base_cover_chr_dict[chr_id][depth].append((start, end))

    return gene_cover_depth_dict, range_loci_cover_chr_dict, range_base_cover_chr_dict


def WGD_check_pipeline(mcscanx_collinearity_file, query_species, query_gff3, query_genome_fasta, subject_species, subject_gff3, subject_genome_fasta, OG_tsv_file=None, OG_filter=0.3):
    q_genome = Genome(query_species, query_gff3, query_genome_fasta)
    s_genome = Genome(subject_species, subject_gff3, subject_genome_fasta)

    # load block
    synteny_block_dict = collinearity_parser(
        mcscanx_collinearity_file, query_species, q_genome, subject_species, s_genome)
    # print(len(synteny_block_dict))

    # filter by OG
    if OG_tsv_file:
        OG_pair_set = get_OG_pair_set(
            OG_tsv_file, query_species, subject_species)

        for i in synteny_block_dict:
            synteny_block_dict[i] = map_ortho_to_block(
                synteny_block_dict[i], OG_pair_set)

        synteny_block_dict = {i: synteny_block_dict[i] for i in synteny_block_dict if len(
            synteny_block_dict[i].property['OG_pair_list']) / len(synteny_block_dict[i].gene_pair_dict) > OG_filter}

    # merge block
    synteny_block_dict = merge_blocks(synteny_block_dict, q_genome, s_genome)

    # get gene cover dict
    q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict = gene_cover_depth_stat(
        synteny_block_dict, 'query', q_genome)
    s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict = gene_cover_depth_stat(
        synteny_block_dict, 'subject', s_genome)

    return q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict


def WGD_check_pipeline_for_self_comparsion(mcscanx_collinearity_file, species_id, gff3_file, genome_fasta, OG_tsv_file=None, OG_filter=0.3):
    genome = Genome(species_id, gff3_file, genome_fasta)

    # load block
    synteny_block_dict = collinearity_parser(
        mcscanx_collinearity_file, species_id, genome, species_id, genome)
    # print(len(synteny_block_dict))

    # filter by OG
    if OG_tsv_file:
        OG_pair_set = get_OG_pair_set(OG_tsv_file, species_id)

        for i in synteny_block_dict:
            synteny_block_dict[i] = map_ortho_to_block(
                synteny_block_dict[i], OG_pair_set)

        synteny_block_dict = {i: synteny_block_dict[i] for i in synteny_block_dict if len(
            synteny_block_dict[i].property['OG_pair_list']) / len(synteny_block_dict[i].gene_pair_dict) > OG_filter}

    # merge block
    synteny_block_dict = merge_blocks(synteny_block_dict, genome, genome)
    synteny_block_dict = pair_self_synteny_block_dict(
        synteny_block_dict, genome)

    # get gene cover dict
    gene_cover_depth_dict, range_loci_cover_chr_dict, range_base_cover_chr_dict = gene_cover_depth_stat(
        synteny_block_dict, 'query', genome)

    return gene_cover_depth_dict, range_loci_cover_chr_dict, range_base_cover_chr_dict, synteny_block_dict


def collinearity_file_to_synteny_block_range_csv(query_id, query_gff, subject_id, subject_gff, mcscanx_collinearity_file, csv_file):

    q_genome = Genome(query_id, query_gff)
    s_genome = Genome(subject_id, subject_gff)

    # load block
    synteny_block_dict = collinearity_parser(
        mcscanx_collinearity_file, query_id, q_genome, subject_id, s_genome)

    with open(csv_file, 'w') as f:

        for sb_id in synteny_block_dict:
            sb = synteny_block_dict[sb_id]

            sb.query_from
            sb.query_to
            sb.subject_from
            sb.subject_to
            sb.strand

            f.write(printer_list([query_id, sb.q_chr, sb.query_from, sb.query_to,
                                  subject_id, sb.s_chr, sb.subject_from, sb.subject_to, sb.strand]) + "\n")


if __name__ == "__main__":

    species1_prefix = 'Aof'
    species1_gff3 = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/Aof.merge.gff3'
    species1_aa_fasta = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/Aof.merge.fasta'

    species2_prefix = 'Gel'
    species2_gff3 = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/Gel.merge.gff3'
    species2_aa_fasta = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/Gel.merge.fasta'

    work_dir = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/python'
    give_bls_file = None
    skip_gene_list = []

    running_mcscanx(species1_gff3, species2_gff3, work_dir, species1_prefix='aa', species1_aa_fasta=None,
                    species2_prefix='bb', species2_aa_fasta=None, skip_gene_list=[], give_bls_file=None)

    # parse
    # from toolbiox.lib.evolution.mcscan import WGD_check_pipeline
    from collections import Counter, OrderedDict

    query_species = 'Ash'
    query_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Ash.gff3'
    query_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Apostasia_shenzhenica/T1088818N0.genome.fasta'
    subject_species = 'Gel'
    subject_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.gff3'
    subject_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta'
    mcscanx_collinearity_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel_vs_Ash/mcscanx.collinearity'

    q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = WGD_check_pipeline(
        mcscanx_collinearity_file, query_species, query_gff3, query_genome_fasta, subject_species, subject_gff3, subject_genome_fasta)

    Counter([q_gene_covered_dict[i] for i in q_gene_covered_dict])
    Counter([s_gene_covered_dict[i] for i in s_gene_covered_dict])
