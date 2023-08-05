from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
from toolbiox.lib.common.genome.seq_base import read_fasta
import re

repeat_superfamily_dict = {
    'LTR':['LTR/Gypsy', 'LTR/unknown', 'LTR/Copia'],
    'MITE':['MITE/DTM', 'MITE/DTC', 'MITE/DTH', 'MITE/DTA', 'MITE/DTT'],
    'TIR':['DNA/DTM', 'TIR/MuDR_Mutator', 'DNA/DTC', 'TIR/EnSpm_CACTA', 'DNA/DTH', 'TIR/PIF_Harbinger', 'DNA/DTA', 'TIR/hAT', 'DNA/DTT', 'TIR/Tc1_Mariner', ],
    'Helitron':['DNA/Helitron', 'Helitron'],
    'Maverick':['Maverick'],
    'LINE':['LINE/unknown'],
    'Other':['Unknown', 'pararetrovirus'],
}

def get_r_family_name(r_name):
    mlist = re.findall(r'(TE_\d+)', r_name)
    if len(mlist):
        r_name = mlist[0]
    else:
        r_name = None
    return r_name

def read_EDTA_gff(EDTA_gff_file):
    EDTA_gff_dict = read_gff_file(EDTA_gff_file)
    
    repeat_class_dict = {}
    for source in EDTA_gff_dict:
        for r_id in EDTA_gff_dict[source]:
            r = EDTA_gff_dict[source][r_id]
            r_name = r.qualifiers['Name'][0]
            r_family_id = get_r_family_name(r_name)
            if r_family_id:        
                repeat_class = r.qualifiers['Classification'][0]
                repeat_class_dict.setdefault(repeat_class, {}).setdefault(r_family_id,{})
                repeat_class_dict[repeat_class][r_family_id][r_id] = r

    return repeat_class_dict
    
def read_EDTA_lib(EDTA_lib_file):
    
    EDTA_lib_dict = read_fasta(EDTA_lib_file)[0]

    EDTA_lib_seq_dict = {}
    for i in EDTA_lib_dict:
        EDTA_lib_seq_dict[get_r_family_name(i)] = EDTA_lib_dict[i]

    return EDTA_lib_seq_dict
