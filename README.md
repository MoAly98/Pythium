<p align="center">
  <img src=https://github.com/MoAly98/Pythium/blob/maly-typing/misc/Pythium.png?raw=true" width="400" />
</p>

# The story
Pythium is a library intended to be a comple tool-box to perform a typical HEP analysis. In such a workflow, a user would pre-process some ROOT files to skim/slim them (sklimming), then often histograms need to be built from the outputs. These histograms will then be either studied individually by plotting them, or be used as templates to perform statisitcal fitting and inference. 

What often happens is that each analysis group will write a ***framework*** which performs these various steps, and these frameworks are written in ROOT/C++ (a HEP-specific language) and are not re-usable for other analyses. 

With the super growth of the PyHEP ecosystem, and the beginning of the LHC Run 3, this is an exciting time to write a consistent analysis frameowork in python that can be re-used by any analyser (and even theorists!). Born in the University of Manchester, this is excatly what Pythium wants to be! 

The name “Pythium” is inspired by a genus of parasites which attacks the roots of crops. Name and logo credits go to Callum Birch-Sykes.

# The Design
In Pythium, we try to assume very little about what you want to do; our main goal is to take care of pieces that are not physics, and provide you an interface to tell us how to do the physics part :)

The API we provide is mostly in the form of a python configuration files (`config.py`) where you interact with Pythium objects. The "s" in "files" is important -- in order to avoid bloated configs, we ask for a seperate config file for each of the steps: *Sklimming*, *Histogramming* and *Fitting*.

For example, let's say you have some pre-processed sample (by Pythium) `bigsample_nominal.parquet` stored in `bigsample_dir/` and you want to grab an observable `foo` from that sample to histogram it. To do this, you can add the following lines to your histogramming configuration file 

```
sample = [Sample(name = "bigsample", 
                 tag = ['bigsample'],
                 where = "bigsample_dir")]

observables = [Observable(var = "foo",
                          name = "foo", 
                          binning =  RegBin(low=0, high=1000, nbins = 50)
                          dataset = 'nominal'
                          )]
```
and that's pretty much all you need, modulu some general settings! 

 ***In the future***, We will be supporting a custom function to read your custom pre-processed samples (without assuming a Pythium naming system or file structure), and we will also be able to provide an API so that you can build these Analysis objects (e.g. Sample, Observable) in your own python script and play around with them (e.g. use Pythium API to make a quick histogram and play with the binning before changing the config). 

Pythium is compliant with the big-data industry movement towards ***Columnar Analysis***; the analyser will have to think about their data as tables, with the columns being different variables, the rows being an event number, and operations are performed on an entire column in one go (well, chunks of the column) rather than in a conventional event loop. This is made possible through the use of **Awkward Arrays**, which has the speed of C++ code in Python! If you can't think of your operation in a columnar way, don't worry ! **Numba** comes to the rescue, and Pythium will not complain when you `@jit` your operations. This is particularly important when designing your sklimming config and you want to build some complex variables. 


Pythium from the start is meant to put together tools that already exist, rather than re-invent the wheel. So for file reading we use methods from `Uproot` and `awkward`, for histogramming we use `boost-histogram` and `dask`, and for fitting we are planning to utilise `cabinetry` and `pyhf` with `gpu` backends. We also are studying moving our pre-processing code to utilise `coffea` processors in the backend. 

# How to Install 

Getting started with Pythium is quite easy. At the moment, Pythium is avialable on `Test PyPI` since we are still in development stage. To install it as a user, go to your favorite virtual enviornment and run: 
```
pip install --extra-index-url https://test.pypi.org/simple/ pythium
```
which will deliver the pythium wheel to you and install all dependancies (a long list for now). 

# Documentation

The pythium documentation is hosted on ReadTheDocs at 
https://pythium.readthedocs.io/en/main/ and there you can find a quickstart guide to get your first Pythium analysis !

# How to run 

To run a configuration file, you should use the provided CLI for now (again this will change once an API is more mature) -- if package was installed correctly you can run
```
pythium-sklim -c <sklim-config.py>
```
for sklimming configs, or 
```
pythium-hist -c <sklim-config.py>
```
for histogramming configs. 

# The configuration files 
## Sklimming 

## Histogramming 

## Fitting

Under construction!




<!-- Projec Aims:
-  Use ```Uproot``` to slim-down NTuples to small-size files (e.g. .json, .h5, .pkl)
  -   A dedicated configuration file for slimming is needed 
  - Cofiguration structure:
    - Add CL option ```--append```to be included to add branches to output files, but with required ```--outdir``` option to ensure user doesn't appednt to wrong files
    - A list of "Branch" objects to initialise with a ```(Name, Formula)```
    - A list of "AnalysisObjects" objects to initialise with ```SampleName, DSIDs = [...], Trees = [...], ON_branches = [...], OFF_branches = [...])```
      where "ON" is to keep and "OFF" to remove
-  Build a histogram wrapper around ```hist``` package 
  - A dedicated configuration file for histogramming is needed
  - Configuration structure:
    - A list of Histogram objects to initialise with  ```(Hist_Name, Branch, Binning = [...])```
    - Functionality to read in ROOT histograms
    - Cross-check needed between slimming and histogramming configurations
- Build a single confiugration file to set-up statsitcal workspace and perform a fit 
  - Add option to turn fitting off, if user needs just workspace to share 
-  A single configuration file for plotting and/or tables
- Classes to handle proper Logging
- Batch support 

Logo and Name credits to Callum Birch-Sykes  -->
