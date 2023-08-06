jf_file = '/lustre/home/xuyuxing/Database/Gel/other/Aof/sra_data/ERR2040729.jf'

from toolbiox.lib.xuyuxing.base.base_function import cmd_open
from toolbiox.lib.common.util import printer_list
from toolbiox.lib.common.os import cmd_run


def jf_file_parse(jf_file):
    for i in cmd_open("jellyfish dump -c %s" % jf_file):
        print(i)
        kmer, num = i.split()
        num = int(num)
        yield kmer, num


def get_jf_file(input_file_list, jf_file, gzip_flag=False, sra_flag=False):

    if gzip_flag:
        input_file_string = printer_list(input_file_list, sep=" ", head="<(zcat ") + ")"
    else:
        input_file_string = printer_list(input_file_list, sep=" ", head="<(cat ") + ")"
    
    if sra_flag:
        input_file_string = printer_list(input_file_list, sep=" ", head="<(fastq-dump -Z ") + ")"


    cmd_string = "jellyfish count -m 17 -s 100M -t 20 -C -o " + jf_file + " " + input_file_string
    
    cmd_run(cmd_string)

jf_file = '/lustre/home/xuyuxing/Database/Gel/other/Aof/sra_data/ERR2040729.jf'
num = 0
for i in jf_file_parse(jf_file):
    num += 1

def compare_two_jf():
    pass