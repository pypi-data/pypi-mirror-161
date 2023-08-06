from Bio import SeqIO
from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_name_record_dict_db

mirbase_path = "/lustre/home/xuyuxing/Database/mirbase/mirbase22/"
tax_record_dict_file = "/lustre/home/xuyuxing/Database/genome/info/NCBI/taxonomy/tax_record_dict.db"
miRNA_dat = mirbase_path + "miRNA.dat"

def find_miRNA_in_lineage():

    Viridiplantae_taxid = "33090"
    output_file = "/lustre/home/xuyuxing/Database/mirbase/mirbase22/plant.miRNA"

    num = 0
    output_list = []
    for record in SeqIO.parse(miRNA_dat, "embl"):
        mirna_id = record.id
        description = record.description
        species = description.split(" ")[0] + " " + description.split(" ")[1]
        for i in record.features:
            if i.type == "miRNA":
                product = i.qualifiers['product'][0]
                accession = i.qualifiers['accession'][0]
                evidence = i.qualifiers['evidence'][0]
                output_list.append((mirna_id, accession, product, evidence, species))
                num = num + 1

    output_list = list(set(output_list))

    output_dict = {}
    for mirna_id, accession, product, evidence, species in output_list:
        if accession in output_dict:
            if output_dict[accession]["evidence"] == "experimental":
                continue
        output_dict[accession] = {}
        output_dict[accession] = {
            "mirna_id": mirna_id,
            "accession": accession,
            "product": product,
            "evidence": evidence,
            "species": species
        }

    tax_name_list = [output_dict[i]["species"] for i in output_dict]
    tax_name_list = list(set(tax_name_list))

    tax_record_dict = read_tax_name_record_dict_db(tax_record_dict_file, tax_name_list)

    plant_miRNA = {}
    missed_taxid = []
    for i in output_dict:
        record = output_dict[i]
        if not record["species"] in tax_record_dict:
            missed_taxid.append(record["species"])
            continue
        record_tax_record = tax_record_dict[record["species"]]
        if hasattr(record_tax_record,"kingdom") and record_tax_record.kingdom == Viridiplantae_taxid:
            plant_miRNA[i] = output_dict[i]

    missed_taxid = list(set(missed_taxid))

    with open(output_file,"w") as f:
        for i in plant_miRNA:
            key_name = ["mirna_id", "accession", "product", "evidence", "species"]
            printer = ""
            for j in key_name:
                printer = printer+plant_miRNA[i][j]+"\t"
            printer.rstrip("\t")
            f.write(printer+"\n")


def get_all_ref():
    with open("/lustre/home/xuyuxing/Database/mirbase/mirbase22/refernces.txt","w") as f:
        output_list=[]
        for record in SeqIO.parse(miRNA_dat, "embl"):
            if "references" in record.annotations:
                for ref in record.annotations["references"]:
                    output_list.append((ref.title,ref.journal,ref.pubmed_id))
        output_list = list(set(output_list))
        for i in output_list:
            f.write("%s\t%s\t%s\n" % i)
