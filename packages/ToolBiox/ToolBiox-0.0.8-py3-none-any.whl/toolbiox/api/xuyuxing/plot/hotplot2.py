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

intersection_list = {"WT": ("S02_S01", "S06_S05", "S10_S26", "S25_S09"),
                     "sT": ("S04_S03", "S08_S07", "S12_S11", "S28_S27"),
                     "Wm": ("S18_S17", "S22_S30", "S29_S21", "S32_S31"),
                     "sm": ("S14_S13", "S16_S15", "S20_S19", "S24_S23")}

id = 'ATCG01170.1'
strand = "-"

peak_data_WT = []
for peak_tab in intersection_list['WT']:
    peak_data_WT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_sT = []
for peak_tab in intersection_list['sT']:
    peak_data_sT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_WT = add_high(np.array(peak_data_WT), 3,strand)
peak_data_sT = add_high(np.array(peak_data_sT), 3,strand)

# plt.style.use('ggplot')

# Make plot with vertical (default) colorbar
# fig, (ax0, ax1) = plt.subplots(2, 1)

# plt.figure(figsize=(int(len(peak_data_WT[0]) / 100), 10))

#gs = gridspec.GridSpec(17, 1, height_ratios=[200, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
gs = gridspec.GridSpec(17, 1, height_ratios=[10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

ax0 = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1], sharex=ax0)
ax2 = plt.subplot(gs[2], sharex=ax0)
ax3 = plt.subplot(gs[3], sharex=ax0)
ax4 = plt.subplot(gs[4], sharex=ax0)
ax5 = plt.subplot(gs[5], sharex=ax0)
ax6 = plt.subplot(gs[6], sharex=ax0)
ax7 = plt.subplot(gs[7], sharex=ax0)
ax8 = plt.subplot(gs[8], sharex=ax0)
ax9 = plt.subplot(gs[9], sharex=ax0)
ax10 = plt.subplot(gs[10], sharex=ax0)
ax11 = plt.subplot(gs[11], sharex=ax0)
ax12 = plt.subplot(gs[12], sharex=ax0)
ax13 = plt.subplot(gs[13], sharex=ax0)
ax14 = plt.subplot(gs[14], sharex=ax0)
ax15 = plt.subplot(gs[15], sharex=ax0)
ax16 = plt.subplot(gs[16], sharex=ax0)

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
line2 = ax0.axhline(y=11.5, color='w', linewidth=2)

WT_coverage_p = []
WT_coverage_n = []
for peak_tab in intersection_list['WT']:
    CMC_p, CMC_n = peak_tab.split('_')
    WT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    WT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

num = 0
for ax_tmp1, ax_tmp2 in [(ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)]:

    ax_tmp1.set_xlim(0, len(WT_coverage_p[num]))

    if strand == "+":
        data = WT_coverage_p[num]
    else:
        data = list(reversed(WT_coverage_p[num]))

    cax1 = ax_tmp1.plot(range(0, len(WT_coverage_p[num])), data, 'b', lw=0.8)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp1.spines['top'].set_visible(False)
    ax_tmp1.spines['right'].set_visible(False)
    ax_tmp1.spines['bottom'].set_visible(False)
    ax_tmp1.spines['left'].set_visible(False)
    ax_tmp1.get_xaxis().set_visible(False)

    ax_tmp2.set_xlim(0, len(WT_coverage_n))

    if strand == "+":
        data = WT_coverage_n[num]
    else:
        data = list(reversed(WT_coverage_n[num]))

    cax2 = ax_tmp2.plot(range(0, len(WT_coverage_n[num])), data, 'b--', lw=0.8)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp2.spines['top'].set_visible(False)
    ax_tmp2.spines['right'].set_visible(False)
    ax_tmp2.spines['bottom'].set_visible(False)
    ax_tmp2.spines['left'].set_visible(False)
    ax_tmp2.get_xaxis().set_visible(False)

    num = num + 1

sT_coverage_p = []
sT_coverage_n = []
for peak_tab in intersection_list['sT']:
    CMC_p, CMC_n = peak_tab.split('_')
    sT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    sT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

num = 0
for ax_tmp1, ax_tmp2 in [(ax9, ax10), (ax11, ax12), (ax13, ax14), (ax15, ax16)]:
    ax_tmp1.set_xlim(0, len(sT_coverage_p[num]))

    if strand == "+":
        data = sT_coverage_p[num]
    else:
        data = list(reversed(sT_coverage_p[num]))

    cax1 = ax_tmp1.plot(range(0, len(sT_coverage_p[num])), data, 'g', lw=0.8)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp1.spines['top'].set_visible(False)
    ax_tmp1.spines['right'].set_visible(False)
    ax_tmp1.spines['bottom'].set_visible(False)
    ax_tmp1.spines['left'].set_visible(False)
    ax_tmp1.get_xaxis().set_visible(False)

    ax_tmp2.set_xlim(0, len(sT_coverage_p[num]))

    if strand == "+":
        data = sT_coverage_n[num]
    else:
        data = list(reversed(sT_coverage_n[num]))

    cax2 = ax_tmp2.plot(range(0, len(sT_coverage_n[num])), data, 'g--', lw=0.8)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp2.spines['top'].set_visible(False)
    ax_tmp2.spines['right'].set_visible(False)
    ax_tmp2.spines['bottom'].set_visible(False)
    ax_tmp2.spines['left'].set_visible(False)
    if not num == 3:
        ax_tmp2.get_xaxis().set_visible(False)

    num = num + 1
xmajorLocator = MultipleLocator(200)

for ax_tmp in [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12, ax13, ax14, ax15, ax16]:
    ax_tmp.xaxis.set_major_locator(xmajorLocator)
    ax_tmp.yaxis.set_major_locator(plt.NullLocator())

# plt.axis('off')

# plt.grid(False)
plt.savefig('/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/' + id + '.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()


####

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

intersection_list = {"WT": ("S02_S01", "S06_S05", "S10_S26", "S25_S09"),
                     "sT": ("S04_S03", "S08_S07", "S12_S11", "S28_S27"),
                     "Wm": ("S18_S17", "S22_S30", "S29_S21", "S32_S31"),
                     "sm": ("S14_S13", "S16_S15", "S20_S19", "S24_S23")}

id = 'ATCG00920.1'
strand = "+"

peak_data_WT = []
for peak_tab in intersection_list['WT']:
    peak_data_WT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_sT = []
for peak_tab in intersection_list['sT']:
    peak_data_sT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_WT = add_high(np.array(peak_data_WT), 40, strand)
peak_data_sT = add_high(np.array(peak_data_sT), 40, strand)

# plt.style.use('ggplot')

# Make plot with vertical (default) colorbar
# fig, (ax0, ax1) = plt.subplots(2, 1)

plt.figure(figsize=(25, 10))

#gs = gridspec.GridSpec(17, 1, height_ratios=[200, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
gs = gridspec.GridSpec(17, 1, height_ratios=[25, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

ax0 = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1], sharex=ax0)
ax2 = plt.subplot(gs[2], sharex=ax0)
ax3 = plt.subplot(gs[3], sharex=ax0)
ax4 = plt.subplot(gs[4], sharex=ax0)
ax5 = plt.subplot(gs[5], sharex=ax0)
ax6 = plt.subplot(gs[6], sharex=ax0)
ax7 = plt.subplot(gs[7], sharex=ax0)
ax8 = plt.subplot(gs[8], sharex=ax0)
ax9 = plt.subplot(gs[9], sharex=ax0)
ax10 = plt.subplot(gs[10], sharex=ax0)
ax11 = plt.subplot(gs[11], sharex=ax0)
ax12 = plt.subplot(gs[12], sharex=ax0)
ax13 = plt.subplot(gs[13], sharex=ax0)
ax14 = plt.subplot(gs[14], sharex=ax0)
ax15 = plt.subplot(gs[15], sharex=ax0)
ax16 = plt.subplot(gs[16], sharex=ax0)

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
line2 = ax0.axhline(y=158, color='w', linewidth=6)

WT_coverage_p = []
WT_coverage_n = []
for peak_tab in intersection_list['WT']:
    CMC_p, CMC_n = peak_tab.split('_')
    WT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    WT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

num = 0
for ax_tmp1, ax_tmp2 in [(ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)]:

    ax_tmp1.set_xlim(0, len(WT_coverage_p[num]))

    if strand == "+":
        data = WT_coverage_p[num]
    else:
        data = list(reversed(WT_coverage_p[num]))

    cax1 = ax_tmp1.plot(range(0, len(WT_coverage_p[num])), data, 'b', lw=0.4)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp1.spines['top'].set_visible(False)
    ax_tmp1.spines['right'].set_visible(False)
    ax_tmp1.spines['bottom'].set_visible(False)
    ax_tmp1.spines['left'].set_visible(False)
    ax_tmp1.get_xaxis().set_visible(False)

    ax_tmp2.set_xlim(0, len(WT_coverage_n))

    if strand == "+":
        data = WT_coverage_n[num]
    else:
        data = list(reversed(WT_coverage_n[num]))

    cax2 = ax_tmp2.plot(range(0, len(WT_coverage_n[num])), data, 'b--', lw=0.4)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp2.spines['top'].set_visible(False)
    ax_tmp2.spines['right'].set_visible(False)
    ax_tmp2.spines['bottom'].set_visible(False)
    ax_tmp2.spines['left'].set_visible(False)
    ax_tmp2.get_xaxis().set_visible(False)

    num = num + 1

sT_coverage_p = []
sT_coverage_n = []
for peak_tab in intersection_list['sT']:
    CMC_p, CMC_n = peak_tab.split('_')
    sT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    sT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

num = 0
for ax_tmp1, ax_tmp2 in [(ax9, ax10), (ax11, ax12), (ax13, ax14), (ax15, ax16)]:
    ax_tmp1.set_xlim(0, len(sT_coverage_p[num]))

    if strand == "+":
        data = sT_coverage_p[num]
    else:
        data = list(reversed(sT_coverage_p[num]))

    cax1 = ax_tmp1.plot(range(0, len(sT_coverage_p[num])), data, 'g', lw=0.4)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp1.spines['top'].set_visible(False)
    ax_tmp1.spines['right'].set_visible(False)
    ax_tmp1.spines['bottom'].set_visible(False)
    ax_tmp1.spines['left'].set_visible(False)
    ax_tmp1.get_xaxis().set_visible(False)

    ax_tmp2.set_xlim(0, len(sT_coverage_p[num]))

    if strand == "+":
        data = sT_coverage_n[num]
    else:
        data = list(reversed(sT_coverage_n[num]))

    cax2 = ax_tmp2.plot(range(0, len(sT_coverage_n[num])), data, 'g--', lw=0.4)
    # cax1 = ax1.imshow(peak_data_sT)
    ax_tmp2.spines['top'].set_visible(False)
    ax_tmp2.spines['right'].set_visible(False)
    ax_tmp2.spines['bottom'].set_visible(False)
    ax_tmp2.spines['left'].set_visible(False)
    if not num == 3:
        ax_tmp2.get_xaxis().set_visible(False)

    num = num + 1
xmajorLocator = MultipleLocator(200)

for ax_tmp in [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12, ax13, ax14, ax15, ax16]:
    ax_tmp.xaxis.set_major_locator(xmajorLocator)
    ax_tmp.yaxis.set_major_locator(plt.NullLocator())

# plt.axis('off')

# plt.grid(False)
plt.savefig('/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/' + id + '.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()
