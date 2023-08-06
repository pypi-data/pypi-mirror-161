# make the shared area of a common contur install

from genericpath import exists
import os, glob
import subprocess

import contur.config.config as cfg
from contur.run.arg_utils import setup_common
from contur.data.data_objects import Beam
import contur.data as cdb

import contur.util.utils as cutil

from contur.data import build_database

home_dir=os.path.expanduser('~')
VERBOSITY = 1
def log(msg, v):
    if v >= VERBOSITY:
        print(msg)
def debug(msg):
    log(msg, 0)
def warning(msg):
    log(msg, 2)


def main(args):
    """
    Main programme to run over the known analysis and build SM theory yodas from the TheoryRaw or REF areas.
    """
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    # build DB
    DB=build_database.BuildDB('analyses.db')
    DB.build_db()

    cfg.results_dbfile = os.path.join(cfg.output_dir,cfg.results_dbfile)
    cfg.models_dbfile = os.path.join(cfg.output_dir,cfg.models_dbfile)

    cfg.contur_log.info("Making shared area in {}".format(cfg.output_dir))
     

    try:
        import yoda
        import rivet
        import contur.data.data_access_db
        cdb.data_access_db.generate_model_and_parameter(model_db=True)
        cutil.generate_rivet_anas(args['WEBPAGES'])
        debug('Successfully found RIVET and YODA Python module')
    except ImportError:
        warning('Warning: rivet and yoda not found, contur functionality will be limited')
        
