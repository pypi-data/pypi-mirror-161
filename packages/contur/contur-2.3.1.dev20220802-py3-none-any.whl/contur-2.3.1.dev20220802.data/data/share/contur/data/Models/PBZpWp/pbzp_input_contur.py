#!/usr/bin/env python

from math import *
from sympy import *
import numpy as np


def matrixform(data):
    """
    Translates an Array or nested list, or anything that behaves
    similarly, into a structure of nested matrices.
    """
    try:
        A = data.tolist()
    except AttributeError:
        A = data
        
    try:
        M = Matrix(A)
        return M.applyfunc(matrixform)
    except TypeError:
        return A

# The default model is the SSM
model = 'SSM'

# Read the name of the model and the values of its parameters from "params.dat"
path_to_params = 'params.dat'
f = open(path_to_params)
for line in f:
	if 'model' in line:
        	model = str(line.split()[2])
## TFHMeg
if model in ['TFHMeg', 'tfhmeg', 'Tfhmeg']:
	f = open(path_to_params)
	for line in f:
		if 'tsb' in line:
			tsb = float(line.split()[2]) # angle theta_{sb} see Fig. 1 (right) in 1905.06073
		if 'mZp' in line:
        		MZp = float(line.split()[2])
## TC
elif model in ['TC', 'tc', 'Tc', 'tC']:
	f = open(path_to_params)
	for line in f:
		if 'cotH' in line:
			cotH = float(line.split()[2]) # see eq. 1 in 1112.4928v3 
		if 'mZp' in line:
        		MZp = float(line.split()[2])
## SSM
else:
	checkGZp = False
	f = open(path_to_params)
	for line in f:
		if 'GZp' in line:
			GZp = float(line.split()[2])
			checkGZp = True 
		if 'mZp' in line:
			MZp = float(line.split()[2])


# Third Family Hypercharge Model example
if model in ['TFHMeg', 'tfhmeg', 'Tfhmeg']:
	## Read alpha_em, mass of Z, and mass of W from "powheg.input_template"
	path_to_template = 'powheg.input_template'
	f = open(path_to_template)
	for line in f:
        	if 'zmass' in line:
                	MZ = float(line.split()[1])
        	if 'wmass' in line:
                	MW = float(line.split()[1])
        	if 'alphaem_inv' in line:
                	alphaem_inv = float(line.split()[1])

	## Input for the TFHMeg   
	s2w = 1 - MW**2/MZ**2
	sw = sqrt(s2w) 
	cw = sqrt(1 - s2w)
	aEM = 1/alphaem_inv
	ee = 2.*sqrt(np.pi)*sqrt(aEM) # in Recola src/class_particles.f90
	const = (sqrt(2.)*ee)/(cw*sw) # Recola factor for Z' couplings
	gF = (MZp/36000.)*(sqrt((24.*1.06)/sin(2*tsb)))  # Eq. 2.16 in 1904.10954, 36000 since MZ' in GeV
	ssb = sin(tsb) # sin of theta_sb
	csb = cos(tsb) # cos of theta_sb

	## VCKM matrix: Eq. 12.27 PDG Review 2018
	VCKM = Matrix([[0.97446,0.22452,0.00365],[0.22438,0.97359,0.04214],[0.00896,0.04133,0.999105]]) 

	## arxiv : 1809.01158 
	xi = Matrix([[0.,0.,0.],[0.,0.,0.],[0.,0.,1.]]) # Eq. 2.12
	VdR = Identity(3)
	VuR = Identity(3)
	VdL = Matrix([[1.,0.,0.],[0.,csb,-ssb],[0.,ssb,csb]]) # Eq. 2.13 (Eq. 1 in 1905.06073)
	VuL = VdL*VCKM.H # page 8 first paragraph
	LamdR = VdR.T*xi*VdR # Eq. 2.11
	LamuR = VuR.T*xi*VuR # Eq. 2.11
	LamdL = VdL.H*xi*VdL # Eq. 2.11
	LamuL = VCKM*LamdL*VCKM.H # page 9 first sentence

# Leptophobic TopColor model
elif model in ['TC', 'tc', 'Tc', 'tC']:
	## Read alpha_em, mass of top, mass of Z, and mass of W from "powheg.input_template"
	path_to_template = 'powheg.input_template'
	f = open(path_to_template)
	for line in f:
		if 'topmass' in line:
			Mtop = float(line.split()[1])
		if 'zmass' in line:
                	MZ = float(line.split()[1])
		if 'wmass' in line:
                	MW = float(line.split()[1])
		if 'alphaem_inv' in line:
                	alphaem_inv = float(line.split()[1])

	## Input for the TC   
	s2w = 1 - MW**2/MZ**2
	sw = sqrt(s2w) 
	cw = sqrt(1 - s2w)
	aEM = 1/alphaem_inv
	ee = 2.*sqrt(np.pi)*sqrt(aEM) # in Recola src/class_particles.f90
	g1 = ee/cw
	const = (sqrt(2.)*ee)/(cw*sw) # Recola factor for Z' couplings


# Set the couplings

## TFHMeg
if model in ['TFHMeg', 'tfhmeg', 'Tfhmeg']:
## Write the TFHMeg couplings into Recola's L-R form 
## float(): convert couplings from sympy.core.numbers.Float to float numbers
	lzpu1x1=float((1./const)*(-1./6.)*LamuL[0,0]*(gF))  
	lzpu1x2=float((1./const)*(-1./6.)*LamuL[0,1]*(gF))
	lzpu1x3=float((1./const)*(-1./6.)*LamuL[0,2]*(gF))
	lzpu2x1=float((1./const)*(-1./6.)*LamuL[1,0]*(gF))
	lzpu2x2=float((1./const)*(-1./6.)*LamuL[1,1]*(gF))
	lzpu2x3=float((1./const)*(-1./6.)*LamuL[1,2]*(gF))
	lzpu3x1=float((1./const)*(-1./6.)*LamuL[2,0]*(gF))
	lzpu3x2=float((1./const)*(-1./6.)*LamuL[2,1]*(gF))
	lzpu3x3=float((1./const)*(-1./6.)*LamuL[2,2]*(gF))
	rzpu1x1=float((1./const)*(-2./3.)*LamuR[0,0]*(gF)) 
	rzpu1x2=float((1./const)*(-2./3.)*LamuR[0,1]*(gF))
	rzpu1x3=float((1./const)*(-2./3.)*LamuR[0,2]*(gF))
	rzpu2x1=float((1./const)*(-2./3.)*LamuR[1,0]*(gF))
	rzpu2x2=float((1./const)*(-2./3.)*LamuR[1,1]*(gF))
	rzpu2x3=float((1./const)*(-2./3.)*LamuR[1,2]*(gF))
	rzpu3x1=float((1./const)*(-2./3.)*LamuR[2,0]*(gF))
	rzpu3x2=float((1./const)*(-2./3.)*LamuR[2,1]*(gF))
	rzpu3x3=float((1./const)*(-2./3.)*LamuR[2,2]*(gF))
	lzpd1x1=float((1./const)*(-1./6.)*LamdL[0,0]*(gF))
	lzpd1x2=float((1./const)*(-1./6.)*LamdL[0,1]*(gF))
	lzpd1x3=float((1./const)*(-1./6.)*LamdL[0,2]*(gF))
	lzpd2x1=float((1./const)*(-1./6.)*LamdL[1,0]*(gF))
	lzpd2x2=float((1./const)*(-1./6.)*LamdL[1,1]*(gF))
	lzpd2x3=float((1./const)*(-1./6.)*LamdL[1,2]*(gF))
	lzpd3x1=float((1./const)*(-1./6.)*LamdL[2,0]*(gF))
	lzpd3x2=float((1./const)*(-1./6.)*LamdL[2,1]*(gF))
	lzpd3x3=float((1./const)*(-1./6.)*LamdL[2,2]*(gF))
	rzpd1x1=float((1./const)*(1./3.)*LamdR[0,0]*(gF)) 
	rzpd1x2=float((1./const)*(1./3.)*LamdR[0,1]*(gF))
	rzpd1x3=float((1./const)*(1./3.)*LamdR[0,2]*(gF))
	rzpd2x1=float((1./const)*(1./3.)*LamdR[1,0]*(gF))
	rzpd2x2=float((1./const)*(1./3.)*LamdR[1,1]*(gF))
	rzpd2x3=float((1./const)*(1./3.)*LamdR[1,2]*(gF))
	rzpd3x1=float((1./const)*(1./3.)*LamdR[2,0]*(gF))
	rzpd3x2=float((1./const)*(1./3.)*LamdR[2,1]*(gF))
	rzpd3x3=float((1./const)*(1./3.)*LamdR[2,2]*(gF))
	lwpq1x1=0.0 
	lwpq1x2=0.0
	lwpq1x3=0.0
	lwpq2x1=0.0
	lwpq2x2=0.0
	lwpq2x3=0.0
	lwpq3x1=0.0
	lwpq3x2=0.0
	lwpq3x3=0.0
	rwpq1x1=0.0
	rwpq1x2=0.0
	rwpq1x3=0.0
	rwpq2x1=0.0
	rwpq2x2=0.0
	rwpq2x3=0.0
	rwpq3x1=0.0
	rwpq3x2=0.0	
	rwpq3x3=0.0
## TC
elif model in ['TC', 'tc', 'Tc', 'tC']:
## Write the TC couplings into Recola's L-R form 
	lzpu1x1=-(1./const)*0.5*(g1)*cotH  
	lzpu1x2=0.0
	lzpu1x3=0.0 
	lzpu2x1=0.0
	lzpu2x2=0.0
	lzpu2x3=0.0
	lzpu3x1=0.0
	lzpu3x2=0.0
	lzpu3x3=(1./const)*0.5*(g1)*cotH
	rzpu1x1=-(1./const)*0.5*(g1)*cotH 
	rzpu1x2=0.0 
	rzpu1x3=0.0
	rzpu2x1=0.0
	rzpu2x2=0.0
	rzpu2x3=0.0
	rzpu3x1=0.0
	rzpu3x2=0.0
	rzpu3x3=(1./const)*0.5*(g1)*cotH
	lzpd1x1=-(1./const)*0.5*(g1)*cotH
	lzpd1x2=0.0 
	lzpd1x3=0.0
	lzpd2x1=0.0
	lzpd2x2=0.0
	lzpd2x3=0.0
	lzpd3x1=0.0
	lzpd3x2=0.0
	lzpd3x3=(1./const)*0.5*(g1)*cotH
	rzpd1x1=0.0 
	rzpd1x2=0.0
	rzpd1x3=0.0
	rzpd2x1=0.0
	rzpd2x2=0.0
	rzpd2x3=0.0
	rzpd3x1=0.0
	rzpd3x2=0.0
	rzpd3x3=0.0
	lwpq1x1=0.0 
	lwpq1x2=0.0
	lwpq1x3=0.0
	lwpq2x1=0.0
	lwpq2x2=0.0
	lwpq2x3=0.0
	lwpq3x1=0.0
	lwpq3x2=0.0
	lwpq3x3=0.0
	rwpq1x1=0.0
	rwpq1x2=0.0
	rwpq1x3=0.0
	rwpq2x1=0.0
	rwpq2x2=0.0
	rwpq2x3=0.0
	rwpq3x1=0.0
	rwpq3x2=0.0	
	rwpq3x3=0.0
## SSM
else:
## The SSM Z' couplings in Recola's LR format 
	lzpu1x1=0.245189276376  
	lzpu1x2=0.0
	lzpu1x3=0.0
	lzpu2x1=0.0
	lzpu2x2=0.245189276376
	lzpu2x3=0.0
	lzpu3x1=0.0
	lzpu3x2=0.0
	lzpu3x3=0.245189276376
	rzpu1x1=-0.108364112362
	rzpu1x2=0.0
	rzpu1x3=0.0
	rzpu2x1=0.0
	rzpu2x2=-0.108364112362
	rzpu2x3=0.0
	rzpu3x1=0.0
	rzpu3x2=0.0
	rzpu3x3=-0.108364112362
	lzpd1x1=-0.299282945137
	lzpd1x2=0.0
	lzpd1x3=0.0
	lzpd2x1=0.0
	lzpd2x2=-0.299282945137
	lzpd2x3=0.0
	lzpd3x1=0.0
	lzpd3x2=0.0
	lzpd3x3=-0.299282945137
	rzpd1x1=0.0542704445273
	rzpd1x2=0.0
	rzpd1x3=0.0
	rzpd2x1=0.0
	rzpd2x2=0.0542704445273
	rzpd2x3=0.0
	rzpd3x1=0.0
	rzpd3x2=0.0
	rzpd3x3=0.0542704445273
	lwpq1x1=0.0 
	lwpq1x2=0.0
	lwpq1x3=0.0
	lwpq2x1=0.0
	lwpq2x2=0.0
	lwpq2x3=0.0
	lwpq3x1=0.0
	lwpq3x2=0.0
	lwpq3x3=0.0
	rwpq1x1=0.0
	rwpq1x2=0.0
	rwpq1x3=0.0
	rwpq2x1=0.0
	rwpq2x2=0.0
	rwpq2x3=0.0
	rwpq3x1=0.0
	rwpq3x2=0.0
	rwpq3x3=0.0


# Set the width of Z'
## TFHMeg
if model in ['TFHMeg', 'tfhmeg', 'Tfhmeg']:
	GZp = float((5.*MZp*gF**2)/(36*np.pi))
## TC
elif model in ['TC', 'tc', 'Tc', 'tC']:
	GZp = ((aEM * cotH**2 * MZp) / (8 * cw**2)) * (sqrt(1 - ((4 * Mtop**2) / (MZp**2))) * (2 + 4 * (Mtop**2/MZp**2)) + 4)
## SSM Z' width, in case not given as a parameter
elif model in ['SSM', 'ssm', 'Ssm']: 
	if checkGZp == False:
		GZp = float(0.03*MZp)

# Read the powheg.input_template file
lines = open('powheg.input_template','r').readlines()

# Edit the content 
for ill,ll in enumerate(lines):
	## TFHMeg
	if model in ['TFHMeg', 'tfhmeg', 'Tfhmeg']:
		if 'This is the TFHMeg' in ll:
			lines[ill] = lines[ill].replace("This is the TFHMeg", str("This is the TFHMeg, see arxiv : 1809.01158"))
		if 'The cot_theta_H' in ll:
                        lines[ill] = lines[ill].replace("! The cot_theta_H parameter is equal to dummy", str(" "))
	## TC
	elif model in ['TC', 'tc', 'Tc', 'tC']:
		if 'This is the TC' in ll:
			lines[ill] = lines[ill].replace("This is the TC", str("This is the Leptophobic TC model, see arxiv : 1112.4928v3"))
		if 'The theta_sb' in ll:
                        lines[ill] = lines[ill].replace("! The theta_sb parameter is equal to dummy", str(" "))
	## SSM
	else:
		if 'This is the SSM' in ll:
                        lines[ill] = lines[ill].replace("This is the SSM", str("This is the SSM, a toy model"))
		if 'The theta_sb' in ll:
                        lines[ill] = lines[ill].replace("! The theta_sb parameter is equal to dummy", str(" "))
		if 'The cot_theta_H' in ll:
                        lines[ill] = lines[ill].replace("! The cot_theta_H parameter is equal to dummy", str(" "))
	## All the models
	if '{GZp}' in ll:
		lines[ill] = lines[ill].replace("{GZp}", "{0:.8e}".format(GZp))
	if '#lzpu1x1' in ll:
		lines[ill] = lines[ill].replace("#lzpu1x1", "{0:.8e}".format(lzpu1x1))
	if '#rzpu1x1' in ll:
		lines[ill] = lines[ill].replace("#rzpu1x1", "{0:.8e}".format(rzpu1x1))
	if '#lzpu2x2' in ll:
		lines[ill] = lines[ill].replace("#lzpu2x2", "{0:.8e}".format(lzpu2x2))
	if '#rzpu2x2' in ll:
		lines[ill] = lines[ill].replace("#rzpu2x2", "{0:.8e}".format(rzpu2x2))
	if '#lzpu3x3' in ll:
		lines[ill] = lines[ill].replace("#lzpu3x3", "{0:.8e}".format(lzpu3x3))
	if '#rzpu3x3' in ll:      
		lines[ill] = lines[ill].replace("#rzpu3x3", "{0:.8e}".format(rzpu3x3))
	if '#lzpd1x1' in ll:
		lines[ill] = lines[ill].replace("#lzpd1x1", "{0:.8e}".format(lzpd1x1))
	if '#rzpd1x1' in ll:
		lines[ill] = lines[ill].replace("#rzpd1x1", "{0:.8e}".format(rzpd1x1))
	if '#lzpd2x2' in ll:
		lines[ill] = lines[ill].replace("#lzpd2x2", "{0:.8e}".format(lzpd2x2))
	if '#rzpd2x2' in ll:
		lines[ill] = lines[ill].replace("#rzpd2x2", "{0:.8e}".format(rzpd2x2))
	if '#lzpd3x3' in ll:
		lines[ill] = lines[ill].replace("#lzpd3x3", "{0:.8e}".format(lzpd3x3))
	if '#rzpd3x3' in ll:      
		lines[ill] = lines[ill].replace("#rzpd3x3", "{0:.8e}".format(rzpd3x3))
	if '#lzpu1x2' in ll:
		lines[ill] = lines[ill].replace("#lzpu1x2", "{0:.8e}".format(lzpu1x2))
	if '#rzpu1x2' in ll:
		lines[ill] = lines[ill].replace("#rzpu1x2", "{0:.8e}".format(rzpu1x2))
	if '#lzpu1x3' in ll:
		lines[ill] = lines[ill].replace("#lzpu1x3", "{0:.8e}".format(lzpu1x3))
	if '#rzpu1x3' in ll:
		lines[ill] = lines[ill].replace("#rzpu1x3", "{0:.8e}".format(rzpu1x3))
	if '#lzpu2x1' in ll:
		lines[ill] = lines[ill].replace("#lzpu2x1", "{0:.8e}".format(lzpu2x1))
	if '#rzpu2x1' in ll:      
		lines[ill] = lines[ill].replace("#rzpu2x1", "{0:.8e}".format(rzpu2x1))
	if '#lzpd1x2' in ll:
		lines[ill] = lines[ill].replace("#lzpd1x2", "{0:.8e}".format(lzpd1x2))
	if '#rzpd1x2' in ll:
		lines[ill] = lines[ill].replace("#rzpd1x2", "{0:.8e}".format(rzpd1x2))
	if '#lzpd1x3' in ll:
		lines[ill] = lines[ill].replace("#lzpd1x3", "{0:.8e}".format(lzpd1x3))
	if '#rzpd1x3' in ll:
		lines[ill] = lines[ill].replace("#rzpd1x3", "{0:.8e}".format(rzpd1x3))
	if '#lzpd2x1' in ll:
		lines[ill] = lines[ill].replace("#lzpd2x1", "{0:.8e}".format(lzpd2x1))
	if '#rzpd2x1' in ll:      
		lines[ill] = lines[ill].replace("#rzpd2x1", "{0:.8e}".format(rzpd2x1))
	if '#lzpu2x3' in ll:
		lines[ill] = lines[ill].replace("#lzpu2x3", "{0:.8e}".format(lzpu2x3))
	if '#rzpu2x3' in ll:
		lines[ill] = lines[ill].replace("#rzpu2x3", "{0:.8e}".format(rzpu2x3))
	if '#lzpu3x1' in ll:
		lines[ill] = lines[ill].replace("#lzpu3x1", "{0:.8e}".format(lzpu3x1))
	if '#rzpu3x1' in ll:
		lines[ill] = lines[ill].replace("#rzpu3x1", "{0:.8e}".format(rzpu3x1))
	if '#lzpu3x2' in ll:
		lines[ill] = lines[ill].replace("#lzpu3x2", "{0:.8e}".format(lzpu3x2))
	if '#rzpu3x2' in ll:      
		lines[ill] = lines[ill].replace("#rzpu3x2", "{0:.8e}".format(rzpu3x2))
	if '#lzpd2x3' in ll:
		lines[ill] = lines[ill].replace("#lzpd2x3", "{0:.8e}".format(lzpd2x3))
	if '#rzpd2x3' in ll:
		lines[ill] = lines[ill].replace("#rzpd2x3", "{0:.8e}".format(rzpd2x3))
	if '#lzpd3x1' in ll:
		lines[ill] = lines[ill].replace("#lzpd3x1", "{0:.8e}".format(lzpd3x1))
	if '#rzpd3x1' in ll:
		lines[ill] = lines[ill].replace("#rzpd3x1", "{0:.8e}".format(rzpd3x1))
	if '#lzpd3x2' in ll:
		lines[ill] = lines[ill].replace("#lzpd3x2", "{0:.8e}".format(lzpd3x2))
	if '#rzpd3x2' in ll:      
		lines[ill] = lines[ill].replace("#rzpd3x2", "{0:.8e}".format(rzpd3x2))
	if '#lwpq1x1' in ll:      
		lines[ill] = lines[ill].replace("#lwpq1x1", "{0:.8e}".format(lwpq1x1))
	if '#lwpq1x2' in ll:      
		lines[ill] = lines[ill].replace("#lwpq1x2", "{0:.8e}".format(lwpq1x2))
	if '#lwpq1x3' in ll:      
		lines[ill] = lines[ill].replace("#lwpq1x3", "{0:.8e}".format(lwpq1x3))
	if '#lwpq2x1' in ll:      
		lines[ill] = lines[ill].replace("#lwpq2x1", "{0:.8e}".format(lwpq2x1))
	if '#lwpq2x2' in ll:      
		lines[ill] = lines[ill].replace("#lwpq2x2", "{0:.8e}".format(lwpq2x2))
	if '#lwpq2x3' in ll:      
		lines[ill] = lines[ill].replace("#lwpq2x3", "{0:.8e}".format(lwpq2x3))
	if '#lwpq3x1' in ll:      
		lines[ill] = lines[ill].replace("#lwpq3x1", "{0:.8e}".format(lwpq3x1))
	if '#lwpq3x2' in ll:      
		lines[ill] = lines[ill].replace("#lwpq3x2", "{0:.8e}".format(lwpq3x2))
	if '#lwpq3x3' in ll:      
		lines[ill] = lines[ill].replace("#lwpq3x3", "{0:.8e}".format(lwpq3x3))
	if '#rwpq1x1' in ll:      
	 	lines[ill] = lines[ill].replace("#rwpq1x1", "{0:.8e}".format(rwpq1x1))
	if '#rwpq1x2' in ll:      
		lines[ill] = lines[ill].replace("#rwpq1x2", "{0:.8e}".format(rwpq1x2))
	if '#rwpq1x3' in ll:      
		lines[ill] = lines[ill].replace("#rwpq1x3", "{0:.8e}".format(rwpq1x3))
	if '#rwpq2x1' in ll:      
		lines[ill] = lines[ill].replace("#rwpq2x1", "{0:.8e}".format(rwpq2x1))
	if '#rwpq2x2' in ll:      
		lines[ill] = lines[ill].replace("#rwpq2x2", "{0:.8e}".format(rwpq2x2))
	if '#rwpq2x3' in ll:      
		lines[ill] = lines[ill].replace("#rwpq2x3", "{0:.8e}".format(rwpq2x3))
	if '#rwpq3x1' in ll:      
		lines[ill] = lines[ill].replace("#rwpq3x1", "{0:.8e}".format(rwpq3x1))
	if '#rwpq3x2' in ll:      
		lines[ill] = lines[ill].replace("#rwpq3x2", "{0:.8e}".format(rwpq3x2))
	if '#rwpq3x3' in ll:      
		lines[ill] = lines[ill].replace("#rwpq3x3", "{0:.8e}".format(rwpq3x3))

# Create a powheg.input file and write the edited content to it
f= open('powheg.input','w')
f.write(''.join(lines))
f.close()

# Delete the Single variables from params.dat to be able to make a HeatMap at a later stage
with open(path_to_params, "r") as f:
	lines = f.readlines()
with open(path_to_params, "w") as f:
    	for line in lines:
        	if "model" not in line.strip("\n"):
            		f.write(line)
with open(path_to_params, "r") as f:
        lines = f.readlines()
with open(path_to_params, "w") as f:
        for line in lines:
                if "dummy" not in line.strip("\n"):
                        f.write(line)
with open(path_to_params, "r") as f:
        lines = f.readlines()
with open(path_to_params, "w") as f:
        for line in lines:
                if "GZp" not in line.strip("\n"):
                        f.write(line)

	

