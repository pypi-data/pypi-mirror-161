import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import numpy as np
import math
from collections import OrderedDict
from toolbiox.lib.common.genome.genome_feature2 import read_gff_file
from interlap import InterLap
from toolbiox.lib.common.math.bin_and_window import split_sequence_to_bins
from toolbiox.lib.common.genome.seq_base import read_fasta_by_faidx
from toolbiox.lib.common.math.interval import merge_intervals, sum_interval_length


class CirclePlot(object):
    def __init__(self, **kwargs):
        # set default parameter
        self.chr_dict = OrderedDict()

        # figure parameter
        self.init_figure_parameter = {
            "figure_size": (20, 20),
            "zero_location": "E",
            "ylim": (0, 5000),
            "direction": -1,
            "zero_location_gap": (2*math.pi/365)*15,
            "interspace_ratio": 0.1,
            "show_polar_axis": False,
        }

        for k in kwargs:
            if k in self.init_figure_parameter:
                self.init_figure_parameter[k] = kwargs[k]

        # build figure and axes
        self.figure = plt.figure(
            figsize=self.init_figure_parameter["figure_size"])
        self.ax = plt.subplot(111, polar=True)
        self.ax.set_theta_zero_location(
            self.init_figure_parameter["zero_location"])
        self.ax.set_theta_direction(self.init_figure_parameter["direction"])
        self.ax.set_ylim(*self.init_figure_parameter["ylim"])

        if not self.init_figure_parameter["show_polar_axis"]:
            # remove polar axis
            self.ax.spines['polar'].set_visible(False)
            self.ax.xaxis.set_ticks([])
            self.ax.xaxis.set_ticklabels([])
            self.ax.yaxis.set_ticks([])
            self.ax.yaxis.set_ticklabels([])

    def load_chr_info(self, chr_id, length, **kwargs):
        self.chr_dict[chr_id] = {}
        self.chr_dict[chr_id]["length"] = length
        self.chr_dict[chr_id]["features"] = []

        for k in ["bottom", "height", "facecolor", "edgecolor", "linewidth"]:
            if k in kwargs:
                self.chr_dict[chr_id][k] = kwargs[k]
            else:
                self.chr_dict[chr_id][k] = None

        self.sum_chr_length = sum([self.chr_dict[i]["length"]
                                   for i in self.chr_dict])
        sum_interspace = self.sum_chr_length * \
            self.init_figure_parameter["interspace_ratio"]
        self.interspace_num = len(self.chr_dict)
        self.interspace_length = sum_interspace/self.interspace_num
        sum_length = self.sum_chr_length + sum_interspace

        sum_theta = 2*math.pi - self.init_figure_parameter["zero_location_gap"]
        self.the_vs_len = sum_theta/sum_length
        self.interspace_theta = self.interspace_length * self.the_vs_len
        self.theta_start = (
            self.init_figure_parameter["zero_location_gap"] + self.interspace_theta) / 2

        tmp_start = self.theta_start
        for chr_id in self.chr_dict:
            theta_s = tmp_start
            theta_e = theta_s + \
                self.chr_dict[chr_id]['length'] * self.the_vs_len
            self.chr_dict[chr_id]['theta'] = (theta_s, theta_e)
            self.chr_dict[chr_id]['theta_length'] = theta_e - theta_s
            tmp_start = theta_e + self.interspace_theta

    def chr_site_to_theta(self, chr_id, site):
        chr_theta_start = self.chr_dict[chr_id]['theta'][0]
        return chr_theta_start + site * self.the_vs_len

    def chrs_plot(self, **kwargs):
        # parameter
        # default parameter

        chr_box_parameter = {
            "bottom": 3500,
            "height": 250,
            "facecolor": "none",
            "edgecolor": "#000000",
            "linewidth": 1.0,
            "ticker": True,
            "ticker_base": 10000000,
            "ticker_length": 10,
            "ticker_label": True,
            "ticker_label_length": 100,
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in chr_box_parameter:
                chr_box_parameter[k] = kwargs[k]

        # add chr box
        for chr_id in self.chr_dict:
            pos = self.chr_dict[chr_id]["theta"][0]
            width = self.chr_dict[chr_id]["theta_length"]

            if self.chr_dict[chr_id]["height"] is None:
                height = chr_box_parameter["height"]
            else:
                height = self.chr_dict[chr_id]["height"]

            if self.chr_dict[chr_id]["bottom"] is None:
                bottom = chr_box_parameter["bottom"]
            else:
                bottom = self.chr_dict[chr_id]["bottom"]

            if self.chr_dict[chr_id]["facecolor"] is None:
                facecolor = chr_box_parameter["facecolor"]
            else:
                facecolor = self.chr_dict[chr_id]["facecolor"]

            if self.chr_dict[chr_id]["edgecolor"] is None:
                edgecolor = chr_box_parameter["edgecolor"]
            else:
                edgecolor = self.chr_dict[chr_id]["edgecolor"]

            if self.chr_dict[chr_id]["linewidth"] is None:
                linewidth = chr_box_parameter["linewidth"]
            else:
                linewidth = self.chr_dict[chr_id]["linewidth"]

            self.chr_dict[chr_id]["bar"] = self.ax.bar(
                [pos], [height], bottom=bottom, width=width, facecolor=facecolor, linewidth=linewidth, edgecolor=edgecolor, align="edge")

        # add chr tick and tick label
        for chr_id in self.chr_dict:
            chr_theta_start = self.chr_dict[chr_id]["theta"][0]
            length = self.chr_dict[chr_id]["length"]

            if self.chr_dict[chr_id]["height"] is None:
                height = chr_box_parameter["height"]
            else:
                height = self.chr_dict[chr_id]["height"]

            if self.chr_dict[chr_id]["bottom"] is None:
                bottom = chr_box_parameter["bottom"]
            else:
                bottom = self.chr_dict[chr_id]["bottom"]

            if self.chr_dict[chr_id]["linewidth"] is None:
                linewidth = chr_box_parameter["linewidth"]
            else:
                linewidth = self.chr_dict[chr_id]["linewidth"]

            tick_theta_positions_list = []
            for i in range(int(length/chr_box_parameter["ticker_base"])+1):
                tick_theta_positions_list.append(
                    chr_theta_start + i * chr_box_parameter["ticker_base"] * self.the_vs_len)

            # add tick
            tick_bottom = bottom + height
            if chr_box_parameter["ticker"]:
                for tick_theta in tick_theta_positions_list:
                    self.ax.plot([tick_theta, tick_theta], [
                        tick_bottom, tick_bottom+chr_box_parameter["ticker_length"]], color="k", linewidth=linewidth)

            # add tick label
            if chr_box_parameter["ticker_label"]:
                tick_label_bottom = tick_bottom + \
                    chr_box_parameter["ticker_length"] + \
                    chr_box_parameter["ticker_label_length"]
                num = 0
                for tick_theta in tick_theta_positions_list:
                    label_text = str(int(num / 1000000))

                    if tick_theta <= math.pi:
                        lab = self.ax.text(tick_theta, tick_label_bottom, label_text, ha='center',
                                        va='center', rotation=np.rad2deg(2*math.pi - (tick_theta - 0.5*math.pi)))
                    else:
                        lab = self.ax.text(tick_theta, tick_label_bottom, label_text, ha='center',
                                        va='center', rotation=np.rad2deg(math.pi - (tick_theta - 0.5*math.pi)))

                    num += chr_box_parameter["ticker_base"]

    def add_chrs_name(self, bottom, **kwargs):
        chrs_name_parameter = {
            "fontsize": "xx-large",
            "color": "#000000",
            "family": 'Arial Unicode MS'
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in chrs_name_parameter:
                chrs_name_parameter[k] = kwargs[k]

        for chr_id in self.chr_dict:
            chrs_name_theta = (self.chr_dict[chr_id]["theta"][1] - self.chr_dict[chr_id]
                               ["theta"][0]) / 2 + self.chr_dict[chr_id]["theta"][0]

            if self.init_figure_parameter["zero_location"] == 'E':
                rotation_now=np.rad2deg(math.pi - (chrs_name_theta - 0.5*math.pi))
            if self.init_figure_parameter["zero_location"] == 'N':
                rotation_now=np.rad2deg(math.pi - (chrs_name_theta - math.pi))
            if self.init_figure_parameter["zero_location"] == 'S':
                rotation_now=np.rad2deg(math.pi - (chrs_name_theta - 1.5*math.pi))
            if self.init_figure_parameter["zero_location"] == 'w':
                rotation_now=np.rad2deg(math.pi - (chrs_name_theta - 0*math.pi))

            lab = self.ax.text(chrs_name_theta, bottom, chr_id, ha='center',
                            va='center', rotation=rotation_now, fontsize=chrs_name_parameter['fontsize'], color=chrs_name_parameter['color'], family=chrs_name_parameter['family'])

    def heatmap_plot(self, data, bin_length, bottom, height, min_plot=None, max_plot=None, cmap=None):
        """
        data = {
            'Chr1' : {0:100,1:20}
            }
        }
        0,1 is index for bins, and 100,20 is value to plot

        should load_chr_info firstly
        """
        bar_width = bin_length * self.the_vs_len

        num_list = []
        for i in data:
            for j in data[i]:
                num_list.append(data[i][j])

        if max_plot:
            max_value = max_plot
        else:
            max_value = max(num_list)

        if min_plot:
            min_value = min_plot
        else:
            min_value = min(num_list)

        for chr_id in self.chr_dict:
            theta = self.chr_dict[chr_id]['theta']
            chr_length = self.chr_dict[chr_id]['length']
            bar_start = []
            theta_start = theta[0]
            for i, s, e in split_sequence_to_bins(chr_length, bin_length, 1):
                bar_start.append(theta_start)
                theta_start += bar_width
            bars = self.ax.bar(bar_start, height=[
                               height] * len(bar_start), bottom=bottom, align="edge", width=bar_width)

            for i, bar in enumerate(bars):
                if i in data[chr_id]:
                    value = data[chr_id][i]
                else:
                    value = min_value

                if value >= max_value:
                    value = max_value
                elif value <= min_value:
                    value = min_value

                bar.set_facecolor(cmap(value/(max_value - min_value)))
                bar.set_linewidth(0.0)

    def line_plot(self, data, bin_length, bottom, height, **kwargs):
        """
        y_axis is a function
        such as:
        y_axis = lambda x:"%.0f%%" % (x * 100)
        """

        line_plot_para = {
            "min_plot": None,
            "max_plot": None,
            "linewidth": 0.5,
            "edgecolor": "k",
            "facecolor": "#5b7281",
            "centripetal": False,
            "fill": True,
            "y_axis": None,
            "axis_linewidth": 1,
            "axis_color": "k",
            "axis_ticker_num": 5,
            "ticker_length": (2*math.pi/365)*0.5,
            "ticker_label_adjust": 5
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in line_plot_para:
                line_plot_para[k] = kwargs[k]

        bar_width = bin_length * self.the_vs_len

        num_list = []
        for i in data:
            for j in data[i]:
                num_list.append(data[i][j])

        if line_plot_para["max_plot"]:
            max_value = line_plot_para["max_plot"]
        else:
            max_value = max(num_list)

        if line_plot_para["min_plot"]:
            min_value = line_plot_para["min_plot"]
        else:
            min_value = min(num_list)

        he_vs_val = height / abs(max_value - min_value)

        for chr_id in self.chr_dict:
            theta = self.chr_dict[chr_id]['theta']
            chr_length = self.chr_dict[chr_id]['length']

            position_list = []
            value_list = []

            theta_start = theta[0]
            for i, s, e in split_sequence_to_bins(chr_length, bin_length, 1):
                position_list.append(theta_start)

                if i in data[chr_id]:
                    value = data[chr_id][i]
                else:
                    value = min_value

                if value >= max_value:
                    value = max_value

                elif value <= min_value:
                    value = min_value

                if line_plot_para["centripetal"]:
                    plot_value = bottom - (value - min_value) * he_vs_val
                else:
                    plot_value = bottom + (value - min_value) * he_vs_val

                value_list.append(plot_value)

                theta_start += bar_width

            if line_plot_para["fill"] == False:
                self.ax.plot(position_list, value_list,
                             color=line_plot_para["edgecolor"], linewidth=line_plot_para["linewidth"])

            elif line_plot_para["fill"] == True:
                if bottom >= 0:
                    self.ax.fill_between(position_list, value_list, bottom,
                                         facecolor=line_plot_para["facecolor"], linewidth=line_plot_para["linewidth"], edgecolor=line_plot_para["edgecolor"])

        # add y-axis
        if line_plot_para["y_axis"]:
            y_axis_theta = self.chr_dict[list(
                self.chr_dict.keys())[0]]['theta'][0] - (2*math.pi/365)*0.5

            # add spine
            spine_start = bottom
            if line_plot_para["centripetal"]:
                spine_end = bottom - height
            else:
                spine_end = bottom + height

            self.ax.plot([y_axis_theta, y_axis_theta], [
                         spine_start, spine_end], color="k", linewidth=line_plot_para["axis_linewidth"])

            # add tick
            tick_height_list = [spine_start, spine_end]
            for i in range(line_plot_para["axis_ticker_num"]):
                tick_height_list.append(
                    spine_start + i * (spine_end - spine_start) / line_plot_para["axis_ticker_num"])

            for tick_theta in tick_height_list:
                self.ax.plot([y_axis_theta, y_axis_theta - line_plot_para["ticker_length"]], [
                    tick_theta, tick_theta], color="k", linewidth=line_plot_para["axis_linewidth"])

            # add tick label
            tick_label_theta = y_axis_theta - \
                line_plot_para["ticker_label_adjust"] * \
                line_plot_para["ticker_length"]
            for tick_label_height, tick_label_value in [(spine_start, min_value), (spine_end, max_value)]:

                lab = self.ax.text(tick_label_theta, tick_label_height, line_plot_para["y_axis"](tick_label_value), ha='center',
                                   va='center', rotation=np.rad2deg(2*math.pi - (tick_label_theta - 0.5*math.pi)))

    def bar_plot(self, data, bin_length, bottom, height, **kwargs):
        """
        y_axis is a function
        such as:
        y_axis = lambda x:"%.0f%%" % (x * 100)
        """

        bar_plot_para = {
            "min_plot": None,
            "max_plot": None,
            "linewidth": 0.0,
            "edgecolor": "k",
            "facecolor": "#5b7281",
            "centripetal": False,
            "y_axis": None,
            "axis_linewidth": 1,
            "axis_color": "k",
            "axis_ticker_num": 5,
            "ticker_length": (2*math.pi/365)*0.5,
            "ticker_label_adjust": 5
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in bar_plot_para:
                bar_plot_para[k] = kwargs[k]

        bar_width = bin_length * self.the_vs_len

        num_list = []
        for i in data:
            for j in data[i]:
                num_list.append(data[i][j])

        if bar_plot_para["max_plot"]:
            max_value = bar_plot_para["max_plot"]
        else:
            max_value = max(num_list)

        if bar_plot_para["min_plot"]:
            min_value = bar_plot_para["min_plot"]
        else:
            min_value = min(num_list)

        he_vs_val = height / abs(max_value - min_value)

        for chr_id in self.chr_dict:
            theta = self.chr_dict[chr_id]['theta']
            chr_length = self.chr_dict[chr_id]['length']

            position_list = []
            value_list = []

            theta_start = theta[0]
            for i, s, e in split_sequence_to_bins(chr_length, bin_length, 1):
                position_list.append(theta_start)

                if i in data[chr_id]:
                    value = data[chr_id][i]
                else:
                    value = min_value

                if value >= max_value:
                    value = max_value

                elif value <= min_value:
                    value = min_value

                if bar_plot_para["centripetal"]:
                    plot_value = - (value - min_value) * he_vs_val
                else:
                    plot_value = + (value - min_value) * he_vs_val

                value_list.append(plot_value)

                theta_start += bar_width

            self.ax.bar(position_list, value_list, bottom=bottom, width=[bar_width] * len(position_list),
                        facecolor=bar_plot_para["facecolor"], linewidth=bar_plot_para["linewidth"], edgecolor=bar_plot_para["edgecolor"])

        # add y-axis
        if bar_plot_para["y_axis"]:
            y_axis_theta = self.chr_dict[list(
                self.chr_dict.keys())[0]]['theta'][0] - (2*math.pi/365)*0.5

            # add spine
            spine_start = bottom
            if bar_plot_para["centripetal"]:
                spine_end = bottom - height
            else:
                spine_end = bottom + height

            self.ax.plot([y_axis_theta, y_axis_theta], [
                         spine_start, spine_end], color="k", linewidth=bar_plot_para["axis_linewidth"])

            # add tick
            tick_height_list = [spine_start, spine_end]
            for i in range(bar_plot_para["axis_ticker_num"]):
                tick_height_list.append(
                    spine_start + i * (spine_end - spine_start) / bar_plot_para["axis_ticker_num"])

            for tick_theta in tick_height_list:
                self.ax.plot([y_axis_theta, y_axis_theta - bar_plot_para["ticker_length"]], [
                    tick_theta, tick_theta], color="k", linewidth=bar_plot_para["axis_linewidth"])

            # add tick label
            tick_label_theta = y_axis_theta - \
                bar_plot_para["ticker_label_adjust"] * \
                bar_plot_para["ticker_length"]
            for tick_label_height, tick_label_value in [(spine_start, min_value), (spine_end, max_value)]:

                lab = self.ax.text(tick_label_theta, tick_label_height, bar_plot_para["y_axis"](tick_label_value), ha='center',
                                   va='center', rotation=np.rad2deg(2*math.pi - (tick_label_theta - 0.5*math.pi)))

    def link_plot(self, start, end, bottom, **kwargs):
        """
        start = ('Chr1', 1000000, 2000000)
        end = ('Chr2', 5000000, 7000000)
        bottom = 1000
        """

        link_plot_para = {
            "bottom": bottom,
            "facecolor": "#5b7281",
            "linewidth": 0.0,
            "edgecolor": "k",
            "alpha": 0.5,
            "center": 0,
            "end_bottom": None,
        }

        for k in kwargs:
            if k in link_plot_para:
                link_plot_para[k] = kwargs[k]

        ss = self.chr_site_to_theta(start[0], start[1])
        se = self.chr_site_to_theta(start[0], start[2])
        stop = bottom

        es = self.chr_site_to_theta(end[0], end[1])
        ee = self.chr_site_to_theta(end[0], end[2])
        etop = bottom

        z1 = stop - stop * math.cos(abs((se-ss) * 0.5))
        z2 = etop - etop * math.cos(abs((ee-es) * 0.5))

        Path = mpath.Path

        path_data = [(Path.MOVETO,  (ss, bottom)),
                     (Path.CURVE3,  (ss, link_plot_para['center'])),
                     (Path.CURVE3,  (ee,   etop)),
                     (Path.CURVE3,  ((es+ee)*0.5, etop+z2)),
                     (Path.CURVE3,  (es, etop)),
                     (Path.CURVE3,  (es, link_plot_para['center'])),
                     (Path.CURVE3,  (se,   bottom)),
                     (Path.CURVE3,  ((ss+se)*0.5, bottom+z1)),
                     (Path.CURVE3,  (ss, bottom)),
                     ]
        codes, verts = list(zip(*path_data))
        path = mpath.Path(verts, codes)
        patch = mpatches.PathPatch(
            path, facecolor=link_plot_para['facecolor'], alpha=link_plot_para['alpha'], linewidth=link_plot_para['linewidth'], zorder=0)
        self.ax.add_patch(patch)

    def synteny_plot(self, data, bottom, **kwargs):
        """
        data = [("Chr1", 1, 1000, "Chr2", 2000, 3000), ("Chr4", 1, 1000, "Chr7", 3000, 2000)]
        """

        synteny_plot_para = {
            "bottom": bottom,
            "facecolor": None,
            "cmap": None,
            "liner_camp": False,
            "alpha": 0.5,
            "center": 0,
        }

        for k in kwargs:
            if k in synteny_plot_para:
                synteny_plot_para[k] = kwargs[k]

        data = dict(enumerate(data))

        chr_list = list(self.chr_dict.keys())

        chr_sb_dict = {}
        used_id = []
        for chr_id in chr_list:
            chr_sb_dict[chr_id] = []

            for i in data:
                q_c, q_s, q_e, s_c, s_s, s_e = data[i]
                if (q_c == chr_id or s_c == chr_id) and i not in set(used_id):
                    chr_sb_dict[chr_id].append(i)
                    used_id.append(i)

        # plot
        if synteny_plot_para["cmap"]:

            cmap = synteny_plot_para["cmap"]
            color_num = len(
                [i for i in chr_sb_dict if len(chr_sb_dict[i]) > 0])
            color_list = np.linspace(0.0, 1.0, color_num, endpoint=True)

            num = -1
            for chr_id in chr_list:
                if len(chr_sb_dict[chr_id]) > 0:
                    num += 1
                    for i in chr_sb_dict[chr_id]:
                        j = data[i]
                        q_c, s_c = j[0], j[3]
                        if q_c not in self.chr_dict or s_c not in self.chr_dict:
                            continue

                        if not synteny_plot_para['liner_camp']:
                            if hasattr(cmap, 'colors'):
                                cmap_num = len(cmap.colors)
                                self.link_plot(j[0:3], j[3:6], bottom, facecolor=cmap(
                                    (num) % cmap_num), alpha=synteny_plot_para['alpha'])
                            else:
                                self.link_plot(j[0:3], j[3:6], bottom, facecolor=cmap(
                                    num), alpha=synteny_plot_para['alpha'])
                        else:
                            self.link_plot(j[0:3], j[3:6], bottom, facecolor=cmap(
                                color_list[num]), alpha=synteny_plot_para['alpha'])

        elif synteny_plot_para["facecolor"]:
            for i in data:
                j = data[i]
                q_c, s_c = j[0], j[3]
                if q_c not in self.chr_dict or s_c not in self.chr_dict:
                    continue
                self.link_plot(
                    j[0:3], j[3:6], bottom, facecolor=synteny_plot_para["facecolor"], alpha=synteny_plot_para['alpha'])

    def scatter_plot(self, data, bin_length, bottom, height, **kwargs):
        """
        y_axis is a function
        such as:
        y_axis = lambda x:"%.0f%%" % (x * 100)
        """

        scatter_plot_para = {
            "min_plot": None,
            "max_plot": None,
            "linewidth": 0.5,
            "edgecolor": "k",
            "facecolor": "#5b7281",
            "centripetal": False,
            "markersize": 1,
            "y_axis": None,
            "axis_linewidth": 1,
            "axis_color": "k",
            "axis_ticker_num": 5,
            "ticker_length": (2*math.pi/365)*0.5,
            "ticker_label_adjust": 5
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in scatter_plot_para:
                scatter_plot_para[k] = kwargs[k]

        bar_width = bin_length * self.the_vs_len

        num_list = []
        for i in data:
            for j in data[i]:
                num_list.append(data[i][j])

        if scatter_plot_para["max_plot"]:
            max_value = scatter_plot_para["max_plot"]
        else:
            max_value = max(num_list)

        if scatter_plot_para["min_plot"]:
            min_value = scatter_plot_para["min_plot"]
        else:
            min_value = min(num_list)

        he_vs_val = height / abs(max_value - min_value)

        for chr_id in self.chr_dict:
            theta = self.chr_dict[chr_id]['theta']
            chr_length = self.chr_dict[chr_id]['length']

            position_list = []
            value_list = []

            theta_start = theta[0]
            for i, s, e in split_sequence_to_bins(chr_length, bin_length, 1):
                position_list.append(theta_start)

                if i in data[chr_id]:
                    value = data[chr_id][i]
                else:
                    value = min_value

                if value >= max_value:
                    value = max_value

                elif value <= min_value:
                    value = min_value

                if scatter_plot_para["centripetal"]:
                    plot_value = bottom - (value - min_value) * he_vs_val
                else:
                    plot_value = bottom + (value - min_value) * he_vs_val

                value_list.append(plot_value)

                theta_start += bar_width

            self.ax.scatter(position_list, value_list, s=scatter_plot_para["markersize"], c=scatter_plot_para[
                            "facecolor"], linewidth=scatter_plot_para["linewidth"], edgecolor=scatter_plot_para["edgecolor"])

        # add y-axis
        if scatter_plot_para["y_axis"]:
            y_axis_theta = self.chr_dict[list(
                self.chr_dict.keys())[0]]['theta'][0] - (2*math.pi/365)*0.5

            # add spine
            spine_start = bottom
            if scatter_plot_para["centripetal"]:
                spine_end = bottom - height
            else:
                spine_end = bottom + height

            self.ax.plot([y_axis_theta, y_axis_theta], [
                         spine_start, spine_end], color="k", linewidth=scatter_plot_para["axis_linewidth"])

            # add tick
            tick_height_list = [spine_start, spine_end]
            for i in range(scatter_plot_para["axis_ticker_num"]):
                tick_height_list.append(
                    spine_start + i * (spine_end - spine_start) / scatter_plot_para["axis_ticker_num"])

            for tick_theta in tick_height_list:
                self.ax.plot([y_axis_theta, y_axis_theta - scatter_plot_para["ticker_length"]], [
                    tick_theta, tick_theta], color="k", linewidth=scatter_plot_para["axis_linewidth"])

            # add tick label
            tick_label_theta = y_axis_theta - \
                scatter_plot_para["ticker_label_adjust"] * \
                scatter_plot_para["ticker_length"]
            for tick_label_height, tick_label_value in [(spine_start, min_value), (spine_end, max_value)]:

                lab = self.ax.text(tick_label_theta, tick_label_height, scatter_plot_para["y_axis"](tick_label_value), ha='center',
                                   va='center', rotation=np.rad2deg(2*math.pi - (tick_label_theta - 0.5*math.pi)))

    def add_box(self, chr_loci_list, bottom, height, **kwargs):
        # parameter
        # default parameter

        box_parameter = {
            "bottom": bottom,
            "height": height,
            "facecolor": "none",
            "edgecolor": "#000000",
            "linewidth": 1.0,
        }

        # overwrite by given parameter
        for k in kwargs:
            if k in box_parameter:
                box_parameter[k] = kwargs[k]

        # add chr box
        for chr_loci in chr_loci_list:

            pos = self.chr_site_to_theta(chr_loci.chr_id, chr_loci.start)
            width = (chr_loci.end - chr_loci.start) * self.the_vs_len

            height = box_parameter["height"]
            bottom = box_parameter["bottom"]
            facecolor = box_parameter["facecolor"]
            edgecolor = box_parameter["edgecolor"]
            linewidth = box_parameter["linewidth"]

            self.ax.bar([pos], [height], bottom=bottom, width=width, facecolor=facecolor,
                        linewidth=linewidth, edgecolor=edgecolor, align="edge")

    def save(self, file_name="test", format="pdf", dpi=None):
        self.figure.patch.set_alpha(0.0)
        if format == "pdf":
            self.figure.savefig(file_name + ".pdf", bbox_inches="tight")
        elif format == "svg":
            self.figure.savefig(file_name + ".svg", format='svg', facecolor='none', edgecolor='none')
        else:
            if dpi is None:
                dpi = 600
            self.figure.savefig(file_name + "." + format,
                                bbox_inches="tight", dpi=dpi)
        return self.figure


def get_gene_density(gff_file, top_gene_feature, bin_length=1000000, print_stat=False):
    gff_dict = read_gff_file(gff_file)[top_gene_feature]

    chr_list = list(set([gff_dict[i].chr_id for i in gff_dict]))

    chr_interlap_dict = {}
    for chr_id in chr_list:
        chr_interlap_dict[chr_id] = InterLap()
        chr_interlap_dict[chr_id].update(
            [(gff_dict[i].start, gff_dict[i].end) for i in gff_dict if gff_dict[i].chr_id == chr_id])

    gene_density_dict = {}
    for chr_id in chr_interlap_dict:
        gene_density_dict[chr_id] = {}
        chr_len = max(chr_interlap_dict[chr_id])[1]
        for i, s, e in split_sequence_to_bins(chr_len, bin_length, 1):
            gene_density_dict[chr_id][i] = len(
                list(chr_interlap_dict[chr_id].find((s, e))))

    if print_stat:
        num_list = []
        for i in gene_density_dict:
            for j in gene_density_dict[i]:
                num_list.append(gene_density_dict[i][j])

        p_range_list = list(range(0, 110, 10))
        percent_list = np.percentile(np.array(num_list), p_range_list)
        for i in range(len(p_range_list)):
            print("P%d: %.2f" % (p_range_list[i], percent_list[i]))

    return gene_density_dict


def get_cds_density(gff_file, TE_gff_file, genome_fasta_file, bin_length=1000000, print_stat=False):
    fa_dict = read_fasta_by_faidx(genome_fasta_file)
    chr_len_dict = {i: fa_dict[i].len() for i in fa_dict}

    # gene gff
    gff_dict = read_gff_file(gff_file)

    chr_dict = {}
    for i in gff_dict:
        for gene in gff_dict[i]:
            gene = gff_dict[i][gene]
            if gene.chr_id not in chr_dict:
                chr_dict[gene.chr_id] = []
            for j in gene.sub_features:
                for k in j.sub_features:
                    if k.type == 'CDS':
                        chr_dict[gene.chr_id].append((k.start, k.end))

    for i in chr_dict:
        chr_dict[i] = merge_intervals(chr_dict[i])

    chr_interlap_dict = {}
    for chr_id in chr_dict:
        chr_interlap_dict[chr_id] = InterLap()
        chr_interlap_dict[chr_id].update(chr_dict[chr_id])

    # TE gff
    te_gff_dict = read_gff_file(TE_gff_file)

    te_chr_dict = {}
    for i in te_gff_dict:
        for gene in te_gff_dict[i]:
            gene = te_gff_dict[i][gene]
            if gene.chr_id not in te_chr_dict:
                te_chr_dict[gene.chr_id] = []
            te_chr_dict[gene.chr_id].append((gene.start, gene.end))

    for i in te_chr_dict:
        te_chr_dict[i] = merge_intervals(te_chr_dict[i])

    te_chr_interlap_dict = {}
    for chr_id in te_chr_dict:
        te_chr_interlap_dict[chr_id] = InterLap()
        te_chr_interlap_dict[chr_id].update(te_chr_dict[chr_id])

    # remove overlap with te
    from toolbiox.lib.common.math.interval import section

    cds_density_dict = {}
    for chr_id in chr_interlap_dict:
        cds_density_dict[chr_id] = {}
        chr_len = chr_len_dict[chr_id]
        for i, s, e in split_sequence_to_bins(chr_len, bin_length, 1):
            cds_list = list(chr_interlap_dict[chr_id].find((s, e)))
            raw_sum_length = sum_interval_length(cds_list)

            overlap_with_te = []
            for cds in cds_list:
                for te in te_chr_interlap_dict[chr_id].find((cds[0], cds[1])):
                    if_flag, deta = section(cds, te)
                    overlap_with_te.append(deta)

            overlap_with_te_length = sum_interval_length(
                merge_intervals(overlap_with_te))

            cds_density_dict[chr_id][i] = (
                raw_sum_length - overlap_with_te_length) / (e-s+1)

    if print_stat:
        num_list = []
        for i in cds_density_dict:
            for j in cds_density_dict[i]:
                num_list.append(cds_density_dict[i][j])

        p_range_list = list(range(0, 110, 10))
        percent_list = np.percentile(np.array(num_list), p_range_list)
        for i in range(len(p_range_list)):
            print("P%d: %.2f" % (p_range_list[i], percent_list[i]))

    return cds_density_dict


def get_genome_CG_ratio(genome_fasta, bin_length=1000000, print_stat=False):
    fasta_dict = read_fasta_by_faidx(genome_fasta)

    genome_CG_ratio_dict = {}
    for chr_id in fasta_dict:
        genome_CG_ratio_dict[chr_id] = {}
        chr_len = fasta_dict[chr_id].len()
        for i, s, e in split_sequence_to_bins(chr_len, bin_length, 1):
            seq_tmp = fasta_dict[chr_id].sub(s, e, "+", False)
            c = seq_tmp.count('C')
            g = seq_tmp.count('G')
            c_ratio = (c + g) / (e-s+1)
            genome_CG_ratio_dict[chr_id][i] = c_ratio

    if print_stat:
        num_list = []
        for i in genome_CG_ratio_dict:
            for j in genome_CG_ratio_dict[i]:
                num_list.append(genome_CG_ratio_dict[i][j])

        p_range_list = list(range(0, 110, 10))
        percent_list = np.percentile(np.array(num_list), p_range_list)
        for i in range(len(p_range_list)):
            print("P%d: %.2f" % (p_range_list[i], percent_list[i]))

    return genome_CG_ratio_dict


if __name__ == "__main__":
    cp = CirclePlot()
    # name, length, bottom (0<=bottom<=1000), height (0<=bottom<=1000)
    cp.load_chr_info("1", 1000, bottom=500, height=100)
    cp.load_chr_info("2", 2000, bottom=500, height=100, facecolor="#ED665D")
    cp.load_chr_info("3", 3000, bottom=500, height=100, facecolor="#6DCCDA")
    cp.load_chr_info("4", 2000, bottom=400, height=100, facecolor="#ED97CA")
    cp.load_chr_info("5", 5000, bottom=550, height=50, facecolor="#EDC948")
    

