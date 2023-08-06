if __name__ == '__main__':

    import argparse

    # command argument parse

    # argument parse
    parser = argparse.ArgumentParser(
        prog='GenomeAnnotation', description='tools help to get genome annotation more easy\n'
    )

    subparsers = parser.add_subparsers(
        title='subcommands', dest="subcommand_name")

    # argparse for ExtractGFF
    parser_a = subparsers.add_parser('ExtractGFF',
                                     help='extract genome feature record from gff file')

    parser_a.add_argument("genome_feature_id_list",
                          help="genome_feature_id_list", type=str)
    parser_a.add_argument("raw_gff_file", help="raw gff file", type=str)
    parser_a.add_argument(
        "output_gff_file", help="path of output gff", type=str)

    # argparse for GFFRename
    parser_a = subparsers.add_parser('GFFRename',
                                     help='Rename a gff file')

    parser_a.add_argument(
        "input_gff_file", help="gff file for input", type=str)
    parser_a.add_argument(
        "output_gff_file", help="gff file for output", type=str)
    parser_a.add_argument(
        "rename_prefix", help="gene name rename prefix", type=str)
    parser_a.add_argument("-c", "--rename_chr_id",
                          help="rename_chr_id", action='store_true')

    # argparse for SortGFF
    parser_a = subparsers.add_parser('SortGFF',
                                     help='sort a gff file by feature location')

    parser_a.add_argument(
        "input_gff_file", help="gff file for input", type=str)
    parser_a.add_argument(
        "output_gff_file", help="gff file for output", type=str)
    parser_a.add_argument("-t", "--sort_for_tabix",
                          help="sort gff file for tabix", action='store_true')

    # argparse for FeatureLen
    parser_a = subparsers.add_parser('FeatureLen',
                                     help='get model mRNA length from a gff file')

    parser_a.add_argument(
        "input_gff_file", help="gff file for input", type=str)

    # argparse for GffModel
    parser_a = subparsers.add_parser('GffModel',
                                     help='get gene model from NCBI gff',
                                     description='get gene model from NCBI gff by the longest transcript')

    parser_a.add_argument('ncbi_gff', type=str,
                          help='Path of NCBI genomic gff')
    parser_a.add_argument("-o", "--output_file", help="Output file name (default as *.gene.model)", default=None,
                          type=str)

    # argparse for NtPtMap
    parser_b = subparsers.add_parser('NtPtMap',
                                     help='find the gene which have pt and nt both',
                                     description='for mission which need use pt and nt both')

    parser_b.add_argument('Nt_file', type=str,
                          help='Path of Nt file with NCBI fasta format')
    parser_b.add_argument('Pt_file', type=str,
                          help='Path of Pt file with NCBI fasta format')
    parser_b.add_argument('gene_model', type=str,
                          help='Path of gene mode file from GffModel')
    parser_b.add_argument('tag', type=str, help='tag for output')

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    # command detail

    if args_dict["subcommand_name"] == "ExtractGFF":
        from toolbiox.src.xuyuxing.tools.gene_feature_tools import extract_gff_main
        extract_gff_main(args)

    elif args_dict["subcommand_name"] == "GFFRename":
        from toolbiox.src.xuyuxing.tools.gene_feature_tools import gff_rename_main
        gff_rename_main(args)

    elif args_dict["subcommand_name"] == "FeatureLen":
        from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, Gene

        gf_dict = read_gff_file(args.input_gff_file)

        for feature_tmp in gf_dict:
            for gf_id in gf_dict[feature_tmp]:
                gf = gf_dict[feature_tmp][gf_id]
                gene = Gene(from_gf=gf)
                gene.build_gene_seq()
                if 'exon' in gene.model_mRNA.sgf_len_dir:
                    print("%s\t%s" %
                          (gf.id, gene.model_mRNA.sgf_len_dir['exon']))
                else:
                    print("%s\t%s" %
                          (gf.id, gene.model_mRNA.sgf_len_dir['CDS']))

    elif args_dict["subcommand_name"] == "SortGFF":
        from toolbiox.src.xuyuxing.tools.gene_feature_tools import sort_gff_file
        sort_gff_file(args)

    elif args_dict["subcommand_name"] == "GffModel":
        from toolbiox.lib.common.genome.seq_base import read_fasta
        from BCBio import GFF
        import re

        in_file = args.ncbi_gff
        output_file = args.output_file

        cmd_string = "sed -i '/;part=/d' " + in_file
        cmd_run(cmd_string)

        in_handle = open(in_file)
        gene_dict = {}
        num = 0
        gene_model = {}
        for rec in GFF.parse(in_handle):
            for gene in rec.features:
                gene_dict[gene.id] = gene, rec.id
                if 'gene_biotype' in gene.qualifiers and gene.qualifiers['gene_biotype'][0] == 'protein_coding':
                    protein_dict = {}
                    for rna in gene.sub_features:
                        for cds in rna.sub_features:
                            if cds.type == "CDS":
                                protein_id = cds.qualifiers["protein_id"][0]
                                cds_length = abs(
                                    cds.location.start - cds.location.end)
                                if protein_id not in protein_dict:
                                    protein_dict[protein_id] = cds_length
                                else:
                                    protein_dict[protein_id] = protein_dict[protein_id] + cds_length
                    for cds in gene.sub_features:
                        if cds.type == "CDS":
                            protein_id = cds.qualifiers["protein_id"][0]
                            cds_length = abs(
                                cds.location.start - cds.location.end)
                            if protein_id not in protein_dict:
                                protein_dict[protein_id] = cds_length
                            else:
                                protein_dict[protein_id] = protein_dict[protein_id] + cds_length
                    model_protein = sorted(
                        protein_dict, key=lambda x: protein_dict[x], reverse=True)[0]
                    gene_model[gene.id] = model_protein
        in_handle.close()

        if output_file is not None:
            output_file = output_file
        else:
            output_file = in_file + ".gene.model"

        with open(output_file, 'w') as f:
            for i in gene_model:
                f.write(i + "\t" + gene_model[i] + "\n")

    elif args_dict["subcommand_name"] == "NtPtMap":
        from toolbiox.lib.common.genome.seq_base import read_fasta
        from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
        from BCBio import GFF
        import re

        def record_qulifiers_dict(qualifiers):
            output = {}
            for i in qualifiers:
                i = re.sub(r'\[', '', i)
                i = re.sub(r'\]', '', i)
                try:
                    key_tmp, value_tmp = i.split("=")
                    output[key_tmp] = value_tmp
                except:
                    pass
            return output

        def NCBI_nt_id_parse(nt_file):
            seqdict, seqname_list = read_fasta(nt_file)
            qualifiers_dict = {}
            seqdict_new = {}
            for i in seqdict:
                record = seqdict[i]
                qualifiers = re.findall(r'\[\S+\]', record.seqname)
                qualifiers = record_qulifiers_dict(qualifiers)
                if 'pseudo' in qualifiers and qualifiers['pseudo'] == 'true':
                    continue
                qualifiers['raw_id'] = i
                if qualifiers['protein_id'] in qualifiers_dict:
                    del qualifiers_dict[qualifiers['protein_id']]
                    del seqdict_new[qualifiers['protein_id']]
                else:
                    qualifiers_dict[qualifiers['protein_id']] = qualifiers
                    record.seqname = qualifiers['protein_id']
                    seqdict_new[qualifiers['protein_id']] = record
            return qualifiers_dict, seqdict_new

        nt_file = args.Nt_file
        pt_file = args.Pt_file
        gene_model_file = args.gene_model
        tag = args.tag

        pt_seqdict, pt_seqname_list = read_fasta(pt_file)
        qualifiers_dict, nt_seqdict = NCBI_nt_id_parse(nt_file)

        Maped_id = set(pt_seqdict.keys()) & set(qualifiers_dict.keys())
        gene_mode = tsv_file_parse(gene_model_file)
        gene_mode = [gene_mode[id][1] for id in gene_mode.keys()]

        output_id = set(Maped_id) & set(gene_mode)

        with open(tag + ".fasta", 'w') as f:
            for i in output_id:
                record = pt_seqdict[i]
                f.write(">%s|%s\n%s\n" % (tag, i, record.seqs))

        with open(tag + ".nt.fasta", 'w') as f:
            for i in output_id:
                record = nt_seqdict[i]
                f.write(">%s|%s\n%s\n" % (tag, i, record.seqs))

        print("%s\t%d\t%d" % (tag, len(gene_mode), len(output_id)))
