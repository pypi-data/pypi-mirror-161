
#custom function to load a datagrid, any file reading format will do, here we use pandas to directly read a csv contraint file
import pandas as pd

# This will define which file we read and which mass.
scan = "1350","T"

if "T" in scan:
    df=pd.read_csv('HEPData-ins1685421-v1-Table_1.csv', sep=',',header=None, skiprows=457)
elif "B" in scan:
    df=pd.read_csv('HEPData-ins1685421-v1-Table_2.csv', sep=',',header=None, skiprows=457)
else:
    print(("Don't know what scan is: %s " % scan))
 
def mass_contours(paramDict):
    """add a new data grid to evaluate, return the list of points by making a new paramDict and giving a value
    plot assumes the values are around 0.0, with numbers larger than 0 being excluded. Translate data table values accordingly
    """
    pts=[]
    vals=[]

    for i in df.get_values():

        temp=dict.fromkeys(paramDict)
        # the same paramDict structure is used an passed from the code, all we do is make a copy of this 
        # and fill each point with the info we need from the csv
        mass = 0
        if i[2] != "-":
            mass = float(i[2])

        if "T" in scan:
            temp["xitpw"]=i[0]
            temp["xitph"]=i[1]
        else:
            temp["xibpw"]=i[0]
            temp["xibph"]=i[1]

        pts.append(temp)
        #then make a corresponding list to the paramPoints we've added to the pts vector, this time the "value" at each point
        #this value is transposed such that numbers larger than 0 are excluded and numbers less than zero are allowed regions
        if mass > float(scan[0]):
            vals.append(1.0)
        else:
            vals.append(-1.0)

    #return the list of parameter space points, pts, and the corresponding transposed values, vals, and the plotting macro will do the rest
    return pts,vals


