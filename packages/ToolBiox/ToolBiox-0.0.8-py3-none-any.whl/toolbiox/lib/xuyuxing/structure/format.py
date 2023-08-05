from Bio import PDB as pdb
from pybel import readfile, Outputfile


def merge_protein_and_ligand(protein_pdb, ligand_pdb, merge_pdb):
    """
    protein_pdb="/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/vina/FKN_apo.pdb"
    ligand_pdb="/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/vina/FKN_apo_vs_n3_ligand_1.pdb"
    merge_pdb="/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/vina/FKN_with_n3.pdb"
    """

    parser = pdb.PDBParser()
    protein_s = parser.get_structure('FKN', protein_pdb)
    protein_l = parser.get_structure('n3', ligand_pdb)


def pybel_file_covert(input_file, input_type, output_file, output_type):
    """
    check informats and outformats
    """
    input = readfile(input_type, input_file)
    output = Outputfile(output_type, output_file)
    for i in input:
        output.write(i)
    output.close()

if __name__ == '__main__':
    pdbqt_file = '/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/fkn_redo/vina/FKN_apo_vs_n3_ligand_1.pdbqt'
    pdb_file = '/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/fkn_redo/vina/FKN_apo_vs_n3_ligand_1.pdb'

    pybel_file_covert(pdbqt_file, 'pdbqt', pdb_file, 'pdb')