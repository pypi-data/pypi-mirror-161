set group_subprocesses Auto
set ignore_six_quark_processes False
set gauge unitary
set loop_optimized_output True
set complex_mass_scheme False
set automatic_html_opening False
set run_mode 0
set nb_core 1
import model ./DM_vector_mediator_UFO
define p = g u c d s u~ c~ d~ s~ b  b~
generate p p > t t~ Y1 DMS=2 QCD=4
output mgevents
launch
shower=Pythia8
set MY1        {mY1}
set MXm        {mXm}
set gYq        {gYq}
set gYXm       {gYXm}
