"""
Defines the colour mapping to analysis pools.

"""

# a colour cycler for any unknown pools
from cycler import cycler
CONTURCOLORS = cycler(color=["black", "darkviolet", "darkcyan", "sienna", "firebrick", "navy"])

POOLCOLORS = {
    # ==================================
    # ATLAS
    # ==================================
    # mixed
    "ATLAS_3L": {
        "color" : "crimson",
    },
    "ATLAS_4L": {
        "color" : "magenta",
    },
    "ATLAS_GAMMA": {
        "color" : "yellow",
    },
    "ATLAS_GAMMA_MET": {
        "color" : "darkgoldenrod",
    },
    "ATLAS_JETS": {
        "color" : "silver",
    },

    "ATLAS_LLJET": {
        "color" : "orange",
    },
    "ATLAS_EEJET": {
        "color" : "orangered",
    },
    "ATLAS_MMJET": {
        "color" : "darkorange",
    },

    "ATLAS_LMETJET": {
        "color" : "blue",
    },
    "ATLAS_EMETJET": {
        "color" : "cadetblue",
    },
    "ATLAS_MMETJET": {
        "color" : "navy",
    },

    "ATLAS_METJET": {
        "color" : "green",
    },
    "ATLAS_TTHAD": {
        "color" : "snow",
        "latexName" : r"ATLAS Hadronic $t\bar{t}$"
    },
    "ATLAS_L1L2MET": {
        "color" : "cornflowerblue",
        "latexName" : r"ATLAS $\ell_1\ell_2$+\met{}",
    },
    "ATLAS_L1L2METJET": {
        "color" : "turquoise",
        "latexName" : r"ATLAS $\ell_1\ell_2$+\met{}+jet",
    },
    "ATLAS_LLMET": {
        "pools" : ["ATLAS_7_LLMET"],        
        "color" : "greenyellow",
    },
    "ATLAS_LL_GAMMA": {
        "pools" : ["ATLAS_7_EE_GAMMA", "ATLAS_7_MM_GAMMA", "ATLAS_8_LL_GAMMA", "ATLAS_13_LL_GAMMA"],
        "color" : "mediumseagreen",
    },

    "ATLAS_HMDY": {
        "pools" : ["ATLAS_7_HMDY","ATLAS_8_HMDY_EL","ATLAS_8_HMDY_MU","ATLAS_13_HMDY"],
        "color" : "darkolivegreen",
        "latexName" : r"ATLAS high-mass Drell-Yan $\ell\ell$"
    },
    "ATLAS_LMDY": {
        "pools" : ["ATLAS_7_LMDY"],
        "color" : "tomato",
        "latexName" : r"ATLAS low-mass Drell-Yan $\ell\ell$"
    },
    "ATLAS_7_LMET_GAMMA": {
        "pools" : ["ATLAS_7_EMET_GAMMA", "ATLAS_7_MMET_GAMMA"],
        "color" : "lightgreen",
    },
    "ATLAS_8_MM_GAMMA": {
        "pools" : ["ATLAS_8_MM_GAMMA"],
        "color" : "indianred",
    },


    # ==================================
    # CMS
    # ==================================
    # mixed
    "CMS_3L": {
        "color" : "saddlebrown",
    },
    "CMS_4L": {
        "color" : "hotpink",
    },
    "CMS_GAMMA": {
        "color" : "gold",
    },
    "CMS_GAMMA_MET": {
        "color" : "goldenrod",
    },
    "CMS_JETS": {
        "color" : "dimgrey",
    },

    "CMS_LLJET": {
        "color" : "salmon",
    },
    "CMS_EEJET": {
        "color" : "lightsalmon",
    },
    "CMS_MMJET": {
        "color" : "darksalmon",
    },

    "CMS_LMETJET": {
        "color" : "powderblue",
    },
    "CMS_EMETJET": {
        "color" : "deepskyblue",
    },
    "CMS_MMETJET": {
        "color" : "steelblue",
    },

    "CMS_METJET": {
        "color" : "darkgreen",
    },
    "CMS_TTHAD": {
        "color" : "wheat",
        "latexName" : r"CMS Hadronic $t\bar{t}$"
    },
    "CMS_L1L2MET": {
        "color" : "royalblue",
    },

    "CMS_HMDY": {
        "color" : "seagreen",
        "latexName" : r"CMS high-mass Drell-Yan $\ell\ell$"
    },

    "LHCB_LLJET": {
        "pools" : ["LHCB_7_EEJET", "LHCB_7_MMJET"],
        "color" : "indigo",
    },
    "LHCB_LJET": {
        "pools" : ["LHCB_8_LJET","LHCB_8_MJET"],
        "color" : "darkorchid",
    },
    "LHCB_L1L2B": {
        "pools" : ["LHCB_13_L1L2B"],
        "color" : "thistle",
    },

    # ===============================================
    # other: used when there isn't room in the legend 
    # ===============================================
    "other": {
        "pools": ["other"],
        "color" : "whitesmoke",
    },
}


# Create energy-specific internal pool groupings for colour tinting
for poolGroupName, poolGroup in POOLCOLORS.items():
    if "pools" in poolGroup:
        continue
    split = poolGroupName.split("_")
    poolGroup["pools"] = ["_".join([split[0], x]+split[1:])
                          for x in ["7", "8", "13"]]

# Create LaTeX pool names
for poolGroupName, poolGroup in POOLCOLORS.items():
    if "latexName" in poolGroup:
        continue
    split = poolGroupName.split("_")
    
    finalState = " ".join([x for x in split[1:] if not x.isdigit()])
    finalState = finalState.replace("JETS", "jets")
    finalState = finalState.replace("JET", "+jet")
    finalState = finalState.replace("MET", r"\met{}+")
    finalState = finalState.replace("GAMMA", r"$\gamma$+")
    finalState = finalState.replace("L", r"$\ell$+")
    finalState = finalState.replace("E", "$e$+")
    finalState = finalState.replace("M", r"$\mu$+")
    finalState = finalState.replace("W", "$W$+")
    finalState = finalState.replace(" ", "")
    finalState = finalState.replace("++", "+")
    finalState = finalState.replace("$+$", "")
    finalState = finalState.strip("+")

    poolGroup["latexName"] = split[0]+" "+finalState
      
