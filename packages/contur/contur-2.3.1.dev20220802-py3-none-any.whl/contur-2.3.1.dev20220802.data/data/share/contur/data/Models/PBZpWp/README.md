## Run a Batch Job

- Create a run-directory then cd into it.

        $ cd run-directory-SSM

  You will need 3 execuatbles (main-pythia, pwhg_main, and pbzp_input_contur.py), 2 files (param_file.dat and powheg.input_template), and 1 directory (RunInfo), all of them in one directory.

- The 'main-pythia' can be created from main-pythia.cc. Pythia must be compiled with HepMC support, using the same version of HepMC used when compiling RIVET. One has to copy the `Makefile` and the `Makefile.inc` from the `/share/Pythia8/examples`. Makefile needs to be edited in order to be able to choose the executable name. 'main-pythia' can be then built as follows

        $ make main-pythia

- The 'RunInfo' directory can be copied from `contur/AnalysisTools/GridSetup/RunInfo`.

- The 'pbzp_input_contur.py' script is used to create and fill the 'powheg.input' files based on the model choice in the 'param_file.dat', it needs the 'powheg.input_template' in order to do so.

- The 'param_file.dat' file defines the parameter space. In the SSM we only have two parameters i.e. the mass and the width of the Z', but we also need to include the name of the model (SSM in this particular case) and the parameters of the other models as dummy (tsb i.e. the angle theta_sb needed for the TFHMeg, and cotH needed for the TC model. This is done in order to be able to use the same 'powheg.input_template' for all the models). The 'param_file.dat' of the SSM should be formatted like this (an example of the one for the TFHMeg can be found in the directory TFHMeg, and for the TC model in the directory TC):

```
#NEW style parameter reading file
#Based off configObj python template
[Run]
generator ='/unix/cedar/altakach/tools_cos7/contur/setupPBZpWp.sh','/unix/cedar/software/cos7/Herwig-repo_Rivet-repo/setupEnv.sh'
contur ='/unix/cedar/altakach/tools_cos7/contur/setupContur.sh'

[Parameters]
[[mZp]]
mode = LIN
start = 1000.0
stop = 5000.0
number = 9
[[GZp]]
mode = LIN
start = 50.0
stop = 500.0
number = 10
[[model]]
mode = SINGLE
name = SSM
[[tsb]]
mode = SINGLE
name = dummy
[[cotH]]
mode = SINGLE
name = dummy

```
- `setupPBZpWp.sh` is a script which sets the environment needed to run the `pwhg_main`.

- `setupEnv.sh` should be a script which sets up your runtime environment which the batch jobs will use. As a minimum
   is will need to contain the lines to execute your rivetenv.sh and yodaenv.sh files. 

- `setupContur.sh` is the contur setup script in your contur directory.

- For all these set up files, you should give the full explicit path. The `setupPBZpWp.sh` and the `setupEnv.sh` should be always in the same order as in shown in this example i.e. in `generator` you first give the full path to `setupPBZpWp.sh` then the one for `setupEnv.sh`.

- You should check that the parameters defined in 'params_file.dat' are also defined in
  the 'powheg.input_template' file within the same directory.

- The example model has parameters 'model', 'tsb', 'cotH', 'mZp', and 'GZp' defined in
  'params_file.dat' and the 'powheg.input_template' file has:

```
	! This is the {model}
	! The theta_sb parameter is equal to {tsb}
	! The cot_theta_H parameter is equal to {cotH}
        zpmass      {mZp} ! The mass of Z'
	zpwidth     {GZp}  ! The width of Z'

```        
  If you want to add or remove parameters you must do this in both files.  

- To run a test scan over the parameter space defined in 'param_file.dat' without submitting it
  to a batch farm.  (The `-s` flag ensure no jobs will be submitted.)

         $ contur-batch -n 1000 -t powheg.input_template -m pbzpwp -s

  This will produce a directory called 'myscan00' containing one directory for each known beam energy, each containing
  however many runpoint directories are indicated by the ranges in your param_file.dat. Have a look at the shell scripts
  ('runpoint_xxxx.sh') which have been generated to check all is as you expected.
  You can manually submit some of the 'runpoint_xxxx.sh' files as a test. We should mention that at this stage i.e. before running the 'runpoint_xxxx.sh' files, the powheg.input files are not yet  
  created, only after running the .sh files, which run the 'pbzp_input_contur.py' script, the 'powheg.input' files needed by PBZpWp will be created and properly edited. 

- Now you are ready to run batch jobs. Remove the myscan00 directory tree you just created, and run the
  batch submit command again, now without the `-s` flag and specifying the queue
  on your batch farm. For example:

         $ contur-batch -n 1000 -t powheg.input_template -m pbzpwp -q mediumc7

  (Note that we assume `qsub` is available on your system here. Slurm and condor batch systems are also supported.
  If you have a different submission system you'll need to
  look into `$CONTURMODULEDIR/AnalysisTools/contur/contur/Scan/batch_submit.py` and work out how to change the appropriate submission
  commands.)

- A successful run will produce a directory called 'myscan00' as before. You need to wait for the farm
  to finish the jobs before continuing. You can check the progress using the 'qstat' command.

- When the batch job is complete there should, in every run point directory, be a 'runpoint_xxxx.yoda' file and an output.pbzpwp directory that contains the .lhe file.
