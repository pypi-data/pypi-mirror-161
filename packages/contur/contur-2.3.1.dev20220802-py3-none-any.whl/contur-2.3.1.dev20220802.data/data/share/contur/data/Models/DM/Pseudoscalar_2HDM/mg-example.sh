set group_subprocesses Auto
set ignore_six_quark_processes False
set gauge unitary
set loop_optimized_output True
set complex_mass_scheme False
set automatic_html_opening False
set run_mode 0
set nb_core 1
set low_mem_multicore_nlo_generation
import model ./Pseudoscalar_2HDM
define p = g u c d s u~ c~ d~ s~ 
define j = g u c d s u~ c~ d~ s~ 
define l+ = e+ mu+
define l- = e- mu-
define vl = ve vm vt
define vl~ = ve~ vm~ vt~
define p = p b  b~
define j = j b  b~
define allsm = t t~ z w+ w- b b~ h1
define allbsm = h2 h3 h+ h- h4 
generate p p > allsm allbsm allbsm DMS=2 QCD=2
add process p p > allsm allsm allbsm DMS=2 QCD=2
add process p p > allbsm allbsm allbsm DMS=2 QCD=2
output mgevents
launch
shower=Pythia8
set ebeam1	{beam}
set ebeam2	{beam}
set maxjetflavor 5
set iseed	{seed}
set nevents	{nevents}
set gPXd	{gPXd}
set tanbeta	{tanbeta}
set sinbma	{sinbma}
set lam3	{lam3}
set lap1	{laP1}
set lap2	{laP2}
set sinp	{sinp}
set Mxd	{mXd}
set mh1	1.250000e+02
set mh2	{mh2}
set mh3 {mh3}
set mhc {mhc}
set mh4 {mh4}
set Wh1 Auto
set Wh2 Auto
set Wh3 Auto
set Whc Auto
set Wh4 Auto
