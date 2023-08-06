
#custom function to draw line for the flavour limits on kappa-mass scans

# command is:
# contur-plot contur.map mtp kappa -eg flavour.py


# This will define which generation we are using
#scan = "1gen"
scan = "2gen"

#
def flavour_limit(paramDict):
    """ return 1 if excluded by flavour constraints in Buchkremer et al arXiv:1305.4172, 0 otherwise """
    import numpy as np

    pts=[]
    vals=[]

    mass = np.linspace(500,2500,1000)

    if scan=="1gen":
        kap = np.linspace(0.005,0.15,200)
        lim = 0.07
    else:
        kap = np.linspace(0.05,0.4,200)
        lim = 0.2

    for k in kap:
        for m in mass:
            temp=dict.fromkeys(paramDict)
            temp["mtp"]=m
            temp["kappa"]=k
            pts.append(temp)
            exc = -1
            if k > lim:
                exc=1
            vals.append(exc)


    return pts, vals, False, "blue"
