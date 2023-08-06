import sys
import re
import sqlite3
import json
from toolbiox.lib.common.math.interval import section, merge_intervals, interval_minus_set, overlap_between_interval_set, \
    group_by_intervals, group_by_intervals_with_overlap_threshold
from toolbiox.lib.common.genome.seq_base import BioSeq, read_fasta_by_faidx, read_fasta
from toolbiox.lib.common.util import printer_list, time_now
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
from interlap import InterLap
from BCBio import GFF
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Seq import Seq, translate
from copy import copy, deepcopy
from collections import OrderedDict
from toolbiox.lib.common.os import multiprocess_running


class ChrLoci(object):
    def __init__(self, chr_id=None, strand=None, start=None, end=None, species_id=None):
        self.chr_id = chr_id
        self.sp_id = species_id

        if strand is None:
            self.strand = strand
        elif strand == "+" or str(strand) == '1':
            self.strand = "+"
        elif strand == "-" or str(strand) == '-1':
            self.strand = "-"
        else:
            self.strand = None

        if end is not None and start is not None:
            self.start = min(int(start), int(end))
            self.end = max(int(start), int(end))
            self._range = (self.start, self.end)
            self.length = abs(self.end - self.start) + 1

    # def __eq__(self, other):
    #     """Implement equality by comparing all the location attributes."""
    #     if not isinstance(other, ChrLoci):
    #         return False
    #     return self.start == other.start and \
    #            self.end == other.end and \
    #            self.strand == other.strand and \
    #            self.chr_id == other.chr_id

    def get_fancy_name(self):
        if self.strand is None:
            self.fancy_name = "%s:%d-%d" % (self.chr_id, self.start, self.end)
        else:
            self.fancy_name = "%s:%d-%d:%s" % (self.chr_id,
                                               self.start, self.end, self.strand)
        return self.fancy_name

    def __str__(self):
        try:
            self.get_fancy_name()
            if self.sp_id:
                return "%s %s" % (self.sp_id, self.fancy_name)
            else:
                return self.fancy_name
        except:
            return "No detail range"

    __repr__ = __str__

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        start, end = value
        if end is not None and start is not None:
            self.start = min(int(start), int(end))
            self.end = max(int(start), int(end))
            self._range = (self.start, self.end)

    def get_sequence(self, data_fasta_file, RNA=False):
        sequence = read_fasta_by_faidx(data_fasta_file)[self.chr_id].sub(self._range[0], self._range[1], self.strand,
                                                                         RNA)
        self.get_fancy_name()
        return BioSeq(sequence, self.fancy_name)

    def get_sequence_quick(self, seq_dict, RNA=False):
        """
        seq_dict should load sequence into memory, and Bioseq not have faidx attr
        """
        sequence = seq_dict[self.chr_id].sub(
            self._range[0], self._range[1], self.strand, RNA)
        self.get_fancy_name()
        return BioSeq(sequence, self.fancy_name)

    def len(self):
        return abs(self.end - self.start) + 1

    def __eq__(self, other):
        return self.chr_id == other.chr_id and self.strand == other.strand and self.start == other.start and self.end == other.end and self.sp_id == other.sp_id

    def __hash__(self):
        return hash(id(self))


class GenomeFeature(ChrLoci):
    def __init__(self, id=None, type=None, chr_loci=None, qualifiers={}, sub_features=None):
        if chr_loci is None:
            super(GenomeFeature, self).__init__(
                chr_id=None, strand=None, start=None, end=None)
        else:
            super(GenomeFeature, self).__init__(chr_id=chr_loci.chr_id, strand=chr_loci.strand, start=chr_loci.start,
                                                end=chr_loci.end)
        self.id = id
        self.type = type
        self.chr_loci = chr_loci
        self.sub_features = sub_features
        self.qualifiers = qualifiers

    def sgf_len(self):
        self.sgf_len_dir = {i: 0 for i in list(
            set([sgf.type for sgf in self.sub_features]))}

        for sgf in self.sub_features:
            sgf_len = abs(sgf.start - sgf.end) + 1
            self.sgf_len_dir[sgf.type] += sgf_len

    def __eq__(self, other):
        return self.id == other.id and self.chr_loci == other.chr_loci and self.type == other.type

    def __hash__(self):
        return hash(id(self))


class mRNA(GenomeFeature):
    def __init__(self, id=None, chr_loci=None, qualifiers=None, sub_features=None, cds_seq=None, aa_seq=None,
                 cDNA_seq=None, from_gf=None):
        if not from_gf is None:
            super(mRNA, self).__init__(id=from_gf.id, type='mRNA', chr_loci=from_gf.chr_loci,
                                       qualifiers=from_gf.qualifiers, sub_features=from_gf.sub_features)
        else:
            super(mRNA, self).__init__(id=id, type='mRNA', chr_loci=chr_loci, qualifiers=qualifiers,
                                       sub_features=sub_features)
        self.cds_seq = cds_seq
        self.aa_seq = aa_seq
        self.cDNA_seq = cDNA_seq

    def build_mRNA_seq(self, genome_file):
        if not hasattr(self, 'sub_features'):
            raise ValueError("build need sub_features")

        self.cds_seq = feature_seq_extract(
            self.sub_features, genome_file, "CDS")
        self.cDNA_seq = feature_seq_extract(
            self.sub_features, genome_file, "exon")

        good_orf, phase, aa_seq, cds_seq = cds_judgment(self.cds_seq, parse_phase=True, keep_stop=False, return_cds=True)

        self.cds_seq = cds_seq
        self.aa_seq = aa_seq
        self.cds_phase = phase
        self.cds_good_orf = good_orf

    def get_introns(self):

        exon_list = [i for i in sub_gf_traveler(self) if i.type in [
            'exon', 'CDS', 'five_prime_UTR', 'three_prime_UTR', 'five_prime_utr', 'three_prime_utr']]
        exon_interval_list = sorted(merge_intervals(
            [(i.start, i.end) for i in exon_list]))
        min_s = min([i[0] for i in exon_interval_list] + [i[1]
                                                          for i in exon_interval_list])
        max_s = max([i[0] for i in exon_interval_list] + [i[1]
                                                          for i in exon_interval_list])

        intron_list_already = [i for i in sub_gf_traveler(self) if i.type == 'intron']
        for i in intron_list_already:
            self.sub_features.remove(i)
        
        intron_interval_list = interval_minus_set(
            (min_s, max_s), exon_interval_list)
        intron_interval_list = sorted(
            intron_interval_list, key=lambda x: x[0], reverse=(self.strand == '-'))
       
        intron_list = []
        num = 1
        for i in intron_interval_list:
            intron_list.append(GenomeFeature(id="%s.intron.%d" % (self.id, num), type='intron', chr_loci=ChrLoci(
                chr_id=self.chr_id, strand=self.strand, start=min(i), end=max(i), species_id=self.sp_id), qualifiers=None, sub_features=[]))
            num += 1

        self.sub_features.extend(intron_list)


class Gene(GenomeFeature):
    def __init__(self, id=None, species=None, chr_loci=None, qualifiers=None, sub_features=None, model_cds_seq=None,
                 model_aa_seq=None, model_cDNA_seq=None, from_gf=None, chr_rank=None):
        if not from_gf is None:
            super(Gene, self).__init__(id=from_gf.id, type='gene', chr_loci=from_gf.chr_loci,
                                       qualifiers=from_gf.qualifiers, sub_features=from_gf.sub_features)
        else:
            super(Gene, self).__init__(id=id, type='gene', chr_loci=chr_loci, qualifiers=qualifiers,
                                       sub_features=sub_features)
        self.model_cds_seq = model_cds_seq
        self.model_aa_seq = model_aa_seq
        self.model_cDNA_seq = model_cDNA_seq
        self.species = species
        self.chr_rank = chr_rank

    def build_gene_seq(self, genome_file=None):
        if not hasattr(self, 'sub_features'):
            raise ValueError("build need sub_features")

        all_mRNA_list = [mRNA(from_gf=gf) for gf in self.sub_features]

        # remove mRNA without CDS
        mRNA_list = []
        for mRNA_now in all_mRNA_list:
            # print(mRNA_now.id)
            if mRNA_now.sub_features:
                cds_num = len(
                    [i for i in mRNA_now.sub_features if i.type == 'CDS'])
            else:
                cds_num = 0
            if cds_num > 0:
                mRNA_list.append(mRNA_now)

        # [i.build_mRNA_seq(genome_file) for i in mRNA_list]
        [i.sgf_len() for i in mRNA_list]

        longest_cds_mRNA = sorted(
            mRNA_list, key=lambda x: x.sgf_len_dir['CDS'], reverse=True)[0]
        self.model_mRNA_id = longest_cds_mRNA.id
        self.model_mRNA = longest_cds_mRNA

        if genome_file is not None:
            longest_cds_mRNA.build_mRNA_seq(genome_file)

            self.model_cds_seq = longest_cds_mRNA.cds_seq
            self.model_aa_seq = longest_cds_mRNA.aa_seq
            self.model_cDNA_seq = longest_cds_mRNA.cDNA_seq
            self.model_cds_good_orf = longest_cds_mRNA.cds_good_orf
            self.model_cds_phase = longest_cds_mRNA.cds_phase

        self.sub_features = mRNA_list

    def __str__(self):
        try:
            return "Gene: %s (%s)" % (self.id, self.chr_loci.get_fancy_name())
        except:
            return "Gene: %s" % self.id

    __repr__ = __str__


class GeneSet(object):
    def __init__(self, id, gene_list):
        self.id = id
        self.gene_list = gene_list
        self.tree_file = None
        self.seq_file = None
        self.aln_file = None
        self.aa_seq_file = None
        self.aa_aln_file = None
        self.cds_seq_file = None
        self.cds_aln_file = None
        self.hmm_file = None

    def speci_stat(self):
        output_dir = {}
        for i in self.gene_list:
            if i.species not in output_dir:
                output_dir[i.species] = 0
            output_dir[i.species] = output_dir[i.species] + 1
        return output_dir

    def __str__(self):
        return "ID: %s; Gene Num: %d" % (self.id, len(self.gene_list))


class Chromosome(object):
    def __init__(self, id=None, species=None, version=None, seq=None, length=None):
        self.id = id
        self.species = species
        self.version = version
        self.seq = seq
        self.len = length

    def load_genome_features(self, feature_dict):
        chr_feature_dict = OrderedDict()
        for type_tmp in feature_dict:
            chr_feature_dict[type_tmp] = OrderedDict()
            for gf_tmp_id in feature_dict[type_tmp]:
                gf_tmp = feature_dict[type_tmp][gf_tmp_id]
                if gf_tmp.chr_loci.chr_id == self.id:
                    chr_feature_dict[type_tmp][gf_tmp.id] = gf_tmp
        self.feature_dict = chr_feature_dict

    def build_index(self):
        if not hasattr(self, 'feature_dict'):
            raise ValueError("build_index need feature_dict")

        self.feature_index = {
            "+": InterLap(),
            "-": InterLap(),
            ".": InterLap()
        }

        for type_tmp in self.feature_dict:
            for gf_tmp_id in self.feature_dict[type_tmp]:
                gf_tmp = self.feature_dict[type_tmp][gf_tmp_id]
                try:
                    index_tmp = self.feature_index[gf_tmp.strand]
                except:
                    raise ValueError("bad: %s" % gf_tmp_id)
                index_tmp.add(
                    (gf_tmp.chr_loci.start, gf_tmp.chr_loci.end, gf_tmp))


class Genome(object):
    def __init__(self, id=None, species=None, version=None, genome_file=None, gff_file=None, cds_file=None,
                 cDNA_file=None, aa_file=None):
        self.id = id
        self.species = species
        self.version = version
        self.genome_file = genome_file
        self.gff_file = gff_file
        self.cds_file = cds_file
        self.cDNA_file = cDNA_file
        self.aa_file = aa_file

    def genome_file_parse(self):
        self.genome_seq = read_fasta_by_faidx(self.genome_file)
        self.chromosomes = OrderedDict()
        for contig_id in self.genome_seq:
            contig_len = self.genome_seq[contig_id].seqs_length()
            self.chromosomes[contig_id] = Chromosome(id=contig_id, species=self.species, version=self.version,
                                                     length=contig_len)

    def genome_feature_parse(self):
        # check needed files
        if not hasattr(self, 'gff_file') or self.gff_file is None:
            raise ValueError("genome_feature_parse need gff_file!")

        self.feature_dict = read_gff_file(self.gff_file)

    def build_gene_sequence(self):
        num = 0

        if not self.genome_file is None:
            genome_dict, contig_list = read_fasta(self.genome_file)
        else:
            genome_dict = None
        nc_gene = OrderedDict()
        only_gene = OrderedDict()
        for gene_id in self.feature_dict['gene']:
            num += 1
            gene_gf = self.feature_dict['gene'][gene_id]

            # if a coding gene (if have CDS)
            cds_num = 0
            if not gene_gf.sub_features is None:
                if not gene_gf.sub_features[0].sub_features is None:
                    cds_num = len(
                        [i for i in gene_gf.sub_features[0].sub_features if i.type == 'CDS'])

            if cds_num == 0:
                nc_gene[gene_id] = gene_gf
                continue

            gene_tmp = Gene(from_gf=gene_gf)
            gene_tmp.build_gene_seq(genome_dict)
            only_gene[gene_id] = gene_tmp

            if num % 10 == 0:
                # print("%s: %d / %d" % (time_now(), num, len(self.feature_dict['gene'])))
                pass

        self.feature_dict['non_coding_gene'] = nc_gene
        self.feature_dict['gene'] = only_gene

    # def cds_fasta_parse(self):
    #     # check needed files
    #     if not hasattr(self, 'cds_file') or self.cds_file is None:
    #         raise ValueError("cds_fasta_parse need cds_file!")
    #
    #     cds_seq_dict = read_fasta_by_faidx(self.cds_file)

    def build_index(self):
        for chr_id in self.chromosomes:
            self.chromosomes[chr_id].load_genome_features(self.feature_dict)
            self.chromosomes[chr_id].build_index()

    def search(self, fancy_name_string):
        contig_name, c_start, c_end, strand = fancy_name_parse(
            fancy_name_string)
        if strand == ".":
            feature_index_list = ["+", "-", "."]
        else:
            feature_index_list = [strand]

        output_dir = OrderedDict()
        for strand_used in feature_index_list:
            feature_index = self.chromosomes[contig_name].feature_index[strand_used]
            for f_s, f_e, feature in feature_index.find((c_start, c_end)):
                output_dir[feature.id] = feature

        return output_dir

    def get_chromosome_from_gff(self):
        """
        get chromosome from gff file, which not very recommended
        """
        self.chromosomes = OrderedDict()
        with open(self.gff_file, 'r') as in_handle:
            for rec in GFF.parse(in_handle):
                contig_id = rec.id
                self.chromosomes[contig_id] = Chromosome(
                    id=contig_id, species=self.species, version=self.version)


class SimpleRangePair(object):
    def __init__(self, rangeA, rangeB, score=None):
        """range is ChrLoci, most time rangeA is strand + """
        self.rangeA = rangeA
        self.rangeB = rangeB
        self.score = score


class BlastHspRecord(SimpleRangePair):
    def __init__(self, rangeA, rangeB, hsp_id, pid):
        super(BlastHspRecord, self).__init__(rangeA, rangeB, float(pid))
        self.query = self.rangeA
        self.subject = self.rangeB
        self.hsp_id = int(hsp_id)
        self.pid = float(pid)


class HomoPredictResults(object):
    def __init__(self, query_gene=None, subject_species=None, hit_gene_list=None):
        self.query_gene = query_gene
        self.subject_species = subject_species
        self.hit_gene_list = hit_gene_list


def fancy_name_parse(input_string):
    match_obj = re.match(r'^(\S+):(\d+)-(\d+)$', input_string)
    if match_obj:
        contig_name, c_start, c_end = match_obj.groups()
        strand = "."

    match_obj = re.match(r'^(\S+):(\d+)-(\d+):(\S+)$', input_string)
    if match_obj:
        contig_name, c_start, c_end, strand = match_obj.groups()

    start = min(int(c_start), int(c_end))
    end = max(int(c_start), int(c_end))

    return contig_name, start, end, strand


def section_of_chr_loci(chr_loci1, chr_loci2):
    """
    chr_loci1 = ChrLoci(chr_id='C000N', start=100, end=1000, strand="+")
    chr_loci2 = ChrLoci(chr_id='C000N', start=900, end=1500, strand="+")
    chr_loci3 = ChrLoci(chr_id='C000N', start=1100, end=1500, strand="+")
    chr_loci4 = ChrLoci(chr_id='C000N', start=900, end=1500, strand="-")

    section_of_chr_loci(chr_loci1, chr_loci2)
    Out: (True, (900, 1000))

    section_of_chr_loci(chr_loci1, chr_loci4)
    Out: (False, None)
    """

    if chr_loci1.chr_id == chr_loci2.chr_id:
        if (not chr_loci1.strand is None) and (not chr_loci2.strand is None):
            if chr_loci1.strand == chr_loci2.strand:
                return section(chr_loci1.range, chr_loci2.range, int_flag=True)
            else:
                return False, None
        else:
            return section(chr_loci1.range, chr_loci2.range, int_flag=True)
    else:
        return False, None


def cluster_of_chr_loci(chr_loci_list, overlap_threshold=0.0, use_strand=True):
    """
    chr_loci1 = ChrLoci(chr_id='C000N', start=100, end=1000, strand="+")
    chr_loci2 = ChrLoci(chr_id='C000N', start=900, end=1500, strand="+")
    chr_loci3 = ChrLoci(chr_id='C000N', start=1100, end=1500, strand="+")
    chr_loci4 = ChrLoci(chr_id='C000N', start=900, end=1500, strand="-")

    chr_loci_list = [chr_loci1,chr_loci2,chr_loci3,chr_loci4]

    cluster_of_chr_loci(chr_loci_list, overlap_threshold=0.0, use_strand=True)
    Out:
    {'C000N': {'+': OrderedDict([('group_1',
                    {'range': [(100, 1500)],
                     'list': [<__main__.ChrLoci at 0x7f29c328d3c8>,
                      <__main__.ChrLoci at 0x7f29c328d2b0>,
                      <__main__.ChrLoci at 0x7f29c328d4e0>]})]),
      '-': OrderedDict([('group_1',
                    {'range': [(900, 1500)],
                     'list': [<__main__.ChrLoci at 0x7f29c328df98>]})]),
      '.': OrderedDict()}}

    """

    if use_strand:
        data_dict = OrderedDict()
        for chr_loci in chr_loci_list:
            if chr_loci.chr_id not in data_dict:
                data_dict[chr_loci.chr_id] = {"+": {}, "-": {}, ".": {}}
            data_dict[chr_loci.chr_id][chr_loci.strand][chr_loci] = (
                chr_loci.start, chr_loci.end)
    else:
        data_dict = OrderedDict()
        for chr_loci in chr_loci_list:
            if chr_loci.chr_id not in data_dict:
                data_dict[chr_loci] = {".": {}}
            data_dict[chr_loci.chr_id][chr_loci.strand][chr_loci] = (
                chr_loci.start, chr_loci.end)

    for chr_id in data_dict:
        for strand in data_dict[chr_id]:
            data_dict[chr_id][strand] = group_by_intervals_with_overlap_threshold(data_dict[chr_id][strand],
                                                                                  overlap_threshold=overlap_threshold)

    return data_dict


def ft2cl(feature_location, chr_id):
    """
    create ChrLoci by FeatureLocation from BCBio
    """
    return ChrLoci(chr_id=chr_id, strand=feature_location.strand, start=feature_location.start + 1,
                   end=feature_location.end)


def cl2ft(chr_loci):
    """
    create FeatureLocation from BCBio by ChrLoci
    """
    if chr_loci.strand == "+" or chr_loci.strand == 1:
        strand = 1
    elif chr_loci.strand == "-" or chr_loci.strand == -1:
        strand = -1
    else:
        strand = 0

    return FeatureLocation(chr_loci.start - 1, chr_loci.end, strand=strand)


def sf2gf(sf, chr_id):
    """
    create GenomeFeature by SeqFeature from BCBio
    """
    sf_cl = ft2cl(sf.location, chr_id)
    gf = GenomeFeature(id=sf.id, type=sf.type, chr_loci=sf_cl)
    gf.qualifiers = sf.qualifiers

    # parse sub_feature
    if hasattr(sf, 'sub_features') and len(sf.sub_features) != 0:
        gf.sub_features = []
        for sub_sf in sf.sub_features:
            gf.sub_features.append(sf2gf(sub_sf, chr_id))

    return gf


def gf2sf(gf, source=None):
    """
    create SeqFeature from BCBio by GenomeFeature
    """
    fl = cl2ft(gf.chr_loci)

    qualifiers = gf.qualifiers
    if source is None:
        if 'source' in gf.qualifiers:
            source = gf.qualifiers['source']
        else:
            source = '.'

    qualifiers["source"] = source
    qualifiers["ID"] = gf.id

    sf = SeqFeature(fl, type=gf.type, qualifiers=qualifiers)

    # parse sub_feature
    sf.sub_features = []
    if hasattr(gf, 'sub_features') and not gf.sub_features is None:
        for sub_gf in gf.sub_features:
            sf.sub_features.append(gf2sf(sub_gf, source))

    sf.id = gf.id
    sf.qualifiers["ID"] = gf.id

    sf = deepcopy(sf)

    return sf


def read_gff_file(gff_file):
    feature_dict = OrderedDict()

    no_id = 0
    with open(gff_file, 'r') as in_handle:
        for rec in GFF.parse(in_handle):
            for feature in rec.features:
                new_feature = sf2gf(feature, rec.id)
                if new_feature.type not in feature_dict:
                    feature_dict[new_feature.type] = OrderedDict()
                if new_feature.id == '':
                    new_feature.id = 'NoID_%d' % no_id
                    no_id += 1
                feature_dict[new_feature.type][new_feature.id] = new_feature

    return feature_dict


def convert_dict_structure(feature_dict_from_read_gff_file):
    gene_dict = {}
    chr_dict = {}
    for gf_type in feature_dict_from_read_gff_file:
        for gf_id in feature_dict_from_read_gff_file[gf_type]:
            gf = feature_dict_from_read_gff_file[gf_type][gf_id]
            gene = Gene(from_gf=gf)
            gene.build_gene_seq()

            if gene.chr_id not in chr_dict:
                chr_dict[gene.chr_id] = {"+": {}, "-": {}}

            chr_dict[gene.chr_id][gene.strand][gf.id] = gene
            gene_dict[gf.id] = gene

    return gene_dict, chr_dict


def gene_compare(gf_chr_dict1, gf_chr_dict2, similarity_type='shorter_overlap_coverage', threshold=0.5):
    overlap_dict = {}
    num = 0
    for chr_id in gf_chr_dict1:
        overlap_dict[chr_id] = {}
        for strand in gf_chr_dict1[chr_id]:
            overlap_dict[chr_id][strand] = []
            if chr_id in gf_chr_dict2 and strand in gf_chr_dict2[chr_id]:

                gene_range_list = []
                g1_tmp = {(1, g1_id): (gf_chr_dict1[chr_id][strand][g1_id].start,
                                       gf_chr_dict1[chr_id][strand][g1_id].end) for g1_id in gf_chr_dict1[chr_id][strand]}

                g2_tmp = {(2, g2_id): (gf_chr_dict2[chr_id][strand][g2_id].start,
                                       gf_chr_dict2[chr_id][strand][g2_id].end) for g2_id in gf_chr_dict2[chr_id][strand]}

                gene_range_dict = merge_dict([g1_tmp, g2_tmp], False)

                grouped_dict = group_by_intervals_with_overlap_threshold(
                    gene_range_dict, overlap_threshold=0)

                overlap_pair = []

                for group_id in grouped_dict:
                    g_list = grouped_dict[group_id]["list"]
                    g1_list = [i[1] for i in g_list if i[0] == 1]
                    g2_list = [i[1] for i in g_list if i[0] == 2]

                    for g1_id in g1_list:
                        gf1 = gf_chr_dict1[chr_id][strand][g1_id]
                        for g2_id in g2_list:
                            gf2 = gf_chr_dict2[chr_id][strand][g2_id]
                            overlap_flag = False

                            for m1 in gf1.sub_features:
                                if overlap_flag:
                                    break
                                for m2 in gf2.sub_features:
                                    if overlap_flag:
                                        break
                                    if get_mRNA_overlap(m1, m2, similarity_type) > threshold:
                                        overlap_flag = True

                            if overlap_flag:
                                overlap_dict[chr_id][strand].append(
                                    (g1_id, g2_id))

    return overlap_dict


def read_bed_file(bed_file):
    file_info = tsv_file_parse(bed_file)

    feature_dict = OrderedDict()

    for i in file_info:
        id = file_info[i][3]
        chr_loci = ChrLoci(
            chr_id=file_info[i][0], strand=file_info[i][5], start=file_info[i][1], end=file_info[i][2])
        gf = GenomeFeature(id=id, chr_loci=chr_loci)
        feature_dict[gf.id] = gf

    return feature_dict


def write_gff_file(gf_list, output_gff_file, source=None, sort=False):
    rec_dict = OrderedDict()

    for gf in gf_list:
        if gf.chr_id not in rec_dict:
            rec = SeqRecord(Seq(""), gf.chr_id, description='')
            rec.features = []
            rec_dict[gf.chr_id] = rec
        sf = gf2sf(gf, source)
        sf = deepcopy(sf)
        rec_dict[gf.chr_id].features.append(sf)

    if sort:
        for ci in rec_dict:
            ft_list = rec_dict[ci].features
            ft_sorted_list = sorted(
                ft_list, key=lambda x: int(x.location.start))
            rec_dict[ci].features = ft_sorted_list

    rec_list = [rec_dict[i] for i in rec_dict]

    with open(output_gff_file, "a") as f:
        GFF.write(rec_list, f)


def feature_seq_extract(gf_list, genome_file, give_type):
    get_seq = ''
    strand = gf_list[0].strand

    if strand == "+":
        feature_list = sorted([gf for gf in gf_list if gf.type ==
                               give_type], key=lambda x: int(x.start), reverse=False)
    elif strand == '-':
        feature_list = sorted([gf for gf in gf_list if gf.type ==
                               give_type], key=lambda x: int(x.start), reverse=True)
    else:
        raise ValueError("strand chr error: %s" % strand)

    for gf in feature_list:
        if isinstance(genome_file, str):
            get_seq += gf.get_sequence(genome_file).seq
        else:
            get_seq += gf.get_sequence_quick(genome_file).seq

    return get_seq


def get_chrloci_overlap(chr_loci1, chr_loci2, similarity_type):
    if chr_loci1.chr_id != chr_loci2.chr_id:
        return 0.0

    if (not chr_loci1.strand is None) and (not chr_loci2.strand is None):
        if chr_loci1.strand != chr_loci2.strand:
            return 0.0

    chr_loci1_range = [(chr_loci1.start, chr_loci1.end)]
    chr_loci2_range = [(chr_loci2.start, chr_loci2.end)]

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
        chr_loci1_range, chr_loci2_range, similarity_type=similarity_type)

    return overlap_ratio


def get_mRNA_overlap(mRNA1, mRNA2, similarity_type):
    if mRNA1.chr_id != mRNA2.chr_id:
        return 0.0

    if mRNA1.strand != mRNA2.strand:
        return 0.0

    gf1_cds_interval = merge_intervals(
        [(j.start, j.end) for j in mRNA1.sub_features], True)
    gf2_cds_interval = merge_intervals(
        [(j.start, j.end) for j in mRNA2.sub_features], True)

    overlap_ratio, overlap_length, overlap = overlap_between_interval_set(
        gf1_cds_interval, gf2_cds_interval, similarity_type=similarity_type)

    return overlap_ratio


def cds_judgment(cds_sequence, parse_phase=True, keep_stop=False, return_cds=False):
    """make sure a cds seq is good for translate"""
    
    if parse_phase:
        phase = 0
        orf_dict = {}
        
        for i in range(3):
            cds_now = cds_sequence[i:]
            aa_seq = translate(cds_now, to_stop=False)
            if '*' in aa_seq:
                star_index = aa_seq.index('*')
                one_star_aa_seq = aa_seq[:star_index+1]
            else:
                one_star_aa_seq = aa_seq
            phase = i
            orf_dict[phase] = (phase, one_star_aa_seq, cds_now[:len(one_star_aa_seq)*3])

        best_phase = sorted(orf_dict, key=lambda x:len(orf_dict[x][1]), reverse=True)[0]

        phase, one_star_aa_seq, cds_now = orf_dict[best_phase] 

        if len(one_star_aa_seq) * 3 / len(cds_sequence) > 0.95:
            good_orf = True
        else:
            good_orf = False

        if not keep_stop and '*' in one_star_aa_seq:
            out_aa_seq = one_star_aa_seq[:-1]
            out_cds_now = cds_now[:-3]
        else:
            out_aa_seq = one_star_aa_seq
            out_cds_now = cds_now

        if good_orf and len(out_aa_seq) * 3 != len(out_cds_now):
            raise ValueError("cds length error")

        if return_cds:
            return good_orf, phase, out_aa_seq, out_cds_now
        else:
            return good_orf, phase, out_aa_seq
    else:
        aa_seq = translate(cds_sequence, to_stop=False)

        if '*' in aa_seq:
            star_index = aa_seq.index('*')
            one_star_aa_seq = aa_seq[:star_index+1]
        else:
            one_star_aa_seq = aa_seq

        good_orf = True if len(cds_sequence) % 3 == 0 and len(one_star_aa_seq) == len(cds_sequence) / 3 else False

        if not keep_stop and '*' in one_star_aa_seq:
            out_aa_seq = one_star_aa_seq[:-1]
            out_cds_now = cds_sequence[:-3]
        else:
            out_aa_seq = one_star_aa_seq
            out_cds_now = cds_sequence

        if good_orf and len(out_aa_seq) * 3 != len(out_cds_now):
            raise ValueError("cds length error")

        if return_cds:
            return good_orf, None, out_aa_seq, out_cds_now
        else:
            return good_orf, None, out_aa_seq


def gf_rename(raw_gf, new_gf_name, chr_new_name, new_qualifiers=None, new_sub_features=None):
    new_gf = deepcopy(raw_gf)

    new_gf.chr_id = chr_new_name
    new_chr_loci = ChrLoci(chr_id=chr_new_name, strand=raw_gf.chr_loci.strand, start=raw_gf.chr_loci.start,
                           end=raw_gf.chr_loci.end)
    new_gf.chr_loci = new_chr_loci
    new_gf.chr_loci.get_fancy_name()
    new_gf.fancy_name = new_gf.chr_loci.fancy_name

    new_gf.id = new_gf_name
    new_gf.old_id = raw_gf.id

    for i in raw_gf.qualifiers:
        if i not in new_qualifiers:
            new_qualifiers[i] = raw_gf.qualifiers[i]

    new_gf.qualifiers = new_qualifiers

    new_gf.sub_features = new_sub_features

    return new_gf


def sub_gf_traveler(gf):
    if gf.sub_features and len(gf.sub_features) > 0:
        all_sub_gfs = []
        for sub_gf in gf.sub_features:
            all_sub_gfs.append(sub_gf)
            all_sub_gfs.extend(sub_gf_traveler(sub_gf))
        return all_sub_gfs
    else:
        return []


def mRNA_rename(raw_mRNA, mRNA_new_name, gene_new_name=None, chr_new_name=None):
    # new_qualifiers
    if gene_new_name:
        new_qualifiers = {
            'ID': [mRNA_new_name],
            'Name': [mRNA_new_name],
            'Parent': [gene_new_name],
            'source': ['RENAME'],
            'old_id': [raw_mRNA.id],
        }
    else:
        new_qualifiers = {
            'ID': [mRNA_new_name],
            'Name': [mRNA_new_name],
            'source': ['RENAME'],
            'old_id': [raw_mRNA.id],
        }

    # new_sub_features
    cds_num = 0
    exon_num = 0
    futr_num = 0
    tutr_num = 0

    new_sub_features = []
    for gf in raw_mRNA.sub_features:
        if gf.type == 'CDS':
            cds_num += 1
            gf_id = mRNA_new_name + ".cds." + str(cds_num)
        if gf.type == 'exon':
            exon_num += 1
            gf_id = mRNA_new_name + ".exon." + str(exon_num)
        if gf.type == 'five_prime_UTR':
            futr_num += 1
            gf_id = mRNA_new_name + ".5utr." + str(futr_num)
        if gf.type == 'three_prime_UTR':
            tutr_num += 1
            gf_id = mRNA_new_name + ".3utr." + str(tutr_num)

        gf_new_qualifiers = {
            'ID': [gf_id],
            'Name': [gf_id],
            'Parent': [mRNA_new_name],
            'source': ['RENAME'],
            'old_id': [gf.id],
        }

        if gf.type == 'CDS':
            if 'phase' in gf.qualifiers:
                gf_new_qualifiers['phase'] = gf.qualifiers['phase']

        if chr_new_name:
            new_gf = gf_rename(gf, gf_id, chr_new_name,
                               new_qualifiers=gf_new_qualifiers)
        else:
            new_gf = gf_rename(gf, gf_id, raw_mRNA.chr_id,
                               new_qualifiers=gf_new_qualifiers)

        new_sub_features.append(new_gf)

    # new_mRNA
    if chr_new_name:
        new_mRNA = gf_rename(raw_mRNA, mRNA_new_name, chr_new_name, new_qualifiers=new_qualifiers,
                             new_sub_features=new_sub_features)
    else:
        new_mRNA = gf_rename(raw_mRNA, mRNA_new_name, raw_mRNA.chr_id, new_qualifiers=new_qualifiers,
                             new_sub_features=new_sub_features)

    return new_mRNA


def gene_rename(raw_gene, gene_new_name, chr_new_name):
    # new_qualifiers
    new_qualifiers = {
        'ID': [gene_new_name],
        'Name': [gene_new_name],
        'source': ['RENAME'],
        'old_id': [raw_gene.id],
    }

    # new_sub_features
    mRNA_list = [gf for gf in raw_gene.sub_features if gf.type == 'mRNA']

    [i.sgf_len() for i in mRNA_list]

    mRNA_list = sorted(
        mRNA_list, key=lambda x: x.sgf_len_dir['CDS'], reverse=True)
    mRNA_number = 1
    new_mRNA_list = []
    for old_mRNA in mRNA_list:
        mRNA_new_name = gene_new_name + "." + str(mRNA_number)
        new_mRNA = mRNA_rename(old_mRNA, mRNA_new_name,
                               gene_new_name, chr_new_name)
        new_mRNA_list.append(new_mRNA)
        mRNA_number += 1

    new_sub_features = new_mRNA_list

    # new_gene
    new_gene = gf_rename(raw_gene, gene_new_name, chr_new_name, new_qualifiers=new_qualifiers,
                         new_sub_features=new_sub_features)

    return new_gene


def genome_rename(raw_genome, rename_prefix, keep_raw_contig_id=False):
    raw_genome.build_index()
    # contig rename
    ctg_num_order = len(str(len(raw_genome.chromosomes)))
    ctg_name_template = rename_prefix + ("C%0" + str(ctg_num_order) + "d")
    # gene rename
    gene_num_order = len(str(len(raw_genome.feature_dict['gene'])))

    if raw_genome.genome_file is None:
        ctg_id_sorted_list = list(raw_genome.chromosomes.keys())
    else:
        ctg_id_sorted_list = sorted(list(raw_genome.chromosomes.keys()), key=lambda x: raw_genome.chromosomes[x].len,
                                    reverse=True)

    new_chr_dict = OrderedDict()
    new_gene_dict = OrderedDict()
    chr_num = 0

    chr_rename_dict = {}
    gene_rename_dict = {}

    for raw_ctg_id in ctg_id_sorted_list:
        chr_old = raw_genome.chromosomes[raw_ctg_id]
        if not keep_raw_contig_id:
            chr_new_name = ctg_name_template % chr_num
        else:
            chr_new_name = raw_ctg_id

        chr_rename_dict[raw_ctg_id] = chr_new_name

        chr_num += 1
        chr_new = Chromosome(id=chr_new_name, species=chr_old.species, version=chr_old.version,
                             seq=chr_old.seq, length=chr_old.len)

        chr_new.old_id = chr_old.id

        new_chr_dict[chr_new_name] = chr_new

        chr_gene_feature_dict = chr_old.feature_dict['gene']
        gene_id_sort_list = sorted(
            list(chr_gene_feature_dict.keys()), key=lambda x: chr_gene_feature_dict[x].start)

        gene_num = 0
        if not keep_raw_contig_id:
            gene_name_template = chr_new_name + \
                ("G%0" + str(gene_num_order) + "d")
        else:
            gene_name_template = ctg_name_template % chr_num + \
                ("G%0" + str(gene_num_order) + "d")
        for raw_gene_id in gene_id_sort_list:
            new_gene = gene_rename(
                chr_gene_feature_dict[raw_gene_id], gene_name_template % gene_num, chr_new_name)
            gene_num += 1
            new_gene_dict[new_gene.id] = new_gene
            gene_rename_dict[raw_gene_id] = new_gene.id

        # print('chr %s with %d gene!' % (chr_new_name, len(chr_gene_feature_dict)))

    new_genome = Genome(
        id=rename_prefix, species=raw_genome.species, version=raw_genome.version)
    new_genome.chromosomes = new_chr_dict
    new_genome.feature_dict = {'gene': new_gene_dict}
    new_genome.build_index()

    return new_genome, chr_rename_dict, gene_rename_dict


def display_features(gf, serial_id, parent_serial_id, top_feature_type, output_dict={}, deep_level=0):

    my_serial_id = deepcopy(serial_id)
    son_serial_id_list = []
    if gf.sub_features is not None:
        for sub_gf in gf.sub_features:
            serial_id += 1
            son_serial_id_list.append(serial_id)
            serial_id = display_features(sub_gf, serial_id, my_serial_id,
                                         top_feature_type, output_dict, deep_level + 1)

    # print(my_serial_id, gf.chr_loci, gf.type)
    output_dict[my_serial_id] = (gf.id, gf.type, gf, gf.qualifiers,
                                 parent_serial_id, son_serial_id_list, deep_level, top_feature_type)
    if deep_level == 0:
        return output_dict
    else:
        return serial_id


# from store gf into sqlite3

def add_gfs_into_db(gf_list, db_file_name):

    table_name = "gene_features_table"
    col_name_list = ['gf_name', 'type', 'contig_name',
                     'start', 'end', 'strand', 'gf_pickle_dump_obj']

    table_columns_dict = {table_name: col_name_list}

    def parse_function(gf):
        return {table_name: (gf.id, gf.type, gf.chr_id, gf.start, gf.end, gf.strand, sc.pickle_dump_obj(gf))}

    sc.build_database(gf_list, parse_function,
                      table_columns_dict, db_file_name, add_mode=True)

    try:
        sc.drop_index(db_file_name, table_name + '_index')
    except:
        pass
    
    sc.build_index(db_file_name, table_name, 'gf_name')

    return db_file_name


def get_gf_name_list_from_db(db_file_name):
    table_name = "gene_features_table"
    gf_name_list = [i[0] for i in sc.sqlite_select(
        db_file_name, table_name, column_list=['gf_name'])]
    return gf_name_list


def get_gf_from_db(db_file_name, contig_name=None, start=None, end=None, strand=None, type=None, gf_name_list=None):

    conn = sqlite3.connect(db_file_name)

    if contig_name is None and start is None and end is None and strand is None and type is None:
        if gf_name_list is None:
            content = conn.execute(
                "SELECT gf_pickle_dump_obj FROM \"gene_features_table\"").fetchall()
        else:
            content = conn.execute(
                "SELECT gf_pickle_dump_obj FROM \"gene_features_table\" WHERE \"gf_name\" IN " + tuple(gf_name_list).__str__()).fetchall()
    else:
        prefix_string = "SELECT gf_pickle_dump_obj FROM \"gene_features_table\" WHERE "
        args_list = []

        if contig_name:
            prefix_string += "\"contig_name\" = ? AND "
            args_list.append(contig_name)
        if strand:
            prefix_string += "\"strand\" = ? AND "
            args_list.append(strand)
        if not start is None:
            prefix_string += "\"end\" >= ? AND "
            args_list.append(start)
        if not end is None:
            prefix_string += "\"start\" <= ? AND "
            args_list.append(end)
        if type:
            prefix_string += "\"type\" = ? AND "
            args_list.append(type)

        cmd_string = prefix_string.rstrip("AND ")

        content = conn.execute(cmd_string, tuple(args_list)).fetchall()

    conn.close()

    gf_dict = OrderedDict()
    for i in content:
        gf = sc.pickle_load_obj(i[0])
        gf_dict[gf.id] = gf

    return gf_dict
    
# def add_gfs_into_db(gf_list, db_file_name, max_table_row=10000):
#     """

#     sqlite3 database

#     Table: meta_table

#     | id | table_name | top_level_type |                                   types | deep_level | record_num |
#     |---:|-----------:|----------------|----------------------------------------:|-----------:|-----------:|
#     |  1 |      A_0_0 |           gene |                                    gene |          0 |          1 |
#     |  2 |      A_1_0 |           gene |                                    mRNA |          1 |          1 |
#     |  3 |      A_2_0 |           gene | CDS;exon;five_prime_UTR;three_prime_UTR |          2 |         12 |

#     Table: A_0_0

#     | id |             gf_name | type |   contig_name |   start | end     | strand | daughter      | qualifiers                                                                                                         |
#     |---:|--------------------:|-----:|--------------:|--------:|---------|--------|---------------|--------------------------------------------------------------------------------------------------------------------|
#     |  0 | T267555N0C000G00075 | gene | T267555N0C000 | 1117615 | 1122372 | +      | {'A1_0':'0'}  | {'ID': ['T267555N0C000G00075'], 'Name': ['T267555N0C000G00075'], 'old_id': ['C000N0078E0'], 'source': ['RENAME']}  |

#     Table: A1_0

#     | id |               gf_name | type |   contig_name |   start | end     | strand | daughter        | qualifiers                                                                                                                                                 |
#     |---:|----------------------:|-----:|--------------:|--------:|---------|--------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
#     |  0 | T267555N0C000G00075.1 | mRNA | T267555N0C000 | 1117615 | 1122372 | +      | {'A2_0':'0-11'} | {'ID': ['T267555N0C000G00075.1'], 'Name': ['T267555N0C000G00075.1'], 'Parent': ['T267555N0C000G00075'], 'old_id': ['C000N0078E0.1'], 'source': ['RENAME']} |

#     Table: A2_0

#     | id |                      gf_name |            type |   contig_name |   start |     end | strand | daughter   | qualifiers                                                                                                                                                                                     |
#     |---:|-----------------------------:|----------------:|--------------:|--------:|--------:|-------:|-----------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
#     |  0 | T267555N0C000G00075.1.5utr.1 |  five_prime_UTR | T267555N0C000 | 1117615 | 1117664 |      + |            |              {'ID': ['T267555N0C000G00075.1.5utr.1'], 'Name': ['T267555N0C000G00075.1.5utr.1'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.utr5p1'], 'source': ['RENAME']} |
#     |  1 | T267555N0C000G00075.1.exon.1 |            exon | T267555N0C000 | 1117615 | 1118379 |      + |            |              {'ID': ['T267555N0C000G00075.1.exon.1'], 'Name': ['T267555N0C000G00075.1.exon.1'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.exon1'], 'source': ['RENAME']}, |
#     |  2 | T267555N0C000G00075.1.exon.2 |            exon | T267555N0C000 | 1118949 | 1119409 |      + |            |              {'ID': ['T267555N0C000G00075.1.exon.2'], 'Name': ['T267555N0C000G00075.1.exon.2'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.exon2'], 'source': ['RENAME']}, |
#     |  3 | T267555N0C000G00075.1.exon.3 |            exon | T267555N0C000 | 1120911 | 1121101 |      + |            |              {'ID': ['T267555N0C000G00075.1.exon.3'], 'Name': ['T267555N0C000G00075.1.exon.3'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.exon3'], 'source': ['RENAME']}, |
#     |  4 | T267555N0C000G00075.1.exon.4 |            exon | T267555N0C000 | 1121226 | 1121292 |      + |            |              {'ID': ['T267555N0C000G00075.1.exon.4'], 'Name': ['T267555N0C000G00075.1.exon.2'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.exon4'], 'source': ['RENAME']}, |
#     |  5 | T267555N0C000G00075.1.exon.5 |            exon | T267555N0C000 | 1121780 | 1122372 |      + |            |              {'ID': ['T267555N0C000G00075.1.exon.5'], 'Name': ['T267555N0C000G00075.1.exon.5'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.exon5'], 'source': ['RENAME']}, |
#     |  6 |  T267555N0C000G00075.1.cds.1 |             CDS | T267555N0C000 | 1117665 | 1118379 |      + |            | {'ID': ['T267555N0C000G00075.1.cds.1'], 'Name': ['T267555N0C000G00075.1.cds.1'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.cds1'], 'source': ['RENAME'], 'phase': ['0']}, |
#     |  7 |  T267555N0C000G00075.1.cds.2 |             CDS | T267555N0C000 | 1118949 | 1119409 |      + |            | {'ID': ['T267555N0C000G00075.1.cds.2'], 'Name': ['T267555N0C000G00075.1.cds.2'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.cds2'], 'source': ['RENAME'], 'phase': ['2']}, |
#     |  8 |  T267555N0C000G00075.1.cds.3 |             CDS | T267555N0C000 | 1120911 | 1121101 |      + |            | {'ID': ['T267555N0C000G00075.1.cds.3'], 'Name': ['T267555N0C000G00075.1.cds.3'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.cds3'], 'source': ['RENAME'], 'phase': ['0']}, |
#     |  9 |  T267555N0C000G00075.1.cds.4 |             CDS | T267555N0C000 | 1121226 | 1121292 |      + |            | {'ID': ['T267555N0C000G00075.1.cds.4'], 'Name': ['T267555N0C000G00075.1.cds.4'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.cds4'], 'source': ['RENAME'], 'phase': ['1']}, |
#     | 10 |  T267555N0C000G00075.1.cds.5 |             CDS | T267555N0C000 | 1121780 | 1121821 |      + |            | {'ID': ['T267555N0C000G00075.1.cds.5'], 'Name': ['T267555N0C000G00075.1.cds.5'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.cds5'], 'source': ['RENAME'], 'phase': ['0']}, |
#     | 11 | T267555N0C000G00075.1.3utr.1 | three_prime_UTR | T267555N0C000 | 1121822 | 1122372 |      + |            |             {'ID': ['T267555N0C000G00075.1.3utr.1'], 'Name': ['T267555N0C000G00075.1.3utr.1'], 'Parent': ['T267555N0C000G00075.1'], 'old_id': ['C000N0078E0.1.utr3p1'], 'source': ['RENAME']}, |

#     """

#     table_list = sc.check_sql_table(db_file_name)

#     if "meta_table" not in table_list:
#         sc.init_sql_db(db_file_name, "meta_table", [
#                        'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], True)

#         table_list = sc.check_sql_table(db_file_name)

#     # meta_info
#     meta_table_dict = {}
#     meta_info = list(sc.sqlite_select(db_file_name, 'meta_table'))
#     for id_tmp, table_name, top_type, types, deep_level, record_num in meta_info:
#         if record_num == 0:
#             sc.drop_table(db_file_name, table_name)
#             try:
#                 sc.drop_index(db_file_name, table_name+"_index")
#             except:
#                 pass
#             sc.sqlite_delete(db_file_name, 'meta_table', 'id', (id_tmp, ))
#             continue

#         if top_type not in meta_table_dict:
#             meta_table_dict[top_type] = {}
#         if deep_level not in meta_table_dict[top_type]:
#             meta_table_dict[top_type][deep_level] = {}

#         meta_table_dict[top_type][deep_level][table_name] = record_num

#     # read gf detail info
#     gf_detail_dict = {}
#     for gf in gf_list:
#         display_features(gf, len(gf_detail_dict), None,
#                          gf.type, gf_detail_dict, 0)

#     # top level type
#     top_level_type_list = list(
#         set([gf_detail_dict[i][1] for i in gf_detail_dict if gf_detail_dict[i][6] == 0]))

#     # build new top level type table
#     builded_type_list = list(meta_table_dict.keys())

#     new_type_list = list(set(top_level_type_list)-set(builded_type_list))

#     new_type_depth = {}
#     for i in gf_detail_dict:
#         top_type = gf_detail_dict[i][7]
#         depth = gf_detail_dict[i][6]
#         if top_type not in new_type_depth:
#             new_type_depth[top_type] = depth
#         if depth >= new_type_depth[top_type]:
#             new_type_depth[top_type] = depth

#     prefix_num = ord('A') + len(builded_type_list)
#     meta_table_row_num = sc.sql_table_row_num(db_file_name, 'meta_table')
#     for new_type in new_type_list:
#         prefix = chr(prefix_num)
#         meta_table_dict[new_type] = {}

#         # build first table
#         for i in range(new_type_depth[new_type] + 1):
#             first_table_name = "%s_%d_%d" % (prefix, i, 0)
#             meta_table_dict[new_type][i] = {first_table_name: 0}
#             sc.init_sql_db(db_file_name, first_table_name, [
#                            'id', 'gf_name', 'type', 'contig_name', 'start', 'end', 'strand', 'daughter', 'qualifiers'], False)

#         # add record in meta table
#             if i == 0:
#                 sc.insert_one_record_to_sql_table([meta_table_row_num, first_table_name, new_type, new_type, i, 0], [
#                                                   'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")
#             else:
#                 sc.insert_one_record_to_sql_table([meta_table_row_num, first_table_name, new_type, '', i, 0], [
#                                                   'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")
#             meta_table_row_num += 1

#         prefix_num += 1

#     # writing

#     for top_type in top_level_type_list:
#         prefix = list(meta_table_dict[top_type][0].keys())[0][0]

#         for deep_level in sorted(list(meta_table_dict[top_type].keys()), reverse=True):
#             sub_gf_dict = {i: gf_detail_dict[i] for i in gf_detail_dict if gf_detail_dict[i]
#                            [-1] == top_type and gf_detail_dict[i][-2] == deep_level}
#             sub_gf_keys = list(sub_gf_dict.keys())

#             # last unfull table
#             last_table_name = None

#             for i in range(len(meta_table_dict[top_type][deep_level])):
#                 table_name = "%s_%d_%d" % (prefix, deep_level, i)
#                 if meta_table_dict[top_type][deep_level][table_name] >= max_table_row:
#                     continue
#                 else:
#                     last_table_name = "%s_%d_%d" % (prefix, deep_level, i)

#             if last_table_name is None:
#                 last_table_name = "%s_%d_%d" % (prefix, deep_level, len(
#                     meta_table_dict[top_type][deep_level]))
#                 meta_table_dict[top_type][deep_level][last_table_name] = 0
#                 sc.init_sql_db(db_file_name, last_table_name, [
#                                'id', 'gf_name', 'type', 'contig_name', 'start', 'end', 'strand', 'daughter', 'qualifiers'], False)

#                 if deep_level == 0:
#                     sc.insert_one_record_to_sql_table([meta_table_row_num, last_table_name, top_type, top_type, deep_level, 0], [
#                         'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")
#                 else:
#                     sc.insert_one_record_to_sql_table([meta_table_row_num, last_table_name, top_type, '', deep_level, 0], [
#                         'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")

#                 meta_table_row_num += 1

#             record_num_already = meta_table_dict[top_type][deep_level][last_table_name]

#             # rename id map
#             rename_map_dict = {}

#             id_start = record_num_already
#             table_start = len(meta_table_dict[top_type][deep_level]) - 1
#             table_gf_keys_dict = {}
#             for i in sub_gf_keys:
#                 if id_start < max_table_row:
#                     rename_map_dict[i] = (table_start, id_start)
#                     id_start += 1
#                 else:
#                     table_start += 1
#                     new_table_name = "%s_%d_%d" % (
#                         prefix, deep_level, table_start)
#                     meta_table_dict[top_type][deep_level][new_table_name] = 0
#                     sc.init_sql_db(db_file_name, new_table_name, [
#                                    'id', 'gf_name', 'type', 'contig_name', 'start', 'end', 'strand', 'daughter', 'qualifiers'], False)

#                     if deep_level == 0:
#                         sc.insert_one_record_to_sql_table([meta_table_row_num, new_table_name, top_type, top_type, deep_level, 0], [
#                             'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")
#                     else:
#                         sc.insert_one_record_to_sql_table([meta_table_row_num, new_table_name, top_type, '', deep_level, 0], [
#                             'id', 'table_name', 'top_level_type', 'types', 'deep_level', 'record_num'], db_file_name, "meta_table")

#                     meta_table_row_num += 1
#                     id_start = 0
#                     rename_map_dict[i] = (table_start, id_start)
#                     id_start += 1

#             rename_map_dict_hash = {}
#             for i in rename_map_dict:
#                 table_num, new_key_id = rename_map_dict[i]
#                 table_name = "%s_%d_%d" % (prefix, deep_level, table_num)
#                 if table_name not in rename_map_dict_hash:
#                     rename_map_dict_hash[table_name] = {}
#                 rename_map_dict_hash[table_name][i] = new_key_id

#             for table_name in rename_map_dict_hash:
#                 waitting_for_load = []
#                 for old_gf_key in rename_map_dict_hash[table_name]:
#                     new_gf_key = rename_map_dict_hash[table_name][old_gf_key]
#                     gf_info = sub_gf_dict[old_gf_key]

#                     # daughter_string
#                     if deep_level == max(list(meta_table_dict[top_type].keys())):
#                         daughter_string = json.dumps([])
#                     else:
#                         daughter_string = json.dumps(
#                             [last_rename_map_dict[i] for i in gf_info[5]])

#                     # qualifiers_string
#                     qualifiers_string = json.dumps(gf_info[3])

#                     waitting_for_load.append((new_gf_key, gf_info[0], gf_info[1], gf_info[2].chr_id,
#                                               gf_info[2].start, gf_info[2].end, gf_info[2].strand, daughter_string, qualifiers_string))

#                 sc.sqlite_write(waitting_for_load, db_file_name, table_name, [
#                                 'id', 'gf_name', 'type', 'contig_name', 'start', 'end', 'strand', 'daughter', 'qualifiers'])

#             last_rename_map_dict = rename_map_dict

#     # stat row number and table types

#     for id_tmp, table_name, top_type, types, deep_level, record_num in sc.sqlite_select(db_file_name, 'meta_table'):

#         table_row_number_now = sc.sql_table_row_num(db_file_name, table_name)
#         type_list = list(set([i[0] for i in sc.sqlite_select(
#             db_file_name, table_name, column_list=['type'])]))
#         type_string = printer_list(type_list, sep=',')

#         conn = sqlite3.connect(db_file_name)
#         # print("UPDATE %s SET %s = %d WHERE id = %d" % ('meta_table', 'record_num', table_row_number_now, id_tmp))
#         conn.execute("UPDATE %s SET %s = %d WHERE id = %d" %
#                      ('meta_table', 'record_num', table_row_number_now, id_tmp))
#         conn.execute("UPDATE %s SET %s = \"%s\" WHERE id = %d" %
#                      ('meta_table', 'types', type_string, id_tmp))
#         conn.commit()
#         conn.close()

#     # build index

#     conn = sqlite3.connect(db_file_name)
#     for id_tmp, table_name, top_type, types, deep_level, record_num in sc.sqlite_select(db_file_name, 'meta_table'):
#         try:
#             conn.execute("DROP INDEX %s_index" % table_name)
#         except:
#             pass
#         # print("CREATE UNIQUE INDEX %s_index on %s (\"id\")" % (table_name, table_name))
#         conn.execute("CREATE UNIQUE INDEX %s_index on %s (\"id\")" %
#                      (table_name, table_name))
#     conn.commit()
#     conn.close()


# def get_gf_db_meta_dict(db_file_name):
#     meta_table_dict = {}

#     meta_info = list(sc.sqlite_select(db_file_name, 'meta_table'))
#     for id_tmp, table_name, top_type, types, deep_level, record_num in meta_info:

#         if top_type not in meta_table_dict:
#             meta_table_dict[top_type] = {}
#         if deep_level not in meta_table_dict[top_type]:
#             meta_table_dict[top_type][deep_level] = {}

#         meta_table_dict[top_type][deep_level][table_name] = record_num

#     for type_tmp in list(meta_table_dict.keys()):
#         deep_list = sorted(list(meta_table_dict[type_tmp].keys()))
#         meta_table_dict[type_tmp]['deep_list'] = deep_list
#         prefix = list(meta_table_dict[top_type][0].keys())[0][0]
#         meta_table_dict[type_tmp]['prefix'] = prefix

#     return meta_table_dict


# def gf_info_retrieval(gf_db_info_tuple, deep_level, prefix, db_file_name):
#     id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers = gf_db_info_tuple

#     sub_features = []
#     lower_deep_level = deep_level + 1
#     for lower_deep_table_id, uniq_id in json.loads(daughter):
#         lower_deep_table = prefix + "_" + \
#             str(lower_deep_level) + "_" + str(lower_deep_table_id)
#         sub_gf_db_info_tuple = sc.sqlite_select(
#             db_file_name, lower_deep_table, key_name='id', value_tuple=(uniq_id,))[0]
#         sub_gf = gf_info_retrieval(
#             sub_gf_db_info_tuple, lower_deep_level, prefix, db_file_name)
#         sub_features.append(sub_gf)

#     chr_loci = ChrLoci(chr_id=contig_name, strand=strand, start=start, end=end)
#     gf = GenomeFeature(id=gf_name, type=type_tmp, chr_loci=chr_loci,
#                        qualifiers=json.loads(qualifiers), sub_features=sub_features)
#     return gf


# def get_gf_from_db(db_file_name, gf_id_list=[], top_level_type='gene'):
#     if len(gf_id_list) > 0:

#         meta_table_dict = get_gf_db_meta_dict(db_file_name)

#         top_tables = meta_table_dict[top_level_type][0]

#         top_gf_list = []
#         for table in top_tables:
#             for gf_info in sc.sqlite_select(db_file_name, table, key_name='gf_name', value_tuple=gf_id_list):
#                 top_gf_list.append(gf_info_retrieval(
#                     gf_info, 0, meta_table_dict[top_level_type]['prefix'], db_file_name))

#         top_gf_dict = {}
#         for gf in top_gf_list:
#             top_gf_dict[gf.id] = gf

#     else:
#         meta_table_dict = get_gf_db_meta_dict(db_file_name)

#         # read mRNA info
#         ev_args_list = []
#         ev_args_id_list = []

#         for table in meta_table_dict[top_level_type][0]:
#             # print(table_name)
#             sql_cmd_string = 'SELECT * FROM %s' % table

#             data_list = sc.sqlite_execute(sql_cmd_string, db_file_name)
#             for gf_info in data_list:
#                 ev_args_list.append(
#                     (gf_info, 0, meta_table_dict[top_level_type]['prefix'], db_file_name))

#                 id_tmp, gf_name, type_tmp, contig_name, start, end, strand, daughter, qualifiers = gf_info

#                 ev_args_id_list.append(gf_name)

#         ev_output = multiprocess_running(
#             gf_info_retrieval, ev_args_list, 56, silence=True, args_id_list=ev_args_id_list)

#         top_gf_dict = {}
#         for i in ev_output:
#             top_gf_dict[i] = ev_output[i]['output']

#     return top_gf_dict


if __name__ == '__main__':
    # genome info input
    genome_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.genome.v1.1.fasta'
    gff_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.v1.1.gff3'
    cds_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.cds.v1.1.fasta'
    pt_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.pt.v1.1.fasta'
    cDNA_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.cDNA.v1.1.fasta'

    # read and write a gff file
    feature_dict = read_gff_file(gff_file)
    """
    feature_dict = {
        "gene": {
            "gene1": gf_object
        } 
    }
    """
    gf_list = []
    for type_tmp in feature_dict:
        for gf_id in feature_dict[type_tmp]:
            gf_list.append(feature_dict[type_tmp][gf_id])

    write_gff_file(
        gf_list, '/lustre/home/xuyuxing/Database/Gel/genome/annotation/base_on_yuan/test.gff')

    # create a genome object
    Cau_genome = Genome(id='Cau', species='267555', version='v1.1', genome_file=genome_file, gff_file=gff_file,
                        cds_file=cds_file, cDNA_file=cDNA_file, aa_file=pt_file)

    # genome feature from genome object
    Cau_genome = Genome(id='Cau', species='267555', version='v1.1', genome_file=genome_file, gff_file=gff_file,
                        cds_file=cds_file, cDNA_file=cDNA_file, aa_file=pt_file)

    Cau_genome.genome_feature_parse()
    feature_dict = Cau_genome.feature_dict

    # search genome feature in a give range
    Cau_genome = Genome(id='Cau', species='267555', version='v1.1', genome_file=genome_file, gff_file=gff_file,
                        cds_file=cds_file, cDNA_file=cDNA_file, aa_file=pt_file)
    Cau_genome.genome_feature_parse()
    Cau_genome.genome_file_parse()  # or Cau_genome.get_chromosome_from_gff()
    Cau_genome.build_index()

    gene_list_in_range = Cau_genome.search("C000N:1-100000")

    # work on gene
    Cau_genome = Genome(id='Cau', species='267555', version='v1.1', genome_file=genome_file, gff_file=gff_file,
                        cds_file=cds_file, cDNA_file=cDNA_file, aa_file=pt_file)

    Cau_genome.genome_feature_parse()
    feature_dict = Cau_genome.feature_dict

    gene_id = 'C000N0008E0'
    gene = Gene(from_gf=feature_dict['gene'][gene_id])
    gene.build_gene_seq(genome_file)

    print(gene.model_aa_seq)

    # read a gff file into sqlite3 db
    gff_file = '/lustre/home/xuyuxing/Work/annotation_pipeline/Cau/1.EDTA/input.genome.fasta.mod.EDTA.intact.gff3'
    db_file_name = '/lustre/home/xuyuxing/Work/annotation_pipeline/Cau/tmp/input.genome.fasta.mod.EDTA.intact.gff3.db'

    gff_dict = read_gff_file(gff_file)

    gf_list = []
    for i in gff_dict:
        for j in gff_dict[i]:
            gf_list.append(gff_dict[i][j])

    add_gfs_into_db(gf_list, db_file_name)

    gf_name_list = get_gf_name_list_from_db(db_file_name)

    gf_dict = get_gf_from_db(db_file_name, gf_name_list=gf_name_list[:10])


    # gff_file = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/all_map/test/T267555N0.genome.gff3'
    # gff_file = '/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/maker_1M/Pae.results.gff'
    # db_file_name = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/all_map/test/Cau/test.gff.db'

    # gff_dict = read_gff_file(gff_file)

    # gf_list = []
    # for i in gff_dict:
    #     for j in gff_dict[i]:
    #         gf_list.append(gff_dict[i][j])

    # add_gfs_into_db(gf_list, db_file_name, max_table_row=10000)

    # gf_id_list = ['T42345N0C00046G00077_30', 'T42345N0C00046G00077_44',
    #               'T42345N0C00035G00003_60', 'T42345N0C00041G00074_56']

    # gf_dict = get_gf_from_db(gf_id_list, db_file_name)
