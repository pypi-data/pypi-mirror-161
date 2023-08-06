from toolbiox.lib.common.os import mkdir, get_file_name, copy_file

"""
mpirun --allow-run-as-root -np 3 generax --families /data/families_plants.txt --species-tree /data/SpeciesTree_rooted.txt --rec-model UndatedDL --per-family-rates  --prefix test --max-spr-radius 3
"""


def prepare_OG_work_dir(OGs, sp_info_dict, top_work_dir, orthofinder_style=False):
    mkdir(top_work_dir, True)

    sp_list = list(sp_info_dict.keys())

    used_og_list = []
    for og_id in OGs.OG_dict:
        og = OGs.OG_dict[og_id]

        # filter not good OG, species number more than 3, single species not more than 50 gene, top two species not have more than 90% gene
        # species more than 3
        if len([i for i in og.species_stat if og.species_stat[i] > 0]) < 3:
            continue
        if max(og.species_stat.values()) > 50:
            continue
        if sum(sorted(og.species_stat.values())[-2:]) / sum(og.species_stat.values()) > 0.9:
            continue
        if sum(og.species_stat.values()) <= 3:
            continue

        # copy file
        og_dir = top_work_dir + "/" + og_id
        mkdir(og_dir, True)

        copy_file(og.tree_file, og_dir)
        copy_file(og.msa_file, og_dir)

        og.tree_file = og_dir + "/" + get_file_name(og.tree_file)
        og.msa_file = og_dir + "/" + get_file_name(og.msa_file)

        # map file
        map_file = og_dir + "/" + og_id + ".map"
        with open(map_file, 'w') as f:
            for gene in og.gene_list:
                if orthofinder_style:
                    f.write("%s_%s\t%s\n" %
                            (gene.species, gene.id, gene.species))
                else:
                    f.write("%s\t%s\n" % (gene.id, gene.species))

        og.map_file = map_file

        used_og_list.append(og_id)

    with open(top_work_dir+"/families.txt", 'w') as f:
        f.write("[FAMILIES]\n")
        for og_id in used_og_list:
            og = OGs.OG_dict[og_id]
            print_string = """- %s
starting_gene_tree = %s
alignment = %s
mapping = %s
subst_model = LG+G            
""" % (og_id, og.tree_file, og.msa_file, og.map_file)
            f.write(print_string)


if __name__ == '__main__':

    OG_tsv_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun01/Orthogroups/Orthogroups.tsv"
    species_tree_file = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun01/Species_Tree/SpeciesTree_rooted.txt"
    ref_xlsx = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss2/S44_version3/Gel_ref.xlsx'
    gene_tree_dir = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun01/Gene_Trees"
    msa_dir = "/lustre/home/xuyuxing/Work/Gel/orcWGD/orthofinder/pt_file/OrthoFinder/Results_Jun01/MultipleSequenceAlignments"
    top_work_dir = "/lustre/home/xuyuxing/Work/Gel/orcWGD/generax/top_data"

    from toolbiox.lib.common.evolution.orthotools2 import OrthoGroups, read_species_info
    from Bio import Phylo

    # species tree
    species_tree = Phylo.read(species_tree_file, 'newick')
    sp_list = [i.name for i in species_tree.get_terminals()]

    # orthogroups
    OGs = OrthoGroups(OG_tsv_file=OG_tsv_file, species_list=sp_list)

    # read a standard species info file: sp_id, taxon_id, species_name, genome_file, gff_file, pt_file, cDNA_file, cds_file
    sp_info_dict = read_species_info(ref_xlsx)
    sp_info_dict = {i: sp_info_dict[i] for i in sp_info_dict if i in sp_list}

    # get tree and msa
    for i in OGs.OG_dict:
        OGs.OG_dict[i].tree_file = "%s/%s_tree.txt" % (gene_tree_dir, i)
        OGs.OG_dict[i].msa_file = "%s/%s.fa" % (msa_dir, i)

    # prepare_OG_work_dir
    prepare_OG_work_dir(OGs, sp_info_dict, top_work_dir, True)
