import sys
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, write_gff_file, gene_rename, Genome, genome_rename, convert_dict_structure
from toolbiox.lib.common.fileIO import read_list_file
from toolbiox.lib.xuyuxing.base.common_command import merge_dict
from toolbiox.lib.common.os import cmd_run


def extract_gff_main(args):
    if not args.output_gff_file is None:
        sys.stdout = open(args.output_gff_file, 'w')

    gf_id_list = read_list_file(args.genome_feature_id_list)

    gf_dict = read_gff_file(args.raw_gff_file)

    gf_col_dict = {}
    for type_tmp in gf_dict:
        for gf_id in gf_dict[type_tmp]:
            gf_col_dict[gf_id] = gf_dict[type_tmp][gf_id]

    output_gf_list = [gf_col_dict[i] for i in gf_id_list]

    write_gff_file(output_gf_list, args.output_gff_file)


def gff_rename_main(args):
    """
    class abc():
        pass

    args = abc()
    args.input_gff_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/rename/Gel.rep.gff3'
    args.rename_prefix = "GelP"
    args.rename_chr_id = False
    args.output_gff_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/rename/Gel.Pseudo.gff3'
    """

    if not args.rename_chr_id:

        gff_dict = read_gff_file(args.input_gff_file)

        gf_list = []
        for gf_type in gff_dict:
            for gf_id in gff_dict[gf_type]:
                gf_list.append(gff_dict[gf_type][gf_id])

        chr_dict = {}
        for gf in gf_list:
            if gf.chr_id not in chr_dict:
                chr_dict[gf.chr_id] = []
            chr_dict[gf.chr_id].append(gf)

        num = 0
        total_num = len(gf_list)
        renamed_gf_list = []
        string_format = "%s%0"+str(len(str(total_num)))+"d"
        for contig_id in sorted(list(chr_dict.keys())):
            for raw_gf in chr_dict[contig_id]:
                gene_new_name = string_format % (args.rename_prefix, num)
                # print(gene_new_name)
                new_gf = gene_rename(raw_gf, gene_new_name, contig_id)
                renamed_gf_list.append(new_gf)
                num += 1

        write_gff_file(renamed_gf_list, args.output_gff_file)

    else:

        genome = Genome(gff_file=args.input_gff_file)
        genome.genome_feature_parse()
        genome.get_chromosome_from_gff()
        genome.build_gene_sequence()

        new_genome, chr_rename_dict, gene_rename_dict = genome_rename(
            genome, args.rename_prefix, keep_raw_contig_id=False)

        gf_list = []
        for gf_type in new_genome.feature_dict:
            gf_list.extend([new_genome.feature_dict[gf_type][i]
                            for i in new_genome.feature_dict[gf_type]])

        write_gff_file(gf_list, args.output_gff_file)


def sort_gff_file(args):
    if args.sort_for_tabix:
        cmd_string = "(grep ^\"#\" %s; grep -v ^\"#\" %s | sort -k1,1 -k4,4n) > %s" % (args.input_gff_file, args.input_gff_file, args.output_gff_file)
        cmd_run(cmd_string, silence=True)

    else:

        gff_dict = read_gff_file(args.input_gff_file)
        gene_dict, chr_dict = convert_dict_structure(gff_dict)

        write_gf_id_list = []
        for contig in chr_dict:
            gf_dict = merge_dict([chr_dict[contig]['+'], chr_dict[contig]['-']], False)
            sorted_gf_list = sorted(list(gf_dict.keys()),key=lambda x:gf_dict[x].start)
            write_gf_id_list.extend(sorted_gf_list)

        write_gf_list = [gene_dict[i] for i in write_gf_id_list]

        write_gff_file(write_gf_list, args.output_gff_file)
