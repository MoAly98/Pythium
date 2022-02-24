import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import numpy as np
import mplhep as hep


"""
This is where all plot classes will be stored
"""


class EmptyPlot():
    
    
    def __init__(self, title=None, layout=(1,1), size=(6.4,4.8), style="ATLAS"):
        
        self.title   = title
        self.layout  = layout
        self.figsize = size
        self.style   = style
        
        self.container1d = []
        self.container2d = []
        self.colorlist   = []
        
        # set default dict of axes titles
        self.xtitles_dict = {"xmain": '',
                             "xtop" : '',
                             "xbot" : '',
        }
        self.ytitles_dict = {"ymain": '',
                             "ytop" : '',
                             "ybot" : '',
        }
    
    
    def create_canvas(self):
        
        self.fig = plt.figure(figsize=self.figsize)
        hep.style.use(self.style) # available syles are: {"ALICE" | "ATLAS" | "CMS" | "LHCb1" | "LHCb2"}

        
    def make_grid(self, **grid_kw):
        
        self.gs = gridspec.GridSpec(self.layout[0], self.layout[1], **grid_kw) # there has to be a smarter way to unpack tuple
    
    
    def make_subplot(self, start_row, end_row, start_col, end_col, **subplot_kw): # these args must be allowed by layout size
        
        return self.fig.add_subplot(self.gs[start_row:end_row,start_col:end_col], **subplot_kw)
    
    
    def set_majorticks(self, ax, **ticks_kw):
        
        ax.tick_params(**ticks_kw)
    
    
    def set_minorticks(self, ax, **ticks_kw):
        
        ax.minorticks_on()
        ax.tick_params(**ticks_kw)
        
    
    def set_xtitles(self, ax, axis_key):
        
        ax.set_xlabel(self.xtitles_dict[axis_key])
    
    
    def set_ytitles(self, ax, axis_key):
        
        ax.set_ylabel(self.ytitles_dict[axis_key])
        
    
    def set_color(self, colormap='viridis', reverse=False):
        
        self.user_cmap = colormap
        if reverse:
            self.user_cmap = self.user_cmap + '_r'
        mpl.rcParams['image.cmap'] = self.user_cmap
    
    
    def set_stack_color(self, colormap="viridis", reverse=False):
        # create custom color map for stack histogram
        
        clist = []
        source = self.dflist # list of units to be stacked
        pct_max = 99 # max percentile of color ramp
        pct_min = 1  # min percentile of color ramp
        cmap = mpl.cm.get_cmap(colormap)
        # number of items in data source
        n = len(source)
        # list of values between 0.00 and 1.00; length equals length of data source
        sequence = list(i/100 for i in (np.arange(pct_min, pct_max, (pct_max-pct_min)/n)))
        # reverse if required
        sequence = sequence if not reverse else reversed(sequence)
        # create list of colors
        for i in sequence:
            color = cmap(i) 
            clist.append(color)

        self.colorlist = clist
    
    
    def config_rcParams(self, settings_dict):
        # let user update global rcParams values of matplotlib
        
        if isinstance(settings_dict, dict):
            for key, value in settings_dict.items():
                mpl.rcParams[key] = value
                print(key, value)
        else:
            print("Please put a dictionary as argument for 'config_rcParams' function") # need logger
        
        # can also add a 'help' command to display all the rcParams variables that can be cahnged to help user
        
        # there is an easier function already in matplotlib, might want to switch to that
        # https://matplotlib.org/stable/api/matplotlib_configuration_api.html#matplotlib.rc
    
    
    def saveimage(self, name, dpi):
        
        self.fig.savefig(name, facecolor='white', transparent=False, dpi=dpi, bbox_inches='tight')
