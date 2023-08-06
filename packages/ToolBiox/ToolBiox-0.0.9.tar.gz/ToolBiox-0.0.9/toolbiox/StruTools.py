from toolbiox.lib.xuyuxing.structure.dcd_file import get_a_frame_from_dcd_to_pdb, atom_distance, get_RMSD, get_RE_RMSD
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
from toolbiox.lib.common.util import printer_list

if __name__ == '__main__':
    import argparse

    ###### argument parse
    parser = argparse.ArgumentParser(
        prog='StruTools',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for Dcd2pdb
    parser_a = subparsers.add_parser('Dcd2pdb',
                                     help='get some or all frame coord from dcd file to pdb file', description='')
    parser_a.add_argument("dcd_file", help="Path for dcd file", type=str)
    parser_a.add_argument("pdb_file", help="Path for raw pdb file", type=str)
    parser_a.add_argument("-f", "--file_of_frame_index", help="a list file include wanted frame indexes)", default=None,
                          type=str)
    parser_a.add_argument("-i", "--frame_index", help="frame index split by ,)", default=None,
                          type=str)
    parser_a.add_argument("-o", "--output_prefix", help="Output pdb file name index", default="output_", type=str)
    parser_a.add_argument("-s", "--atom_select",
                          help="atom select string, read http://prody.csb.pitt.edu/manual/reference/atomic/select.html#module-prody.atomic.select",
                          default="not water", type=str)

    # argparse for AtomDist
    parser_a = subparsers.add_parser('AtomDist',
                                     help='get distance between two atoms from dcd file', description='')
    parser_a.add_argument("dcd_file", help="Path for dcd file", type=str)
    parser_a.add_argument("pdb_file", help="Path for raw pdb file", type=str)
    parser_a.add_argument("atom_pair_file", help="two column file)", type=str)
    parser_a.add_argument("-o", "--output_file", help="Output file", default="output.tsv", type=str)

    # argparse for getRMSD
    parser_a = subparsers.add_parser('getRMSD',
                                     help='get RMSD value for a DCD file', description='')
    parser_a.add_argument("dcd_file", help="Path for dcd file", type=str)
    parser_a.add_argument("pdb_file", help="Path for raw pdb file", type=str)
    parser_a.add_argument("-o", "--output_file", help="Output file", default="output.tsv", type=str)
    parser_a.add_argument("-s", "--atom_select",
                          help="atom select string, read http://prody.csb.pitt.edu/manual/reference/atomic/select.html#module-prody.atomic.select",
                          default="not water", type=str)
    # argparse for getRERMSD
    parser_a = subparsers.add_parser('getRERMSD',
                                     help='get RMSD value for a DCD file', description='')
    parser_a.add_argument("dcd_file", help="Path for dcd file", type=str)
    parser_a.add_argument("pdb_file", help="Path for raw pdb file", type=str)
    parser_a.add_argument("rmsd_file", help="Output file", type=str)
    parser_a.add_argument("rmsf_file", help="Output file", type=str)
    parser_a.add_argument("-s", "--atom_select",
                          help="atom select string, read http://prody.csb.pitt.edu/manual/reference/atomic/select.html#module-prody.atomic.select",
                          default="not water", type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # --------------------------------------------
    #### command detail

    if args_dict["subcommand_name"] == "Dcd2pdb":
        ID_file = args.file_of_frame_index
        ID_list = args.frame_index
        if ID_file:
            ID_list = tsv_file_parse(ID_file, key_col=1)
            ID_list = ID_list.keys()
            ID_list = [int(i) for i in ID_list]
        elif ID_list:
            ID_list = ID_list.split(",")
            ID_list = [int(i) for i in ID_list]
        else:
            ID_list = None

        get_a_frame_from_dcd_to_pdb(args.dcd_file, args.pdb_file, args.output_prefix, index_list=ID_list,
                                    atom_select=args.atom_select)

    elif args_dict["subcommand_name"] == "AtomDist":
        """
        class abc():
            pass
        args = abc()
        
        args.atom_pair_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/atom_pair.txt"
        args.dcd_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/20ns/minimized.dcd"
        args.pdb_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/20ns/solvate.pdb"
        args.output_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/20ns/atom.dis.tsv"
        """

        ID_list = tsv_file_parse(args.atom_pair_file)
        atom_pair_list = [(int(ID_list[i][0]), int(ID_list[i][1])) for i in ID_list]

        output_dir = atom_distance(args.dcd_file, args.pdb_file, atom_pair_list)

        with open(args.output_file, 'w') as f:
            f.write(printer_list(atom_pair_list) + "\n")
            for i in range(0, len(output_dir[atom_pair_list[0]])):
                data_list = [output_dir[j][i] for j in atom_pair_list]
                f.write(printer_list(data_list) + "\n")

    elif args_dict["subcommand_name"] == "getRMSD":
        """
        class abc():
            pass
        args = abc()

        args.dcd_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/minimized.dcd"
        args.output_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/RMSD.txt"
        args.pdb_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/solvate.pdb"
        """

        RMSD_list = get_RMSD(args.dcd_file, args.pdb_file, args.atom_select)

        with open(args.output_file, 'w') as f:
            for i in RMSD_list:
                f.write(str(i) + "\n")

    elif args_dict["subcommand_name"] == "getRERMSD":
        """
        class abc():
            pass
        args = abc()

        args.dcd_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/minimized.dcd"
        args.rmsd_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/RMSD.txt"
        args.rmsf_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/RMSD.txt"
        args.pdb_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190906/n3/20ns/solvate.pdb"
        """

        RMSD_list,RMSF_list = get_RE_RMSD(args.dcd_file, args.pdb_file, args.atom_select)

        with open(args.rmsd_file, 'w') as f:
            for i in RMSD_list:
                f.write(str(i) + "\n")

        with open(args.rmsf_file, 'w') as f:
            for i in RMSF_list:
                f.write(str(i) + "\n")

