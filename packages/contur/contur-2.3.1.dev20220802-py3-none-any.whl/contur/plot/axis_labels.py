""" 
Define some default axis labels

"""

def get_axis_labels():

    axisLabels = {}

    
    # VLQ stuff
    #axisLabels["xibpw"] = "$\\mathrm{BR}(B \\rightarrow~tW)$"
    #axisLabels["xibph"] = "$\\mathrm{BR}(B \\rightarrow~bH)$"
    axisLabels["xibpw"] = "$\\mathrm{BR}(Q \\rightarrow~qW)$"
    axisLabels["xibph"] = "$\\mathrm{BR}(Q \\rightarrow~qH)$"
    axisLabels["xibpz"] = "$\\mathrm{BR}(B \\rightarrow~bZ)$"
    axisLabels["xitpw"] = "$\\mathrm{BR}(T \\rightarrow~bW)$"
    axisLabels["xitph"] = "$\\mathrm{BR}(T \\rightarrow~tH)$"
    axisLabels["xitpz"] = "$\\mathrm{BR}(T \\rightarrow~tZ)$"
    axisLabels["kappa"] = "$\\kappa$"
    axisLabels["KT"] = "$\\kappa$"
    axisLabels["mtp"] = "$M_{T^\\prime}$ (GeV)"
    #axisLabels["mtp"]   = "$M_Q$ (GeV)"
    axisLabels["mbp"] = "$M_{B^\\prime}$ (GeV)"
    axisLabels["mx"] = "$M_Q$ (GeV)"
    
    # DM
    axisLabels["mXd"] = "$M_\\mathrm{DM}$ (GeV)"
    axisLabels["mXm"] = "$M_\\mathrm{DM}$ (GeV)"
    axisLabels["gVq"] = "$g_q$"
    axisLabels["gVl"] = "$g_l$"
    axisLabels["gVXd"] = "$g_{DM}$"
    
    # Zprime
    axisLabels["mY1"] = "$M_{Z^\\prime}$ (GeV)"
    axisLabels["mzp"] = "$M_{Z^\\prime}$ (GeV)"
    
    # top colour
    axisLabels["mZp"] = "$M_{Z^\\prime}$ (GeV)"
    axisLabels["cotH"] = "$\\cot\\theta_\\mathrm{H}$"
    axisLabels["GoM"] = "$\\Gamma_{Z^\\prime}/M_{Z^\\prime}$"
    
    # B-L
    axisLabels["g1p"] = "$g_1^{\\prime}$"
    axisLabels["sa"] = "$\\sin\\alpha$"
    #axisLabels["mh2"] = "$M_{h_2}$ (GeV)"
    
    # TFHM
    axisLabels["tsb"] = "$\\theta_{sb}$"
    axisLabels["gzpmzp"] = "$g_X \\times \\textrm{TeV}/  M_{Z^\\prime}$"
    
    # LQ
    axisLabels["mlq"] = "$M_{LQ}$ (GeV)"
    
    # Heavy Neutrinos
    axisLabels["VeN1"] = "$V_{e_\\nu}$"
    axisLabels["MN1"] = "$M_{\\nu_H}$ (GeV)"
    
    # 2HDM be careful, beta definitions may change between Ken Lane's and everyone else's conventions.
    axisLabels["mh3"] = "$M_A$ (GeV)"
    axisLabels["mh2"] = "$M_{H}$ (GeV)"
    axisLabels["mhc"] = "$M_{H^\\pm}$ (GeV)"
    axisLabels["tanbeta"] = "$\\tan\\beta$"
    axisLabels["sinbma"] = "$\\sin(\\beta-\\alpha)$"
    axisLabels["cosbma"] = "$\\cos(\\beta-\\alpha)$"
    # Kens Gildener-Weinberg thing
    #axisLabels["mh3"] = "$M_A = M_{H^\pm}$ (GeV)"
    
    # 2HDM+a
    axisLabels["mh4"] = "$M_a$ (GeV)"
    axisLabels["sinp"] = "$\\sin\\theta$"
    
    # ALPS
    axisLabels["malp"] = "$M_{ALP}$ (GeV)"
    axisLabels["caa"] = "$c_{\\gamma\\gamma}/\\Lambda$ (TeV$^{-1}$)"
    axisLabels["cah"] = "$c_{ah}/\\Lambda$ (TeV$^{-1}$)"
    axisLabels["gpl"] = "$c_{ee}/\\Lambda$ (TeV$^{-1}$)"
    
    # general light scalar (mphi see below)
    axisLabels["fscale"] = "$\\Lambda$ (GeV)"
    
    # DE
    axisLabels["c1"] = "$C_1$"
    axisLabels["c2"] = "$C_2$"
    axisLabels["mphi"] = "$M_\\phi$ (GeV)"
    axisLabels["mscale"] = "$M_\\mathrm{SCALE}$ (GeV)"
    
    # neutrino EFT
    axisLabels["mn1"] = "$m_N$ (GeV)"
    axisLabels["lambda"] = "$\\Lambda$ (GeV)"
    axisLabels["clnh"] = "$\\alpha_{LNH}$"
    axisLabels["cnnh"] = "$\\alpha_{NNH}$"
    axisLabels["cna"] = "$\\alpha_{NA}$"
    
    # SUSY/SLHA
    axisLabels["1000022"] = "$M(\\tilde{\\chi}_1^0)$ (GeV)"
    axisLabels["1000023"] = "$M(\\tilde{\\chi}_2^0)$ (GeV)"
    axisLabels["1000024"] = "$M(\\tilde{\\chi}_1^+)$ (GeV)"
    axisLabels["1000025"] = "$M(\\tilde{\\chi}_3^0)$ (GeV)"
    axisLabels["1000035"] = "$M(\\tilde{\\chi}_4^0)$ (GeV)"
    
    # Dark Mesons
    axisLabels["PionMass"] = "$m_{\\pi_D}$ (GeV)"
    axisLabels["FermionEta"] = "$\\eta$"
    
    return axisLabels
            
