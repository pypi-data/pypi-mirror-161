# contur-plot merged.map mzp g1p -x \$M\_\{z\'\}\$~\[GeV\] -y \$g\_\{1\}\'\$ -xl -yl -np -t BL3limits
# contur-plot merged.map mh2 sa -x \$M\_\{h\_2\}\$~\[GeV\] -y \$\\sin\\alpha\$ -np -t BL3limits

# Theory and previous experiment limits for B-L 3
# Should all return 1 if excluded, 0 otherwise.

# SM Hggs mass and vev
mh1 = 125.0
vev = 246.0
#
# ATLAS bound from high mass DY search
# ---------------------------------------------------------------------
def bl3ATLASlim(paramDict):
    import numpy as np
    """ return 1 if  excluded by ATLAS dipleton search, 0 otherwise """

    #TODO typing should be handled in dict upstream
    sa=float(paramDict["sa"])
    g1p=float(paramDict["g1p"])
    mh2=float(paramDict["mh2"])
    mnh=float(paramDict["mnh"])
    mzp=float(paramDict["mzp"])

    if sa != 0:
        # strictly this bound only applies if no higgs mixing.
        return 0

#log10 g'/g = k M + c;  M = (log10(g'/g)-c)/k
#0.1 = 2900 = -1
#1.0 = 5000 =  0
# so 5000k = -c,    -1 = 2900k + c = -2100k;    k = 1/2100, c = -5000/2100
#    sqrt(g'^2 + g^2) (SM) = 0.74
    k = 1.0/2100
    c = -50.0/21.0

    atllim = 0.0
    if mzp < (np.log10(g1p/.74)-c)/k and mzp > 150.:
        atllim = 1.0

    return atllim


# Borexino bound in x as function of y
def BorexinoLimit(paramDict):
    """ return 1 if excluded by Borexino neutrino-electron scattering cross section, 0 otherwise """

    #TODO typing should be handled in dict upstream
    sa=float(paramDict["sa"])
    g1p=float(paramDict["g1p"])
    mh2=float(paramDict["mh2"])
    mnh=float(paramDict["mnh"])
    mzp=float(paramDict["mzp"])

    borlim = 0.0
    #if mzp/g1p < 250.:
    #    borlim=1.0
    if g1p/mzp > 0.00065:
        borlim=1

    return borlim

# W mass bound from high mass DY search
# ---------------------------------------------------------------------
def bl3Wmasslim(paramDict):
    import numpy as np

    #TODO typing should be handled in dict upstream
    sa=float(paramDict["sa"])
    g1p=float(paramDict["g1p"])
    mh2=float(paramDict["mh2"])
    mnh=float(paramDict["mnh"])
    mzp=float(paramDict["mzp"])

    wmasslim = 0.0

    if mh2 < 140. or sa < 0.17:
        return wmasslim

    mh2val = [140,
              145,
              150,
              155,
              160,
              165,
              170,
              175,
              180,
              185,
              190,
              200,
              300,
              400,
              500,
              600,
              700,
              800,
              900,
              1000,
              1100,
              1200,
              1300,
              1400,
              1500,
              1600  ]

    samax = [1,
             0.94,
             0.84,
             0.77,
             0.71,
             0.67,
             0.63,
             0.6,
             0.57,
             0.55,
             0.53,
             0.49,
             0.34,
             0.28,
             0.26,
             0.24,
             0.22,
             0.21,
             0.20,
             0.20,
             0.19,
             0.19,
             0.18,
             0.18,
             0.18,
             0.17 ]

    sam = np.interp(mh2, mh2val, samax)
    if sa > sam:
        wmasslim = 1.0

    return wmasslim

# Bound from LHCb dark photon reinterpretation
# ---------------------------------------------------------------------
def LHCblim(paramDict):
    import numpy as np

    #TODO typing should be handled in dict upstream
    sa=float(paramDict["sa"])
    g1p=float(paramDict["g1p"])
    mh2=float(paramDict["mh2"])
    mnh=float(paramDict["mnh"])
    mzp=float(paramDict["mzp"])

    lhcblim = 0.0

    if not sa == 0.0:
        return lhcblim

    if mzp<2.1404e-01 or mzp>6.9861e+01:
        return lhcblim

    mzpval = [
        2.2387e-01 ,
        2.5119e-01 ,
        2.8184e-01 ,
        3.1623e-01 ,
        3.5481e-01 ,
        3.9811e-01 ,
        4.4668e-01 ,
        5.0119e-01 ,
        5.6234e-01 ,
        6.3096e-01 ,
        7.0795e-01 ,
        7.9433e-01 ,
        8.9125e-01 ,
        1.0000e+00 ,
        1.1220e+00 ,
        1.2589e+00 ,
        1.4125e+00 ,
        1.5849e+00 ,
        1.7783e+00 ,
        1.9953e+00 ,
        2.2387e+00 ,
        2.5119e+00 ,
        2.8184e+00 ,
        3.1623e+00 ,
        3.5481e+00 ,
        3.9811e+00 ,
        4.4668e+00 ,
        5.0119e+00 ,
        5.6234e+00 ,
        6.3096e+00 ,
        7.0795e+00 ,
        7.9433e+00 ,
        8.9125e+00 ,
        1.0000e+01 ,
        1.1220e+01 ,
        1.2589e+01 ,
        1.4125e+01 ,
        1.5849e+01 ,
        1.7783e+01 ,
        1.9953e+01 ,
        2.2387e+01 ,
        2.5119e+01 ,
        2.8184e+01 ,
        3.1623e+01 ,
        3.5481e+01 ,
        3.9811e+01 ,
        4.4668e+01 ,
        5.0119e+01 ,
        5.6234e+01 ,
        6.3096e+01
        ]

    g1pmax = [
        7.9576e-04 ,
        4.9910e-04 ,
        5.8049e-04 ,
        6.7650e-04 ,
        7.9260e-04 ,
        7.8817e-04 ,
        8.9280e-04 ,
        1.1048e-03 ,
        1.0602e-03 ,
        5.0980e-04 ,
        4.1689e-04 ,
        3.9686e-04 ,
        6.2051e-04 ,
        1.0000e+05 ,
        8.6097e-04 ,
        9.7618e-04 ,
        9.8909e-04 ,
        7.8800e-04 ,
        6.1891e-04 ,
        8.9025e-04 ,
        9.9600e-04 ,
        1.1867e-03 ,
        1.0000e+05 ,
        9.6133e-04 ,
        8.7600e-04 ,
        8.2915e-04 ,
        1.3209e-03 ,
        1.2482e-03 ,
        1.7601e-03 ,
        1.0789e-03 ,
        1.4354e-03 ,
        1.5287e-03 ,
        1.1464e-03 ,
        1.8011e-03 ,
        1.3522e-03 ,
        6.4257e-04 ,
        1.0073e-03 ,
        1.5675e-03 ,
        8.6887e-04 ,
        9.0891e-04 ,
        1.1131e-03 ,
        9.1943e-04 ,
        2.2470e-03 ,
        1.6569e-03 ,
        2.5145e-03 ,
        1.8485e-03 ,
        2.4859e-03 ,
        1.6217e-03 ,
        2.9113e-03 ,
        2.0039e-03
        ]


    g1pm = np.interp(mzp, mzpval, g1pmax)
    if g1p > g1pm:
        lhcblim = 1.0

    return lhcblim
