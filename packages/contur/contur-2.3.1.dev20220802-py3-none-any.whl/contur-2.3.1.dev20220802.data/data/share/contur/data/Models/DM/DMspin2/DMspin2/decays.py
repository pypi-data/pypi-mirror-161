# This file was automatically created by FeynRules 2.4.43
# Mathematica version: 10.1.0  for Mac OS X x86 (64-bit) (March 24, 2015)
# Date: Wed 1 Jun 2016 20:28:08


from .object_library import all_decays, Decay
from . import particles as P


Decay_H = Decay(name = 'Decay_H',
                particle = P.H,
                partial_widths = {(P.t,P.t__tilde__):'((3*MH**2*yt**2 - 12*MT**2*yt**2)*cmath.sqrt(MH**4 - 4*MH**2*MT**2))/(16.*cmath.pi*abs(MH)**3)',
                                  (P.W__minus__,P.W__plus__):'(((3*ee**4*vev**2)/(4.*sw**4) + (ee**4*MH**4*vev**2)/(16.*MW**4*sw**4) - (ee**4*MH**2*vev**2)/(4.*MW**2*sw**4))*cmath.sqrt(MH**4 - 4*MH**2*MW**2))/(16.*cmath.pi*abs(MH)**3)',
                                  (P.Z,P.Z):'(((9*ee**4*vev**2)/2. + (3*ee**4*MH**4*vev**2)/(8.*MZ**4) - (3*ee**4*MH**2*vev**2)/(2.*MZ**2) + (3*cw**4*ee**4*vev**2)/(4.*sw**4) + (cw**4*ee**4*MH**4*vev**2)/(16.*MZ**4*sw**4) - (cw**4*ee**4*MH**2*vev**2)/(4.*MZ**2*sw**4) + (3*cw**2*ee**4*vev**2)/sw**2 + (cw**2*ee**4*MH**4*vev**2)/(4.*MZ**4*sw**2) - (cw**2*ee**4*MH**2*vev**2)/(MZ**2*sw**2) + (3*ee**4*sw**2*vev**2)/cw**2 + (ee**4*MH**4*sw**2*vev**2)/(4.*cw**2*MZ**4) - (ee**4*MH**2*sw**2*vev**2)/(cw**2*MZ**2) + (3*ee**4*sw**4*vev**2)/(4.*cw**4) + (ee**4*MH**4*sw**4*vev**2)/(16.*cw**4*MZ**4) - (ee**4*MH**2*sw**4*vev**2)/(4.*cw**4*MZ**2))*cmath.sqrt(MH**4 - 4*MH**2*MZ**2))/(32.*cmath.pi*abs(MH)**3)'})

Decay_t = Decay(name = 'Decay_t',
                particle = P.t,
                partial_widths = {(P.W__plus__,P.b):'((MT**2 - MW**2)*((3*ee**2*MT**2)/(2.*sw**2) + (3*ee**2*MT**4)/(2.*MW**2*sw**2) - (3*ee**2*MW**2)/sw**2))/(96.*cmath.pi*abs(MT)**3)'})

Decay_W__plus__ = Decay(name = 'Decay_W__plus__',
                        particle = P.W__plus__,
                        partial_widths = {(P.c,P.d__tilde__):'(CKM2x1*ee**2*MW**4*complexconjugate(CKM2x1))/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.c,P.s__tilde__):'(CKM2x2*ee**2*MW**4*complexconjugate(CKM2x2))/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.t,P.b__tilde__):'((-MT**2 + MW**2)*((-3*ee**2*MT**2)/(2.*sw**2) - (3*ee**2*MT**4)/(2.*MW**2*sw**2) + (3*ee**2*MW**2)/sw**2))/(48.*cmath.pi*abs(MW)**3)',
                                          (P.u,P.d__tilde__):'(CKM1x1*ee**2*MW**4*complexconjugate(CKM1x1))/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.u,P.s__tilde__):'(CKM1x2*ee**2*MW**4*complexconjugate(CKM1x2))/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.ve,P.e__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.vm,P.mu__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.vt,P.ta__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)'})

Decay_Y2 = Decay(name = 'Decay_Y2',
                 particle = P.Y2,
                 partial_widths = {(P.a,P.a):'(MY2**2*((2*cw**4*gTb**2*MY2**4)/Lambda**2 + (4*cw**2*gTb*gTw*MY2**4*sw**2)/Lambda**2 + (2*gTw**2*MY2**4*sw**4)/Lambda**2))/(160.*cmath.pi*abs(MY2)**3)',
                                   (P.a,P.Z):'((MY2**2 - MZ**2)*((2*cw**2*gTb**2*MY2**4*sw**2)/Lambda**2 - (4*cw**2*gTb*gTw*MY2**4*sw**2)/Lambda**2 + (2*cw**2*gTw**2*MY2**4*sw**2)/Lambda**2 - (3*cw**2*gTb**2*MY2**2*MZ**2*sw**2)/Lambda**2 + (6*cw**2*gTb*gTw*MY2**2*MZ**2*sw**2)/Lambda**2 - (3*cw**2*gTw**2*MY2**2*MZ**2*sw**2)/Lambda**2 + (cw**2*gTb**2*MZ**4*sw**2)/(3.*Lambda**2) - (2*cw**2*gTb*gTw*MZ**4*sw**2)/(3.*Lambda**2) + (cw**2*gTw**2*MZ**4*sw**2)/(3.*Lambda**2) + (cw**2*gTb**2*MZ**6*sw**2)/(3.*Lambda**2*MY2**2) - (2*cw**2*gTb*gTw*MZ**6*sw**2)/(3.*Lambda**2*MY2**2) + (cw**2*gTw**2*MZ**6*sw**2)/(3.*Lambda**2*MY2**2) + (cw**2*gTb**2*MZ**8*sw**2)/(3.*Lambda**2*MY2**4) - (2*cw**2*gTb*gTw*MZ**8*sw**2)/(3.*Lambda**2*MY2**4) + (cw**2*gTw**2*MZ**8*sw**2)/(3.*Lambda**2*MY2**4)))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.b,P.b__tilde__):'(3*gTq**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.c,P.c__tilde__):'(3*gTq**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.d,P.d__tilde__):'(MY2**2*((3*gTq**2*MY2**4)/(4.*Lambda**2) + (3*CKM1x1**2*gTq**2*MY2**4*complexconjugate(CKM1x1)**2)/(4.*Lambda**2) + (3*CKM1x1*CKM2x1*gTq**2*MY2**4*complexconjugate(CKM1x1)*complexconjugate(CKM2x1))/(2.*Lambda**2) + (3*CKM2x1**2*gTq**2*MY2**4*complexconjugate(CKM2x1)**2)/(4.*Lambda**2)))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.d,P.s__tilde__):'(MY2**2*((3*CKM1x1*CKM1x2*gTq**2*MY2**4*complexconjugate(CKM1x1)*complexconjugate(CKM1x2))/(4.*Lambda**2) + (3*CKM1x1*CKM2x2*gTq**2*MY2**4*complexconjugate(CKM1x2)*complexconjugate(CKM2x1))/(4.*Lambda**2) + (3*CKM1x2*CKM2x1*gTq**2*MY2**4*complexconjugate(CKM1x1)*complexconjugate(CKM2x2))/(4.*Lambda**2) + (3*CKM2x1*CKM2x2*gTq**2*MY2**4*complexconjugate(CKM2x1)*complexconjugate(CKM2x2))/(4.*Lambda**2)))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.e__minus__,P.e__plus__):'(gTl**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.g,P.g):'(gTg**2*MY2**6)/(10.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.H,P.H):'(((8*gTh**2*MH**4)/(3.*Lambda**2) - (4*gTh**2*MH**2*MY2**2)/(3.*Lambda**2) + (gTh**2*MY2**4)/(6.*Lambda**2))*cmath.sqrt(-4*MH**2*MY2**2 + MY2**4))/(160.*cmath.pi*abs(MY2)**3)',
                                   (P.mu__minus__,P.mu__plus__):'(gTl**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.s,P.d__tilde__):'(MY2**2*((3*CKM1x1*CKM1x2*gTq**2*MY2**4*complexconjugate(CKM1x1)*complexconjugate(CKM1x2))/(4.*Lambda**2) + (3*CKM1x1*CKM2x2*gTq**2*MY2**4*complexconjugate(CKM1x2)*complexconjugate(CKM2x1))/(4.*Lambda**2) + (3*CKM1x2*CKM2x1*gTq**2*MY2**4*complexconjugate(CKM1x1)*complexconjugate(CKM2x2))/(4.*Lambda**2) + (3*CKM2x1*CKM2x2*gTq**2*MY2**4*complexconjugate(CKM2x1)*complexconjugate(CKM2x2))/(4.*Lambda**2)))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.s,P.s__tilde__):'(MY2**2*((3*gTq**2*MY2**4)/(4.*Lambda**2) + (3*CKM1x2**2*gTq**2*MY2**4*complexconjugate(CKM1x2)**2)/(4.*Lambda**2) + (3*CKM1x2*CKM2x2*gTq**2*MY2**4*complexconjugate(CKM1x2)*complexconjugate(CKM2x2))/(2.*Lambda**2) + (3*CKM2x2**2*gTq**2*MY2**4*complexconjugate(CKM2x2)**2)/(4.*Lambda**2)))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.t,P.t__tilde__):'(((-16*gTq3**2*MT**4)/Lambda**2 - (2*gTq3**2*MT**2*MY2**2)/Lambda**2 + (3*gTq3**2*MY2**4)/(2.*Lambda**2))*cmath.sqrt(-4*MT**2*MY2**2 + MY2**4))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.ta__minus__,P.ta__plus__):'(gTl**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.u,P.u__tilde__):'(3*gTq**2*MY2**6)/(160.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.ve,P.ve__tilde__):'(gTl**2*MY2**6)/(320.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.vm,P.vm__tilde__):'(gTl**2*MY2**6)/(320.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.vt,P.vt__tilde__):'(gTl**2*MY2**6)/(320.*cmath.pi*Lambda**2*abs(MY2)**3)',
                                   (P.W__minus__,P.W__plus__):'(((12*gTw**2*MW**4)/Lambda**2 - (6*gTw**2*MW**2*MY2**2)/Lambda**2 + (2*gTw**2*MY2**4)/Lambda**2 - (10*ee**2*gTh*gTw*MW**2*vev**2)/(3.*Lambda**2*sw**2) + (10*ee**2*gTh*gTw*MY2**2*vev**2)/(3.*Lambda**2*sw**2) + (7*ee**4*gTh**2*vev**4)/(12.*Lambda**2*sw**4) + (ee**4*gTh**2*MY2**2*vev**4)/(8.*Lambda**2*MW**2*sw**4) + (ee**4*gTh**2*MY2**4*vev**4)/(96.*Lambda**2*MW**4*sw**4))*cmath.sqrt(-4*MW**2*MY2**2 + MY2**4))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.Xd,P.Xd__tilde__):'(((-16*gTx**2*MXd**4)/(3.*Lambda**2) - (2*gTx**2*MXd**2*MY2**2)/(3.*Lambda**2) + (gTx**2*MY2**4)/(2.*Lambda**2))*cmath.sqrt(-4*MXd**2*MY2**2 + MY2**4))/(80.*cmath.pi*abs(MY2)**3)',
                                   (P.Z,P.Z):'(((2*cw**4*gTw**2*MY2**4)/Lambda**2 - (6*cw**4*gTw**2*MY2**2*MZ**2)/Lambda**2 + (12*cw**4*gTw**2*MZ**4)/Lambda**2 + (4*cw**2*gTb*gTw*MY2**4*sw**2)/Lambda**2 - (12*cw**2*gTb*gTw*MY2**2*MZ**2*sw**2)/Lambda**2 + (24*cw**2*gTb*gTw*MZ**4*sw**2)/Lambda**2 + (2*gTb**2*MY2**4*sw**4)/Lambda**2 - (6*gTb**2*MY2**2*MZ**2*sw**4)/Lambda**2 + (12*gTb**2*MZ**4*sw**4)/Lambda**2 + (10*cw**2*ee**2*gTb*gTh*MY2**2*vev**2)/(3.*Lambda**2) + (20*cw**2*ee**2*gTh*gTw*MY2**2*vev**2)/(3.*Lambda**2) - (10*cw**2*ee**2*gTb*gTh*MZ**2*vev**2)/(3.*Lambda**2) - (20*cw**2*ee**2*gTh*gTw*MZ**2*vev**2)/(3.*Lambda**2) + (10*cw**4*ee**2*gTh*gTw*MY2**2*vev**2)/(3.*Lambda**2*sw**2) - (10*cw**4*ee**2*gTh*gTw*MZ**2*vev**2)/(3.*Lambda**2*sw**2) + (20*ee**2*gTb*gTh*MY2**2*sw**2*vev**2)/(3.*Lambda**2) + (10*ee**2*gTh*gTw*MY2**2*sw**2*vev**2)/(3.*Lambda**2) - (20*ee**2*gTb*gTh*MZ**2*sw**2*vev**2)/(3.*Lambda**2) - (10*ee**2*gTh*gTw*MZ**2*sw**2*vev**2)/(3.*Lambda**2) + (10*ee**2*gTb*gTh*MY2**2*sw**4*vev**2)/(3.*cw**2*Lambda**2) - (10*ee**2*gTb*gTh*MZ**2*sw**4*vev**2)/(3.*cw**2*Lambda**2) + (7*ee**4*gTh**2*vev**4)/(2.*Lambda**2) + (ee**4*gTh**2*MY2**4*vev**4)/(16.*Lambda**2*MZ**4) + (3*ee**4*gTh**2*MY2**2*vev**4)/(4.*Lambda**2*MZ**2) + (7*cw**4*ee**4*gTh**2*vev**4)/(12.*Lambda**2*sw**4) + (cw**4*ee**4*gTh**2*MY2**4*vev**4)/(96.*Lambda**2*MZ**4*sw**4) + (cw**4*ee**4*gTh**2*MY2**2*vev**4)/(8.*Lambda**2*MZ**2*sw**4) + (7*cw**2*ee**4*gTh**2*vev**4)/(3.*Lambda**2*sw**2) + (cw**2*ee**4*gTh**2*MY2**4*vev**4)/(24.*Lambda**2*MZ**4*sw**2) + (cw**2*ee**4*gTh**2*MY2**2*vev**4)/(2.*Lambda**2*MZ**2*sw**2) + (7*ee**4*gTh**2*sw**2*vev**4)/(3.*cw**2*Lambda**2) + (ee**4*gTh**2*MY2**4*sw**2*vev**4)/(24.*cw**2*Lambda**2*MZ**4) + (ee**4*gTh**2*MY2**2*sw**2*vev**4)/(2.*cw**2*Lambda**2*MZ**2) + (7*ee**4*gTh**2*sw**4*vev**4)/(12.*cw**4*Lambda**2) + (ee**4*gTh**2*MY2**4*sw**4*vev**4)/(96.*cw**4*Lambda**2*MZ**4) + (ee**4*gTh**2*MY2**2*sw**4*vev**4)/(8.*cw**4*Lambda**2*MZ**2))*cmath.sqrt(MY2**4 - 4*MY2**2*MZ**2))/(160.*cmath.pi*abs(MY2)**3)'})

Decay_Z = Decay(name = 'Decay_Z',
                particle = P.Z,
                partial_widths = {(P.a,P.Y2):'((-MY2**2 + MZ**2)*((2*cw**2*gTb**2*MY2**4*sw**2)/Lambda**2 - (4*cw**2*gTb*gTw*MY2**4*sw**2)/Lambda**2 + (2*cw**2*gTw**2*MY2**4*sw**2)/Lambda**2 + (cw**2*gTb**2*MY2**6*sw**2)/(Lambda**2*MZ**2) - (2*cw**2*gTb*gTw*MY2**6*sw**2)/(Lambda**2*MZ**2) + (cw**2*gTw**2*MY2**6*sw**2)/(Lambda**2*MZ**2) - (3*cw**2*gTb**2*MY2**2*MZ**2*sw**2)/Lambda**2 + (6*cw**2*gTb*gTw*MY2**2*MZ**2*sw**2)/Lambda**2 - (3*cw**2*gTw**2*MY2**2*MZ**2*sw**2)/Lambda**2 - (3*cw**2*gTb**2*MZ**4*sw**2)/Lambda**2 + (6*cw**2*gTb*gTw*MZ**4*sw**2)/Lambda**2 - (3*cw**2*gTw**2*MZ**4*sw**2)/Lambda**2 + (2*cw**2*gTb**2*MZ**6*sw**2)/(Lambda**2*MY2**2) - (4*cw**2*gTb*gTw*MZ**6*sw**2)/(Lambda**2*MY2**2) + (2*cw**2*gTw**2*MZ**6*sw**2)/(Lambda**2*MY2**2) + (cw**2*gTb**2*MZ**8*sw**2)/(Lambda**2*MY2**4) - (2*cw**2*gTb*gTw*MZ**8*sw**2)/(Lambda**2*MY2**4) + (cw**2*gTw**2*MZ**8*sw**2)/(Lambda**2*MY2**4)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.b,P.b__tilde__):'(MZ**2*(ee**2*MZ**2 + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.c,P.c__tilde__):'(MZ**2*(-(ee**2*MZ**2) + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (17*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.d,P.d__tilde__):'(MZ**2*(ee**2*MZ**2 + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.e__minus__,P.e__plus__):'(MZ**2*(-(ee**2*MZ**2) + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.mu__minus__,P.mu__plus__):'(MZ**2*(-(ee**2*MZ**2) + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.s,P.s__tilde__):'(MZ**2*(ee**2*MZ**2 + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.t,P.t__tilde__):'((-11*ee**2*MT**2 - ee**2*MZ**2 - (3*cw**2*ee**2*MT**2)/(2.*sw**2) + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (7*ee**2*MT**2*sw**2)/(6.*cw**2) + (17*ee**2*MZ**2*sw**2)/(6.*cw**2))*cmath.sqrt(-4*MT**2*MZ**2 + MZ**4))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.ta__minus__,P.ta__plus__):'(MZ**2*(-(ee**2*MZ**2) + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.u,P.u__tilde__):'(MZ**2*(-(ee**2*MZ**2) + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (17*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.ve,P.ve__tilde__):'(MZ**2*(ee**2*MZ**2 + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.vm,P.vm__tilde__):'(MZ**2*(ee**2*MZ**2 + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.vt,P.vt__tilde__):'(MZ**2*(ee**2*MZ**2 + (cw**2*ee**2*MZ**2)/(2.*sw**2) + (ee**2*MZ**2*sw**2)/(2.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
                                  (P.W__minus__,P.W__plus__):'(((-12*cw**2*ee**2*MW**2)/sw**2 - (17*cw**2*ee**2*MZ**2)/sw**2 + (4*cw**2*ee**2*MZ**4)/(MW**2*sw**2) + (cw**2*ee**2*MZ**6)/(4.*MW**4*sw**2))*cmath.sqrt(-4*MW**2*MZ**2 + MZ**4))/(48.*cmath.pi*abs(MZ)**3)'})

