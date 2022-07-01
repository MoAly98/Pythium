# Pythium <img src="https://github.com/MoAly98/Pythium/blob/main/misc/pythium_logo.png?raw=true" width="50">

A ROOT Killa'

Projec Aims:
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

Logo and Name credits to Callum Birch-Sykes 
