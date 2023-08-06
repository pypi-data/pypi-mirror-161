from Bio import SeqIO
import gzip
from toolbiox.lib.common.sqlite_command import pickle_dump_obj, build_database, build_index, sqlite_select, pickle_load_obj
import sqlite3
from toolbiox.api.xuyuxing.file_parser.xml_parser import getelements
from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_record_dict_db

def store_uniprot_swiss_into_sqlite(xml_file, sql3_db_file, gzip_flag=False):

    table_columns_dict = {'record': ['id', 'codenstring']}

    if gzip_flag:
        handle = gzip.open(xml_file, "rt")
    else:
        handle = xml_file

    data_generator = SeqIO.parse(handle, "uniprot-xml")

    def parse_function(seqio_obj):
        return {'record': (seqio_obj.id, pickle_dump_obj(seqio_obj))}

    build_database(data_generator, parse_function,
                   table_columns_dict, sql3_db_file)

    build_index(sql3_db_file, 'record', 'id')

    if gzip_flag:
        handle.close()

    return sql3_db_file


def extract_swiss_info(swiss_id_list, sql3_db_file):
    data_get = sqlite_select(sql3_db_file, 'record', [
                             'id', 'codenstring'], key_name='id', value_tuple=tuple(swiss_id_list))
    output_dict = {}
    for id_tmp, codenstring in data_get:
        obj = pickle_load_obj(codenstring)
        output_dict[id_tmp] = obj
    return output_dict


def iterUniprotDB(db_file):
    conn = sqlite3.connect(db_file)
    for id_tmp, codenstring in conn.execute('SELECT * FROM record'):
        obj = pickle_load_obj(codenstring)
        yield (id_tmp, obj)
    conn.close()



def filter_by_taxon(input_dict, target_taxon_id, taxon_db_file):
    # input_dict = {id: [id, seq, taxon_list]}

    all_taxon_id_list = []
    for i in input_dict:
        taxon_list = input_dict[i][2]
        all_taxon_id_list.extend(taxon_list)

    all_taxon_id_list = list(set(all_taxon_id_list))

    tax_dict = read_tax_record_dict_db(taxon_db_file, tax_id_list=all_taxon_id_list)

    output_dict = {}
    for i in input_dict:
        save_flag = False
        for j in input_dict[i][2]:
            if j in tax_dict:
                t = tax_dict[j]
                t_ancestor = set([i[0] for i in t.get_lineage])
                if target_taxon_id in t_ancestor:
                    save_flag = True

        if save_flag:
            output_dict[i] = input_dict[i]

    return output_dict

def get_plant_uniprot90(uniprot90_xml,taxon_db_file,output_file):
    # 3398 Magnoliopsida angiosperms flowering plants
    plant = '3398'

    with open(output_file, 'w') as f:
        tmp_store_dict = {}
        input_handle = gzip.open(uniprot90_xml, 'r')
        num = 0
        for entry in getelements(input_handle,'{http://uniprot.org/uniref}entry'):
            num += 1
            

            entry_id = entry.attrib['id']

            representativeMember_list = entry.findall('{http://uniprot.org/uniref}representativeMember')
            rep_member = representativeMember_list[0]
            rep_seq = rep_member.find('{http://uniprot.org/uniref}sequence').text

            dbReference = rep_member.find('{http://uniprot.org/uniref}dbReference')

            taxon_id_list = []
            for property_tmp in dbReference:
                if property_tmp.attrib['type'] == "NCBI taxonomy":
                    taxon_id = property_tmp.attrib['value']
                    taxon_id_list.append(taxon_id)

            member_list = entry.findall('{http://uniprot.org/uniref}member')

            for member in member_list:

                dbReference = member.find('{http://uniprot.org/uniref}dbReference')

                for property_tmp in dbReference:
                    if property_tmp.attrib['type'] == "NCBI taxonomy":
                        taxon_id = property_tmp.attrib['value']
                        taxon_id_list.append(taxon_id)

            taxon_id_list = list(set(taxon_id_list))

            tmp_store_dict[entry_id] = [entry_id, rep_seq, taxon_id_list]

            if len(tmp_store_dict) > 50000:
                print(num)
                output_dict = filter_by_taxon(tmp_store_dict, plant, taxon_db_file)
                tmp_store_dict = {}

                for r_id in output_dict:
                    f.write(">%s\n%s\n" % (r_id, output_dict[r_id][1]))

        output_dict = filter_by_taxon(tmp_store_dict, plant, taxon_db_file)

        for r_id in output_dict:
            f.write(">%s\n%s\n" % (r_id, output_dict[r_id][1]))    

                

                

if __name__ == "__main__":

    # # store xml into sqlite

    # xml_file = "/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.xml.gz"
    # db_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.db'
    # store_uniprot_swiss_into_sqlite(xml_file, db_file, True)

    # xml_file = "/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.xml.gz"
    # db_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.db'
    # store_uniprot_swiss_into_sqlite(xml_file, db_file, True)


    # # iter database
    # db_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.db'
    # db_fasta_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_sprot_plants.faa'

    # with open(db_fasta_file, 'w') as f:
    #     for id_tmp, obj in iterUniprotDB(db_file):
    #         f.write(">%s\n%s\n" % (id_tmp, str(obj.seq)))

    # db_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.db'
    # db_fasta_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/plant/uniprot_trembl_plants.faa'

    # with open(db_fasta_file, 'w') as f:
    #     for id_tmp, obj in iterUniprotDB(db_file):
    #         f.write(">%s\n%s\n" % (id_tmp, str(obj.seq)))

    # # extract record by accession

    # swiss_id_list = ['W8QP19', 'W8QNH8']

    # extract_swiss_info(swiss_id_list, db_file)

    # #
    taxon_db_file = '/lustre/home/xuyuxing/Database/NCBI/taxonomy/tax_xyx.db'
    uniprot90_xml = '/lustre/home/xuyuxing/Database/Uniprot/2020/uniref50.xml.gz'
    output_file = '/lustre/home/xuyuxing/Database/Uniprot/2020/uniref50.plant.faa'

    get_plant_uniprot90(uniprot90_xml,taxon_db_file,output_file)