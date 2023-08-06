import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import cm
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
import matplotlib.gridspec as gridspec


def add_high(data, num):
    new_array = []
    for i in range(0, int(data.shape[0])):
        for j in range(0, num):
            new_array.append(data[i,])
    return np.array(new_array)


file = '/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/printdata.txt'

data_dir = tsv_file_dict_parse(file)

intersection_list = {"WT": ("S02_S01", "S06_S05", "S10_S26", "S25_S09"),
                     "sT": ("S04_S03", "S08_S07", "S12_S11", "S28_S27"),
                     "Wm": ("S18_S17", "S22_S30", "S29_S21", "S32_S31"),
                     "sm": ("S14_S13", "S16_S15", "S20_S19", "S24_S23")}

id = 'ATCG01170.1'

peak_data_WT = []
for peak_tab in intersection_list['WT']:
    peak_data_WT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_sT = []
for peak_tab in intersection_list['sT']:
    peak_data_sT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_WT = add_high(np.array(peak_data_WT), 3)
peak_data_sT = add_high(np.array(peak_data_sT), 3)

# plt.style.use('ggplot')

# Make plot with vertical (default) colorbar
# fig, (ax0, ax1) = plt.subplots(2, 1)

# plt.figure(figsize=(int(len(peak_data_WT[0]) / 100), 10))

gs = gridspec.GridSpec(5, 1, height_ratios=[3, 1, 1, 1, 1])

ax0 = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1], sharex=ax0)
ax2 = plt.subplot(gs[2], sharex=ax0)
ax3 = plt.subplot(gs[3], sharex=ax0)
ax4 = plt.subplot(gs[4], sharex=ax0)

# plt.set_size_inches(18.5, 10.5)

# plt.subplots_adjust(wspace=0, hspace=-100)

cax0 = ax0.imshow(np.array(list(peak_data_WT) + list(peak_data_sT)), interpolation='nearest', cmap=cm.YlOrRd)
# plt.colorbar(cax0, ax=ax0)
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

WT_coverage_p = np.array(WT_coverage_p).mean(axis=0)

ax1.set_xlim(0, len(WT_coverage_p))

cax1 = ax1.plot(range(0, len(WT_coverage_p)), WT_coverage_p, 'b')
# cax1 = ax1.imshow(peak_data_sT)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.spines['left'].set_visible(False)
ax1.get_xaxis().set_visible(False)

WT_coverage_n = np.array(WT_coverage_n).mean(axis=0)

ax2.set_xlim(0, len(WT_coverage_n))

cax2 = ax2.plot(range(0, len(WT_coverage_n)), WT_coverage_n, 'b--')
# cax1 = ax1.imshow(peak_data_sT)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.get_xaxis().set_visible(False)

sT_coverage_p = []
sT_coverage_n = []
for peak_tab in intersection_list['sT']:
    CMC_p, CMC_n = peak_tab.split('_')
    sT_coverage_p.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    sT_coverage_n.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

sT_coverage_p = np.array(sT_coverage_p).mean(axis=0)

ax3.set_xlim(0, len(sT_coverage_p))

cax3 = ax3.plot(range(0, len(sT_coverage_p)), sT_coverage_p, 'g')
# cax1 = ax1.imshow(peak_data_sT)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax3.spines['left'].set_visible(False)
ax3.get_xaxis().set_visible(False)

sT_coverage_n = np.array(sT_coverage_n).mean(axis=0)

ax4.set_xlim(0, len(sT_coverage_p))

cax4 = ax4.plot(range(0, len(sT_coverage_n)), sT_coverage_n, 'g--')
# cax1 = ax1.imshow(peak_data_sT)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['bottom'].set_visible(False)
ax4.spines['left'].set_visible(False)

xmajorLocator = MultipleLocator(200)
ax0.xaxis.set_major_locator(xmajorLocator)
ax1.xaxis.set_major_locator(xmajorLocator)
ax2.xaxis.set_major_locator(xmajorLocator)
ax3.xaxis.set_major_locator(xmajorLocator)
ax4.xaxis.set_major_locator(xmajorLocator)
# plt.axis('off')
ax0.yaxis.set_major_locator(plt.NullLocator())
ax1.yaxis.set_major_locator(plt.NullLocator())
ax2.yaxis.set_major_locator(plt.NullLocator())
ax3.yaxis.set_major_locator(plt.NullLocator())
ax4.yaxis.set_major_locator(plt.NullLocator())

# plt.grid(False)
plt.savefig('/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/' + id + '.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()

##################################

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import cm
from toolbiox.lib.common.fileIO import tsv_file_dict_parse


def add_high(data, num):
    new_array = []
    for i in range(0, int(data.shape[0])):
        for j in range(0, num):
            new_array.append(data[i,])
    return np.array(new_array)


file = '/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/printdata.txt'

data_dir = tsv_file_dict_parse(file)

intersection_list = {"WT": ("S02_S01", "S06_S05", "S10_S26", "S25_S09"),
                     "sT": ("S04_S03", "S08_S07", "S12_S11", "S28_S27"),
                     "Wm": ("S18_S17", "S22_S30", "S29_S21", "S32_S31"),
                     "sm": ("S14_S13", "S16_S15", "S20_S19", "S24_S23")}

id = 'ATCG01180.1'

peak_data_WT = []
for peak_tab in intersection_list['WT']:
    peak_data_WT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_sT = []
for peak_tab in intersection_list['sT']:
    peak_data_sT.append([float(data_dir[i][peak_tab]) for i in data_dir if data_dir[i]['Gene_id'] == id])

peak_data_WT = add_high(np.array(peak_data_WT), 10)
peak_data_sT = add_high(np.array(peak_data_sT), 10)

# plt.style.use('ggplot')

# Make plot with vertical (default) colorbar
fig, (ax0, ax1) = plt.subplots(2, 1)

fig.set_size_inches(18.5, 10.5)

plt.subplots_adjust(wspace=0, hspace=0)

cax0 = ax0.imshow(np.array(list(peak_data_WT) + list(peak_data_sT)), interpolation='nearest', cmap=cm.YlOrRd)
# fig.colorbar(cax0, ax=ax0)
# cax0 = ax0.imshow(peak_data_WT, interpolation='nearest', cmap=cm.YlOrRd)
# cax0 = ax0.imshow(peak_data_WT)

WT_coverage = []
for peak_tab in intersection_list['WT']:
    CMC_p, CMC_n = peak_tab.split('_')
    WT_coverage.append([float(data_dir[i][CMC_p]) for i in data_dir if data_dir[i]['Gene_id'] == id])
    WT_coverage.append([float(data_dir[i][CMC_n]) for i in data_dir if data_dir[i]['Gene_id'] == id])

cax1 = ax1.plot(range(0, len(WT_coverage[0])), WT_coverage[0])
# cax1 = ax1.imshow(peak_data_sT)

xmajorLocator = MultipleLocator(200)
ax0.xaxis.set_major_locator(xmajorLocator)
ax1.xaxis.set_major_locator(xmajorLocator)
plt.axis('off')
ax0.yaxis.set_major_locator(plt.NullLocator())
ax1.yaxis.set_major_locator(plt.NullLocator())

plt.grid(False)
fig.savefig('/lustre/home/xuyuxing/Work/Other/Pseudouracil/all_tran/' + id + '.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()


def add_high(data, num):
    new_array = []
    for i in range(0, int(data.shape[0])):
        for j in range(0, num):
            new_array.append(data[i,])
    return np.array(new_array)


plt.style.use('ggplot')
from numpy.random import randn

# Make plot with vertical (default) colorbar
fig, ax = plt.subplots()
fig.set_size_inches(18.5, 10.5)
# data = np.clip(randn(250, 250), -1, 1)

data = np.loadtxt("/lustre/home/xuyuxing/Work/Other/tmp/printdata.txt", delimiter="\t")

# 18s rRNA
data = data.transpose()[:, 0:2075]
# 25s rRNA
# data = data.transpose()[:, 2428:5902]
# data = data.transpose()

maker = data[0,]
other_data = np.array([data[1,], data[2,], data[3,], data[4,]])
other_data2 = np.array([data[5,], data[6,], data[7,], data[8,]])

data2 = add_high(other_data, 10)
data3 = add_high(other_data2, 10)
# data = np.array([[1,2],[3,4],[5,6]])

data2 = np.array(
    list(data2) + list(data3) + [maker, maker, maker, maker, maker, maker, maker, maker, maker, maker, maker])

cax = ax.imshow(data2, interpolation='nearest', cmap=cm.YlOrRd)
# ax.set_title('Gaussian noise with vertical colorbar')

# Add colorbar, make sure to specify tick locations to match desired ticklabels
# cbar = fig.colorbar(cax, ticks=[-1, 0, 1])
# cbar.ax.set_yticklabels(['< -1', '0', '> 1'])  # vertically oriented colorbar

line = ax.axhline(y=79, color='w', linewidth=0.8)
line2 = ax.axhline(y=39, color='w', linewidth=0.8)

xmajorLocator = MultipleLocator(200)
ax.xaxis.set_major_locator(xmajorLocator)

# plt.axis('off')
ax.yaxis.set_major_locator(plt.NullLocator())
plt.grid(False)
fig.savefig('18S rRNA.pdf', dpi=1000)
# fig.savefig('25S rRNA.pdf', dpi=1000)

plt.show()
