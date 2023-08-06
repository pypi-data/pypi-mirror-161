
# functions build theory reference yodas from various raw inputs.

import contur
import re
import sys
import os
import rivet
import yoda
from contur.data.sm_theory_builders import *
import contur.config.config as cfg
from contur.run.arg_utils import setup_common

def make_sm_yoda(analysis):
    '''
    Make the SM yoda file for analysis

    Reads a yoda file from a standard location, filters out analysis objects which
    are not assigned to an analysis pool.

    If source == "REF", will look for additonal y axes on the REF plots (y02 by default, others from axis parameter) 
                        and convert into y01 /THY versions. 

    if source == "RAW" will look in the TheoryRaw areas for /THY/ yodas and just filter them.

    if source == "HEPDATA" will look in the TheoryRaw area for a HEPDATA download

    if source == "SPECIAL" invoke a special routine for this analysis (usually reading from
                           text files supplied by theorists).

    the above will only be applied to histograms with a regexp match to the pattern.

    '''

    ao_out = []
    a_name = analysis.shortname    
    if analysis.sm() is None:
        return
    

    output_aos = {}
    
    for prediction in analysis.sm():
    
        if prediction.file_name not in output_aos:
            output_aos[prediction.file_name] = []
        
        if prediction.origin == "RAW":

            cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
            f = os.path.join(os.getenv("CONTUR_ROOT"),"data","TheoryRaw",a_name,a_name)
            if prediction.axis is not None:
                f = f+"-Theory"+prediction.axis+".yoda"
            else:
                f = f+"-Theory.yoda"
            if  os.path.isfile(f):
                cfg.contur_log.debug("Reading from {}".format(f))
                aos = yoda.read(f)
                for path, ao in aos.items():
                    if rivet.isTheoryPath(path):
                        pool = contur.data.get_pool(path=path)
                        if pool is not None:
                            if ao.type() == "Scatter1D":
                                ao = contur.util.mkScatter2D(ao)
                            ao.setTitle(prediction.short_description)
                            output_aos[prediction.file_name].append(ao)
                        else:
                            cfg.contur_log.debug("No pool for {}".format(path))

            else:
                cfg.contur_log.critical("File {} does not exist.".format(f))

        elif prediction.origin == "REF":
            # from the installed ref data
            cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
            
            f = contur.util.utils.find_ref_file(analysis)
            aos = yoda.read(f)
            for path, ao in aos.items():            
                pool = contur.data.get_pool(path=path)
                if pool is not None:
                    if re.search(prediction.pattern, path):
                        # get the appropriate theory axis for this plot.
                        thypath = path[:-3]+prediction.axis
                        thy_ao = aos[thypath]                        
                        if thy_ao.type() == "Scatter1D":
                            thy_ao = contur.util.mkScatter2D(thy_ao)
                        thy_ao.setPath("/THY"+path[4:])
                        thy_ao.setTitle(prediction.short_description)
                        output_aos[prediction.file_name].append(thy_ao)

        elif prediction.origin == "HEPDATA":
            
            # from specially downloaded HEPData
            cfg.contur_log.info("Making SM theory for {}".format(analysis.name))            
            f = os.path.join(os.getenv("CONTUR_ROOT"),"data","TheoryRaw",a_name,a_name)
            f = f+".yoda.gz"

            aos = yoda.read(f)
            cfg.contur_log.debug("Reading from {}".format(f))
            for path, ao in aos.items():            
                pool = contur.data.get_pool(path=path)
                cfg.contur_log.debug("Pool is {} for {}".format(pool.id,path))
                if pool is not None:
                    if re.search(prediction.pattern, path):
                        thypath = path+prediction.axis
                        try:
                            thy_ao = aos[thypath]
                            if thy_ao.type() == "Scatter1D":
                                thy_ao = contur.util.mkScatter2D(thy_ao)
                            thy_ao.setPath("/THY"+path[4:])
                            thy_ao.setTitle(prediction.short_description)
                            output_aos[prediction.file_name].append(thy_ao)
                        except KeyError:
                            pass
                        
        elif prediction.origin == "SPECIAL":

            if analysis.name == "ATLAS_2016_I1457605":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_ATLAS_2016_I1457605(prediction)

            if analysis.name == "ATLAS_2017_I1645627":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_ATLAS_2017_I1645627(prediction)

            if analysis.name == "ATLAS_2012_I1199269":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_ATLAS_2012_I1199269(prediction)
                
            if analysis.name == "ATLAS_2017_I1591327":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_ATLAS_2017_I1591327(prediction)

            if analysis.name == "ATLAS_2016_I1467454:LMODE=MU":
                cfg.contur_log.info("Making SM theory for {} (E and MU)".format(analysis.shortname))
                # this actually does both EL and MU
                do_ATLAS_2016_I1467454(prediction)

            if analysis.name == "CMS_2017_I1467451":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_CMS_2017_I1467451(prediction)

            if analysis.name == "ATLAS_2015_I1408516:LMODE=MU":
                cfg.contur_log.info("Making SM theory for {} (E and MU)".format(analysis.shortname))
                # this actually does both EL and MU
                do_ATLAS_2015_I1408516(prediction)

            if analysis.name == "ATLAS_2019_I1725190":
                cfg.contur_log.info("Making ATLAS background fit for {}".format(analysis.name))
                do_ATLAS_2019_I1725190(prediction)
                
            if analysis.name == "ATLAS_2021_I1852328":
                cfg.contur_log.info("Making SM theory for {}".format(analysis.name))
                do_ATLAS_2021_I1852328(prediction)
                
        else:
            cfg.contur_log.critical("Unknown source {}".format(source))
            sys.exit(1)

    for fname, ao_out in output_aos.items():
        if len(ao_out)>0:
            yoda.write(ao_out, fname)

    return


def main(args):
    """
    Main programme to run over the known analysis and build SM theory yodas from the TheoryRaw or REF areas.
    """
#    cfg.setup_logger(filename="contur_mkthy.log")
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    cfg.input_dir = args["INPUTDIR"]
    cfg.contur_log.info("Looking for raw theory files in {}".format(cfg.input_dir))
        
    do_all = (args['ANALYSIS'] == "all")

    # -------------------------------------
    for analysis in contur.data.get_analyses(filter=False):
        if analysis.shortname in args["ANALYSIS"] or do_all:
            make_sm_yoda(analysis)            
        
