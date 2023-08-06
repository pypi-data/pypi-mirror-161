import contur.config
from contur.util.utils import *
import contur.config.config as cfg

'''
Various Herwig-specific utilites, mainly for reading output/log files. See also the herwig steering in the scan module.
'''


recognisedParticles = {
    "e+" : "e+",
    "e-" : "e-",
    "nu" : r"\nu",
    "mu" : r"\mu",
    "tau" : r"\tau",
    "W+" : "W",
    "W-" : "W",
    "Z0" : "Z",
    "gamma": " \\gamma ",  # TODO
}


def read_herwig_out_file(root,files,matrix_elements,particles,particle_props):
    """ 
    Find the Herwig .out file and read cross sections for requested matrix element values from it.

    :param root: Top directory from which to  searching for .out files began
    :type root: string
    :param files: List of files being searches
    :param matrix_elements: list of matrix elements to look for
    :param particles: list of the names of the particles we care about
    :return: dictionary of matrix element (name, value) pairs

    """

    for test_name in files:
        if test_name.endswith('.out'):
            out_file_path = os.path.join(root, test_name)
            with open(out_file_path, 'r') as fxs:

                fxs_lines=fxs.readlines()
    
                # populate herwigMEChainMap
                herwigMEChainMap = build_herwig_ME_map(fxs_lines,particles)
        
                # get the cross sections
                totalXS, procDict = get_herwig_cross_sections(fxs_lines,herwigMEChainMap,particle_props)

                
    procDict = compress_xsec_info(procDict,matrix_elements)
    
    return procDict

 
def read_herwig_log_file(root,files,particles):
    """
    Find the Herwig .log file and read various values from it

    :param root: Top directory from which to  searching for .log files began
    :type root: string
    :param files: List of files being searched
    :param particles: list of particles to look for
    :return: dictionary of (name, value) pairs for the extracted parameters.


    """
    particle_dict = {}

    for test_name in files:
        if test_name.endswith('.log'):
            log_file_path = os.path.join(root, test_name)

            # get the particle info
            with open(log_file_path, 'r') as fbr:
                property_dict = get_particle_properties(fbr)       

            for particle, info in property_dict.items():

                # sometimes have SM particles for which we don't (re)calculate masses and which we don't want to save.
                if 'mass' in info.keys():
                    # now add the requested particle info as parameters.
                    if particle in particles or 'ALL' in particles:
                        particle_dict.update(compress_particle_info(particle,info))
                    
    return particle_dict


def get_particle_properties(logfile, foldBSMBRs=False, splitLeptons=False, splitBQuarks=False, splitIncomingPartons=False,
                            splitLightQuarks=False, splitAntiParticles=False, mergeEWBosons=False):
    '''
    Read file logfile, extract particle properties into a dictionary
    
    :param: logfile file to read.
    
    :returns: ParticleDict, dictionary containing branching fractions, widths and mass

    '''
    ParticleDict = {}
    inBRBlock = False
    
    for line in logfile.readlines():
        line = line.strip()
        if "# Parent:" in line:
            inBRBlock = True
            values = line.split()
            lv = len(values)
            parent = values[lv-8]
            if not parent in ParticleDict.keys():
                ParticleDict[parent] = {}
            ParticleDict[parent]["width"] = float(values[lv-1])
            ParticleDict[parent]["mass"] = float(values[lv-5])
            continue
        if inBRBlock and "#" in line:
            continue
        if inBRBlock and not "->" in line:
            inBRBlock = False
            continue
        if not inBRBlock:
            continue
        p_d_string = make_latex_safe(line.split(";")[0], debug=1).split("\\rightarrow")
        parent = p_d_string [0]
        decay = p_d_string [1]
        br = float(line.split()[2])
        if br == 0:
            continue
        parent = parent.replace(",","").strip()
        if not parent in ParticleDict.keys():
            ParticleDict[parent] = {}
        if not decay in ParticleDict[parent].keys():
            ParticleDict[parent][decay] = 0
        ParticleDict[parent][decay] += br

    # add SM BRs:
    if not foldBSMBRs:
        if not "Z" in ParticleDict.keys():
            ParticleDict["Z"] = {}
            ParticleDict["Z"]["\\nu, \\nu"] = 0.205
            if splitLeptons:
                ParticleDict["Z"]["e, e"] = 0.035
                ParticleDict["Z"]["\\mu, \\mu"] = 0.035
                ParticleDict["Z"]["\\tau, \\tau"] = 0.035
            else:
                ParticleDict["Z"]["l, l"] = 0.105
            if splitBQuarks:
                ParticleDict["Z"]["b, b"] = 0.15
                ParticleDict["Z"]["q, q"] = 0.54
            else:
                ParticleDict["Z"]["q, q"] = 0.69

        if not "W" in ParticleDict.keys():
            ParticleDict["W"] = {}
            if splitLeptons:
                ParticleDict["W"]["e, \\nu"] = 0.105
                ParticleDict["W"]["\\mu, \\nu"] = 0.105
                ParticleDict["W"]["\\tau, \\nu"] = 0.105
            else:
                ParticleDict["W"]["l, \\nu"] = 0.32
            ParticleDict["W"]["q, q"] = 0.68

        if not "t" in ParticleDict.keys():
            if not splitBQuarks:
                ParticleDict["t"] = {"W, q": 1.0}
            else:
                ParticleDict["t"] = {"W, b": 1.0}
    else:
        #del ParticleDict["H"]
        if "H" in ParticleDict.keys(): del ParticleDict["H"]

    return ParticleDict


def make_latex_safe(text, splitIncomingPartons=False, splitLightQuarks=False, splitAntiParticles=False,
                    mergeEWBosons=False, splitLeptons=False, splitBQuarks=False, debug=0, isME=0):
    '''
    Take a line from a Herwig log (text) and make it into
    some reasonable latex, applying various criteria according to the input arguments.

    '''
    
    text = text.replace("bar", "BAR")
    #for p, lat in bsmParticles.items():
    #    text = text.replace(p, " "+lat)
    if isME:
        text = text.replace("ME", "")
    text = text.replace(",", ", ")
    text = text.replace("->", ", > ,")
    text = removeNeutrinoFlavours(text)
    for p, lat in sorted(recognisedParticles.items(), key=lambda x: len(x[0]), reverse=True):
        lat = lat.replace("tau", "TAU").replace("mu", "MU").replace(
            "nu", "NU").replace("gamma", "GAMMA")
        text = text.replace(p, " "+lat)
    text = text.replace("TAU", "tau").replace(
        "MU", "mu").replace("NU", "nu").replace("GAMMA", "gamma")
    while "  " in text:
        text = text.replace("  ", " ").strip()
    tokens = []
    for token in text.split(","):
        token=token.strip()
        if "BAR" in token:
            tokens += ["\\bar{%s}" % token.replace("BAR", "")]
        elif "~" in token:
            tokens += ["\\bar{%s}" % token.replace("~", "")]
        else:
            tokens += [token]
    text = ",".join(tokens)
    text = text.replace(">", " \\rightarrow ")
    if not splitIncomingPartons:
        text = mergeIncomingPartons(text)
    if not splitLightQuarks:
        text = groupLightQuarks(text, splitBQuarks)
    if not splitAntiParticles:
        text = ignoreAntiParticles(text)
    if mergeEWBosons:
        text = mergeEWBosons(text)
    if not splitLeptons:
        text = mergeLeptons(text)
    return text

def removeNeutrinoFlavours(text):
    tokens = [x if not "nu" in x else "nu" for x in text.split(",")]
    text = ", ".join(tokens)
    return text

def mergeIncomingPartons(text):
    sep = " \\rightarrow "
    partons=  text.partition(sep)[0]
    products= text.partition(sep)[-1]
    text = text.replace("bar", "BAR")
    partons = groupLightQuarks(ignoreAntiParticles(partons))
    partons = partons.replace("q", "p").replace("g", "p")
    text = text.replace("BAR", "bar")
    text = partons+sep+products
    return text

def mergeEWBosons(text, mergeHiggs=True):
    if mergeHiggs:
        text = text.replace("H", "V")
    text = text.replace("Z0", "V")
    text = text.replace("W+", "V")
    text = text.replace("W-", "V")
    text = text.replace("Z", "V")
    text = text.replace("W", "V")
    return text

def mergeLeptons(text):
    text = text.replace("e", "l")
    text = text.replace("\\mu", "l")
    text = text.replace("\\tau", "l")
    return text


def ignoreAntiParticles(text):
    text = text.replace("~", "")

    # remove charge
    tokens = []
    for token in text.split(","):
        is_rec_particle = False
        for key, value in recognisedParticles.items():
            if key in token:
                is_rec_particle = True
                break
        
        if is_rec_particle:
            token = token.replace("+", "")
            token = token.replace("-", "")
        else:
            token = token.replace("+", "PLUSORMINUS")
            token = token.replace("-", "PLUSORMINUS")
            token = token.replace("PLUSORMINUS", "_ch")
        tokens.append(token.strip())
    text = ",".join(tokens)

    # remove \bar{}
    tokens = []
    for token in text.split(","):
        if "bar" in token or "BAR" in token:
            token = token.split("{")[-1].split("}")[0]
        tokens += [token.strip()]
    res=", ".join(tokens)
    return res


def groupLightQuarks(text, splitBquarks=False, splitTquarks=True):
    tokens = []
    for t in text.split(","):
        t=t.strip()
        
        qStrings = [
                    "u", "s", "d", "c" ,"b", "t", 
                     "ubar", "dbar", "cbar", "sbar", "bbar", "tbar",
                     "\\bar{u}", "\\bar{d}", "\\bar{c}", "\\bar{s}", "\\bar{b}", "\\bar{t}" 
                   ] 
        if t in  qStrings:

            t = t.replace("ubar", "qbar")
            t = t.replace("dbar", "qbar")
            t = t.replace("sbar", "qbar")
            t = t.replace("cbar", "qbar")
            t = t.replace("u", "q")
            t = t.replace("s", "q")
            t = t.replace("d", "q")
            t = t.replace("c", "q")
            if not (splitBquarks):
                t = t.replace("bar", "BAR").replace(
                    "b", "q").replace("BAR", "bar")
                t = t.replace("bbar", "qbar")
            if not (splitTquarks):
                t = t.replace("t", "q")
                t = t.replace("tbar", "qbar")
        tokens += [t]
    text = ", ".join(tokens)
    return text




def printBRs(ParticleDict, tol=0.01, drawToDir=False):
    for proc, decays in ParticleDict.items():
        cfg.contur_log.info("Decays of {}".format(proc))
        countMinorDecays = 0
        labels=[]
        sizes=[]
        try:
            cfg.contur_log.info("mass = {} GeV, width = {} GeV".format(decays["mass"],decays["width"]))
        except KeyError:
            cfg.contur_log.info("SM particle")
            
        for decay, br in sorted(decays.items(), key=lambda x: x[1], reverse=True):
            if decay == "mass" or decay == "width":
                continue
            if br > tol:
                cfg.contur_log.info("--> %s = %.2f%%" % (decay, br*100))
                labels+=[proc+ "->"+ decay]
                sizes+=[br*100]
            else:
                countMinorDecays += 1
        
        if drawToDir != "" :
          os.system("mkdir -p %s" %drawToDir)
          fig1, ax1 = plt.subplots(figsize=(10, 10))
          ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                  shadow=True, startangle=90)
          valuesText = valsText.split(",")
          ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
          cc=0
          for vt in valsText:
            cc+=0.1
          plt.title(valsText.replace(", ","\n"))
          plt.savefig("%s/%s_BR_%s.pdf"%(drawToDir,number,proc))
          plt.savefig("%s/%s_BR_%s.png"%(drawToDir,number,proc))
          plt.close(fig1)
        if countMinorDecays:
            cfg.contur_log.info("(skipped %d decays with BR<%.1f%%)" %
                  (countMinorDecays, tol*100))


def validateLine(txt):
    tokens = txt.split()
    if not len(tokens) == 4:
        return False
    if remove_brackets(tokens[1]) is None or remove_brackets(tokens[2]) is None or remove_brackets(tokens[3]) is None:
        return False
    return True


def apply_bfs(text, brs, procDict, validationDict, totBR=1, indent=""):
    '''
    if requested, recursively apply branching fractions for SM and BSM particles
    until only stable particles remain in the reaction
    '''

    if "width" in text or "mass" in text:
        return  validationDict
    
    if len(indent) > 100:
        if not text in procDict.keys():
            procDict[text] = 0
        procDict[text] += 100*totBR
        if not text in validationDict.keys():
            validationDict[text] = 0
        validationDict[text] += 100*totBR
        return validationDict

    hasUnstableParticles = False
    baseText = text.replace("\\rightarrow", "-->")
    tokenCounter = -1
    tokenBreak = False
    for token in baseText.split(","):
        token=token.strip()
        tokenCounter += 1
        if tokenBreak:
            break
        if token in brs.keys():
            hasUnstableParticles = True
            for decay, br in brs[token].items():
                if not ("width"==decay or "mass"==decay):
                    newTextTokens = baseText.split()
                    newTextTokens[tokenCounter] = decay
                    newText = ", ".join(newTextTokens).strip()
                    newTokens = []
                    for token in newText.split(" --> "):
                        newTokens += [", ".join(sorted(token.split(","))).strip()]
                    text = " --> ".join(newTokens)
                    apply_bfs(text, brs, procDict, validationDict, totBR*br, indent+"+")
            tokenBreak = True

    if hasUnstableParticles == False:
        cfg.contur_log.debug("===> text ''{}'' is stable! BR= {:.4f}".format(text, 100*totBR))
        if not text in procDict.keys():
            procDict[text] = 0
        procDict[text] += 100*totBR
        if not text in validationDict.keys():
            validationDict[text] = 0
        validationDict[text] += 100*totBR


    return validationDict       

def build_herwig_ME_map(lines,particles):
    ''' 
    Build a map between the incomprehensible garble of the
    herwig process names to something Human-readable eg: MEdubar2Y1W- d,ubar->Y1,W
    populated from the .out files "Detailed breakdown" lines
    '''
    herwigMEChainMap = {}

    for l in lines:
        l = l.strip()
        if not "(PPExtractor)" in l:
            continue
        # example (PPExtractor) ubar u (MEuubar2XmXm u,ubar->Xm,Xm)
        # we want the part in the second brackets
        tokenOfInterest=l.split("(")[-1].split(")")[0]
        for particleName in particles: 
            if "2" in particleName:
                tokenOfInterest=tokenOfInterest.replace(particleName, particleName.replace("2","TWO"))
        key=tokenOfInterest.split(" ")[0]
        value=tokenOfInterest.split(" ")[-1]
        isSChannel = False
        if key.count("2") == 2 : isSChannel = True
        if isSChannel:
            mediator = key.split("2")[1]
            value=value.replace("->","->%s->"%mediator)
        key=key.replace("TWO","2")
        value=value.replace("TWO","2")
        if key in herwigMEChainMap.keys():
            assert(herwigMEChainMap[key]==value)
        herwigMEChainMap[key]=value

    return herwigMEChainMap

def get_herwig_cross_sections(lines, herwigMEChainMap, particle_props,
                              splitIncomingPartons=False, splitLightQuarks=False, splitAntiParticles=False,
                              mergeEWBosons=False, splitLeptons=False, splitBQuarks=False, ws=False,
                              foldBRs=False,tol=0.0,drawToDir=""):

    procDict = {}
    totalXS = -999.
    runningTotXS = 0.


    # extract raw cross-sections for processes which contribute at this point
    for l in lines:
        l = l.strip()
        if "PPExtractor" in l:
            continue
        if "Total (from generated events)" in l:
            l = l.replace("Total (from generated events)", "")
            totalXS = remove_brackets(l.split()[3])
            if not ws: 
                try:
                    cfg.contur_log.info("totalXS {:.2f} fb".format(totalXS *1e6))
                except:
                    print("totalXS {:.2f} fb".format(totalXS *1e6))
        tokens = l.split()
        if validateLine(l):
            procName = tokens[0]
            thisXS = remove_brackets(tokens[3])
            if thisXS == 0:
                continue
            if ":" in procName:
                continue
            runningTotXS += thisXS
            procName = herwigMEChainMap[procName]
            procName = make_latex_safe(procName, splitIncomingPartons=splitIncomingPartons,
                                       splitLightQuarks=splitLightQuarks, splitAntiParticles=splitAntiParticles,
                                       mergeEWBosons=mergeEWBosons, splitLeptons=splitLeptons,
                                       splitBQuarks=splitBQuarks, isME=1)

            if foldBRs:

                validationDict = {}
                apply_bfs(procName, particle_props, procDict, validationDict, thisXS/totalXS)
                sumBR = 0
                for k, v in sorted(validationDict.items(), key=lambda x: x[0]):
                    sumBR += v*(totalXS/thisXS)
                assert(abs(sumBR-100) < 0.1)

            else:
                if not procName in procDict.keys():
                    procDict[procName] = 0
                procDict[procName] += 100*thisXS/totalXS

    return totalXS, procDict
