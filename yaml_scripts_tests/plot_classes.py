import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import numpy as np
import mplhep as hep



class EmptyPlot():
    
    def __init__(self, title=None, layout=(1,1), size=(6.4,4.8), style="ATLAS"):
        
        self.title  = title
        self.layout = layout
        self.size   = size
        self.style  = style
        
        self.container1d = []
        self.container2d = []
        self.colorlist   = []
    
    def create_canvas(self):
        self.fig = plt.figure(figsize=self.size)
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
    
    def set_color(self, colormap='viridis'):
        mpl.rcParams['image.cmap'] = colormap
    
    def set_stack_color(self, colormap="viridis", reverse=False): # create custom color map
        
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
    
    def saveimage(self, name):
        self.fig.savefig(name, facecolor='white', transparent=False, dpi=1200, bbox_inches='tight')