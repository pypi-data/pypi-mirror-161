import sys

sys.path.append("/lustre/home/xuyuxing/python_project/Genome_work_tools/")
from BCBio import GFF
from toolbiox.api.xuyuxing.file_parser.fileIO import dict_to_tsv_file
from toolbiox.lib.common.os import md5sum_maker
import re
import gzip
import os
import sys


def get_location_string(location_range_list, strand):
    location_range_list = sorted(location_range_list, key=lambda x: x[0])
    if len(location_range_list) > 1:
        location_string = ""
        for i in location_range_list:
            if min(i) == max(i):
                location_string = location_string + "%d," % min(i)
            else:
                location_string = location_string + "%d..%d," % (min(i), max(i))
        location_string = location_string.rstrip(",")
        location_string = "join(%s)" % location_string

    else:
        i = location_range_list[0]
        location_string = "%d..%d" % (i[0], i[1])

    if strand == -1:
        location_string = "complement(%s)" % location_string

    return location_string


def NCBIGffModel(in_file):
    # remove line with "part" tag, which GFF reader can't parse
    f_orgin = gzip.open(in_file, 'rt')
    f_filterd = open(in_file.replace(".gff.gz", "") + ".filterd.gff", "w")
    for row in f_orgin:
        row_filterd = re.match(r".*;part=.*", row)
        if not row_filterd:
            f_filterd.write(row)
    f_orgin.close()
    f_filterd.close()

    # NCBI gff file have many diff type
    ## best type, which have "gene_biotype" tag, it can tell me this gene is good
    in_handle = open(in_file.replace(".gff.gz", "") + ".filterd.gff")
    gene_dict = {}
    num = 0
    gene_model = {}
    for rec in GFF.parse(in_handle):
        for gene in rec.features:
            gene_dict[gene.id] = gene, rec.id
            if 'gene_biotype' in gene.qualifiers and gene.qualifiers['gene_biotype'][0] == 'protein_coding':
                protein_dict = {}
                for rna in gene.sub_features:
                    location_range_list = []
                    gene_length = 0
                    for cds in rna.sub_features:
                        if cds.type == "CDS":
                            if not "protein_id" in cds.qualifiers:
                                continue
                            # protein_id = cds.qualifiers["protein_id"][0]
                            cds_length = abs(cds.location.start - cds.location.end)
                            location_range_list.append((int(cds.location.start) + 1, int(cds.location.end)))
                            gene_length = gene_length + cds_length
                            # if protein_id not in protein_dict:
                            #     protein_dict[protein_id] = cds_length
                            # else:
                            #     protein_dict[protein_id] = protein_dict[protein_id] + cds_length

                    if len(location_range_list) == 0:
                        continue

                    location_string = get_location_string(location_range_list, gene.strand)

                    protein_dict[location_string] = gene_length

                if len(protein_dict) == 0:
                    # some time cds not under a mRNA, but close to gene
                    location_range_list = []
                    gene_length = 0
                    for cds in gene.sub_features:
                        if cds.type == "CDS":
                            if not "protein_id" in cds.qualifiers:
                                continue
                            # protein_id = cds.qualifiers["protein_id"][0]
                            location_range_list.append((int(cds.location.start) + 1, int(cds.location.end)))
                            cds_length = abs(cds.location.start - cds.location.end)
                            gene_length = gene_length + cds_length
                            # if protein_id not in protein_dict:
                            #     protein_dict[protein_id] = cds_length
                            # else:
                            #     protein_dict[protein_id] = protein_dict[protein_id] + cds_length

                    if len(location_range_list) == 0:
                        continue

                    location_string = get_location_string(location_range_list, gene.strand)

                    protein_dict[location_string] = gene_length

                if len(protein_dict) == 0:
                    continue

                model_protein = sorted(protein_dict, key=lambda x: protein_dict[x], reverse=True)[0]
                gene_model[gene.id] = (model_protein, rec.id)
    in_handle.close()

    ## this type don't have "gene_biotype" tag, we need try every gene
    if len(gene_model) == 0:  # maybe no pseudogene
        in_handle = open(in_file.replace(".gff.gz", "") + ".filterd.gff")
        gene_dict = {}
        num = 0
        gene_model = {}
        for rec in GFF.parse(in_handle):
            for gene in rec.features:
                gene_dict[gene.id] = gene, rec.id
                protein_dict = {}
                for rna in gene.sub_features:
                    location_range_list = []
                    gene_length = 0
                    for cds in rna.sub_features:
                        if cds.type == "CDS":
                            if not "protein_id" in cds.qualifiers:
                                continue
                            # protein_id = cds.qualifiers["protein_id"][0]
                            cds_length = abs(cds.location.start - cds.location.end)
                            location_range_list.append((int(cds.location.start) + 1, int(cds.location.end)))
                            gene_length = gene_length + cds_length
                            # if protein_id not in protein_dict:
                            #     protein_dict[protein_id] = cds_length
                            # else:
                            #     protein_dict[protein_id] = protein_dict[protein_id] + cds_length

                    if len(location_range_list) == 0:
                        continue

                    location_string = get_location_string(location_range_list, gene.strand)

                    protein_dict[location_string] = gene_length

                if len(protein_dict) == 0:
                    # some time cds not under a mRNA, but close to gene
                    location_range_list = []
                    gene_length = 0
                    for cds in gene.sub_features:
                        if cds.type == "CDS":
                            if not "protein_id" in cds.qualifiers:
                                continue
                            # protein_id = cds.qualifiers["protein_id"][0]
                            location_range_list.append((int(cds.location.start) + 1, int(cds.location.end)))
                            cds_length = abs(cds.location.start - cds.location.end)
                            gene_length = gene_length + cds_length
                            # if protein_id not in protein_dict:
                            #     protein_dict[protein_id] = cds_length
                            # else:
                            #     protein_dict[protein_id] = protein_dict[protein_id] + cds_length

                    if len(location_range_list) == 0:
                        continue

                    location_string = get_location_string(location_range_list, gene.strand)

                    protein_dict[location_string] = gene_length

                if len(protein_dict) == 0:
                    continue

                model_protein = sorted(protein_dict, key=lambda x: protein_dict[x], reverse=True)[0]
                gene_model[gene.id] = (model_protein, rec.id)
        in_handle.close()

    ## this type all gff file just have cds type

    if len(gene_model) == 0:  # maybe is all cds gff
        # raise ValueError(in_file)
        in_handle = open(in_file.replace(".gff.gz", "") + ".filterd.gff")
        gene_dict = {}
        num = 0
        gene_model = {}
        type_list = []

        for rec in GFF.parse(in_handle):
            location_range_dict = {}
            for cds in rec.features:
                gene_dict[cds.id] = cds, rec.id
                if cds.type == "sequence_alteration":
                    continue
                type_list.append(cds.type)
                if cds.type == "CDS":
                    if not "protein_id" in cds.qualifiers:
                        continue
                    protein_id = cds.qualifiers["protein_id"][0]
                    if not protein_id in location_range_dict:
                        location_range_dict[protein_id] = [[], cds.strand]
                    location_range_dict[protein_id][0].append((int(cds.location.start) + 1, int(cds.location.end)))

            for protein_id in location_range_dict:
                location_string = get_location_string(location_range_dict[protein_id][0],
                                                      location_range_dict[protein_id][1])
                gene_model[protein_id] = (location_string, rec.id)

        type_list = list(set(type_list))
        if not "CDS" in type_list:
            raise ValueError("Unknown gff style!")
        in_handle.close()

    os.remove(in_file.replace(".gff.gz", "") + ".filterd.gff")

    # # gene id in ncbi gff hard to link to pt cds fasta id, so we need change to locus_tag or Dbxref and so on
    #
    # gene_tmp_id = list(gene_model.keys())[0]
    # gene_tmp, chr_id = gene_dict[gene_tmp_id]
    #
    # if 'locus_tag' in gene_tmp.qualifiers:
    #     renew_id_flag = 'locus_tag'
    # elif 'Dbxref' in gene_tmp.qualifiers:
    #     renew_id_flag = 'Dbxref'
    # else:
    #     raise ValueError("I don't know what can I use as new gene id")

    # gene id in ncbi gff hard to link to pt cds fasta id, so we need change to locus_tag or Dbxref and so on
    # not each gene have locus_tag or Dbxref, but they have locus info, I will use it

    output_dict = {}
    for i in gene_model:
        location_string, chr_id = gene_model[i]

        start = min([int(i) for i in re.findall(r'\d+', location_string)])
        end = max([int(i) for i in re.findall(r'\d+', location_string)])

        if re.match(r'complement', location_string):
            strand = -1
        else:
            strand = 1

        output_dict[i] = {
            "location_string": location_string,
            "scaffold": chr_id,
            "start": start,
            "end": end,
            "strand": strand,
            # "locus_tag": gene.qualifiers['locus_tag'][0]
        }

    return output_dict


def JGIGffModel(in_file, out_file):
    import re

    def hash_map(dict_list):
        dict_hash = {}
        for i in dict_list:
            for j in dict_list[i]:
                if not j in dict_hash:
                    dict_hash[j] = []
                dict_hash[j].append(i)
        return dict_hash

    def integrate_element(dict_list, num):
        dict_hash = hash_map(dict_list)
        flag = 0
        deleted = []
        for i in dict_hash:
            if not len(dict_hash[i]) > 1:
                continue
            #        print i
            dict_list[num] = []
            for j in dict_hash[i]:
                if j in deleted:
                    continue
                dict_list[num] = list(set(dict_list[num] + dict_list[j]))
                del dict_list[j]
                deleted.append(j)
                flag = 1
            num = num + 1
            break
        return flag, num

    def NoRed_element(list_all):
        dict_list = {}
        num = 0
        for i in list_all:
            dict_list[num] = i
            num = num + 1
        # print dict_list
        flag = 1
        while flag == 1:
            flag, num = integrate_element(dict_list, num)
        #        print len(dict_list)
        output = []
        for i in dict_list:
            output.append(dict_list[i])
        return output

    def section(list1, list2):
        all = sorted(list(list(list1) + list(list2)))
        deta = all[2] - all[1] + 1
        smallest_length = min(abs(list1[1] - list1[0] + 1), abs(list2[1] - list2[0] + 1))
        if max(list1) >= min(list2) and max(list2) >= min(list1):
            If_inter = 1  # Yes
        else:
            If_inter = 0  # No
        overlap = float(deta) / float(smallest_length)
        return int(If_inter), overlap

    def Detect_Red_Range(all_list, overlap_cut=0.6):
        Candi_list = []
        for i in all_list:
            i_section = all_list[i][0]
            for j in all_list:
                j_section = all_list[j][0]
                if i == j:
                    continue
                # print i,j
                If_inter, overlap = section(i_section, j_section)
                if If_inter:
                    if overlap >= overlap_cut:
                        Candi_list.append(sorted([i, j]))
        return NoRed_element(Candi_list)

    F3 = gzip.open(in_file, 'rt')
    output = {}
    cds_info_dict = {}
    temp_id = 0
    for each_line in F3:
        each_line = re.sub('\n', '', each_line)
        info = each_line.split("\t")
        scaffold = info[0]
        type = info[2]
        if not type == "CDS":
            continue
        start = min(int(info[3]), int(info[4]))
        end = max(int(info[3]), int(info[4]))
        if info[6] == "+":
            strand = 1
        else:
            strand = -1
        qualifiers = info[8]
        qualifiers = qualifiers.split("; ")
        for i in qualifiers:
            name_matchObj = re.match(r'name \"(.*)\"', i)
            proteinId_matchObj = re.match(r'proteinId (\d+)', i)
            if name_matchObj:
                name = name_matchObj.group(1)
            if proteinId_matchObj:
                proteinId = proteinId_matchObj.group(1)

        temp_id = temp_id + 1
        cds_info = [proteinId, scaffold, start, end, strand, name]
        cds_info_dict[temp_id] = cds_info

        if not proteinId in output:
            output[proteinId] = [[proteinId, scaffold, start, end, strand, name], [temp_id]]
        else:
            if start < output[proteinId][0][2]:
                output[proteinId][0][2] = start
            if end > output[proteinId][0][3]:
                output[proteinId][0][3] = end
            output[proteinId][1].append(temp_id)
    F3.close()

    # mapping to scaffold
    mapping = {}
    for proteinId in output:
        [proteinId, scaffold, start, end, strand, name], cds_id = output[proteinId]
        if not scaffold in mapping:
            mapping[scaffold] = {}
            mapping[scaffold][1] = {}
            mapping[scaffold][-1] = {}
        mapping[scaffold][strand][proteinId] = [[start, end], cds_id]

    # No isoform
    Red_gene_list = []
    for scaffold in mapping:
        Red_gene_list = Red_gene_list + Detect_Red_Range(mapping[scaffold][1])
        Red_gene_list = Red_gene_list + Detect_Red_Range(mapping[scaffold][-1])

    smaller_proteins_list = []
    for pairs in Red_gene_list:
        id_length = []
        for proteins in pairs:
            total_length = 0
            for cds in output[proteins][1]:
                proteinId_all, scaffold, start, end, strand, name = cds_info_dict[cds]
                length = end - start + 1
                total_length = total_length + length
            id_length.append([proteins, total_length])
        id_length = sorted(id_length, key=lambda e: e[1], reverse=True)

        for i in id_length:
            if id_length.index(i) == 0:
                continue
            smaller_proteins_list.append(i[0])

    column_name_list = ["gene_id", "protein_id", "scaffold", "start", "end", "strand"]

    gene_dict_num = 0
    gene_model = {}
    for i in output:
        proteinId, scaffold, start, end, strand, name = output[i][0]
        if proteinId in smaller_proteins_list:
            continue
        gene_dict_num = gene_dict_num + 1

        gene_model[name] = {
            "gene_id": name,
            "protein_id": proteinId,
            "scaffold": scaffold,
            "start": start,
            "end": end,
            "strand": strand
        }

    column_name_list = ["gene_id", "protein_id", "scaffold", "start", "end", "strand"]

    dict_to_tsv_file(gene_model, out_file, column_name_list, seq=",", gzip_flag=True)

    md5_string = md5sum_maker(out_file)

    return gene_model, md5_string


def BIGGffModel(in_file):
    # remove line with "part" tag, which GFF reader can't parse
    in_handle = gzip.open(in_file, 'rt')
    gene_dict = {}
    num = 0
    gene_model = {}
    for rec in GFF.parse(in_handle):
        for gene in rec.features:
            gene_dict[gene.id] = gene, rec.id

            protein_dict = {}
            for cds in gene.sub_features:
                if not cds.type == "CDS":
                    continue
                protein_id = cds.qualifiers["Protein_Accession"][0]
                if not protein_id in protein_dict:
                    protein_dict[protein_id] = 0
                cds_length = abs(cds.location.start - cds.location.end)
                protein_dict[protein_id] = protein_dict[protein_id] + cds_length

            if len(protein_dict) == 0:
                protein_dict = {}
                for rna in gene.sub_features:
                    if not rna.type == "mRNA":
                        continue
                    for cds in rna.sub_features:
                        if not cds.type == "CDS":
                            continue
                        protein_id = cds.qualifiers["Protein_Accession"][0]
                        if not protein_id in protein_dict:
                            protein_dict[protein_id] = 0
                        cds_length = abs(cds.location.start - cds.location.end)
                        protein_dict[protein_id] = protein_dict[protein_id] + cds_length

            model_protein = sorted(protein_dict, key=lambda x: protein_dict[x], reverse=True)[0]
            gene_model[gene.id] = model_protein

    in_handle.close()

    output_dict = {}
    for i in gene_model:
        gene, rec_id = gene_dict[i]
        start = min(int(gene.location.start+1),int(gene.location.end))
        end = max(int(gene.location.start + 1), int(gene.location.end))


        output_dict[i] = {
            "protein_id": gene_model[i],
            "scaffold": rec_id,
            "start": start,
            "end": end,
            "strand": gene.strand,
            # "locus_tag": gene.qualifiers['locus_tag'][0]
        }

    return output_dict



if __name__ == '__main__':
    in_file = sys.argv[1]
    NCBIGffModel(in_file)
