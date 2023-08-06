# contur-plot contur.map mzp gzpmzp -yl -ef Width_cut

# Draw a limit line based on an auxilliary parameter stored from the generator logs.
# (In this example, cut on the width < 30% of mass for the Z-prime)
# Should all return 1 if excluded, 0 otherwise.

def width_cut(paramDict):
    import numpy as np
    """ return 1 if width > 30% of mass for the Z-prime,  0 otherwise """

    #TODO typing should be handled in dict upstream
    width=float(paramDict["AUX:Zp"])
    mzp=float(paramDict["mzp"])
    gzp=float(paramDict["gzp"])
    gzpmzp=float(paramDict["gzpmzp"])

    #print("Width={:.2e}, mzp={:.2e}, gzp={:.2e}, 1000*GZP/MZP={:.2e}, Width/mzp={:.2e}".format(width, mzp, gzp, gzpmzp, width/mzp))
     #if gzp < 1.0:
      #   return 0


    if width/mzp < 1.0/3.0:
        ret=0
    else:
        ret=1
    return ret, False, "black"

#def preferred_gzmz(paramDict):
#    """ return 0 if in preferred zone, 1 otherwise """
#    gzpmzp=float(paramDict["gzpmzp"])
#    if gzpmzp>0.05 and gzpmzp<0.62:
#        ret=0
#    else:
#        ret=1
#
#    return ret, False, "black"
