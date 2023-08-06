import sys, os
import contur.config.config as cfg
import yoda, rivet



def get_histos(filename):
    """
    Get signal histograms from a generated YODA file.
    Loops over all yoda objects in the input file looking for valid signal histograms.

    Ignores REF and THY (which are read elsewhere) and RAW histograms.

    :Param filename: (```string```) name of yoda input file.

    Returns: 

    *   mchistos = dictionary containing {path, ao} pairs for candidate signal histograms.
    *   xsec     = yoda analysis object containing the generated xsec and its uncertainty
    *   Nev      = yoda analysis object containing sum of weights, sum of squared weight, number of events

    """
    
    mchistos = {}
    xsec = None
    Nev = None

    try:
        analysisobjects = yoda.read(filename)
    except Exception as e:
        cfg.contur_log.error("Failed to read {}. {}".format(filename,e))
        return None, None, None

    cfg.contur_log.info("Found {} analysisobjects in {}".format(len(analysisobjects),filename))
    for path, ao in analysisobjects.items():
        if path.startswith('/_EVTCOUNT'):
            Nev = ao
        if path.startswith('/_XSEC'):
            xsec = ao
        if os.path.basename(path).startswith("_"):
            continue
        if rivet.isRefPath(path):
            # Reference histograms are read elsewhere.
            continue
        if rivet.isRawPath(path):
            continue
        if rivet.isTheoryPath(path):
            # Theory histograms are read elsewhere.
            continue


        else:
            if path not in mchistos:
                mchistos[path] = ao

                
    if xsec is not None and Nev is not None:    
        cfg.contur_log.info("Found {} potentially valid histograms in {}, with cross section {} pb".format(len(mchistos),filename,xsec.point(0).x()))
    else:    
        cfg.contur_log.warning("Found {} potentially valid histograms in {}, but number of events or cross section could not be determined.".format(len(mchistos),filename))
        
    return mchistos, xsec, Nev

def read_slha_file(root,slha_file,block_list):
    """ 
    read requested blocks from an SLHA1 file (if found) 

    returns a dictionary blocks_dict{ block: {name: value} } 
    for each block in block_list.

    the name of the block is prepended to each parameter, for disambiguation when
    written to the map file.

    for the MASS block the binwidth and binoffset will be applied, if provided.
    @TODO that would be better handled at the visualisation/plotting step?

    :param root: path to SLHA file
    :param slha_file: name of SLHA file
    :param block_list: list of SLHA blocks to read

    :return: dictionary  (blockname, (name, value))

    """

    import pyslha
    blocks_dict = {}

    shla_file_path = os.path.join(root, slha_file)
    if os.path.exists(shla_file_path):

        slha_file = open(shla_file_path, 'r')
        d = pyslha.read(slha_file)
        for block in block_list:
            tmp_dict = {}
            for k, v in d.blocks[block].items():
                if block == "MASS" and cfg.binwidth > 0:
                    tmp_dict["{}:{}".format(block,k)]=cfg.binoffset+cfg.binwidth*int(abs(v)/cfg.binwidth)
                else:
                    tmp_dict["{}:{}".format(block,k)]=v  
            blocks_dict[block]=tmp_dict

    else:
        cfg.contur_log.warning("{} does not exist".format(shla_file_path))
        
              
    return blocks_dict



def read_param_point(file_path):
    """
    Read a parameter file and return dictionary of (strings of) contents

    :param file_path: full path the the parameter file
    :type file_path: string

    :return: dictionary of parameter (parameter_name, value) pairs

    """
    with open(file_path, 'r') as param_file:
        raw_params = param_file.read().strip().split('\n')

    param_dict = {}
    for param in raw_params:
        name, value = param.split(' = ')
        param_dict[name] = value

    return param_dict


def get_generator_values(root, files, matrix_elements, particles):
    ''' 
    read and parse the generator log files to get subprocess cross sections 
    and/or particle properties.
    '''

    additional_params = {}
    
    if matrix_elements == None and particles == None:
        # nothing to see here.
        return additional_params

    if cfg.mceg=="herwig":
        # If requested, get particle info from the generator log files
        if particles is not None:
            particle_list = particles.split(",")
            particle_props = contur.util.read_herwig_log_file(root, files, particle_list)
            additional_params.update(particle_props)

        if matrix_elements is not None:
            me_list = matrix_elements.split(",")
            additional_params.update(contur.util.read_herwig_out_file(
                root, files, me_list, particles, particle_props))

        cfg.contur_log.info("Added this info: {}".format(additional_params))
                
            
    else:
        cfg.contur_log.error("Log file parsing is not yet implemented for {}.".format(mceg))
        sys.exit(1)


        
                                       
    return additional_params
