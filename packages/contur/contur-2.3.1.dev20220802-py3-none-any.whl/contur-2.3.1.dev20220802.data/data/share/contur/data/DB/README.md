# Directory contents

- The [analyses.sql](analyses.sql) file is the main metadata file for Contur. It is an [sqlite](https://www.sqlite.org/index.html) database and is compiled by the top-level contur Makefile.
 contains tables defining the know rivet analyses, collider beams, SM theory predictions, and perhaps most importantly the analysis pools into which the measurements are divided. The tables are documented in the file.
- The python modules handling this are in  [`contur/data`](../../contur/data)

# Adding a new measurement to Contur

If a new measurement already exists in your installed version Rivet and you want to make use of it in Contur, you
only need to add it to the [Contur database](analyses.sql).

The changes you'll need to make are:

- Check if the new measurement fits in an existing analysis pool. If it does not, then you need to create a new analysis pool with an appropriate name, and add it to the ``analysis_pool`` table with a line like: 

   ```
   INSERT INTO analysis_pool VALUES('ATLAS_7_JETS','7TeV','Inclusive hadronic final states');
   ```
   
   The first entry is the name, the second the beam descriptor, the third a brief text description of the pool.

- Once you have done this, or have identified an existing pool in which the analysis belongs, add the analysis to the ``analysis`` table with a line like: 

   ```
   INSERT INTO analysis VALUES('ATLAS_2014_I1325553','pb','ATLAS_7_JETS');
   ```

   where the first field is the Rivet analysis name, the second is the units in which the cross section is given (check the finalise method the rivet routine if in doubt) and the third is the analysis pool name. (The intergrated luminosity used to be required but is now taken from the rivet *.info file.)

For simple cases, that's all! Next time you type ``make``, the database will be remade and the ``.ana`` files for steering rivet etc will be remade to include your new data. If you use those then next time you run Herwig/Rivet/Contur, you should see comparisons to your new data.

## Additional tweaks:

- If you have the SM theory prediction please [add that too](../Theory/README.md)!

- If the plots in the paper are area normalised, Contur needs to know the absolute normalisation. This should be provided in the ``normalization`` table in ``analyses.sql``, for example: 

   ```
   INSERT INTO normalization VALUES('ATLAS_2012_I1203852','(d03|d05|d07)',0.0254,0);
   ``` 
   The first field is the full analysis name, the second a regular expression, the third is the integrated cross section for plots matching the regexp, and the fourth is a flag for treat plots which are numbers of events rather than differential cross sections. See the in-file comments for detailed information.

- If there are a few plots you don't want to use in the comparison, add them to the ``blacklist`` table. They will be ignored by contur.

- Alternatively, if there are only a few plots you *do* want to use in the comparison, add them to the ``whitelist`` table. All other plots from the analysis will be ignored by Contur.

- If there are several statistically independent plots in your analysis, you can add them to a subpool in the ``subpool`` table to maximise sensitivity.

- If the analysis is a search analysis, add it to the ``searches`` table.

- Check the other tables such as: ``metratio``, ``neddtheory``, ``higgsgg``, ``higgsww``, ``atlaswz``, ``bveto``. These flag up various special cases. If you just want to run locally you can probably ignore them, but if you want to contribute your new work to the Contur repository (encouraged!) please check them.

# New rivet routine?

If you have a new local Rivet routine you want to use then just add it (the usual ``.cc, .yoda, .plot`` and ``.info`` files) to the [data/Rivet](../Rivet) directory of your local Contur installation, and do all the above steps in the database as well. Next time you ``make``, the new routne should be compiled along with the database.


