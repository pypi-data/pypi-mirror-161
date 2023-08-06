# B-L gauged model

As used in [these studies](https://contur.hepforge.org/results/BL3/index.html)

The file BL3limits.py contains functions used to plot the experimental and theoretical limits on the plots.

In order to plot smooth limits from other tools an additional visualisation tool was developed, so called "Data constraints". Named as the constraints come from data tables (not necessarily experimental data)

An example of a csv file containing 3 columns, in this case the mzp and g1p values, and the value of the scale that the model is perturbative to as output from mathematica is included in RGE_X.csv

An example script that loads this into contur as a dataconstraint is included in BL3dataConstraints.py, this file loads the csv and defines a function call that contur will make that returns the parameter space point and the value that is used in the plotting.

this is loaded by running
contur-plot -d BL3dataConstraints
as one would load the theory functions (both can be loaded at once)


## Model Authors
Wei Liu, Frank Deppisch
