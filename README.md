# Pythium Plots

A thorough walkthrough of how plotting classes work in Pythium.

## General Structure

As of now (May 2022) there are 6 classes: `EmptyPlot`, `Hist1D`, `RatioPlot`, `PullPlot`, `ProjectionPlot` and `CMatrixPlot`. Of these, the first one is a virtual class from which all other classes inherit.