import matplotlib.path as mpath
import matplotlib.patches as mpatches

def scale_to_give_size(a_point_coord, target_size, raw_size, blank=(0, 0, 0, 0), reverse_x=False, reverse_y=False):
    """
    scale a point in a raw size to a new size

    point = (0,0)
    raw_size = (-2,2,-2,2) # x leaf,x right, y tail,y head

    target_size = (0,20,0,100)
    new point = (10,50)

    """

    b_x_L, b_x_R, b_y_T, b_y_H = blank
    a_x_L, a_x_R, a_y_T, a_y_H = target_size
    w_x_L, w_x_R, w_y_T, w_y_H = a_x_L + b_x_L, a_x_R - b_x_R, a_y_T + b_y_T, a_y_H - b_y_H
    r_x_L, r_x_R, r_y_T, r_y_H = raw_size

    if reverse_x:
        o_x = w_x_R - (a_point_coord[0] - r_x_L) / (r_x_R - r_x_L) * (w_x_R - w_x_L)
    else:
        o_x = (a_point_coord[0] - r_x_L) / (r_x_R - r_x_L) * (w_x_R - w_x_L) + w_x_L

    if reverse_y:
        o_y = w_y_H - (a_point_coord[1] - r_y_T) / (r_y_H - r_y_T) * (w_y_H - w_y_T)
    else:
        o_y = (a_point_coord[1] - r_y_T) / (r_y_H - r_y_T) * (w_y_H - w_y_T) + w_y_T

    return o_x, o_y

def line_segment_plot(ax, start, end, facecolor='w', lw=2):
    verts = [start, end]
    codes = [mpath.Path.MOVETO, mpath.Path.LINETO]

    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor=facecolor, lw=lw)
    ax.add_patch(patch)


