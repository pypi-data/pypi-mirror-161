from toolbiox.lib.common.util import printer_list
from toolbiox.api.xuyuxing.resource.GO import Obo
from toolbiox.lib.common.os import multiprocess_running
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse, tsv_file_dict_parse
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.api.xuyuxing.resource.uniprot import iterUniprotDB, extract_swiss_info
import pickle
import os
import re
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file


def Arabidopsis_genome_function(work_dir, clean_data_fasta, clean_to_raw_id_map, araport_gff, uniprot_sprot_plants_db, uniprot_trembl_plants_db, kegg_overview, plantcyc_file, obo_file):

    ref_db_name = 'Araport'

    clean_seq_dict = read_fasta_by_faidx(clean_data_fasta)
    seq_annotation_dict = {i: {"dbxrefs": {}} for i in clean_seq_dict}

    tmp_info = tsv_file_parse(clean_to_raw_id_map)
    for i in tmp_info:
        clean_id, raw_id = tmp_info[i]

        if clean_id not in seq_annotation_dict:
            continue

        seq_annotation_dict[clean_id]['dbxrefs']['ref_id'] = raw_id

    # on araport11
    araport_gff = read_gff_file(araport_gff)

    tmp_info = {}
    for g_id in araport_gff['gene']:
        gf = araport_gff['gene'][g_id]
        # gene_name
        if 'symbol' in gf.qualifiers:
            gene_name = gf.qualifiers['symbol'][0]
        else:
            gene_name = ''
        # gene_alias
        if 'Alias' in gf.qualifiers:
            gene_alias = gf.qualifiers['Alias']
        else:
            gene_alias = []
        # full_name
        if 'full_name' in gf.qualifiers:
            full_name = gf.qualifiers['full_name'][0]
        else:
            full_name = ''
        # gene_note
        if 'Note' in gf.qualifiers:
            gene_note = gf.qualifiers['Note'][0]
        else:
            gene_note = ''
        
        tmp_info[g_id] = (gene_name, gene_alias, full_name, gene_note)
        
    for clean_id in seq_annotation_dict:
        raw_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']
        if raw_id in tmp_info:
            seq_annotation_dict[clean_id]['gff_info'] = tmp_info[raw_id]


    # on uniprot

    uniprot_map_file = work_dir+"/uniprot.map"

    if not os.path.exists(uniprot_map_file):
        ref_id_list = set()
        with open(work_dir+"/uniprot.map", 'w') as f:
            num = 0

            for db_tmp in [uniprot_sprot_plants_db, uniprot_trembl_plants_db]:

                for id_tmp, obj in iterUniprotDB(db_tmp):
                    num += 1
                    print(num)

                    dbxref_dict = {}
                    for i in obj.dbxrefs:
                        db_name, db_record = i.split(":", 1)
                        if db_name not in dbxref_dict:
                            dbxref_dict[db_name] = []
                        dbxref_dict[db_name].append(db_record)

                    if ref_db_name in dbxref_dict:
                        ref_id = dbxref_dict[ref_db_name][0]
                        if ref_id not in ref_id_list:
                            ref_id_list = ref_id_list | set([ref_id])
                            f.write("%s\t%s\n" % (ref_id, id_tmp))

    tmp_info = tsv_file_parse(uniprot_map_file)
    ref_dict = {}
    for i in tmp_info:
        ref_id, uniprot_id = tmp_info[i]
        ref_dict[ref_id] = uniprot_id

    for clean_id in seq_annotation_dict:
        ref_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']

        if ref_id in ref_dict:
            seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] = ref_dict[ref_id]
        else:
            seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] = None

    print("There are %d genes, %d have uniprot id, %d failed to find" % (len(seq_annotation_dict), len(
        [i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id']]), len([i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id'] is None])))

    uniq_id_list = [seq_annotation_dict[i]['dbxrefs']['uniprot_id']
                    for i in seq_annotation_dict if not seq_annotation_dict[i]['dbxrefs']['uniprot_id'] is None]

    sprot_dict = extract_swiss_info(uniq_id_list, uniprot_sprot_plants_db)
    trembl_dict = extract_swiss_info(uniq_id_list, uniprot_trembl_plants_db)

    for clean_id in seq_annotation_dict:
        uniprot_id = seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id']

        if uniprot_id:
            if uniprot_id in sprot_dict:
                uni_obj = sprot_dict[uniprot_id]
            elif uniprot_id in trembl_dict:
                uni_obj = trembl_dict[uniprot_id]
            else:
                raise ValueError("error 1")

            # # gene name
            # fullName = uni_obj.description
            # gene_name = uni_obj.annotations['gene_name_primary']
            # alias = uni_obj.annotations['gene_name_synonym']
            # keywords = uni_obj.annotations['keywords']
            # comment_function = uni_obj.annotations['comment_function']

            # db covert
            dbxref_dict = {}
            for i in uni_obj.dbxrefs:
                db_name, db_record = i.split(":", 1)
                if db_name not in dbxref_dict:
                    dbxref_dict[db_name] = []
                dbxref_dict[db_name].append(db_record)

            for i in dbxref_dict:
                seq_annotation_dict[clean_id]['dbxrefs'][i] = dbxref_dict[i]

    for key_word in ['uniprot_id', 'BioCyc', 'GO', 'KEGG', 'Pfam', 'PubMed', 'RefSeq']:
        all_gene = len(seq_annotation_dict)
        get_num = len([i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id']
                       and key_word in seq_annotation_dict[i]['dbxrefs'] and len(seq_annotation_dict[i]['dbxrefs'][key_word]) > 0])
        failed_num = all_gene - get_num
        print("There are %d genes, %d have %s, %d failed to find" %
              (all_gene, get_num, key_word, failed_num))

    # add kegg
    kegg_info_dict = tsv_file_parse(kegg_overview, key_col=1)

    key_word = 'KEGG'
    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            kegg_id = seq_annotation_dict[clean_id]['dbxrefs'][key_word][0]
            if kegg_id in kegg_info_dict:
                kegg_info = kegg_info_dict[kegg_id]
                kg_id, ncbi_id, pw_id, pw_info, md_id, md_info, ko_id, ko_info = kegg_info
                seq_annotation_dict[clean_id]['KEGG'] = (
                    pw_id, pw_info, md_id, md_info, ko_id, ko_info)

    # add GO
    ontology = Obo(obo_file)

    key_word = 'GO'
    all_go_list = []
    for clean_id in seq_annotation_dict:

        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            go_id_list = seq_annotation_dict[clean_id]['dbxrefs'][key_word]

            go_info_dict = {}
            for go_id in go_id_list:
                go_info = ontology.get(go_id)
                if go_info:
                    go_info_dict[go_info['id']] = go_info
                    all_go_list.append(go_id)

            seq_annotation_dict[clean_id]['GO'] = go_info_dict

    all_go_list = list(set(all_go_list))

    def get_all_parents(go_id):
        parent_list = [i[0] for i in ontology.find_parents(go_id, expand=True)]
        parent_list.append(go_id)
        return list(set(parent_list))

    go_parent_dict = multiprocess_running(
        get_all_parents, [(i,) for i in all_go_list], 56, args_id_list=all_go_list)

    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            go_id_list = seq_annotation_dict[clean_id]['dbxrefs'][key_word]

            all_parent_list = []
            for i in go_id_list:
                if i in go_parent_dict:
                    all_parent_list.extend(go_parent_dict[i]['output'])

            all_parent_list = list(set(all_parent_list))

            seq_annotation_dict[clean_id]['GO_parent'] = all_parent_list

    # add Plantcyc
    tmp_info = tsv_file_parse(plantcyc_file)
    cyc_info_dict = {}
    for i in tmp_info:
        pw_id, pw_info, ra_id, ec, p_id, p_name, g_id, g_name = tmp_info[i]
        if g_id not in cyc_info_dict:
            cyc_info_dict[g_id] = []
        cyc_info_dict[g_id].append((pw_id, pw_info))

    cyc_info_dict2 = {}
    for i in tmp_info:
        pw_id, pw_info, ra_id, ec, p_id, p_name, g_id, g_name = tmp_info[i]
        if g_name not in cyc_info_dict2:
            cyc_info_dict2[g_name] = []
        cyc_info_dict2[g_name].append((pw_id, pw_info))

    key_word = 'BioCyc'
    num = 0
    num2 = 0
    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            cyc_id = seq_annotation_dict[clean_id]['dbxrefs'][key_word][0]
            cyc_id = cyc_id.split(":")[1]
            cyc_id = cyc_id.split("-")[0]
            num2 += 1
            if cyc_id in cyc_info_dict:
                cyc_list = cyc_info_dict[cyc_id]
                seq_annotation_dict[clean_id]['Plantcyc'] = cyc_list
            elif cyc_id in cyc_info_dict2:
                cyc_list = cyc_info_dict2[cyc_id]
                seq_annotation_dict[clean_id]['Plantcyc'] = cyc_list
            else:
                # print(cyc_id)
                num += 1

    # get output

    with open(work_dir+"/all_annotation.tsv", 'w') as f:
        head_list = ["ref_id", "Gene Name", "Alias", "Full Name", "key_words", "Computational Description", "PubMed_number",
                     "KEGG pathway(id)", "KEGG pathway", "KEGG module(id)", "KEGG module",  "KEGG KO(id)", "KEGG KO", "GO(id)", "GO_parent", "GO", "Plantcyc(id)", "Plantcyc",  "clean_id"]

        head_string = printer_list(head_list, sep='\t')
        f.write(head_string + "\n")

        data_dict = {}

        for clean_id in seq_annotation_dict:
            uniprot_id = seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id']
            ref_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']

            if uniprot_id in sprot_dict:
                uni_obj = sprot_dict[uniprot_id]
            elif uniprot_id in trembl_dict:
                uni_obj = trembl_dict[uniprot_id]
            else:
                gene_name, fullName, keywords, comment_function, pw_id, pw_info, md_id, md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string = [
                    ""]*15
                alias = []
                keywords = []
                PubMed_number = 0

            # from uniprot
            fullName = uni_obj.description

            if 'gene_name_primary' in uni_obj.annotations:
                gene_name = uni_obj.annotations['gene_name_primary']
            else:
                gene_name = ""

            if 'gene_name_synonym' in uni_obj.annotations:
                alias = uni_obj.annotations['gene_name_synonym']
            else:
                alias = []

            if 'keywords' in uni_obj.annotations:
                keywords = uni_obj.annotations['keywords']
            else:
                keywords = []

            if 'comment_function' in uni_obj.annotations:
                comment_function = uni_obj.annotations['comment_function']
                comment_function = printer_list(comment_function, '; ')
            else:
                comment_function = ""

            if 'references' in uni_obj.annotations:
                PubMed_list = uni_obj.annotations['references']
                PubMed_number = len(PubMed_list)
            else:
                PubMed_number = 0

            # from other db
            # kegg
            if 'KEGG' in seq_annotation_dict[clean_id]:
                pw_id, pw_info, md_id, md_info, ko_id, ko_info = seq_annotation_dict[
                    clean_id]['KEGG']
                tmp_tuple = []
                for i in pw_id, pw_info, md_id, md_info, ko_id, ko_info:
                    if i == 'None':
                        tmp_tuple.append("")
                    else:
                        i = i.replace(
                            ' - Arabidopsis thaliana (thale cress)', '')
                        tmp_tuple.append(i)

                pw_id, pw_info, md_id, md_info, ko_id, ko_info = tmp_tuple
            else:
                pw_id, pw_info, md_id, md_info, ko_id, ko_info = [""] * 6

            # go
            if 'GO' in seq_annotation_dict[clean_id]:
                go_info_dict = seq_annotation_dict[clean_id]['GO']

                go_list = list(go_info_dict.keys())
                go_id_string = printer_list(go_list, '; ')

                go_des = [go_info_dict[i]['name'] for i in go_list]
                go_des_string = printer_list(go_des, '; ')

                GO_parent_list = seq_annotation_dict[clean_id]['GO_parent']
                GO_parent_string = printer_list(GO_parent_list, '; ')

            else:
                go_id_string, go_des_string, GO_parent_string = [""] * 3

            # Plantcyc
            if 'Plantcyc' in seq_annotation_dict[clean_id]:
                cyc_list = seq_annotation_dict[clean_id]['Plantcyc']
                cyc_id_list = []
                cyc_des_list = []

                for i in cyc_list:
                    cyc_id_list.append(i[0])
                for i in cyc_list:
                    cyc_des_list.append(i[1])

                cyc_id_string = printer_list(cyc_id_list, '; ')
                cyc_des_string = printer_list(cyc_des_list, '; ')

            else:
                cyc_id_string, cyc_des_string = [""] * 2

            # 
            if 'gff_info' in seq_annotation_dict[clean_id]:
                gff_gene_name, gff_gene_alias, gff_full_name, gff_gene_note = seq_annotation_dict[clean_id]['gff_info']

                alias.extend(gff_gene_alias)
                alias = list(set(alias))

                keywords.extend([gff_gene_note])
                keywords = list(set(keywords))

                if gene_name == "" and gff_gene_name != "":
                    gene_name = gff_gene_name

                if fullName == "" and gff_full_name != "":
                    fullName = gff_full_name

            if '' in alias:
                alias.remove('')
            alias = printer_list(alias, '; ')

            if '' in keywords:
                keywords.remove('')
            keywords = printer_list(keywords, '; ')


            printer_string = printer_list([ref_id, gene_name, alias, fullName, keywords, comment_function, PubMed_number, pw_id, pw_info, md_id,
                                           md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string, clean_id], "\t")

            f.write(printer_string+'\n')

            data_dict[clean_id] = (ref_id, gene_name, alias, fullName, keywords, comment_function, PubMed_number, pw_id, pw_info, md_id,
                                   md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string, clean_id)

    OUT = open(work_dir + "/all_annotation.pyb", 'wb')
    pickle.dump(data_dict, OUT)
    OUT.close()


def Oryza_genome_function(work_dir, clean_data_fasta, clean_to_raw_id_map,blast_id_map, uniprot_sprot_plants_db, uniprot_trembl_plants_db, kegg_overview, plantcyc_file, obo_file):

    clean_seq_dict = read_fasta_by_faidx(clean_data_fasta)
    seq_annotation_dict = {i: {"dbxrefs": {}} for i in clean_seq_dict}

    tmp_info = tsv_file_parse(clean_to_raw_id_map)
    for i in tmp_info:
        clean_id, raw_id = tmp_info[i]

        if clean_id not in seq_annotation_dict:
            continue

        seq_annotation_dict[clean_id]['dbxrefs']['ref_id'] = raw_id

    tsv_info = tsv_file_parse(RAP_MSU_table_file)

    MSU_to_RAP_dict = {}
    for i in tsv_info:
        RAP_id, MSU_id = tsv_info[i]

        for j in MSU_id.split(","):
            if j == 'None':
                continue
            else:
                j = j.split(".")[0]
                MSU_to_RAP_dict[j] = RAP_id

    #  RAP
    for clean_id in seq_annotation_dict:
        MSU_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']
        if MSU_id in MSU_to_RAP_dict:
            RAP_id = MSU_to_RAP_dict[MSU_id]
            seq_annotation_dict[clean_id]['dbxrefs']['RAP_id'] = RAP_id

    # from RAP
    RAP_info_dict = tsv_file_dict_parse(RAP_tsv_file, key_col='Locus_ID')

    for clean_id in seq_annotation_dict:
        if not 'RAP_id' in seq_annotation_dict[clean_id]['dbxrefs']:
            continue

        RAP_id = seq_annotation_dict[clean_id]['dbxrefs']['RAP_id']

        if RAP_id not in RAP_info_dict:
            continue

        seq_annotation_dict[clean_id]['raw_tsv'] = {}

        RAP_info = RAP_info_dict[RAP_id]

        # gene_name
        gene_name = RAP_info['CGSNL Gene Name']

        # alias
        alias = RAP_info['RAP-DB Gene Symbol Synonym(s)'].split(", ")
        alias.extend(RAP_info['RAP-DB Gene Name Synonym(s)'].split(", "))
        alias.extend(RAP_info['CGSNL Gene Symbol'].split(", "))
        alias.extend(RAP_info['CGSNL Gene Name'].split(", "))
        alias.extend(RAP_info['Oryzabase Gene Symbol Synonym(s)'].split(", "))
        alias.extend(RAP_info['Oryzabase Gene Name Synonym(s)'].split(", "))

        alias = list(set(alias))

        # Full Name
        Full_Name = RAP_info['Description']

        # GO
        GO_list = re.findall('GO:.......', RAP_info['GO'])

        # PMID
        PMID = RAP_info['Literature PMID'].split(", ")

        seq_annotation_dict[clean_id]['raw_tsv'] = {
            'gene_name': gene_name,
            'alias': alias,
            'Full_Name': Full_Name,
            'GO_list': GO_list,
            'PMID': PMID,
        }

    # uniprot

    uniprot_map_file = work_dir+"/uniprot.map"

    if not os.path.exists(uniprot_map_file):
        RAP_or_MSU_id = []
        for clean_id in seq_annotation_dict:
            MSU_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']
            if MSU_id != 'None':
                RAP_or_MSU_id.append(MSU_id)
            if 'RAP_id' in seq_annotation_dict[clean_id]['dbxrefs']:
                RAP_id = seq_annotation_dict[clean_id]['dbxrefs']['RAP_id']
                if RAP_id != 'None':
                    RAP_or_MSU_id.append(RAP_id)

        osa_all_gene_list = set(RAP_or_MSU_id)

        with open(work_dir+"/uniprot.map", 'w') as f:
            num = 0

            for db_tmp in [uniprot_sprot_plants_db, uniprot_trembl_plants_db]:

                for id_tmp, obj in iterUniprotDB(db_tmp):
                    num += 1
                    print(num)

                    dbxref_dict = {}
                    for i in obj.dbxrefs:
                        db_name, db_record = i.split(":", 1)
                        if db_name not in dbxref_dict:
                            dbxref_dict[db_name] = []
                        dbxref_dict[db_name].append(db_record)

                    if 'gene_name_ordered locus' in obj.annotations:
                        ref_ids = obj.annotations['gene_name_ordered locus']
                        ref_id_get = set(ref_ids) & osa_all_gene_list
                        if len(ref_id_get) > 0:
                            for i in ref_id_get:
                                f.write("%s\t%s\n" % (i, id_tmp))

    tmp_info = tsv_file_parse(uniprot_map_file)
    ref_dict = {}
    for i in tmp_info:
        ref_id, uniprot_id = tmp_info[i]
        ref_dict[ref_id] = uniprot_id

    for clean_id in seq_annotation_dict:
        ref_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']

        if ref_id in ref_dict:
            seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] = ref_dict[ref_id]
        else:
            seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] = None

    # add blast results
    tmp_info = tsv_file_parse(blast_id_map)
    blast_dict = {}
    for i in tmp_info:
        clean_id, uniprot_id = tmp_info[i]
        blast_dict[clean_id] = uniprot_id

    for i in seq_annotation_dict:
        if seq_annotation_dict[i]['dbxrefs']['uniprot_id'] is None:
            if i in blast_dict:
                seq_annotation_dict[i]['dbxrefs']['uniprot_id'] = blast_dict[i]

    print("There are %d genes, %d have uniprot id, %d failed to find" % (len(seq_annotation_dict), len(
        [i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id']]), len([i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id'] is None])))


    uniq_id_list = [seq_annotation_dict[i]['dbxrefs']['uniprot_id']
                    for i in seq_annotation_dict if not seq_annotation_dict[i]['dbxrefs']['uniprot_id'] is None]

    sprot_dict = extract_swiss_info(uniq_id_list, uniprot_sprot_plants_db)
    trembl_dict = extract_swiss_info(uniq_id_list, uniprot_trembl_plants_db)

    for clean_id in seq_annotation_dict:
        uniprot_id = seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id']

        if uniprot_id:
            if uniprot_id in sprot_dict:
                uni_obj = sprot_dict[uniprot_id]
            elif uniprot_id in trembl_dict:
                uni_obj = trembl_dict[uniprot_id]
            else:
                raise ValueError("error 1")

            # # gene name
            # fullName = uni_obj.description
            # gene_name = uni_obj.annotations['gene_name_primary']
            # alias = uni_obj.annotations['gene_name_synonym']
            # keywords = uni_obj.annotations['keywords']
            # comment_function = uni_obj.annotations['comment_function']

            # db covert
            dbxref_dict = {}
            for i in uni_obj.dbxrefs:
                db_name, db_record = i.split(":", 1)
                if db_name not in dbxref_dict:
                    dbxref_dict[db_name] = []
                dbxref_dict[db_name].append(db_record)

            for i in dbxref_dict:
                seq_annotation_dict[clean_id]['dbxrefs'][i] = dbxref_dict[i]

    for key_word in ['uniprot_id', 'BioCyc', 'GO', 'KEGG', 'Pfam', 'PubMed', 'RefSeq']:
        all_gene = len(seq_annotation_dict)
        get_num = len([i for i in seq_annotation_dict if seq_annotation_dict[i]['dbxrefs']['uniprot_id']
                       and key_word in seq_annotation_dict[i]['dbxrefs'] and len(seq_annotation_dict[i]['dbxrefs'][key_word]) > 0])
        failed_num = all_gene - get_num
        print("There are %d genes, %d have %s, %d failed to find" %
              (all_gene, get_num, key_word, failed_num))

    # add kegg
    kegg_info_dict = tsv_file_parse(kegg_overview, key_col=1)

    key_word = 'KEGG'
    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            kegg_id = seq_annotation_dict[clean_id]['dbxrefs'][key_word][0]
            if kegg_id in kegg_info_dict:
                kegg_info = kegg_info_dict[kegg_id]
                kg_id, ncbi_id, pw_id, pw_info, md_id, md_info, ko_id, ko_info = kegg_info
                seq_annotation_dict[clean_id]['KEGG'] = (
                    pw_id, pw_info, md_id, md_info, ko_id, ko_info)

    # add GO
    ontology = Obo(obo_file)

    key_word = 'GO'
    all_go_list = []
    for clean_id in seq_annotation_dict:

        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            go_id_list = seq_annotation_dict[clean_id]['dbxrefs'][key_word]

            go_info_dict = {}
            for go_id in go_id_list:
                go_info = ontology.get(go_id)
                if go_info:
                    go_info_dict[go_info['id']] = go_info
                    all_go_list.append(go_id)

            seq_annotation_dict[clean_id]['GO'] = go_info_dict

    all_go_list = list(set(all_go_list))

    def get_all_parents(go_id):
        parent_list = [i[0] for i in ontology.find_parents(go_id, expand=True)]
        parent_list.append(go_id)
        return list(set(parent_list))

    go_parent_dict = multiprocess_running(
        get_all_parents, [(i,) for i in all_go_list], 56, args_id_list=all_go_list)

    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            go_id_list = seq_annotation_dict[clean_id]['dbxrefs'][key_word]

            all_parent_list = []
            for i in go_id_list:
                if i in go_parent_dict:
                    all_parent_list.extend(go_parent_dict[i]['output'])

            all_parent_list = list(set(all_parent_list))

            seq_annotation_dict[clean_id]['GO_parent'] = all_parent_list

    # add Plantcyc
    tmp_info = tsv_file_parse(plantcyc_file)
    cyc_info_dict = {}
    for i in tmp_info:
        pw_id, pw_info, ra_id, ec, p_id, p_name, g_id, g_name = tmp_info[i]
        if g_id not in cyc_info_dict:
            cyc_info_dict[g_id] = []
        cyc_info_dict[g_id].append((pw_id, pw_info))

    cyc_info_dict2 = {}
    for i in tmp_info:
        pw_id, pw_info, ra_id, ec, p_id, p_name, g_id, g_name = tmp_info[i]
        if g_name not in cyc_info_dict2:
            cyc_info_dict2[g_name] = []
        cyc_info_dict2[g_name].append((pw_id, pw_info))

    key_word = 'BioCyc'
    num = 0
    num2 = 0
    for clean_id in seq_annotation_dict:
        if seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id'] and key_word in seq_annotation_dict[clean_id]['dbxrefs'] and len(seq_annotation_dict[clean_id]['dbxrefs'][key_word]) > 0:
            cyc_id = seq_annotation_dict[clean_id]['dbxrefs'][key_word][0]
            cyc_id = cyc_id.split(":")[1]
            cyc_id = cyc_id.split("-")[0]
            num2 += 1
            if cyc_id in cyc_info_dict:
                cyc_list = cyc_info_dict[cyc_id]
                seq_annotation_dict[clean_id]['Plantcyc'] = cyc_list
            elif cyc_id in cyc_info_dict2:
                cyc_list = cyc_info_dict2[cyc_id]
                seq_annotation_dict[clean_id]['Plantcyc'] = cyc_list
            else:
                # print(cyc_id)
                num += 1

    # get output

    with open(work_dir+"/all_annotation.tsv", 'w') as f:
        head_list = ["ref_id", "Gene Name", "Alias", "Full Name", "key_words", "Computational Description", "PubMed_number",
                     "KEGG pathway(id)", "KEGG pathway", "KEGG module(id)", "KEGG module",  "KEGG KO(id)", "KEGG KO", "GO(id)", "GO_parent", "GO", "Plantcyc(id)", "Plantcyc",  "clean_id"]

        head_string = printer_list(head_list, sep='\t')
        f.write(head_string + "\n")

        data_dict = {}

        for clean_id in seq_annotation_dict:
            uniprot_id = seq_annotation_dict[clean_id]['dbxrefs']['uniprot_id']
            ref_id = seq_annotation_dict[clean_id]['dbxrefs']['ref_id']

            if uniprot_id in sprot_dict:
                uni_obj = sprot_dict[uniprot_id]
            elif uniprot_id in trembl_dict:
                uni_obj = trembl_dict[uniprot_id]
            else:
                gene_name, fullName, keywords, comment_function, PubMed_number, pw_id, pw_info, md_id, md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string = [
                    ""]*16
                alias = []

            # from uniprot
            fullName = uni_obj.description

            if 'gene_name_primary' in uni_obj.annotations:
                gene_name = uni_obj.annotations['gene_name_primary']
            else:
                gene_name = ""

            if 'gene_name_synonym' in uni_obj.annotations:
                alias = uni_obj.annotations['gene_name_synonym']
            else:
                alias = []

            if 'keywords' in uni_obj.annotations:
                keywords = uni_obj.annotations['keywords']
                keywords = printer_list(keywords, '; ')
            else:
                keywords = ""

            if 'comment_function' in uni_obj.annotations:
                comment_function = uni_obj.annotations['comment_function']
                comment_function = printer_list(comment_function, '; ')
            else:
                comment_function = ""

            if 'references' in uni_obj.annotations:
                PubMed_list = uni_obj.annotations['references']
                PubMed_number = len(PubMed_list)
            else:
                PubMed_number = ""

            # from other db
            # kegg
            if 'KEGG' in seq_annotation_dict[clean_id]:
                pw_id, pw_info, md_id, md_info, ko_id, ko_info = seq_annotation_dict[
                    clean_id]['KEGG']
                tmp_tuple = []
                for i in pw_id, pw_info, md_id, md_info, ko_id, ko_info:
                    if i == 'None':
                        tmp_tuple.append("")
                    else:
                        i = i.replace(
                            ' - Arabidopsis thaliana (thale cress)', '')
                        tmp_tuple.append(i)

                pw_id, pw_info, md_id, md_info, ko_id, ko_info = tmp_tuple
            else:
                pw_id, pw_info, md_id, md_info, ko_id, ko_info = [""] * 6

            # go
            if 'GO' in seq_annotation_dict[clean_id]:
                go_info_dict = seq_annotation_dict[clean_id]['GO']

                go_list = list(go_info_dict.keys())
                go_id_string = printer_list(go_list, '; ')

                go_des = [go_info_dict[i]['name'] for i in go_list]
                go_des_string = printer_list(go_des, '; ')

                GO_parent_list = seq_annotation_dict[clean_id]['GO_parent']
                GO_parent_string = printer_list(GO_parent_list, '; ')

            else:
                go_id_string, go_des_string, GO_parent_string = [""] * 3

            # Plantcyc
            if 'Plantcyc' in seq_annotation_dict[clean_id]:
                cyc_list = seq_annotation_dict[clean_id]['Plantcyc']
                cyc_id_list = []
                cyc_des_list = []

                for i in cyc_list:
                    cyc_id_list.append(i[0])
                for i in cyc_list:
                    cyc_des_list.append(i[1])

                cyc_id_string = printer_list(cyc_id_list, '; ')
                cyc_des_string = printer_list(cyc_des_list, '; ')

            else:
                cyc_id_string, cyc_des_string = [""] * 2

            if 'raw_tsv' in seq_annotation_dict[clean_id]:
                if 'alias' in seq_annotation_dict[clean_id]['raw_tsv']:
                    alias.extend(seq_annotation_dict[clean_id]['raw_tsv']['alias'])
                    alias = list(set(alias))

                if gene_name == "" and 'gene_name' in seq_annotation_dict[clean_id]['raw_tsv']:
                    gene_name = seq_annotation_dict[clean_id]['raw_tsv']['gene_name']

                if fullName == "" and 'Full_Name' in seq_annotation_dict[clean_id]['raw_tsv']:
                    fullName = seq_annotation_dict[clean_id]['raw_tsv']['Full_Name']

            if '' in alias:
                alias.remove('')
            alias = printer_list(alias, '; ')


            printer_string = printer_list([ref_id, gene_name, alias, fullName, keywords, comment_function, PubMed_number, pw_id, pw_info, md_id,
                                           md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string, clean_id], "\t")

            f.write(printer_string+'\n')

            data_dict[clean_id] = (ref_id, gene_name, alias, fullName, keywords, comment_function, PubMed_number, pw_id, pw_info, md_id,
                                   md_info, ko_id, ko_info, go_id_string, GO_parent_string, go_des_string, cyc_id_string, cyc_des_string, clean_id)

    OUT = open(work_dir + "/all_annotation.pyb", 'wb')
    pickle.dump(data_dict, OUT)
    OUT.close()


if __name__ == "__main__":
    # Ath
    work_dir = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function"
    clean_data_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/T3702N0.gene_model.protein.fasta'
    clean_interpro = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/T3702N0.gene_model.protein.interpro.tsv'
    clean_to_raw_id_map = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/id.map'


    araport_gff = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Arabidopsis_thaliana/function/Araport11_GFF3_genes_transposons.201606.gff'

    # uniprot
    uniprot_sprot_plants_db = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.db'
    uniprot_trembl_plants_db = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.db'

    # kegg
    kegg_overview = '/lustre/home/xuyuxing/Database/kegg/ath/ath.overview.tsv'

    # plantcyc
    plantcyc_file = '/lustre/home/xuyuxing/Database/plantcyc/aracyc_pathways.20180702'

    # go
    obo_file = "/lustre/home/xuyuxing/Database/GO/go.obo"

    Arabidopsis_genome_function(work_dir, clean_data_fasta, clean_to_raw_id_map,
                                uniprot_sprot_plants_db, uniprot_trembl_plants_db, kegg_overview, plantcyc_file, obo_file)

    # Osa

    work_dir = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function"
    clean_data_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/T4530N0.gene_model.protein.fasta'
    clean_interpro = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/T4530N0.gene_model.protein.interpro.tsv'
    clean_to_raw_id_map = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function/id.map'
    

    # RAP
    RAP_MSU_table_file = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function/RAP-MSU_2020-09-09.txt"
    RAP_tsv_file = "/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function/IRGSP-1.0_representative_annotation_2020-09-09.tsv"

    # uniprot
    uniprot_sprot_plants_db = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.db'
    uniprot_trembl_plants_db = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.db'
    blast_id_map = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Oryza_sativa/function/osa_vs_uniprot.idmap'

    # kegg
    kegg_overview = '/lustre/home/xuyuxing/Database/kegg/osa/osa.overview.tsv'

    # plantcyc
    plantcyc_file = '/lustre/home/xuyuxing/Database/plantcyc/oryzacyc_pathways.20180702'

    # go
    obo_file = "/lustre/home/xuyuxing/Database/GO/go.obo"

    Arabidopsis_genome_function(work_dir, clean_data_fasta, clean_to_raw_id_map, ref_db_name,
                                uniprot_sprot_plants_db, uniprot_trembl_plants_db, kegg_overview, plantcyc_file, obo_file)
