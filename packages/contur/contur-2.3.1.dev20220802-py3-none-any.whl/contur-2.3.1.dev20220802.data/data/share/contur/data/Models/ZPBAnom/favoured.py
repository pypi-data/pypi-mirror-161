# Function used to draw the lines delineating the regions favoured by the fit in https://arxiv.org/abs/2110.13518
# 
# contur-plot contur.map mzp gzpmzp -yl -eg favoured



# Return +ve if favoured, -ve if not
#

def favoured(paramDict):
    import numpy as np
    """ return list of points and values (<0 excluded >0 ok)"""

    # set these to the x values as appropriate for the model you are plotting (see Table 2 of paper)
    # This is for B3-L2
    max_x=0.62
    min_x=0.05

    
    pts=[]
    vals=[]

    x = np.logspace(-2,1,1000)
    masses = np.linspace(20,6000,100)

    for gzpmzp in x:        
        for mzp in masses:
            temp=dict.fromkeys(paramDict)
            temp["mzp"]=mzp
            temp["gzpmzp"]=gzpmzp 
            pts.append(temp)             
            exc = -100
            if gzpmzp>min_x and gzpmzp<max_x:
                exc = 100
            vals.append(exc)
#            print(gzpmzp,mzp,exc)

    return pts, vals, False, "blue"
