import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import numpy as np
import mplhep as hep
import boost_histogram as bh
import pandas as pd


"""
This is where all plot classes will be stored
"""


class EmptyPlot():
    
    
    def __init__(self, title="", layout=(1,1), size=(6.4,4.8), style="ATLAS"):
        
        self.master_title = title
        self.layout       = layout
        self.figsize      = size
        self.style        = style
        
        self.active_data = None
        self.data_container  = [] # allow to store multiple objects
        
        # set default dict of axes titles
        self.xtitles_dict = {"xmain" : '',
                             "xtop"  : '',
                             "xbot"  : '',
                             "xleft" : '', # not used
                             "xright": ''
                            }
        self.ytitles_dict = {"ymain" : '',
                             "ytop"  : '',
                             "ybot"  : '',
                             "yleft" : '', # not used
                             "yright": ''
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
    
    
    def create_canvas(self):
        # create figure and set the hep style (rcParams)
        
        self.fig = plt.figure(figsize=self.figsize)
        hep.style.use(self.style) # available syles are: {"ALICE" | "ATLAS" | "CMS" | "LHCb1" | "LHCb2"}
        
        # set math text font to non-italics
        mpl.rcParams['mathtext.default'] = 'regular'

        
    def make_grid(self, **grid_kw):
        # create gridspec object to set configuration of subplots
        
        self.gs = gridspec.GridSpec(self.layout[0], self.layout[1], **grid_kw) # there has to be a smarter way to unpack tuple
    
    
    def make_subplot(self, start_row, end_row, start_col, end_col, **subplot_kw): # these args must be allowed by layout size
        # generate ax objects (subplots)
        
        return self.fig.add_subplot(self.gs[start_row:end_row,start_col:end_col], **subplot_kw)
    
    
    def fill_titlesdict(self, **titles_kw):
        
        if isinstance(titles_kw, dict):
            
            for key, value in titles_kw.items():
                if   key in self.xtitles_dict.keys():
                    self.xtitles_dict[key] = value
                elif key in self.ytitles_dict.keys():
                    self.ytitles_dict[key] = value
                else:
                    print("Key not valid") #logger
        
        else:
            print(f"{titles_kw} is not a dictionary")
        
    
    def set_xtitles(self, ax, axis_key, fontsize, labelpad):
        # set x axis labels according to xtitles_dict
        
        ax.set_xlabel(self.xtitles_dict[axis_key], fontsize=fontsize, labelpad=labelpad)
    
    
    def set_ytitles(self, ax, axis_key, fontsize, labelpad):
        # set y axis labels according to ytitles_dict
        
        ax.set_ylabel(self.ytitles_dict[axis_key], fontsize=fontsize, labelpad=labelpad)
        
    
    def set_color(self, colormap='viridis', reverse=False):
        
        self.user_cmap = colormap
        if reverse:
            self.user_cmap = self.user_cmap + '_r'
        mpl.rcParams['image.cmap'] = self.user_cmap
    
    
    def config_rcParams(self, settings_dict):
        # let user update global rcParams values of matplotlib
        
        if isinstance(settings_dict, dict):
            for key, value in settings_dict.items():
                mpl.rcParams[key] = value
                print(key, value) # make sure it's working
        else:
            print(f"Put a dictionary as argument for {__name__} function") # need logger
        
        # can also add a 'help' command to display all the rcParams variables that can be cahnged to help user
        
        # there is an easier function already in matplotlib, might want to switch to that
        # https://matplotlib.org/stable/api/matplotlib_configuration_api.html#matplotlib.rc
    
    
    def saveimage(self, name, dpi):
        
        self.fig.savefig(name, facecolor='white', transparent=False, dpi=dpi, bbox_inches='tight')

        
    def show_content(self):
        # print out data content of histogram and returns pandas dataframe
        
        if isinstance(self.data, bh.Histogram):
            pass
        
        elif isinstance(self.data, pd.core.frame.DataFrame):
            print(self.data)
        
        else:
            pass