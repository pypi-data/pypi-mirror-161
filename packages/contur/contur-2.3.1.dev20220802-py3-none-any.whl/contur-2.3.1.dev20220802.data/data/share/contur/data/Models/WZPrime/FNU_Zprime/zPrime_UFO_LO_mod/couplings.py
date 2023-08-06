# This file was automatically created by FeynRules 2.3.3
# Mathematica version: 11.3.0 for Linux x86 (64-bit) (March 7, 2018)
# Date: Mon 15 Jul 2019 15:02:48


from .object_library import all_couplings, Coupling

from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# custom UFO pimping
# up-type quark vector
GC_81 = Coupling(name = 'GC_81',
                value = '(5/18)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                order = {'QED':1})
# up-type quark axial times (-1)
GC_82 = Coupling(name = 'GC_82',
                value = '-(1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                order = {'QED':1})
# down-type quark vector
GC_83 = Coupling(name = 'GC_83',
                value = '(-1/18)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                order = {'QED':1})
# down-type quark axial times (-1)
GC_84 = Coupling(name = 'GC_84',
                value = '(1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                order = {'QED':1})

# modified lepton coupling
# e
GC_9 = Coupling(name = 'GC_9',
                value = '-(complex(0,1)*g1p*gAl1x1) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                order = {'QED':1})
GC_18 = Coupling(name = 'GC_18',
                 value = 'complex(0,1)*g1p*gVl1x1 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})

# nu e
GC_19 = Coupling(name = 'GC_19',
                 value = '-(complex(0,1)*g1p*gAl1x1) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp) + complex(0,1)*g1p*gVl1x1 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})

# mu
GC_13 = Coupling(name = 'GC_13',
                 value = '-(complex(0,1)*g1p*gAl2x2) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})

GC_26 = Coupling(name = 'GC_26',
                 value = 'complex(0,1)*g1p*gVl2x2 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})
# nu mu
GC_27 = Coupling(name = 'GC_27',
                 value = '-(complex(0,1)*g1p*gAl2x2) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp) + complex(0,1)*g1p*gVl2x2 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})
# tau
GC_17 = Coupling(name = 'GC_17',
                 value = '-(complex(0,1)*g1p*gAl3x3) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})

GC_34 = Coupling(name = 'GC_34',
                 value = 'complex(0,1)*g1p*gVl3x3 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})

# nu tau
GC_35 = Coupling(name = 'GC_35',
                 value = '-(complex(0,1)*g1p*gAl3x3) + (1/6)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp) + complex(0,1)*g1p*gVl3x3 + (-1/2)*(g1p*aEW*complex(0,1))/((1-sw2)*cmath.pi)*(gVl1x1+gVl2x2+gVl3x3)*cmath.log(UVcut/MZp)',
                 order = {'QED':1})


GC_1 = Coupling(name = 'GC_1',
                value = '-(ee*complex(0,1))/3.',
                order = {'QED':1})

GC_2 = Coupling(name = 'GC_2',
                value = '(2*ee*complex(0,1))/3.',
                order = {'QED':1})

GC_3 = Coupling(name = 'GC_3',
                value = '-(ee*complex(0,1))',
                order = {'QED':1})

GC_4 = Coupling(name = 'GC_4',
                value = 'ee*complex(0,1)',
                order = {'QED':1})

GC_5 = Coupling(name = 'GC_5',
                value = 'ee**2*complex(0,1)',
                order = {'QED':2})

GC_6 = Coupling(name = 'GC_6',
                value = '-G',
                order = {'QCD':1})

GC_7 = Coupling(name = 'GC_7',
                value = 'complex(0,1)*G',
                order = {'QCD':1})

GC_8 = Coupling(name = 'GC_8',
                value = 'complex(0,1)*G**2',
                order = {'QCD':2})

#GC_9 = Coupling(name = 'GC_9',
#                value = '-(complex(0,1)*g1p*gAl1x1)',
#                order = {'QED':1})

GC_10 = Coupling(name = 'GC_10',
                 value = '-(complex(0,1)*g1p*gAl1x2)',
                 order = {'QED':1})

GC_11 = Coupling(name = 'GC_11',
                 value = '-(complex(0,1)*g1p*gAl1x3)',
                 order = {'QED':1})

GC_12 = Coupling(name = 'GC_12',
                 value = '-(complex(0,1)*g1p*gAl2x1)',
                 order = {'QED':1})

#GC_13 = Coupling(name = 'GC_13',
#                 value = '-(complex(0,1)*g1p*gAl2x2)',
#                 order = {'QED':1})

GC_14 = Coupling(name = 'GC_14',
                 value = '-(complex(0,1)*g1p*gAl2x3)',
                 order = {'QED':1})

GC_15 = Coupling(name = 'GC_15',
                 value = '-(complex(0,1)*g1p*gAl3x1)',
                 order = {'QED':1})

GC_16 = Coupling(name = 'GC_16',
                 value = '-(complex(0,1)*g1p*gAl3x2)',
                 order = {'QED':1})

#GC_17 = Coupling(name = 'GC_17',
#                 value = '-(complex(0,1)*g1p*gAl3x3)',
#                 order = {'QED':1})

#GC_18 = Coupling(name = 'GC_18',
#                 value = 'complex(0,1)*g1p*gVl1x1',
#                 order = {'QED':1})
#
#GC_19 = Coupling(name = 'GC_19',
#                 value = '-(complex(0,1)*g1p*gAl1x1) + complex(0,1)*g1p*gVl1x1',
#                 order = {'QED':1})

GC_20 = Coupling(name = 'GC_20',
                 value = 'complex(0,1)*g1p*gVl1x2',
                 order = {'QED':1})

GC_21 = Coupling(name = 'GC_21',
                 value = '-(complex(0,1)*g1p*gAl1x2) + complex(0,1)*g1p*gVl1x2',
                 order = {'QED':1})

GC_22 = Coupling(name = 'GC_22',
                 value = 'complex(0,1)*g1p*gVl1x3',
                 order = {'QED':1})

GC_23 = Coupling(name = 'GC_23',
                 value = '-(complex(0,1)*g1p*gAl1x3) + complex(0,1)*g1p*gVl1x3',
                 order = {'QED':1})

GC_24 = Coupling(name = 'GC_24',
                 value = 'complex(0,1)*g1p*gVl2x1',
                 order = {'QED':1})

GC_25 = Coupling(name = 'GC_25',
                 value = '-(complex(0,1)*g1p*gAl2x1) + complex(0,1)*g1p*gVl2x1',
                 order = {'QED':1})

#GC_26 = Coupling(name = 'GC_26',
#                 value = 'complex(0,1)*g1p*gVl2x2',
#                 order = {'QED':1})
#
#GC_27 = Coupling(name = 'GC_27',
#                 value = '-(complex(0,1)*g1p*gAl2x2) + complex(0,1)*g1p*gVl2x2',
#                 order = {'QED':1})

GC_28 = Coupling(name = 'GC_28',
                 value = 'complex(0,1)*g1p*gVl2x3',
                 order = {'QED':1})

GC_29 = Coupling(name = 'GC_29',
                 value = '-(complex(0,1)*g1p*gAl2x3) + complex(0,1)*g1p*gVl2x3',
                 order = {'QED':1})

GC_30 = Coupling(name = 'GC_30',
                 value = 'complex(0,1)*g1p*gVl3x1',
                 order = {'QED':1})

GC_31 = Coupling(name = 'GC_31',
                 value = '-(complex(0,1)*g1p*gAl3x1) + complex(0,1)*g1p*gVl3x1',
                 order = {'QED':1})

GC_32 = Coupling(name = 'GC_32',
                 value = 'complex(0,1)*g1p*gVl3x2',
                 order = {'QED':1})

GC_33 = Coupling(name = 'GC_33',
                 value = '-(complex(0,1)*g1p*gAl3x2) + complex(0,1)*g1p*gVl3x2',
                 order = {'QED':1})

#GC_34 = Coupling(name = 'GC_34',
#                 value = 'complex(0,1)*g1p*gVl3x3',
#                 order = {'QED':1})

#GC_35 = Coupling(name = 'GC_35',
#                 value = '-(complex(0,1)*g1p*gAl3x3) + complex(0,1)*g1p*gVl3x3',
#                 order = {'QED':1})

GC_36 = Coupling(name = 'GC_36',
                 value = '-6*complex(0,1)*lam',
                 order = {'QED':2})

GC_37 = Coupling(name = 'GC_37',
                 value = '(ee**2*complex(0,1))/(2.*sw**2)',
                 order = {'QED':2})

GC_38 = Coupling(name = 'GC_38',
                 value = '-((ee**2*complex(0,1))/sw**2)',
                 order = {'QED':2})

GC_39 = Coupling(name = 'GC_39',
                 value = '(cw**2*ee**2*complex(0,1))/sw**2',
                 order = {'QED':2})

GC_40 = Coupling(name = 'GC_40',
                 value = '(ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_41 = Coupling(name = 'GC_41',
                 value = '(CKM1x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_42 = Coupling(name = 'GC_42',
                 value = '(CKM1x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_43 = Coupling(name = 'GC_43',
                 value = '(CKM1x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_44 = Coupling(name = 'GC_44',
                 value = '(CKM2x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_45 = Coupling(name = 'GC_45',
                 value = '(CKM2x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_46 = Coupling(name = 'GC_46',
                 value = '(CKM2x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_47 = Coupling(name = 'GC_47',
                 value = '(CKM3x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_48 = Coupling(name = 'GC_48',
                 value = '(CKM3x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_49 = Coupling(name = 'GC_49',
                 value = '(CKM3x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_50 = Coupling(name = 'GC_50',
                 value = '(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_51 = Coupling(name = 'GC_51',
                 value = '(-2*cw*ee**2*complex(0,1))/sw',
                 order = {'QED':2})

GC_52 = Coupling(name = 'GC_52',
                 value = '(ee*complex(0,1)*sw)/(3.*cw)',
                 order = {'QED':1})

GC_53 = Coupling(name = 'GC_53',
                 value = '(-2*ee*complex(0,1)*sw)/(3.*cw)',
                 order = {'QED':1})

GC_54 = Coupling(name = 'GC_54',
                 value = '(ee*complex(0,1)*sw)/cw',
                 order = {'QED':1})

GC_55 = Coupling(name = 'GC_55',
                 value = '-(cw*ee*complex(0,1))/(2.*sw) - (ee*complex(0,1)*sw)/(6.*cw)',
                 order = {'QED':1})

GC_56 = Coupling(name = 'GC_56',
                 value = '(cw*ee*complex(0,1))/(2.*sw) - (ee*complex(0,1)*sw)/(6.*cw)',
                 order = {'QED':1})

GC_57 = Coupling(name = 'GC_57',
                 value = '-(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_58 = Coupling(name = 'GC_58',
                 value = '(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_59 = Coupling(name = 'GC_59',
                 value = 'ee**2*complex(0,1) + (cw**2*ee**2*complex(0,1))/(2.*sw**2) + (ee**2*complex(0,1)*sw**2)/(2.*cw**2)',
                 order = {'QED':2})

GC_60 = Coupling(name = 'GC_60',
                 value = '-6*complex(0,1)*lam*vev',
                 order = {'QED':1})

GC_61 = Coupling(name = 'GC_61',
                 value = '(ee**2*complex(0,1)*vev)/(2.*sw**2)',
                 order = {'QED':1})

GC_62 = Coupling(name = 'GC_62',
                 value = 'ee**2*complex(0,1)*vev + (cw**2*ee**2*complex(0,1)*vev)/(2.*sw**2) + (ee**2*complex(0,1)*sw**2*vev)/(2.*cw**2)',
                 order = {'QED':1})

GC_63 = Coupling(name = 'GC_63',
                 value = '-((complex(0,1)*yb)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_64 = Coupling(name = 'GC_64',
                 value = '-((complex(0,1)*yc)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_65 = Coupling(name = 'GC_65',
                 value = '-((complex(0,1)*ydo)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_66 = Coupling(name = 'GC_66',
                 value = '-((complex(0,1)*ye)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_67 = Coupling(name = 'GC_67',
                 value = '-((complex(0,1)*ym)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_68 = Coupling(name = 'GC_68',
                 value = '-((complex(0,1)*ys)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_69 = Coupling(name = 'GC_69',
                 value = '-((complex(0,1)*yt)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_70 = Coupling(name = 'GC_70',
                 value = '-((complex(0,1)*ytau)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_71 = Coupling(name = 'GC_71',
                 value = '-((complex(0,1)*yup)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_72 = Coupling(name = 'GC_72',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_73 = Coupling(name = 'GC_73',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_74 = Coupling(name = 'GC_74',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_75 = Coupling(name = 'GC_75',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_76 = Coupling(name = 'GC_76',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_77 = Coupling(name = 'GC_77',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_78 = Coupling(name = 'GC_78',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_79 = Coupling(name = 'GC_79',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_80 = Coupling(name = 'GC_80',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

