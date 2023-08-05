import numpy as np
from matplotlib import cm, rc, rcParams
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
from matplotlib.path import Path
import matplotlib.patches as Patches

from toolbiox.lib.xuyuxing.base.console import green, dark
import copy
import os.path as op
import sys
import logging
import matplotlib.cbook as cbook


def save_figure(fig_object, output_file, format='svg'):
    fig_object.savefig(output_file, format=format,
                       facecolor='none', edgecolor='none', bbox_inches='tight')


# def savefig(figname, dpi=150, iopts=None, cleanup=True):
#     try:
#         format = figname.rsplit(".", 1)[-1].lower()
#     except:
#         format = "pdf"
#     try:
#         plt.savefig(figname, dpi=dpi, format=format)
#     except Exception as e:
#         message = "savefig failed. Reset usetex to False."
#         message += "\n{0}".format(str(e))
#         rc("text", usetex=False)
#         plt.savefig(figname, dpi=dpi)

#     msg = "Figure saved to `{0}`".format(figname)
#     if iopts:
#         msg += " {0}".format(iopts)

#     if cleanup:
#         plt.rcdefaults()


def load_image(input_file):
    with cbook.get_sample_data(input_file) as image_file:
        image = plt.imread(image_file)
    return image


def quick_show_image_from_file(input_file):

    fig, ax = plt.subplots()

    im = load_image(input_file)

    ax.imshow(im)
    ax.axis('off')

    plt.show()


# def load_image(filename):
#     img = plt.imread(filename)
#     if len(img.shape) == 2:  # Gray-scale image, convert to RGB
#         # http://www.socouldanyone.com/2013/03/converting-grayscale-to-rgb-with-numpy.html
#         h, w = img.shape
#         ret = np.empty((h, w, 3), dtype=np.uint8)
#         ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = img
#         img = ret
#     else:
#         h, w, c = img.shape
#     print("Image `{0}` loaded ({1}px x {2}px).".format(filename, w, h))
#     return img

# ascii


def asciiaxis(x, digit=1):
    if isinstance(x, int):
        x = str(x)
    elif isinstance(x, float):
        x = "{0:.{1}f}".format(x, digit)
    elif isinstance(x, np.int64):
        x = str(x)
    elif isinstance(x, np.ndarray):
        assert len(x) == 2
        x = str(x).replace("]", ")")  # upper bound not inclusive

    return x


def asciiplot(x, y, digit=1, width=50, title=None, char="="):
    """
    Print out a horizontal plot using ASCII chars.
    width is the textwidth (height) of the plot.
    """
    ax = np.array(x)
    ay = np.array(y)

    if title:
        print(dark(title), file=sys.stderr)

    az = ay * width // ay.max()
    tx = [asciiaxis(x, digit=digit) for x in ax]
    rjust = max([len(x) for x in tx]) + 1

    for x, y, z in zip(tx, ay, az):
        x = x.rjust(rjust)
        y = y or ""
        z = green(char * z)
        print("{0} |{1} {2}".format(x, z, y), file=sys.stderr)


# litter plot
def add_stick_box_plot(start, end, high=5, x_y_lim=None, thickness=2, linewidth=2, alpha=0.5, facecolor='b', edgecolor='k', bulge=2):
    if not x_y_lim:
        circle_radius = thickness/bulge
    else:
        x_lim, y_lim = x_y_lim
        x_y_ratio = (max(x_lim) - min(x_lim)) / (max(y_lim) - min(y_lim))
        circle_radius = (thickness/bulge) * x_y_ratio

    if end - start > 2 * circle_radius:

        start = start + circle_radius
        end = end - circle_radius

        path_data = [
            # up line
            (Path.MOVETO, [start, high+thickness/2]),
            (Path.LINETO, [end, high+thickness/2]),
            # right CURVE4
            (Path.CURVE4, [end+circle_radius, high+thickness/2]),
            (Path.CURVE4, [end+circle_radius, high-thickness/2]),
            (Path.CURVE4, [end, high-thickness/2]),
            # down line
            (Path.LINETO, [start, high-thickness/2]),
            # left CURVE4
            (Path.CURVE4, [start-circle_radius, high-thickness/2]),
            (Path.CURVE4, [start-circle_radius, high+thickness/2]),
            (Path.CURVE4, [start, high+thickness/2]),
        ]

        codes, verts = zip(*path_data)
        path = Path(verts, codes)

        patch = Patches.PathPatch(
            path, alpha=alpha, facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth)

    else:
        patch = Patches.Circle(((end + start)/2, high), radius=circle_radius,
                               alpha=alpha, facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth)

    return patch


def add_small_axes_on_other(main_ax, figure, left_bottom_xy, right_top_xy):
    """
    add a new axes on a main axes by left_bottom_xy and right_top_xy

    left_bottom_xy = (2,2)
    right_top_xy = (3,4)
    """

    # print(ax.transData.transform((0, 4)))
    lb_xy = figure.transFigure.inverted().transform(
        main_ax.transData.transform(left_bottom_xy))
    rt_xy = figure.transFigure.inverted().transform(
        main_ax.transData.transform(right_top_xy))

    return figure.add_axes([lb_xy[0], lb_xy[1], rt_xy[0]-lb_xy[0], rt_xy[1]-lb_xy[1]])
