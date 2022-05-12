import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import mplhep as hep
import boost_histogram as bh
import hist
import pandas as pd
import numpy as np
import logging
import pickle




class EmptyPlot(object):
    
    
    def __init__(self, title="", layout=(1,1), size=(6.4,4.8), style='ATLAS', directory='') -> None:
        
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
        
        # common rcParams to all (or most) plot types
        self.rcps = {
            'xaxis.labellocation' : 'right', # location of x label w.r.t. x axis
            'yaxis.labellocation' : 'top', # location of y label w.r.t. y axis
            'axes.labelpad'       : 1, # distance of axis label from axis tick labels
            'axes.titlesize'      : 20, # master title font size
            'font.size'           : 10, # x, y label AND ticks label AND legend font size
            'lines.linewidth'     : 1,
            'lines.marker'        : '.', # marker style
            'lines.markersize'    : 8,
        }
        
        # dictionary of marker styles from matplotlib
        # -> https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.markers.MarkerStyle.html#matplotlib.markers.MarkerStyle.markers
        self.markerstyles = mpl.markers.MarkerStyle.markers
        
        # default font sizes
        self.mastersize = self.rcps['axes.titlesize'] # figure title font size
        self.fontsize = 15 # axis label font size
        
        # default text to diaplay near atlas logo
        self.logotext = "Internal"
    
    
    """
    -----------------------------------------------------------------------------------------------------
    Private functions
    -----------------------------------------------------------------------------------------------------
    """    
    
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
    
    
    """
    -----------------------------------------------------------------------------------------------------
    Public functions
    -----------------------------------------------------------------------------------------------------
    """ 
    
    
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
 
    
    def saveimage(self, name: str, dpi: int) -> None:
        
        self.fig.savefig(name, facecolor='white', transparent=False, dpi=dpi, bbox_inches='tight')

        
    def show_content(self):
        """ Print out data content of histogram and returns pandas dataframe """
        
        if isinstance(self.data, bh.Histogram):
            pass
        
        elif isinstance(self.data, pd.core.frame.DataFrame):
            print(self.data)
        
        else:
            pass




class Hist1D(EmptyPlot):
    
    
    def __init__(self, samples=[], data=[], errors: str =None, stack=False, **kwargs) -> None:
        
        super().__init__(**kwargs)
        
        # set histogram plot specific rcParams
        self.hist_rcps = {
            'legend.handletextpad': 0.3, # space between the legend handle and text
            'legend.columnspacing': 0.5,
            'legend.labelspacing' : 0.05, # vertical space between the legend entries
            'legend.markerscale'  : 1.1,
        }
        self.rcps.update(self.hist_rcps)
        # self.config_rcParams(self.rcps) # i think this doesnt work
        
        self.samples  = samples
        self.data     = data
        self.is_stack = stack
        self.errors   = errors

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
        
        # default variables
        self.shape = 'full' if self.is_stack else 'hollow'
        self.need_grid = False
        
        # list of basic 10 colors the class will automatically use (if number of plotted elements is less than 10)
        # (chosen from: https://matplotlib.org/stable/gallery/color/named_colors.html)
        self.color_order = [
            'black', 'red', 'blue', 'limegreen', 'orangered', 'magenta', 'yellow', 'aqua', 'chocolate', 'darkviolet'
        ]
        self.assign_colors()
        
        self.store_data()
    
    
    """
    -----------------------------------------------------------------------------------------------------
    Private functions
    -----------------------------------------------------------------------------------------------------
    """
    
    def check_input(self) -> None:
        
        if self.samples:
            
            if self.type_checker(self.samples, str):
                
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
                    
                for samplename in self.samples:
                    try:
                        with open(self.dir + f"{samplename}.pkl", 'rb') as file:
                            obj = pickle.load(file)

                            # check whether input is bh
                            if isinstance(obj, bh.Histogram):
                                self.is_obj_bh = True
                            else:
                                logging.error(f"The file {samplename}.pkl does not contain a hist object")
                                break

                            # here, assuming each file contains only one bh
                            self.samples_dict[samplename] = obj
                            if samplename in self.data or self.data == 'all':
                                self.data_dict[samplename] = obj
                                self.plot_types[samplename] = 'data'
                            else:
                                self.histos_dict[samplename] = obj
                                self.histos_list.append(obj)
                                self.plot_types[samplename] = 'histo'
                    except:
                        logging.error(f"There is no file named {samplename}.pkl containing a hist object")
                        break
            else:
                logging.error("Sample entry must be strings")
        else:
            logging.error("Enter a non-empty list of samples to plot.")
    
    
    def store_data(self) -> None:
        
        # right now, this assumes all samples have same dim and length (should check for this)
        # thus, take the first sample to retrieve general info
        if self.histos_dict:
            first_sample = self.histos_dict[next(iter(self.histos_dict))]
        else:
            first_sample = self.data_dict[next(iter(self.data_dict))]
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
        if self.style == 'ATLAS':
            text = hep.atlas.label(ax=ax, label=self.logotext, data=data, lumi=lumi)
        elif self.style == 'LHCb1' or self.style == 'LHCb2':
            text = hep.lhcb.label(ax=ax, label=self.logotext, data=data, lumi=lumi)
        
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
        from matplotlib.offsetbox import AnchoredText
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
    
    
    def assign_colors(self, custom: list =None) -> None:
        """ Fills colors_dict accordingly """
        
        for i, samplename in enumerate(self.samples_dict.keys()):
            if custom:
                self.colors_dict[samplename] = custom[i]
            else:
                if len(self.samples) > 10 or self.is_stack:
                    cmaplist = self.colorlist_gen(len(self.samples))
                    self.colors_dict[samplename] = cmaplist[i]
                else:
                    self.colors_dict[samplename] = self.color_order[i]
    
    
    def get_samples_colors(self, d: dict) -> (list, list):
        """ Retrive the list of samples and the list of colors from dictionary of the form 'samplename: sample' """
        
        samples = list(d.values())
        colors = []
        for samplename in d.keys():
            colors.append(self.colors_dict[samplename])
        
        if len(colors) == 1:
            return samples, colors[0]
        else:
            return samples, colors
    
    
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
        
        histlist, _clist = self.get_samples_colors(self.histos_dict)
        if type(_clist) != list:
            _clist = [_clist]
        
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
                    label= 'Uncertainty' if _clist[i] == 'black' else None
                )
        
    
    def scatterdata_plotter(self, _ax: mpl.axes.Axes, data: list =None) -> None:
        """ Main function to plot scatter data points """
        
        H, _clist = self.get_samples_colors(self.data_dict)
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
            marker=self.rcps['lines.marker'],
            markersize=self.rcps['lines.markersize'],
            label=self.scatterlabels
        )
    
    
    def histbins_plotter(self, _ax: mpl.axes.Axes, data: list =None) -> None:
        """ Main functin to plot histogram bins """
        
        H, _clist = self.get_samples_colors(self.histos_dict)
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
                label=self.histolabels
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
        ax.ticklabel_format(style='scientific')
        ax.yaxis.get_offset_text().set_fontsize(self.rcps['font.size'])
        ax.xaxis.get_offset_text().set_fontsize(self.rcps['font.size'])
        
        if self.need_grid:
            ax.grid(axis=self.gridaxis, linestyle=self.gridline, alpha=0.3, color='k')
            
        self.set_legend(ax)
        
        # add atlas logo and text
        self.set_explabel(ax)
                
        # scale ylim automatically for optimal legend placement
        hep.plot.yscale_legend(ax) # gives error if ATLAS label is not plotted yet (idk why)
        
        # set master title
        ax.set_title(self.mastertitle, fontsize=self.mastersize)
        
        # set x and y axis labels
        self.set_xtitles(ax, 'xmain', self.fontsize)
        self.set_ytitles(ax, 'ymain', self.fontsize)
        
    
    def set_legend(self, ax: mpl.axes.Axes) -> None:
        """ Create legend for main plot """
        
        # should make ncol be detected automatically
        ax.legend(
            ncol=1, 
            handlelength=mpl.rcParams['legend.handleheight']+0.04, 
            fontsize=self.fontsize,
            markerscale=self.rcps['legend.markerscale'],
            labelspacing=self.rcps['legend.labelspacing'],
            handletextpad=self.rcps['legend.handletextpad']
        )
        
        # sort legend entries
        hep.sort_legend(ax)

        
    def colorlist_gen(self, n: int, colormap='gist_rainbow', reverse=False) -> list:
        """ Create custom color list of length n from a given colormap """
        
        clist = []
        pct_max, pct_min = 98, 2 # max and min percentile of color ramp
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
        

    
    """
    -----------------------------------------------------------------------------------------------------
    Public functions
    -----------------------------------------------------------------------------------------------------
    """ 
    
    def plot_options(self, shape: tuple =None, gridstring='', marker: str =None, markersize: float =None, rcp_kw={}) -> None:
        
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
        if marker:
            if marker in self.markerstyles.keys():
                self.rcps['lines.marker'] = marker
        if markersize:
            self.rcps['lines.markersize'] = markersize
        
    
    def color_options(self, colors=[], colormap='', reverse=False) -> None:
        """ Allow user to enter custom colors for histos and data plots """

        if colors and self.type_checker(colors, str):

            if not isinstance(colors, list):
                colors = [colors]
            if len(colors) != len(self.samples):
                logging.error("Length mismatch between color list and total samples list")
            else:
                self.assign_colors(colors)
                    
        elif colormap and self.type_checker(colormap, str):
            if colormap in plt.colormaps():
                self.assign_colors(self.colorlist_gen(len(self.samples), colormap, reverse))
            else:
                logging.error("Invalid matplotlib colormap; choose from https://matplotlib.org/stable/gallery/color/colormap_reference.html")
        
    
    def create(self, save_name='', dpi=1000) -> None:
        
        # create plot figure and subplots
        self.create_canvas()
        self.make_grid()
        self.ax = self.make_subplot(0, 1, 0, 1)
        
        # make plot
        self.hist_plot(self.ax)
        
        if save_name:
            self.saveimage(save_name, dpi)