import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.path as path


def histogram_style1(data_list, figure_file=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Fixing random state for reproducibility
    # np.random.seed(19680801)

    # histogram our data with numpy
    # data = np.random.randn(1000)
    n, bins = np.histogram(data_list, bins='auto')

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n
    nrects = len(left)

    nverts = nrects * (1 + 3 + 1)
    verts = np.zeros((nverts, 2))
    codes = np.ones(nverts, int) * path.Path.LINETO
    codes[0::5] = path.Path.MOVETO
    codes[4::5] = path.Path.CLOSEPOLY
    verts[0::5, 0] = left
    verts[0::5, 1] = bottom
    verts[1::5, 0] = left
    verts[1::5, 1] = top
    verts[2::5, 0] = right
    verts[2::5, 1] = top
    verts[3::5, 0] = right
    verts[3::5, 1] = bottom

    barpath = path.Path(verts, codes)
    # patch = patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)
    patch = patches.PathPatch(barpath, facecolor='blue', edgecolor="blue", linewidth=0.0)
    ax.add_patch(patch)

    ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())

    if not figure_file is None:
        plt.savefig(figure_file, dpi=1000)
    plt.show()
    plt.close('all')
    return n, bins


def histogram_style2(data_list, figure_file):
    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # n, bins, whatever = ax.hist(data_list, 'auto', density=True, histtype='stepfilled', facecolor='b', alpha=0.75)
    n, bins, whatever = plt.hist(data_list, 'auto', histtype='stepfilled')

    # get the corners of the rectangles for the histogram
    # left = np.array(bins[:-1])
    # right = np.array(bins[1:])
    # bottom = np.zeros(len(left))
    # top = bottom + n

    # ax.set_xlim(left[0], right[-1])
    # ax.set_ylim(bottom.min(), top.max())

    plt.savefig(figure_file, dpi=1000)
    plt.show()
    plt.close('all')
    return n, bins


def int_barplot(data_list, figure_file):
    from collections import Counter
    Counter_data = Counter(data_list)
    x, y = [], []
    for i in range(min(Counter_data.keys()), max(Counter_data.keys()) + 1):
        x.append(i)
        y.append(Counter_data[i])

    fig = plt.gcf()
    fig.set_size_inches(10.5, 10.5)
    plt.subplot(111)
    plt.axis([min(x), max(x), min(y), max(y)])
    plt.bar(x, y, width=1)
    # plt.xlabel('time (s)')
    # plt.ylabel('Wild type cmc+')
    ax = plt.gca()
    #ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    #plt.yticks([])
    #plt.xticks([])
    plt.grid(False)

    plt.savefig(figure_file, dpi=1000)

    plt.show()
