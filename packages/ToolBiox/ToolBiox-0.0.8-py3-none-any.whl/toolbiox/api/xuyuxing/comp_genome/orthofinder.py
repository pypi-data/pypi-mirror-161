import os
import re
import gzip
import pickle
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.genome.seq_base import FastaRecord, read_fasta
from toolbiox.api.common.genome.blast import blast_to_sqlite
from Bio.Phylo.BaseTree import Tree
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
from toolbiox.lib.common.math.set import merge_same_element_set
from collections import OrderedDict
from toolbiox.lib.common.genome.genome_feature2 import Gene, GeneSet
from toolbiox.lib.common.os import multiprocess_running


def mclmatrix_parser(file_name):
    with open(file_name, 'r') as f:
        mclmatrix = ""
        matrix_flag = 0
        for each_line in f:
            # each_line = each_line.strip()
            if re.match('^begin$', each_line):
                matrix_flag = 1
                continue
            if matrix_flag == 1:
                mclmatrix = mclmatrix + each_line

        group_string_list = mclmatrix.split('$')
        group_dir = OrderedDict()
        for i in group_string_list:
            j = i.split()
            if j[0] == ')':
                continue
            group_dir[j[0]] = j[1:]
    return group_dir


def OG_tsv_file_parse(file_name):
    file_info = tsv_file_dict_parse(file_name)
    
    OG_dict = OrderedDict()
    for i in file_info:
        OG_id = file_info[i]['Orthogroup']
        OG_dict[OG_id] = {}
        for j in file_info[i]:
            if j == 'Orthogroup':
                continue
            if file_info[i][j]:
                OG_dict[OG_id][j] = file_info[i][j].split(", ")
            else:
                OG_dict[OG_id][j] = ""
    
    return OG_dict


def write_OG_tsv_file(OG_dict, output_file, species_list=None):
    if not species_list:
        species_list = list(OG_dict[list(OG_dict.keys())[0]].keys())

    with open(output_file, 'w') as f:
        f.write(printer_list(species_list,head='Orthogroup\t')+"\n")
    
        for OG_id in OG_dict:
            string_list = []
            for sp_id in species_list:
                string_list.append(printer_list(OG_dict[OG_id][sp_id],sep=', '))
            output_string = printer_list(string_list,head=OG_id+"\t")
            f.write(output_string+"\n")

    return output_file


def get_species_id_from_gene_id(gene_id):
    return gene_id.split('_')[0]


def orthofinder_dir_tree_parse():
    pass

class OrthoFinderResults(object):
    def __init__(self, orthofinder_work_dir):
        # input
        self.dir = orthofinder_work_dir

    def pase_file_and_dir(self, modify_dict={}):
        """
        in modify_dict you can change
        """
        # get cwd and relpath of dir
        self.reldir = os.path.relpath(self.dir)
        self.cwd = os.getcwd()

        # get important dir and file in orthofinder output
        self.orthogroup_work_dir = self.reldir + "/WorkingDirectory"
        self.species_ID_file = self.orthogroup_work_dir + "/SpeciesIDs.txt"
        self.sequence_ID_file = self.orthogroup_work_dir + "/SequenceIDs.txt"

        for file_and_dir_tmp in os.listdir(self.reldir):
            if re.match('Orthologues_(.*)', file_and_dir_tmp):
                self.orthologues_results_dir = self.reldir + "/" + file_and_dir_tmp

        if not hasattr(self, 'orthologues_results_dir'):
            self.orthologues_results_dir = "Not found"

        self.orthologues_work_dir = self.orthologues_results_dir + "/WorkingDirectory"
        # self.orthologues_pair_dir = self.orthologues_results_dir + "/Orthologues"
        self.orthologues_pair_dir = self.reldir + "/Orthologues"
        self.orthogroup_tree_dir = self.orthologues_work_dir + "/Trees_ids"
        self.orthogroup_aln_dir = self.orthologues_work_dir + "/Alignments_ids"
        self.orthogroup_seq_dir = self.orthologues_work_dir + "/Sequences_ids"
        self.orthogroup_recon_tree_dir = self.orthologues_results_dir + "/Recon_Gene_Trees"

        for new_attr in modify_dict:
            if hasattr(self, new_attr):
                setattr(self, new_attr, modify_dict[new_attr])

    # speci and seq info
    def get_name_info(self, hash_table=False):
        self.species_info = {}
        with open(self.species_ID_file, 'r') as f:
            for each_line in f:
                each_line = each_line.strip()
                if len(re.findall("^(\d+)\:\s+(.*).fasta$", each_line)) > 0:
                    rename_id, speci_id = re.findall("^(\d+)\:\s+(.*).fasta$", each_line)[0]
                elif len(re.findall("^(\d+)\:\s+(.*).fa$", each_line)) > 0:
                    rename_id, speci_id = re.findall("^(\d+)\:\s+(.*).fa$", each_line)[0]
                self.species_info[rename_id] = {'id': speci_id}

        self.sequences_info = {}
        for speci_id in self.species_info:
            self.sequences_info[speci_id] = {}
            with open(self.sequence_ID_file, 'r') as f:
                for each_line in f:
                    each_line = each_line.strip()
                    rename_id, raw_id = re.findall("^(\S+)\:\s+(.*)$", each_line)[0]
                    raw_short_id = re.search('^(\S+)', raw_id).group(1)
                    speci_id_tmp = get_species_id_from_gene_id(rename_id)
                    gene_tmp = Gene(id=rename_id, species=speci_id_tmp)
                    gene_tmp.old_name = {
                        "raw_full_id": raw_id,
                        "raw_short_id": raw_short_id
                    }
                    self.sequences_info[speci_id][gene_tmp.id] = gene_tmp

        if hash_table:
            hash_table_file = self.orthogroup_work_dir + "/hash_table.pyb"
            if not os.path.exists(hash_table_file):
                self.raw_full_id_hash = {}
                self.raw_short_id_hash = {}
                self.new_id_hash = {}
                for species_id in self.sequences_info:
                    for rename_id in self.sequences_info[species_id]:
                        self.raw_full_id_hash[
                            self.sequences_info[species_id][rename_id].old_name['raw_full_id']] = rename_id
                        self.raw_short_id_hash[
                            self.sequences_info[species_id][rename_id].old_name['raw_short_id']] = rename_id
                        self.new_id_hash[rename_id] = self.sequences_info[species_id][rename_id].old_name['raw_short_id']
                OUT = open(hash_table_file, 'wb')
                pickle.dump((self.raw_full_id_hash, self.raw_short_id_hash, self.new_id_hash), OUT)
                OUT.close()
            else:
                TEMP = open(hash_table_file, 'rb')
                self.raw_full_id_hash, self.raw_short_id_hash, self.new_id_hash = pickle.load(TEMP)
                TEMP.close()

    def get_OrthoGroups(self):
        # orthogroup
        for file_and_dir_tmp in os.listdir(self.orthogroup_work_dir):
            if re.match('(clusters_OrthoFinder_.*_id_pairs.txt)', file_and_dir_tmp):
                self.orthogroup_file = self.orthogroup_work_dir + "/" + file_and_dir_tmp

        group_dir = mclmatrix_parser(self.orthogroup_file)
        self.orthogroup_dir = {}
        for i in group_dir:
            gene_set_name = "OG%07d" % int(i)
            gene_set_list = []
            for j in group_dir[i]:
                gene_set_list.append(self.sequences_info[get_species_id_from_gene_id(j)][j])
            gene_set_tmp = GeneSet(gene_set_name, gene_set_list)
            gene_set_tmp.tree_file = self.orthogroup_tree_dir + "/" + gene_set_name + '_tree_id.txt'
            gene_set_tmp.aln_file = self.orthogroup_aln_dir + "/" + gene_set_name + '.fa'
            gene_set_tmp.seq_file = self.orthogroup_seq_dir + "/" + gene_set_name + '.fa'

            self.orthogroup_dir[gene_set_name] = gene_set_tmp

    def get_OG_hash(self):
        self.OG_hash = {}
        for OG_id in self.orthogroup_dir:
            gene_list = self.orthogroup_dir[OG_id].gene_list
            for gene_tmp in gene_list:
                self.OG_hash[gene_tmp.id] = OG_id

    def read_aa_fasta(self):
        # find rename fasta file
        self.blast_results_file = {}
        for file_and_dir_tmp in os.listdir(self.orthogroup_work_dir):
            if re.match('Species(.*)\.fa', file_and_dir_tmp):
                speci_id = re.findall('Species(.*)\.fa', file_and_dir_tmp)[0]
                self.species_info[speci_id]['file_path'] = self.orthogroup_work_dir + "/" + file_and_dir_tmp

        for speci_id in self.species_info:
            speci_aa_file = self.species_info[speci_id]['file_path']
            fasta_dict = read_fasta(speci_aa_file)[0]
            for fasta_record_id in fasta_dict:
                fasta_record = fasta_dict[fasta_record_id]
                self.sequences_info[speci_id][fasta_record.seqname].model_aa_seq = fasta_record.seq

    # def add_aa_fasta(self, aa_fasta_dir):
    #     self.aa_fasta_dir = os.path.relpath(aa_fasta_dir)
    #     for speci_id in self.species_info:
    #         speci_old_id = self.species_info[speci_id]['id']
    #         for file_and_dir_tmp in os.listdir(self.aa_fasta_dir):
    #             if speci_old_id + ".fasta" == file_and_dir_tmp:
    #                 self.species_info[speci_id]['raw_file_path'] = self.aa_fasta_dir + "/" + file_and_dir_tmp
    #                 break

    def blast_to_sqlite(self, force_redo=False, threads=10):
        # find blast file
        self.blast_results_file = {}
        for file_and_dir_tmp in os.listdir(self.orthogroup_work_dir):
            if re.match('Blast(\d+)_(\d+)\.txt\.gz', file_and_dir_tmp):
                speci_1, speci_2 = re.findall('Blast(\d+)_(\d+)\.txt\.gz', file_and_dir_tmp)[0]
                self.blast_results_file[(speci_1, speci_2)] = {
                    'outfmt6': self.orthogroup_work_dir + "/" + file_and_dir_tmp
                }

        args_list = []
        for speci_pair in self.blast_results_file:
            blast_file = self.blast_results_file[speci_pair]['outfmt6']
            db_file = re.sub('\.txt\.gz', '', blast_file) + ".db"
            self.blast_results_file[speci_pair]['db'] = db_file
            if not force_redo and os.path.exists(db_file):
                continue
            args_list.append((db_file, blast_file, None, None, 6, None, None, None, False, True))

        if args_list != []:
            multiprocess_running(blast_to_sqlite, args_list, threads)

    def get_Orthologues(self):

        if not hasattr(self, 'raw_short_id_hash'):
            raise AttributeError("Running get_name with hash_table firstly")

        raw_name_list = [i['id'] for i in self.species_info.values()]

        # read all csv file to get orthologues, first get in a dir with many list
        orthogroup_sort_tmp_dir = {}
        for speci_raw_id_i in raw_name_list:
            tmp_dir = self.orthologues_pair_dir + "/Orthologues_" + speci_raw_id_i
            for speci_raw_id_j in raw_name_list:
                if speci_raw_id_i == speci_raw_id_j:
                    continue
                # tmp_file = "%s/%s__v__%s.tsv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)
                if os.path.exists("%s/%s__v__%s.tsv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)):
                    tmp_file = "%s/%s__v__%s.tsv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)
                elif os.path.exists("%s/%s__v__%s.csv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)):
                    tmp_file = "%s/%s__v__%s.csv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)
                else:
                    raise EnvironmentError("failed to found orthologues files")

                tmp_info = tsv_file_dict_parse(tmp_file)
                for id_tmp in tmp_info:
                    OG_id = tmp_info[id_tmp]['Orthogroup']
                    tmp_list = tmp_info[id_tmp][speci_raw_id_i].split(", ") + tmp_info[id_tmp][
                        speci_raw_id_j].split(", ")
                    tmp_list_new_id = [self.raw_short_id_hash[i] for i in tmp_list]
                    if OG_id not in orthogroup_sort_tmp_dir:
                        orthogroup_sort_tmp_dir[OG_id] = []
                    orthogroup_sort_tmp_dir[OG_id].append(tmp_list_new_id)

        # merge list by same iter in a orthogroup

        self.orthologues_dir = {}
        for OG_id in orthogroup_sort_tmp_dir:
            orthogroup_sort_tmp_dir[OG_id] = merge_same_element_set(orthogroup_sort_tmp_dir[OG_id])
            num = 0
            for orthologues_list in sorted(orthogroup_sort_tmp_dir[OG_id], key=lambda x: len(x), reverse=True):
                gene_set_name = OG_id + "_" + str(num)
                num = num + 1
                gene_set_list = []
                for j in orthologues_list:
                    gene_set_list.append(self.sequences_info[get_species_id_from_gene_id(j)][j])
                gene_set_tmp = GeneSet(gene_set_name, gene_set_list)
                self.orthologues_dir[gene_set_name] = gene_set_tmp

    def get_OL_hash(self):
        self.OL_hash = {}
        for OL_id in self.orthologues_dir:
            gene_list = self.orthologues_dir[OL_id].gene_list
            for gene_tmp in gene_list:
                self.OL_hash[gene_tmp.id] = OL_id


def get_orthologues(orthologues_dir, output_file):

    species_list = []

    for i in os.listdir(orthologues_dir):
        mobj = re.match(r'^Orthologues_(\S+)$', i)
        if mobj:
            speci = mobj.groups()[0]
            species_list.append(speci)

    orthogroup_sort_tmp_dir = {}
    seq_species_dict = {}
    for speci in species_list:
        tmp_dir = orthologues_dir + "/Orthologues_" + speci
        for speci_p in species_list:
            if speci == speci_p:
                continue
            # tmp_file = "%s/%s__v__%s.tsv" % (tmp_dir, speci_raw_id_i, speci_raw_id_j)
            if os.path.exists("%s/%s__v__%s.tsv" % (tmp_dir, speci, speci_p)):
                tmp_file = "%s/%s__v__%s.tsv" % (tmp_dir, speci, speci_p)
            elif os.path.exists("%s/%s__v__%s.csv" % (tmp_dir, speci, speci_p)):
                tmp_file = "%s/%s__v__%s.csv" % (tmp_dir, speci, speci_p)
            else:
                raise EnvironmentError("failed to found orthologues files")

            tmp_info = tsv_file_dict_parse(tmp_file)
            for id_tmp in tmp_info:
                OG_id = tmp_info[id_tmp]['Orthogroup']
                tmp_list = tmp_info[id_tmp][speci].split(", ") + tmp_info[id_tmp][
                    speci_p].split(", ")
                if OG_id not in orthogroup_sort_tmp_dir:
                    orthogroup_sort_tmp_dir[OG_id] = []
                orthogroup_sort_tmp_dir[OG_id].append(tmp_list)

                if not speci in seq_species_dict:
                    seq_species_dict[speci] = []
                if not speci_p in seq_species_dict:
                    seq_species_dict[speci_p] = []
                seq_species_dict[speci].extend(tmp_info[id_tmp][speci].split(", "))
                seq_species_dict[speci_p].extend(tmp_info[id_tmp][speci_p].split(", "))
    
    for i in seq_species_dict:
        seq_species_dict[i] = list(set(seq_species_dict[i]))

    seq_species_hash = {}
    for speci in seq_species_dict:
        for seq in seq_species_dict[speci]:
            seq_species_hash[seq] = speci
    

    # merge list by same iter in a orthogroup

    orthologues_dict = {}
    for OG_id in orthogroup_sort_tmp_dir:
        orthogroup_sort_tmp_dir[OG_id] = merge_same_element_set(orthogroup_sort_tmp_dir[OG_id])
        num = 0
        for orthologues_list in sorted(orthogroup_sort_tmp_dir[OG_id], key=lambda x: len(x), reverse=True):
            gene_set_name = OG_id + "_" + str(num)
            num = num + 1
            gene_set_list = []
            for j in orthologues_list:
                gene_set_list.append(j)
            gene_set_tmp = GeneSet(gene_set_name, gene_set_list)
            orthologues_dict[gene_set_name] = gene_set_tmp

    # output tsv file

    with open(output_file,'w') as f:
        header = ['Orthologues'] + species_list
        header_string = printer_list(header)
        f.write(header_string+"\n")

        for ol_id in orthologues_dict:
            output_list = [ol_id]
            gene_set = orthologues_dict[ol_id]
            for speci in species_list:
                gene_list = [i  for i in gene_set.gene_list if seq_species_hash[i] == speci]
                gene_string = printer_list(gene_list, sep=', ')
                output_list.append(gene_string)
            f.write(printer_list(output_list)+"\n")


def tsv_to_gene_pair(orthologues_tsv, species1, species2=None, output_file=None, huge_gene_family_filter=None):
    tmp_info = tsv_file_dict_parse(orthologues_tsv)

    with open(output_file, 'w') as f:
        for ol_id in tmp_info:
            if species2:
                if tmp_info[ol_id][species1] and tmp_info[ol_id][species2]:

                    speices_1_gene = tmp_info[ol_id][species1].split(", ")
                    speices_2_gene = tmp_info[ol_id][species2].split(", ")

                    if len(speices_1_gene) == 0 or len(speices_2_gene) == 0:
                        continue

                    for i in speices_1_gene:
                        for j in speices_2_gene:
                            f.write("%s\t%s\n" % (i, j))
            else:
                if tmp_info[ol_id][species1]:
                    speices_1_gene = tmp_info[ol_id][species1].split(", ")
            
                    if len(speices_1_gene) == 0:
                        continue

                    if huge_gene_family_filter and len(speices_1_gene) > huge_gene_family_filter:
                        continue

                    for i in speices_1_gene:
                        for j in speices_1_gene:
                            if i == j:
                                continue

                            f.write("%s\t%s\n" % (i, j))



if __name__ == '__main__':
    # parse orthofinder dir
    ortho_obj = OrthoFinderResults('/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10')

    # get file and dir info
    ortho_obj.pase_file_and_dir(modify_dict={})

    # If you need to specify parameters you can use modify
    ortho_obj.pase_file_and_dir(modify_dict={'orthogroup_tree_dir': '/other/path'})

    # get speci and seq name info
    ortho_obj.get_name_info(hash_table=False)

    # get OrthoGroups info
    ortho_obj.get_OrthoGroups()

    # get orthologues
    ortho_obj.get_name_info(hash_table=True)
    ortho_obj.get_Orthologues()

    # change blast results to sqlite, can be dry_run just get exist db file path
    ortho_obj.blast_to_sqlite(force_redo=True)

    # # get raw seq id and changed seq id map
    # ortho_obj.get_RenameMap()

    # get orthogroups info from orthofinder dir
    ortho_obj.get_OrthoGroups()

    # get Orthologues info from orthofinder dir
    ortho_obj.get_Orthologues()

    # not by class

    # get Orthologues info from orthofinder dir
    orthologues_dir = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Aof/orthofinder2/OrthoFinder/Results_Nov21/Orthologues'
    output_file = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Aof/orthofinder2/OrthoFinder/Results_Nov21/Orthologues/Orthologues.tsv'
    get_orthologues(orthologues_dir, output_file)

    # get Orthologues pair between two species
    orthologues_tsv = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/orthofinder2/OrthoFinder/Results_Nov21/Orthologues/Orthologues.tsv'
    species1 = 'Aof.merge'
    species2 = 'Gel.merge'
    output_file = '/lustre/home/xuyuxing/Work/Gel/mcscanx/Gel_vs_Other/Gel_vs_Aof/Aof_vs_Gel.OL.pair'
    tsv_to_gene_pair(orthologues_tsv, species1, species2, output_file)



