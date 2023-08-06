from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys, os, logging
from shutil import copyfile

import contur.config.version
import contur.config.config as cfg
from contur.data.static_db import get_beams, get_beam_names

def get_args(argv, arg_group="unknown argument group"):
    """Parse command line arguments"""

    parser = get_argparser(arg_group)
    args = parser.parse_args(argv)
    args = vars(args)
    return args


def get_argparser(arg_group):
    """
    Build and return an argument parser

    :param arg_groups: which argument groups will be used.

    * group **mapplot** for plotting map files
    * group **analysis** for running analysis on a gird or a single yoda file
    * group **smtest** for running statistical tests on SM theory
    * group **gridtools** for running grid utilities
    * group **batchsub** for running evgen batch jobs
    * group **xsbf** for extracting cross sections and branching fractions from a single yoda
    * group **xsbfscan** for extracting and plottingcross sections and branching fractions from a grid
    * group **html** for making html pages

    """

    known_groups = {}
    known_groups['smtest'] = ['stats', 'select', 'ioshort']
    known_groups['mapplot'] = ['map_plotting']
    known_groups['analysis'] = ['io', 'dress', 'select', 'stats','params']
    known_groups['gridtools'] = ['tools', 'batch', 'mceg_select','params']
    known_groups['batchsub'] = ['batch','mceg_select']
    known_groups['xsbfscan'] = ['xsbf','xsscan','mceg_select']
    known_groups['xsbf'] = ['xsbf','mceg_select']
    known_groups['bib'] = ['ioshort','select']
    known_groups['html'] = ['html']
    known_groups['theory'] = ['smtheory']
    known_groups['share'] = ['share']

    if arg_group not in known_groups.keys():
        print("Do not recognize the requested argument group: {}".format(arg_group))
        sys.exit(1)

    active_groups = []
    for flag in known_groups[arg_group]:
        active_groups.append(flag)

    if arg_group == 'batchsub':
        parser_description = ("Run a parameter space scan and submit batch jobs.\n"
            "Produces a directory for each beam containing generator config file detailing the "
            "parameters used at that run point and a shell script to run the generator "
            "that is then submitted to batch. (if --single, just make one example directory)\n")

    elif arg_group == 'mapplot':
        parser_description = ("Plot contur data from a .map file.\n")

    elif arg_group == 'xsbf':
        parser_description = ("Extract and plot cross section and branching ratio information from single run.\n")
        
    elif arg_group == 'xsbfscan':
        parser_description = ("Extract and plot cross section and branching ratio information from scan.\n")
        
    elif arg_group == 'theory':
        parser_description = ("Rebuild SM theory library.\n")
        
    elif arg_group == 'bib':
        parser_description = ("Building contur LaTeX bibliography files.\n")
        
    else:
        parser_description = ("This is the main analysis executable for Contur: Constraints on new theories using Rivet\n ")

    parser = ArgumentParser(usage=__doc__, description=parser_description,
                            formatter_class=ArgumentDefaultsHelpFormatter)



    # generic arguments, always allowed.
    parser.add_argument("-v", "--version", action="store_true", dest="printVersion",
                        default=False, help="print version number and exit.")
    parser.add_argument("-d", "--debug", action="store_true", dest="DEBUG", default=False,
                        help="Switch on Debug to all, written to log file")
    parser.add_argument("-q", "--quiet", action="store_true", dest="QUIET", default=False,
                        help="Suppress info messages")
    parser.add_argument("-l", "--log", dest="LOG",
                        default=cfg.logfile_name, help="Specify logfile name.")


    # arguments used when building shared area
    if "share" in active_groups:
        parser.add_argument("-w", "--webpages", dest="WEBPAGES", action="store_true",
                          default=False,
                          help="Also build the webpage rsts for sphinx")
        parser.add_argument('-o', '--outputdir', type=str, default=cfg.share, dest="OUTPUTDIR",
                            help="Output path.")


    # arguments used when plotting from map file
    if "map_plotting" in active_groups:
        mapplot = parser.add_argument_group("Map file plotting arguments")
        # Positional arguments
        mapplot.add_argument('map_file', nargs=1, type=str, help=('Path to .map file '
                                                        'containing list of depot objects.'))
        mapplot.add_argument('variables', nargs='*', type=str,
                            help=('x, y [and z] variables to plot.'))

        # Optional arguments
        mapplot.add_argument('-o', '--outputdir', type=str, default='conturPlot', dest="OUTPUTDIR",
                            help="Output path for plot(s).")

        mapplot.add_argument('-ef', "--externalFunction", type=str, default=None,
                            help="Python file with external functions to load and plot")
        mapplot.add_argument('-eg', "--externalGrid", type=str, default=None,
                            help="Python file loading alternative external grids")

        mapplot.add_argument('-xl', "--xlog", action="store_true",
                            help="Set the xaxis to be displayed on a log scale")
        mapplot.add_argument('-yl', "--ylog", action="store_true",
                            help="Set the yaxis to be displayed on a log scale")
        mapplot.add_argument('--pools', dest="plot_pools", action='store_true',
                            help="Turn on plotting of individual analysis pools (much slower!)")
        mapplot.add_argument('-O', '--omit', type=str,
                            help='Name of pool to omit (will slow things down!)', default="")

        mapplot.add_argument('-x', '--xlabel', type=str, default=None,
                            help='x-axis label. Accepts latex formatting but special characters must be input with a slash, e.g. \$M\_\{z\'\}\$~\[GeV\]')
        mapplot.add_argument('-y', '--ylabel', type=str, default=None,
                            help='y-axis label. Accepts latex formatting but special characters must be input with a slash, e.g. \$M\_\{z\'\}\$~\[GeV\]')
        mapplot.add_argument('-sp', '--save_plots', action='store_true',
                            help="Save the raw matplotlib axes to a file for graphical manipulation")
        mapplot.add_argument('-T', '--title', type=str,
                            help='Title for plot.', default="")
        mapplot.add_argument('-L', '--ilevel', '--iLevel', type=int,
                            help='interpolation zoom level', default=3)
        mapplot.add_argument('--style', dest="style", default="DRAFT", choices=["DRAFT", "FINAL"], type=str.upper,
                            help="Global flag for plot-styling variations: 'final' will have no title or cmap key and will produce a .tex file containing a colour legend for the dominant pools plot")
        mapplot.add_argument('--isigma', '--iSigma', type=float,
                            help='interpolation smoothing radius, in mesh cells', default=0.75)
        mapplot.add_argument('--num-dpools', dest="ndpools", type=int,
                            help='Number of levels of (sub)dominant pool plots to make.', default=1)
        mapplot.add_argument('--clstxt', dest="showcls", default=False, action="store_true",
                            help="Write CLs values on top of the mesh in the detailed dominant-pool plots.")
        mapplot.add_argument('--no-clsdpool', dest="simplecls", default=False, action="store_true",
                            help="Skip the detailed dominant-pool plot with lead/sub/diff CLs meshes.")
#        mapplot.add_argument('-c', '--contour_colour', dest="contour_colour", default=cfg.contour_colour,
#                            type=dict, help="Dict of colours for the 68/95 contours")
        mapplot.add_argument('-f', '--format', dest="plot_format", default=cfg.plot_format,
                            type=str, help="format for plots (pdf, png...)")
        mapplot.add_argument('--databg', dest="databg", default=False,
                            action="store_true",
                             help="Make data-as-background the primary exclusion.")
        mapplot.add_argument('--secondary-contours', dest="secondary_contours", default=False,
                            action="store_true",
                             help="Add contour(s) for stats other than the default.")

        
    # minimal io arguments
    if "ioshort" in active_groups:        
        parser.add_argument("-o", "--outputdir", dest="OUTPUTDIR",
                            default=None, help="Specify output directory.")
    
    # io arguments for major contur run
    if "io" in active_groups:
        io = parser.add_argument_group("Input/Output control options")
        io.add_argument("-o", "--outputdir", dest="OUTPUTDIR",
                        default=cfg.output_dir, help="Top level output directory.")
        io.add_argument('yoda_files', nargs='*', help='.yoda files to process.')
        io.add_argument("--ns", "--nostack",
                        action="store_true", dest="NOSTACK", default=False,
                        help="in single run mode, do not stack the histograms in dat file output")
        io.add_argument("-g", "--grid", dest="GRID", default=None,
                        help="grid mode: specify folder containing a structured grid of points."
                             "The next few options only apply in grid mode.")
        io.add_argument('--tag', dest='TAG', default=cfg.tag,
                        help='Identifier for merged yoda files.')
        io.add_argument("--map", dest="MAPFILE", default=cfg.mapfile,
                        help="Name of map file output.")
        io.add_argument("--runname", dest="RUNNAME", default="my_run",
                        help="Unique indentifier for each run, for example author name")
        io.add_argument("--remerge", action="store_true", dest="REMERGE",
                        help="Force Contur to not use possibly available merges of yoda files but merge yoda files anew")
        io.add_argument("--initDB", action="store_true", dest="INIT_DB", default=False,
                             help="build local db for later analysis")


    # arguments for adding extra info to contur run
    if "dress" in active_groups:
        dress = parser.add_argument_group("Dressing options to embellish outputs")
        dress.add_argument("-p", "--param_file", dest="PARAM_FILE", default=cfg.paramfile,
                           help="Optionally specify a parameter file.")
        dress.add_argument("--model", dest="MODEL",
                           help="Optionally give name for model used. Only used for documentation.")
        dress.add_argument("-P", "--particle_info", nargs="?", dest="PI", default=None, const="ALL",
                           help="Comma-separated list of particles for which mass, width, branchings will be stored."
                           "If flag is present with no list, info will be saved for all particles found.")
        dress.add_argument("-M", "--matrix_element", nargs="?", dest="ME", default=None, const="ALL",
                           help="Comma-separated list of matrix elements for which cross sections will be stored."
                           "If flag is present with no list, info will be saved for all non-zero processes found.")
        dress.add_argument("-S", "--slha", dest="SLHA", default="MASS",
                           help="read parameters from a comma-seperated list of blocks in an SLHA file")
        dress.add_argument("--BW", "--binwidth", dest="BINWIDTH",
                           help="optional binning of SLHA paramters")
        dress.add_argument("--BO", "--binoffset", dest="BINOFFSET",
                           help="optional bin offset for SLHA parameters")

    # arguments for selecting subsets of data
    if "select" in active_groups:
        select = parser.add_argument_group("Options to exclude/include subsets of data")
        select.add_argument("--all",
                            action="store_true", dest="USEALL", default=False,
                            help="Convenience option to use all data. Overrides any other selections.")
        select.add_argument("--xr", "--nometratio",
                            action="store_true", dest="EXCLUDEMETRAT", default=cfg.exclude_met_ratio,
                            help="Exclude plots where exclusion would be based on a ratio to the SM dileptons"
                                 "Use this when you have ehnanced Z production in your model.")
        select.add_argument("--tracks-only",
                            action="store_true", dest="TRACKSONLY", default=cfg.tracks_only,
                            help="Only use plots which are based on tracking information"
                            "Useful for models where calorimeter jet calibration may be suspect (e.g. dark showers).")
        select.add_argument("--soft-physics",
                            action="store_true", dest="USESOFTPHYSICS", default=(not cfg.exclude_soft_physics),
                            help="Include plots which are very sensitive to soft QCD."
                            "Not reliable unless you really know what you are doing.")

        select.add_argument("--xhg", "--nohiggsgamma",
                            action="store_true", dest="EXCLUDEHGG", default=cfg.exclude_hgg,
                            help="Exclude plots where Higgs to photons signal is background-subtracted by fitting continuum."
                                 "Do this when you have large non-Higgs diphoton production from your model.")
        select.add_argument("--whw", "--withhiggsww",
                            action="store_true", dest="USEHWW", default=(not cfg.exclude_hww),
                            help="Include plots where Higgs to WW signal is background-subtracted using data."
                                 "Only try this when you have large Higgs WW from your model and not much top or other source of WW.")
        select.add_argument("--wbv", "--withbvetos",
                            action="store_true", dest="USEBV", default=(not cfg.exclude_b_veto),
                            help="Include plots where a b-jet veto was applied in the measurement but not in the fiducial definition."
                                 "Only try this when you have large W+jets enhancements and no extra top or other source of W+b.")
        select.add_argument("--awz", "--atlas-wz",
                            action="store_true", dest="USEAWZ", default=(not cfg.exclude_awz),
                            help="Include the ATLAS WZ analysis with dodgy SM assumptions."
                                 "Might be useful for enhanced WZ cross sections but be careful.")
        select.add_argument("-s", "--use-searches",
                            action="store_true", dest="USESEARCHES", default=(not cfg.exclude_searches),
                            help="Use reco-level search analyses in the sensitivity evaluation (beta).")
        select.add_argument("--wn", "--weight-name", dest="WEIGHTNAME", default="",
                            help="for weighted events/histos, select the name of the weight to use.")
        select.add_argument("--ana-match", action="append", dest="ANAPATTERNS", default=[],
                            help="only run on analyses whose name matches any of these regexes")
        select.add_argument("--ana-unmatch", action="append", dest="ANAUNPATTERNS", default=[],
                            help="exclude analyses whose name matches any of these regexes")
        select.add_argument("-b", "--beams", dest="BEAMS", default="all",
                            help=f"""in grid mode, only run on these beams. Default is to run on any valid beams found.
                            Known beams are {get_beam_names(allow_all=True)}. NOTE: em_ep_91_2 is currently beta, see https://gitlab.com/hepcedar/rivet/-/issues/293.""")

    # arguments for selecting model parameters
    if "params" in active_groups:
        params = parser.add_argument_group("Options affecting model parameters")
        params.add_argument("-f", "--findPoint", action="append", dest="FINDPARAMS", default=[],
                            help="identify points consistent with these parameters and make histograms for them")
        
    # arguments for tweaking the statistical treatment
    if "stats" in active_groups:
        stats = parser.add_argument_group(
            'Options to Manipulate the constructed test statistic. They dont apply if correlations are switched off')
        stats.add_argument("-u", "--diagonalise_cov", action="store_true", dest="UNCORR", default=False,
                           help="Use diagonal version of covariance matrix (ie no systematic correlations).")
        stats.add_argument("--xtc", "--notheorycorr", dest="THCORR", default=True, action="store_false",
                           help="Assume SM theory uncertainties are uncorrelated")
        stats.add_argument("--mnp", "--minimize_np", action="store_true", dest="MIN_NP", default=False,
                           help="If using correlations, perform nuisance parameter minimization (slow)")
        stats.add_argument("--min_syst", dest="MIN_SYST", default=cfg.min_syst, type=float,
                           help="Correlated systematic errors with a maximum fractional contribution below this will be ignored")
        stats.add_argument("--error_precision", dest="ERR_PREC", default=cfg.err_prec,
                           help="precision cut off in nuisance parameters when minimizing LL")
        stats.add_argument("--ll_precision", dest="LL_PREC", default=cfg.ll_prec,
                           help="precision cut off in LL when minimizing it")
        stats.add_argument("--n_iter", dest="N_ITER", default=cfg.n_iter, type=int,
                           help="minimize cuts off after n_iter*n_variables iterations")
        stats.add_argument("--min_num_sys", dest="MNS", default=cfg.min_num_sys, type=int,
                           help="minimum number of systematic nuisance parameters for them to be treated as correlated")
        select.add_argument("--split-pools", action="append", dest="POOLPATTERNS", default=[],
                            help="write out histograms from analyses in given pools separately")
        select.add_argument("--ana-split", action="append", dest="ANASPLIT", default=[],
                            help="write out histograms from given analyses separately")


        
    # arguments for manipulating a grid of batch files
    if "tools" in active_groups:
        options = parser.add_argument_group("Control options")

        parser.add_argument('scan_dirs', nargs='*', help='scan directories to process.')

        options.add_argument("--merge", action="store_true", dest="MERGE_GRIDS",
                             default=False, help="merge two or more grids using symbolic links. Excludes other options")

        options.add_argument("--rm", "--remove-merged", action="store_true", dest="RM_MERGED",
                             default=False, help="if unmerged yodas exist, unzip them, and remove merged ones")

        options.add_argument("-x", action="append", dest="ANAPATTERNS", default=[],
                             help="create a new grid containing output of only these analyses")

        options.add_argument("--nc", "--no-clean", action="store_true", dest="DO_NOT_CLEAN",
                             default=False, help="do not remove unnecessary files.")

        options.add_argument("--archive", action="store_true", dest="COMPRESS_GRID",
                             default=False, help="remove intermediate and unncessary files, and compress others.")

        options.add_argument("-c", "--check", action="store_true", dest="CHECK_GRID",
                             default=False, help="check whether all grid points have valid yodas")

        options.add_argument("--ca", "--check-all", action="store_true", dest="CHECK_ALL",
                             default=False, help="include grid points without logfiles when checking for yodas")

        options.add_argument("-S", "--submit", action="store_true", dest="RESUB",
                             default=False, help="(re)submit any jobs which are found to have failed.")

        options.add_argument("--detail", action="store_true", dest="PARAM_DETAIL", default=False,
                             help="output detailed information for certain parameter point")

        options.add_argument("--plot", action="store_true", dest="PLOT", default=False,
                             help="make histograms for specified parameters (much slower!)")

    # arguments for handling batch job submission
    if "batch" in active_groups:
        # Optional arguments
        parser.add_argument("-o", "--outputdir", dest="OUTPUTDIR", type=str,
                            default="myscan00", help="Specify the output directory name.")
        parser.add_argument('-p', '--param_file', dest='param_file', type=str,
                            default=cfg.param_steering_file, help='File specifying parameter space.')
        parser.add_argument('-t', '--template', dest='template_file',
                            default=cfg.mceg_template, help='Template Herwig .in file.')
        parser.add_argument("-r", "--runinfo", dest="run_info", type=str, default=cfg.run_info, 
                            help=("Directory with required run information. Set to 'none' to not use one."))
        parser.add_argument("-n", "--numevents", dest="num_events",
                            default=cfg.default_nev, type=int, help="Number of events to generate.")
        parser.add_argument('--seed', dest='seed', default=cfg.seed,
                            type=int, help="Seed for random number generator.")
        parser.add_argument("-Q", "--queue", dest="queue", default="", type=str, help="batch queue.")
        parser.add_argument('-s', '--scan_only', '--scan-only', dest='scan_only', default=False,
                            action='store_true', help='Only perform scan and do not submit batch job.')
        parser.add_argument('-b', '--beams', dest="BEAMS", default="13TeV", type=str,
                            help=f"Generate events using these beams. Known beams are {get_beam_names(allow_all=True)}. NOTE: em_ep_91_2 is currently beta, see https://gitlab.com/hepcedar/rivet/-/issues/293.")
        parser.add_argument('-P', '--pipe_hepmc', '--pipe-hepmc', dest="pipe_hepmc", default=False,
                            action='store_true', help="Rivet reading from pipe.")
        parser.add_argument('-w', '--wallTime', '--walltime', type=str, default=None,
                            help="Set maximum wall time for jobs (HH:MM).")
        parser.add_argument('--memory', type=str, default=None,
                            help="Set maximum memory consumption for jobs (e.g. 2G).")
        parser.add_argument('-B', '--batch', dest="batch_system", default='qsub',
                            type=str, help="Specify which batch system is using, support: qsub, condor or slurm")
        parser.add_argument('-V', '--variablePrecision', action='store_true',
                            help='Use this flag to make number of events for each point variable')
        parser.add_argument("--single", action="store_true", dest="SINGLE", default=False,
                            help="just generate one example directory, no job submission")


        parser.add_argument("-g", "--analyse_grid", dest="analyse_grid", default=None,
                            help="run analysis and make map files from an existing grid.")
        parser.add_argument("-N", "--num_points", dest="num_points", default=50,
                            help="break an analysis run down into jobs/maps with N parameter points in each")
        parser.add_argument("-a", "--analysis_flags", dest="analysis_flags", default="",
                            help="flags to pass to the contur analysis step (separate with commas)")
        parser.add_argument("--setup", dest="setup_script", default=None,
                            help="specify a setup script to be sourced at start of analysis batch job.")
        parser.add_argument("-db", "--initDB", action="store_true", dest="INIT_DB", default=False,
                             help="init responsive db for grid mode")

    # arguments for handling the cross section/branch fraction extraction.
    if "xsbf" in active_groups:

        parser.add_argument('inputDir', nargs='*', help="Path to scan directory")
        parser.add_argument("-t", "--tolerance", type=float,
                            help="Minimum cross-section in fb for a process to be drawn", dest="tolerance", default=0.0)
        parser.add_argument("--txs", "--xsFracTolerance", type=float,
                            help="Fractional tolerance for which processes to include. Processes which contribute less than this xs at a given point are ignored", dest="fractolerance", default=0.0)
        parser.add_argument("--br", "--foldBRs", help="Whether or not to fold in the branching ratios",
                            dest="foldBRs", default=False, action="store_true")
        parser.add_argument("--bsm_br", "--foldBSMBRs", help="Whether or not to fold in the BSM branching ratios ",
                            dest="foldBSMBRs", default=False, action="store_true")
        parser.add_argument("--sl", "--splitLeptons", help="Leptons e, mu tau are set to l by default. Apply this flag to split them again",
                            dest="splitLeptons", default=False, action="store_true")
        parser.add_argument("--mb", "--mergeBosons", help="Set W, Z, H to V",
                            dest="mergeEWBosons", default=False, action="store_true")
        parser.add_argument("--sp", "--splitIncomingPartons", help="We normally don't care about the incoming partons, just set them to pp. Apply this flag to split them again",
                            dest="splitIncomingPartons", default=False, action="store_true")
        parser.add_argument("--sa", "--splitAntiparticles", help="Particles and antiparticles are merged by default. Add this options to split them out",
                            dest="splitAntiParticles", default=False, action="store_true")
        parser.add_argument("--sb", "--splitB", help="u, d, s, c, b are grouped into q by default. Add this options to split out the b",
                            dest="splitBQuarks", default=False, action="store_true")
        parser.add_argument("--sq", "--splitLightQuarks", help="u, d, s, c, b are grouped into q by default. Add this options to split them out",
                            dest="splitLightQuarks", default=False, action="store_true")
        parser.add_argument("--p", "--pools", help="Split into pools based on final state ? Only works with --br option",
                            dest="splitIntoPools", default=False, action="store_true")
        parser.add_argument("--xy", help="Variables to scan", dest="xy", default=None )
        parser.add_argument("--bro", "--onlyBRs", help="Print ONLY the BSM branching ratios and exit.",
                            dest="printBRsOnly", default=False, action="store_true")
        parser.add_argument("--ws","--website", help="Alternative format output for web-visializer",
                            dest="ws", default=False, action="store_true")

    # arguments for handling the cross section scan
    if "xsscan" in active_groups:

        parser.add_argument("-o", "--outputdir", help="Output directory for your plots",
                            dest="OUTPUTDIR", default="CONTUR_xs_scans/")
        parser.add_argument("--xc", "--ignoreCache",
                            help="Extraction of the cross-sections for each point are cached by default to speed up processing."
                            "If you don't want to use caching, use this flag", dest="ignoreCache", default=False, action="store_true")
        parser.add_argument("--cc", "--clearCache",
                            help="Extraction of the cross-sections for each point are cached by default to speed up processing."
                            "If you want to reset the cache, use this flag",
                            dest="clearCache", default=False, action="store_true")
        parser.add_argument("--do", "--drawTo", help="Output directory for plots of BRs, if using.",
                            dest="drawToDir", default="")

    if "mceg_select" in active_groups:
        parser.add_argument("-m", "--mceg", dest="mceg", default=cfg.mceg,
                            type=str, help="MC event generator.")
        
    if "html" in active_groups:
        
        parser.add_argument("-i", "--indir", dest="INPUTDIR",
                            default=cfg.input_dir, help="the ANALYSIS directory storing contur output")
        parser.add_argument("-o", "--outdir", dest="OUTPUTDIR",
                            default="contur-plots", help="directory where output will be written.")
        parser.add_argument("-n", "--num-threads", metavar="NUMTHREADS", dest="NUMTHREADS", type=int,
                            default=None, help="request make-plots to use a specific number of threads")
        parser.add_argument("--no-cleanup", dest="NO_CLEANUP", action="store_true", default=False,
                            help="keep plotting temporary directory")
        parser.add_argument("--no-subproc", dest="NO_SUBPROC", action="store_true", default=False,
                            help="don't use subprocesses to render the plots in parallel -- useful for debugging")
        parser.add_argument("--pwd", dest="PATH_PWD", action="store_true", default=False,
                            help="append the current directory (pwd) to the analysis/data search paths (cf. $RIVET_ANALYSIS_PATH)")        
        parser.add_argument("--all", dest="ALLPLOTS", default=False, action="store_true",
                            help="Make all plots. (By default only those contributing to the exclusion are made.)")
        parser.add_argument("--vis","--forVisualiser", dest="FORVISUALISER", action="store_true", default=False,
                            help="Tweak the way the output is written, for use in contur-visualiser")
        parser.add_argument("--ana-match", action="append", dest="ANAPATTERNS", default=[],
                            help="only run on these analyses")
        parser.add_argument("--ana-unmatch", action="append", dest="ANAUNPATTERNS", default=[],
                            help="exclude these analyses")

        stygroup = parser.add_argument_group("Style options")
        stygroup.add_argument("-t", "--title", dest="TITLE",
                              default="Constraints On New Theories Using Rivet",
                              help="title to be displayed on the main web page")
        stygroup.add_argument("-a","--all-errbars", dest="ALL_ERRBARS", action="store_true",
                              default=False, help="Draw error bars on all histos.")
        stygroup.add_argument("--offline", dest="OFFLINE", action="store_true",
                              default=False, help="generate HTML that does not use external URLs.")
        stygroup.add_argument("--font", dest="OUTPUT_FONT", choices="palatino,cm,times,helvetica,minion".split(","),
                              default="palatino", help="choose the font to be used in the plots")
        stygroup.add_argument("-c","--config", dest="CONFIG",
                              default="", help="supply a plot config file. See examples in $CONTUR_ROOT/data/Plotting")
        
    if "smtheory" in active_groups:

        parser.add_argument("-a", "--analysis", dest="ANALYSIS",
                          default="all",
                          help="Which analysis do you want to make theory for? (comma separated list)")
        parser.add_argument("-i", "--input", dest="INPUTDIR",
                          default=cfg.path("data/TheoryRaw"),
                          help="Root directory for the theory raw data")
        
    return parser

def valid_mceg_arg(args):
    '''
    Checks the arguments for what mceg is selected, and set cfg.mceg
    Returns False if the selection is isvalid.
    '''

    if not args['mceg'] in cfg.known_mcegs:
        cfg.contur_log.error("Unrecognised event generator: {}".format(args['mceg']))
        return False
    else:
        cfg.mceg = args['mceg']
        try:
            cfg.mceg_template = os.path.basename(args['template_file'])
        except:
            # this is ok, the template file arg is not defined when extracting xsecs, for example
            pass
        return True
    
def valid_beam_arg(args):
    '''
    Checks the arguments for what beams are selected and return them in a list. 
    Returns None if the selection is isvalid.
    '''

    known_beams = get_beams()
    try:
        if args['BEAMS'] == "all":
            return known_beams

        else:
            beams = []
            try_beams = args['BEAMS'].split(",")
            for try_beam in try_beams:
                found_beam = False
                for beam in known_beams:
                    if try_beam == beam.id:
                        beams.append(beam)
                        found_beam = True
                if not found_beam:
                    contur.config.contur_log.error("Beam {} is not known. Possible beams are: {}".format(try_beam, get_beam_names(allow_all=True)))
                    return None
            return beams

    except KeyError:
        return known_beams
            

def valid_batch_arguments(args):
    """
    Check that command line arguments are valid; return True or False.
    This function is also responsible for formatting some arguments e.g.
    converting the RunInfo path to an absolute path and checking it contains .ana files.
    valid_args = True

    """
    valid_args = True

    beams = valid_beam_arg(args)
    if beams is None:
        return False, None
    

    if args['wallTime'] is not None:
        timespans = args['wallTime'].split(":")
        if len(timespans) != 2:
            cfg.contur_log.error("Have to give max wall time in the format <hh:mm>!")
            valid_args = False
        else:
            try:
                for span in timespans:
                    span = int(span)
                    if span >= 60:
                        cfg.contur_log.error(
                            "Have to give time spans of less than 60 [units]!")
                        valid_args = False
            except ValueError:
                cfg.contur_log.error("Have to give time spans that can be converted to integers!")
                valid_args = False

    if args['memory'] is not None:
        number, unit = args['memory'][0:-1], args['memory'][-1]
        valid_units = ["M", "G"]
        if unit not in valid_units:
            cfg.contur_log.error("'%s' is not a valid unit for the memory. (%s are valid units.)" % (
                unit, valid_units))
            valid_args = False
        if not number.isdigit():
            cfg.contur_log.error("'%s' is not a valid number for the memory." % number)
            valid_args = False

    if args['analyse_grid']:
        cfg.contur_log.info("Analysing existing grid: {}".format(args['analyse_grid']))
        if args['num_points']:
            try:
                n_points = int(args['num_points'])
                cfg.contur_log.info(
                    "Splitting into {} parameter points per map file.".format(args['num_points']))
            except ValueError:
                cfg.contur_log.error(
                    "Number of points {} cannot be converted to integer!".format(args['num_points']))
                valid_args = False

        return valid_args, beams

    if not os.path.exists(args['param_file']):
        cfg.contur_log.error("Param file '%s' does not exist!" % args['param_file'])
        valid_args = False

    if not os.path.exists(args['template_file']):
        cfg.contur_log.error("Template file '%s' does not exist!" % args['template_file'])
        valid_args = False

    if args['run_info'].lower() == 'none':
        args['run_info'] = None
    else:
        args['run_info'] = os.path.abspath(args['run_info'])
        if not os.path.isdir(args['run_info']):
            cfg.contur_log.info("Creating run information directory '{}'!".format(args['run_info']))
            from contur.util.utils import mkoutdir
            mkoutdir(args['run_info'])

        for beam in beams:
            afile = beam.id + ".ana"
            if not os.path.exists(os.path.join(args['run_info'], afile)):
                gpfrom = os.path.join(cfg.share, afile)
                gpto = os.path.join(args['run_info'], afile)
                cfg.contur_log.info("Copying {} to {}".format(gpfrom, gpto))
                copyfile(gpfrom, gpto)

    try:
        int(args['num_events'])
    except ValueError:
        cfg.contur_log.error("Number of events '%s' cannot be converted to integer!"
                                       % args['num_events'])
        valid_args = False

    try:
        args['seed'] = int(args['seed'])
    except ValueError:
        cfg.contur_log.error("Seed '%s' cannot be converted to integer!" % args['seed'])
        valid_args = False

    valid_args = valid_mceg_arg(args)
        
    return valid_args, beams


def setup_common(args):
    """
    Set up the configuration parameters for the common arguments/flags.
    If printVersion is set, do this and exit
    """

    if args['printVersion']:
        print("Contur " + contur.config.version.version)
        sys.exit(0)

    cfg.logfile_name = args['LOG']
    cfg.setup_logger(filename=cfg.logfile_name,logstream=args.get("LOGSTREAM"))
    
    cfg.contur_log.setLevel(logging.INFO)
    if args['QUIET']:
        cfg.contur_log.setLevel(logging.WARNING)
    else:
        from contur.util.utils import write_banner
        write_banner()
    if args['DEBUG']:
        cfg.contur_log.setLevel(logging.DEBUG)

    # This is a very common flag but there are some cases where it isn't defined.
    try:
        cfg.output_dir = args['OUTPUTDIR']
        if not os.path.isabs(cfg.output_dir):
            cfg.output_dir = os.path.join(os.getcwd(),cfg.output_dir)
    except KeyError:
        pass
    except TypeError:
        pass

def setup_batch(args):
    """
    setup up the configuration parameters for the batch arguments/flags
    """

    cfg.param_steering_file = args['param_file']

    cfg.using_condor = (args['batch_system'] == 'condor')
    cfg.using_slurm = (args['batch_system'] == 'slurm')
    cfg.using_qsub = not (
            cfg.using_condor or cfg.using_slurm)


def setup_stats(args, message):
    """
    setup the parameters for the stats argument group
    """

    if not (args['MNS'] == cfg.min_num_sys):
        print("args[MNS]",args['MNS'],cfg.min_num_sys)        
        cfg.min_num_sys = args['MNS']
        message += "Minimum number of systematic uncertainties contributions for correlations changed to {} \n".format(
            cfg.min_num_sys)
        
    cfg.useTheoryCorr = args['THCORR']
    if cfg.useTheoryCorr:
        message += "Theory uncertainties assumed correlated. \n"
    else:
        message += "Theory uncertainties assumed uncorrelated. \n"        


    if args['UNCORR']:
        cfg.diag = True
        message += "No data systematic correlations being used. \n"

    else:                

        if not cfg.min_syst == args['MIN_SYST']:
            cfg.min_syst = float(args['MIN_SYST'])
            message += "Systematic materiality cutoff changed to {} \n".format(
                cfg.min_syst)

        # are we minimising nuisance parameters?
        if args['MIN_NP']:
            message += "Attempting marginalisation over nuisance parameters \n"
            cfg.min_np = True

            if not cfg.ll_prec == float(args['LL_PREC']):
                cfg.ll_prec = float(args['LL_PREC'])
                message += "LL precision criterion changed to  {} \n".format(
                    cfg.ll_prec)

            if not cfg.n_iter == int(args['N_ITER']):
                cfg.n_iter = int(args['N_ITER'])
                message += "max number of iterations changed to  {} \n".format(
                    cfg.n_iter)

            if not cfg.err_prec == float(args['ERR_PREC']):
                cfg.err_prec = float(args['ERR_PREC'])
                message += "Precision cut off in nuisance parameters when minimizing LL changed to {} \n".format(
                    cfg.err_prec)

    return message

def setup_selection(args,modeMessage):

    if args['EXCLUDEHGG']:
        cfg.excludeHgg = True
        modeMessage += "Excluding Higgs to photons measurements \n"

    if args['USESEARCHES']:
        cfg.exclude_searches = False
        modeMessage += "Using search analyses \n"

    if args['TRACKSONLY']:
        cfg.tracks_only=True
        modeMessage += "Including only plots which are based on tracking information \n"

    if args['USESOFTPHYSICS']:
        cfg.exclude_soft_physics=False
        modeMessage += "Including soft QCD stuff. Hope you know what you are doing! \n"

    if args['USEHWW']:
        cfg.exclude_hww = False
        modeMessage += "Including Higgs to WW measurements if available \n"

    if args['USEBV']:
        cfg.exclude_b_veto = False
        modeMessage += "Including secret b-veto measurements if available \n"

    if args['USEAWZ']:
        cfg.exclude_awz = False
        modeMessage += "Including ATLAS WZ SM measurement \n"

    if args['EXCLUDEMETRAT']:
        cfg.exclude_met_ratio = True
        modeMessage += "Excluding MET ratio measurements \n"

    return modeMessage

