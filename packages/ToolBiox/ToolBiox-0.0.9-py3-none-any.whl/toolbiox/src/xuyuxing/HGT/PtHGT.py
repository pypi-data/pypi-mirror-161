from toolbiox.api.common.genome.blast import outfmt6_read_big
from toolbiox.lib.xuyuxing.evolution.taxonomy import read_tax_record_dict_db
from collections import OrderedDict
from toolbiox.lib.common.os import multiprocess_running


def donorGenus(blast_query, donor_taxon_id, receptor_taxon_id, tax_db_file):
    """
    return (num of donor genus in top 10), (if top 1 genus is donor)
    """

    # get hit info
    hit_list = []
    all_taxon_id_list = []
    for i in blast_query.hit:
        hit_list.append((i.Hit_def, i.Hit_taxon_id[0], i.hsp[0].Hsp_bit_score))
        all_taxon_id_list.append(i.Hit_taxon_id[0])

    # get max score for each genus, exclude receptor subject
    tax_record_dict = read_tax_record_dict_db(tax_db_file, all_taxon_id_list)

    genus_score_dict = OrderedDict()
    hash_donor_genus_table = {}
    for accession, taxid, score in hit_list:
        if taxid == '' or taxid not in tax_record_dict:
            continue

        # get taxon record
        taxon_tmp = tax_record_dict[taxid]
        if hasattr(taxon_tmp, 'genus'):
            genus_id = taxon_tmp.genus
        else:
            genus_id = taxon_tmp.tax_id

        # if in donor?
        if_in_donor = taxon_tmp.is_child_of(donor_taxon_id)
        hash_donor_genus_table[genus_id] = if_in_donor

        # if in receptor, remove it
        if_in_receptor = taxon_tmp.is_child_of(receptor_taxon_id)
        if if_in_receptor:
            continue

        # keep genus max score
        if genus_id in genus_score_dict:
            continue
        else:
            genus_score_dict[genus_id] = score

    # get top 10 score genus
    top_10_genus = list(genus_score_dict.keys())[0:10]

    if len(top_10_genus) == 0:
        return (0, False)
    else:

        donor_genus_rank = []
        no_donor_genus_rank = []
        for i in top_10_genus:
            if hash_donor_genus_table[i]:
                donor_genus_rank.append(top_10_genus.index(i) + 1)
            else:
                no_donor_genus_rank.append(top_10_genus.index(i) + 1)

        # if top 1 is donor
        if hash_donor_genus_table[top_10_genus[0]]:
            return (len(donor_genus_rank), True)
        else:
            return (len(donor_genus_rank), False)


def QuickBlastHGT(taxon_outfmt6_file, donor_taxon_id, receptor_taxon_id, tax_db_file, num_threads=10, log_file=None):
    args_list = []
    args_id_list = []

    output_dict = {}

    num = 0
    for query_tmp in outfmt6_read_big(taxon_outfmt6_file,
                                      fieldname=["qseqid", "sseqid", "staxids", "pident", "length", "mismatch",
                                                 "gapopen", "qstart", "qend", "sstart", "send", "evalue",
                                                 "bitscore"]):
        num += 1
        args_list.append((query_tmp, donor_taxon_id,
                          receptor_taxon_id, tax_db_file))
        args_id_list.append(query_tmp.qDef)

        if len(args_list) >= 300:

            print(num)
            mp_out = multiprocess_running(
                donorGenus, args_list, num_threads, log_file=log_file, silence=True, args_id_list=args_id_list)
            for i in mp_out:
                output_dict[i] = mp_out[i]['output']

            args_list = []
            args_id_list = []

    mp_out = multiprocess_running(donorGenus, args_list, num_threads,
                                  log_file=log_file, silence=True, args_id_list=args_id_list)
    for i in mp_out:
        output_dict[i] = mp_out[i]['output']

    return output_dict


if __name__ == "__main__":

    class abc(object):
        pass

    args = abc()

    args.taxon_outfmt6_file = '/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/passed.diamond.taxon.bls'
    args.donor_taxon_id = '4751'
    args.receptor_taxon_id = '4747'
    args.tax_db_file = '/lustre/home/xuyuxing/Database/NCBI/taxonomy/tax_xyx.db'
    args.num_threads = 56
    args.output_file = '/lustre/home/xuyuxing/Work/Gel/HGT_WPGmapper/pseudo/HGT.txt'



    output_dict = QuickBlastHGT(args.taxon_outfmt6_file, args.donor_taxon_id, args.receptor_taxon_id, args.tax_db_file, args.num_threads)

    with open(args.output_file, 'w') as f:
        for i in output_dict:
            f.write("%s\t%d\t%s\n" % (i,output_dict[i][0],output_dict[i][1]))