import re
from toolbiox.lib.common.math.interval import sum_interval_length


class repeat_case(object):
    def __init__(self, SW_score, perc_div, perc_del, perc_ins, query, begin, end, left, strand, repeat_id, repeat_class,
                 repeat_range1, repeat_range2, repeat_range3, ID=None, star=False):
        self.SW_score = int(SW_score)
        self.perc_div = float(perc_div)
        self.perc_del = float(perc_del)
        self.perc_ins = float(perc_ins)
        self.q_name = query
        self.q_start = int(begin)
        self.q_end = int(end)

        # q_length
        left = int(re.search(r'^\((.*)\)$', left).groups()[0])
        self.q_length = self.q_end + left

        # strand
        if strand == "C":
            self.strand = "-"
        else:
            self.strand = "+"

        self.repeat_name = repeat_id
        self.repeat_class = repeat_class

        # repeat range
        if self.strand == "+":
            self.r_start = int(repeat_range1)
            self.r_end = int(repeat_range2)
            repeat_range3 = int(re.search(r'^\((.*)\)$', repeat_range3).groups()[0])
            self.r_length = int(repeat_range2) + repeat_range3
        else:
            self.r_start = int(repeat_range3)
            self.r_end = int(repeat_range2)
            repeat_range1 = int(re.search(r'^\((.*)\)$', repeat_range1).groups()[0])
            self.r_length = int(repeat_range2) + repeat_range1

        if ID:
            self.ID = ID
        else:
            self.ID = None


        if star:
            self.star = True
        else:
            self.star = False

    def __str__(self):
        return "ID: %s\n" \
               "query: %s\n" \
               "begin: %d\n" \
               "end: %d\n" \
               "strand: %s\n" \
               "repeat_class: %s\n" \
               "repeat_id: %s\n" \
               "repeat_begin: %d\n" \
               "repeat_end: %d\n" \
               "repeat_length: %d\n" \
               "repeat_coverage: %.2f\n" \
               "div: %.1f\n" \
               "del: %.1f\n" \
               "ins: %.1f\n" \
               "SW_score: %d\n" \
               "star: %s\n" % (
                   self.ID, self.q_name, self.q_start, self.q_end, self.strand, self.repeat_class, self.repeat_name,
                   self.r_start, self.r_end, self.r_length, (self.r_end - self.r_start) / self.r_length * 100,
                   self.perc_div,
                   self.perc_del, self.perc_ins, self.SW_score, self.star)


class repeat_family(object):
    def __str__(self):
        case_num = len(self.case_list)
        total_length = self.length_sum()
        return "repeat_name: %s\n" \
               "repeat_class: %s\n" \
               "case_num: %d\n" \
               "length_sum: %d\n" % (self.repeat_name, self.repeat_class, case_num, total_length)

    def __init__(self, repeat_name, repeat_class, case_list):
        self.repeat_name = repeat_name
        self.repeat_class = repeat_class
        self.case_list = case_list

    def length_sum(self):

        range_dict = {}
        for case_tmp in self.case_list:
            if case_tmp.q_name not in range_dict:
                range_dict[case_tmp.q_name] = []
            range_dict[case_tmp.q_name].append((case_tmp.q_start,case_tmp.q_end))

        total_length = 0
        for query in range_dict:
            total_length = total_length + sum_interval_length(range_dict[query])

        return total_length

def repeatmasker_parser(repeatmasker_outfile):
    """
    repeatmasker_outfile = "/lustre/home/xuyuxing/Database/Cuscuta/Cau/genomev1.1/repeat/denovo/Cuscuta.genome.v1.1.fasta.finial.out/Cuscuta.genome.v1.1.fasta.out"
    :param repeatmasker_out:
    :return:
    """

    repeat_category = ['SINE',
                       'DNA',
                       'DNAauto',
                       'scRNA',
                       'LINE',
                       'snRNA',
                       'RC',
                       'LTR',
                       'RNA',
                       'Retroposon',
                       'Low_complexity',
                       'Simple_repeat',
                       'rRNA',
                       'tRNA',
                       'Satellite',
                       'Unknown',
                       'Segmental',
                       'Unspecified']

    output_dir = {}
    with open(repeatmasker_outfile, "r") as f:
        num = 0
        for each_line in f.readlines():
            num = num + 1
            if num <= 3:
                continue
            each_line = each_line.strip()
            each_line = re.sub(r'\s+', ' ', each_line)
            info = each_line.split(" ")

            repeat_record = repeat_case(*info)

            head_class = repeat_record.repeat_class.split("/")[0]
            head_class = re.sub('\?', '', head_class )

            if head_class in repeat_category:
                if head_class not in output_dir:
                    output_dir[head_class] = {}
                repeat_family_name = repeat_record.repeat_name
                if repeat_family_name not in output_dir[head_class]:
                    output_dir[head_class][repeat_family_name] = repeat_family(repeat_family_name,head_class,[])
                output_dir[head_class][repeat_family_name].case_list.append(repeat_record)
            else:
                raise ValueError("category incomp: %s" % head_class)

    return output_dir