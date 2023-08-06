 ###  SM theory predictions

To add new SM theory predictions to the contur release, you need to get them into YODA file format and put them in
your local copy of this directory. The histogram path names should start with ``/THY/`` and otherwise
match the histograms they are intended to be compared to. 

The details of what the prediction is and where it comes from should then be added to the ``theory_predictions``
table in the analysis database [here](../DB/analyses.sql).

Several predictions for the same cross section may be stored in the [``TheoryRaw`` directory](../TheoryRaw),
but the one that is used it the one here. Do use a different one, rename it into this directory.

