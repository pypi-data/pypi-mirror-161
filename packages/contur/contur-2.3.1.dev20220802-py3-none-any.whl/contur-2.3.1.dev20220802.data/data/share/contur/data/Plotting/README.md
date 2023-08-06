# Plotting miscellany

This directory contains some miscellaneous things which have been useful when plotting Contur results.

## Rivet histograms

The `.dat` files contain some handy syntax which you can add to your yoda dat files to acheive various effects when plotting the
rivet histograms from Contur.


## Adding extra limit curves to contur plots

You can supply information to be plotted as additional curves on Contur plots either as grids of data points or as functions on the
grid of parameter points you generated.

For specific models, you can find some examples from Contur publications archived in the `data/Models` directory.

The file `Width_cut.py` gives an example of plotting a function which uses auxilliary variables read from the event generator
logs ar run time.

It is also possible to export one contur scan from the `.map` file, and then overlay it on another. To do this, convert the map
files that you would like to plot into CSV files with the following command:

        $ contur-export -i <input map files with space separation> -o <output CSV file name>

Sometimes you may wish to use contur-mapmerge functionality of contur to merge map files before exporting into a CSV file.

After the above steps, the command that you should use to perform the plotting is:

        $ contur-plot -eg <input python script supplying the extra contour data> <your map file> <xarg> <yarg> ...
 
The python script included before the arugment `-eg` is the file that contains the functions which extract the necessary data from the CSV
files for plotting the contour lines. An example is shown in `external_contur.py`.
You can change the `x` and `y` arguments that you are looking to plot in the CSV files and specify the corresponding columns
to suit your purpose (e.g. L49-51). 

If you would not like to rename the csv files in the reading order, you could discard the codes at the beginning of the file
and replace the name with your preferred name. 

You could also change the CL that you would like to filter out (L53).

Lastly, the number of functions defined should be the same number of CSV files that you have. If you have three CSV files,
uncomment the last function in the file. If you have more than three CSV files to plot, first edit the dataframe reading at
the top of the file and then add in extra functions with unique names. 
