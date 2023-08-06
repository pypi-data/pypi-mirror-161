from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.api.common.genome.blast import outfmt6_read_big
import toolbiox.lib.common.sqlite_command as sc
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
import pickle
import re

close_group_bls = "/lustre/home/xuyuxing/Work/Gel/HGT/nt_genome_HGT/plant_bls/plant.bls"
distant_group_bls = "/lustre/home/xuyuxing/Work/Gel/HGT/nt_genome_HGT/fungi_bls/simple_split/fungi.bls"
genome_fasta = "/lustre/home/xuyuxing/Work/Gel/GenomeStat/T91201N0.genome.fasta"
tmp_dir = "/lustre/home/xuyuxing/Work/Gel/GenomeStat/HGT"
bin_length=100

def simple_nt_HGT_stat(genome_fasta, close_group_bls, distant_group_bls, bin_length=100, tmp_dir="/tmp"):
    """
    DOI: 10.1016/j.cub.2020.12.045
    from Figure 5C
    """
    def parse_function(blast_results):
        return {'record': (blast_results.qID, sc.pickle_dump_obj(blast_results))} 

    def extract_function(query_id_list, bls_db):
        return {i[0]:sc.pickle_load_obj(i[1]) for i in sc.sqlite_select(bls_db, 'record', key_name='id', value_tuple=query_id_list)}

    def get_similarity(bls_record, bin_length=None, use_identity=True):
        if use_identity:
            similarity = bls_record.hit[0].hsp[0].Hsp_identity / 100
            return similarity
        else:
            # similarity = min(1.0, bls_record.hit[0].hsp[0].Hsp_identity / 100 * bls_record.hit[0].hsp[0].Hsp_align_len / bin_length)
            similarity = min(1.0, bls_record.hit[0].hsp[0].Hsp_align_len / bin_length)
            return similarity

    # load blast into db
    distant_bls_db = tmp_dir + "/distant_bls.db"
    sc.build_database(outfmt6_read_big(distant_group_bls), parse_function, {'record':['id', 'codenstring']}, distant_bls_db)
    sc.build_index(distant_bls_db, 'record', 'id')

    close_bls_db = tmp_dir + "/close_bls.db"
    sc.build_database(outfmt6_read_big(close_group_bls), parse_function, {'record':['id', 'codenstring']}, close_bls_db)
    sc.build_index(close_bls_db, 'record', 'id')

    # bin HGT
    chr_dict = read_fasta_by_faidx(genome_fasta)

    key_list = []
    for chr_id in chr_dict:
        chr_length = chr_dict[chr_id].len()
        for i, s, e in split_sequence_to_bins(chr_length, bin_length, 1):
            key_str = "%s_%d-%d" % (chr_id, s, e)
            key_list.append(key_str)
    
    step = 10000
    sim_dict = {}
    for i in range(0, len(key_list), step):
        # print(i)
        sub_key_list = key_list[i:i+step]
        close_record = extract_function(sub_key_list, close_bls_db)
        distant_record = extract_function(sub_key_list, distant_bls_db)

        # get similarity
        for k in sub_key_list:
            if k in close_record:
                cr = close_record[k]
            else:
                cr = None

            if k in distant_record:
                dr = distant_record[k]
            else:
                dr = None

            if cr:
                crs = get_similarity(cr, bin_length=bin_length, use_identity=False)
                drs = 0.0
            elif dr:
                crs = 0.0
                drs = get_similarity(dr, bin_length=bin_length, use_identity=False)
            else:
                crs=0.0
                drs=0.0

            sim_dict[k] = (crs,drs,cr,dr)

    output_dict = {}
    for k in sim_dict:
        chr_id, s, e = re.findall(r'(\S+)_(\S+)-(\S+)', k)[0]
        if chr_id not in output_dict:
            output_dict[chr_id] = {}
        output_dict[chr_id][(int(s),int(e))] = sim_dict[k]

    return output_dict
