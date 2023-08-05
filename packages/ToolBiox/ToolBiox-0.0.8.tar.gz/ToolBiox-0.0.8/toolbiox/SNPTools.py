# coding:utf-8
from cyvcf2 import VCF
from pyfaidx import Fasta
from toolbiox.lib.common.genome.seq_base import fancy_name_get


def get_speci_info(seq_id):
    return seq_id.split("|")[0]


if __name__ == '__main__':
    import argparse

    ###### argument parse
    parser = argparse.ArgumentParser(
        prog='SNPTools',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for VCFcompare
    parser_a = subparsers.add_parser('VCFcompare',
                                     help='compare two vcf file')
    parser_a.add_argument("vcf_1", help="first vcf file", type=str)
    parser_a.add_argument("vcf_2", help="second vcf file", type=str)
    parser_a.add_argument("ref", help="ref genome fasta file", type=str)
    parser_a.add_argument("-t", "--vcf_file_type", help="what type of vcf file you give? (default:deepvarient)",
                          default="deepvarient", choices=['deepvarient', 'gatk'])

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    #### command detail

    if args_dict["subcommand_name"] == "VCFcompare":
        # pre
        """
        class abc(object):
            pass

        args = abc()
        args.vcf_1 = "/lustre/home/xuyuxing/Work/Other/Guojin/201905/analysis/deepvarient/CM.output.vcf"
        args.vcf_2 = "/lustre/home/xuyuxing/Work/Other/Guojin/201905/analysis/deepvarient/Mutant.output.vcf"
        args.ref = "/lustre/home/xuyuxing/Work/Other/Guojin/201905/analysis/database/Slycopersicum_514_SL3.0.fa"
        args.vcf_file_type = "deepvarient"
        """

        ref_dict = Fasta(args.ref)

        if args.vcf_file_type == "deepvarient":

            vcf1 = VCF(args.vcf_1)
            vcf2 = VCF(args.vcf_2)

            fancy_name_get("SL3.0ch00", 1, 1000000)

            for v in vcf1(fancy_name_get("SL3.0ch00", 1, 1000000)):
                #if v.INFO["AF"] > 0.1: continue
                print(str(v))
