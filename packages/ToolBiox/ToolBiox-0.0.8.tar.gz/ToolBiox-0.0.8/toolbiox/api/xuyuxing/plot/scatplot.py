# coding:utf-8
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.append("/lustre/home/xuyuxing/python_project/Genome_work_tools/")
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
data_file = "/lustre/home/xuyuxing/Work/Other/tmp/printdata.txt"

data_dict = tsv_file_dict_parse(data_file)

x=sys.argv[1]
y=sys.argv[2]

S02_S01_unknown_peak = [float(data_dict[i][x]) for i in data_dict if (data_dict[i]["Known"] == "" and data_dict[i]["Detected"] == "")]
S02_S01_known_peak = [float(data_dict[i][x]) for i in data_dict if data_dict[i]["Known"] == "6"]
S02_S01_Detected_peak = [float(data_dict[i][x]) for i in data_dict if data_dict[i]["Detected"] == "6"]

S06_S05_unknown_peak = [float(data_dict[i][y]) for i in data_dict if (data_dict[i]["Known"] == "" and data_dict[i]["Detected"] == "")]
S06_S05_known_peak = [float(data_dict[i][y]) for i in data_dict if data_dict[i]["Known"] == "6"]
S06_S05_Detected_peak = [float(data_dict[i][y]) for i in data_dict if data_dict[i]["Detected"] == "6"]

plt.plot(S02_S01_unknown_peak, S06_S05_unknown_peak, 'bo', markersize=3, label='Other sites')
plt.plot(S02_S01_Detected_peak, S06_S05_Detected_peak, 'yo', markersize=3, label='Detected')
plt.plot(S02_S01_known_peak, S06_S05_known_peak, 'ro', markersize=3, label='Published')

plt.legend(loc='upper left')

plt.xlabel(x)
plt.ylabel(y)

plt.savefig('/lustre/home/xuyuxing/Work/Other/tmp/%s.vs.%s.pdf' % (x,y), dpi=1000)
