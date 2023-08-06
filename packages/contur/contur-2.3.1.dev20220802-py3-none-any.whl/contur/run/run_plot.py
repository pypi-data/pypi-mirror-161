""" 
Making plots out of map files 
"""

from inspect import getmembers, isfunction
import importlib

import matplotlib
matplotlib.use('Agg')

import contur
import contur.config.config as cfg
from contur.plot.contur_plot import ConturPlotBase
from contur.run.arg_utils import setup_common
import contur.util.utils as cutil

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys, os, pickle
import logging


def load_external_function(file_name):
    """ 
    Load exteral functions for plotting additonal contours, from command line.

    :param file_name: the name of the file containing the functions, with or without a .py extension. can be specified with a (rel or abs) path, otherwise with be assumed to be in the current working directory.


    """   

    if "/" not in file_name:
        directory = os.path.join(".", file_name)

        
    moddir, modfile = os.path.split(file_name)
    modname = os.path.splitext(modfile)[0]

    # Set the import path as needed, and import the module from there
    sys.path.append(moddir)
    i = importlib.import_module(modname)
    store = [o for o in getmembers(i) if isfunction(o[1])]

    # Alphabetically sort this list in place so the colors are consistently trackable
    store.sort(key=lambda v: (v[0].upper(), v[0].islower()))
    cfg.contur_log.info("Imported additional constraints from {}".format(file_name))
    return store

def main(args):
    """
    Main method Executable to make contur/contour plots from map files.
    args should be a dictionary
    """

    # set up the logging
#    cfg.logfile_name = args['LOG']
#    cfg.setup_logger(filename=cfg.logfile_name)
    # set up the general argument flags
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))


    # don't write bytecode, since this isn't CPU intensive
    sys.dont_write_bytecode = True
    
    # Error catching
    parsing_error_msg = ("To call contur-plot you must specify an input .map "
                         "file and 2 or 3 variables to plot!\nThe format must "
                         "follow:\ncontur-plot .map_file x_variable "
                         "y_variable [z_variable] [optional_arguments]")
    if len(args['variables']) not in [2, 3]:
        cfg.contur_log.critical("Error parsing arguments!\n\n" + parsing_error_msg)
        sys.exit()

    # Import a module containing grids to define extra contours    
    if args['externalGrid']:
        external_grids=load_external_function(args['externalGrid'])
    # Import a module containing functions to define extra contours    
    if args['externalFunction']:
        external_functions=load_external_function(args['externalFunction'])

    # set the colour for the main 68/95 contours TODO allow user to set this again, now this is a dict keyed on stat_type
    #cfg.contour_colour = args['contour_colour']

    # set the out file format
    cfg.plot_format = args['plot_format']

    
    # Run the conturPlot processing
    with open(args['map_file'][0], 'rb') as f:

        # load the map file
        file = pickle.load(f)

        # make the output directory, if not already present
        cutil.mkoutdir(args['OUTPUTDIR'])

        if args['databg']:
            primary_stat = cfg.databg
        else:
            primary_stat = cfg.smbg
        
        # create contur plotbase object which extends the contur depot class
        ctrPlot = ConturPlotBase(file,
                                 outPath=args['OUTPUTDIR'], plotTitle=args['title'],
                                 savePlotFile=args['save_plots'], omittedPools=args['omit'],
                                 iLevel=args['ilevel'], iSigma=args['isigma'], clLevel=args['ndpools'],
                                 style=args['style'], showcls=args['showcls'], simplecls=args['simplecls'],
                                 primary_stat=primary_stat,
                                 show_secondary=args['secondary_contours'])

        # tell the plotbase object whether or not we are plotting the separate analysis pool plots
        ctrPlot.do_plot_pools = args['plot_pools']

        # add the external grids and functions to the plotbase, if present
        if args['externalFunction']:
            ctrPlot.add_external_functions(external_functions)
        if args['externalGrid']:
            ctrPlot.add_external_grids(external_grids)

        # build the axes
        ctrPlot.build_axes_from_grid(xarg=args['variables'][0], yarg=args['variables'][1], logX=args['xlog'],
                                     logY=args['ylog'],
                                     xlabel=args['xlabel'], ylabel=args['ylabel'])

        # plot them
        ctrPlot.plot_figures()

        
        if args['save_plots']:
            # save the plot objects for later matplotlib manipulation
            ctrPlot.dump_plot_objects()

    cfg.contur_log.info("Done")

def doc_argparser():
    """ wrap the arg parser for the documentation pages """    
    from contur.run.arg_utils import get_argparser    
    return get_argparser('mapplot')

