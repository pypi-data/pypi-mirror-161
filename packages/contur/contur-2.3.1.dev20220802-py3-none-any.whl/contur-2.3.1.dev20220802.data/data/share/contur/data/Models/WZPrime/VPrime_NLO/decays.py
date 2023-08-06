# This file was automatically created by FeynRules 2.3.10
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Thu 19 Jan 2017 16:30:59


from object_library import all_decays, Decay
import particles as P


Decay_H = Decay(name = 'Decay_H',
                particle = P.H,
                partial_widths = {(P.t,P.t__tilde__):'((3*MH**2*yt**2 - 12*MT**2*yt**2)*cmath.sqrt(MH**4 - 4*MH**2*MT**2))/(16.*cmath.pi*abs(MH)**3)',
                                  (P.W__minus__,P.W__plus__):'(((3*ee**4*vev**2)/(4.*sw**4) + (ee**4*MH**4*vev**2)/(16.*MW**4*sw**4) - (ee**4*MH**2*vev**2)/(4.*MW**2*sw**4))*cmath.sqrt(MH**4 - 4*MH**2*MW**2))/(16.*cmath.pi*abs(MH)**3)',
                                  (P.Z,P.Z):'(((9*ee**4*vev**2)/2. + (3*ee**4*MH**4*vev**2)/(8.*MZ**4) - (3*ee**4*MH**2*vev**2)/(2.*MZ**2) + (3*cw**4*ee**4*vev**2)/(4.*sw**4) + (cw**4*ee**4*MH**4*vev**2)/(16.*MZ**4*sw**4) - (cw**4*ee**4*MH**2*vev**2)/(4.*MZ**2*sw**4) + (3*cw**2*ee**4*vev**2)/sw**2 + (cw**2*ee**4*MH**4*vev**2)/(4.*MZ**4*sw**2) - (cw**2*ee**4*MH**2*vev**2)/(MZ**2*sw**2) + (3*ee**4*sw**2*vev**2)/cw**2 + (ee**4*MH**4*sw**2*vev**2)/(4.*cw**2*MZ**4) - (ee**4*MH**2*sw**2*vev**2)/(cw**2*MZ**2) + (3*ee**4*sw**4*vev**2)/(4.*cw**4) + (ee**4*MH**4*sw**4*vev**2)/(16.*cw**4*MZ**4) - (ee**4*MH**2*sw**4*vev**2)/(4.*cw**4*MZ**2))*cmath.sqrt(MH**4 - 4*MH**2*MZ**2))/(32.*cmath.pi*abs(MH)**3)'})

Decay_t = Decay(name = 'Decay_t',
                particle = P.t,
                partial_widths = {(P.W__plus__,P.b):'((MT**2 - MW**2)*((3*ee**2*MT**2)/(2.*sw**2) + (3*ee**2*MT**4)/(2.*MW**2*sw**2) - (3*ee**2*MW**2)/sw**2))/(96.*cmath.pi*abs(MT)**3)',
                                  (P.Wp__plus__,P.b):'((MT**2 - MWp**2)*((3*ee**2*kL**2*MT**2)/(2.*sw**2) + (3*ee**2*kR**2*MT**2)/(2.*sw**2) + (3*ee**2*kL**2*MT**4)/(2.*MWp**2*sw**2) + (3*ee**2*kR**2*MT**4)/(2.*MWp**2*sw**2) - (3*ee**2*kL**2*MWp**2)/sw**2 - (3*ee**2*kR**2*MWp**2)/sw**2))/(96.*cmath.pi*abs(MT)**3)'})

Decay_W__plus__ = Decay(name = 'Decay_W__plus__',
                        particle = P.W__plus__,
                        partial_widths = {(P.c,P.s__tilde__):'(ee**2*MW**4)/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.t,P.b__tilde__):'((-MT**2 + MW**2)*((-3*ee**2*MT**2)/(2.*sw**2) - (3*ee**2*MT**4)/(2.*MW**2*sw**2) + (3*ee**2*MW**2)/sw**2))/(48.*cmath.pi*abs(MW)**3)',
                                          (P.u,P.d__tilde__):'(ee**2*MW**4)/(16.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.ve,P.e__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.vm,P.mu__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)',
                                          (P.vt,P.ta__plus__):'(ee**2*MW**4)/(48.*cmath.pi*sw**2*abs(MW)**3)'})

Decay_Wp__plus__ = Decay(name = 'Decay_Wp__plus__',
                         particle = P.Wp__plus__,
                         partial_widths = {(P.c,P.s__tilde__):'(MWp**2*((3*ee**2*kL**2*MWp**2)/sw**2 + (3*ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)',
                                           (P.t,P.b__tilde__):'((-MT**2 + MWp**2)*((-3*ee**2*kL**2*MT**2)/(2.*sw**2) - (3*ee**2*kR**2*MT**2)/(2.*sw**2) - (3*ee**2*kL**2*MT**4)/(2.*MWp**2*sw**2) - (3*ee**2*kR**2*MT**4)/(2.*MWp**2*sw**2) + (3*ee**2*kL**2*MWp**2)/sw**2 + (3*ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)',
                                           (P.u,P.d__tilde__):'(MWp**2*((3*ee**2*kL**2*MWp**2)/sw**2 + (3*ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)',
                                           (P.ve,P.e__plus__):'(MWp**2*((ee**2*kL**2*MWp**2)/sw**2 + (ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)',
                                           (P.vm,P.mu__plus__):'(MWp**2*((ee**2*kL**2*MWp**2)/sw**2 + (ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)',
                                           (P.vt,P.ta__plus__):'(MWp**2*((ee**2*kL**2*MWp**2)/sw**2 + (ee**2*kR**2*MWp**2)/sw**2))/(48.*cmath.pi*abs(MWp)**3)'})

Decay_Z = Decay(name = 'Decay_Z',
                particle = P.Z,
                partial_widths = {(P.b,P.b__tilde__):'(MZ**2*(ee**2*MZ**2 + (3*cw**2*ee**2*MZ**2)/(2.*sw**2) + (5*ee**2*MZ**2*sw**2)/(6.*cw**2)))/(48.*cmath.pi*abs(MZ)**3)',
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

Decay_Zp = Decay(name = 'Decay_Zp',
                 particle = P.Zp,
                 partial_widths = {(P.b,P.b__tilde__):'(MZp**2*((6*ee**2*gZpdL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpdR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.c,P.c__tilde__):'(MZp**2*((6*ee**2*gZpuL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpuR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.d,P.d__tilde__):'(MZp**2*((6*ee**2*gZpdL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpdR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.e__minus__,P.e__plus__):'(MZp**2*((2*ee**2*gZpeL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpeR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.mu__minus__,P.mu__plus__):'(MZp**2*((2*ee**2*gZpeL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpeR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.s,P.s__tilde__):'(MZp**2*((6*ee**2*gZpdL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpdR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.t,P.t__tilde__):'(((-6*ee**2*gZpuL**2*kL**2*MT**2)/(cw**2*sw**2) + (36*ee**2*gZpuL*gZpuR*kL**2*MT**2)/(cw**2*sw**2) - (6*ee**2*gZpuR**2*kL**2*MT**2)/(cw**2*sw**2) + (6*ee**2*gZpuL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpuR**2*kL**2*MZp**2)/(cw**2*sw**2))*cmath.sqrt(-4*MT**2*MZp**2 + MZp**4))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.ta__minus__,P.ta__plus__):'(MZp**2*((2*ee**2*gZpeL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpeR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.u,P.u__tilde__):'(MZp**2*((6*ee**2*gZpuL**2*kL**2*MZp**2)/(cw**2*sw**2) + (6*ee**2*gZpuR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.ve,P.ve__tilde__):'(MZp**2*((2*ee**2*gZpvL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpvR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.vm,P.vm__tilde__):'(MZp**2*((2*ee**2*gZpvL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpvR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)',
                                   (P.vt,P.vt__tilde__):'(MZp**2*((2*ee**2*gZpvL**2*kL**2*MZp**2)/(cw**2*sw**2) + (2*ee**2*gZpvR**2*kL**2*MZp**2)/(cw**2*sw**2)))/(48.*cmath.pi*abs(MZp)**3)'})

