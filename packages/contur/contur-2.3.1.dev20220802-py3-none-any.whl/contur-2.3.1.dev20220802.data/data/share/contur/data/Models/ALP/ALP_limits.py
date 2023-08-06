# contur-plot merged.map mY1 mXm -o conturPlot -sp -y \$M\_\{DM\}\$ -x \$M\_\{Z\'\}\$~\[GeV\] -t DM_limits

# Theory limits for the original contur DM model
# Should all return 1 if excluded, 0 otherwise.


def hBSMBR(paramDict):  
    """ return 1 if  excluded, 0 otherwise """
#  This is from  eq.(61) of 1708.00443, higgs to BSM branching ratio

    import numpy as np


    malp=float(paramDict["malp"])
    gpl=float(paramDict["gpl"])
    gpu=float(paramDict["gpu"])
    gpd=float(paramDict["gpd"])
    cgg=float(paramDict["cgg"])
    cza=float(paramDict["cza"])
    cah=float(paramDict["cah"])
    czh5=float(paramDict["czh5"])
#    cah2=float(paramDict["cah2"])

    if cah > 1.34 and malp < 62:
        return 1.0
    else:
        return 0.0


