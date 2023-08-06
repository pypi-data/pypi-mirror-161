import csv
import re


def trf_dat_to_dict(trf_dat):
    # trf_dat = "/lustre/home/xuyuxing/Database/Other_genome/Ath/Tair10/TAIR10_Chr.all.fasta.2.7.7.80.10.20.10.dat"
    fieldnames_list = ["start", "end", "period_size", "copy_num", "consensus_size", "matches", "indels", "score",
                       "A_perc", "C_perc", "G_perc", "T_perc", "entropy", "unit", "sequence"]
    trf_dict = {}
    with open(trf_dat, 'r') as dat:
        num = 0
        for info in dat.read().split("Sequence: "):
            if num == 0:
                num = num + 1
                continue
            info_dict = list(csv.DictReader(info.splitlines(), delimiter=" ", fieldnames=fieldnames_list))
            seqname = info.splitlines()[0]
            name_short = re.search('^(\S+)', seqname).group(1)
            del info_dict[0]
            del info_dict[0]
            trf_dict[name_short] = []
            for i in info_dict:
                i["chr"] = name_short
                if re.match(r'^\d+$', i["start"]):
                    i['start'] = int(i['start'])
                    i['end'] = int(i['end'])
                    i['period_size'] = int(i['period_size'])
                    i['copy_num'] = float(i['copy_num'])
                    i['consensus_size'] = int(i['consensus_size'])
                    i['matches'] = int(i['matches'])
                    i['indels'] = int(i['indels'])
                    i['score'] = int(i['score'])
                    i['A_perc'] = int(i['A_perc'])
                    i['C_perc'] = int(i['C_perc'])
                    i['G_perc'] = int(i['G_perc'])
                    i['T_perc'] = int(i['T_perc'])
                    i['entropy'] = float(i['entropy'])
                    trf_dict[name_short].append(i)
    return trf_dict
