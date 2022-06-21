import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
import matplotlib as mpl
import mplhep as hep
import boost_histogram as bh
import hist
import pandas as pd
import numpy as np
import logging
import pickle
from typing import Tuple
from matplotlib.offsetbox import AnchoredText
#from numba import jit, njit
from matplotlib import transforms
from math import ceil



class EmptyPlot(object):
    
    
    def __init__(self, title="", layout=(1,1), size=(6.4,4.8), style='ATLAS', directory='', logotext='Internal') -> None:
        
        self.mastertitle = title
        self.layout      = layout
        self.figsize     = size
        self.style       = style
        self.dir         = directory
        
        # set default dict of axes titles
        self.xtitles_dict = {
            'xmain' : '',
            'xtop'  : '',
            'xbot'  : '',
            'xleft' : '', # not used
            'xright': ''
        }
        self.ytitles_dict = {
            'ymain' : '',
            'ytop'  : '',
            'ybot'  : '',
            'yleft' : '', # not used
            'yright': ''
        }
        """
        The terms 'main', 'top', 'bot' etc. refer to the follownig subplot scheme:
        
                 -------- 
                |  top   |
                 --------        
         -----   --------   -----
        |     | |        | |     |
        |left | |  main  | |right|
        |     | |        | |     |
         -----   --------   -----
                 -------- 
                |  bot   |
                 --------
        
        And each plot type (ratio, pull, projection, corrm) will be a combination of
        these subplots (Ax objects). For example, the ratio plot will be made of main
        and bot subplots and the projection plot will be made of main, top and right
        subplots. The left subplot is currently not used and might be deleted in the 
        future if no use cases are found.
        
        The space between the subplots is called 'spacing' throughout all classes
        """
        
        # dictionary of marker styles from matplotlib
        # -> https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.markers.MarkerStyle.html#matplotlib.markers.MarkerStyle.markers
        self.markerstyles = mpl.markers.MarkerStyle.markers

        # common rcParams to all (or most) plot types
        self.rcps = {
            'xaxis.labellocation' : 'right', # location of x label w.r.t. x axis
            'yaxis.labellocation' : 'top', # location of y label w.r.t. y axis
            'axes.labelpad'       : 1, # distance of axis label from axis tick labels
            'axes.titlesize'      : 20, # master title font size
            'font.size'           : 10, # x, y label AND ticks label AND legend font size
            'lines.linewidth'     : 1,
            'lines.marker'        : list(mpl.markers.MarkerStyle.filled_markers),
            'lines.markersize'    : 8,
        }

        # default font sizes
        self.mastersize = self.rcps['axes.titlesize'] # figure title font size
        self.fontsize = 15 # axis label font size
        
        # default text to diaplay near atlas logo
        self.logotext = logotext
    
    def create_canvas(self) -> None:
        """ Create figure and set the hep style (rcParams) """
        
        self.fig = plt.figure(figsize=self.figsize)
        hep.style.use(self.style) # available syles are: {"ALICE" | "ATLAS" | "CMS" | "LHCb1" | "LHCb2"}
        
        # set math text font to non-italics
        mpl.rcParams['mathtext.default'] = 'regular'

        
    def make_grid(self, **grid_kw) -> None:
        """ Create gridspec object to set configuration of subplots """
        
        self.gs = gridspec.GridSpec(*self.layout, **grid_kw)
    
    
    def make_subplot(self, start_row: int, end_row: int, start_col: int, end_col: int, **subplot_kw) -> mpl.axes.Axes:
        """ Generate ax objects (subplots). Arguments must be allowed by layout size """
        
        return self.fig.add_subplot(self.gs[start_row:end_row,start_col:end_col], **subplot_kw)
        
    
    def set_xtitles(self, ax: mpl.axes.Axes, axis_key: str, fontsize: int, labelpad=5, loc='right') -> None:
        """ Set x axis labels according to xtitles_dict """
        
        ax.set_xlabel(self.xtitles_dict[axis_key], fontsize=fontsize, labelpad=labelpad, loc=loc)
    
    
    def set_ytitles(self, ax: mpl.axes.Axes, axis_key: str, fontsize: int, labelpad=5, loc='top') -> None:
        """ Set y axis labels according to ytitles_dict """
        
        ax.set_ylabel(self.ytitles_dict[axis_key], fontsize=fontsize, labelpad=labelpad, loc=loc)
    
    
    def set_tickparams(self, ax: mpl.axes.Axes, labelsize: int) -> None:
        
        ax.tick_params(direction='in', length=10, labelsize=labelsize)
        ax.tick_params(which='minor', direction='in', length=5)
        
    
    def set_color(self, colormap='viridis', reverse=False) -> None:
        """ Set colormap to use for plot """
        
        self.user_cmap = colormap
        if reverse:
            self.user_cmap = self.user_cmap + '_r'
        mpl.rcParams['image.cmap'] = self.user_cmap
    

    def config_rcParams(self, settings_dict: dict) -> None:
        """ Let user update global rcParams values of matplotlib """
        if isinstance(settings_dict, dict):
            for key, value in settings_dict.items():
                #PATCHED: skip if lines.marker is a list
                if key == 'lines.marker' and isinstance(value, list): continue
                mpl.rcParams[key] = value

        else:
            print(f"Put a dictionary as argument for {__name__} function") # need logging
        
        # can also add a 'help' command to display all the rcParams variables that can be cahnged to help user
        
        # there is an easier function already in matplotlib, might want to switch to that
        # https://matplotlib.org/stable/api/matplotlib_configuration_api.html#matplotlib.rc

    
    def type_checker(self, obj, _type) -> bool:
        """ Checks type of obj, also considering case when it is a list of other objs """

        is_type = False

        if isinstance(obj, list):
            if all(isinstance(x, _type) for x in obj):
                is_type = True
            else:
                logging.error(f"All elements in list must be {_type} objects")
        elif isinstance(obj, dict):
            if all(isinstance(x, _type) for k, x in obj.items()):
                is_type = True
            else:
                logging.error(f"All values in dict must be {_type} objects")
        elif isinstance(obj, _type):
            is_type = True
        else:
            logging.error(f"Object type is not {_type}")

        return is_type
    
    
    def gridstring_converter(self, string: str) -> None:
        """
        The gridstring argument is a combination of '(axis) + (linestyle)'
        strings, for example x: will put grid lines of type ':' on each major x 
        axis ticks. The line styles are taken from the matplotlib environment:
        https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.axes.Axes.grid.html
        """
        
        linestyles = ['-', '--', '-.', ':']
        
        if (string[0] == 'x' or string[0] == 'y') and string[1:] in linestyles:
            self.gridaxis = string[0]
            self.gridline = string[1:]
        elif string[:4] == 'both' and string[4:] in linestyles:
            self.gridaxis = string[:4]
            self.gridline = string[4:]
        else:
            logging.error("Invalid grid string argument. Please enter 'axis'+'linestyle' string, e.g. 'y:' or 'x--'")
    
    
    def set_axislabels(self, fontsize: float =None, **labels_kw) -> None:
        """ Set axis labels (also called titles here) according to user input """
        
        if fontsize:
            self.fontsize = fontsize
        
        if isinstance(labels_kw, dict):
            
            for key, value in labels_kw.items():
                if   key in self.xtitles_dict.keys():
                    self.xtitles_dict[key] = value
                elif key in self.ytitles_dict.keys():
                    self.ytitles_dict[key] = value
                else:
                    print("Key not valid") #logging
        
        else:
            print(f"{labels_kw} is not a dictionary")
        
        
    def fontsize_options(self, title: str =None, labels: str =None, ticks: str =None) -> None:
        """ Control fontsizes of title, axis labels, axis ticks labels """
        
        if title:
            self.mastersize = title
        if labels:
            self.fontsize = labels
        if ticks:
            self.rcps['font.size'] = ticks
    
    
    def figure_options(self, **kwargs) -> None:

        for key, val in kwargs.items():
            setattr(self, key, val)
 
    
    def saveimage(self, name: str, dpi: int=None) -> None:
        
        self.fig.savefig(name, facecolor='white', transparent=False, dpi=dpi, bbox_inches='tight')

    #FIXME
    def show_content(self):
        """ Print out data content of histogram and returns pandas dataframe """
        
        if isinstance(self.data, bh.Histogram):
            pass
        
        elif isinstance(self.data, pd.core.frame.DataFrame):
            print(self.data)
        
        else:
            pass

#FIXME: This is not a 1D histogram class. It is a canvas class for plots of 1D histograms
class Hist1D(EmptyPlot):
    
    
    def __init__(
        self, 
        observable: str, 
        samples=[], 
        data=[], 
        labels={}, 
        errors: str =None, 
        logy: bool =None,
        logx: bool =None, 
        stack=False, 
        xlim : Tuple[float,float] = None,
        ylim : Tuple[float,float] = None,
        **kwargs
        ) -> None:
        
        super().__init__(**kwargs)
        
        # set histogram plot specific rcParams
        self.rcps.update({
            'legend.handletextpad': 0.3, # space between the legend handle and text
            'legend.columnspacing': 0.5,
            'legend.labelspacing' : 0.1, # vertical space between the legend entries
            'legend.markerscale'  : 1.1,
        })

        self.config_rcParams(self.rcps)
        self.obs      = observable
        self.samples  = samples
        self.data     = data
        self.is_stack = stack
        self.errors   = errors
        self.leglabels= labels
        self.logy     = logy
        self.logx     = logx
        self.xlim     = xlim
        self.ylim     = ylim

        self.samples_dict = {} # {'samplename': sample}
        self.histos_dict  = {} # {'samplename': sample (which will be plotted as histo bins)}
        self.histos_list  = [] # list of hist objects that will be plotted as histo bins
        self.data_dict    = {} # {'sameplname': sample (which will be plotted as data point)}
        self.plot_types   = {} # {'samplename': 'histo' or 'data'}
        self.colors_dict  = {} # {'samplename': 'color'}
        self.names         = []
        self.labels        = []
        self.histolabels   = []
        self.scatterlabels = []
        
        self.check_input()
        self.check_axis_limits()

        # default variables
        self.shape = 'full' if self.is_stack else 'hollow'
        self.need_grid = False
        self.legend_ncols = 1
        self.legend_loc = 'upper right'
        
        # list of basic 10 colors the class will automatically use (if number of plotted elements is less than 10)
        # (chosen from: https://matplotlib.org/stable/gallery/color/named_colors.html)
        self.color_order = [ 
            'red', 'blue', 'limegreen', 'orangered', 'magenta', 'yellow', 'aqua', 'chocolate', 'darkviolet','darkgreen'
        ]
        self.assign_colors()
        
        self.store_data()
    
    #TODO: Move to parent class and override. Check dimension of histogram object
    #TODO: Move to config file parser
    def check_input(self) -> None:
        
        if not self.samples:
            logging.error("Enter a non-empty list of samples to plot.")

        if not self.type_checker(self.samples, str):
            logging.error("Sample entry must be strings")

        if self.data and self.type_checker(self.data, str):
            if self.data != 'all':
                if not isinstance(self.data, list):
                    self.data = [self.data]
                    
                # check if given data (scatter) names are present in samples
                for samplename in self.data:
                    if samplename not in self.samples:
                        logging.error(f"There is no variable named {samplename} in 'samples'")

        if not isinstance(self.samples, list):
            self.samples = [self.samples]
    
        obj = None
        try:
            with open(self.dir + f"{self.obs}_file.pkl", 'rb') as file:
                print('Reading from file: '+file.name)
                obj = pickle.load(file)
        except:
            logging.error(f"There is no file named {self.dir}{self.obs}_file.pkl")
        
        if obj is None:
            logging.error(f"Could not load dictionary from {self.dir}{self.obs}_file.pkl")

        if not self.type_checker(obj, bh.Histogram):
            logging.error(f"The file {self.dir}{self.obs}.pkl does not contain a dict of hist objects")

        if not all(sname in obj for sname in self.samples):
            logging.error(f"A sample is not in the file {self.dir}{self.obs}_file.pkl")                

        #TODO: move to separate function
        self.samples_dict = obj
        for samplename in self.samples:
            #self.samples_dict[samplename] = obj[samplename]
            if samplename in self.data or self.data == 'all':
                self.data_dict[samplename] = obj[samplename]
                self.plot_types[samplename] = 'data'            #FIXME: redundant? Not used
            else:
                self.histos_dict[samplename] = obj[samplename]
                self.histos_list.append(obj[samplename])        #FIXME: redundant? Used in ratio plot, but can use histos_dict.items to the same end
                self.plot_types[samplename] = 'histo'           #FIXME: redundant? Not used

    def check_axis_limits(self,logx: bool = None, logy: bool = None, xlim: Tuple[float,float]= None, ylim: Tuple[float,float]=None) -> None:
        if logy: self.logy = True
        if logx: self.logx = True
        if xlim: self.xlim = xlim
        if ylim: self.ylim = ylim
        if self.ylim:
            if self.logy and self.ylim[0] == 0:
                logging.error(f"Cannot create a logarithmic y-scale with 0 minimum.")
        if self.xlim:
            if self.logx and self.xlim[0] == 0:
                logging.error(f"Cannot create a logarithmic x-scale with 0 minimum.")

    def store_data(self) -> None:
        
        # right now, this assumes all samples have same dim and length (should check for this)
        # thus, take the first sample to retrieve general info
        #if self.histos_dict:
        #    first_sample = self.histos_dict[next(iter(self.histos_dict))]
        #else:
        #    first_sample = self.data_dict[next(iter(self.data_dict))]
        if not self.samples_dict:
            logging.error(f"Missing samples dictionary.")
        first_sample = self.samples_dict[next(iter(self.samples_dict))]
        self.datasize, = first_sample.axes.size
        self.edges = list(first_sample.axes[0].edges)
        self.values = [list(x.values()) for x in self.samples_dict.values()]

        # store label and name variables
        for samplename, sample in self.samples_dict.items():
            name = sample.axes[0].name
            label = sample.axes[0].label
            self.names.append(name if name else '')
            self.labels.append(label if label else '')
            if samplename in self.data or self.data == 'all':
                self.scatterlabels.append(label)
            else:
                self.histolabels.append(label)

    def set_explabel(self, ax: mpl.axes.Axes, data=True, lumi=139) -> None:
        """ Set experimental label inside plot and scale y axis automatically to avoid collision with plot elements """
        
        # generate text
        #TODO: Why does this take so long? ~1.8s using mplhep
        #See issue here https://github.com/scikit-hep/mplhep/issues/338
        #See open discussion here https://github.com/scikit-hep/mplhep/discussions/382
        #See source code https://github.com/scikit-hep/mplhep/blob/master/src/mplhep/label.py
        if self.style == 'ATLAS':
            text = hep.atlas.label(ax=ax, label=self.logotext, data=data, lumi=lumi)
        elif self.style == 'LHCb1' or self.style == 'LHCb2':
            text = hep.lhcb.label(ax=ax, label=self.logotext, data=data, lumi=lumi)
        #print(text)
        #text = ax.text(0.05,0.1,'ATLAS')

        # evaluate all bbox edges of the text
        xarray = []
        yarray = []
        for label in text:
            position = label.get_position()
            T = ax.transAxes.inverted()
            bbox = label.get_window_extent(renderer = ax.figure.canvas.renderer)
            bbox_axes = bbox.transformed(T)
            points = bbox_axes.get_points().tolist()
            x = [xy[0] for xy in points]
            y = [xy[1] for xy in points]
            xarray += x
            yarray += y
            
        # get lowest point of edges which would collide with plot
        for x, y in zip(xarray, yarray):
            if y == min(yarray):
                lowest = (x, y)
        
        """
        The function used to scale y axis up, hep.plot.yscale_text() below, needs to
        detect AnchoredText objects to funcion correctly. For this reason, an invisible 
        AnchoredText object is created right below the text and only then the yscale 
        function is called
        """
        
        # create and put invisible AnchoredText object
        anch_text = AnchoredText(
            "", 
            loc='lower left', 
            bbox_to_anchor=lowest,
            bbox_transform=ax.transAxes,
            borderpad=0,
            frameon=False
        )
        ax.add_artist(anch_text)

        # I dont know why but an ax.scatter() function needs to be called before
        # the yscale function in order to not crash with an error...
        # I also found out that the yscale funcion to scale the y axis in case
        # of a big legend in the plot, also dont work without this scatter call
        ax.scatter(0, 0, visible=False)
        hep.plot.yscale_text(ax)
    
    
    def get_data_markers(self, as_list : bool = False) -> dict:
        data_markers = {}
        marker_list = []
        if not isinstance(self.rcps['lines.marker'], list):
            self.rcps['lines.marker'] = list(self.rcps['lines.marker'])
        for marker in self.rcps['lines.marker']:
            if marker not in self.markerstyles.keys():
                #TODO: warning message for invalid marker style
                self.rcps['lines.marker'].remove(marker)
        if len(self.rcps['lines.marker']) < len(self.data):
            #TODO: warning message for length of marker list, fetching from filled markers
            for filled_mark in list(mpl.markers.MarkerStyle.filled_markers):
                if filled_mark not in self.rcps['lines.marker']:
                    self.rcps['lines.marker'].append(filled_mark)
                if len(self.rcps['lines.marker']) >= len(self.data): break
        for i,samplename in enumerate(self.data):
            data_markers[samplename] = self.rcps['lines.marker'][i]
            marker_list.append(self.rcps['lines.marker'][i])
        if as_list: return marker_list
        else: return data_markers


    def assign_colors(self, custom: list =None, d : dict = None) -> None:
        """ Fills colors_dict accordingly """
        
        #for i, samplename in enumerate(self.samples_dict.keys()):
        samplelist = self.samples
        if d: samplelist = list(d.keys())

        j = 0
        ndata = len(self.data_dict.keys())
        for i, samplename in enumerate(samplelist):
            if custom:
                self.colors_dict[samplename] = custom[i]
            else:
                if samplename in list(self.data_dict.keys()):
                    cmaplist = self.colorlist_gen(ndata,'Greys',True,100,100-10*ndata)
                    self.colors_dict[samplename] = cmaplist[j]
                    j+=1
                elif len(samplelist) > 10 or self.is_stack:
                    cmaplist = self.colorlist_gen(len(samplelist))
                    self.colors_dict[samplename] = cmaplist[i]
                else:
                    self.colors_dict[samplename] = self.color_order[i]
        

    
    def get_samples_colors_labels(self, d: dict) -> Tuple[list, list, list]:
        """ Retrive the list of samples and the list of colors from dictionary of the form 'samplename: sample' """
        
        samples = list(d.values())
        colors = []
        labels = []
        for samplename in list(d.keys()):
            colors.append(self.colors_dict[samplename])
            labels.append(self.leglabels[samplename])
        
        return samples, colors, labels
        #if len(colors) == 1:
        #    return samples, colors[0]
        #else:
        #    return samples, colors
    
    
    def get_stackvalues(self, listofhist: list) -> list:
        """ Get total height values of a list of hist objects (with same edges, binwidths, etc.) """
        
        if len(listofhist) == 1:
            return listofhist[0].values()
        
        else:
            valueslist = []
            for h in listofhist:
                values = h.values()
                valueslist.append(values)
            
            return np.sum(valueslist, axis=0)
    
    
    def histbins_errs(self, ax: mpl.axes.Axes, ratio=False) -> None:
        """ Creates error bins on histbins using ax.bar """
        
        histlist, _clist, ___ = self.get_samples_colors_labels(self.histos_dict)
        
        # all hists have same bin edges and thus same bin centers and widths
        _centers, = histlist[0].axes.centers
        _width, = histlist[0].axes.widths
        
        # if stack plot, put error only on the total height
        if self.is_stack:
            values = self.get_stackvalues(histlist)
            poisson = np.sqrt(values)
            
            # if ratio is True, this function is used to plot histbin errors on a ratio plot
            if ratio:
                heights = 2 * (((poisson + values) / values) - 1)
                _bottom = 1 - (((poisson + values) / values) - 1)
            else:
                heights = 2*poisson
                _bottom = values - poisson

            ax.bar(
                _centers,
                heights,
                width=_width,
                bottom=_bottom,
                fill=False,
                linewidth=0,
                alpha=0.5,
                hatch='/////',
                label='Uncertainty'
            )
        
        else:
            for i, H in enumerate(histlist):
                values = H.values()
                poisson = np.sqrt(values)

                # if ratio is True, this function is used to plot histbin errors on ratio plot
                if ratio:
                    heights = 2 * (((poisson + values) / values) - 1)
                    _bottom = 1 - (((poisson + values) / values) - 1)
                else:
                    heights = 2*poisson
                    _bottom = values - poisson

                ax.bar(
                    _centers,
                    heights,
                    width=_width,
                    bottom=_bottom,
                    fill=False,
                    linewidth=0,
                    edgecolor=_clist[i],
                    alpha=0.5,
                    hatch='/////',
                    label= 'Uncertainty' if _clist[i] == 'black' else None #FIXME: Why?
                )
        
    
    def scatterdata_plotter(self, _ax: mpl.axes.Axes, data: list =None) -> None:
        """ Main function to plot scatter data points """
        
        H, _clist, _llist = self.get_samples_colors_labels(self.data_dict)
        markers = self.get_data_markers(as_list = True)
        if data:
            H = data
            _bins = self.edges
        else:
            _bins = None
        
        # yerr=True in hep.histplot uses Poisson errors (sqrtN)
        if self.errors == 'data' or self.errors == 'all':
            _yerr = True
        else:
            _yerr = False

        hep.histplot(
            H,
            bins=_bins,
            ax=_ax, 
            stack=self.is_stack, 
            yerr=_yerr, 
            histtype='errorbar',
            color=_clist,
            marker = markers,
            markersize=self.rcps['lines.markersize'],
            label=_llist
        )
    
    
    def histbins_plotter(self, _ax: mpl.axes.Axes, data: list =None) -> None:
        """ Main functin to plot histogram bins """
        
        H, _clist, _llist = self.get_samples_colors_labels(self.histos_dict)
        if data:
            H = data
            _bins = self.edges
        else:
            _bins = None
    
        if self.shape == 'hollow':
            hep.histplot(
                H,
                bins=_bins,
                ax=_ax,
                stack=self.is_stack,
                yerr=False,
                color=_clist,
                linewidth=self.rcps['lines.linewidth'],
                label=_llist
            )
        
        elif self.shape == 'full':            
            hep.histplot(
                H,
                bins=_bins,
                ax=_ax,
                stack=True,
                yerr=False,
                histtype='fill',
                facecolor=_clist,
                edgecolor='black',
                linewidth=self.rcps['lines.linewidth'],
                label=self.histolabels
            )

        
    def hist_plot(self, ax: mpl.axes.Axes) -> None:
        """ Main plot function """
        
        if self.histos_dict:
            self.histbins_plotter(ax)
        
        if self.data:
            self.scatterdata_plotter(ax)
        
        # currently, errors are only Poisson (sqrtN) for each bin
        if self.errors == 'hist' or self.errors == 'all':
            self.histbins_errs(ax)
                  
        # adjust ticks
        self.set_tickparams(ax, self.rcps['font.size'])
        
        # show full numbers without scientific notation
        #ax.ticklabel_format(style='scientific')
        ax.yaxis.get_offset_text().set_fontsize(self.rcps['font.size'])
        ax.xaxis.get_offset_text().set_fontsize(self.rcps['font.size'])
        
        if self.need_grid:
            ax.grid(axis=self.gridaxis, linestyle=self.gridline, alpha=0.3, color='k')
            
        self.set_legend(ax)
        
        # add atlas logo and text
        self.set_explabel(ax)
                
        # scale ylim automatically for optimal legend placement
        #hep.plot.yscale_legend(ax) # gives error if ATLAS label is not plotted yet (idk why)
        
        # set master title
        ax.set_title(self.mastertitle, fontsize=self.mastersize)
        
        # set x and y axis labels
        self.set_xtitles(ax, 'xmain', self.fontsize)
        self.set_ytitles(ax, 'ymain', self.fontsize)

        # set range of axes
        if self.xlim: ax.set_xlim(self.xlim)
        if self.ylim: ax.set_ylim(self.ylim)
        if self.logx: ax.set_xscale('log')
        if self.logy: ax.set_yscale('log')
        
    
    def set_legend(self, ax: mpl.axes.Axes) -> None:
        """ Create legend for main plot """
        
        # should make ncol be detected automatically
        ax.legend(
            ncol=self.legend_ncols, 
            handlelength=mpl.rcParams['legend.handleheight']+0.04, 
            fontsize=self.fontsize,
            markerscale=self.rcps['legend.markerscale'],
            labelspacing=self.rcps['legend.labelspacing'],
            handletextpad=self.rcps['legend.handletextpad'],
            loc=self.legend_loc
        )
        
        # sort legend entries
        hep.sort_legend(ax)
        #if hep.plot.overlap(ax, hep.plot._draw_leg_bbox(ax)):
        #hep.plot.yscale_legend(ax) #FIXME: done iteratively in mplhep backend and takes too long.
        
    def colorlist_gen(self, n: int, colormap='gist_rainbow', reverse=False, max=98, min=2) -> list:
        """ Create custom color list of length n from a given colormap """
        
        clist = []
        pct_max, pct_min = max, min # max and min percentile of color ramp
        cmap = mpl.cm.get_cmap(colormap)
        
        # list of values between 0.00 and 1.00; length equals length of data source
        sequence = list(i/100 for i in (np.arange(pct_min, pct_max, (pct_max-pct_min)/n)))
        
        # reverse if required
        if reverse:
            sequence = reversed(sequence)
        
        # create list of colors
        for i in sequence:
            color = cmap(i) 
            clist.append(color)
        
        return clist
        
    
    def plot_options(
        self, 
        shape: str = None, 
        gridstring = '', 
        marker: str = None, 
        markersize: float = None, 
        legendcols: int = None,
        legendloc: str = None,
        logy: bool = None,
        logx: bool = None,
        xlim: Tuple[float,float] = None,
        ylim: Tuple[float,float] = None,
        rcp_kw = {}
    ) -> None:
        
        # select shape of plotted data
        if shape:
            if shape == 'full' and (not self.is_stack) and len(self.histos_dict) > 1:
                logging.error("Cannot select a full shape if it's not a stack plot")
            elif shape == 'full' or shape == 'hollow':
                self.shape = shape
            else:
                logging.error("'shape' must be either 'full' or 'hollow'")
        
        # select grid options
        # TO DO: option to make able to use all of ax.grid() kwargs
        if gridstring:
            self.gridstring_converter(gridstring)
            self.need_grid = True
        
        # update rcp dictionary if passed
        self.rcps.update({k: v for k, v in rcp_kw.items() if k in mpl.rcParams})
        self.config_rcParams(self.rcps)
        
        # set marker style and marker size if passed
        # must be done manually to bypass mpl.rcParams (cannot interpret string) 
        if marker:
            if all(m in self.markerstyles.keys() for m in marker):
                self.rcps['lines.marker'] = marker
        if markersize:
            self.rcps['lines.markersize'] = markersize
        
        # change number of columns in the legend
        if legendcols:
            self.legend_ncols = legendcols
        
        # change location of legend
        if legendloc:
            self.legend_loc = legendloc
        
        # if it is a stack plot but the shape is hollow, use color_order
        # (otherwise would automatically switch to default colormap)
        if self.is_stack and shape == 'hollow' and len(self.samples) <= 10:
            self.assign_colors(self.color_order)

        self.check_axis_limits(logx,logy,xlim,ylim)

    
    def color_options(self, colors=[], colormap='', reverse=False) -> None:
        """ Allow user to enter custom colors for histos and data plots """

        self.assign_colors(None, self.data_dict)
        if colors and self.type_checker(colors, str):

            if not isinstance(colors, list):
                colors = [colors]
            if len(colors) != len(self.histos_dict.keys()):
                logging.error("Length mismatch between color list and total samples list")
            else:
                self.assign_colors(colors, self.histos_dict)
                    
        elif colormap and self.type_checker(colormap, str):
            if colormap in plt.colormaps():
                self.assign_colors(self.colorlist_gen(len(self.samples), colormap, reverse),self.histos_dict)
            else:
                logging.error("Invalid matplotlib colormap; choose from https://matplotlib.org/stable/gallery/color/colormap_reference.html")
        
    
    def create(self, save_name='', dpi=1000) -> None:
        
        # create plot figure and subplots
        self.create_canvas()
        self.make_grid()
        self.ax = self.make_subplot(0, 1, 0, 1)
        #print(self.ax)
        
        # make plot
        self.hist_plot(self.ax)
        
        if save_name:
            self.saveimage(save_name, dpi)


            
            
class RatioPlot(Hist1D):
    
    
    def __init__(
        self, 
        samples=[], 
        reference: str =None, 
        data=[], 
        errors: str =None, 
        logy: bool = None,
        logx: bool = None,
        ylim: Tuple[float,float] = None,
        xlim: Tuple[float,float] = None, 
        stack=False, 
        **kwargs
        ) -> None:
        
        super().__init__(
            samples=samples, 
            data=data, 
            errors=errors, 
            logy=logy, 
            logx=logx,
            ylim=ylim,
            xlim=xlim, 
            stack=stack, 
            layout=(2,1), 
            **kwargs
            )
        self.check_input
        
        self.reference = reference
        
        self.numerators = {}
        self.denominator = {}
        self.dvals = []
        
        self.check_reference()
        self.ratiovalues_calculator()
        
        # default variables
        self.spacing = 0
        self.stretch = 4
            
        # bool if user put a custom y limits for bot plot
        self.custom_ylims = False
        
    
    def check_reference(self) -> None:
        
        if self.reference:
            if self.reference in self.samples:
                for samplename, sample in self.samples_dict.items():
                    if samplename == self.reference:
                        self.denominator[samplename] = sample
                        self.dvals = list(next(iter(self.denominator.values())).values())
                    elif samplename in self.samples:
                        self.numerators[samplename] = sample
            elif self.reference == 'total':
                if self.data and len(self.data) == 1:
                    self.numerators = self.data_dict
                    self.dvals = self.get_stackvalues(self.histos_list)
                else:
                    logging.error("Please specify one (and only one) sample that will be plotted as data using the 'data' argument")
            #elif self.reference == 'data':
            #    self.denominator = self.data_dict
            #    for samplename, sample in self.samples_dict.items():
            #        if samplename in self.samples:
            #            self.numerators[samplename] = sample
            #            self.dvals = list(next(iter(self.denominator.values())).values())

            else:
                logging.error("Selected reference is not in 'samples'")
        else:
            logging.error("Specify a reference sample which will act as the denominator for the ratio plot")
    
    
    def ratiovalues_calculator(self) -> None:
        """ Calculate and store ratio values of specified samples (numerators) """
        
        self.ratiovalues = {}
        for samplename, sample in self.numerators.items():
            self.ratiovalues[samplename] = []
            for n, m in zip(sample.values(), self.dvals):
                if m != 0:
                    self.ratiovalues[samplename].append(n/m)
                else:
                    self.ratiovalues[samplename].append(0)
    
    
    def ratio_scatters(self, samplename: str, color: str) -> None:
        """ Used when need to plot ratio values in bot plot as scatter points """

        markers = self.get_data_markers()
        markerstyle = None
        if samplename in markers.keys(): 
            markerstyle = markers[samplename]

        hep.histplot(
            # np.ones(len(self.ratiovalues[samplename])),
            self.ratiovalues[samplename],
            bins=self.edges,
            ax=self.botax,
            yerr=False, 
            histtype='errorbar',
            color=color,
            marker=markerstyle,
            markersize=self.rcps['lines.markersize'],
        )
        
    
    def ratio_histbins(self, samplename: str, color: str) -> None:
        """ Used when need to plot ratio values in bot plot as hist bins """

        if self.shape == 'hollow':
            self.botax.stairs(
                self.ratiovalues[samplename], 
                self.edges, 
                baseline=1,
                color=color,
                fill=False,
                linewidth=self.rcps['lines.linewidth'],
            )
        
        else:            
            self.botax.stairs(
                self.ratiovalues[samplename], 
                self.edges, 
                baseline=1,
                edgecolor='black',
                facecolor=color,
                fill=True,
                linewidth=self.rcps['lines.linewidth'],
            )
        
        
    def custom_yaxis(self, ylims: list, step: float =None, edges=False) -> None:
        """
        Allow user to manually change the bot y axis limits, which can often
        overlap with various other plot elements. If edges is set to True,
        the first and last ticks will be shown in the plot.
        """
        
        if step is None:
            # do something
            step = step
        
        self.custom_ylims = True
        
        self.ylims = ylims
        self.ystep = step
        self.ybotrange = np.arange(ylims[0], ylims[-1]+step, step)
        
        # check if any tick label would have non zero decimal places,
        # if so, leave zeros for all other tick labels as well
        # if not, remove all decimal zeros from tick labels
        temprange = [f'{x:.2f}' for x in self.ybotrange]
        need1 = False
        need2 = False
        
        for num in temprange[1:-1]:
            decimals = num.split('.')[1]
            d1 = decimals[0]
            d2 = decimals[1]
            
            if d2 != '0':
                need2 = True
                break
            if d1 != '0':
                need1 = True
        if need2:
            self.ybotlabels = [f'{x:.2f}' for x in self.ybotrange]
        elif need1:
            self.ybotlabels = [f'{x:.1f}' for x in self.ybotrange]
        else:
            self.ybotlabels = [f'{x:.0f}' for x in self.ybotrange]            
        
        if not edges:
            self.ybotlabels[0] = ''
            self.ybotlabels[-1] = ''
    
    
    def main_plot(self) -> None:
        
        self.hist_plot(self.mainax)
        
        # set x axis ticks
        #self.mainax.set_xticks(np.linspace(self.edges[0], self.edges[-1], 11))
        self.mainax.set_xticklabels([]) # suppress x tick labels
    
    
    def bot_plot(self) -> None:

        ___, _clist, ___ = self.get_samples_colors_labels(self.numerators)
        if type(_clist) != list:
            _clist = [_clist]
        
        # iterate through all samples in self.numerators along with corresponding color
        for i, samplename in enumerate(self.numerators.keys()):
            if samplename in self.data or self.data == 'all':
                self.ratio_scatters(samplename, _clist[i])
            else:
                self.ratio_histbins(samplename, _clist[i])
        
        # plot error histograms
        if self.errors == 'hist' or self.errors == 'all':
            self.histbins_errs(self.botax, ratio=True)
            
        # set tick params
        self.set_tickparams(self.botax, self.rcps['font.size'])
        
        # set x ticks
        self.botax.set_xticks(np.linspace(self.edges[0], self.edges[-1], 11))
        
        # set x and y axis labels
        self.set_xtitles(self.botax, 'xbot', self.fontsize)
        if self.ytitles_dict['ybot']:
            self.set_ytitles(self.botax, 'ybot', self.fontsize)
        else:
            self.botax.set_ylabel(f"Ratio against \n{self.leglabels[self.reference]}", fontsize=self.fontsize)
        
        # draw horizontal line at y=1
        self.botax.axhline(1, -1, 2, color='k', linestyle='--', linewidth=0.7)

        # in case there is custom y lims
        if self.custom_ylims:
            self.botax.set_ylim(self.ylims)
            self.botax.set_yticks(self.ybotrange)
            self.botax.set_yticklabels(self.ybotlabels, fontsize=self.rcps['font.size'])

        if self.xlim: self.botax.set_xlim(self.xlim)
        if self.logx: self.botax.set_xscale('log')
                
        # put grid if requested
        if self.need_grid:
            self.botax.grid(axis=self.gridaxis, linestyle=self.gridline, alpha=0.3, color='k')
        
    
    def ratio_plot(self) -> None:
        
        # main plot
        self.main_plot()

        # ratio plot
        self.bot_plot()

    
    def ratio_options(self, ylims=[], step: float = None, edges=False) -> None:
        
        self.custom_yaxis(ylims, step, edges)
    
    
    def figure_options(self, spacing: float = None, stretch: int = None, **figkw) -> None:
        
        super().figure_options(**figkw)
        if spacing:
            self.spacing = spacing
        if stretch:
            self.stretch = stretch

    
    def create(self, save_name='', dpi=1000) -> None:
        
        # create plot figure and subplots
        self.create_canvas()
        self.make_grid(hspace=self.spacing, height_ratios=[self.stretch,1])
        self.mainax = self.make_subplot(0, 1, 0, 1)
        self.botax  = self.make_subplot(1, 2, 0, 1)
        # make plot
        self.ratio_plot()
        
        if save_name:
            self.saveimage(save_name, dpi)
      
            
class PullPlot(EmptyPlot):

    
    def __init__(self, pd_obj, **kwargs):

        super().__init__(**kwargs)
        self.data = pd_obj
        self.store_data()

        self.set_figsize()
        
        self.use_custom_range = False
        self.labelside = 'right'
        self.onesigmacolor = 'limegreen'
        self.twosigmacolor = 'yellow'
        self.logotext = "Internal"

        # errorbar_kw are keyword argyments from the matplotlib function ax.errorbar:
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html
        self.errorbar_kw = {
            'color'     : 'k',
            'fmt'       : 'o',
            'markersize': 3,
            'elinewidth': 1
        }
        self.xtitles_dict['xmain'] = r'$(\hat{\theta}-\theta)/\Delta\theta$'
    

    def set_figsize(self):
        """ Variable figure length based on number of data points """
        
        n = self.nvariables
        ly = 0.4012*n**(0.763) # empiric formula from manually measured numbers and fitted with excel
        self.figsize = (2,ly)  # WARNING: starts to deviate at around n > 140
    
    
    def store_data(self):
        
        self.values      = self.data[1] # pandas series
        self.pos_err     = self.data[2] # pandas series
        self.neg_err     =-self.data[3] # pandas series
        self.data_labels = self.data.index.to_list() # list
        self.nvariables  = len(self.values)
        
        # central value of the pull plot
        self.center = self.values[0]
    
    
    #FIXME: CURRENTLY NOT USED
    def generate_cells(self):
        """ Function used when there is more than one entry per bin """
        
        # need to think a bit about this feature
        
        # print(self.data_container[0].iloc[0].to_list())
        cellsize = len(self.data_container) # how many entries one cell contains
        cells = [[self.data_container[j].iloc[i].to_list() for j in range(cellsize)] for i in range(len(self.data_container[0]))]
        print(cells)
        gap = 0.1
    
    
    def set_yaxis(self):
        """ Set y axis and y axis ticks """
        
        # set numerical limits of plot
        self.ax.set_ylim(-1, self.nvariables)
        
        # put ticklabels accordingly
        if self.labelside == 'right':
            self.ax.yaxis.tick_right()
        elif self.labelside == 'left':
            self.ax.yaxis.tick_left()
        
        # put variable names onto axis
        self.ax.set_yticks(
            self.ypos, 
            labels=self.data_labels, 
            fontsize=self.rcps['font.size'],
        )
        
    
    def set_xaxis(self):
        """ Set x axis range either automatically or using user input """
        
        # if user provided x axis ranges
        if self.use_custom_range:
            xmin = self.user_xmin
            xmax = self.user_xmax
            
        else:
            # retrieve highest value in data
            longest = ceil(max([max(self.neg_err), max(self.pos_err)]))
            nice_range = longest + 2
            xmin = -nice_range+self.center
            xmax = nice_range+self.center

        self.ax.set_xlim(xmin, xmax)
        self.ax.set_xticks(np.arange(xmin, xmax+1))
        
        # xticklabels_kw from: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xticklabels.html
        self.ax.set_xticklabels(
            [str(int(x)) for x in np.arange(xmin, xmax+1)], 
            fontsize=self.rcps['font.size'],
        )
        
    
    def pull_plot(self):
        """ Main plotting function """
        
        # define base transformations and rotation transformations
        base = self.ax.transData
        rot = transforms.Affine2D().rotate_deg(90)
        
        # create arrays for errobar plot
        self.ypos = np.arange(self.nvariables)
        self.xerrs = pd.concat([self.neg_err, self.pos_err], axis=1).T

        # make plot
        self.ax.errorbar(self.values, self.ypos, xerr=self.xerrs, **self.errorbar_kw)
        
        # put yellow and green bands
        self.ax.fill_between([-2+self.center, 2+self.center], -1, self.nvariables, color=self.twosigmacolor)
        self.ax.fill_between([-1+self.center, 1+self.center], -1, self.nvariables, color=self.onesigmacolor)
        
        # put dotted line in the center value
        self.ax.axvline(self.center, color='k', linestyle='--', linewidth=0.6, ymin=-1, ymax=2) # ymin, ymax to fix bug
        
        # set x and y axis
        self.set_xaxis()
        self.set_yaxis()
        
        # remove axis ticks for left and right axis of plot
        self.ax.tick_params(which='both', bottom=True, left=False, top=True, right=False)
        
        # set title
        self.ax.set_title(self.mastertitle, fontsize=self.rcps['axes.titlesize'])
        
        # set x and y axis labels
        self.set_xtitles(self.ax, 'xmain', self.fontsize, loc='center')
        self.set_ytitles(self.ax, 'ymain', self.fontsize, loc='center')
        
        # display atlas logo
        hep.atlas.text(self.logotext, ax=self.ax, loc=0)

    
    def figure_options(self, labelside=None, **figkw):
        
        # manual change of fig size
        super().figure_options(**figkw)
        if 'figsize' in figkw.keys():
            logging.warning("Manually changing the figure size")
        
        if labelside == 'right' or labelside == 'left':
            self.labelside = labelside
    
    
    def plot_options(self, center=None, rangelist=None, rcp_kw={}, **errorbar_kw):
                
        # update rcp dictionary if passed
        self.rcps.update({k: v for k, v in rcp_kw.items() if k in mpl.rcParams})
        self.config_rcParams(self.rcps)
        
        # update errorbar keywords if passed
        self.errorbar_kw.update(errorbar_kw)
        
        # update central value
        if center != None:
            self.center = center
        
        # allow user to enter custom range for the x axis
        # rangelist = [xmin, xmax]
        if rangelist:
            if isinstance(rangelist, list) and len(rangelist) == 2:
                self.rangelist = rangelist
                self.user_xmin = self.rangelist[0]
                self.user_xmax = self.rangelist[1]
                self.use_custom_range = True
    
    
    def color_options(self, marker=None, onesigma=None, twosigma=None):
        
        self.onesigmacolor = onesigma
        self.twosigmacolor = twosigma
        
        if marker:
            self.errorbar_kw['color'] = marker
        
        
    def create(self, save_name='', dpi=1000):
        
        # create plot figure and ax
        self.create_canvas()
        self.make_grid()
        self.ax = self.make_subplot(0, 1, 0, 1)        
        
        # make plot
        self.pull_plot()
        # self.fig.set_tight_layout(True) # tightlayout might be useful?
        
        if save_name:
            self.saveimage(save_name, dpi)
      
            
class ProjectionPlot(EmptyPlot):
    
    
    def __init__(self, obj, **kwargs):
        
        super().__init__(layout=(5,3), **kwargs)
        self.hist = obj
        self.set_color() # set default colormap
        
        # default attributes
        self.spacing = 0.15
        self.stretch = 4.
        self.need_grid = False
        self.cbar_space = '15%'
        self.cbar_size = '5%'
        self.xtitles_dict['xcbar'] = ''
        self.figsize = (8,8)
        self.norm = None
        self.logz = None
        
        self.store_data(self.hist)
    
        
    def store_data(self, obj):
        """ Retrieve x and y data from obj """
        
        self.pd_data = pd.DataFrame(obj.to_numpy()[0])
        self.xsum = self.pd_data.sum(axis=0).to_list()
        self.ysum = self.pd_data.sum(axis=1).to_list()
        self.xedges = [x for [x] in [list(obj.axes.edges[0][i]) for i in range(len(obj.axes.edges[0]))]]
        self.yedges = [y for y in obj.axes.edges[1][0]]
        self.vmin = min(self.pd_data)
        self.vmax = max(self.pd_data)
    
    def side_plots(self):
        """ Make vertical and horizontal plots """
        
        # horizontal plot
        hep.histplot(
            self.xsum, 
            bins=self.xedges, 
            ax=self.h_ax, 
            color='k', 
            zorder=1
        )
        self.set_h_ax()

        # adjust ticks
        #self.h_ax.ticklabel_format(style='plain')
        for ytick in self.h_ax.yaxis.get_major_ticks():
            ytick.label.set_fontsize(self.rcps['font.size'])
        
        # vertical plot
        hep.histplot(
            self.ysum, 
            bins=self.yedges, 
            ax=self.v_ax, 
            color='k', 
            zorder=1, 
            orientation='horizontal'
        )
        self.set_v_ax()

        # adjust ticks
        #self.v_ax.ticklabel_format(style='plain')
        for xtick in self.v_ax.xaxis.get_major_ticks():
            xtick.label.set_fontsize(self.rcps['font.size'])
        
        # put grid on both subplots if needed
        if self.need_grid:
            self.h_ax.grid(linestyle=self.gridline, alpha=0.3, color='k', axis='x')
            self.h_ax.grid(linestyle=self.gridline, alpha=0.3, color='k', axis='y', which='minor')
            self.v_ax.grid(linestyle=self.gridline, alpha=0.3, color='k', axis='y')
            self.v_ax.grid(linestyle=self.gridline, alpha=0.3, color='k', axis='x', which='minor')
            self.h_ax.set_axisbelow(True)
            self.v_ax.set_axisbelow(True)
        
        
    def main_plot(self):
        """ Main plot function """
        
        hep.hist2dplot(
            self.hist, 
            ax=self.main_ax, 
            zorder=2, #FIXME draw last to hide weird square created with pcolor
            cbar=False,
            norm=self.norm
        )
        
        # main plot
        _xrange = np.arange(self.xedges[0], self.xedges[-1]+0.5, 0.5)
        xlabel_list = [f'{x:.1f}' for x in _xrange]
        _yrange = np.arange(self.yedges[0], self.yedges[-1]+0.5, 0.5)
        ylabel_list = [f'{y:.1f}' for y in _yrange]
        
        # x axis
        self.main_ax.set_xticks(_xrange) #FIXME:_xrange
        self.main_ax.set_xticklabels(xlabel_list, fontsize=self.rcps['font.size'])
        
        # y axis
        self.main_ax.set_yticks(_yrange) #FIXME: _yrange
        self.main_ax.set_yticklabels(ylabel_list, fontsize=self.rcps['font.size'])
        
        # set title
        self.fig.suptitle(self.mastertitle, fontsize=self.rcps['axes.titlesize'])
        
        # set x and y axis labels
        self.set_xtitles(self.main_ax, 'xmain', self.fontsize, loc=self.rcps['xaxis.labellocation'])
        self.set_ytitles(self.main_ax, 'ymain', self.fontsize, loc=self.rcps['yaxis.labellocation'])
        self.set_xtitles(self.v_ax, 'xright', self.fontsize, loc=self.rcps['xaxis.labellocation'])
        self.set_ytitles(self.h_ax, 'ytop', self.fontsize, loc=self.rcps['yaxis.labellocation'])
        
        #FIXME: put atlas logo -> generalise Hist1D::set_explabel
        hep.atlas.text(self.logotext, ax=self.title_ax, loc=2)

        #plot colour bar
        im = self.main_ax.pcolor(self.hist, norm=self.norm, cmap=mpl.cm.get_cmap(self.user_cmap))
        self.cax.tick_params(axis='y', which='both', length=5, labelsize=10)
        cbar = self.fig.colorbar(im,cax=self.cax, orientation="horizontal")
        cbar.ax.tick_params(labelsize=10)
        cbar.set_label(self.xtitles_dict['xcbar'], loc='center', fontsize = self.rcps['font.size'])

        #TODO: set x and y axis log scale options and limits

    #TODO: Set projection plot axis limits   
    def set_h_ax(self, **hax_kw):
        """ Horizonthal subplot """
        
        self.hax_kw = {
            'axis'       :'x',
            'labelbottom': False,
            'labelsize'  : 5
        }
        self.hax_kw.update(hax_kw)
                
        #self.h_ax.set_xlim(-1, 1)
        self.h_ax.tick_params(**self.hax_kw)
        if self.logz:
            self.h_ax.set_yscale('log')
        
    #TODO: Set projection plot axis limits
    def set_v_ax(self, **vax_kw):
        """ Vertical subplot """
        
        self.vax_kw = {
            'axis'     :'y',
            'labelleft': False,
            'labelsize': 5
        }
        self.vax_kw.update(vax_kw)
                
        # self.v_ax.set_ylim(-1, 1)
        self.v_ax.tick_params(**self.vax_kw)
        if self.logz:
            self.v_ax.set_xscale('log')

    
    def plot_options(self, gridstring='', rcp_kw={}, logz=None, vmin=None, vmax=None):
                        
        # update rcp dictionary if passed
        self.rcps.update({k: v for k, v in rcp_kw.items() if k in mpl.rcParams})
        self.config_rcParams(self.rcps)

        # grid options
        if gridstring:
            self.gridstring_converter(gridstring)
            self.need_grid = True
        
        if vmin: self.vmin = vmin
        if vmax: self.vmax = vmax
        if logz:
            self.logz=True
            if self.vmin == 0:
                logging.error(f"Cannot set logarithmic z-scale with minimum of 0")
            self.norm = colors.LogNorm(self.vmin,self.vmax)
        elif vmin or vmax:
            self.norm = colors.Normalize(vmin=self.vmin,vmax=self.vmax)
        #TODO: add functionality for other options https://matplotlib.org/stable/tutorials/colors/colormapnorms.html
    
    
    def color_options(self, colormap=None, reverse=False):
        
        self.set_color(colormap, reverse)

        
    def create(self, save_name='', dpi=1000):
        
        # create plot figure and subplots
        self.create_canvas()

        cbarsize = float(self.cbar_size.strip('%'))/100.
        cbarspace = float(self.cbar_space.strip('%'))/100.
        #cbarwidth = self.stretch/(1.-cbarsize-cbarspace)-self.stretch #in case of cbar=True in hist2dplot

        self.make_grid(
            hspace=0,#self.spacing, 
            wspace=0,#self.spacing, 
            height_ratios=[1, self.spacing,self.stretch, self.stretch*cbarspace, self.stretch*cbarsize], 
            width_ratios=[self.stretch,self.spacing,1]
        )
        self.h_ax = self.make_subplot(0, 1, 0, 1 ) # horizonthal subplot
        self.v_ax = self.make_subplot(2, 3, 2, 3 ) # vertical subplot
        self.main_ax = self.make_subplot(2, 3, 0, 1) # main subplot
        self.cax = self.make_subplot(4, 5, 0, 1) # colorbar
        self.title_ax = self.make_subplot(0, 1, 2, 4)
        self.title_ax.axis('off')

        # make plot
        self.side_plots()
        self.main_plot()
        
        if save_name:
            self.saveimage(save_name, dpi)
            
class CMatrixPlot(EmptyPlot):
    
    
    def __init__(self, obj, threshold, **kwargs):        
        
        super().__init__(**kwargs)
        self.hist = obj
        
        # cut original data
        self.hist = self.cut_data(threshold)
        self.list_vals = self.hist.index.to_list()
        
        # set figsize based on data size
        n = len(self.hist)
        self.figsize = (n/3, n/3)
        
        # set default colormap
        self.set_color(colormap='bwr')
        
        # default attributes
        self.setcbar = False
        self.decimal = 1
    
    
    def cut_data(self, threshold):
        """ Filter correlation data based on numerical threshold """
        """ 
        FIXME: currently, if any data is lower than threshold, entire row/column
              gets cut, need adjustments
        """
        
        data = self.hist
        
        # filter rows
        data = data[abs(data.iloc[0]) >= threshold]
        
        # filter columns based on filtered rows
        data = data.loc[:,[x for x in data.index]]
        
        return data*100

        
    def c_matrix(self, **kwargs):

        # plot the heatmap
        im = self.ax.imshow(self.hist, **kwargs, cmap=mpl.cm.get_cmap(self.user_cmap))
        
        # set color limits to -1, 1 (which is the values correlation can take)
        im.set_clim(-100,100)
        
        if self.setcbar:
            # create new ax for colorbar
            cax = self.fig.add_axes(
                [self.ax.get_position().x1 + 0.01, self.ax.get_position().y0, 0.03, self.ax.get_position().height]
            )
            cbar = self.fig.colorbar(im, cax=cax)

            # change range of colorbar
            cax.set_yticks(np.arange(-100, 101, 25))
            cax.set_yticklabels(np.arange(-100, 101, 25), fontsize=10)
            
            # reduce tick size of colorbar
            cax.tick_params(axis='y', which='both', length=5)

        # set variable names as axis tick labels
        self.ax.set_xticks(np.arange(len(self.list_vals)), labels=self.list_vals, fontsize=self.rcps['font.size'])
        self.ax.set_yticks(np.arange(len(self.list_vals)), labels=self.list_vals, fontsize=self.rcps['font.size'])
        
        # rotate x axis labels
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        
        # format entries to one decimal place
        valfmt = mpl.ticker.StrMethodFormatter('{x:.1f}')
        
        # put text in cells
        for i in range(len(self.list_vals)):
            for j in range(len(self.list_vals)):
                self.ax.text(
                    j, 
                    i, 
                    valfmt(self.hist.iloc[i][j], None), 
                    ha='center', # horizontal alignment
                    va='center', # vertical alignment
                    color='k', 
                    size=self.rcps['font.size']
                )
        
        # reset minor ticks
        self.ax.set_xticks(np.arange(len(self.list_vals)+1)-0.5, minor=True)
        self.ax.set_yticks(np.arange(len(self.list_vals)+1)-0.5, minor=True)
        
        # set dotted line internal grid
        self.ax.grid(which='minor', color='k', linestyle='--', linewidth=1)
        
        # remove the axis ticks on every side
        self.ax.tick_params(which='both', bottom=False, left=False, top=False, right=False)
        
        # set master title
        self.fig.suptitle(self.mastertitle, fontsize=self.rcps['axes.titlesize'])
        
        # put atlas logo
        hep.atlas.text(self.logotext, ax=self.ax, loc=0)
    
    
    def figure_options(self, **figkw):
        
        super().figure_options(**figkw)
    
    
    def plot_options(self, setcbar=False, decimal=1, rcp_kw={}):
        
        self.setcbar = setcbar
        self.decimal = decimal
    
    
    def color_options(self, colormap=None, reverse=False):
        
        self.set_color(colormap, reverse)
        
        
    def create(self, save_name='', dpi=1000):
        
        # create plot figure and ax
        self.create_canvas()
        self.make_grid()
        self.ax = self.make_subplot(0, 1, 0, 1)
        
        # make plot
        self.c_matrix()
        
        if save_name:
            self.saveimage(save_name, dpi)