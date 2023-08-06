# quick function to return the bound from neutrinoloess double beta decay
# 

def existingLimit1(paramDict):
    """ return 1 if  excluded by 0v2B decay search, 0 otherwise """
    VeN=float(paramDict["VeN1"])
    MN1=float(paramDict["MN1"])

    ndb=5.0e-08

    if MN1 > (VeN)**2/ndb:
        return 0 
    else:
        return 1
