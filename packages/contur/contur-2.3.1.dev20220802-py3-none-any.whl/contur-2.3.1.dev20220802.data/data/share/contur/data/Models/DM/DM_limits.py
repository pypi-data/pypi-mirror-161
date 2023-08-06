# contur-plot merged.map mY1 mXm -o conturPlot -sp -y \$M\_\{DM\}\$ -x \$M\_\{Z\'\}\$~\[GeV\] -t DM_limits

# Theory limits for the original contur DM model
# Should all return 1 if excluded, 0 otherwise.


def PertUni(paramDict):  
    """ return 1 if  excluded, 0 otherwise """
#  MZ'/g' > 6.9  so MZ' = g' * 6.9 TeV

    import numpy as np

    mY1=float(paramDict["mY1"])
    gYXm=float(paramDict["gYXm"])
    mXm=float(paramDict["mXm"])
    gYq=float(paramDict["gYq"])

    if mXm > np.sqrt(np.pi/2.0) * mY1/gYXm:
        return 1.0
    else:
        return 0.0


