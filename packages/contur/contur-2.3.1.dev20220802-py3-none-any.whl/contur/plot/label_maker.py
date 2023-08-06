"""
This file is to allow some closer interaction with the labels 
put on plots, this is just to keep the conturPlot methods
cleaner until a good UI for placing labels is dreamt up.
In the meantime, if you want to label curves on plots,
you will have to write methods here and modify the addLimits
function in contur_plot.py to use them.

pass the axes instance you want to dress with a label to a function to do that

#TODO Look at an optional second legend

"""

# import the declared color wheel
# NB: limits are stored in alphabetical order, so whichever colour shows up can be matched by considering that order
from contur.plot import color_config
# convert the colorwheel into a list for this backwards compatibility
limitColors = color_config.CONTURCOLORS.by_key()["color"]

# B-L
# -----------------------
# EXAMPLE BL CASE D AND E


def BLCaseDE(axes):
    axes.text(540, 0.63, "Vacuum stability",
              color=limitColors[0], rotation="-40", size=9)
    axes.text(500, 0.28, "W Mass",
              color=limitColors[2], rotation="-14", size=9)


def BLCaseA(axes):
    axes.text(3100, 0.3, "ATLAS", color=limitColors[1], rotation="75", size=8)
    axes.text(13, 0.1, r"$\nu$ Scattering",
              color=limitColors[3], rotation="40", size=8)
    axes.text(5, 0.00035, "LHCb", color=limitColors[4], size=8)


def BLCaseB(axes):
    axes.text(1.1, 0.4, "Perturbativity",
              color=limitColors[0], rotation="40", size=8)
    axes.text(13, 0.1, r"$\nu$ Scattering",
              color=limitColors[3], rotation="40", size=8)
    axes.text(10.3, 0.019, "W Mass and",
              color=limitColors[2], rotation="40", size=8)
    axes.text(100, 0.25, "Perturbativity",
              color=limitColors[0], rotation="40", size=8)


def BLCaseC(axes):
    # Case C
    axes.text(3, 0.2, "Perturbativity",
              color=limitColors[0], rotation="40", size=8)
    axes.text(13, 0.1, r"$\nu$ Scattering",
              color=limitColors[3], rotation="40", size=8)


def DM_LF(axes):
    axes.text(300, 1200, "Perturbative Unitarity",
              color=limitColors[2], rotation="70", size=8)


# TODO others leftover from plot macro copied here, put in same format and add corresponding case line to macro
    # Case D & E
    #self.axes[0].text(540,0.63,"Vacuum stability",color=limitColors[3],rotation="-40",size=9)
    #self.axes[0].text(500,0.28,"W Mass",color=limitColors[0],rotation="-14",size=9)

    # Case B
    # self.axes[0].text(1.1,0.4,"Perturbativity",color=limitColors[1],rotation="40",size=8)
    #self.axes[0].text(13, 0.1, r"$\nu$ Scattering", color=limitColors[3], rotation="40", size=8)
    #self.axes[0].text(10.3,0.019,"W Mass and",color=limitColors[2],rotation="40",size=8)
    # self.axes[0].text(100,0.25,"Perturbativity",color=limitColors[1],rotation="40",size=8)
    # # Case A
    # self.axes[0].text(3100,0.3,"ATLAS",color=limitColors[0],rotation="75",size=8)
    #self.axes[0].text(13,0.1,r"$\nu$ Scattering",color=limitColors[3],rotation="40",size=8)
    # self.axes[0].text(5,0.00035,"LHCb",color=limitColors[4],size=8)

    # DMsimp
    # -----------------------
