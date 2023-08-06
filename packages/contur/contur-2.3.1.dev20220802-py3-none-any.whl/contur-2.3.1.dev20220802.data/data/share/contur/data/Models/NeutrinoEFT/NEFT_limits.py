# 
# Limit file for NeutrinoEFT
# Should all return 1 if excluded, 0 otherwise.
# Need to have saved the values when running contur, e.g.
# contur -xc -w "Parent: N1" -bf "H->N1"  -g myscan00

# in GeV/s
hbar = 6.58e-25

def HBR(paramDict):  
    """ don't let H->N1 be bigger than the SM Higgs width, ie BF < 0.5
    ATLAS limit on invisible Higgs decay BF is 0.24. 
    return 1 if  excluded, 0 otherwise """
    import numpy as np

    hbr=float(paramDict["H->N1"])

    if hbr > 0.5: 
        return 1.0
    else:
        return 0.0

def Nlife(paramDict):  
    """ return 1 if  excluded, 0 otherwise
        Reject if the heavy neutrino decays none-prompt but in the detector volume """
    import numpy as np

    nwid=float(paramDict["Parent: N1"])
    # in picoseconds
    nlifeps = 1e12 * hbar / nwid

    if nlifeps < 10: 
        return 0.0

    if nlifeps > 3000:
        return 0.0

    return 1.0
