from toolbiox.lib.common.genome.genome_feature2 import read_bed_file, get_chrloci_overlap

input1_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/Ath.rep.bed'
input2_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/PC_Ath.bed'
input3_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/Ath.pseudo.bed'

gf_dict1 = read_bed_file(input1_file)
gf_dict2 = read_bed_file(input2_file)
gf_dict3 = read_bed_file(input3_file)
gf_dict3_long = {i:gf_dict3[i] for i in gf_dict3 if gf_dict3[i].end - gf_dict3[i].start + 1 > 200}

similarity_type = 'shorter_overlap_coverage'
threshold = 0.6

def feature_compare(gf_dict1, gf_dict2, threshold, similarity_type):
    num = 0
    overlap_gf = []
    for i in gf_dict1:
        num += 1
        print(num)
        gf1 = gf_dict1[i]
        for j in gf_dict2:
            gf2 = gf_dict2[j]
            overlap_ratio = get_chrloci_overlap(gf1, gf2, similarity_type=similarity_type)
            if overlap_ratio >= threshold:
                overlap_gf.append((i, j))

    overlap_gf_dict1 = [gf_dict1_id for gf_dict1_id, gf_dict2_id in overlap_gf]
    overlap_gf_dict2 = [gf_dict2_id for gf_dict1_id, gf_dict2_id in overlap_gf]

    only_in_set1 = list(set(gf_dict1.keys()) - set(overlap_gf_dict1))
    only_in_set2 = list(set(gf_dict2.keys()) - set(overlap_gf_dict2))

    return overlap_gf_dict1, overlap_gf_dict2, only_in_set1, only_in_set2

c1_1v2, c2_1v2, o1_1v2, o2_1v2 = feature_compare(gf_dict1, gf_dict2, threshold, similarity_type)
c1_1v3, c3_1v3, o1_1v3, o3_1v3 = feature_compare(gf_dict1, gf_dict3_long, threshold, similarity_type)
c2_2v3, c3_2v3, o2_2v3, o3_2v3 = feature_compare(gf_dict2, gf_dict3_long, threshold, similarity_type)



from toolbiox.lib.common.genome.genome_feature2 import read_bed_file, get_chrloci_overlap

input1_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/Ath.rep.bed'
input2_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/PC_Ath.bed'
input3_file = '/lustre/home/xuyuxing/Work/Gel/Pseudogene/temp/Ath.pseudo.bed'

gf_dict1 = read_bed_file(input1_file)
gf_dict2 = read_bed_file(input2_file)
gf_dict3 = read_bed_file(input3_file)
gf_dict3_long = {i:gf_dict3[i] for i in gf_dict3 if gf_dict3[i].end - gf_dict3[i].start + 1 > 200}
    num = 0
    overlap_gf = []
    for i in gf_dict1:
        num += 1
        print(num)
        gf1 = gf_dict1[i]
        for j in gf_dict2:
            gf2 = gf_dict2[j]
            overlap_ratio = get_chrloci_overlap(gf1, gf2, similarity_type=similarity_type)
            if overlap_ratio > 0:
                overlap_gf.append(overlap_ratio)
similarity_type = "jaccord_score"
    num = 0
    overlap_gf = []
    for i in gf_dict1:
        num += 1
        print(num)
        gf1 = gf_dict1[i]
        for j in gf_dict3_long:
            gf2 = gf_dict3_long[j]
            overlap_ratio = get_chrloci_overlap(gf1, gf2, similarity_type=similarity_type)
            if overlap_ratio > 0:
                overlap_gf.append(overlap_ratio)
overlap_gf
overlap_gf
with open("1.txt", 'w') as f:
    for i in overlap_gf:
        f.write(str(i)+"\n")
pwd
    num = 0
    overlap_gf = []
    for i in gf_dict2:
        num += 1
        print(num)
        gf1 = gf_dict2[i]
        for j in gf_dict3_long:
            gf2 = gf_dict3_long[j]
            overlap_ratio = get_chrloci_overlap(gf1, gf2, similarity_type=similarity_type)
            if overlap_ratio > 0:
                overlap_gf.append(overlap_ratio)
with open("2.txt", 'w') as f:
    for i in overlap_gf:
        f.write(str(i)+"\n")
hist