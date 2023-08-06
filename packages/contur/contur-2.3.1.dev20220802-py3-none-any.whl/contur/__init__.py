"""\
The Contur package for model interpretation of collider-physics measurements

The Contur package contains the following submodules, which should be imported by hand as needed.

* `contur.config` - Global configuration options
* `contur.data` - Database and associated functions parsing data/covariance info from Rivet/YODA
* `contur.export` - Utiluty for exporting map files to csv
* `contur.factories` - Main worker classes for contur functionality
* `contur.oracle` - Driver for scans using active learning
* `contur.plot` - Plotting engine and styling
* `contur.run` - Defines logic used in python executables
* `contur.scan` - Utilities for steering/running creation of MC grids
* `contur.util` - Misc helper functions


"""

import contur.config.version
__version__ = contur.config.version.version
