import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import cm
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import matplotlib.gridspec as gridspec


def add_high(data, num, strand):
    new_array = []
    for i in range(0, int(data.shape[0])):
        for j in range(0, num):
            if strand == "+":
                new_array.append(data[i,])
            else:
                new_array.append(list(reversed(data[i,])))
    return np.array(new_array)


file = '/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/printdata2.txt'

data_dir = tsv_file_dict_parse(file)

intersection_list = {"WT": ("S02_S01", "S06_S05", "S10_S26"),
                     "sT": ("S04_S03", "S08_S07", "S12_S11"),
                     "Wm": ("S18_S17", "S22_S30", "S32_S31"),
                     "sm": ("S14_S13", "S16_S15", "S20_S19")}

id = 'ATCG01210.1'
strand = "+"
site = 136479

a = list(range(site - 20, site + 21))

peak_data_WT = []
for peak_tab in intersection_list['WT']:
    peak_data_WT.append([float(data_dir[i][peak_tab]) for i in data_dir if int(data_dir[i]['site']) in a])

peak_data_sT = []
for peak_tab in intersection_list['sT']:
    peak_data_sT.append([float(data_dir[i][peak_tab]) for i in data_dir if int(data_dir[i]['site']) in a])

peak_data_WT = add_high(np.array(peak_data_WT), 10, strand)
peak_data_sT = add_high(np.array(peak_data_sT), 10, strand)

# plt.style.use('ggplot')

# Make plot with vertical (default) colorbar
# fig, (ax0, ax1) = plt.subplots(2, 1)

#plt.figure(figsize=(25, 10))

# gs = gridspec.GridSpec(17, 1, height_ratios=[200, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
gs = gridspec.GridSpec(1, 1, height_ratios=[1])

ax0 = plt.subplot(gs[0])
# plt.set_size_inches(18.5, 10.5)

# plt.subplots_adjust(wspace=0, hspace=-100)

cax0 = ax0.imshow(np.array(list(peak_data_WT) + list(peak_data_sT)), interpolation='nearest', cmap=cm.YlOrRd)
plt.colorbar(cax0, ax=ax0)
# cax0 = ax0.imshow(peak_data_WT, interpolation='nearest', cmap=cm.YlOrRd)
# cax0 = ax0.imshow(peak_data_WT)
ax0.spines['top'].set_visible(False)
ax0.spines['right'].set_visible(False)
ax0.spines['bottom'].set_visible(False)
ax0.spines['left'].set_visible(False)
ax0.get_xaxis().set_visible(False)
ax0.set_xlim(0, len(peak_data_WT[0]))
line2 = ax0.axhline(y=29, color='w', linewidth=6)

WT_coverage_p = []
WT_coverage_n = []
for peak_tab in intersection_list['WT']:
    CMC_p, CMC_n = peak_tab.split('_')
    WT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    WT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

#xmajorLocator = MultipleLocator(200)

for ax_tmp in [ax0]:
    #ax_tmp.xaxis.set_major_locator(xmajorLocator)
    ax_tmp.yaxis.set_major_locator(plt.NullLocator())

# plt.axis('off')

# plt.grid(False)
plt.savefig('/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/' + id + '_' + str(site) + '.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()
