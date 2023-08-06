import prody


def get_a_frame_from_dcd_to_pdb(dcd_file, pdb_file, output_pdb_prefix, index_list=None, atom_select="not water"):
    #    structure = prody.parsePDB(pdb_file).select('not water')
    structure = prody.parsePDB(pdb_file)
    ensemble = prody.parseDCD(dcd_file)
    ensemble.setAtoms(structure)
    ensemble.setCoords(structure)

    for frame in ensemble:
        if not index_list or frame.getIndex() in index_list:
            atoms = frame.getAtoms()
            coords = frame.getCoords()
            atoms.setCoords(coords)
            # prody.writePDB("%s.%d.pdb" % (output_pdb_prefix,num), atoms.select('not water'))
            prody.writePDB("%s.%d.pdb" % (output_pdb_prefix, frame.getIndex()), atoms.select(atom_select))


def atom_distance(dcd_file, pdb_file, atom_pair_list):
    structure = prody.parsePDB(pdb_file)

    ensemble = prody.parseDCD(dcd_file)
    ensemble.setAtoms(structure)
    ensemble.setCoords(structure)

    output_dir = {}
    for pair_tuple in atom_pair_list:
        output_dir[tuple(pair_tuple)] = []

    for frame in ensemble:
        atoms = frame.getAtoms()
        coords = frame.getCoords()
        # print(frame.getIndex(), prody.calcDistance(coords[2744], coords[5351]))
        for i in output_dir:
            output_dir[i].append(prody.calcDistance(coords[i[0] - 1], coords[i[1] - 1]))

    return output_dir


def get_RMSD(dcd_file, pdb_file, atom_select="not water"):
    structure = prody.parsePDB(pdb_file)
    target_atoms = structure.select(atom_select)

    ensemble = prody.parseDCD(dcd_file)
    ensemble.setAtoms(target_atoms)
    # ensemble.setCoords(target_atoms)

    # prody.calcRMSD(ensemble.getCoords())

    RMSD_list = []
    for frame in ensemble:
        atoms = frame.getAtoms()
        coords = frame.getCoords()
        if frame.getIndex() == 0:
            ref_coord = coords
            RMSD_list.append(0)
        else:
            RMSD_list.append(prody.calcRMSD(ref_coord, coords))

    return RMSD_list

"""
dcd_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190904/step1fs8000dcd20ns/minimized.dcd"
pdb_file = "/lustre/home/xuyuxing/Work/Kena/qmmm/fkn/n3_20190904/step1fs8000dcd20ns/solvate.pdb"
"""

def get_RE_RMSD(dcd_file, pdb_file, atom_select="not water"):
    structure = prody.parsePDB(pdb_file)
    ensemble = prody.parseDCD(dcd_file)

    target_atoms = structure.select(atom_select)
    ensemble.setAtoms(target_atoms)
    #ensemble.setCoords(target_atoms)

    #target_atoms = structure.select(atom_select)

    ensemble.superpose()
    rmsd_1 = ensemble.getRMSDs()
    rmsf_1 = ensemble.getRMSFs()

#########
    # structure = prody.parsePDB(pdb_file)
    # ensemble = prody.parseDCD(dcd_file)
    # ensemble.setAtoms(structure)
    # ensemble.setCoords(structure)
    #
    # target_atoms = structure.select(atom_select)
    # ensemble.setAtoms(target_atoms)
    #
    # ensemble.superpose()
    # rmsd = ensemble.getRMSDs()
    # rmsf = ensemble.getRMSFs()


    # prody.calcRMSD(ensemble.getCoords())

    # RMSD_list = []
    # for frame in ensemble:
    #     atoms = frame.getAtoms()
    #     coords = frame.getCoords()
    #     if frame.getIndex() == 0:
    #         ref_coord = coords
    #         RMSD_list.append(0)
    #     else:
    #         RMSD_list.append(prody.calcRMSD(ref_coord, coords))

    return rmsd_1,rmsf_1