from toolbiox.lib.common.genome.genome_feature2 import ChrLoci, Gene, Genome, Chromosome
from toolbiox.lib.common.math.interval import section
from collections import OrderedDict
from toolbiox.lib.xuyuxing.base.common_command import get_od


class GenePair(object):
    def __init__(self, q_gene, s_gene, property_dict=None, gene_pair_id=None):
        self.q_gene = q_gene
        self.s_gene = s_gene
        self.property = property_dict
        self.id = gene_pair_id

    def reverse_myself(self):
        new_GP = GenePair(self.s_gene, self.q_gene, self.property)
        return new_GP

    def __str__(self):
        return "%s vs %s" % (self.q_gene, self.s_gene)

    __repr__ = __str__

    def __eq__(self, other):
        return (self.q_gene == other.q_gene and self.s_gene == other.s_gene) or (self.q_gene == other.s_gene and self.s_gene == other.q_gene)


class LociPair(object):
    def __init__(self, q_chr_loci, s_chr_loci, strand=None, loci_pair_id=None):
        self.q_chr_loci = q_chr_loci
        self.s_chr_loci = s_chr_loci
        self.strand = strand
        self.id = loci_pair_id

    def reverse_myself(self, new_loci_pair_id=None):
        new_lp = LociPair(self.s_chr_loci, self.q_chr_loci,
                          self.strand, self.new_loci_pair_id)
        return new_lp

    def __str__(self):
        return "Q = %s vs S = %s, %s" % (self.q_chr_loci, self.s_chr_loci, self.strand)

    __repr__ = __str__

    def __eq__(self, other):
        return (self.q_chr_loci == other.q_chr_loci and self.s_chr_loci == other.s_chr_loci) or (self.q_chr_loci == other.s_chr_loci and self.s_chr_loci == other.q_chr_loci)


def sort_gene_list_by_chr_rank(gene_list):
    return sorted(gene_list, key=lambda x: x.chr_rank)


class SyntenyBlock(LociPair):
    def __init__(self, q_gene_list=None, s_gene_list=None, anchored_gene_pair_list=None, property_dict=None, parameter_dict=None, synteny_block_id=None):
        # sort gene
        q_gene_list = sort_gene_list_by_chr_rank(q_gene_list)
        s_gene_list = sort_gene_list_by_chr_rank(s_gene_list)

        first_q_gene_rank = min([i.chr_rank for i in q_gene_list])
        last_q_gene_rank = min([i.chr_rank for i in q_gene_list])
        first_s_gene_rank = min([i.chr_rank for i in s_gene_list])
        last_s_gene_rank = min([i.chr_rank for i in s_gene_list])

        q_genes = OrderedDict()
        for gene in q_gene_list:
            q_genes[gene.id] = gene

        s_genes = OrderedDict()
        for gene in s_gene_list:
            s_genes[gene.id] = gene

        # if all anchored gene in gene list
        for gp in anchored_gene_pair_list:
            if not (gp.q_gene.id in q_genes):
                raise ValueError(
                    "find a query anchored gene (%s) not in gene list" % gp.q_gene.id)
            if not (gp.s_gene.id in s_genes):
                raise ValueError(
                    "find an subject anchored gene (%s) not in gene list" % gp.s_gene.id)

        # sort anchored_gene_pair_list by query rank
        anchored_gene_pair_list_sorted = sorted(
            anchored_gene_pair_list, key=lambda x: x.q_gene.chr_rank)

        # get q & s chr_loci
        q_chr_id = q_gene_list[0].chr_loci.chr_id
        q_sp_id = q_gene_list[0].chr_loci.sp_id
        q_start = min([i.start for i in q_gene_list] +
                      [i.end for i in q_gene_list])
        q_end = max([i.start for i in q_gene_list] +
                    [i.end for i in q_gene_list])
        q_chr_loci = ChrLoci(chr_id=q_chr_id, strand=None,
                             start=q_start, end=q_end, species_id=q_sp_id)
        q_chr_loci.get_fancy_name()

        s_chr_id = s_gene_list[0].chr_loci.chr_id
        s_sp_id = s_gene_list[0].chr_loci.sp_id
        s_start = min([i.start for i in s_gene_list] +
                      [i.end for i in s_gene_list])
        s_end = max([i.start for i in s_gene_list] +
                    [i.end for i in s_gene_list])
        s_chr_loci = ChrLoci(chr_id=s_chr_id, strand=None,
                             start=s_start, end=s_end, species_id=s_sp_id)
        s_chr_loci.get_fancy_name()

        # get strand
        first_gp = [
            i for i in anchored_gene_pair_list_sorted if i.q_gene.chr_rank == first_q_gene_rank][0]
        if first_gp.s_gene.chr_rank == first_s_gene_rank:
            strand = "+"
        elif first_gp.s_gene.chr_rank == last_s_gene_rank:
            strand = "-"
        else:
            raise ValueError("failed to get strand")

        # change to LociPair
        super(SyntenyBlock, self).__init__(q_chr_loci, s_chr_loci,
                                           strand=strand, loci_pair_id=synteny_block_id)

        self.id = synteny_block_id
        self.property_dict = property_dict
        self.parameter_dict = parameter_dict

        # add other information
        self.q_genes = q_genes
        self.s_genes = s_genes
        self.anchored_gene_pairs = anchored_gene_pair_list_sorted
        self.q_sp_id = q_sp_id
        self.s_sp_id = s_sp_id
        self.q_chr = q_chr_id
        self.s_chr = s_chr_id

    def reverse_myself(self, new_sb_id):
        s_gene_list = [self.q_genes[i] for i in self.q_genes]
        q_gene_list = [self.s_genes[i] for i in self.s_genes]

        anchored_gene_pair_list = []
        for gp in self.anchored_gene_pair_list:
            re_gp = gp.reverse_myself()
            anchored_gene_pair_list.append(re_gp)

        new_sb = SyntenyBlock(q_gene_list=q_gene_list, s_gene_list=s_gene_list, anchored_gene_pair_list=anchored_gene_pair_list,
                              property_dict=self.property_dict, parameter_dict=self.parameter_dict, synteny_block_id=new_sb_id)

        return new_sb

    def __str__(self):
        q_s = get_od(self.q_genes, 0).chr_rank
        q_e = get_od(self.q_genes, -1).chr_rank

        if self.strand == "-":
            s_s = get_od(self.s_genes, 0).chr_rank
            s_e = get_od(self.s_genes, -1).chr_rank
        else:
            s_s = get_od(self.s_genes, -1).chr_rank
            s_e = get_od(self.s_genes, 0).chr_rank

        return "Q = %s:%s gene: %d-%d (%d) base: %d-%d (%d) vs S = %s:%s gene: %d-%d (%d) base: %d-%d (%d), %s, have %d gene pair" % (
            self.q_sp_id,
            self.q_chr_id,
            q_s,
            q_e,
            q_e - q_s + 1,
            self.q_chr_loci.start,
            self.q_chr_loci.end,
            self.q_chr_loci.end - self.q_chr_loci.start + 1,
            self.s_sp_id,
            self.s_chr_id,
            s_s,
            s_e,
            s_e - s_s + 1,
            self.s_chr_loci.start,
            self.s_chr_loci.end,
            self.s_chr_loci.end - self.s_chr_loci.start + 1,
            self.strand,
            len(self.anchored_gene_pairs)
        )

    __repr__ = __str__


def section_LP(loci_pair_a, loci_pair_b, section_side=2):
    a_q_chr_loci = loci_pair_a.q_chr_loci
    a_s_chr_loci = loci_pair_a.s_chr_loci
    b_q_chr_loci = loci_pair_b.q_chr_loci
    b_s_chr_loci = loci_pair_b.s_chr_loci

    if section_side == 2:
        if a_q_chr_loci.sp_id == b_q_chr_loci.sp_id and a_q_chr_loci.chr_id == b_q_chr_loci.chr_id and a_s_chr_loci.sp_id == b_s_chr_loci.sp_id and a_s_chr_loci.chr_id == b_s_chr_loci.chr_id:
            if section(a_q_chr_loci.range, b_q_chr_loci.range, just_judgement=True) and section(a_s_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
                return True
        elif a_q_chr_loci.sp_id == b_s_chr_loci.sp_id and a_q_chr_loci.chr_id == b_s_chr_loci.chr_id and a_s_chr_loci.sp_id == b_q_chr_loci.sp_id and a_s_chr_loci.chr_id == b_q_chr_loci.chr_id:
            if section(a_q_chr_loci.range, b_s_chr_loci.range, just_judgement=True) and section(a_q_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
                return True

        return False

    elif section_side == 1:
        if a_q_chr_loci.sp_id == b_q_chr_loci.sp_id and a_q_chr_loci.chr_id == b_q_chr_loci.chr_id and section(a_q_chr_loci.range, b_q_chr_loci.range, just_judgement=True):
            return True

        if a_s_chr_loci.sp_id == b_s_chr_loci.sp_id and a_s_chr_loci.chr_id == b_s_chr_loci.chr_id and section(a_s_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
            return True

        if a_q_chr_loci.sp_id == b_s_chr_loci.sp_id and a_q_chr_loci.chr_id == b_s_chr_loci.chr_id and section(a_q_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
            return True

        if a_s_chr_loci.sp_id == b_q_chr_loci.sp_id and a_s_chr_loci.chr_id == b_q_chr_loci.chr_id and section(a_q_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
            return True

        return False


def merge_two_loci_pair(loci_pair_a, loci_pair_b, new_lp_id=None):
    if not section_LP(loci_pair_a, loci_pair_b, 2):
        raise ValueError(
            "given loci pair is failed to get section in two side")

    a_q_chr_loci = loci_pair_a.q_chr_loci
    a_s_chr_loci = loci_pair_a.s_chr_loci
    b_q_chr_loci = loci_pair_b.q_chr_loci
    b_s_chr_loci = loci_pair_b.s_chr_loci

    q_chr = a_q_chr_loci.chr_id
    q_sp_id = a_q_chr_loci.sp_id
    s_chr = a_s_chr_loci.chr_id
    s_sp_id = a_s_chr_loci.sp_id

    if a_q_chr_loci.sp_id == b_q_chr_loci.sp_id and a_q_chr_loci.chr_id == b_q_chr_loci.chr_id and section(a_q_chr_loci.range, b_q_chr_loci.range, just_judgement=True):
        q_start = min([a_q_chr_loci.start, a_q_chr_loci.end] +
                      [b_q_chr_loci.start, b_q_chr_loci.end])
        q_end = max([a_q_chr_loci.start, a_q_chr_loci.end] +
                    [b_q_chr_loci.start, b_q_chr_loci.end])
        s_start = min([a_s_chr_loci.start, a_s_chr_loci.end] +
                      [b_s_chr_loci.start, b_s_chr_loci.end])
        s_end = max([a_s_chr_loci.start, a_s_chr_loci.end] +
                    [b_s_chr_loci.start, b_s_chr_loci.end])

    elif a_q_chr_loci.sp_id == b_s_chr_loci.sp_id and a_q_chr_loci.chr_id == b_s_chr_loci.chr_id and section(a_q_chr_loci.range, b_s_chr_loci.range, just_judgement=True):
        q_start = min([a_q_chr_loci.start, a_q_chr_loci.end] +
                      [b_s_chr_loci.start, b_s_chr_loci.end])
        q_end = max([a_q_chr_loci.start, a_q_chr_loci.end] +
                    [b_s_chr_loci.start, b_s_chr_loci.end])
        s_start = min([a_s_chr_loci.start, a_s_chr_loci.end] +
                      [b_q_chr_loci.start, b_q_chr_loci.end])
        s_end = max([a_s_chr_loci.start, a_s_chr_loci.end] +
                    [b_q_chr_loci.start, b_q_chr_loci.end])

    else:
        raise ValueError(
            "given loci pair is failed to get section in two side")

    q_chr_loci = ChrLoci(q_chr, None, q_start, q_end, q_sp_id)
    s_chr_loci = ChrLoci(s_chr, None, s_start, s_end, s_sp_id)

    if a_q_chr_loci.len() > b_q_chr_loci.len():
        strand = loci_pair_a.strand
    else:
        strand = loci_pair_b.strand

    new_lp = LociPair(q_chr_loci, s_chr_loci,
                      strand=strand, loci_pair_id=new_lp_id)

    return new_lp


def merge_loci_pair_list(loci_pair_list):
    # print(len(loci_pair_list))
    # print(loci_pair_list)
    loci_pair_dict = dict(enumerate(loci_pair_list))

    merged_flag = False
    merged_id_list = []
    merged_loci_pair_list = []
    for i in loci_pair_dict:
        if merged_flag:
            break
        for j in loci_pair_dict:
            if merged_flag:
                break
            if i == j:
                continue
            else:
                if section_LP(loci_pair_dict[i], loci_pair_dict[j], 2):
                    merged_lp = merge_two_loci_pair(
                        loci_pair_dict[i], loci_pair_dict[j])
                    merged_loci_pair_list.append(merged_lp)
                    merged_flag = True
                    merged_id_list.append(i)
                    merged_id_list.append(j)

    if merged_flag:
        output_loci_pair_list = []
        for i in loci_pair_dict:
            if not i in merged_id_list:
                output_loci_pair_list.append(loci_pair_dict[i])

        output_loci_pair_list = output_loci_pair_list + merged_loci_pair_list
        output_loci_pair_list = merge_loci_pair_list(output_loci_pair_list)
        return output_loci_pair_list
    else:
        return loci_pair_list


if __name__ == "__main__":
    # test

    q_cl = ChrLoci(chr_id='Chr1', start=1000000, end=2000000, species_id='Sly')
    s_cl = ChrLoci(chr_id='Chr6', start=11000000,
                   end=12000000, species_id='Stu')

    lp1 = LociPair(q_cl, s_cl, strand="+", loci_pair_id=1)

    q_cl = ChrLoci(chr_id='Chr1', start=1500000, end=1600000, species_id='Sly')
    s_cl = ChrLoci(chr_id='Chr6', start=11500000,
                   end=11600000, species_id='Stu')

    lp2 = LociPair(q_cl, s_cl, strand="-", loci_pair_id=2)

    q_cl = ChrLoci(chr_id='Chr1', start=150000, end=160000, species_id='Sly')
    s_cl = ChrLoci(chr_id='Chr6', start=1150000, end=1160000, species_id='Stu')

    lp3 = LociPair(q_cl, s_cl, strand="-", loci_pair_id=2)

    q_cl = ChrLoci(chr_id='Chr1', start=2500000, end=2600000, species_id='Sly')
    s_cl = ChrLoci(chr_id='Chr6', start=21500000,
                   end=21600000, species_id='Stu')

    lp4 = LociPair(q_cl, s_cl, strand="+", loci_pair_id=2)

    q_cl = ChrLoci(chr_id='Chr1', start=1550000, end=2150000, species_id='Sly')
    s_cl = ChrLoci(chr_id='Chr6', start=11550000,
                   end=11650000, species_id='Stu')

    # lp5 = LociPair(q_cl, s_cl, strand="+", loci_pair_id=2)
    lp5 = LociPair(s_cl, q_cl, strand="+", loci_pair_id=2)

    lp_list = [lp1, lp2, lp3, lp4, lp5]

    merged_lp_list = merge_loci_pair_list(lp_list)

    # merge test
    from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse

    synteny_file = '/lustre/home/xuyuxing/Work/Gel/GenomeStat/Gel_synteny_by_Ash.txt'
    file_info = tsv_file_parse(synteny_file)

    lp_list = []
    for i in file_info:
        q_sp, q_c, q_s, q_e, s_sp, s_c, s_s, s_e, strand = file_info[i]
        q_sp, q_c, q_s, q_e, s_sp, s_c, s_s, s_e, strand = q_sp, q_c, int(q_s), int(q_e), s_sp, s_c, int(s_s), int(s_e), strand
        
        q_cl = ChrLoci(chr_id=q_c, start=q_s, end=q_e, species_id=q_sp)
        s_cl = ChrLoci(chr_id=s_c, start=s_s, end=s_e, species_id=s_sp)

        lp = LociPair(q_cl, s_cl, strand=strand)

        lp_list.append(lp)

    merged_lp_list = merge_loci_pair_list(lp_list)

    # coverage
    