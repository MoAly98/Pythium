# Pythium Plots (TEMP)

A (quick) thorough walkthrough of how plotting classes work in Pythium. Currently, Jupyter test files that are present in the `plot_misc` file contain plot classes and examples of use cases. The file `plot_classes.py` stores all classes.

## General Structure

As of now (May 2022) there are 6 classes: `EmptyPlot`, `Hist1D`, `RatioPlot`, `PullPlot`, `ProjectionPlot` and `CMatrixPlot`. Of these, the first one is a virtual class from which all other classes inherit.

### Use case

Plots are made by creating an instance of the class by calling the constructor and then calling the `create()` function after that. Optional public functions may be called but they must be before the `create()` method for them to take effect.

    plot = Hist1D(...)
    ... optional methods ...
    plot.create()

This behaviour is universal for all plots, although internally, the way variables are stored/kept track of slightly varies between the two main histogram classes (Hist1D and RatioPlot) and other classes. This is because the histogram classes have been developed further, while other classes were left a bit behind.

`create()` serves the same purpose for all plots but is slightly different for each of them; for this reason it is not included in `EmptyPlot`, but rather defined separately in each class.

### Optional public functions

Sorry, but for now, you will have to deal with the text I already wrote for my report 😛 (it's basically the same section)

![image](https://user-images.githubusercontent.com/91688435/169562993-8de88201-d4a6-4ce8-b21b-5eddd3c6586f.png)

![image](https://user-images.githubusercontent.com/91688435/169563527-1c0672b2-9e10-44ed-83e6-c7eb4eb6298c.png)


### Titling system

The base class (`EmptyPlot`) also stores two dictionaries (called `xtitles_dict` and `xtitles_dict`) to store x and y axis labels of any subplot that might be present in the plot. These titles are set by the user calling the function `set_axislabels()`. Take `xtitles_dict` as an example:

    self.xtitles_dict = {
        "xmain" : '',
        "xtop"  : '',
        "xbot"  : '',
        "xleft" : '', # not used
        "xright": ''
    }

The terms `xmain`, `xtop`, `xbot` etc. refer to the follownig subplot scheme:

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

Each plot type (ratio, pull, projection, cmatrix) will be a combination of these subplots (Ax objects). For example, the ratio plot will be made of main and bot subplots and the projection plot will be made of main, top and right subplots. The left subplot is currently not used and might be deleted in the future if no use cases are found. So for example, in `RatioPlot` the user can pass in `set_axislabels()` arguments of `ymain`, `ybot` and `xbot`. `xmain` can be passed but will be ignored since there is no $x$ axis label between the main subplot and the bottom subplot (there's not axis tick labels either, for that matter).

The space between the subplots is called `spacing` throughout all classes.

### Font sizes

As matplotlib makes a lot of confusion in the `rcParams` that control font sizes of each element in the plot, I decided to standardise them in the following way (example from pull plot):

<img src="https://user-images.githubusercontent.com/91688435/156620566-67d09e8d-0773-4a98-9be0-a6571027a2ca.png" width="400"/>

* figure title = `matplotlib.rcParams['axes.titlesize']`
* axis tick labels (numbers and strings) = `matplotlib.rcParams['font.size']`
* axis labels and legend items labels = internal `fontsize` attribute, which is passed in as argument in `set_axislabels()` function

It is possible to modify all these at the same time by calling `fontsize_options()` (public function in `EmptyPlot`). Call signature: `fontsize_options(title = None, labels = None, ticks = None)`

### Plot internal creation

This is handled by private functions present in `EmptyPlot`. When `create()` is called, each class will call in order:
* `create_canvas()`
  - Creates the figure using `self.figsize` variable
* `make_grid()`
  - Creates gridspec object that sets the layout of the subplots: ncols and nrows of subplots, spacing between them
* `make_subplot()` -> as many times as the number of subplots in the figure
  - Creates an `Ax` objects which is the actual subplot where matplotlib functions are called on (e.g. `ax.errorbar()` etc.)

Then, after these core functions are called, `create()` will call other internal functions that ultimately lead to either matplotlib calls (`ax.errorbar()`, `ax.stairs()` etc.) or mplhep functions (`hep.histplot()`, `hist2dplot()`).

### rcParams

rcParams are stored in a dictionary called `self.rcps` created by constructor of `EmptyPlot`. The current default dictionary is shown below. Other classes that inherit from `EmptyPlot` will then add other entries, updating `self.rcps`.

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

The user has access (can add and modify) this dictionary by creating their own and passing it in the `plot_options(rcp_kw={})` public function.

## Hist1D

Explanation of storage variables:

    self.samples: list[str] or str -> Names of all samples
    self.data: list[str] or str -> Names of all samples that are going to be plotted as points
    self.is_stack: bool
    self.errors: 'hist', 'data' or 'all' -> Which samples will have errrors
    self.shape: 'hollow' or 'full', defaults to 'full' if self.is_stack = True -> Whether to plot hollow histos or filled histos. Hollow ones will have different edgecolors, while full ones will have black edgecolor and colored facecolor

    1  self.samples_dict = {} # {'samplename': sample}
    2  self.histos_dict  = {} # {'samplename': sample (which will be plotted as histo bins)}
    3  self.histos_list  = [] # list of hist objects that will be plotted as histo bins
    4  self.data_dict    = {} # {'sameplname': sample (which will be plotted as data point)}
    5  self.plot_types   = {} # {'samplename': 'histo' or 'data'}
    6  self.colors_dict  = {} # {'samplename': 'color'}
    7  self.names         = []
    8  self.labels        = []
    9  self.histolabels   = []
    10 self.scatterlabels = []

1. {samplename: str, sample: Hist}; Stores all the input samples
2. {samplename: str, sample: Hist}; Stores all samples that are NOT in `self.data`
3. [sample: Hist]; List of all Hist objects that will be plotted as histos
4. {samplename: str, sample: Hist}; Stores all sample that will be plotted as data (points)
5. {samplename: str, 'data' or 'histo': str}; Stores if sample is a histo or data
6. {samplename: str, color: str}; Stores color of each sample (histos and data)
7. Stores `Hist.axes[0].names` from all samples
8. Stores `Hist.axes[0].label` from all samples
9. Same as above but only for histo samples
10. Same as above but only for data samples

### Coloring system

A list of default colors is created in the constructor:

    self.color_order = [
        'black', 'red', 'blue', 'limegreen', 'orangered', 'magenta', 'yellow', 'aqua', 'chocolate', 'darkviolet'
    ]

These colors are used (in order) both for data and histo samples, provided plotted elements are less than 10 (lenght of `color_order`). If it is not a stack plot, `self.shape` defaults to hollow and `color_order` is used for the edgecolors of the histos and markercolors of the data points. If it is a stack plot, `self.shape` defaults to `full` and colormaps are instead used. The default colormap is `gist_rainbow`, but this can be changed in the `color_options(colormap='colormap')` public function that the user can call (one of the optional function previously mentioned). If it is NOT a stack plot BUT there are more than 10 plotted elements, colormaps are used. The function `color_options(colors=[])` also allows the user to enter specific colors for each plotted element, provided the length of the passed list is equal to the length of the samples passed.

Colors get assigned by the `assign_colors()` private function:

    def assign_colors(self, custom: list = None) -> None:
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
           
This gets called the first time in the constructor, but can be recalled if `color_options()` has been called, so that `colors_dict` gets properly updated.

### Plotting methods

The three most important functions that the main function `hist_plot()` calls are:
1. `histbins_plotter()`

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
                
    * Uses `hep.histplot()` but with different arguments depending on `self.shape`. A custom data (list of raw values) can be passed to it since `hep.histplot()` supports input of both raw data and Hist objects.
2. `scatterdata_plotter()`

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
    * If `self.errors = 'data' or 'all'`, the `yerr` argument is set to True. This is by default a simple error of sqrt(N). Markerstyle and markersize are drawn from `self.rcps` so they are modifiable from the user.

4. `histbins_errs()` if `self.errors = 'hist' or 'all'`
    * This is to put the gray hatched bins around the top of histos bins. If it is a stack plot, the error will go only on the top of stack histograms and will be fixed to black, if it is not a stack plot, each hitos will have their own error bins of the same color (different for each of them).

### `set_explabel()`

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

Generates ATLAS logo inside plot (for now works only for Hist1D and RatioPlot, others use directly the `hep.atlas.text`). To allow for `hep.plot.yscale_text` (mplhep function that increases $y$ axis to fit any text in the plot) to work properly, since this function only detects `matplotlib.AncoredText` objects, an empty one is created right under the ATLAS logo, then the function is called. The bbox evaluation is to determine the lower right corner of the ATLAS logo generated with `hep.atlas.label`.

## RatioPlot

Inherits from Hist1D so all of the above applies as well. In particular, to make the main subplot, the Hist1D `hist_plot()` function is called, so that's exactly the same. There are still few technicalities regarding the lower subplot (also called bot plot, or `botax`).

### Variables storage

        1. self.reference = reference -> str, i.e. 'samplename' or 'total' (taken from input)
        2. self.numerators = {} -> {samplename: str, sample: Hist}
        3. self.denominator = {} -> {samplename: str, sample: Hist}
        4. self.dvals = [] -> [float]

1. Denotes with respect to which sample the ratio will be calculated. If it's `total`, see below.
2. Which samples to use as "numerator".
3. Which sample to use as "denominator".
4. Raw values to be used as denominator when calculating the ratio values. These can be either taken directly from Hist objects using `Hist.values()`, or calculated using the function `get_stackvalues()` (present in Hist1D) in case `self.reference = 'total'`:

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

If `self.reference = 'total'`, things are a bit different. This is the case when there is only one data sample and the other histo samples are stacked together. The ratio plot is then the data histogram divided by the total of the stack histograms.
* `self.numerators` is not a dictionary with multiple samples but now only contains the data sample.
* `self.dvals` is not just the `Hist.values()` of the denominator sample, but is calculaed from all the stack histograms using `get_stackvalues()` which takes in a list of Hist objects, extracts their values using `.values()` and sums them all up for each bin.

Ratio values are calculated using the funtion `ratiovalues_calculator()` and stored in `self.ratiovalues`:

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

### Plotting methods

For the lower subplot, the main function is `bot_plot()`. The following happens:

        # iterate through all samples in self.numerators along with corresponding color
        for i, samplename in enumerate(self.numerators.keys()):
            if samplename in self.data or self.data == 'all':
                self.ratio_scatters(samplename, _clist[i])
            else:
                self.ratio_histbins(samplename, _clist[i])

`ratio_scatters()` uses `hep.histplot()`, while `ratio_histbins()` uses `matplotlib.stairs` becaues of an issue with not being able to adject properly the baseline of the histograms (the starting $y$ values of it, which in the lower subplot must be 1).

To plot the error bins (currently only available for histo samples) the function `histbins_errs()` from Hist1D is used.

It is also possible for the user to change the bot plot's y axis range using `ratio_options()`, so that this doesn't happen:

![image](https://user-images.githubusercontent.com/91688435/169562440-973f9994-e713-4671-a332-ebb3b9e75531.png)

this function calls `custom_yaxis()`, which does the following:

    def custom_yaxis(self, ylims: list, step: float =None, edges=False) -> None:
        """
        Allow user to manually change the bot y axis limits, which can often
        overlap with various other plot elements. If edges is set to True,
        the first and last ticks will be shown in the plot.
        """
        
## PullPlot

## ProjectionPlot

## CMatrixPlot

# Things that are not supported in the existing classes

![image](https://user-images.githubusercontent.com/91688435/169566841-7ecf7125-e668-4d29-994c-718c3f969780.png)
