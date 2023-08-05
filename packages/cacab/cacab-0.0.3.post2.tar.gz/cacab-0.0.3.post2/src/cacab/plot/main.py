import collections
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import matplotlib
import pandas as pd
from matplotlib import cm
import matplotlib.dates
from matplotlib.colors import ListedColormap
from matplotlib.widgets import RectangleSelector
from matplotlib.transforms import Bbox, TransformedBbox
import matplotlib.patches as pch
import matplotlib.lines
from matplotlib.artist import Artist
import numpy as np
from scipy.ndimage import gaussian_filter
import colorsys

orsted_colors = ['#4099da', '#8ecdc8', '#644c76', '#e85757', '#fdd779','#b7ada5', '#d8d1ca', '#3b4956', '#99a4ae']
# defaultcolors = plt.rcParams['axes.prop_cycle'].by_key()['color']
defaultcolors = orsted_colors

backgroundcolors = list(
    map(lambda x: '#%02x%02x%02x' % tuple([(int(x[i + 1:i + 3], 16) + 255) // 2 for i in (0, 2, 4)]), defaultcolors))
semibackgroundcolors = list(
    map(lambda x: '#%02x%02x%02x' % tuple([(int(x[i + 1:i + 3], 16) * 3 + 255) // 4 for i in (0, 2, 4)]),
        defaultcolors))

def get_cmap(cols):
    new_cols = []
    for col in cols:
        if isinstance(col, str):
            col = [int(col[i + 1:i + 3], 16) for i in (0, 2, 4)]
        new_cols.append(col)
    n_vals = 1680
    for i in range(len(cols) - 1):
        try:
            col_array = np.append(col_array, np.array([between_colors(cols[i], cols[i+1], p, return_string=False) for p in np.linspace(0, 1, n_vals//(len(cols) -1))]), axis=0)
        except:
            col_array = np.array([between_colors(cols[i], cols[i+1], p, return_string=False) for p in np.linspace(0, 1, n_vals//(len(cols) -1))])
    col_array = col_array / 255
    return ListedColormap(col_array)

def float_col_to_int_col(col):
    for i in range(3):
        if col[0] != col[0]//1:
            return int(col[0]*255), int(col[1]*255), int(col[2]*255)
    return col

def between_colors(col1, col2, perc, return_string=True):
    if isinstance(col1, str):
        col1 = [(int(col1[i + 1:i + 3], 16)) for i in (0, 2, 4)]
    if isinstance(col2, str):
        col2 = [(int(col2[i + 1:i + 3], 16)) for i in (0, 2, 4)]
    assert len(col1) == 3 and len(
        col2) == 3, 'col1 and col2 should be either a colour string or 3 value array indicating rgb'
    col1, col2 = float_col_to_int_col(col1), float_col_to_int_col(col2)
    col = [int((1-perc) * col1[i] + (perc) * col2[i]) for i in range(3)]
    if return_string:
        return '#%02x%02x%02x' % tuple(col)
    return col

def hue_shift(col, shift):
    if isinstance(col, str):
        col = [(int(col[i + 1:i + 3], 16))/255 for i in (0, 2, 4)]
    return colorsys.hls_to_rgb(*[i+j for (i,j) in zip(colorsys.rgb_to_hls(*col), [shift, 0, 0])])

def extended_cycle(i):
    return {'c':hue_shift(defaultcolors[i%len(defaultcolors)], (i//len(defaultcolors))*0.03),
            'ls':['-', '--', ':', '-.'][(i//len(defaultcolors))%4]}

def fade_color(color, alpha):
    return '#%02x%02x%02x' % tuple(
        [int((int(color[i + 1:i + 3], 16) * alpha + 255 * (1 - alpha))) for i in (0, 2, 4)])

def variable_backgroundcolors(alpha):
    return list(
        map(lambda x: fade_color(x, alpha), defaultcolors)
    )


def density(x_i, sigma=None, n=2000):
    x_i = np.asarray(x_i)
    x_i = x_i[~np.isnan(x_i)]
    if sigma is None:
        sigma = np.std(x_i)
    x = np.linspace(x_i.min() - 5*sigma, x_i.max() + 5*sigma, n)
    five_sigma_n = int(n/(x[-1] - x[0]) * 5 * sigma)
    dx = x[1] - x[0]
    x_edges = np.concatenate([x-dx, np.array([x[-1]+dx])])
    y, _ = np.histogram(x_i, bins=x_edges)
    kernel = np.arange(-five_sigma_n, five_sigma_n + 1) * dx / sigma
    kernel = np.exp(-0.5*kernel**2)
    y = np.convolve(y, kernel, 'same')
    y = y / (y.sum()*dx)
    return x, y

def add_ax_distribution(fig, ax, x=None, y=None, ax_top_len=0.05, ax_right_len=0.05, x_sigma=None, y_sigma=None, c=None, fill=True, alpha=0.5, ax_top=None, ax_right=None):
    ax_pos = ax.get_position()
    c = c or defaultcolors[0]
    if x is not None:
        xlim = ax.get_xlim()
        y_max = -1e10
        if ax_top is None:
            ax_top = fig.add_axes([ax_pos.x0, ax_pos.y0+ax_pos.height, ax_pos.width, ax_top_len], sharex=ax)
        else:
            y_max = ax_top.get_ylim()[1]
        ax_top.set_facecolor([1, 1, 1, 0])
        x_sigma = x_sigma or np.std(x[~np.isnan(x)])/10
        x_base, top_dens = density(x, sigma=x_sigma, n=5000)
        ax_top.plot(x_base, top_dens, c=c, alpha=alpha)
        if fill:
            ax_top.fill_between(x_base, top_dens, facecolor=between_colors(c, '#ffffff', 0.5), alpha=alpha)
        ax_top.set_ylim([0, max(y_max, top_dens.max() * 1.1)])
        plt.setp(ax_top.get_xticklabels(), visible=False)
        ax_top.set_yticks([])
        ax_top.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        ax_top.grid(False)
        ax.set_xlim(xlim)
    if y is not None:
        ylim = ax.get_ylim()
        x_max = -1e10
        if ax_right is None:
            ax_right = fig.add_axes([ax_pos.x0 + ax_pos.width, ax_pos.y0, ax_right_len, ax_pos.height], sharey=ax)
        else:
            x_max = ax_right.get_xlim()[1]
        ax_right.set_facecolor([1, 1, 1, 0])
        y_sigma = y_sigma or np.std(y[~np.isnan(y)])/10
        y_base, right_dens = density(y, sigma=y_sigma, n=5000)
        ax_right.plot(right_dens, y_base, c=c, alpha=alpha)
        if fill:
            ax_right.fill_betweenx(y_base, right_dens, facecolor=between_colors(c, '#ffffff', 0.5), alpha=alpha)
        ax_right.set_xlim([0, max(x_max, right_dens.max()*1.1)])

        plt.setp(ax_right.get_yticklabels(), visible=False)
        ax_right.set_xticks([])
        ax_right.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
        ax_right.grid(False)
        ax.set_ylim(ylim)
    return ax_top, ax_right

def heatmap_2d(x_i, y_i, ax=None, x_arr=None, y_arr=None, xlim=None, ylim=None, n=2000, imshow_kwgs={}, blur_sigma=None, heatmap_func=None):
    x_i, y_i = np.asarray(x_i), np.asarray(y_i)
    filt = (~np.isnan(x_i)) & (~np.isinf(x_i)) & (~np.isnan(y_i)) & (~np.isinf(y_i))
    if xlim is not None:
        filt = filt & (x_i > xlim[0]) & (x_i < xlim[1])
    if ylim is not None:
        filt = filt & (y_i > ylim[0]) & (y_i < ylim[1])
    x_i, y_i = x_i[filt], y_i[filt]
    if x_arr is None:
        xlim = xlim or [1.1 * x_i.min() - 0.1 * x_i.max(), 1.1*x_i.max() - 0.1*x_i.min()]
        try:
            x_arr = np.linspace(xlim[0], xlim[1], n[0])
        except TypeError:
            x_arr = np.linspace(xlim[0], xlim[1], n)

    if y_arr is None:
        ylim = ylim or [1.1 * y_i.min() - 0.1 * y_i.max(), 1.1*y_i.max() - 0.1*y_i.min()]
        try:
            y_arr = np.linspace(ylim[0], ylim[1], n[1])
        except TypeError:
            y_arr = np.linspace(ylim[0], ylim[1], n)
    hm = np.histogram2d(y_i, x_i, bins=[y_arr, x_arr])[0]
    hm = np.flip(hm, axis=0)
    if heatmap_func is not None:
        hm = heatmap_func(hm).astype('float')
    if blur_sigma is not None:
        hm = gaussian_filter(hm, sigma=blur_sigma, mode='constant', cval=0)
    hm = hm / hm.max()
    if ax is not None:
        imsh = ax.imshow(hm, extent=[x_arr[0], x_arr[-1], y_arr[0], y_arr[-1]], aspect='auto', **imshow_kwgs)
        return hm, imsh
    else:
        return hm, None

def heatmap_3d(x_i, y_i, z_i, ax=None, cax=None, x_arr=None, y_arr=None, xlim=None, ylim=None, zlim=None, n=2000, imshow_kwgs={}, blur_sigma=None, heatmap_func=None, zfilt=False):
    cmap = get_cmap(['#00ffff', '#0000ff', '#ff00ff', '#ff0000', '#ffff00'])
    x_i, y_i, z_i = np.asarray(x_i), np.asarray(y_i), np.asarray(z_i)
    filt = (~np.isnan(x_i)) & (~np.isnan(y_i)) & (~np.isnan(z_i))
    if xlim is not None:
        filt = filt & (x_i > xlim[0]) & (x_i < xlim[1])
    if ylim is not None:
        filt = filt & (y_i > ylim[0]) & (y_i < ylim[1])
    if zlim is not None and zfilt:
        filt = filt & (z_i > zlim[0]) & (z_i < zlim[1])
    x_i, y_i, z_i = x_i[filt], y_i[filt], z_i[filt]
    if x_arr is None:
        xlim = xlim or [1.1 * x_i.min() - 0.1 * x_i.max(), 1.1*x_i.max() - 0.1*x_i.min()]
        try:
            x_arr = np.linspace(xlim[0], xlim[1], n[0])
        except TypeError:
            x_arr = np.linspace(xlim[0], xlim[1], n)
    xlim = [x_arr.min(), x_arr.max()]
    if y_arr is None:
        ylim = ylim or [1.1 * y_i.min() - 0.1 * y_i.max(), 1.1*y_i.max() - 0.1*y_i.min()]
        try:
            y_arr = np.linspace(ylim[0], ylim[1], n[1])
        except TypeError:
            y_arr = np.linspace(ylim[0], ylim[1], n)
    ylim = [y_arr.min(), y_arr.max()]
    hm, _ = heatmap_2d(x_i, y_i, ax=ax, x_arr=x_arr, y_arr=y_arr, xlim=xlim, ylim=ylim, n=n, imshow_kwgs=imshow_kwgs,
                       blur_sigma=None, heatmap_func=heatmap_func)
    df = pd.DataFrame(data={'x':x_i, 'y':y_i, 'z':z_i})
    df['x_cut'] = pd.cut(df['x'], bins=x_arr, labels=np.arange(len(x_arr) - 1, dtype='int')).astype('int')
    df['y_cut'] = pd.cut(df['y'], bins=y_arr, labels=np.arange(len(y_arr) - 1, dtype='int')).astype('int')
    z_group = df.groupby(['y_cut', 'x_cut'])['z']
    z_sum = z_group.sum().unstack()
    z_count = z_group.count().unstack()
    arrs = []
    for i_arr, arr in enumerate([z_sum, z_count]):
        arr = pd.concat([arr, pd.DataFrame(columns=[i for i in range(len(x_arr) - 1) if i not in arr.columns])])
        arr = pd.concat([arr, pd.DataFrame(columns=[], index=[i for i in range(len(y_arr) - 1) if i not in arr.index])], axis=1)
        arr = arr.sort_index(ascending=False).reset_index(drop=True).values.astype('float')
        arr[np.isnan(arr)] = 0
        if blur_sigma is not None:
            gaussian_filter(arr, sigma=blur_sigma, mode='constant', cval=0, output=arr)
        arrs.append(arr)
    z_sum, z_count = arrs
    z_filt = z_count <= 0
    z_count[z_filt] = 1
    z_mean = z_sum/z_count
    if zlim is None:
        zrange = [z_mean[~z_filt].min().min(), z_mean[~z_filt].max().max()]
    else:
        zrange = zlim
    z_mean = z_mean - zrange[0]
    z_mean = (z_mean / (zrange[1] - zrange[0]))

    if blur_sigma is not None:
        gaussian_filter(hm, sigma=blur_sigma, mode='constant', cval=0, output=hm)

    z_mean[z_mean < 0] = 0
    z_mean[z_mean > 1] = 1

    col_r = (2 - 4 * abs(z_mean-0))
    col_g = (2 - 4 * abs(z_mean-0.5))
    col_b = (2 - 4 * abs(z_mean-1))
    hm = hm / hm.max()
    test_hm = False
    if test_hm:
        fig = plt.figure()
        ax = fig.gca()
        ax.imshow(z_mean)
        plt.show()
    cols = np.dstack([1 - hm*col_r, 1 - hm*col_g, 1 - hm*col_b])
    # cols = np.dstack([1 - col_r, 1 - col_g, 1 - col_b])

    if ax:
        imsh = ax.imshow(cols, extent=[x_arr[0], x_arr[-1], y_arr[0], y_arr[-1]], aspect='auto', **imshow_kwgs)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    else:
        imsh = None
    if cax:
        matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=matplotlib.colors.Normalize(vmin=zrange[0], vmax=zrange[1]))
    return cols, imsh, cmap, zrange


def fill_between_gradient(ax, x0, y0, y1, c0, c1=None, x1=None, alpha0=1, alpha1=0, n=100, perc_func=None):
    for i in range(n):
        flat_perc = i / n
        if perc_func is not None:
            perc = perc_func(flat_perc)
        if c1 is None:
            c = c0
        else:
            c = between_colors(c0, c1, perc)
        alpha = alpha0 * (1 - perc) + alpha1 * perc

        end_perc = flat_perc + 2 / n
        y_start = y0 * (1 - flat_perc) + y1 * flat_perc
        y_end = y0 * (1 - end_perc) + y1 * (end_perc)
        if x1 is not None:
            x = x0 * (1 - flat_perc) + x1 * flat_perc
        else:
            x = x0

        ax.fill_between(x, y_start, y_end, facecolor=c, edgecolor=None, alpha=alpha, step="post", lw=0)


def annotated_axline(ax, value, text, ax_type: str = 'h', text_loc=0.5, axline_kwargs=None, clear_line_width=0.2, rotation=None):
    ax_type = {"horizontal":"h", "vertical":"v"}.get(ax_type.lower(), ax_type.lower())
    axline_kwargs = axline_kwargs if axline_kwargs is not None else {}
    if not ax_type in ["h", "v"]:
        raise ValueError("ax_type needs to be h, v, horizontal or vertical.")
    axline = {"v":ax.axvline, "h":ax.axhline}.get(ax_type)
    line_elements = [axline(value, **axline_kwargs) for _ in range(2)]
    xytext = {"v":(value, text_loc), "h":(text_loc, value)}.get(ax_type)
    textcoords = {"v":("data", "axes fraction"), "h":("axes fraction", "data")}.get(ax_type)
    if rotation is None:
        rotation = {"h": 0, "v": 90}.get(ax_type)
    ax.annotate(text=text, xy=(0, 0), xytext=xytext, textcoords=textcoords, va='center', ha='center', rotation=rotation)

    bbox_low = {
        "h": TransformedBbox(Bbox([[0, 0], [text_loc - clear_line_width / 2, 1]]), transform=ax.transAxes),
        "v": TransformedBbox(Bbox([[0, 0], [1, text_loc - clear_line_width / 2]]), transform=ax.transAxes)
    }.get(ax_type)
    bbox_high = {
        "h": TransformedBbox(Bbox([[text_loc + clear_line_width / 2, 0], [1, 1]]), transform=ax.transAxes),
        "v": TransformedBbox(Bbox([[0, text_loc + clear_line_width / 2], [1, 1]]), transform=ax.transAxes)
    }.get(ax_type)

    line_elements[0].set_clip_box(bbox_low)
    line_elements[1].set_clip_box(bbox_high)

class PointSelector:
    """
    Tool for linking multiple Line2D objects together, such that they can highlight each other with a selector tool.\n
    The mouse is used to control the selection area\n
    Enter adds the selection\n
    Delete removes the selection\n
    Pressing Backspace clears selection\n
    Pressing s calls a save_callback function where something like fig.savefig(path) can be called\n
    Pressing i inverts the selection\n
    Pressing z goes to the previous selection\n

         Parameters
         ----------
         scatter_lines : `[~matplotlib.lines.Line2D]`
             The lines to be linked to each other. Ensure that they are the same length!
         fade_kwargs=None : dict or [dict]
             A dictionary or list of dictionaries (same length as list of scatter_lines). The keys in the dictionary are used to call the Line2D.set_{key} function to value
         verbose=True : bool
             Whether the class should give hints to how to be used.
         background_fade : float
             Should be between 0 and 1. Describes how much the background color will sample between the original color and white. 1 is full original color, 0 is full white.
    """

    def __init__(self, scatter_lines: [matplotlib.lines.Line2D], fade_kwargs=None, verbose=True, background_fade=0.2):
        self.init = True
        self.verbose = verbose
        # Make sure that scatter_lines is iterables.
        if fade_kwargs is None:
            fade_kwargs = {}
        if isinstance(fade_kwargs, dict):
            fade_kwargs = [fade_kwargs for _ in range(len(scatter_lines))]
        else:
            assert len(fade_kwargs) == len(scatter_lines), "scatter_lines and fade_kwargs must be equal length"
        self.scatter_lines = scatter_lines
        self.axs = [scatter_line.axes for scatter_line in self.scatter_lines]
        self.canvas = self.axs[0].figure.canvas
        self.unique_axs = list(set(self.axs))
        self.line_cols = [scatter_line.get_color() for scatter_line in self.scatter_lines]
        [scatter_line.set_linestyle('None') for scatter_line in self.scatter_lines]
        [scatter_line.set_marker('.') for scatter_line in self.scatter_lines if scatter_line.get_marker() == 'None']
        self.faded_cols = [fade_color(line_col, background_fade) for line_col in self.line_cols]

        self.xyss = [scatter_line.get_data() for scatter_line in scatter_lines]
        self.faded_lines = []
        for i_sl, scatter_lines in enumerate(self.scatter_lines):
            self.faded_lines.append(self.axs[i_sl].plot(self.xyss[i_sl][0], self.xyss[i_sl][1])[0])
            self.faded_lines[i_sl].update_from(self.scatter_lines[i_sl])
            self.faded_lines[i_sl].set_color(self.faded_cols[i_sl])
            self.faded_lines[i_sl].set_zorder(self.faded_lines[i_sl].get_zorder() - 0.001)
            for key, value in fade_kwargs[i_sl].items():
                try:
                    func = getattr(self.faded_lines[i_sl], 'set_' + key)
                    func(value)
                except AttributeError:
                    raise Warning(f'Can not call set_{key} on Line2D object')

        xyss_list = []
        for xys in self.xyss:
            xy_pair = []
            for i in range(2):
                if np.issubdtype(xys[i].dtype, np.datetime64):
                    xy = matplotlib.dates.date2num(xys[i])
                else:
                    xy = xys[i]
                xy_pair.append(xy)
            xyss_list.append(np.array(list(zip(xy_pair[0], xy_pair[1]))))
        self.xyss = xyss_list
        Nptss = [len(xys) for xys in self.xyss]
        assert len(set(Nptss)) <= 1, "All scatter lines should have the same length"
        self.Npts = Nptss[0]
        self.selectors = []
        for ax in self.unique_axs:
            self.selectors.append(
                RectangleSelector(ax, onselect=lambda eclick, erelease, clickax=ax: self.onselect(clickax, eclick,
                                                                                                  erelease),
                                  useblit=True, interactive=True,
                                  props=dict(facecolor='xkcd:lightish blue', edgecolor='black',
                                                 alpha=0.2, fill=True)))
        self.inds = []
        self.all_inds = []
        self.ind_memory = []
        self.canvas.mpl_connect("key_press_event", lambda event: self.accept(event))
        self.canvas.mpl_connect("button_press_event", self.onclick)
        DummyEvent = collections.namedtuple('DummyEvent', ['key'])
        self.accept(DummyEvent('backspace'))

        def handler(msg_type, msg_log_context, msg_string):
            pass

        from PyQt5 import QtCore
        QtCore.qInstallMessageHandler(handler)
        try:
            plt.rcParams['keymap.save'].remove('s')
        except ValueError:
            pass
        try:
            plt.rcParams['keymap.back'].remove('backspace')
        except ValueError:
            pass

        if self.verbose:
            print('PointSelector Initialized')
        self.init = False
        self.last_ax = None

    def onclick(self, event):
        self.last_ax = event.inaxes
        for i_uax, ax in enumerate(self.unique_axs):
            if event.inaxes == ax:
                if not self.selectors[i_uax].visible:
                    self.selectors[i_uax].set_visible(True)
            else:
                if self.selectors[i_uax].visible:
                    self.selectors[i_uax].set_visible(False)
                    self.selectors[i_uax].update()

    def onselect(self, clickax, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        ll = np.array([min(x1, x2), min(y1, y2)])
        ur = np.array([max(x1, x2), max(y1, y2)])
        inds = [np.nonzero(np.all(np.logical_and(ll <= xys, xys <= ur), axis=1)) for (xys, ax) in
                zip(self.xyss, self.axs) if ax == clickax]

        self.inds = np.unique(np.concatenate(inds, axis=1))

    def accept(self, event):
        if event.key == "enter":
            if self.all_inds is not []:
                self.all_inds = np.unique(np.concatenate([self.inds, self.all_inds])).astype('int').tolist()
            else:
                self.all_inds = self.inds
        if event.key == 'delete':
            if self.all_inds is not []:
                self.all_inds = [ind for ind in self.all_inds if ind not in self.inds]
        if event.key == "backspace":
            self.all_inds = []
            for selector in self.selectors:
                selector.set_visible(False)
                # selector.update()
        if event.key == "i":
            self.all_inds = sorted(set(range(0, self.Npts)) - set(self.all_inds))
        if event.key == "z":
            if len(self.ind_memory) > 1:
                self.all_inds = self.ind_memory[-2]

        if event.key in ["enter", "backspace", "delete", "i", "z"]:
            anti_inds = sorted(set(range(0, self.Npts)) - set(self.all_inds))
            # print(self.all_inds)
            # print(anti_inds)
            for i_s, (scatter_line, faded_line) in enumerate(zip(self.scatter_lines, self.faded_lines)):
                scatter_line.set_data(None if self.all_inds is None else np.transpose(self.xyss[i_s][self.all_inds]))
                faded_line.set_data(np.transpose(None if anti_inds is None else self.xyss[i_s][anti_inds]))

            self.accept_callback(self.all_inds)
            if not event.key == "z":
                self.ind_memory.append(self.all_inds)
            elif len(self.ind_memory) > 1:
                self.ind_memory.pop(len(self.ind_memory)-1)
            if event.key == 'enter':
                for i_ax, ax in enumerate(self.unique_axs):
                    if ax == self.last_ax:
                        # print(dir(self.selectors[i_ax]))
                        # print(self.selectors[i_ax].corners)
                        corners = self.selectors[i_ax].corners
                        self.accept_selectrect_callback(corners[0][0], corners[0][1], corners[1][0], corners[1][2])

        if event.key in ['s']:
            for selector in self.selectors:
                if selector.visible:
                    selector.set_visible(False)
                    selector.update()
            self.save_callback()
        self.canvas.draw_idle()

    def accept_callback(self, inds):
        '''
        Override this with your own callback to get additional functionality on selection changes.
        The argument fed to this callback is the indices describing which points have been selected.
        '''
        if self.verbose and not self.init:
            print(f"override PointSelector.accept_callback to add functionality to finishing a selection. "
                  f"The active indices are given as an argument for this function.")

    def accept_selectrect_callback(self, x0, x1, y0, y1):
        '''
        Override this with your own callback to get additional functionality on enter.
        The argument fed to this callback is the the event press and event release.
        '''
        if self.verbose and not self.init:
            print(f"override PointSelector.accept_callback to add functionality to finishing a selection. "
                  f"The active indices are given as an argument for this function.")

    def save_callback(self):
        '''
        Override this with your own callback to add functionality when 's' is pressed. (meant for saving the figure).
        '''
        if self.verbose:
            print(f"override PointSelector.save_callback to add functionality to pressing the 's' key")

    def disconnect(self):
        [selector.disconnect_events() for selector in self.selectors]
        # for i in range(len(self.collections)):
        #     self.fcs[i][:, -1] = 1
        #     self.collections[i].set_facecolors(self.fcs[i])
        self.canvas.draw_idle()

def freeze_axes(ax):
    xlim_base = ax.get_xlim()
    ylim_base = ax.get_ylim()
    ax.callbacks.connect("xlim_changed", lambda _, ax_i=ax, xlim_i=xlim_base: ax_i.set_xlim(xlim_i) if ax_i.get_xlim() != xlim_i else None)
    ax.callbacks.connect("ylim_changed", lambda _, ax_j=ax, ylim_j=ylim_base: ax_j.set_ylim(ylim_j) if ax_j.get_ylim() != ylim_j else None)

def setup_orsted():
    matplotlib.use("Qt5Agg")
    matplotlib.pyplot.style.use({
        "grid.alpha": 0.5,
        "axes.grid": True,
        "axes.prop_cycle": matplotlib.cycler(color=orsted_colors),
    })


def specify_zoom_ax(ax_zoom: plt.axes, ax_main, c, ltrb_transform=None, rect_kwargs=None, connection_path_kwargs=None, update=True):
    rect_kwargs = rect_kwargs if rect_kwargs is not None else dict()
    connection_path_kwargs = connection_path_kwargs if connection_path_kwargs is not None else dict()
    rect_base_kwargs = dict(lw=2, edgecolor=c, facecolor=c, alpha=0.3, zorder=99)
    rect_zoom_kwargs = dict(lw=4, edgecolor=c, facecolor=c, alpha=0.3, zorder=-100)
    if ltrb_transform:
        rect_kwargs.update(transform=ltrb_transform)
    rect_base_kwargs.update(rect_kwargs)
    rect_zoom_kwargs.update(rect_kwargs)

    connection_path_base_kwargs = dict(color=c, alpha=0.2, annotation_clip=False, zorder=100)
    connection_path_base_kwargs.update(connection_path_kwargs)

    for spine in ax_zoom.spines.values():
        spine.set_edgecolor(c)

    conn_patches = []
    main_box_patch = None
    zoom_box_patch = None

    def set_zoom(ax_event):
        left_top_right_bottom = (
            ax_zoom.get_xlim()[0], ax_zoom.get_ylim()[1], ax_zoom.get_xlim()[1], ax_zoom.get_ylim()[0])
        left, top, right, bottom = [
            matplotlib.dates.date2num(v.to_datetime64()) if isinstance(v, pd.Timestamp) else v
            for v in left_top_right_bottom
        ]
        width = (right - left)
        height = (top - bottom)
        center = (left, bottom)

        nonlocal main_box_patch
        if main_box_patch is None:
            main_box_patch = pch.Rectangle(center, width, height, **rect_base_kwargs)
            ax_main.add_artist(main_box_patch)
        else:
            main_box_patch.set_xy(center)
            main_box_patch.set_width(width)
            main_box_patch.set_height(height)

        nonlocal zoom_box_patch
        if zoom_box_patch is None:
            zoom_box_patch = pch.Rectangle(center, width, height, **rect_base_kwargs)
            ax_zoom.add_artist(zoom_box_patch)
        else:
            zoom_box_patch.set_xy(center)
            zoom_box_patch.set_width(width)
            zoom_box_patch.set_height(height)

        four_pair_points = [
            ((left, top), (0, 1)),
            ((right, top), (1, 1)),
            ((right, bottom), (1, 0)),
            ((left, bottom), (0, 0)),
        ]

        if len(conn_patches) == 0:
            for pair_points in four_pair_points:
                conn_patch = pch.ConnectionPatch(pair_points[0], pair_points[1], "data", "axes fraction", ax_main, ax_zoom,
                                                 **connection_path_base_kwargs)
                conn_patches.append(conn_patch)
                ax_main.get_figure().add_artist(conn_patch)
        else:
            for i in range(4):
                conn_patches[i].xy1 = four_pair_points[i][0]

    if update:
        ax_zoom.callbacks.connect("xlim_changed", set_zoom)
        ax_zoom.callbacks.connect("ylim_changed", set_zoom)
    set_zoom(None)


if __name__ == '__main__':
    plt.close('all')
    matplotlib.use('Qt5Agg')
    selector_test = False
    if selector_test:
        import pandas as pd

        dates = np.arange(pd.Timestamp('2020-01-01'), pd.Timestamp('2020-04-01'), pd.Timedelta('120s'))
        frame = pd.DataFrame(index=dates,
                             data={'std_x': np.sin(np.arange(len(dates)) / len(dates) * np.pi + np.pi / 2) + 1,
                                   'std_y': np.sin(np.arange(len(dates)) / len(dates) * np.pi + 3 * np.pi / 2) + 1})
        frame['x'] = frame['std_x'].map(lambda x: np.random.normal(0, x))
        frame['y'] = frame['std_y'].map(lambda x: np.random.normal(0, x))

        fig, _ = plt.subplots(figsize=(8, 8))
        fig.gridspec = gs.GridSpec(2, 1)
        fig.gridspec.update(hspace=0.4, right=0.75)
        fig.clf()
        axs = [fig.add_subplot(fig.gridspec[0, 0]),
               fig.add_subplot(fig.gridspec[1, 0])]

        sls = []
        for i_ax, ax in enumerate(axs):
            if i_ax == 0:
                sl, = ax.plot(frame.index, frame['std_x'], ls='None', marker='.', ms=4, alpha=0.1, c=defaultcolors[0])
                ax.plot([], [], ls='None', marker='.', label='std x', c=defaultcolors[0])
                sls.append(sl)
                sl, = ax.plot(frame.index, frame['std_y'], ls='None', marker='.', ms=4, alpha=0.1, c=defaultcolors[1])
                ax.plot([], [], ls='None', marker='.', label='std y', c=defaultcolors[1])
                ax.set_xlim([frame.index.min(), frame.index.max()])
                ax.set_xlabel('Date')
                ax.set_ylabel('Std')
                ax.legend(bbox_to_anchor=(1, 0.8, 0.2, 0.2), loc='upper left')
            else:
                sl, = ax.plot(frame['x'], frame['y'], marker='.', ms=4, alpha=0.1)
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_xlim([frame['x'].min(), frame['x'].max()])
                ax.set_ylim([frame['y'].min(), frame['y'].max()])
            sls.append(sl)

        # Link Line2D's together. fade_kwargs is optional.
        selector = PointSelector(scatter_lines=sls, fade_kwargs=[{'ms': 2}, {'ms': 2}, {'ms': 2, 'color': 'grey'}])
        # Optional callbacks to add to the function. Will be activated on pressing enter / s. (s also clears the selector objects)
        selector.accept_callback = lambda x: fig.suptitle(f'{len(x)} points selected')
        selector.save_callback = lambda: print(
            'custom function that could have called something like fig.savefig(path)')
        plt.show()

    dist_add_test = False
    if dist_add_test:
        np.random.seed(10)
        x = np.concatenate([np.random.normal(5, 2, 10000), np.random.normal(0, 1, 5000)])
        y = np.concatenate([np.random.normal(5, 2, 10000), np.random.normal(0, 1, 5000)])

        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x, y, ls='none', marker='.')
        add_ax_distribution(fig, ax, x, y, c=defaultcolors[0], ax_right_len=0.03, y_sigma=0.05)
        plt.show()


        x1 = np.random.normal(5, 2, 10000)
        x2 = np.random.normal(0, 1, 5000)
        y1 = np.random.normal(5, 2, 10000)
        y2 = np.random.normal(0, 1, 5000)

        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x1, y1, ls='none', marker='.')
        ax.plot(x2, y2, ls='none', marker='.')
        add_ax_distribution(fig, ax, x1, y1, c=defaultcolors[0], ax_right_len=0.03, y_sigma=0.05)
        add_ax_distribution(fig, ax, x2, y2, c=defaultcolors[1], ax_right_len=0.03, y_sigma=0.05)
        plt.show()

    set_zoom_ax_test = True
    if set_zoom_ax_test:
        import numpy as np
        setup_orsted()
        fig = plt.figure(figsize=(10, 5))
        fig.gridspec = gs.GridSpec(1, 2)
        axs = [fig.add_subplot(fig.gridspec[0, i]) for i in range(2)]
        n = 10000
        x = np.random.normal(0, 1, n)
        y = np.random.normal(0, 1, n)
        axs[0].scatter(x, y, c=defaultcolors[0], marker='.')
        axs[1].scatter(x, y, c=defaultcolors[0], marker='.')
        axs[1].set_xlim([-0.3, 0.3])
        axs[1].set_ylim([-0.3, 0.3])
        set_zoom_ax(axs[1], axs[0], c=defaultcolors[1])
        plt.show()


