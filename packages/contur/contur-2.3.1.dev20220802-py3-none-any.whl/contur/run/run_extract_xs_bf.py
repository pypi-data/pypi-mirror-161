import os
import sys

import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import contur
import contur.config.config as cfg
from contur.run.arg_utils import *
from contur.util.utils import *

def run_extract_xs_bf(args,input_dir=None,outfile=None):
    
    '''
    Extract various requested cross sections and branching ratios from from Herwig
    out files.
    args should be a dictionary.
    '''

    try:
        drawToDir = args["drawToDir"]
    except KeyError:
        drawToDir = ""

    # Set up / respond to the common argument flags and logger config
#    cfg.setup_logger(filename=args['LOG'])
    setup_common(args) 

    if not valid_mceg_arg(args):
        sys.exit(1)
    
    print("Writing log to {}".format(cfg.logfile_name))

    # take this input directory from the arguments, unless it is set explicitly by the input parameter.
    if input_dir is None:
        try:
            input_dir = args["inputDir"][0]
        except IndexError:
            cfg.contur_log.critical("No input directory defined. Exiting.")
            sys.exit(1)
    # format input dir path
    if input_dir[-1] == "/":
        input_dir = input_dir[:-1]
        
    if args["foldBSMBRs"]:
        args["foldBRs"] = True

    # redirect the output if requested.
    if outfile is not None:

        orig_stdout = sys.stdout
        f = open(outfile, 'w')
        sys.stdout = f

        
    drawBRs=0
    valsText=""

    # open the params file and print values
    number = input_dir.split("/")[-1]
    param_file = os.path.join(input_dir,cfg.paramfile)
    if not os.path.isfile(param_file):
        cfg.contur_log.error("[ERROR] Required file {} does not exist. Abort.".format(param_file))
        sys.exit(1)
    fParams = open(param_file)
    vals={}                                       
    for l in fParams.readlines():
        l = l.strip()
        tokens = l.split(" = ")
        vals[tokens[0]] = float(tokens[1])
        valsText+="%s=%f, "%(tokens[0],float(tokens[1]))
    valsText=valsText[:-2]
    cfg.contur_log.info("Reading files in {}. \nParameter values are :: \n{} ".format(input_dir, valsText))
    print(" {} :: {} ".format(input_dir, valsText))

    
    # Get the particle properties
    if cfg.mceg == "herwig":
        # build the herwig log file format and import the relevant functions.
        from contur.util.herwig_utils import get_particle_properties, build_herwig_ME_map, get_herwig_cross_sections
        fstem = "{}/{}-S{}-{}{}".format(input_dir,cfg.mceg,cfg.seed,cfg.tag,number)

        # This is the file containing particle properties 
        f_log = open("{}.log".format(fstem))

        # This is the file containing cross sections
        fxs = open("{}.out".format(fstem))

    else:
        cfg.contur_log.critical("Cross section and branching fraction extract not yet implemented for {}. Exiting.".format(cfg.mceg))
        sys.exit(1)
        
    particle_props = get_particle_properties(f_log, foldBSMBRs=args["foldBSMBRs"], splitLeptons=args["splitLeptons"],
                                             splitBQuarks=args["splitBQuarks"], splitIncomingPartons=args["splitIncomingPartons"],
                                             splitLightQuarks=args["splitLightQuarks"], splitAntiParticles=args["splitAntiParticles"],
                                             mergeEWBosons=args["mergeEWBosons"])
    if args["printBRsOnly"]:
        printBRs(particle_props, tol=args["tolerance"], drawToDir=drawToDir)
        sys.exit(0)

    #### Get the cross sections

    fxs_lines=fxs.readlines()
    
    # populate herwigMEChainMap
    herwigMEChainMap = build_herwig_ME_map(fxs_lines,particle_props.keys())
        
    # get the cross sections
    totalXS, procDict = get_herwig_cross_sections(fxs_lines,herwigMEChainMap,particle_props,splitIncomingPartons=args["splitIncomingPartons"],
                                                  splitLightQuarks=args["splitLightQuarks"],
                                                  splitAntiParticles=args["splitAntiParticles"],
                                                  mergeEWBosons=args["mergeEWBosons"], splitLeptons=args["splitLeptons"],
                                                  splitBQuarks=args["splitBQuarks"],ws=args["ws"],foldBRs=args["foldBRs"],
                                                  tol=args["tolerance"], drawToDir=drawToDir)
    
    for k, v in reversed(sorted(procDict.items(), key=lambda item: item[1])):

        k=cleanupCommas(k)
        if v < 100*float(args["tolerance"]):
            break

        if not args["ws"]:  
            print("%.2f fb, (%.2f%%), %s"%(v*totalXS*0.01*1e6,v, k.replace("-->","\\rightarrow")))
        else:
            print("%s [%.2f fb, %.2f%%]"%(k.replace("\\rightarrow","->"), v*totalXS*0.01*1e6,v))


    if outfile is not None:
        sys.stdout = orig_stdout
        f.close()

    return

def main(args):
    run_extract_xs_bf(args)

