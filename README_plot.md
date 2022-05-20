# Pythium Plots

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

## Hist1D

Explanation of storage variables:

    self.samples: list[str] or str; Names of all samples
    self.data: list[str] or str; Names of all samples that are going to be plotted as points
    self.is_stack: bool
    self.errors: 'hist', 'data' or 'all'; Which samples will have errrors

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
