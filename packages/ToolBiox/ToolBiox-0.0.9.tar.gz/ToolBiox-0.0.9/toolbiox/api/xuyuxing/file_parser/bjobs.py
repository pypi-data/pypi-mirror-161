import string
import re

class BjobsCommand():
    def __init__(self):
        pass

#    def seqname_short(self):
#        name_short = re.search('^(\S+)', self.seqname).group(1)
#        return name_short

def read_bjobs_l(file_name):
    with open(file_name, 'r') as f:
        all_text = f.read()
        info = string.split(all_text, '------------------------------------------------------------------------------')
        while '' in info:
            info.remove('')
        dict_output={}
        for i in info:
            not_sp = re.sub('\n', '', i)
            not_sp = re.sub(' '*21, '', not_sp)
            command = re.findall("\S+ <[^<>]+>",not_sp)
            command_detail = {}
            for j in command:
                detail = re.match(r'(\S+) <(.*)>',j)
                key_tmp = re.sub(',','',detail.group(1))
                command_detail[key_tmp]=detail.group(2)
            dict_output[command_detail['Job']] = command_detail
    return dict_output

def read_bjobs_output(file_name):
    with open(file_name, 'r') as f:
        all_text = f.read()
        info = string.split(all_text, 'The output (if any) follows:')
        while '' in info:
            info.remove('')
        output = info[1]
        bjobs_inf = info[0]
        bjobs_inf = string.split(bjobs_inf,"\n")
    return bjobs_inf,output
