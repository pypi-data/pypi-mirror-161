from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.xuyuxing.evolution.taxonomy import build_taxon_database
from collections import OrderedDict
from toolbiox.lib.common.util import printer_list
import re

def ContaminationFilter_main(args):
    split_genome = read_fasta_by_faidx(args.split_genome_fasta)
    split_contig_list = list(split_genome.keys())
    tax_record_dict = build_taxon_database(args.tax_dir)

    # read contig split
    contig_split_dict = {}
    for split_contig_id in split_contig_list:
        matchOBJ = re.match(r'^(\S+)_(\d+)-(\d+)$', split_contig_id)
        if matchOBJ:
            contig_id, start, end = matchOBJ.groups()
            if not contig_id in contig_split_dict:
                contig_split_dict[contig_id] = []
            contig_split_dict[contig_id].append(split_contig_id)

    # read taxon_assign_output
    from toolbiox.lib.common.fileIO import tsv_file_dict_parse

    taxon_assign_dict = tsv_file_dict_parse(args.taxon_assign_output,
                                            fieldnames=["split_id", "mrca_taxon_id", "mrca_taxon",
                                                        "recommand_taxon_id",
                                                        "recommand_taxon", "q_value"], key_col="split_id")

    classification_type = OrderedDict(
        {"Viruses": "10239", "Archaea": "2157", "Bacteria": "2", "Viridiplantae": "33090",
            "Fungi": "4751", "Metazoa": "33208", "Other": None, "No_hit": None})

    contig_taxon_dict = {}
    for contig_id in contig_split_dict:
        contig_taxon_dict[contig_id] = {i: 0 for i in classification_type}
        for split_id in contig_split_dict[contig_id]:
            if split_id in taxon_assign_dict:
                recommand_taxon_id = taxon_assign_dict[split_id]["recommand_taxon_id"]
                recommand_taxon = tax_record_dict[recommand_taxon_id]
                recommand_taxon_lineage = [i[0] for i in recommand_taxon.get_lineage(tax_record_dict)]
                recommand_classtype_list = [i for i in classification_type if
                                            classification_type[i] in recommand_taxon_lineage]
                if len(recommand_classtype_list) == 0:
                    contig_taxon_dict[contig_id]["Other"] += 1
                else:
                    recommand_classtype = recommand_classtype_list[0]
                    contig_taxon_dict[contig_id][recommand_classtype] += 1
            else:
                contig_taxon_dict[contig_id]["No_hit"] += 1

    with open(args.output_file, 'w') as f:
        header_string = printer_list([type for type in classification_type], sep="\t", head="contig_id\t")
        f.write(header_string + "\n")

        for contig_id in contig_taxon_dict:
            record_string = printer_list([contig_taxon_dict[contig_id][type] for type in classification_type],
                                            sep="\t", head=contig_id + "\t")
            f.write(record_string + "\n")

"""
genome_fasta=
split_genome_fasta=$genome_fasta.split
diamond_output=$split_genome_fasta.bls
taxon_assign_output=$split_genome_fasta.taxon
contamination_report=contamination_report.txt

taxon_nr_db=/lustre/home/xuyuxing/Database/NCBI/nr/2020/nr.taxon.dmnd
taxon_dump=/lustre/home/xuyuxing/Database/NCBI/nr/2020/taxdmp
threads=56
max_target_seqs=50

python ~/python_project/Genome_work_tools/GenomeTools.py FragmentGenome $genome_fasta $split_genome_fasta 10000 10000

diamond blastx --query $split_genome_fasta --max-target-seqs $max_target_seqs --db $taxon_nr_db --evalue 1e-5 --out $diamond_output --outfmt 6 qseqid sseqid staxids pident length mismatch gapopen qstart qend sstart send evalue bitscore --threads $threads

python ~/python_project/Genome_work_tools/TaxonTools.py DiamondTaxonAssign -n $threads -o $taxon_assign_output $diamond_output $taxon_dump

python ~/python_project/Genome_work_tools/GenomeTools.py ContaminationFilter $split_genome_fasta $taxon_assign_output $contamination_report
"""

"""
class abc():
    pass

args=abc()

args.split_genome_fasta = "/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/diamond/Gel.genome.v1.0.final.rename.split.fasta"
args.taxon_assign_output = "/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/diamond/Gel.genome.v1.0.final.rename.split.taxon"
args.tax_dir = '/lustre/home/xuyuxing/Database/NCBI/nr/2020/taxdmp'
args.output_file = "/lustre/home/xuyuxing/Database/Gel/genome/assembly/contig_filter/diamond/Gel.genome.v1.0.final.rename.contamination_report.txt"
"""