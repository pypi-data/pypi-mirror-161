
import rivet

import sys
import os
import pickle
import logging
import yoda
import matplotlib
import matplotlib.pyplot as pyp
matplotlib.use('Agg')

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import contur
import contur.config.config as cfg
import contur.config.paths
import contur.data.static_db as cdb
import contur.factories.likelihood as lh
import contur.factories.yoda_factories
import contur.factories.test_observable
import contur.util.utils as cutil
from contur.run.arg_utils import setup_stats, setup_common, setup_selection

def fake_thy_paths(ana,aos):
    '''
    make thy paths read from a file look like generated signal yoda paths for analysis ana.
    '''

    for ao in aos.values():
    
        old_ana, hname = cutil.splitPath(ao.path())

        new_path = "/"+ana + "/" + hname
        ao.setPath(new_path)


def main(args):
    '''
    arguments should be passed as a dictionary.
    '''
    
#    cfg.setup_logger(filename=args['LOG'])

    # set up / respond to the common argument flags.
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    modeMessage = "Performing SM test \n"
    modeMessage += "Contur is running in {} \n".format(os.getcwd())
    
    # set up the data selection options.
    modeMessage = setup_selection(args,modeMessage)
    cfg.mode = cfg.smbg
    
    modeMessage = setup_stats(args,modeMessage)

    if args['ANAPATTERNS']:
        cfg.onlyAnalyses = args['ANAPATTERNS']
        modeMessage += "Only using analysis objects whose path includes %s. \n" % args['ANAPATTERNS']

    if args['ANAUNPATTERNS']:
        cfg.vetoAnalyses = args['ANAUNPATTERNS']
        modeMessage += "Excluding analyses names: %s. \n" % args['ANAUNPATTERNS']
    
    cfg.contur_log.info(modeMessage)

    cfg.exclude_met_ratio=False
    cfg.exclude_hgg=False
    cfg.exclude_hww=False
    cfg.exclude_b_veto=False
    cfg.exclude_awz=False
    cfg.exclude_searches=False
    cfg.exclude_soft_physics=False
    cfg.tracks_only=False
    
    cfg.noStack=True

    if args["OUTPUTDIR"] is not None:
        plotdirs = [args["OUTPUTDIR"]]
        cfg.plot_dir = args["OUTPUTDIR"]
    else:
        plotdirs = [cfg.smdir]
        cfg.plot_dir = cfg.smdir

    cfg.contur_log.info("SM dat files will be written to {}".format(plotdirs[0]))
    
    # to make sure we don't read the same file more than once.
    read_once = []
    aolist= []
    analyses = cdb.get_analyses(filter=False)
    for analysis in sorted(analyses, key=lambda a: a.poolid):
        ana = analysis.name
        sm_theory = analysis.sm()
        if sm_theory is not None:
            for prediction in sm_theory:
                try:
                    aos = {}
                    if prediction.file_name not in read_once:
                        aos = yoda.read(contur.config.paths.data_path("data","Theory",prediction.file_name))
                        read_once.append(prediction.file_name)
                        fake_thy_paths(ana,aos)
                except:
                    try:
                        aos = yoda.read(contur.config.paths.data_path("data","TheoryRaw",ana,prediction.file_name))
                        fake_thy_paths(ana,aos)
                    except:
                        cfg.contur_log.critical("could not find SM file at {} or {}".format(contur.config.paths.data_path("data","Theory",prediction.file_name),contur.config.paths.data_path("data","TheoryRaw",ana,prediction.file_name)))
                        sys.exit(1)
                        
                aolist.extend(aos.values())
    
    pvalues = {}
    for thy in aolist:

        if cdb.validHisto(thy.path()):

            # now load the REF and SM THY info for this analysis
            contur.factories.yoda_factories.load_bg_data(thy.path())
        
            hist = contur.factories.test_observable.Observable(thy, None, None)
            if hist.pool is None:
                continue

            bin_widths = []
            for xerr in hist._ref.xErrs():
                bin_widths.append(xerr[0])

            sm_likelihood = lh.Likelihood(calculate=True,
                                          ratio=hist._isRatio,
                                          profile=hist._isProfile,
                                          lumi=hist._lumi,
                                          tags=hist.signal.path(),
                                          sm_values=hist.sm_values,
                                          measured_values=hist.measured_values)

            hist.likelihood = sm_likelihood

            # write the dat file for plotting
            if hist.thyplot is not None:
                cutil.write_yoda_dat(hist, nostack=True, smtest=True)
                
                name = "{}, {}".format(hist.pool, hist._ref.path()[5:])
                pvalues[name] = hist.get_sm_pval()
                
        else:
            cfg.contur_log.debug("{} was invalid.".format(thy.path()))


    pvalues = sorted(pvalues.items(), key=lambda x: x[1])
    
    probs = []
    cfg.contur_log.info("These distributions have a p value < 0.35")
    for name, value in pvalues:
        probs.append(value)
        if value < 0.35:
            cfg.contur_log.info("Measurement: {}, p-value = {}".format(name,value))

    cfg.contur_log.info("{} distributions were checked.".format(len(pvalues)))

    # make a plot of the more reliable probabilities... should be unitform 0->1 but never is.
    pyp.hist(probs,20,(0,1))
    pyp.ylabel('Frequency')
    pyp.xlabel('Probability')
    pyp.savefig("probs.pdf")

            
def doc_argparser():
    """ wrap the arg parser for the documentation pages """    
    from contur.run.arg_utils import get_argparser    
    return get_argparser('smtest')

