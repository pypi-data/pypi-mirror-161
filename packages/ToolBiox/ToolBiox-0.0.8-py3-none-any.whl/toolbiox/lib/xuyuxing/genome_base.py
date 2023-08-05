import re
import random
import math
from copy import deepcopy
from pyfaidx import Fasta
import pandas as pd
from collections import OrderedDict
from interlap import InterLap
from BCBio import GFF
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from toolbiox.lib.common.math.interval import merge_intervals, interval_minus_set
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.os import cmd_run
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.util import printer_list

# tools for seq as string

nucl_char_list = ["A", "T", "C", "G", "U"]
nucl_degenerate_char_list = ["M", "S", "W", "B", "D", "R", "H", "Y", "V", "K"]
any_nucl_char_list = ["N"]
prot_char_list = ["A", "P", "B", "Q", "C", "R", "D", "S", "E", "T", "F", "U", "G", "V", "H", "W", "I", "Y", "K", "Z", "L",
                  "M", "N"]
any_prot_char_list = ["X"]
stop_site_char_list = ["*"]
gap_site_char_list = ['-']


def sequence_clean(seq, seq_type='nucl', degenerate_sites_allowed=False, gap_allowed=False, translation_stop_allowed=False):
    # make code
    if seq_type == 'nucl':
        seq_type_flag = 0b0001
    elif seq_type == 'prot':
        seq_type_flag = 0b0000

    dsa_flag = degenerate_sites_allowed
    if dsa_flag:
        dsa_flag = 0b0010

    ga_flag = gap_allowed
    if ga_flag:
        ga_flag = 0b0100

    tsa_flag = translation_stop_allowed
    if tsa_flag:
        tsa_flag = 0b1000

    bit_field = seq_type_flag + dsa_flag + ga_flag + tsa_flag

    if bit_field == 0b0111:
        all_allowed = nucl_char_list + any_nucl_char_list + \
            nucl_degenerate_char_list + gap_site_char_list
        safe_remove = []
        safe_replace = any_nucl_char_list
    elif bit_field == 0b0011:
        all_allowed = nucl_char_list + any_nucl_char_list + nucl_degenerate_char_list
        safe_remove = gap_site_char_list
        safe_replace = any_nucl_char_list
    elif bit_field == 0b0101:
        all_allowed = nucl_char_list + any_nucl_char_list + gap_site_char_list
        safe_remove = []
        safe_replace = any_nucl_char_list
    elif bit_field == 0b0001:
        all_allowed = nucl_char_list + any_nucl_char_list
        safe_remove = gap_site_char_list
        safe_replace = any_nucl_char_list
    elif bit_field == 0b0000:
        all_allowed = prot_char_list + any_prot_char_list
        safe_remove = gap_site_char_list + stop_site_char_list
        safe_replace = any_prot_char_list
    elif bit_field == 0b0100:
        all_allowed = prot_char_list + any_prot_char_list + gap_site_char_list
        safe_remove = stop_site_char_list
        safe_replace = any_prot_char_list
    elif bit_field == 0b1100:
        all_allowed = prot_char_list + any_prot_char_list + \
            gap_site_char_list + stop_site_char_list
        safe_remove = []
        safe_replace = any_prot_char_list
    elif bit_field == 0b1000:
        all_allowed = prot_char_list + any_prot_char_list + stop_site_char_list
        safe_remove = gap_site_char_list
        safe_replace = any_prot_char_list
    else:
        raise ValueError("Bad input flag")

    new_seq = seq
    char_site = set(new_seq)
    bad_flag = False
    for i in char_site:
        if i in all_allowed:
            continue
        elif i in safe_remove:
            if i == "*":
                new_seq = re.sub("\*", "", new_seq)
            else:
                new_seq = re.sub(i, "", new_seq)
        else:
            if i == "*":
                new_seq = re.sub("\*", "", new_seq)
            else:
                new_seq = re.sub(i, safe_replace[0], new_seq)
            bad_flag = True

    return new_seq, bad_flag


def slice_scaffold_by_N(sequence, scaffold_maker="N"):
    """
    some scaffold sequence have many N in the seq, I can find the start and end for each Non-N seq, e.g. contig. I will
    return a list which have tuple(start,end) 0-base
    """
    subseqs = sequence.split(scaffold_maker)
    sub_seq_slice = []
    pointer = 0
    for i in subseqs:
        if len(i) == 0:
            pointer = pointer + 1
            continue
        sub_seq_slice.append((pointer, pointer + len(i)))
        pointer = pointer + len(i) + 1
    return sub_seq_slice


def contig_cutting(sequence, step, length, pointer_start=1):
    """
    cutting a sequence as windows, you can give me step and window length. I will return a generator which every one is
    start point and window sequence. pointer_start is the begin pointer it just for ID, will not change sequence cutting
    """
    seq_len = len(sequence)
    sub_seq_dict = {}
    for i in range(pointer_start - 1, seq_len, step):
        if seq_len - i > length:
            sub_seq = sequence[i:i + length]
            yield (pointer_start, sub_seq)
            sub_seq_dict[pointer_start] = sub_seq
        else:
            sub_seq = sequence[i:seq_len]
            yield (pointer_start, sub_seq)
            break
        pointer_start = pointer_start + step


def scaffold_cutting(sequence, step=500, length=1000, Consider_scaffold=True, shift_start=0):
    """
    cutting a sequence as windows, you can give me step and window length. I will return a generator which every one is
    start point and window sequence. pointer_start is the begin pointer it just for ID, will not change sequence cutting
    If the sequence is scaffold, I can split scaffold by N firstly, and get contig to make windows, the pointer will follow
    scaffold which based on 1
    """
    if Consider_scaffold is True:
        sub_seq_slice = slice_scaffold_by_N(sequence)
        # output_dict = {}
        for start, end in sub_seq_slice:
            sub_seq = sequence[start:end]
            for pointer, sub_sub_seq in contig_cutting(sub_seq, step, length, start + 1):
                yield (pointer, sub_sub_seq)
                # output_dict[pointer] = sub_sub_seq
    else:
        if shift_start != 0:
            # print(shift_start)
            yield (1, sequence[1 - 1:shift_start])

        # output_dict = {}
        for pointer, sub_seq in contig_cutting(sequence, step, length, shift_start + 1):
            yield (pointer, sub_seq)
            # output_dict[pointer] = sub_seq

    # return output_dict


def reverse_complement(seq, RNA=False):
    """
    #>>> seq = "TCGGinsGCCC"
    #>>> print "Reverse Complement:"
    #>>> print(reverse_complement(seq))
    #GGGCinsCCGA
    """
    alt_map = {'ins': '0'}
    if RNA:
        complement = {'A': 'U', 'C': 'G', 'G': 'C', 'U': 'A'}
    else:
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    # for k, v in alt_map.iteritems():
    for k, v in alt_map.items():
        seq = seq.replace(k, v)
    bases = list(seq)
    bases = reversed([complement.get(base, base) for base in bases])
    bases = ''.join(bases)
    # for k, v in alt_map.iteritems():
    for k, v in alt_map.items():
        bases = bases.replace(v, k)
    return bases


def reverse_seq(seq):
    """just reverse"""
    return "".join(reversed(seq))


def complement_seq(seq):
    """just complement"""
    if 'U' in seq:
        complement = {'A': 'U', 'C': 'G', 'G': 'C', 'U': 'A'}
    else:
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    bases = list(seq)
    bases = [complement.get(base, base) for base in bases]
    bases = ''.join(bases)
    return bases


def sub_seq(seq, site_start, site_end, strand, RNA):
    """get sub set of a seq"""
    start = min(site_start, site_end)
    end = max(site_start, site_end)
    sub_seq_out = seq[start - 1:end]

    if RNA is True:
        sub_seq_out = sub_seq_out.replace("T", "U")
    if strand == "-":
        sub_seq_out = reverse_complement(sub_seq_out, RNA)

    return sub_seq_out


def iter_kmers(seq, k, overlap=True):
    """
    from skbio.Sequence.iter_kmers
    """
    if k < 1:
        raise ValueError("k must be greater than 0.")

    if overlap:
        step = 1
        count = len(seq) - k + 1
    else:
        step = k
        count = len(seq) // k

    seq_bytes = np.array([ord(i) for i in seq], dtype='uint8')

    # Optimized path when positional metadata doesn't need slicing.
    kmers = np.lib.stride_tricks.as_strided(
        seq_bytes, shape=(k, count), strides=(1, step)).T

    for s in kmers:
        yield s


def kmer_frequencies(seq, k, overlap=True, relative=False):
    """
    from skbio.Sequence.kmer_frequencies
    """
    kmers = iter_kmers(seq, k, overlap=overlap)
    freqs = dict(Counter((str(seq) for seq in kmers)))

    if relative:
        if overlap:
            num_kmers = len(seq) - k + 1
        else:
            num_kmers = len(seq) // k

        relative_freqs = {}
        for kmer, count in freqs.items():
            relative_freqs[kmer] = count / num_kmers
        freqs = relative_freqs

    return freqs


def sequence_entropy(sequence_input, kmer):
    freqs = kmer_frequencies(sequence_input, kmer,
                             overlap=False, relative=False)
    t_num = sum([freqs[i] for i in freqs])

    entropy = 0
    for i in freqs:
        p = freqs[i]/t_num
        entropy = entropy - (p * math.log(p, 2))

    return entropy


def random_sequence(seq_char, length, random_seed=None):
    """
    get random sequence
    :param seq_char: for DNA, you can give "ATCG"
    """
    random.seed(random_seed)
    sa = []
    for i in range(length):
        sa.append(random.choice(seq_char))
    salt = ''.join(sa)
    return salt


def get_seq_index_ignore_gap(give_site, seq_with_gap, seq_start=1, gap_chr='-'):
    """
    seq_with_gap = "------------ATGC---CAGTCA---ACG-GCATGCTA"
    give_site = 5
    seq_start = 1
    gap_chr = '-'

    give a seq with gap, and a site number, return index in gap seq
    """
    go_on_flag = True
    round_use_range = (0, 0)
    add_length = give_site - seq_start + 1
    round_true_site = 0
    while (go_on_flag):
        round_use_range = (
            round_use_range[1] + 1, round_use_range[1] + add_length)
        round_seq = seq_with_gap[round_use_range[0] - 1:round_use_range[1]]
        round_true_site = round_true_site + \
            len(round_seq) - round_seq.count(gap_chr)
        add_length = round_seq.count(gap_chr)
        print(round_use_range, round_seq, round_true_site, add_length)

        if add_length == 0:
            go_on_flag = False

    return round_use_range[1]


# tools for seq class

class BioSeq(object):
    def __init__(self, seq_id=None, seq='', seq_type='nucl'):
        self.id = seq_id
        self.seq = seq
        self.seq_type = seq_type

    def __str__(self):
        return self.seq

    def __len__(self):
        if len(self.seq) == 0 and hasattr(self, 'length'):
            return self.length
        else:
            return len(self.seq)

    def seq_clean(self, degenerate_sites_allowed=False, gap_allowed=False,
                  translation_stop_allowed=False):

        new_seq, bad_flag = sequence_clean(
            self.seq, self.seq_type, degenerate_sites_allowed, gap_allowed, translation_stop_allowed)
        self.seq = new_seq

    def seqs_upper(self):
        self.seq = self.seq.upper()

    def seqs_lower(self):
        self.seq = self.seq.lower()

    def no_wrap(self):
        self.seq = re.sub("\n", "", self.seq)

    def wrap(self, line_length=75):
        raw_seq = str(self.seq)
        raw_seq = re.sub("\n", "", raw_seq)
        new_seq = ""

        for j in (raw_seq[x: x + line_length] for x in range(0, len(raw_seq), line_length)):
            new_seq += j + "\n"

        self.seq = new_seq

        return new_seq

    def sub(self, site_start, site_end, strand, RNA):
        return sub_seq(self.seq, site_start, site_end, strand, RNA)

    def RNA(self):
        return self.seq.replace("T", "U")

    def reverse(self):
        return reverse_seq(self.seq)

    def complement(self):
        return complement_seq(self.seq)

    def reverse_complement(self):
        return complement_seq(reverse_seq(self.seq))


class FastaRecord(BioSeq):
    def __init__(self, seqname, seq=None, faidx=None):
        super(FastaRecord, self).__init__(seq)
        self.id = seqname
        self.faidx = faidx
        self.qualifiers = re.findall('\[([^\[\]]+)=([^\[\]]+)\]', seqname)

    def short_id(self):
        name_short = re.search('^(\S+)', self.id).group(1)
        return name_short

    @property
    def seq(self):
        if self.faidx is not None:
            return str(self.faidx)
        else:
            return self._seq

    @seq.setter
    def seq(self, value):
        self._seq = value

    def read_seq_to_mem(self):
        self._seq = str(self.faidx)

    def sub(self, site_start, site_end, strand, RNA):
        if self.faidx is not None:
            output = str(self.faidx[site_start - 1:site_end])
            if RNA is True:
                output = output.replace("T", "U")
            if strand == "-":
                output = reverse_complement(output, RNA)
            return output
        else:
            return sub_seq(self.seq, site_start, site_end, strand, RNA)

    def len(self):
        if hasattr(self, 'faidx'):
            return len(self.faidx)
        else:
            return len(self.seq)

    def get_GC_ratio(self):
        gc_now = (self.seq.count('C') + self.seq.count('G') +
                  self.seq.count('c') + self.seq.count('g'))/self.len()
        return gc_now


class FastqRecord(FastaRecord):
    def __init__(self, seqname, seq, quality):
        super(FastqRecord, self).__init__(seqname, seq)
        self.quality = quality


def faidx2xyx(pyfaidx_record, write_seq_mem):
    try:
        seq_name = pyfaidx_record.long_name
    except:
        seq_name = pyfaidx_record.name

    if write_seq_mem:
        return FastaRecord(seq_name, str(pyfaidx_record), pyfaidx_record)
    else:
        return FastaRecord(seq_name, None, pyfaidx_record)


def read_fasta_by_faidx(file_name, write_seq_mem=False, force_wrap_file=False):
    # if file_name.split(".")[-1] == 'gz':
    #     cmd_run("gzip %s" % file_name, slience=True)
    #     file_name = remove_file_name_suffix(file_name, 1)

    try:
        output_dict = OrderedDict()
        for i in Fasta(file_name):
            output_dict[i.name] = faidx2xyx(i, write_seq_mem)
        return output_dict
    except:
        try:
            cmd_run("samtools faidx %s" % file_name)
            output_dict = OrderedDict()
            for i in Fasta(file_name):
                output_dict[i.name] = faidx2xyx(i, write_seq_mem)
            return output_dict
        except:
            raise EnvironmentError("fasta file not suit for pyfaidx")

    #
    #
    # wrap_file_name = remove_file_name_suffix(file_name, 1) + ".pyfaidx.fasta"
    # if force_wrap_file:
    #     wrap_fasta_file(file_name, wrap_file_name, 75)
    #     try:
    #         return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #     except:
    #         raise EnvironmentError("fasta file not suit for pyfaidx")
    # else:
    #     if os.path.exists(wrap_file_name):
    #         try:
    #             return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #         except:
    #             wrap_fasta_file(file_name, wrap_file_name, 75)
    #             try:
    #                 return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #             except:
    #                 raise EnvironmentError("fasta file not suit for pyfaidx")
    #     else:
    #         try:
    #             return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(file_name)}
    #         except:
    #             wrap_fasta_file(file_name, wrap_file_name, 75)
    #             try:
    #                 return {i.name: faidx2xyx(i, write_seq_mem) for i in Fasta(wrap_file_name)}
    #             except:
    #                 raise EnvironmentError("fasta file not suit for pyfaidx")
    #


def write_fasta(fasta_record_list, output_file, wrap_length=75, upper=False):
    with open(output_file, 'w') as f:
        for record in fasta_record_list:
            record.no_wrap()
            raw_seq = str(record.seq)

            if upper:
                raw_seq = raw_seq.upper()

            f.write(">%s\n" % record.id)
            for x in range(0, len(raw_seq), wrap_length):
                i = raw_seq[x: x + wrap_length]
                f.write(i + "\n")

# class for genome


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

        good_orf, phase, aa_seq = cds_judgment(self.cds_seq)

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
            cds_num = len(
                [i for i in mRNA_now.sub_features if i.type == 'CDS'])
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


class Chromosome(BioSeq):
    def __init__(self, chr_id=None, species=None, version=None, seq='', length=None, feature_dict=None, qualifiers={}, auto_get_gene_index=True):
        # base info
        super(Chromosome, self).__init__(
            seq_id=chr_id, seq=seq, seq_type='nucl')
        self.sp_id = species
        self.version = version
        self.qualifiers = qualifiers

        if length:
            self.length = length

        # chromesome feature info
        if feature_dict and auto_get_gene_index:
            self.auto_get_gene_index(feature_dict)

    def auto_get_gene_index(self, feature_dict):
        self.load_genome_features(feature_dict)
        self.gene_index = self.build_index('gene')
        self.sync_species_and_gene_rank_info()

    def load_genome_features(self, feature_dict):
        chr_feature_dict = OrderedDict()
        for type_tmp in feature_dict:
            chr_feature_dict[type_tmp] = OrderedDict()
            for gf_tmp_id in feature_dict[type_tmp]:
                gf_tmp = feature_dict[type_tmp][gf_tmp_id]
                if gf_tmp.chr_loci.chr_id == self.id:
                    chr_feature_dict[type_tmp][gf_tmp.id] = gf_tmp
        self.feature_dict = chr_feature_dict

    def build_index(self, top_type='gene'):
        if not hasattr(self, 'feature_dict'):
            raise ValueError("build_index need feature_dict")

        feature_index = {
            "+": InterLap(),
            "-": InterLap(),
            ".": InterLap()
        }

        for type_tmp in self.feature_dict:
            for gf_tmp_id in self.feature_dict[type_tmp]:
                gf_tmp = self.feature_dict[type_tmp][gf_tmp_id]
                index_tmp = feature_index[gf_tmp.strand]
                index_tmp.add(
                    (gf_tmp.chr_loci.start, gf_tmp.chr_loci.end, gf_tmp))

                feature_index["."].add(
                    (gf_tmp.chr_loci.start, gf_tmp.chr_loci.end, gf_tmp))

        return feature_index

    def sync_species_and_gene_rank_info(self):
        num = 0
        for s, e, gf in self.gene_index['.']:
            gf.sp_id = self.sp_id
            gf.index = num
            num += 1


class Genome(object):
    def __init__(self, genome_id=None, species=None, version=None, chr_dict=None):
        self.id = genome_id
        self.sp_id = species
        self.version = version
        self.chr_dict = chr_dict

        if self.chr_dict:
            self.get_gene_dict()

    def get_gene_dict(self):
        self.gene_dict = {}
        for chr_id in self.chr_dict:
            chromo_now = self.chr_dict[chr_id]
            for gene_id in chromo_now.feature_dict['gene']:
                self.gene_dict[gene_id] = chromo_now.feature_dict['gene'][gene_id]


def build_genome(genome_id, species, genome_fasta_file=None, gff_file=None, version=None):
    chr_dict = OrderedDict()

    if genome_fasta_file:
        genome_seq_dict = read_fasta_by_faidx(genome_fasta_file)
        for contig_id in genome_seq_dict:
            contig_seq = genome_seq_dict[contig_id]
            chr_dict[contig_id] = Chromosome(chr_id=contig_id, species=species, version=version, seq='', length=len(
                contig_seq), feature_dict=None, qualifiers={})

    if gff_file:
        gff_dict = read_gff_file(gff_file)
        gff_by_chr_dict = {}
        for top_type in gff_dict:
            for gf_id in gff_dict[top_type]:
                gf = gff_dict[top_type][gf_id]
                if gf.chr_id not in gff_by_chr_dict:
                    gff_by_chr_dict[gf.chr_id] = {}
                if top_type not in gff_by_chr_dict[gf.chr_id]:
                    gff_by_chr_dict[gf.chr_id][top_type] = {}
                gff_by_chr_dict[gf.chr_id][top_type][gf_id] = gf

        if len(chr_dict) > 0:
            for chr_id in chr_dict:
                chromo_now = chr_dict[chr_id]
                chromo_now.auto_get_gene_index(gff_by_chr_dict[chr_id])
        else:
            for chr_id in gff_by_chr_dict:
                max_site = 0
                for top_type in gff_by_chr_dict[chr_id]:
                    for gf_id in gff_by_chr_dict[chr_id][top_type]:
                        gf = gff_by_chr_dict[chr_id][top_type][gf_id]
                        max_site = max(gf.start, gf.end, max_site)
                chr_dict[contig_id] = Chromosome(chr_id=chr_id, species=species, version=version,
                                                 seq='', length=max_site, feature_dict=gff_by_chr_dict[chr_id], qualifiers={})

    return Genome(genome_id=genome_id, species=species, version=version, chr_dict=chr_dict)


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

    with open(gff_file, 'r') as in_handle:
        for rec in GFF.parse(in_handle):
            for feature in rec.features:
                new_feature = sf2gf(feature, rec.id)
                if new_feature.type not in feature_dict:
                    feature_dict[new_feature.type] = OrderedDict()
                feature_dict[new_feature.type][new_feature.id] = new_feature

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

# class for compare genome


def if_conserved(species_list, conserved_arguments):
    """
    conserved_arguments = [
        [['Cau', 'Ini', 'Sly'], ['Ath', 'Aco']],
        [2,2]
    ]
    """
    sp_group_lol = conserved_arguments[0]
    group_min_num_list = conserved_arguments[1]

    conserved_flag = True

    for sp_group_list, min_num in zip(sp_group_lol, group_min_num_list):
        if len(set(species_list) & set(sp_group_list)) < min_num:
            conserved_flag = False

    return conserved_flag


class GeneSet(object):
    def __init__(self, id, gene_list):
        self.id = id
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
        return "ID: %s; Gene Num: %d" % (self.id, len(self.gene_list))


class OrthoGroup(GeneSet):
    def __init__(self, id=None, from_gene_list=None, species_list=None, from_OG_dict=None):
        if from_OG_dict and from_gene_list is None:
            if not species_list:
                species_list = list(from_OG_dict.keys())

            from_gene_list = []
            for sp_id in from_OG_dict:
                for g_id in from_OG_dict[sp_id]:
                    from_gene_list.append(Gene(id=g_id, species=sp_id))

        if species_list:
            gene_dict = {i: [] for i in species_list}
        else:
            gene_dict = {}
            for i in from_gene_list:
                gene_dict[i.species] = []

        gene_list = [i for i in from_gene_list if i.species in gene_dict]

        super(OrthoGroup, self).__init__(id=id, gene_list=gene_list)

        self.gene_dict = gene_dict
        for i in self.gene_list:
            self.gene_dict[i.species].append(i)

        self.species_stat = {}
        for sp_id in self.gene_dict:
            self.species_stat[sp_id] = len(self.gene_dict[sp_id])

        self.species_list = list(self.species_stat.keys())

    def conserved(self, conserved_arguments_dict):
        non_zero_species_list = [
            i for i in self.species_stat if self.species_stat[i] == 0]

        return if_conserved(non_zero_species_list, conserved_arguments_dict)


class OrthoGroups(object):
    def __init__(self, id=None, OG_tsv_file=None, from_OG_dict=None, from_OG_list=None, species_list=None, note=None, new_OG_name=False):
        self.id = id
        self.note = note
        self.OG_tsv_file = OG_tsv_file
        self.from_OG_dict = from_OG_dict

        if OG_tsv_file:
            OG_dict = self.build_from_OG_tsv_file(
                OG_tsv_file, species_list=species_list)
        elif from_OG_dict:
            OG_dict = self.build_from_OG_dict(
                from_OG_dict, species_list=species_list)
        elif from_OG_list:
            OG_dict = self.build_from_OG_list(
                from_OG_list, species_list=species_list, new_OG_name=new_OG_name)
        else:
            OG_dict = OrderedDict()

        self.OG_dict = OG_dict
        if species_list:
            self.species_list = species_list
        else:
            self.species_list = OG_dict[list(OG_dict.keys())[0]].species_list
        self.OG_id_list = list(self.OG_dict.keys())

    def get(self, key_tuple):
        """
        key_tuple: ('OG1234', 'Ath'), or ('OG1234', None), or (None, 'Ath')
        """

        OG_id, sp_id = key_tuple

        if OG_id and sp_id:
            return self.OG_dict[OG_id].gene_dict[sp_id]
        elif OG_id:
            return self.OG_dict[OG_id].gene_dict
        elif sp_id:
            output_dict = {}
            for i in self.OG_dict:
                output_dict[i] = self.OG_dict[i].gene_dict[sp_id]
            return output_dict

    def build_from_OG_tsv_file(self, OG_tsv_file, species_list=None):
        file_info = tsv_file_dict_parse(OG_tsv_file)

        full_species_list = list(
            file_info[list(file_info.keys())[0]].keys())[1:]

        OG_dict = OrderedDict()

        for i in file_info:
            OG_id = file_info[i]['Orthogroup']

            gene_list = []
            for j in file_info[i]:
                if j == 'Orthogroup':
                    continue
                if file_info[i][j] == '':
                    continue
                gene_list.extend([Gene(id=k, species=j)
                                  for k in file_info[i][j].split(", ")])

            if species_list:
                OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=species_list)
            else:
                OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=full_species_list)

        return OG_dict

    def build_from_OG_dict(self, OG_dict, species_list=None):
        """
        OG_dict = {
            "OG0001": {
                "Ath": ['AT0001', 'AT0002'],
                "Osa": ['OS0001', 'OS0002']
            }
        }
        """
        new_OG_dict = OrderedDict()

        for OG_id in OG_dict:

            if isinstance(OG_dict[OG_id], dict):
                gene_list = []
                for sp_id in OG_dict[OG_id]:
                    gene_list.extend([Gene(id=i, species=sp_id)
                                      for i in OG_dict[OG_id][sp_id]])
                new_OG_dict[OG_id] = OrthoGroup(
                    id=OG_id, from_gene_list=gene_list, species_list=species_list)
            else:
                new_OG_dict[OG_id] = OG_dict[OG_id]

        return new_OG_dict

    def build_from_OG_list(self, OG_list, species_list=None, new_OG_name=False):
        if species_list:
            all_species_list = species_list
        else:
            all_species_list = []
            for og in OG_list:
                all_species_list.extend(og.species_list)
            all_species_list = list(set(all_species_list))

        new_OG_dict = OrderedDict()

        num = 0
        for og in OG_list:
            if new_OG_name:
                og_id = "OG%d" % num
                num += 1
            else:
                og_id = og.id

            gene_list = [
                gene for gene in og.gene_list if gene.species in set(all_species_list)]
            new_OG_dict[og_id] = OrthoGroup(
                id=og_id, from_gene_list=gene_list, species_list=all_species_list)

        return new_OG_dict

    def write_OG_tsv_file(self, output_file, species_list=None):
        if not species_list:
            species_list = self.species_list

        with open(output_file, 'w') as f:
            f.write(printer_list(species_list, head='Orthogroup\t')+"\n")

            for OG_id in self.OG_dict:
                OG = self.OG_dict[OG_id]
                string_list = []
                for sp_id in species_list:
                    string_list.append(printer_list(
                        [i.id for i in OG.gene_dict[sp_id]], sep=', '))
                output_string = printer_list(string_list, head=OG_id+"\t")
                f.write(output_string+"\n")

        return output_file

    def get_conserved_OG_list(self, conserved_arguments_dict):

        output_list = []
        for i in self.OG_dict:
            og = self.OG_dict[i]
            if og.conserved():
                output_list.append(i)

        return output_list

    def remove_some_OG(self, removed_OG_list):
        for i in removed_OG_list:
            self.OG_id_list.remove(i)
            del self.OG_dict[i]


class Species(object):
    def __init__(self,
                 sp_id=None,
                 taxon_id=None,
                 species_name=None,
                 genome_file=None,
                 gff_file=None,
                 pt_file=None,
                 cDNA_file=None,
                 cds_file=None):

        self.sp_id = sp_id
        self.taxon_id = taxon_id
        self.species_name = species_name
        self.genome_file = genome_file
        self.gff_file = gff_file
        self.pt_file = pt_file
        self.cDNA_file = cDNA_file
        self.cds_file = cds_file


def read_species_info(species_info_table, add_option=[]):

    species_info_df = pd.read_excel(species_info_table)
    species_info_dict = {}
    for index in species_info_df.index:
        sp_id = str(species_info_df.loc[index]['sp_id'])

        base_info_dict = {i: None for i in [
            'taxon_id', 'species_name', 'genome_file', 'gff_file', 'pt_file', 'cDNA_file', 'cds_file']}

        for i in base_info_dict:
            if i in species_info_df.loc[index]:
                base_info_dict[i] = species_info_df.loc[index][i]

        species_info_dict[sp_id] = Species(
            sp_id, base_info_dict['taxon_id'], base_info_dict['species_name'], base_info_dict['genome_file'], base_info_dict['gff_file'], base_info_dict['pt_file'], base_info_dict['cDNA_file'], base_info_dict['cds_file'])

        for i in add_option:
            if i in species_info_df.loc[index]:
                setattr(species_info_dict[sp_id], i,
                        species_info_df.loc[index][i])

    return species_info_dict


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
    def __init__(self, sb_id=None, q_chr=None, s_chr=None, strand=None, gene_pair_dict=None, property_dict={}, parameter_dict={}):
        self.id = sb_id
        self.property = property_dict
        self.parameter = parameter_dict
        self.strand = strand
        self.q_chr = q_chr
        self.s_chr = s_chr
        self.gene_pair_dict = gene_pair_dict

        if gene_pair_dict:
            self.get_full_info()

    def get_full_info(self):

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

    def reverse_myself(self, new_sb_id):
        gene_pair_dict = {
            i: self.gene_pair_dict[i].reverse_myself() for i in self.gene_pair_dict}
        new_sb = SyntenyBlock(new_sb_id, self.q_sp, self.s_sp,
                              self.strand, gene_pair_dict, self.property, self.parameter)
        return new_sb

    def __str__(self):
        return "Q = %s:%s gene: %d-%d (%d) base: %d-%d (%d) vs S = %s:%s gene: %d-%d (%d) base: %d-%d (%d), %s, have %d gene pair" % (self.q_sp, self.q_chr, self.first_q_gene_loci, self.last_q_gene_loci, self.last_q_gene_loci - self.first_q_gene_loci + 1,  self.query_from, self.query_to, self.query_to - self.query_from + 1, self.s_sp, self.s_chr, self.first_s_gene_loci, self.last_s_gene_loci, self.last_s_gene_loci - self.first_s_gene_loci + 1,   self.subject_from, self.subject_to, self.subject_to - self.subject_from + 1, self.strand, len(self.gene_pair_dict))

    __repr__ = __str__


if __name__ == '__main__':
    from toolbiox.config import project_dir

    Ath_genome_fasta_file = project_dir + \
        "/example_dataset/genome/Ath/T3702N0.genome.fasta"
    Ath_genome_gff3 = project_dir + "/example_dataset/genome/Ath/T3702N0.genome.gff3"

    Ath_genome = build_genome(
        'Ath', 'Ath', genome_fasta_file=Ath_genome_fasta_file, gff_file=Ath_genome_gff3, version='xyx')
