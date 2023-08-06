import sys
import re
from toolbiox.lib.common.math.interval import section, group_by_intervals_with_overlap_threshold
from toolbiox.lib.common.genome.seq_base import BioSeq, read_fasta_by_faidx
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from interlap import InterLap
from BCBio import GFF
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation


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


class ChrLoci(object):
    def __init__(self, chr_id=None, strand=None, start=None, end=None, chrome=None):
        self.chr_id = chr_id
        self.chrome = chrome

        if strand is None:
            self.strand = strand
        elif strand == "+" or str(strand) == '1':
            self.strand = "+"
        elif strand == "-" or str(strand) == '-1':
            self.strand = "-"

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
            self.fancy_name = "%s:%d-%d:%s" % (self.chr_id, self.start, self.end, self.strand)
        return self.fancy_name

    def __str__(self):
        try:
            self.get_fancy_name()
            return self.fancy_name
        except:
            return "No detail range"

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


def section_of_chr_loci(chr_loci1, chr_loci2):
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
    if use_strand:
        data_dict = {}
        for chr_loci in chr_loci_list:
            if chr_loci.chr_id not in data_dict:
                data_dict[chr_loci.chr_id] = {"+": {}, "-": {}, ".": {}}
            data_dict[chr_loci.chr_id][chr_loci.strand][chr_loci] = (chr_loci.start, chr_loci.end)
    else:
        data_dict = {}
        for chr_loci in chr_loci_list:
            if chr_loci.chr_id not in data_dict:
                data_dict[chr_loci] = {".": {}}
            data_dict[chr_loci.chr_id][chr_loci.strand][chr_loci] = (chr_loci.start, chr_loci.end)

    for chr_id in data_dict:
        for strand in data_dict[chr_id]:
            data_dict[chr_id][strand] = group_by_intervals_with_overlap_threshold(data_dict[chr_id][strand],
                                                                                  overlap_threshold=overlap_threshold)

    return data_dict


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

    def genome_feature_parse(self, load_seq_info=False):
        # check needed files
        if not hasattr(self, 'gff_file') or self.gff_file is None:
            raise ValueError("genome_feature_parse need gff_file!")

        if load_seq_info:
            if not hasattr(self, 'genome_file') or self.genome_file is None:
                if not hasattr(self, 'cDNA_file') or self.cds_file is None:
                    raise ValueError("load_seq_info need genome_file or cDNA_file!")

        self.chromosome = {}
        feature_dict_list = []
        with open(self.gff_file, 'r') as in_handle:
            for rec in GFF.parse(in_handle):
                self.chromosome[rec.id] = Chromosome(id=rec.id, species=self.species, version=self.version,
                                                     sub_feature=rec.features)
                feature_dict = self.chromosome[rec.id].make_feature_index()
                feature_dict_list.append(feature_dict)
        self.feature_dict = merge_dict(feature_dict_list, True)

        tmp_dict = {}
        for i in self.feature_dict:
            tmp_dict[i] = {}
            for j in self.feature_dict[i]:
                tmp_dict[i][j.name] = j

        self.feature_dict = tmp_dict

    def search(self, fancy_name_string):
        contig_name, c_start, c_end, strand = fancy_name_parse(fancy_name_string)
        if strand == ".":
            feature_index_list = ["+", "-", "."]
        else:
            feature_index_list = [strand]

        output_dir = {}
        for strand_used in feature_index_list:
            feature_index = self.chromosome[contig_name].feature_index[strand_used]
            for f_s, f_e, feature in feature_index.find((c_start, c_end)):
                output_dir[feature.name] = feature

        return output_dir


class Chromosome(object):
    def __init__(self, id=None, species=None, version=None, seq=None, sub_feature=None):
        self.id = id
        self.species = species
        self.version = version
        self.seq = seq
        self.sub_feature = sub_feature

    def make_feature_index(self):
        if not hasattr(self, 'sub_feature'):
            raise ValueError("make_feature_index need sub_feature!")

        self.feature_index = {
            "+": InterLap(),
            "-": InterLap(),
            ".": InterLap()
        }

        feature_dict = {}

        for feature in self.sub_feature:
            start_tmp = feature.location.start.position + 1
            end_tmp = feature.location.end.position
            start = min(start_tmp, end_tmp)
            end = max(start_tmp, end_tmp)
            chr_loci = ChrLoci(chr_id=self.id, strand=feature.strand, start=start, end=end, chrome=self)

            if feature.strand == 1:
                index_tmp = self.feature_index['+']
            elif feature.strand == -1:
                index_tmp = self.feature_index['-']
            else:
                index_tmp = self.feature_index['.']

            gene_xyx = GenomeFeature(feature.id, type=feature.type, chr_loci=chr_loci, sub_feature=feature.sub_features)

            index_tmp.add((start, end, gene_xyx))

            if feature.type not in feature_dict:
                feature_dict[feature.type] = []

            feature_dict[feature.type].append(gene_xyx)

        return feature_dict


# class GenomeFeature(object):
#     def __init__(self, name, type=None, chr_loci=None, sub_feature=None):
#         self.name = name
#         self.type = type
#         self.chr_loci = chr_loci
#         self.sub_feature = sub_feature

class GenomeFeature(ChrLoci):
    def __init__(self, name=None, type=None, chr_loci=None, sub_feature=None, chr_id=None, strand=None, start=None,
                 end=None, chrome=None, bio_location=None):
        if not chr_loci is None:
            chr_loci = chr_loci
        elif not bio_location is None:
            chr_loci = ChrLoci(chr_id=chr_id, strand=bio_location.strand, start=bio_location.start + 1,
                               end=bio_location.end)
        else:
            chr_loci = ChrLoci(chr_id=chr_id, strand=strand, start=start, end=end, chrome=chrome)
        super(GenomeFeature, self).__init__(chr_id=chr_loci.chr_id, strand=chr_loci.strand, start=chr_loci.start,
                                            end=chr_loci.end, chrome=chr_loci.chrome)
        self.name = name
        self.type = type
        self.chr_loci = chr_loci
        self.sub_feature = sub_feature


class mRNA(GenomeFeature):
    def __init__(self, name, gene_name=None, chr_loci=None, sub_feature=None, cds_seq=None, aa_seq=None, cDNA_seq=None):
        super(mRNA, self).__init__(name=name, type='mRNA', chr_loci=chr_loci, sub_feature=sub_feature)
        self.cds_seq = cds_seq
        self.aa_seq = aa_seq
        self.cDNA_seq = cDNA_seq
        self.gene_name = gene_name


class Gene(GenomeFeature):
    def __init__(self, name, species=None, chr_loci=None, sub_feature=None, model_cds_seq=None, model_aa_seq=None,
                 model_cDNA_seq=None):
        super(Gene, self).__init__(name=name, type='gene', chr_loci=chr_loci, sub_feature=sub_feature)
        self.model_cds_seq = model_cds_seq
        self.model_aa_seq = model_aa_seq
        self.model_cDNA_seq = model_cDNA_seq
        self.species = species

    def __str__(self):
        return "ID: %s" % self.name


class GeneSet(object):
    def __init__(self, name, gene_list):
        self.name = name
        self.gene_list = gene_list
        self.tree_file = None
        self.seq_file = None
        self.aln_file = None

    def speci_stat(self):
        output_dir = {}
        for i in self.gene_list:
            if i.species not in output_dir:
                output_dir[i.species] = 0
            output_dir[i.species] = output_dir[i.species] + 1
        return output_dir

    def __str__(self):
        return "ID: %s; Gene Num: %d" % (self.name, len(self.gene_list))


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


# some useful tools

def biogff_convert_to_GenomeFeature(biogff_object, chr_id=None):
    gf = GenomeFeature(name=biogff_object.id, type=biogff_object.type, chr_id=chr_id,
                       bio_location=biogff_object.location)
    if hasattr(biogff_object, 'sub_features') and len(biogff_object.sub_features) != 0:
        gf.sub_feature = []
        for sub_biogff_object in biogff_object.sub_features:
            gf.sub_feature.append(biogff_convert_to_GenomeFeature(sub_biogff_object, chr_id))

    return gf


def read_gff_to_feature_dict(gff_file):
    feature_dict = {}

    with open(gff_file, 'r') as in_handle:
        for rec in GFF.parse(in_handle):
            for feature in rec.features:
                new_feature = biogff_convert_to_GenomeFeature(feature, rec.id)
                feature_dict[new_feature.name] = new_feature

    return feature_dict


def extract_sub_feature_to_gff_object(GenomeFeature_Object, source):
    sub_features = []
    # print(GenomeFeature_Object.name)
    for sgf in GenomeFeature_Object.sub_feature:
        if sgf.strand == "+" or sgf.strand == 1:
            strand = 1
        elif sgf.strand == "-" or sgf.strand == -1:
            strand = -1
        else:
            strand = 0

        sub_qualifiers = {
            "source": source,
            "ID": sgf.name
        }

        if sgf.type == 'CDS':
            sub_qualifiers['phase'] = sgf.phase

        sub_feature = SeqFeature(FeatureLocation(sgf.start - 1, sgf.end, strand=strand),
                                 type=sgf.type, qualifiers=sub_qualifiers)

        if hasattr(sgf, 'sub_feature') and (not sgf.sub_feature is None):
            # print(sgf.sub_feature)
            sub_sub_features = extract_sub_feature_to_gff_object(sgf, source)
            sub_feature.sub_features = sub_sub_features

        sub_features.append(sub_feature)

    return sub_features


def write_GenomeFeature_to_GFF(GenomeFeature_list, output_gff_file, source="."):
    chr_list = list(set([gf.chr_id for gf in GenomeFeature_list]))

    rec_list = []
    for chr_id in chr_list:
        rec = SeqRecord(Seq(""), chr_id, description='')
        rec.features = []

        for gf in GenomeFeature_list:
            if gf.strand == "+" or gf.strand == 1:
                strand = 1
            elif gf.strand == "-" or gf.strand == -1:
                strand = -1
            else:
                strand = 0

            if gf.chr_id == chr_id:
                qualifiers = {
                    "source": source,
                    "ID": gf.name
                }
                top_feature = SeqFeature(FeatureLocation(gf.start - 1, gf.end, strand=strand), type=gf.type,
                                         qualifiers=qualifiers)

                top_feature.sub_features = extract_sub_feature_to_gff_object(gf, source)

                rec.features.append(top_feature)

        rec_list.append(rec)

    with open(output_gff_file, "w") as f:
        GFF.write(rec_list, f)


# todo
def get_uniq_annotation(hit_gene_list, overlap_threshold=0.5):
    loci_sort_dict = {}
    for hit_gene in hit_gene_list:
        hit_loci = hit_gene.chr_loci
        if hit_loci.chr_id not in loci_sort_dict:
            loci_sort_dict[hit_loci.chr_id] = {"+": [], "-": []}
        loci_sort_dict[hit_loci.chr_id][hit_loci.strand].append(hit_gene)

    for chr_id in loci_sort_dict:
        for strand in loci_sort_dict[chr_id]:
            group_dict = group_by_intervals_with_overlap_threshold(
                {hit_gene: hit_gene.range for hit_gene in loci_sort_dict[chr_id][strand]}, overlap_threshold)


if __name__ == '__main__':
    # build a genome database
    genome_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.genome.v1.1.fasta'
    gff_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.v1.1.gff3'
    cds_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.cds.v1.1.fasta'
    pt_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.pt.v1.1.fasta'
    cDNA_file = '/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/Cuscuta.cDNA.v1.1.fasta'

    Cau_genome = Genome(id='Cau', species='267555', version='v1.1', genome_file=genome_file, gff_file=gff_file,
                        cds_file=cds_file, cDNA_file=cDNA_file, aa_file=pt_file)

    Cau_genome.genome_feature_parse()

    all_gene_list = Cau_genome.feature_dict['gene']

    gene_list_in_range = Cau_genome.search("C000N:1-100000")

    # compare two annotation

    # just read a gff file

    gf_dict = read_gff_to_feature_dict(gff_file)
