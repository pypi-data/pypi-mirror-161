

def ew_limits(paramDict):

    from math import pi, log, sqrt
    import numpy as np
    from   scipy                   import ndimage

    def f(m1, m2, m3):
        if m1==m3:
            return 0
        numerator = m1**4*(m2**2-m3**2)
        denominator = m3**2*(m1**2-m2**2)*(m1**2-m3**2)
        a = float(numerator)/float(denominator)
        b = float(m1)**2 / float(m3)**2
        return a * log(b)

        return numerator / denominator * log(m1**2 / m3**2)

    def max_sin_theta(ma, mA, mH):
        max_delta_rho = 2.4*pow(10,-3)
        min_delta_rho = -1.2*pow(10,-3)
        mHc = mA
        v = 246.0
        if mA==mH:
            return 1.0
        denominator = 1/(4*pi)**2 * mHc**2/v**2
        f_term = 1+f(mH, ma, mHc)+f(ma, mH, mHc)
        if f_term<0:
            sin_squared = min_delta_rho / (denominator * f_term) # bound on max_delta_rho also fulfilled
        else:
            sin_squared = max_delta_rho / (denominator * f_term) # bound on min_delta_rho also fulfilled
        return sqrt(sin_squared)

    sinTh=0.35
    ma=100.0

    pts=[]
    vals=[]

    # define axes
    mH_vals = list(range(150, 2150, 11))
    mA_vals = list(range(150, 2150, 11))
    if 2150 not in mH_vals:
        mH_vals.append(2150)
    if 2150 not in mA_vals:
        mA_vals.append(2150)

    # get constraints
    for i, mH in enumerate(mH_vals):
        for j, mA in enumerate(mA_vals):
            temp=dict.fromkeys(paramDict)
            temp["mh3"]=mA
            temp["mhc"]=mH
            pts.append(temp)
            if sinTh > max_sin_theta(ma, mA, mH):
                vals.append(1)
            else:
                vals.append(-1)

    return pts, vals

