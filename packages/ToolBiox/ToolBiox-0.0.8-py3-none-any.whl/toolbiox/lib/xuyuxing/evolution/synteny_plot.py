import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as Patches
import matplotlib.ticker as ticker
import matplotlib.patheffects as path_effects
from matplotlib.collections import PatchCollection
import re
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file, convert_dict_structure
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.fileIO import read_list_file, tsv_file_dict_parse
from toolbiox.api.xuyuxing.plot.base import add_stick_box_plot, add_small_axes_on_other
from collections import OrderedDict


class chromesome(object):
    def __init__(self, chr_id, gf_list, fasta_record):
        self.id = chr_id
        self.length = fasta_record.len()
        self.gf_list = sorted(gf_list, key=lambda x: x.start)

    def __str__(self):
        return '%s (%d bp): %d genes on forward strand, %d genes on reverse strand' % (self.id, self.length, len([i for i in self.gf_list if i.strand == '+']), len([i for i in self.gf_list if i.strand == '-']))

    __repr__ = __str__

    def gene_site_list(self):
        site_list = []
        for gf in self.gf_list:
            site_list.append((gf.id, gf.start, gf.end, gf.strand))
        return site_list


def build_chr_dict(gff_file, fasta_file):
    gff_dict = read_gff_file(gff_file)
    gene_dict, gf_chr_dict = convert_dict_structure(gff_dict)
    fasta_record_dict = read_fasta_by_faidx(fasta_file)

    chr_dict = {}
    for chr_id in fasta_record_dict:
        if chr_id in gf_chr_dict:
            gf_list = [gf_chr_dict[chr_id]['+'][i] for i in gf_chr_dict[chr_id]['+']
                       ] + [gf_chr_dict[chr_id]['-'][i] for i in gf_chr_dict[chr_id]['-']]
        else:
            gf_list = []
        chr_dict[chr_id] = chromesome(
            chr_id, gf_list, fasta_record_dict[chr_id])

    return chr_dict


def add_chr_patch(ax, start, end, high=5, x_y_lim=None, thickness=2, linewidth=2, color='b', chr_id=None, chr_id_site='down'):
    # add outline
    outline_patch = add_stick_box_plot(start, end, high=high, x_y_lim=x_y_lim, thickness=thickness,
                                       linewidth=linewidth, alpha=1, facecolor='none', edgecolor='k', bulge=3)
    # add inner box
    inner_patch = add_stick_box_plot(start, end, high=high, x_y_lim=x_y_lim, thickness=thickness *
                                     0.6, linewidth=0, alpha=0.5, facecolor=color, edgecolor='none', bulge=2)

    # add chr name
    if chr_id:
        if chr_id_site == 'down':
            ax.text(start, high-0.5, chr_id)
        else:
            ax.text(start, high+0.2, chr_id)

    # add chr tick

    ax.add_patch(outline_patch)
    ax.add_patch(inner_patch)


def one_way_transformation(input_data, range_input, range_output):
    return ((input_data - range_input[0]) / (range_input[1]-range_input[0]) * (range_output[1]-range_output[0])) + range_output[0]


def plot_genome(ax, chr_dict, plot_chr_id_list, plot_size_range, high, x_y_lim=None, thickness=0.2, linewidth=2, color='b'):
    plot_chr_list = [chr_dict[i] for i in plot_chr_id_list]
    plot_genome_len = sum([i.length for i in plot_chr_list])
    gap_sum_length = plot_genome_len * 0.1
    gap_num = len(plot_chr_id_list) - 1
    gap_length = gap_sum_length/gap_num
    plot_num_range = (0, plot_genome_len + gap_sum_length)

    start_point = 0
    chr_start_dict = {}
    for chr_tmp in plot_chr_list:
        add_chr_patch(ax, one_way_transformation(start_point, plot_num_range, plot_size_range), one_way_transformation(
            start_point+chr_tmp.length, plot_num_range, plot_size_range), high=high, x_y_lim=x_y_lim, thickness=thickness, linewidth=linewidth, color=color)
        chr_start_dict[chr_tmp.id] = start_point
        # print(start_point, start_point+chr_tmp.length)
        start_point = start_point+chr_tmp.length + gap_length

    return chr_start_dict, plot_num_range

# two genome synteny compare plot


def add_map_bar(query_range, subject_range, q_h, s_h, curve_deep=1):

    q_s, q_e = query_range
    s_s, s_e = subject_range

    path_data = [
        # q_s curve4
        (Path.MOVETO, [q_s, q_h]),
        (Path.CURVE4, [q_s, q_h - curve_deep]),
        (Path.CURVE4, [s_s, s_h + curve_deep]),
        (Path.CURVE4, [s_s, s_h]),
        # s_line
        (Path.LINETO, [s_e, s_h]),
        # q_e curve4
        (Path.CURVE4, [s_e, s_h + curve_deep]),
        (Path.CURVE4, [q_e, q_h - curve_deep]),
        (Path.CURVE4, [q_e, q_h]),
        # q_e curve4
        (Path.LINETO, [q_s, q_h]),
    ]

    codes, verts = zip(*path_data)
    path = Path(verts, codes)

    patch = Patches.PathPatch(
        path, alpha=0.2, facecolor='black', edgecolor='black', linewidth=0)

    return patch


def add_map_by_fancy_name(q_chr_id, q_s, q_e, s_chr_id, s_s, s_e, strand, query_chr_start_dict, query_plot_range, subject_chr_start_dict, subject_plot_range, plot_size_range, query_high, subject_high, curve_deep=1):

    q_s = min([q_s, q_e])
    q_e = max([q_s, q_e])

    if strand == '-':
        s_s = max([s_s, s_e])
        s_e = min([s_s, s_e])
    else:
        s_s = min([s_s, s_e])
        s_e = max([s_s, s_e])

    q_s = query_chr_start_dict[q_chr_id]+int(q_s)
    q_e = query_chr_start_dict[q_chr_id]+int(q_e)
    s_s = subject_chr_start_dict[s_chr_id]+int(s_s)
    s_e = subject_chr_start_dict[s_chr_id]+int(s_e)

    q_s = one_way_transformation(q_s, query_plot_range, plot_size_range)
    q_e = one_way_transformation(q_e, query_plot_range, plot_size_range)
    s_s = one_way_transformation(s_s, subject_plot_range, plot_size_range)
    s_e = one_way_transformation(s_e, subject_plot_range, plot_size_range)

    map_bar = add_map_bar((q_s, q_e), (s_s, s_e), query_high,
                          subject_high, curve_deep=curve_deep)

    return map_bar


def two_genome_synteny_block_plot(ax, plot_size_range, x_y_lim, query_id, query_contig_list, query_gff_file, query_fasta_file, subject_id, subject_contig_list, subject_gff_file, subject_fasta_file, query_vs_subject_collinearity_csv_file):

    query_chr_dict = build_chr_dict(query_gff_file, query_fasta_file)
    subject_chr_dict = build_chr_dict(subject_gff_file, subject_fasta_file)

    query_chr_start_dict, query_genome_plot_range = plot_genome(
        ax, query_chr_dict, query_plot_chr_id_list, plot_size_range, 8, x_y_lim=x_y_lim, color='b')
    subject_chr_start_dict, subject_genome_plot_range = plot_genome(
        ax, subject_chr_dict, subject_plot_chr_id_list, plot_size_range, 4, x_y_lim=x_y_lim, color='r')

    tmp_info_dict = tsv_file_dict_parse(query_vs_subject_collinearity_csv_file, fieldnames=[
                                        "query_id", "q_chr", "query_from", "query_to", "subject_id", "s_chr", "subject_from", "subject_to", "strand"])
    col_dict = {}
    for i in tmp_info_dict:
        col_dict[i] = {}
        col_dict[i][tmp_info_dict[i]["query_id"]] = (tmp_info_dict[i]["q_chr"], int(
            tmp_info_dict[i]["query_from"]), int(tmp_info_dict[i]["query_to"]))
        col_dict[i][tmp_info_dict[i]["subject_id"]] = (tmp_info_dict[i]["s_chr"], int(
            tmp_info_dict[i]["subject_from"]), int(tmp_info_dict[i]["subject_to"]))
        col_dict[i]['strand'] = tmp_info_dict[i]["strand"]

    for i in col_dict:
        map_bar = add_map_by_fancy_name(col_dict[i][query_id][0], col_dict[i][query_id][1], col_dict[i][query_id][2], col_dict[i][subject_id][0], col_dict[i][subject_id][1], col_dict[i][subject_id][2], col_dict[i][subject_id], query_chr_start_dict,
                                        query_genome_plot_range, subject_chr_start_dict, subject_genome_plot_range, plot_size_range, 8, 4, curve_deep=1)
        ax.add_patch(map_bar)


# genome cover plot
def divide_into_row(plot_chr_id_list, chr_length_dict, base_per_row):
    """
    plot_chr_id_list = ['Chr1','Chr2']
    chr_length_dict = {'Chr1':10000,'Chr2':20000}
    base_per_row = 50000
    """

    row_plot_dict = {}
    row_num = 1
    for chr_id in plot_chr_id_list:
        if len(row_plot_dict) == 0:
            now_row = row_num
            row_plot_dict[now_row] = []
            row_plot_dict[now_row].append(chr_id)
            base_in_row = chr_length_dict[chr_id]
        elif base_in_row + chr_length_dict[chr_id] > base_per_row:
            now_row = now_row + 1
            row_plot_dict[now_row] = []
            row_plot_dict[now_row].append(chr_id)
            base_in_row = chr_length_dict[chr_id]
        else:
            row_plot_dict[now_row].append(chr_id)
            base_in_row += chr_length_dict[chr_id]

    gap_num = 0
    for i in row_plot_dict:
        gap_num += len(row_plot_dict[i]) - 1

    plot_genome_len = sum([chr_length_dict[i] for i in plot_chr_id_list])
    gap_sum_length = plot_genome_len * 0.1
    gap_length = gap_sum_length/gap_num

    chr_site_dict = {}
    row_length_list = []
    for r_id in row_plot_dict:
        start_tmp = 0
        for chr_id in row_plot_dict[r_id]:
            chr_site_dict[chr_id] = (r_id, start_tmp)
            start_tmp += (chr_length_dict[chr_id] + gap_length)
        row_length_list.append(start_tmp - gap_length)

    max_row_length = max(row_length_list)

    return row_plot_dict, chr_site_dict, gap_length, max_row_length


def plot_genome_by_row(ax, row_plot_dict, chr_site_dict, max_row_length, chr_length_dict, plot_size_range, top_row_high, row_spacing, x_y_lim=None, thickness=0.2, linewidth=2, color='b'):

    plot_num_range = (0, max_row_length)

    row_high = top_row_high

    output_dict = {}

    for r_id in row_plot_dict:
        for chr_id in row_plot_dict[r_id]:
            start_point = chr_site_dict[chr_id][1]
            output_dict[chr_id] = ((one_way_transformation(start_point, plot_num_range, plot_size_range), one_way_transformation(
                start_point+chr_length_dict[chr_id], plot_num_range, plot_size_range)), row_high, thickness)
            add_chr_patch(ax, one_way_transformation(start_point, plot_num_range, plot_size_range), one_way_transformation(
                start_point+chr_length_dict[chr_id], plot_num_range, plot_size_range), high=row_high, x_y_lim=x_y_lim, thickness=thickness, linewidth=linewidth, color=color, chr_id=chr_id)

        row_high = row_high - row_spacing

    return output_dict


def add_cover_plot(ax, chr_cover_dict, chr_length):
    for depth in chr_cover_dict:
        for start, end in chr_cover_dict[depth]:
            patch = add_stick_box_plot(start, end, high=depth, thickness=0.2,
                                       linewidth=0, alpha=0.5, facecolor='g', edgecolor='k', bulge=2)
            ax.add_patch(patch)


def genome_cover_plot(plot_chr_id_list, chr_length_dict, base_cover_chr_dict, base_per_row=200000000, row_spacing=3, fig_size=(20, 15), genome_stick_color='b', genome_stick_thickness=0.2, genome_stick_linewidth=2, max_cover_depth=3):
    """
    plot_chr_id_list = ['Chr1','Chr2']
    chr_length_dict = OrderDict({'Chr1':100000,'Chr2':80000})
    base_cover_chr_dict =  {'Chr1': {1: [(30830, 404093), (1896881, 2312291), (3588453, 3734439)], 2:[(1,10000)]}
    base_per_row = 200000000
    row_spacing = 3
    fig_size = (20,15)
    genome_stick_color = 'b'
    genome_stick_thickness = 0.2
    genome_stick_linewidth = 2
    max_cover_depth = 3
    """

    row_plot_dict, chr_site_dict, gap_length, max_row_length = divide_into_row(
        plot_chr_id_list, chr_length_dict, base_per_row)

    # make main axes x,y limit
    row_num = len(row_plot_dict)
    plot_size_range = [10, 110]
    x_y_lim = (
        (plot_size_range[0]-10, plot_size_range[1]+10), (1, (row_num+1)*row_spacing))

    # make fig & ax
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(x_y_lim[0])
    ax.set_ylim(x_y_lim[1])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    chr_plot_dict = plot_genome_by_row(ax, row_plot_dict, chr_site_dict, max_row_length, chr_length_dict, plot_size_range,
                                       x_y_lim[1][1]-row_spacing, row_spacing, x_y_lim=x_y_lim, thickness=genome_stick_thickness, linewidth=genome_stick_linewidth, color=genome_stick_color)

    for chr_id in chr_plot_dict:
        (chr_genome_start,
         chr_genome_end), chr_genome_high, thickness = chr_plot_dict[chr_id]
        chr_ax = add_small_axes_on_other(
            ax, fig, (chr_genome_start, chr_genome_high + thickness), (chr_genome_end, chr_genome_high + thickness + 1.5))
        chr_ax.patch.set_facecolor('none')

        add_cover_plot(
            chr_ax, base_cover_chr_dict[chr_id], chr_length_dict[chr_id])

        chr_ax.set_xlim((1, chr_length_dict[chr_id]))
        chr_ax.set_ylim((0, max_cover_depth+0.5))
        chr_ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1))
        chr_ax.get_xaxis().set_visible(False)
        chr_ax.spines['top'].set_visible(False)
        chr_ax.spines['right'].set_visible(False)
        chr_ax.spines['bottom'].set_visible(False)

        if not chr_genome_start == plot_size_range[0]:
            chr_ax.spines['left'].set_visible(False)
            chr_ax.get_yaxis().set_visible(False)

    plt.show()

# dotplot + cover plot


def add_contig_grid(ax, query_contig_length_dict, subject_contig_length_dict, q_top=None, s_top=None, grid_colors='k', linewidths=0.5, q_contig_list=None, s_contig_list=None):
    query_contig_coord = {}
    subject_contig_coord = {}

    # for query aka y axis h
    q_hline_y_site = []
    q_tick_local = []
    q_tick_label = []
    q_num = 0
    q_top_num = 0

    if q_contig_list is None:
        q_contig_list = list(query_contig_length_dict.keys())

    for i in q_contig_list:
        q_top_num += 1
        if q_top and q_top_num > q_top:
            continue
        if q_top_num == 1:
            top_q_len = query_contig_length_dict[i]
        query_contig_coord[i] = q_num
        q_num += query_contig_length_dict[i]
        q_hline_y_site.append(q_num)
        q_tick_local.append(q_num - query_contig_length_dict[i]/2)
        q_tick_label.append(i)

    q_hline_y_site = q_hline_y_site[:-1]

    ax.hlines(q_hline_y_site, 0, 1, transform=ax.get_yaxis_transform(),
              colors=grid_colors, linewidths=linewidths)

    # for subject aka x axis v
    s_vline_y_site = []
    s_tick_local = []
    s_tick_label = []
    s_num = 0
    s_top_num = 0

    if s_contig_list is None:
        s_contig_list = list(subject_contig_length_dict.keys())

    for i in s_contig_list:
        s_top_num += 1
        if s_top and s_top_num > s_top:
            continue
        if s_top_num == 1:
            top_s_len = subject_contig_length_dict[i]
        subject_contig_coord[i] = s_num
        s_num += subject_contig_length_dict[i]
        s_vline_y_site.append(s_num)
        s_tick_local.append(s_num - subject_contig_length_dict[i]/2)
        s_tick_label.append(i)

    s_vline_y_site = s_vline_y_site[:-1]

    ax.vlines(s_vline_y_site, 0, 1, transform=ax.get_xaxis_transform(),
              colors=grid_colors, linewidths=linewidths)

    ax.invert_yaxis()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.tick_params(axis='both', which='both', bottom=False, top=False,
                   left=False, right=False, labeltop=True, labelleft=True)

    ax.set_xticks(s_tick_local)
    ax.set_xticklabels(s_tick_label)
    ax.set_yticks(q_tick_local)
    ax.set_yticklabels(q_tick_label)

    ax.xaxis.set_tick_params(
        which='major', labelrotation=90, labeltop=True, labelbottom=False)

    x_y_lim = ((0, s_num), (q_num, 0))
    ax.set_xlim(x_y_lim[0])
    ax.set_ylim(x_y_lim[1])

    return query_contig_coord, subject_contig_coord


def add_synteny_dot(ax, query_contig_coord, subject_contig_coord, synteny_block_dict, reverse=False, color='#617a95', linewidth=3):
    for id_tmp in synteny_block_dict:
        sb_tmp = synteny_block_dict[id_tmp]
        strand = sb_tmp.strand
        if not reverse:
            q_id = sb_tmp.q_chr
            s_id = sb_tmp.s_chr
            q_f = sb_tmp.query_from
            q_t = sb_tmp.query_to
            s_f = sb_tmp.subject_from
            s_t = sb_tmp.subject_to
        else:
            q_id = sb_tmp.s_chr
            s_id = sb_tmp.q_chr
            q_f = sb_tmp.subject_from
            q_t = sb_tmp.subject_to
            s_f = sb_tmp.query_from
            s_t = sb_tmp.query_to

        if q_id not in query_contig_coord or s_id not in subject_contig_coord:
            continue

        q_f = query_contig_coord[q_id] + q_f
        q_t = query_contig_coord[q_id] + q_t

        s_f = subject_contig_coord[s_id] + s_f
        s_t = subject_contig_coord[s_id] + s_t

        if strand == '+':
            ax.plot((s_f, s_t), (q_f, q_t), color, linewidth=linewidth)
        else:
            ax.plot((s_t, s_f), (q_f, q_t), color, linewidth=linewidth)


def small_cover_plot(ax, orientation, base_cover_chr_dict, contig_coord, max_cover_depth=5, facecolor='r'):

    rectangle_list = []
    for chr_id in base_cover_chr_dict:
        for depth in base_cover_chr_dict[chr_id]:
            for s, e in base_cover_chr_dict[chr_id][depth]:
                if chr_id not in contig_coord:
                    continue
                contig_coord_base = contig_coord[chr_id]
                ps, pe = s+contig_coord_base, e+contig_coord_base
                if orientation == 'h':
                    rect = Patches.Rectangle((ps, 0), pe-ps, depth)
                elif orientation == 'v':
                    rect = Patches.Rectangle((0, ps), depth, pe-ps)
                rectangle_list.append(rect)

    pc = PatchCollection(rectangle_list, facecolor=facecolor, edgecolor='None')
    ax.add_collection(pc)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if orientation == 'h':
        ax.set_ylim((0, max_cover_depth+0.5))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1))
        ax.get_xaxis().set_visible(False)

    elif orientation == 'v':
        ax.set_xlim((0, max_cover_depth+0.5))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
        ax.get_yaxis().set_visible(False)


def synteny_dotplot(query_id, subject_id, synteny_block_dict, q_range_base_cover_chr_dict, s_range_base_cover_chr_dict, query_genome_fasta, subject_genome_fasta, q_top=None, s_top=None, reverse=False, max_cover_depth=4, save_file=None, q_contig_list=None, s_contig_list=None):
    # parameter
    fig_size = (20, 20)

    # chr length
    query_fasta_dict = read_fasta_by_faidx(query_genome_fasta)
    query_contig_length_dict = OrderedDict()
    for i in sorted(list(query_fasta_dict.keys()), key=lambda x: query_fasta_dict[x].len(), reverse=True):
        query_contig_length_dict[i] = query_fasta_dict[i].len()

    subject_fasta_dict = read_fasta_by_faidx(subject_genome_fasta)
    subject_contig_length_dict = OrderedDict()
    for i in sorted(list(subject_fasta_dict.keys()), key=lambda x: subject_fasta_dict[x].len(), reverse=True):
        subject_contig_length_dict[i] = subject_fasta_dict[i].len()

    # make fig & ax
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    spacing = 0.02
    cover_plot_height = 0.04

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom - cover_plot_height -
                  spacing, width, cover_plot_height]
    rect_histy = [left + width + spacing*1.5,
                  bottom, cover_plot_height, height]

    fig = plt.figure(figsize=fig_size)

    ax = fig.add_axes(rect_scatter)
    ax_histx = fig.add_axes(rect_histx, sharex=ax)
    ax_histy = fig.add_axes(rect_histy, sharey=ax)

    query_contig_coord, subject_contig_coord = add_contig_grid(
        ax, query_contig_length_dict, subject_contig_length_dict, q_top, s_top, q_contig_list=q_contig_list, s_contig_list=s_contig_list)
    add_synteny_dot(ax, query_contig_coord, subject_contig_coord,
                    synteny_block_dict, reverse=reverse)

    small_cover_plot(ax_histx, 'h', s_range_base_cover_chr_dict,
                     subject_contig_coord, max_cover_depth=max_cover_depth)
    # ax_histx.set_title(query_id,fontsize=20)
    small_cover_plot(ax_histy, 'v', q_range_base_cover_chr_dict,
                     query_contig_coord, max_cover_depth=max_cover_depth)
    # ax_histy.set_ylabel(subject_id,fontsize=20)

    ax.set_xlabel(subject_id, fontsize=20)
    ax.xaxis.set_label_position('bottom')
    ax.xaxis.set_label_coords(0.5, -0.01)
    ax.set_ylabel(query_id, fontsize=20)
    ax.yaxis.set_label_position('right')
    ax.yaxis.set_label_coords(1.01, 0.5)

    plt.show()

    if save_file:
        fig.savefig(save_file, format='pdf', facecolor='none',
                    edgecolor='none', bbox_inches='tight')


# cover stat plot
def cover_stat_plot(speci_list, pair_dict):
    fig = plt.figure(figsize=(20, 20))

    num = 1
    for i in speci_list:
        for j in speci_list:

            ax = fig.add_subplot(len(speci_list), len(speci_list), num)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
            ax.set_xlim(0, 7)
            ax.set_ylim(0, 1)

            if not num % len(speci_list) == 1 and num != 2:
                labels = [item.get_text() for item in ax.get_yticklabels()]

                empty_string_labels = ['']*len(labels)
                ax.set_yticklabels(empty_string_labels)

            if num < len(speci_list)*(len(speci_list)-1):
                labels = [item.get_text() for item in ax.get_xticklabels()]

                empty_string_labels = ['']*len(labels)
                ax.set_xticklabels(empty_string_labels)

            if i == j:
                text = ax.text(3.5, 0.5, i, ha='center', va='center', size=20)
                text.set_path_effects([path_effects.Normal()])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                num += 1
                continue
            else:
                sp_pair = (i, j)
                sp_pair_r = (j, i)
                if sp_pair in pair_dict:
                    q_no_zero_sum_ratio, q_no_zero_ratio, s_no_zero_sum_ratio, s_no_zero_ratio = pair_dict[
                        sp_pair]['gene_cover_stat']
                    plot_no_zero_sum_ratio, plot_no_zero_ratio = s_no_zero_sum_ratio, s_no_zero_ratio
                else:
                    q_no_zero_sum_ratio, q_no_zero_ratio, s_no_zero_sum_ratio, s_no_zero_ratio = pair_dict[
                        sp_pair_r]['gene_cover_stat']
                    plot_no_zero_sum_ratio, plot_no_zero_ratio = q_no_zero_sum_ratio, q_no_zero_ratio

                text = ax.text(4.5, 0.85, "%.2f%%" %
                               (plot_no_zero_sum_ratio*100), size=12)
                ax.bar(list(range(1, len(plot_no_zero_ratio)+1)),
                       plot_no_zero_ratio)
                num += 1

    plt.show()


if __name__ == "__main__":

    # make a big synteny compare between two genome

    query_id = 'Gel'
    query_contig_list_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.chr.id'
    query_gff_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.gff3'
    query_fasta_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta'

    subject_id = 'Aof'
    subject_contig_list_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Aof.chr.id'
    subject_gff_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Aof.gff3'
    subject_fasta_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Asparagus_officinalis/T4686N0.genome.fasta'

    query_vs_subject_collinearity_csv_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Aof_vs_Gel_h/mcscanx.collinearity.csv'

    query_plot_chr_id_list = read_list_file(query_contig_list_file)
    subject_plot_chr_id_list = read_list_file(subject_contig_list_file)

    plot_size_range = [10, 110]
    x_y_lim = ((plot_size_range[0]-10, plot_size_range[1]+10), (1, 10))

    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(1, 1, 1)

    two_genome_synteny_block_plot(ax, plot_size_range, x_y_lim, query_id, query_plot_chr_id_list, query_gff_file, query_fasta_file,
                                  subject_id, subject_plot_chr_id_list, subject_gff_file, subject_fasta_file, query_vs_subject_collinearity_csv_file)

    ax.set_xlim(x_y_lim[0])
    ax.set_ylim(x_y_lim[1])

    plt.show()

    # plot WGD synteny genome cover
    from toolbiox.api.xuyuxing.comp_genome.mcscan import WGD_check_pipeline

    query_species = 'Ash'
    query_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Ash.gff3'
    query_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Apostasia_shenzhenica/T1088818N0.genome.fasta'
    subject_species = 'Gel'
    subject_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.gff3'
    subject_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta'
    mcscanx_collinearity_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Ash_vs_Gel_h/mcscanx.collinearity'

    q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = WGD_check_pipeline(
        mcscanx_collinearity_file, query_species, query_gff3, query_genome_fasta, subject_species, subject_gff3, subject_genome_fasta)

    sp_id = 'Gel'
    contig_list_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.chr.id'
    genome_fasta_file = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta'

    plot_chr_id_list = read_list_file(contig_list_file)
    fasta_dict = read_fasta_by_faidx(genome_fasta_file)
    chr_length_dict = {i: fasta_dict[i].len() for i in fasta_dict}

    genome_cover_plot(plot_chr_id_list, chr_length_dict,
                      s_range_base_cover_chr_dict)

    # plot dotplot
    from toolbiox.api.xuyuxing.comp_genome.mcscan import WGD_check_pipeline

    query_species = 'Ash'
    query_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Ash.gff3'
    query_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Apostasia_shenzhenica/T1088818N0.genome.fasta'
    subject_species = 'Gel'
    subject_gff3 = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Gel.gff3'
    subject_genome_fasta = '/lustre/home/xuyuxing/Database/Plant_genome/clean_data/Gastrodia_elata/Gel.genome.v2.0.fasta'
    mcscanx_collinearity_file = '/lustre/home/xuyuxing/Work/Gel/synteny/redo_big/Ash_vs_Gel_h/mcscanx.collinearity'

    q_gene_covered_dict, q_range_loci_cover_chr_dict, q_range_base_cover_chr_dict, s_gene_covered_dict, s_range_loci_cover_chr_dict, s_range_base_cover_chr_dict, synteny_block_dict = WGD_check_pipeline(
        mcscanx_collinearity_file, query_species, query_gff3, query_genome_fasta, subject_species, subject_gff3, subject_genome_fasta)

    synteny_dotplot('Ash', 'Gel', synteny_block_dict, q_range_base_cover_chr_dict, s_range_base_cover_chr_dict,
                    query_genome_fasta, subject_genome_fasta, q_top=200, s_top=18, reverse=False, max_cover_depth=4)
