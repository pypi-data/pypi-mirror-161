"""Global configuration class setting default behavior, importing contur loads all of the following

:Module members:

Where these are settable from the command line. See ```contur --help``` for documentation.

    * **useTheoryCorr** (``bool``) see ```--tc```

    * **vetoAnalyses** (``string``) see ```--ana-match```
    * **onlyAnalyses** (``string``) see ```--ana-unmatch```
    * **splitAnalysis** (``bool``) see ```--ana-split```

    * **exclude_met_ratio** (``bool``) see ```--xr```
    * **exclude_hgg** (``bool``) see ```--xhg```
    * **exclude_hww** (``bool``) see ```--xhw```
    * **exclude_awz** (``bool``) see ```--awz```
    * **exclude_b_veto** (``bool``) see ```--wbv```
    * **exclude_searches** (``bool``) see ```-s```
    * **exclude_soft_physics** (``bool``) see ```--soft_physics```
    * **tracks_only** (``bool``) see ```--tracks_only```

    * **gridMode** (``bool``) see ```-g```
    * **weight** (``string``) see ```--wn``

    * **binwidth** see ```--BW```
    * **binoffset** see ```--BO```
    * **blocklist** (default {"MASS","STOPMIX"}) see ```--S```


Stats/fitting, parameters, see ```contur --help```

    * **min_np**
    * **min_num_sys**
    * **min_syst**
    * **ll_prec**
    * **err_prec**
    * **n_iter**

Batch system

    * using_condor
    * condor_os
    * **using_qsub** (Default)
    * using_slurm
    * seed (random number seed)

These are used by ```contur-plot```

    * contour_colour
    * mapfile (default "contur.map")
    * map_colorCycle (set to None, will be initialised from colour config if a pool name is unrecognised)
    * plot_format (pdf or png)

Default file names

    * mceg (default "herwig")
    * mceg_template (default "herwig.in")
    * paramfile (default "params.dat")
    * tag (default "runpoint\_")
    * unneeded_files (default ["herwig.run","Looptools.log", "py.py", "mgevents"])
      These files will be removed when runing ```contur-gridtool```
    * param_steering_file (default "param_file.dat")
    * summary_file (default Summary.txt)
    * output_dir (default ANALYSIS)

These are used internally, set from other conditions.

    * **silenceWriter** (``bool``) --
      Disables a lot of plotting output, for when it is not needed (eg in grid mode).

    * **contur_log** (``logging.logger``) logger object

    * **stat_types** ["DATABG","SMBG","EXP"] This indexes three different ways of evaluating a likelihood.
       DATABG: using the data as the background. This can always be done and is what has been used for most 
       contur results so far.
       SMBG: if we have the Standard Model prediction, we evaluate the exclusion using this as the background too.
       EXP: this is the expected limit. Evaluated by moving the data central value to the SM prediction (when we have one) 
       but keeping the data uncertainties.

"""
contur_log=None
logfile_name="contur.log"

# this will make numpy raise exceptions instead of printing warnings
import numpy
numpy.seterr("raise")

def setup_logger(filename=logfile_name, logstream=None, level="ERROR"):
    """
    set up the logger object

    :param filename: name of log file
    """

    import logging, sys
    import contur.config.config as cfg
    cfg.logfile_name=filename

    level = getattr(logging, level)

    #for some reason we can't supply a formatter to the basic config: https://stackoverflow.com/questions/34319521/python-logging-module-having-a-formatter-causes-attributeerror
    if logstream is None:
        try:
            logging.basicConfig(
                level=level,
                format='%(name)s - %(levelname)s - %(message)s',
                filemode="w",
                filename=cfg.logfile_name,
            )
        except PermissionError:
            print("Do not have permission to write your logfile to {}. Run contur from a directory you can write to.".format(os.path.join(os.getcwd(),cfg.logfile_name)))
            sys.exit(1)
            
    else:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=logstream
        )

    stream = logging.StreamHandler(sys.stdout)
    FMT=logging.Formatter('%(levelname)s - %(message)s')
    stream.setFormatter(FMT)

    cfg.contur_log=logging.getLogger()
    cfg.contur_log.addHandler(stream)

# Setup some module level variable defaults

# if true, only use the diagonal elements of the covariance matrices
diag=False
# treat theory systematics as correlated within a plot
useTheoryCorr=True

vetoAnalyses=[]
onlyAnalyses=[]
exclude_met_ratio=False
exclude_hgg=False
exclude_hww=True
exclude_b_veto=True
exclude_awz=True
exclude_searches=True
exclude_soft_physics=True
tracks_only=False

gridMode=False
splitAnalysis=False

weight=""

# minimum number of systematic uncertainty contributions before they will be treated as a valid error breakdown
min_num_sys=4
# minimise nuiance parameters? (very slow!)
min_np=False
min_syst=0.001
# termination criteria for scipy.minimize
ll_prec=0.0001
err_prec=0.0001
n_iter=200

found_ref = []
found_thy = []
silenceWriter=False #For API mode: disable file output

binwidth=-100.
binoffset=0.

using_condor=False
using_qsub  =True
using_slurm =False
seed = 101

condor_os = "CentOS7"
condor_jdl_extras = ["+JobFlavour = 'testmatch'"] #< needed for CERN lxbatch

mceg="herwig"
known_mcegs = ["herwig",  "madgraph","pbzpwp", "pythia8" ]
default_nev=30000
mceg_template=mceg+".in"


# Some default filenames
paramfile="params.dat"
tag="runpoint_"
unneeded_files=["herwig.run","Looptools.log", "py.py", "mgevents"]
blocklist={"MASS","STOPMIX"}
mapfile="contur.map"
param_steering_file="param_file.dat"
summary_file="Summary.txt"
grid_summary_file="GridSummary.txt"
output_dir="ANALYSIS"
input_dir="ANALYSIS"
import os
# directory to write all plots to
plot_dir=os.path.join(output_dir,"plots")
grid=None
using_results_db=False
results_dbfile="contur_run.db"
models_dbfile="models.db"
# directories to igore when looking for yoda files.
hidden_directories=["mgevents","ANALYSIS"]
# default directory to write all the SM plots to.
smdir = "sm_plots"
run_info = "RunInfo"
import contur.config.paths as paths
share = paths.user_path()


import re
# This allows for the form EXPERIMENT_YEAR_INSPIRENUMBER or EXPERIMENT_PHYSICSGROUP_YEAR_ID
APATT=r'(([A-Z0-9]+_\d{4}_[IS]\d{5,8})|([A-Z0-9]+_[A-Z]{4}_\d{4}_[A-Z0-9]+)'
ANALYSISPATTERN = re.compile(APATT+r')')
ANALYSIS        = re.compile(r'('+APATT+r')[^/]*)')
ANALYSISHISTO   = ANALYSISHISTO   = re.compile(r'('+APATT+r')[^/]*)/((d\d+-x\d+-y\d+)|\w+)')

# reference data
refObj = {}
thyObj = {}
refCorr = {}
refUncorr = {}
refErrors = {}
theoryCorr = {}
theoryUncorr = {}
theoryErrors = {}

# A one-off to hold objects that have been scaled in an unscaled form for plotting
plotObj = {}
plotThObj = {}


# various types of statistic evaluations
databg = "DATABG"
smbg = "SMBG"
expected = "EXP"
stat_types = [databg,smbg,expected]
mode = databg


# plotting config
contour_colour = {}
contour_colour[databg]="white"
contour_colour[smbg]="black"
contour_colour[expected]="black"
contour_style = {}
contour_style[databg]="solid"
contour_style[smbg]="solid"
contour_style[expected]="dotted"
map_colorCycle=None
plot_format="pdf"

class _DuplicateFilter(object):
    """
    Private class to filter log messages so only one instance shows once, from:
    from https://stackoverflow.com/questions/31953272/python-logging-print-message-only-once
    """
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv


class ConturError(Exception):
    pass
