"""
Main module for running Contur on a single YODA file or a parameter grid of YODA files
"""

import rivet

import sys, os
import contur.config.config as cfg
import contur.util.utils as cutil
import contur.util.file_readers as cfr
import contur.scan.grid_tools as cgt
import contur.run.arg_utils as cau
import contur.factories.depot
import contur.data.static_db as cdb
from contur.data.data_access_db import write_grid_data


def process_grid(args, poolid=None, mergedDirs=[]):
    """
    Process the grid, creating a depot and calling analyse_grid for each beam.

    """


    if args['INIT_DB']:
        cfg.using_results_db = True

    if poolid is not None:
        cfg.contur_log.info(
            "Processing grid for pool {}, analysis {}".format(poolid, cfg.onlyAnalyses))

    depots = {}
    # look for beams subdirectories in the chosen grid and analyse each of them
    beams = cau.valid_beam_arg(args)
    cfg.contur_log.info("Looking for these beams to run on:")
    for beam in beams:
        cfg.contur_log.info("- {}".format(beam.id))

    known_beams = cdb.get_beams(poolid)
    for beam in known_beams:
        beam_dir = os.path.join(cfg.grid, beam.id)

        if beam in beams and os.path.exists(beam_dir):

            # merge/rename all the yoda files for each beam and parameter point
            if not beam.id in mergedDirs:

                cgt.grid_loop(scan_path=beam_dir, unmerge=args['REMERGE'])
                mergedDirs.append(beam.id)

            contur_depot = contur.factories.depot.Depot(noStack=args['NOSTACK'])
            analyse_grid(os.path.abspath(beam_dir), contur_depot, args)
            # save some memory
            contur_depot.resort_points()
            depots[beam_dir] = contur_depot

    if len(depots) > 0:
        # merge maps for each beam
        cfg.contur_log.info("Merging maps")
        target = None
        for beam_id, depot in depots.items():
            if len(depot.inbox)>0:
                if not target:
                    target = depot
                else:
                    target.merge(depot)
            else:
                cfg.contur_log.warn("No {} data".format(beam_id))

        if target:
            target.resort_points()
            target.write(cfg.output_dir)

            # populate the local database for this grid
            if cfg.using_results_db:
                try:
                    write_grid_data(args['RUNNAME'],target)
                except cfg.ConturError as ce:
                    cfg.contur_log.error("Failed to write results database. Error was: {}".format(ce))

    elif len(args['BEAMS']) == 0:

        # No beam directories present, so just look for all yodas below the given top directory.
        contur_depot = contur.factories.depot.Depot(noStack=args['NOSTACK'])
        analyse_grid(os.path.abspath(cfg.grid), contur_depot, args)

        contur_depot.write(os.path.join(cfg.output_dir))

        # populate the local database for this grid
        if cfg.using_results_db:
            write_grid_data(args['RUNNAME'],contur_depot)

    else:
        cfg.contur_log.info("No compatible YODA files found.")


def analyse_grid(scan_paths, conturDepot, args):
    """
    perform the analysis on a grid (called by process_grid) and store results in the depot

    """

    yoda_counter = 0
    yodapaths = []
    parampaths = []

    for scan_path in scan_paths.split(","):
        for root, dirs, files in sorted(os.walk(scan_path)):

            valid_yoda_file = False
            for file_name in files:
                valid_yoda_file = cgt.is_valid_yoda_filename(file_name)
                if valid_yoda_file:
                    yoda_counter += 1
                    yoda_file_path = os.path.join(root, file_name)
                    break

            if not valid_yoda_file:
                continue

            param_file_path = os.path.join(root, cfg.paramfile)
            yodapaths.append(yoda_file_path)
            parampaths.append(param_file_path)
            cfg.contur_log.debug(
                'Reading parameters from {}'.format(param_file_path))
            params = cfr.read_param_point(param_file_path)
            cfg.contur_log.info('Found valid yoda file ' +
                                  yoda_file_path.strip('./'))
            sample_str = 'Sampled at:'
            tmp_params = {}
            for param, val in params.items():
                sample_str += ('\n'+param + ': ' + str(val))

                if args['SLHA'] and param=="slha_file":
                    block_list = args['SLHA'].split(",")
                # read parameters from blocks in an SLHA file
                    block_dict = cfr.read_slha_file(root, val, block_list)
                    for block in block_list:
                        tmp_params.update(block_dict[block])

            params.update(tmp_params)
            cfg.contur_log.info(sample_str)

            # If requested, grab some values from the generator log files and add them as extra parameters.
            params.update(cfr.get_generator_values(root, files, args['ME'],args['PI']))

            # Perform analysis
            try:
                conturDepot.add_point(param_dict=params, yodafile=yoda_file_path)
            except ValueError as ve:
                cfg.contur_log.warning("Failed to add parameter point {}, no likelihoods present. YODA file is {}".format(params,yoda_file_path))

    cfg.contur_log.info("Found %i YODA files" % yoda_counter)
    #conturDepot.build_axes()


def main(args):
    """
    Main programme to run contur analysis on a grid of YODA files, a single YODA, or a YODA stream.
    arguments should be passed as a dictionary.
    """

    # Set up / respond to the common argument flags and logger config
    cau.setup_common(args) 
    print("Writing log to {}".format(cfg.logfile_name))

    if 'YODASTREAM' not in args:
        args['YODASTREAM'] = None

    cfg.grid = args['GRID']
    
    modeMessage = "Run Information \n"

    modeMessage += "Contur is running in {} \n".format(os.getcwd())
    if cfg.grid:
        modeMessage += "on files in {} \n".format(cfg.grid)
        cfg.gridMode = True
        cfg.mapfile = args['MAPFILE']
        cfg.silenceWriter = True
    elif args['YODASTREAM'] is None:
        modeMessage += "on analysis objects in {} \n".format(args['yoda_files'])
        cfg.gridMode = False
    else:
        modeMessage += "on analysis objects in YODASTREAM StringIO \n"
        cfg.gridMode = False
        if not args.get('UNSILENCE_WRITER_FOR_STREAMS', False):
            cfg.silenceWriter=True


    cfg.results_dbfile = os.path.join(cfg.output_dir,cfg.results_dbfile)
    cfg.models_dbfile = os.path.join(cfg.share,cfg.models_dbfile)

    # set up the plot output directory
    cfg.plot_dir = os.path.join(cfg.output_dir,"plots")

    # set up the data selection options.
    modeMessage = cau.setup_selection(args,modeMessage)

    if (not args['yoda_files'] and not cfg.gridMode and (args['YODASTREAM'] is None)):
        cfg.contur_log.critical("Error: You need to specify some YODA files to be "
                              "analysed!\n")
        sys.exit(1)

    if (not args.get('UNSILENCE_WRITER_FOR_STREAMS', False)) and args.get('OUTPUTDIR') is None:
        cfg.contur_log.critical("Error: If you wish to output .dat files running on a "
        "yoda stream, you must specify an OUTPUTDIR")
        sys.exit(1)

    if args['WEIGHTNAME'] is not None:
        cfg.weight = args['WEIGHTNAME']

    # Set the global args used in config.py
    if args['PARAM_FILE']:
        cfg.paramfile = args['PARAM_FILE']

    modeMessage = cau.setup_stats(args, modeMessage)

    if args['ANAPATTERNS']:
        cfg.onlyAnalyses = args['ANAPATTERNS']
        modeMessage += "Only using analysis objects whose path includes %s. \n" % args['ANAPATTERNS']
    if args['ANASPLIT']:
        cfg.splitAnalysis = True
        modeMessage += "Splitting these analyses into seperate histograms %s. \n" % args['ANASPLIT']
    if args['ANAUNPATTERNS']:
        cfg.vetoAnalyses = args['ANAUNPATTERNS']
        modeMessage += "Excluding analyses names: %s. \n" % args['ANAUNPATTERNS']
    if args['POOLPATTERNS']:
        modeMessage += "Splitting analyses of pools %s. \n" % args['POOLPATTERNS']

    if args['BINWIDTH']:
        cfg.binwidth = float(args['BINWIDTH'])
    if args['BINOFFSET']:
        cfg.binoffset = float(args['BINOFFSET'])
    if args['MODEL']:
        modeMessage += '\n Model: ' + args['MODEL']
        cfg.contur_log.info('\n Model: ' + args['MODEL'])

    cfg.contur_log.info(modeMessage)

    contur_depot = contur.factories.depot.Depot(noStack=args['NOSTACK'])

    # rather than porting arguments though class instance initialisations, instead set these as variables in the global config.py
    # all these are imported on import contur so set them here and pick them up when needed later

    if cfg.gridMode:


        # grid mode
        # --------------------------------------------------------------------------------------------------
        mergedDirs = []
        if args['POOLPATTERNS']:
            # In this case we are running on specified pools and breaking them down into separate analyses
            anaDir = cfg.output_dir
            for poolid in args['POOLPATTERNS']:
                anas = cdb.get_analyses(poolid)
                for a in anas:
                    if a.name in cfg.vetoAnalyses:
                        continue
                    cfg.onlyAnalyses = args['ANAPATTERNS'] + \
                        [a.name]  # add analysis to must-match anas
                    # setup a different directory for each ana
                    cfg.output_dir = os.path.join(anaDir, poolid, a.name)
                    process_grid(args, poolid, mergedDirs)
            cfg.output_dir = anaDir  # reset ANALYSIDIR to original value
        elif cfg.splitAnalysis:
            # In this case we are running on specified analyses and breaking them down into histos/subpools.
            anaDir = cfg.output_dir
            # One analysis at a time
            for ana in args['ANASPLIT']:
                cfg.contur_log.info(
                    'Running grid on {} and splitting it into pools'.format(ana))
                # setup a different directory for each ana
                cfg.output_dir = os.path.join(anaDir, ana)
                cfg.onlyAnalyses = args['ANAPATTERNS'] + [ana]
                # for subpool/hist etc
                process_grid(args, None, mergedDirs)

            cfg.output_dir = anaDir  # reset ANALYSIDIR to original value

        else:
            # In this case we are running on everything
            process_grid(args)

        contur_depot.write_summary_file(modeMessage)

    elif (args['YODASTREAM'] is None):
        # single mode
        # --------------------------------------------------------------------------------------------------

        # find the specified parameter point.
        yodaFiles = cgt.find_param_point(
            args['yoda_files'], args['TAG'], args['FINDPARAMS'])
        
        for infile in yodaFiles:

            
            if not os.path.exists(infile):
                cfg.contur_log.critical("{} does not exist".format(infile))
                sys.exit(1)
                
            anaDir = cfg.output_dir
            plotDir = cfg.plot_dir
            cfg.output_dir = os.path.join(
                os.path.dirname(infile), anaDir)
            cfg.plot_dir = os.path.join(
                os.path.dirname(infile), plotDir)

            contur_depot = contur.factories.depot.Depot(noStack=args['NOSTACK'])

            # get info from paramfile if it is there
            param_file_path = os.path.join(
                os.path.dirname(infile), cfg.paramfile)
            if os.path.exists(param_file_path):
                params = cfr.read_param_point(param_file_path)
                modeMessage += '\nSampled at:'
                for param, val in params.items():
                    modeMessage += '\n' + param + ': ' + str(val)
            else:
                params = {}
                params["No parameters specified"] = 0.0
                modeMessage += "\nParameter values not known for this run."


            # If requested, grab some values from the log file and add them as extra parameters.
            root = "."

            tmp_params = {}
            for param, val in params.items():
                if args['SLHA'] and param=="slha_file":
                    block_list = args['SLHA'].split(",")
                    # read parameters from blocks in an SLHA file
                    block_dict = cfr.read_slha_file(root, val, block_list)
                    for block in block_list:
                        tmp_params.update(block_dict[block])

            params.update(tmp_params)

            files = os.listdir(root)

            # If requested, grab some values from the generator log files and add them as extra parameters.
            params.update(cfr.get_generator_values(root, files, args['ME'],args['PI']))

            # read the yodafile, do the comparison
            try:
                contur_depot.add_point(param_dict=params, yodafile=infile)
            except ValueError as ve:
                cfg.contur_log.critical("Failed to add parameter point {}, no likelihoods present. Yodafile is {}.\n {}".format(params,infile,ve))
                raise

            cfg.contur_log.info(modeMessage)
            contur_depot.write_summary_file(modeMessage)

            cfg.output_dir = anaDir  # reset ANALYSIDIR to original value
            cfg.plot_dir = plotDir  # reset ANALYSIDIR to original value

    else:
        # single mode, but run from YODA stream
        # --------------------------------------------------------------------------------------------------
        contur_depot = contur.factories.depot.Depot(noStack=args['NOSTACK'])

        params = {}
        params["No parameters specified"] = 0.0
        modeMessage += "\nParameter values not known for this run."

        # If requested, grab some values from the log file and add them as extra parameters.
        root = "."
        files = os.listdir(root)

        # If requested, grab some values from the generator log files and add them as extra parameters.
        params.update(cfr.get_generator_values(root, files, args['ME'],args['PI']))

        # read the yodafile, do the comparison
        try:
            contur_depot.add_point(param_dict=params, yodafile=args['YODASTREAM'])
        except ValueError as ve:
            cfg.contur_log.warning("Failed to add parameter point {}, no likelihoods present. Yodafile is {}".format(params,infile))

        cfg.contur_log.info(modeMessage)
        output_options = args.get('YODASTREAM_API_OUTPUT_OPTIONS', [])
        return cutil.write_summary_dict(output_options, contur_depot)

       

def doc_argparser():
    """ wrap the arg parser for the documentation pages """
    from contur.run.arg_utils import get_argparser
    return get_argparser('analysis')
