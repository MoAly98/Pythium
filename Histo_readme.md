# Histogramming Guide

This guide shows how to fill histograms with event data sklimmed in the preprocessing phase.

## Filling Types

 There are 2 types of filling availalbe to users: simple fill and cross product fill with multiple samples, regions and systematics.

## Running Simple Fill

To run a simple fill change directory to pythium folder and run `python3 scripts/histogramming.py`. This will load event data, fill histograms and save them in a directory specified in `histogramming_config.py`.

## Configuring Simple Fill

The configuration file `histogramming_config.py` contains important parameters that control filling process. The following variables affect the simple fill:

- `client_params` dictionary of arguments passed to the Dask client.
- `file_list` dictionary of arguments that controls the function that creates a list of files to be used in the filling process.
- `computation_params` dictionary of arguments that controls which observable dictionary is used in the filling process and how many files are processed in each batch.
- `out_dir` specifies output directory.

## Running Cross Product Fill

To run a cross prodcut fill change directory to pythium folder and run `python3 scripts/cross_product.py`. This will load event data, fill histograms in a cross product manner and save combinations to a directory specified in `histogramming_config.py`.

## Configuring Cross Product Fill

The same configuration file `histogramming_config.py` contains other parameters that describe the cross porduct:

- `Samples_XP` contains a list of samples that are used in the cross product. 
- `Regions` variable is a list of regions that are used in the cross product.
- `Systematics`contains, as above, a list of systematics used in the cross product. 

These lists contain 3 objects that are important for the cross product performance, these are respectively: `XP_Sample`. `XP_Region` and `XP_Systematics`.

### Sample Object

`XP_Sample` is an object that contains list of files for each sample. Upon initialization, file list is compiled. This can be done in 3 ways, user can pass a list of files directly.

`XP_Sample(name = 'test', file_list = ['tmp/data/file.h5'])`

User can also pass a top directory to start a search for files and a regex filter.

`XP_Sample(name = 'test', regex = True, top_directory = 'tmp/data/', file_regex = '(.*file.*)(.*h5$)')`

One can also pass `Sample` object from the preprocessing stage.

`XP_Sample(Sklim_Sample = item, top_directory = 'tmp/data/')`

### Region Object

`XP_Region` is an object that contains different regions and their selection criteria. During cross product filling, these selection criterai are applied to the data set.

`XP_Region(name = 'test', filter = 'col1 >= 1')`

Filter argument uses pandas `query` function.

### Systematic Object

`XP_Systematics` is a parent object of different kinds of systematics:

- `XP_Overall` changes the weight of the entire histogram by a set amount.
- `XP_Formula` changes based on a function defined by a user.
- `XP_Histo` subtracts specified histogram from one another.

### Systematic Object Examples

| synatx | explanation |
|--------|-------------|
| `XP_Overall(name = 'test1', Adjustment = 0.5)`| Increase each weight by 50%|
| `XP_Formula(name = 'test2', Formula = myfunc)` | Change weights according to the formula provided in myfunc function |
| `XP_Histo(name = 'test3', name_of_hist = hist_object)` | Subtract hist_object from a histogram |


