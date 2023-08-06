# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.0.1 for Linux x86 (64-bit) (January 29, 2022)
# Date: Fri 8 Apr 2022 19:16:51



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
dmsq21 = Parameter(name = 'dmsq21',
                   nature = 'external',
                   type = 'real',
                   value = 7.39e-23,
                   texname = '\\text{$\\Delta $m}_{21}^2',
                   lhablock = 'MNU',
                   lhacode = [ 2 ])

dmsq31 = Parameter(name = 'dmsq31',
                   nature = 'external',
                   type = 'real',
                   value = 2.5e-21,
                   texname = '\\text{$\\Delta $m}_{31}^2',
                   lhablock = 'MNU',
                   lhacode = [ 3 ])

th12 = Parameter(name = 'th12',
                 nature = 'external',
                 type = 'real',
                 value = 0.59,
                 texname = '\\theta _{12}',
                 lhablock = 'PMNS',
                 lhacode = [ 1 ])

th23 = Parameter(name = 'th23',
                 nature = 'external',
                 type = 'real',
                 value = 0.87,
                 texname = '\\theta _{23}',
                 lhablock = 'PMNS',
                 lhacode = [ 2 ])

th13 = Parameter(name = 'th13',
                 nature = 'external',
                 type = 'real',
                 value = 0.15,
                 texname = '\\theta _{13}',
                 lhablock = 'PMNS',
                 lhacode = [ 3 ])

delCP = Parameter(name = 'delCP',
                  nature = 'external',
                  type = 'real',
                  value = 0,
                  texname = '\\delta _{\\text{CP}}',
                  lhablock = 'PMNS',
                  lhacode = [ 4 ])

phiM1 = Parameter(name = 'phiM1',
                  nature = 'external',
                  type = 'real',
                  value = 0.,
                  texname = '\\phi _1',
                  lhablock = 'PMNS',
                  lhacode = [ 5 ])

phiM2 = Parameter(name = 'phiM2',
                  nature = 'external',
                  type = 'real',
                  value = 0.,
                  texname = '\\phi _2',
                  lhablock = 'PMNS',
                  lhacode = [ 6 ])

lamHD1 = Parameter(name = 'lamHD1',
                   nature = 'external',
                   type = 'real',
                   value = 0.1,
                   texname = '\\lambda _{\\text{h$\\Delta $1}}',
                   lhablock = 'QUARTICS',
                   lhacode = [ 1 ])

lamD1 = Parameter(name = 'lamD1',
                  nature = 'external',
                  type = 'real',
                  value = 0.11,
                  texname = '\\lambda _{\\text{$\\Delta $1}}',
                  lhablock = 'QUARTICS',
                  lhacode = [ 2 ])

lamD2 = Parameter(name = 'lamD2',
                  nature = 'external',
                  type = 'real',
                  value = 0.15,
                  texname = '\\lambda _{\\text{$\\Delta $1}}',
                  lhablock = 'QUARTICS',
                  lhacode = [ 3 ])

aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.9,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.0000116637,
               texname = 'G_f',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.1184,
               texname = '\\alpha _s',
               lhablock = 'SMINPUTS',
               lhacode = [ 3 ])

vevD = Parameter(name = 'vevD',
                 nature = 'external',
                 type = 'real',
                 value = 1.e-7,
                 texname = 'v_{\\Delta }',
                 lhablock = 'VEVDELTA',
                 lhacode = [ 1 ])

ymb = Parameter(name = 'ymb',
                nature = 'external',
                type = 'real',
                value = 4.7,
                texname = '\\text{ymb}',
                lhablock = 'YUKAWA',
                lhacode = [ 5 ])

ymt = Parameter(name = 'ymt',
                nature = 'external',
                type = 'real',
                value = 172,
                texname = '\\text{ymt}',
                lhablock = 'YUKAWA',
                lhacode = [ 6 ])

ymtau = Parameter(name = 'ymtau',
                  nature = 'external',
                  type = 'real',
                  value = 1.777,
                  texname = '\\text{ymtau}',
                  lhablock = 'YUKAWA',
                  lhacode = [ 15 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MB = Parameter(name = 'MB',
               nature = 'external',
               type = 'real',
               value = 4.7,
               texname = '\\text{MB}',
               lhablock = 'MASS',
               lhacode = [ 5 ])

MH = Parameter(name = 'MH',
               nature = 'external',
               type = 'real',
               value = 125,
               texname = '\\text{MH}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

Mv1 = Parameter(name = 'Mv1',
                nature = 'external',
                type = 'real',
                value = 5.e-11,
                texname = '\\text{Mv1}',
                lhablock = 'MASS',
                lhacode = [ 12 ])

MDP = Parameter(name = 'MDP',
                nature = 'external',
                type = 'real',
                value = 503.,
                texname = '\\text{MDP}',
                lhablock = 'MASS',
                lhacode = [ 38 ])

MDPP = Parameter(name = 'MDPP',
                 nature = 'external',
                 type = 'real',
                 value = 502.,
                 texname = '\\text{MDPP}',
                 lhablock = 'MASS',
                 lhacode = [ 61 ])

WZ = Parameter(name = 'WZ',
               nature = 'external',
               type = 'real',
               value = 2.4952,
               texname = '\\text{WZ}',
               lhablock = 'DECAY',
               lhacode = [ 23 ])

WW = Parameter(name = 'WW',
               nature = 'external',
               type = 'real',
               value = 2.085,
               texname = '\\text{WW}',
               lhablock = 'DECAY',
               lhacode = [ 24 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00407,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

WD0 = Parameter(name = 'WD0',
                nature = 'external',
                type = 'real',
                value = 0.00001017718,
                texname = '\\text{WD0}',
                lhablock = 'DECAY',
                lhacode = [ 44 ])

WDP = Parameter(name = 'WDP',
                nature = 'external',
                type = 'real',
                value = 0.0000101709,
                texname = '\\text{WDP}',
                lhablock = 'DECAY',
                lhacode = [ 38 ])

WDPP = Parameter(name = 'WDPP',
                 nature = 'external',
                 type = 'real',
                 value = 0.00001011029,
                 texname = '\\text{WDPP}',
                 lhablock = 'DECAY',
                 lhacode = [ 61 ])

Wchi = Parameter(name = 'Wchi',
                 nature = 'external',
                 type = 'real',
                 value = 0.00001017817,
                 texname = '\\text{Wchi}',
                 lhablock = 'DECAY',
                 lhacode = [ 62 ])

Mv2 = Parameter(name = 'Mv2',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(dmsq21 + Mv1**2)',
                texname = 'm_{\\text{$\\nu $2}}')

Mv3 = Parameter(name = 'Mv3',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(dmsq31 + Mv1**2)',
                texname = 'm_{\\text{$\\nu $3}}')

PMNS1x1 = Parameter(name = 'PMNS1x1',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.cos(th12)*cmath.cos(th13)',
                    texname = '\\text{PMNS1x1}')

PMNS1x2 = Parameter(name = 'PMNS1x2',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.cos(th13)*cmath.exp((complex(0,1)*phiM1)/2.)*cmath.sin(th12)',
                    texname = '\\text{PMNS1x2}')

PMNS1x3 = Parameter(name = 'PMNS1x3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.exp(complex(0,1)*(-delCP + phiM2/2.))*cmath.sin(th13)',
                    texname = '\\text{PMNS1x3}')

PMNS2x1 = Parameter(name = 'PMNS2x1',
                    nature = 'internal',
                    type = 'complex',
                    value = '-(cmath.cos(th23)*cmath.sin(th12)) - cmath.cos(th12)*cmath.exp(delCP*complex(0,1))*cmath.sin(th13)*cmath.sin(th23)',
                    texname = '\\text{PMNS2x1}')

PMNS2x2 = Parameter(name = 'PMNS2x2',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.exp((complex(0,1)*phiM1)/2.)*(cmath.cos(th12)*cmath.cos(th23) - cmath.exp(delCP*complex(0,1))*cmath.sin(th12)*cmath.sin(th13)*cmath.sin(th23))',
                    texname = '\\text{PMNS2x2}')

PMNS2x3 = Parameter(name = 'PMNS2x3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.cos(th13)*cmath.exp((complex(0,1)*phiM2)/2.)*cmath.sin(th23)',
                    texname = '\\text{PMNS2x3}')

PMNS3x1 = Parameter(name = 'PMNS3x1',
                    nature = 'internal',
                    type = 'complex',
                    value = '-(cmath.cos(th12)*cmath.cos(th23)*cmath.exp(delCP*complex(0,1))*cmath.sin(th13)) + cmath.sin(th12)*cmath.sin(th23)',
                    texname = '\\text{PMNS3x1}')

PMNS3x2 = Parameter(name = 'PMNS3x2',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.exp((complex(0,1)*phiM1)/2.)*(-(cmath.cos(th23)*cmath.exp(delCP*complex(0,1))*cmath.sin(th12)*cmath.sin(th13)) - cmath.cos(th12)*cmath.sin(th23))',
                    texname = '\\text{PMNS3x2}')

PMNS3x3 = Parameter(name = 'PMNS3x3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'cmath.cos(th13)*cmath.cos(th23)*cmath.exp((complex(0,1)*phiM2)/2.)',
                    texname = '\\text{PMNS3x3}')

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\alpha _{\\text{EW}}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

MW = Parameter(name = 'MW',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(MZ**2/2. + cmath.sqrt(MZ**4/4. - (aEW*cmath.pi*MZ**2)/(Gf*cmath.sqrt(2))))',
               texname = 'M_W')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

yDL1x1 = Parameter(name = 'yDL1x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '(Mv1*complexconjugate(PMNS1x1)**2 + Mv2*complexconjugate(PMNS1x2)**2 + Mv3*complexconjugate(PMNS1x3)**2)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL1x1}')

yDL1x2 = Parameter(name = 'yDL1x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS1x1*PMNS2x1 + Mv2*PMNS1x2*PMNS2x2 + Mv3*PMNS1x3*PMNS2x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL1x2}')

yDL1x3 = Parameter(name = 'yDL1x3',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS1x1*PMNS3x1 + Mv2*PMNS1x2*PMNS3x2 + Mv3*PMNS1x3*PMNS3x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL1x3}')

yDL2x1 = Parameter(name = 'yDL2x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS1x1*PMNS2x1 + Mv2*PMNS1x2*PMNS2x2 + Mv3*PMNS1x3*PMNS2x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL2x1}')

yDL2x2 = Parameter(name = 'yDL2x2',
                   nature = 'internal',
                   type = 'complex',
                   value = '(Mv1*complexconjugate(PMNS2x1)**2 + Mv2*complexconjugate(PMNS2x2)**2 + Mv3*complexconjugate(PMNS2x3)**2)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL2x2}')

yDL2x3 = Parameter(name = 'yDL2x3',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS2x1*PMNS3x1 + Mv2*PMNS2x2*PMNS3x2 + Mv3*PMNS2x3*PMNS3x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL2x3}')

yDL3x1 = Parameter(name = 'yDL3x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS1x1*PMNS3x1 + Mv2*PMNS1x2*PMNS3x2 + Mv3*PMNS1x3*PMNS3x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL3x1}')

yDL3x2 = Parameter(name = 'yDL3x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'complexconjugate(Mv1*PMNS2x1*PMNS3x1 + Mv2*PMNS2x2*PMNS3x2 + Mv3*PMNS2x3*PMNS3x3)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL3x2}')

yDL3x3 = Parameter(name = 'yDL3x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '(Mv1*complexconjugate(PMNS3x1)**2 + Mv2*complexconjugate(PMNS3x2)**2 + Mv3*complexconjugate(PMNS3x3)**2)/(vevD*cmath.sqrt(2))',
                   texname = '\\text{yDL3x3}')

sw2 = Parameter(name = 'sw2',
                nature = 'internal',
                type = 'real',
                value = '1 - MW**2/MZ**2',
                texname = '\\text{sw2}')

cw = Parameter(name = 'cw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(1 - sw2)',
               texname = 'c_w')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

g1 = Parameter(name = 'g1',
               nature = 'internal',
               type = 'real',
               value = 'ee/cw',
               texname = 'g_1')

gw = Parameter(name = 'gw',
               nature = 'internal',
               type = 'real',
               value = 'ee/sw',
               texname = 'g_w')

vev = Parameter(name = 'vev',
                nature = 'internal',
                type = 'real',
                value = '(2*MW*sw)/ee',
                texname = 'v')

mD2 = Parameter(name = 'mD2',
                nature = 'internal',
                type = 'real',
                value = 'MDPP**2 - (lamHD1*vev**2)/2. - lamD1*vevD**2',
                texname = 'm_{\\Delta }^2')

lamHD2 = Parameter(name = 'lamHD2',
                   nature = 'internal',
                   type = 'real',
                   value = '(4*(-MDPP**2 - lamD2*vevD**2 + MDP**2/(1 + (2*vevD**2)/vev**2)))/vev**2',
                   texname = '\\lambda _{\\text{h$\\Delta $2}}')

muHD = Parameter(name = 'muHD',
                 nature = 'internal',
                 type = 'real',
                 value = '-((vevD*(-2*MDP**2 + (MDPP**2 + lamD2*vevD**2)*(1 + (2*vevD**2)/vev**2))*cmath.sqrt(2))/(vev*(vev + (2*vevD**2)/vev)))',
                 texname = '\\mu _{\\text{h$\\Delta $}}')

yb = Parameter(name = 'yb',
               nature = 'internal',
               type = 'real',
               value = '(ymb*cmath.sqrt(2))/vev',
               texname = '\\text{yb}')

yt = Parameter(name = 'yt',
               nature = 'internal',
               type = 'real',
               value = '(ymt*cmath.sqrt(2))/vev',
               texname = '\\text{yt}')

ytau = Parameter(name = 'ytau',
                 nature = 'internal',
                 type = 'real',
                 value = '(ymtau*cmath.sqrt(2))/vev',
                 texname = '\\text{ytau}')

Mchi = Parameter(name = 'Mchi',
                 nature = 'internal',
                 type = 'real',
                 value = 'cmath.sqrt((1 + (4*vevD**2)/vev**2)*(2*mD2 + vev**2*(lamHD1 + lamHD2 + (2*(lamD1 + lamD2)*vevD**2)/vev**2)))/cmath.sqrt(2)',
                 texname = 'M_{\\chi }')

MD0 = Parameter(name = 'MD0',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(-((4*mD2**2*(1 + (4*vevD**2)/vev**2) + 4*mD2*vev**2*(lamHD1 + lamHD2 + (2*(lamD1 + lamD2)*vevD**2*(3 + (4*vevD**2)/vev**2))/vev**2) + vev**4*((lamHD1 + lamHD2)**2 + (12*(lamD1 + lamD2)*(lamHD1 + lamHD2)*vevD**2)/vev**2 + (4*(lamD1 + lamD2)**2*vevD**4*(9 + (4*vevD**2)/vev**2))/vev**4) - 2*MH**2*(2*mD2 + vev**2*(lamHD1 + lamHD2 + (6*(lamD1 + lamD2)*vevD**2)/vev**2)))/(-4*mD2 + 4*MH**2 - 2*vev**2*(lamHD1 + lamHD2 + (6*(lamD1 + lamD2)*vevD**2)/vev**2))))',
                texname = 'M_{\\Delta ^0}')

lamH = Parameter(name = 'lamH',
                 nature = 'internal',
                 type = 'real',
                 value = '(2*mD2*MH**2 - 2*MH**4 + (8*vevD**2*(mD2 + (lamD1 + lamD2)*vevD**2)**2)/vev**2 + MH**2*vev**2*(lamHD1 + lamHD2 + (6*(lamD1 + lamD2)*vevD**2)/vev**2))/(2.*vev**2*(2*mD2 - 2*MH**2 + vev**2*(lamHD1 + lamHD2 + (6*(lamD1 + lamD2)*vevD**2)/vev**2)))',
                 texname = '\\lambda _h')

muH2 = Parameter(name = 'muH2',
                 nature = 'internal',
                 type = 'real',
                 value = 'lamH*vev**2 - (vevD**2*(4*mD2 + vev**2*(lamHD1 + lamHD2 + (4*(lamD1 + lamD2)*vevD**2)/vev**2)))/(2.*vev**2)',
                 texname = '\\mu _H{}^2')

t2xi = Parameter(name = 't2xi',
                 nature = 'internal',
                 type = 'real',
                 value = '(8*vevD*(mD2 + (lamD1 + lamD2)*vevD**2))/(vev*(2*mD2 + vev**2*(-4*lamH + lamHD1 + lamHD2 + (6*(lamD1 + lamD2)*vevD**2)/vev**2)))',
                 texname = 't_{\\text{2$\\xi $}}')

cxi = Parameter(name = 'cxi',
                nature = 'internal',
                type = 'real',
                value = 'cmath.cos(cmath.atan(t2xi)/2.)',
                texname = 'c_{\\xi }')

sxi = Parameter(name = 'sxi',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sin(cmath.atan(t2xi)/2.)',
                texname = 's_{\\xi }')

