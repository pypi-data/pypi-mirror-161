import math
import os
import re
from toolbiox.lib.common.os import mkdir, cmd_run, multiprocess_running
from toolbiox.lib.common.genome.seq_base import read_fasta_big
from toolbiox.api.common.genome.blast import outfmt6_read_big
from toolbiox.lib.xuyuxing.base.base_function import merge_file

def w_index(evalue):
    if evalue == 0.0:
        return 100
    else:
        return min(100, round(-math.log(evalue, 10) / 2))

def hcluster_pipeline(pt_file_dir, output_dir, threads=56, option_string="-m 750 -w 0 -s 0.34 -O"):
    mkdir(output_dir, True)
    rename_seq_dir = output_dir + "/rename_seq"
    mkdir(rename_seq_dir, True)
    diamond_dir = output_dir + "/diamond"
    mkdir(diamond_dir, True)

    # rename step

    rename_dict = {}
    seq_file_dict = {}
    new_seq_species_dict = {}
    f_n = 0
    for f_name in os.listdir(pt_file_dir):
        p1 = r'(.*)\.fasta'
        p2 = r'(.*)\.fa'
        if re.match(p1, f_name) or re.match(p2, f_name):
            mbj = re.match(p1, f_name) or re.match(p2, f_name)
            prefix = mbj.groups()[0]
            input_f_name = pt_file_dir + "/" + f_name
            output_f_name = rename_seq_dir + "/" + prefix+".re.fa"
            bls_f_name = diamond_dir + "/" + prefix+".bls"
            seq_file_dict[prefix] = {'raw':input_f_name ,'rename':output_f_name ,'bls':bls_f_name}
            r_n = 0
            with open(output_f_name, 'w') as f:
                for r in read_fasta_big(input_f_name):
                    new_seq_id = str(f_n) + "_" + str(r_n)
                    rename_dict[new_seq_id] = r.seqname
                    new_seq_species_dict[new_seq_id] = prefix
                    f.write(">%s\n%s" % (new_seq_id, r.wrap()))
                    r_n += 1
            f_n += 1
            
    rename_map_file = rename_seq_dir + "/rename.map"
    with open(rename_map_file, 'w') as f:
        for i in rename_dict:
            f.write("%s\t%s\n" % (rename_dict[i], i))
    
    # diamond
    ## makedb

    # args_list = []
    # for sp_id in seq_file_dict:
    #     cmd_string = "diamond makedb --in %s --db %s" % (seq_file_dict[sp_id]['rename'], seq_file_dict[sp_id]['db'])
    #     args_list.append((cmd_string, None, 1, True, None))

    # multiprocess_running(cmd_run, args_list, threads, None, True)

    merged_fasta = diamond_dir + "/merged.fa"
    merge_file([seq_file_dict[i]['rename'] for i in seq_file_dict], merged_fasta)

    merged_db = diamond_dir + "/merged.dmnd"
    cmd_string = "diamond makedb --in %s --db %s" % (merged_fasta, merged_db)
    cmd_run(cmd_string, None, 1, True, None)

    ## run blastp
    args_list = []
    for sp_id in seq_file_dict:
        q_file = seq_file_dict[sp_id]['rename']
        bls_file = seq_file_dict[sp_id]['bls']
        cmd_string = "diamond blastp -d %s -q %s -o %s --more-sensitive -p 8 --quiet -e 1e-5" % (merged_db, q_file, bls_file)
        args_list.append((cmd_string, None, 1, True, None))
        # print(cmd_string)
    multiprocess_running(cmd_run, args_list, threads, None, True)

    # w-value
    hcluster_dir = output_dir + "/hcluster"
    mkdir(hcluster_dir, True)

    for sp_id in seq_file_dict:
        bls_file = seq_file_dict[sp_id]['bls']
        wvalue_file = hcluster_dir + "/" + sp_id+".wvalue"
        seq_file_dict[sp_id]['wvalue'] = wvalue_file

        with open(wvalue_file, 'w') as f:
            for r in outfmt6_read_big(bls_file):
                for hit in r.hit:
                    hsp = hit.hsp[0]
                    q_id = hsp.query.qID
                    s_id = hsp.subject.Hit_id
                    evalue = hsp.Hsp_evalue
                    wvalue = w_index(evalue)
                    f.write("%s\t%s\t%d\n" % (q_id, s_id, wvalue))

    # hcluster running
    merged_wvalue = hcluster_dir + "/merged.wvalue"
    merge_file([seq_file_dict[i]['wvalue'] for i in seq_file_dict], merged_wvalue)

    hcluster_outfile = hcluster_dir + "/hcluster.out"
    cmd_string = 'hcluster_sg %s -o %s %s' % (option_string, hcluster_outfile, merged_wvalue)
    cmd_run(cmd_string, None, 1, True, None)

    # convert hcluster out to tsv
    all_id_list = []
    with open(hcluster_outfile, 'r') as fi:
        for each_line in fi:
            each_line = each_line.strip()
            info = each_line.split('\t')
            id_list = info[6].split(",")
            id_list.remove("")
            all_id_list.append(id_list)

    all_id_list = sorted(all_id_list, key=lambda x:len(x), reverse=True)

    num = 0

    sp_id_list = list(seq_file_dict.keys())

    cluster_dict = {}
    for cluster_tmp in all_id_list:
        id_tmp = "hcluster%d" % num
        cluster_dict[id_tmp] = {i:[] for i in sp_id_list}

        for sp_id in sp_id_list:
            cluster_dict[id_tmp][sp_id] = [rename_dict[i] for i in cluster_tmp if new_seq_species_dict[i] == sp_id]

        num += 1
    
    # add uncluster seqid

    clustered_gene_dict = {i:[] for i in sp_id_list}
    for sp_id in sp_id_list:
        clustered_gene_dict[sp_id] = []
        for id_tmp in cluster_dict:
            clustered_gene_dict[sp_id] += cluster_dict[id_tmp][sp_id]
    
    unclustered_gene_dict = {}
    for sp_id in sp_id_list:
        all_gene_list = [rename_dict[i] for i in new_seq_species_dict if new_seq_species_dict[i] == sp_id]
        unclustered_gene_dict[sp_id] = list(set(all_gene_list) - set(clustered_gene_dict[sp_id]))
        
    for sp_id in sp_id_list:
        for gene_id in unclustered_gene_dict[sp_id]:
            id_tmp = "hcluster%d" % num
            cluster_dict[id_tmp] = {i:[] for i in sp_id_list}
            cluster_dict[id_tmp][sp_id] = [gene_id]

            num += 1

    # write tsv
    tsv_file = output_dir + '/hcluster.tsv'
    with open(tsv_file, 'w') as f:
        f.write("\t".join(['Orthogroup'] + sp_id_list) + "\n")
        for id_tmp in cluster_dict:
            printer_list = []
            for sp_id in sp_id_list:
                printer_list.append(", ".join(cluster_dict[id_tmp][sp_id]))
            printer_string = "\t".join([id_tmp] + printer_list)
            f.write(printer_string+"\n")
            
    # write GeneCount tsv
    tsv_file = output_dir + '/hcluster.GeneCount.tsv'
    with open(tsv_file, 'w') as f:
        f.write("\t".join(['Orthogroup'] + sp_id_list) + "\n")
        for id_tmp in cluster_dict:
            printer_list = []
            for sp_id in sp_id_list:
                printer_list.append(str(len(cluster_dict[id_tmp][sp_id])))
            printer_string = "\t".join([id_tmp] + printer_list)
            f.write(printer_string+"\n")
            




