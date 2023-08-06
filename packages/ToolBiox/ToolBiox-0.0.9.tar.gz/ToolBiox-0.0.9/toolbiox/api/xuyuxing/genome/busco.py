# busco 4 output dir information parser

import os
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.xuyuxing.seq.genome_feature import ChrLoci, section_of_chr_loci
from toolbiox.api.xuyuxing.genome.hmmer import hmmsearch_domtblout_parse
from BCBio import GFF


def read_full_table(full_table_file, mode):
    """
    full_table_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.genome_vs_embryophyta_odb10/run_embryophyta_odb10/full_table.tsv'
    full_table_file = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker_v2/round1/Gel.frag.1.maker.output/Gel_aa_vs_embryophyta_odb10/run_embryophyta_odb10/full_table.tsv'
    """
    busco_dict = {}

    if mode == 'genome':
        data_info = tsv_file_dict_parse(full_table_file,
                                        fieldnames=["Busco_id", "Status", "Sequence", "Gene_Start", "Gene_End", "Score",
                                                    "Length", "OrthoDB_url", "Description"], ignore_prefix=r'^#')

        for i in data_info:
            info = data_info[i]
            if info["Busco_id"] not in busco_dict:
                busco_dict[info["Busco_id"]] = BuscoObject(info["Busco_id"], info["Status"], [], info["OrthoDB_url"],
                                                           info["Description"])

            tmp_chr_loci = ChrLoci(
                chr_id=info["Sequence"], strand=None, start=info["Gene_Start"], end=info["Gene_End"])
            busco_dict[info["Busco_id"]].hits.append(tmp_chr_loci)

    elif mode == 'proteins':
        data_info = tsv_file_dict_parse(full_table_file,
                                        fieldnames=["Busco_id", "Status", "Sequence", "Score", "Length", "OrthoDB_url",
                                                    "Description"], ignore_prefix=r'^#')

        for i in data_info:
            info = data_info[i]
            if info["Busco_id"] not in busco_dict:
                busco_dict[info["Busco_id"]] = BuscoObject(info["Busco_id"], info["Status"], [], info["OrthoDB_url"],
                                                           info["Description"])

            busco_dict[info["Busco_id"]].hits.append(info["Sequence"])

    return busco_dict


def load_augustus_output(augustus_output_dir):
    """
    augustus_output_dir = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.genome_vs_embryophyta_odb10/run_embryophyta_odb10/augustus_output"
    """

    # gff
    gff_dir = augustus_output_dir + "/gff"

    augustus_range_dict = {}
    for gff_file in os.listdir(gff_dir):
        if gff_file.split('.')[-1] == 'gff':
            query_busco_id = gff_file.split('.')[0]
            gff_file = gff_dir + "/" + gff_file
            chr_loci_list = []
            with open(gff_file, 'r') as in_handle:
                for rec in GFF.parse(in_handle):
                    for gene in rec.features:
                        if gene.type != 'gene':
                            continue
                        start = gene.location.start.position + 1
                        end = gene.location.end.position
                        chr_loci_list.append(
                            ChrLoci(chr_id=rec.id, strand=gene.strand, start=start, end=end))

            augustus_range_dict[query_busco_id] = chr_loci_list

    return augustus_range_dict


def load_blast_output(blast_output_dir):
    """
    blast_output_dir = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.genome_vs_embryophyta_odb10/run_embryophyta_odb10/blast_output"
    """

    coordinates_file1 = blast_output_dir + "/coordinates.tsv"
    coordinates_file2 = blast_output_dir + "/coordinates_missing_and_frag_rerun.tsv"

    info_dict1 = tsv_file_dict_parse(coordinates_file1, fieldnames=[
                                     'busco_id', 'contig', 'start', 'end'], prefix="A_")
    info_dict2 = tsv_file_dict_parse(coordinates_file2, fieldnames=[
                                     'busco_id', 'contig', 'start', 'end'], prefix="B_")

    info_dict = merge_dict([info_dict1, info_dict2], False)

    blast_range_dict = {}
    for id in info_dict:
        info = info_dict[id]
        if info['busco_id'] not in blast_range_dict:
            blast_range_dict[info['busco_id']] = []

        chr_loci_tmp = ChrLoci(
            chr_id=info['contig'], strand=None, start=info['start'], end=info['end'])

        overlap_loci = []
        for i in blast_range_dict[info['busco_id']]:
            if section_of_chr_loci(chr_loci_tmp, i)[0]:
                overlap_loci.append(i)

        for i in overlap_loci:
            blast_range_dict[info['busco_id']].remove(i)

        overlap_loci.append(chr_loci_tmp)

        blast_range_dict[info['busco_id']].append(
            sorted(overlap_loci, key=lambda x: x.length, reverse=True)[0])

    return blast_range_dict


def load_hmmer_output(hmmer_output_dir):
    """
    hmmer_output_dir = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.genome_vs_embryophyta_odb10/run_embryophyta_odb10/hmmer_output"
    """

    hmmer_range_dict = {}
    for hmmer_file in os.listdir(hmmer_output_dir):
        hmmer_file = hmmer_output_dir + "/" + hmmer_file
        hmmer_info = hmmsearch_domtblout_parse(hmmer_file)

        for hmmer_target_id in hmmer_info:
            hmmer_target = hmmer_info[hmmer_target_id]
            for domin in hmmer_target.HmmDomain_list:
                q_name = domin.q_name
                if q_name not in hmmer_range_dict:
                    hmmer_range_dict[q_name] = []
                hmmer_range_dict[q_name].append(hmmer_target_id)

    for i in hmmer_range_dict:
        hmmer_range_dict[i] = list(set(hmmer_range_dict[i]))

    return hmmer_range_dict


class BuscoObject(object):
    def __init__(self, id, status=None, hits=None, OrthoDB_url=None, description=None, evidence=None):
        self.id = id
        self.status = status
        self.hits = hits
        self.OrthoDB_url = OrthoDB_url
        self.description = description
        self.evidence = evidence


class BuscoResults(object):
    def __init__(self, busco_output_dir, mode, lineage, busco_datadir=None, modify_dict={}):
        # input
        self.dir = busco_output_dir
        self.mode = mode
        self.lineage = lineage
        self.busco_datadir = busco_datadir

        # get cwd and relpath of dir
        self.abspath = os.path.abspath(self.dir)
        self.cwd = os.getcwd()

        # get important dir and file in busco output
        self.busco_run_dir = self.abspath + "/run_" + self.lineage

        self.full_table = self.busco_run_dir + "/full_table.tsv"

        self.evidence_dir = {}
        self.evidence_dir['hmmer'] = self.busco_run_dir + "/hmmer_output"

        # only in genome mode
        if self.mode == 'genome':
            self.evidence_dir['augustus'] = self.busco_run_dir + \
                "/augustus_output"
            self.evidence_dir['blast'] = self.busco_run_dir + "/blast_output"

        # from modify_dict to change defaults attr
        for new_attr in modify_dict:
            if hasattr(self, new_attr):
                setattr(self, new_attr, modify_dict[new_attr])

        # if have busco_datadir
        if self.busco_datadir:
            self.lineage_datadir = self.busco_datadir + "/lineages/" + self.lineage

        # load results
        self.load_busco_results()

    def load_busco_results(self):
        # load full table
        self.busco_dict = read_full_table(self.full_table, self.mode)

        # load evidence_dir
        # for genome mode
        if self.mode == 'genome':
            # augustus output
            augustus_range_dict = load_augustus_output(
                self.evidence_dir['augustus'])

            # blast output
            blast_range_dict = load_blast_output(self.evidence_dir['blast'])

            # hmmer output
            hmmer_range_dict = load_hmmer_output(self.evidence_dir['hmmer'])

            for busco_id in self.busco_dict:
                self.busco_dict[busco_id].evidence = {}

                if busco_id in augustus_range_dict:
                    self.busco_dict[busco_id].evidence['augustus'] = augustus_range_dict[busco_id]
                else:
                    self.busco_dict[busco_id].evidence['augustus'] = None

                if busco_id in blast_range_dict:
                    self.busco_dict[busco_id].evidence['blast'] = blast_range_dict[busco_id]
                else:
                    self.busco_dict[busco_id].evidence['blast'] = None

                if busco_id in hmmer_range_dict:
                    self.busco_dict[busco_id].evidence['hmmer'] = hmmer_range_dict[busco_id]
                else:
                    self.busco_dict[busco_id].evidence['hmmer'] = None

        # for protein mode
        elif self.mode == 'proteins':
            # hmmer output
            hmmer_range_dict = load_hmmer_output(self.evidence_dir['hmmer'])

            for busco_id in self.busco_dict:
                self.busco_dict[busco_id].evidence = {}

                if busco_id in hmmer_range_dict:
                    self.busco_dict[busco_id].evidence['hmmer'] = hmmer_range_dict[busco_id]
                else:
                    self.busco_dict[busco_id].evidence['hmmer'] = None


if __name__ == '__main__':
    # parse orthofinder dir
    busco_output_dir = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.genome_vs_embryophyta_odb10'
    mode = 'genome'
    lineage = 'embryophyta_odb10'
    busco_datadir = '/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/busco_downloads'

    # load data dir
    busco_results = BuscoResults(
        busco_output_dir, mode, lineage, busco_datadir=busco_datadir, modify_dict={})

    # count status number
    from collections import Counter
    busco_status = Counter(
        [busco_results.busco_dict[i].status for i in busco_results.busco_dict])

    complete_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Complete']
    duplicated_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Duplicated']
    fragmented_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Fragmented']
    missing_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Missing']

    # parse orthofinder dir
    busco_output_dir = '/lustre/home/xuyuxing/Work/Orobanchaceae/phylogenetic/busco/Aca_vs_embryophyta_odb10'
    mode = 'proteins'
    lineage = 'embryophyta_odb10'
    busco_datadir = '/lustre/home/xuyuxing/Work/Orobanchaceae/phylogenetic/busco/busco_downloads'

    # load data dir
    busco_results = BuscoResults(
        busco_output_dir, mode, lineage, busco_datadir=busco_datadir, modify_dict={})

    # count status number
    from collections import Counter
    busco_status = Counter(
        [busco_results.busco_dict[i].status for i in busco_results.busco_dict])

    complete_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Complete']
    duplicated_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Duplicated']
    fragmented_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Fragmented']
    missing_buscos = [
        i for i in busco_results.busco_dict if busco_results.busco_dict[i].status == 'Missing']
