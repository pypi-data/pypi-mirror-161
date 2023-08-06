
#custom function to load a datagrid, any file reading format will do, here we use pandas to directly read a csv contraint file
import pandas as pd

scan = "CaseA"

if scan == "CaseA":
    df=pd.read_csv('RGE_A.csv', sep=',',header=None)
elif scan == "CaseB":
    df=pd.read_csv('RGE_B.csv', sep=',',header=None)
elif scan == "CaseC":
    df=pd.read_csv('RGE_C.csv', sep=',',header=None)
elif scan == "CaseD":
    df=pd.read_csv('RGE_D.csv', sep=',',header=None)
elif scan == "CaseE":
    df=pd.read_csv('RGE_E.csv', sep=',',header=None)

def bl3theory(paramDict):
    """add a new data grid to evaluate, return the list of points by making a new paramDict and giving a value
    plot assumes the values are around 0.0, with numbers larger than 0 being excluded. Translate data table values accordingly
    """
    pts=[]
    vals=[]

    for i in df.values:
        temp=dict.fromkeys(paramDict)
        #the same paramDict structure is used an passed from the code, all we do is make a copy of this and fill each point with the info we need from the csv
        if scan=="CaseD" or scan=="CaseE": 
            temp["mh2"]=i[0]
            temp["sa"]=i[1]
        else:
            temp["mzp"]=i[0]
            temp["g1p"]=i[1]
        pts.append(temp)
        #then make a corresponding list to the paramPoints we've added to the pts vector, this time the "value" at each point
        #this value is transposed such that numbers larger than 0 are excluded and numbers less than zero are allowed regions
        vals.append(-i[2]/2.0+1.0)
    #return the list of parameter space points, pts, and the corresponding transposed values, vals, and the plotting macro will do the rest

    return pts,vals


# Bound from LHCb dark photon reinterpretation
# ---------------------------------------------------------------------
def LHCblim(paramDict):
    import numpy as np

    if scan != "CaseA":
        return None, None

    pts=[]
    vals=[]
    
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

    couplings = np.logspace(-5.0,0.0,10*len(mzpval))

    for i in range(len(mzpval)):
        for g in couplings:
            temp=dict.fromkeys(paramDict)
            temp["mzp"]=mzpval[i]
            temp["g1p"]=g 
            pts.append(temp)
            vals.append(g-g1pmax[i])

    return pts, vals


# ATLAS bound from high mass DY search
# ---------------------------------------------------------------------
def bl3ATLASlim(paramDict):
    import numpy as np
    """ return list of points and values (<0 excluded >0 ok)"""

    if scan != "CaseA":
        return None, None

    pts=[]
    vals=[]

    couplings = np.logspace(-5.0,0.0,400)
    masses = np.logspace(0,4,400)

#log10 g'/g = k M + c;  M = (log10(g'/g)-c)/k 
#0.1 = 2900 = -1
#1.0 = 5000 =  0
# so 5000k = -c,    -1 = 2900k + c = -2100k;    k = 1/2100, c = -5000/2100
#    sqrt(g'^2 + g^2) (SM) = 0.74
    k = 1.0/2100
    c = -50.0/21.0

    for g1p in couplings:
        for mzp in masses:
            temp=dict.fromkeys(paramDict)
            temp["mzp"]=mzp
            temp["g1p"]=g1p 
            pts.append(temp)             
            exc = -1
            if mzp < (np.log10(g1p/.74)-c)/k and mzp > 150.:
                exc = 1
            vals.append(exc)

    return pts, vals


# Borexino bound in x as function of y
def NeutrinoScatteringLimit(paramDict):
    """ return 1 if excluded by Borexino neutrino-electron scattering cross section, 0 otherwise """
    import numpy as np

    if scan == "CaseD" or scan=="CaseE":
        return None, None

    pts=[]
    vals=[]

    couplings = np.logspace(-5,0,400)
    masses = np.logspace(0,4,400)

    for g1p in couplings:
        for mzp in masses:
            temp=dict.fromkeys(paramDict)
            temp["mzp"]=mzp
            temp["g1p"]=g1p 
            pts.append(temp)             
            exc = -1
            if g1p/mzp > 0.00065:
                exc=1
            vals.append(exc)


    return pts, vals


# W mass bound from high mass DY search
# ---------------------------------------------------------------------
def bl3Wmasslim(paramDict):
    import numpy as np

    if scan != "CaseD" and scan!="CaseE":
        return None, None

    pts=[]
    vals=[]

    sins   = np.linspace(0,1,400.)
    masses = np.linspace(0,1000,500.)

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


    for mh2 in masses:
        for sa in sins:
            temp=dict.fromkeys(paramDict)
            temp["mh2"]=mh2
            temp["sa"]=sa
            pts.append(temp)             
            exc = -1
            sam = np.interp(mh2, mh2val, samax)
            if sa > sam:
                exc=1
            vals.append(exc)

    return pts, vals

