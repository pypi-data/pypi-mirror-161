import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
from toolbiox.lib.common.genome.genome_feature2 import sub_gf_traveler
from toolbiox.lib.common.math.interval import section
from matplotlib.patches import Rectangle

# gene structure plot



def gene_box(start, end, chr_line=0, box_width=1, **kwargs):
    if end < start:
        start, end = end, start
    
    rectangle_anchor_point = start,chr_line-0.5*box_width
    rectangle_width = end - start + 1
    rectangle_height = box_width
    
    return Rectangle(rectangle_anchor_point,rectangle_width,rectangle_height,**kwargs)
    

def add_box(ax, start, end, **kwargs):
    """
    use to plot a exon box on ax

    kwargs can have:
    horizon=0, width=1, facecolor='tab:blue', edgecolor='k', linewidth=2

    """

    defaults_kwargs = {
        'horizon': 0, 'vertical': None, 'width': 1, 'facecolor': 'tab:blue', 'edgecolor': 'k', 'linewidth': 2
    }

    for i in kwargs:
        if i in defaults_kwargs:
            defaults_kwargs[i] = kwargs[i]

    start, end = min(start, end), max(start, end)

    if not defaults_kwargs['vertical'] is None:
        path_data = [
            (mpath.Path.MOVETO, [
            defaults_kwargs['vertical'] + defaults_kwargs['width']/2, start]),
            (mpath.Path.LINETO, [
            defaults_kwargs['vertical'] + defaults_kwargs['width']/2, end]),
            (mpath.Path.LINETO, [
            defaults_kwargs['vertical'] - defaults_kwargs['width']/2, end]),
            (mpath.Path.LINETO, [
            defaults_kwargs['vertical'] - defaults_kwargs['width']/2, start]),
            (mpath.Path.CLOSEPOLY, [start, defaults_kwargs['vertical'] + defaults_kwargs['width']/2])]
    else:
        path_data = [
            (mpath.Path.MOVETO, [
            start, defaults_kwargs['horizon'] + defaults_kwargs['width']/2]),
            (mpath.Path.LINETO, [
            end, defaults_kwargs['horizon'] + defaults_kwargs['width']/2]),
            (mpath.Path.LINETO, [
            end, defaults_kwargs['horizon'] - defaults_kwargs['width']/2]),
            (mpath.Path.LINETO, [
            start, defaults_kwargs['horizon'] - defaults_kwargs['width']/2]),
            (mpath.Path.CLOSEPOLY, [start, defaults_kwargs['horizon'] + defaults_kwargs['width']/2])]
    

    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(
        path, facecolor=defaults_kwargs['facecolor'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])

    ax.add_patch(patch)

    return patch


def add_fat_arrow(ax, start, end, **kwargs):
    """
    use to plot a fat arrow to show gene direction

    kwargs can have:
    horizon=0, width=1, alpha=0.5, facecolor='tab:blue', edgecolor='k', linewidth=2, direction='right', arrow_head=0.5, arrow_head_length=None

    """

    defaults_kwargs = {
        'horizon': 0, 'width': 1, 'facecolor': 'tab:blue', 'edgecolor': 'k', 'linewidth': 2, "direction": 'right', "arrow_head": 0.5, "arrow_head_length": None
    }

    for i in kwargs:
        if i in defaults_kwargs:
            defaults_kwargs[i] = kwargs[i]

    if defaults_kwargs['arrow_head_length'] is None:
        defaults_kwargs['arrow_head_length'] = int(
            abs(start-end) * defaults_kwargs['arrow_head'])

    start, end = min(start, end), max(start, end)

    if defaults_kwargs['direction'] == "right":
        path_data = [
            (mpath.Path.MOVETO, [
             start, defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [end - defaults_kwargs['arrow_head_length'],
                                 defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [end, defaults_kwargs['horizon']]),
            (mpath.Path.LINETO, [end - defaults_kwargs['arrow_head_length'],
                                 defaults_kwargs['horizon'] - defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [
             start, defaults_kwargs['horizon'] - defaults_kwargs['width'] / 2]),
            (mpath.Path.CLOSEPOLY, [start, defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2])]

    elif defaults_kwargs['direction'] == "left":
        path_data = [
            (mpath.Path.MOVETO, [
             end, defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [start + defaults_kwargs['arrow_head_length'],
                                 defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [start, defaults_kwargs['horizon']]),
            (mpath.Path.LINETO, [start + defaults_kwargs['arrow_head_length'],
                                 defaults_kwargs['horizon'] - defaults_kwargs['width'] / 2]),
            (mpath.Path.LINETO, [
             end, defaults_kwargs['horizon'] - defaults_kwargs['width'] / 2]),
            (mpath.Path.CLOSEPOLY, [end, defaults_kwargs['horizon'] + defaults_kwargs['width'] / 2])]

    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(
        path, facecolor=defaults_kwargs['facecolor'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])
    ax.add_patch(patch)

    return patch


def add_broken_line(ax, start, end, **kwargs):
    defaults_kwargs = {
        'horizon': 0, 'width': 1, 'edgecolor': 'k', 'linewidth': 2
    }

    for i in kwargs:
        if i in defaults_kwargs:
            defaults_kwargs[i] = kwargs[i]

    start, end = min(start, end), max(start, end)

    mid_site = int((end + start) / 2)
    x = np.array([start, mid_site, end])
    y = np.array([defaults_kwargs['horizon'], defaults_kwargs['horizon'] +
                  defaults_kwargs['width']/2, defaults_kwargs['horizon']])
    ax.plot(x, y, color=defaults_kwargs['edgecolor'],
            linewidth=defaults_kwargs['linewidth'])


def mRNA_structure_plot(ax, mRNA, **kwargs):
    """
    use to plot a fat arrow to show gene direction

    kwargs can have:
    horizon=0, width=1, facecolor='tab:blue', edgecolor='k', linewidth=2, utr_alpha=0.5, relative_flag=False

    """

    defaults_kwargs = {
        'horizon': 0, 'width': 1, 'cds_color': '#4F94CD', 'utr_color': '#CAE1FF', 'edgecolor': '#316399', 'linewidth': 2, 'relative_flag': False, 'plot_utr': True}

    for i in kwargs:
        if i in defaults_kwargs:
            defaults_kwargs[i] = kwargs[i]

    mRNA.get_introns()
    if defaults_kwargs['plot_utr']:
        utr_list = sorted([i for i in sub_gf_traveler(mRNA) if i.type in [
            'five_prime_UTR', 'three_prime_UTR', 'five_prime_utr', 'three_prime_utr']], key=lambda x: x.start, reverse=(mRNA.strand == '-'))
    else:
        utr_list = []
    cds_list = sorted([i for i in sub_gf_traveler(mRNA) if i.type == 'CDS'], key=lambda x: x.start, reverse=(mRNA.strand == '-'))
    intron_list = sorted([i for i in sub_gf_traveler(mRNA) if i.type == 'intron'], key=lambda x: x.start, reverse=(mRNA.strand == '-'))

    if mRNA.strand == '+':
        last_box = sorted(utr_list + cds_list,
                          key=lambda x: x.start, reverse=True)[0]
        mRNA_start = min([i.start for i in utr_list + cds_list] + [i.end for i in utr_list + cds_list])
        mRNA_end = max([i.start for i in utr_list + cds_list] + [i.end for i in utr_list + cds_list])
    else:
        last_box = sorted(utr_list + cds_list,
                          key=lambda x: x.start, reverse=False)[0]
        mRNA_start = max([i.start for i in utr_list + cds_list] + [i.end for i in utr_list + cds_list])
        mRNA_end = min([i.start for i in utr_list + cds_list] + [i.end for i in utr_list + cds_list])

    # print(mRNA_start)

    for utr in utr_list:
        if utr == last_box:
            continue
        if defaults_kwargs['relative_flag']:
            add_box(ax, abs(utr.start - mRNA_start) + 1, abs(utr.end - mRNA_start) + 1, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'],
                    facecolor=defaults_kwargs['utr_color'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])            
        else:
            add_box(ax, utr.start, utr.end, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'],
                    facecolor=defaults_kwargs['utr_color'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])

    for cds in cds_list:
        if cds == last_box:
            continue
        if defaults_kwargs['relative_flag']:
            add_box(ax, abs(cds.start - mRNA_start) + 1, abs(cds.end - mRNA_start) + 1, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'],
                facecolor=defaults_kwargs['cds_color'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])
        else:
            add_box(ax, cds.start, cds.end, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'],
                facecolor=defaults_kwargs['cds_color'], edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])

    for intron in intron_list:
        if_flag, deta = section(intron.range, (mRNA_start, mRNA_end))
        if if_flag and abs(deta[1] - deta[0]) > 0:
            if defaults_kwargs['relative_flag']:
                add_broken_line(ax, abs(intron.start - mRNA_start) + 1, abs(intron.end - mRNA_start) + 1, horizon=defaults_kwargs['horizon'], width=defaults_kwargs[
                            'width']/2, edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])
            else:
                add_broken_line(ax, intron.start, intron.end, horizon=defaults_kwargs['horizon'], width=defaults_kwargs[
                            'width']/2, edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'])

    if last_box in utr_list:
        last_color = defaults_kwargs['utr_color']
    else:
        last_color = defaults_kwargs['cds_color']

    if mRNA.strand == '+':
        direction = 'right'
    elif mRNA.strand == '-':
        direction = 'left'

    arrow_head_length = min(sum(
        [abs(i.start - i.end) + 1 for i in utr_list + cds_list]) * 0.1, abs(last_box.start - last_box.end) + 1 * 0.5)

    if defaults_kwargs['relative_flag']:
        add_fat_arrow(ax, abs(last_box.start - mRNA_start) + 1, abs(last_box.end - mRNA_start) + 1, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'], facecolor=last_color,
                  edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'], direction='right', arrow_head_length=arrow_head_length)
    else:
        add_fat_arrow(ax, last_box.start, last_box.end, horizon=defaults_kwargs['horizon'], width=defaults_kwargs['width'], facecolor=last_color,
                  edgecolor=defaults_kwargs['edgecolor'], linewidth=defaults_kwargs['linewidth'], direction=direction, arrow_head_length=arrow_head_length)


def collinear_bar(ax, A_range, B_range, facecolor='orange', alpha=0.3, A_y=2, A_y_c=1, B_y=-2, B_y_c=-1):

    A_start, A_end = A_range
    A_y = 2
    A_y_c = 1
    B_start, B_end = B_range
    B_y = -2
    B_y_c = -1

    verts = [
        (A_start, A_y),
        (A_end, A_y),
        (A_end, A_y_c),
        (B_end, B_y_c),
        (B_end, B_y),
        (B_start, B_y),
        (B_start, B_y_c),
        (A_start, A_y_c),
        (A_start, A_y),
        (A_start, A_y),
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CLOSEPOLY,
    ]

    path = Path(verts, codes)

    patch = patches.PathPatch(path, facecolor=facecolor, alpha=alpha, lw=0)
    ax.add_patch(patch)


if __name__ == "__main__":
    from toolbiox.lib.common.genome.genome_feature2 import mRNA, read_gff_file

    gff_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/T91201N0.genome.gff3'
    gff_dict = read_gff_file(gff_file)
    gene_dict = gff_dict['gene']

    gf = gene_dict['GelC19G00020']

    # plot
    fig, ax = plt.subplots(figsize=(50,10))

    mRNA_gf = mRNA(from_gf=gf.sub_features[0])

    mRNA_structure_plot(ax, mRNA_gf)
    mRNA_structure_plot(ax, mRNA_gf, horizon=0, relative_flag=True)

    ax.set_xlim(mRNA_gf.start, mRNA_gf.end)

    ax.set_ylim(-5, 5)    
        
    plt.show()    
