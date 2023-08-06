"""
quick plot for mining data
    Yuxing Xu
    2020.04.19
"""
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

__author__ = 'Yuxing Xu'

if __name__ == '__main__':
    import argparse

    ###### argument parse
    parser = argparse.ArgumentParser(
        prog='QuickPlot',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for Histogram
    parser_a = subparsers.add_parser('Histogram',
                                     help='get Histogram plot for a number list', description='')
    parser_a.add_argument("input_file", help="a file have a list of number (each line have one number)", type=str)
    parser_a.add_argument("-o", "--output_file", help="Output file name (default as hist_plot.pdf)",
                          default='hist_plot.pdf', type=str)

    # argparse for VennPlot
    parser_a = subparsers.add_parser('VennPlot',
                                     help='get venn plot for list of file', description='')
    parser_a.add_argument("input_file", nargs='*', help="a file have a list of object (each line have one object)",
                          type=str)
    parser_a.add_argument("-o", "--output_prefix", help="Output file name (default as venn)", default='venn', type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # --------------------------------------------
    #### command detail

    if args_dict["subcommand_name"] == "Histogram":
        from toolbiox.api.xuyuxing.plot.histogram import histogram_style1
        from toolbiox.lib.common.fileIO import read_list_file

        """
        class abc():
            pass
        
        args=abc()
        
        args.input_file = "/lustre/home/xuyuxing/Work/Other/qi/full_trans/X101SC19111988-Z01_PacbioRawdata_20191231/TZC_MIX/All/list1"
        """

        number_list = read_list_file(args.input_file)
        number_list = [float(i) for i in number_list]
        histogram_style1(number_list, args.output_file)

    elif args_dict["subcommand_name"] == "VennPlot":

        import toolbiox.api.xuyuxing.plot.VennDiagram as venn
        from toolbiox.lib.common.fileIO import read_list_file
        from collections import OrderedDict
        from toolbiox.lib.common.util import printer_list

        """
        class abc():
            pass

        args=abc()

        args.input_file = ["/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/maker_1M/busco/eudicots_miss_test/est.miss","/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/maker_1M/busco/eudicots_miss_test/aa.miss"]
        args.output_prefix = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/maker_1M/busco/eudicots_miss_test/venn"
        """

        venn_len = len(args.input_file)
        if venn_len < 2:
            raise ValueError("At least two list")
        else:
            data_dict = OrderedDict()
            tag_list = []
            for i in args.input_file:
                tag = i.split("/")[-1]
                tag_list.append(tag)
                list_tmp = read_list_file(i)
                data_dict[tag] = list_tmp

            labels, set_collections = venn.get_labels([data_dict[i] for i in tag_list], fill=['number'],
                                                      return_set_collections=True)

            text_report = args.output_prefix + ".txt"
            with open(text_report, 'w') as f:
                for code_tag in sorted(list(set_collections.keys()), key=lambda x: int(x), reverse=True):
                    decode_tag_list = []
                    for i in range(len(code_tag)):
                        if int(code_tag[i]):
                            decode_tag_list.append(tag_list[i])
                    # print(decode_tag_list)

                    f.write(printer_list(decode_tag_list, head="> ") + "\n")
                    f.write(printer_list(list(set_collections[code_tag]), wrap_num=20) + "\n")


            if venn_len == 2:
                venn_function = venn.venn2
            elif venn_len == 3:
                venn_function = venn.venn3
            elif venn_len == 4:
                venn_function = venn.venn4
            elif venn_len == 5:
                venn_function = venn.venn5
            elif venn_len == 6:
                venn_function = venn.venn6
            else:
                venn_function = None
                print("too many group, just do txt analysis")

            if venn_function:
                fig, ax = venn_function(labels, names=tag_list)
                fig.savefig(args.output_prefix + ".pdf", dpi=1000)
