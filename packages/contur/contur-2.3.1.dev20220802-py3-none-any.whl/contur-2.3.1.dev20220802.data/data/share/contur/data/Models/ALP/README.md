### Axion-like particles - "ALPS"

* The UFO file in ALP is from [Collider Probes of Axion-Like Particles](https://arxiv.org/abs/1708.00443) by Martin Bauer, Matthias Neubert, Andrea Thamm, with one bug fixed and one worked around (see notes below).

  Note that to use this, you need to ignore the vertices which Herwig can't handle:
    `ufo2herwig ALP --ignore-skipped ; make`

Note 1: The cZh5 parameter should determine the Higgs width to ZA, but is having no effect on it. However, when the default
is changed in the model, this does have the expected effect. In the parameters.py file above, cZh5 is defaulted to zero, which means
we don't have a ridouclously large H to ZA BR (in fact it is zero, as expected when cZh5 is zero).

Note 2: There was a bug in the UFO file which crashed Herwig when MALP+MZ > MH. This is fixed in the version given here.
 
* Some other possibly interesting papers
    - [Axion global fits with Peccei-Quinn symmetry breaking before inflation using GAMBIT](https://arxiv.org/abs/1810.07192)  
    - [Gravity safe, electroweak natural axionic solution to strong CP and SUSY mu problems](https://arxiv.org/abs/1810.03713)




