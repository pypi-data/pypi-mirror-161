
#custom function to load a datagrid, any file reading format will do, here we use pandas to directly read a csv contraint file
import pandas as pd
import numpy as np

scan = "masses"

if scan == "masses":
    df1=pd.read_csv('Tri_Higgs_CP_even_masses.gp', sep=' ',skipinitialspace=True,header=None, skiprows=13, nrows=211)
    df2=pd.read_csv('Tri_Higgs_CP_even_masses.gp', sep=' ',skipinitialspace=True,header=None, skiprows=225, nrows=211)
else:
    exit

def gw_masses(paramDict):
    """add a new data grid to evaluate, return the list of points by making a new paramDict and giving a value
    plot assumes the values are around 0.0, with numbers larger than 0 being excluded. Translate data table values accordingly
    """
    pts=[]
    vals=[]


    masses = np.linspace(100,550,5000)

    icount = 0
    for i in df1.to_numpy():
         #print i
        #mh2 = df2.get_value(icount,1)
        mh2 = df2.at[icount,1]
        mhp = i[1]
         #print mhp,mh2
        masses = np.linspace(mhp-1,mh2+1,100)
        for m in masses:

            temp=dict.fromkeys(paramDict)
            # the same paramDict structure is used as passed from the code, all we do is make a copy of this and fill each point with the info 
            # we need from the csv
            temp["mh3"]=i[0]                
            temp["mh2"]=m
            pts.append(temp)
            val = -1
             #print m, mhp, mh2
            if m > mhp-0.6 and m < mh2+0.6:
                val = 1
            vals.append(val)

        icount=icount+1

    #return the list of parameter space points, pts, and the corresponding transposed values, vals, and the plotting macro will do the rest
    return pts,vals

