"""
Perform various manipulations on an existing contur scan grid or grids, but NOT the actual contur statistical analysis.

"""

import logging
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import contur
import contur.data.data_access_db as cdba
import contur.config.config as cfg
from contur.config.config import ConturError
import contur.scan.grid_tools as cgt


def main(args):
    """
    arguments should be passed as a dictionary.

    """

    contur.run.arg_utils.setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    if args['INIT_DB']:
        cfg.results_dbfile = cfg.path('data', 'DB', 'responsive_storage.db')
        cfg.contur_log.info("generate db with model and parameter data initialised")
        contur.data.generate_model_and_parameter()
        if len(args['scan_dirs']) == 0:
            sys.exit(0)
        
    if len(args['scan_dirs']) == 0:
        cfg.contur_log.critical("No grid directory specified")
        sys.exit(1)
        
    Clean = True
    if args['DO_NOT_CLEAN']:
        cfg.contur_log.info("Not removing unnecessary files from grid")
        Clean = False

    if args['MERGE_GRIDS']:
        cfg.contur_log.info("Merging Grids")
        contur.scan.merge_grids.merge_main(sys.argv[2:])
        sys.exit(0)

    elif args['ANAPATTERNS']:
        cfg.contur_log.info("Extract histograms from {} into a new grid".format(args['ANAPATTERNS']))
        if not len(args['scan_dirs']) == 1:
            cfg.contur_log.critical(
                "Requires exactly one directory. {} given. ({})".format(len(args['scan_dirs']), args['scan_dirs']))
            sys.exit(1)

        cgt.grid_loop(scan_path=args['scan_dirs'][0], patterns=args['ANAPATTERNS'], extract=True, clean=Clean)

    elif args['RM_MERGED']:
        cfg.contur_log.info("If unmerged yodas exists, unzipping them and removing merge yodas.")
        cgt.grid_loop(scan_path=args['scan_dirs'][0], unmerge=True, clean=Clean)

    elif args['COMPRESS_GRID']:
        cfg.contur_log.info("Archiving this directory tree")
        cgt.grid_loop(scan_path=args['scan_dirs'][0], archive=True)

    elif args['CHECK_GRID'] or args['CHECK_ALL']:
        cfg.contur_log.info("Checking directory tree")
        if args['CHECK_ALL']:
            cfg.contur_log.info("Also counting jobs without batch logs as failed")
        cgt.grid_loop(scan_path=args['scan_dirs'][0], check=True, resub=args['RESUB'], check_all=args['CHECK_ALL'], queue=args['queue'])


    elif args['FINDPARAMS']:
        # find the specified parameter point.
        yoda_files = []

        
        try:
            if not cfg.results_dbfile:
                cfg.results_dbfile = cfg.path('data', 'DB', 'responsive_storage.db')

            if args['PARAM_DETAIL']:
                yoda_files = cdba.show_param_detail_db(args['scan_dirs'], args['FINDPARAMS'])
            else:
                yoda_files = cdba.find_param_point_db(args['scan_dirs'], args['FINDPARAMS'])
        except ConturError as dboe:
            cfg.contur_log.info(dboe)
            cfg.contur_log.info("Could not get info from DB. Will use file system instead.")

        if len(yoda_files)==0:
            # nothing found in the DB. try the file system.
            yoda_files = cgt.find_param_point(args['scan_dirs'], cfg.tag, args['FINDPARAMS'])

            
        if args['PLOT']:
            cfg.contur_log.info("*************************************************")
            cfg.contur_log.info("Starting making histogram for matched yoda files")
            for yoda_file in yoda_files:
                os.system("gzip -d " + yoda_file)
                yoda_file_unziped = ".".join(yoda_file.split(".")[:-1])
                os.system("contur " + yoda_file_unziped)
                os.chdir(os.path.dirname(yoda_file_unziped))
                os.system("contur-mkhtml " + yoda_file_unziped)

    elif Clean:
        cgt.grid_loop(scan_path=args['scan_dirs'][0], clean=Clean)


    sys.exit(0)


def doc_argparser():
    """ wrap the arg parser for the documentation pages """
    from contur.run.arg_utils import get_argparser
    return get_argparser('gridtools')
