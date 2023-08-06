# This file was automatically created by FeynRules 2.3.47
# Mathematica version: 12.2.0 for Mac OS X x86 (64-bit) (December 12, 2020)
# Date: Fri 30 Jul 2021 09:56:21



from .object_library import all_parameters, Parameter


from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
gzp = Parameter(name = 'gzp',
                nature = 'external',
                type = 'real',
                value = 0.35,
                texname = 'g_F',
                lhablock = 'newinputs',
                lhacode = [ 1 ])

tsb = Parameter(name = 'tsb',
                nature = 'external',
                type = 'real',
                value = 0.1,
                texname = '\\theta _{\\text{sb}}',
                lhablock = 'newinputs',
                lhacode = [ 2 ])

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

ymdo = Parameter(name = 'ymdo',
                 nature = 'external',
                 type = 'real',
                 value = 0.00504,
                 texname = '\\text{ymdo}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 1 ])

ymup = Parameter(name = 'ymup',
                 nature = 'external',
                 type = 'real',
                 value = 0.0025499999999999997,
                 texname = '\\text{ymup}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 2 ])

yms = Parameter(name = 'yms',
                nature = 'external',
                type = 'real',
                value = 0.101,
                texname = '\\text{yms}',
                lhablock = 'YUKAWA',
                lhacode = [ 3 ])

ymc = Parameter(name = 'ymc',
                nature = 'external',
                type = 'real',
                value = 1.27,
                texname = '\\text{ymc}',
                lhablock = 'YUKAWA',
                lhacode = [ 4 ])

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

yme = Parameter(name = 'yme',
                nature = 'external',
                type = 'real',
                value = 0.0005110000000000001,
                texname = '\\text{yme}',
                lhablock = 'YUKAWA',
                lhacode = [ 11 ])

ymm = Parameter(name = 'ymm',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{ymm}',
                lhablock = 'YUKAWA',
                lhacode = [ 13 ])

ymtau = Parameter(name = 'ymtau',
                  nature = 'external',
                  type = 'real',
                  value = 1.777,
                  texname = '\\text{ymtau}',
                  lhablock = 'YUKAWA',
                  lhacode = [ 15 ])

Null = Parameter(name = 'Null',
                 nature = 'external',
                 type = 'real',
                 value = 1,
                 texname = '\\text{Null}',
                 lhablock = 'FRBlock',
                 lhacode = [ 1 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

MZp = Parameter(name = 'MZp',
                nature = 'external',
                type = 'real',
                value = 1000.,
                texname = '\\text{MZp}',
                lhablock = 'MASS',
                lhacode = [ 32 ])

Me = Parameter(name = 'Me',
               nature = 'external',
               type = 'real',
               value = 0.0005110000000000001,
               texname = '\\text{Me}',
               lhablock = 'MASS',
               lhacode = [ 11 ])

MMU = Parameter(name = 'MMU',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{MMU}',
                lhablock = 'MASS',
                lhacode = [ 13 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MU = Parameter(name = 'MU',
               nature = 'external',
               type = 'real',
               value = 0.0025499999999999997,
               texname = 'M',
               lhablock = 'MASS',
               lhacode = [ 2 ])

MC = Parameter(name = 'MC',
               nature = 'external',
               type = 'real',
               value = 1.27,
               texname = '\\text{MC}',
               lhablock = 'MASS',
               lhacode = [ 4 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MD = Parameter(name = 'MD',
               nature = 'external',
               type = 'real',
               value = 0.00504,
               texname = '\\text{MD}',
               lhablock = 'MASS',
               lhacode = [ 1 ])

MS = Parameter(name = 'MS',
               nature = 'external',
               type = 'real',
               value = 0.101,
               texname = '\\text{MS}',
               lhablock = 'MASS',
               lhacode = [ 3 ])

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

MsF = Parameter(name = 'MsF',
                nature = 'external',
                type = 'real',
                value = 1000.,
                texname = '\\text{MsF}',
                lhablock = 'MASS',
                lhacode = [ 125 ])

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

WZp = Parameter(name = 'WZp',
                nature = 'external',
                type = 'real',
                value = 10.,
                texname = '\\text{WZp}',
                lhablock = 'DECAY',
                lhacode = [ 32 ])

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

WsF = Parameter(name = 'WsF',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{WsF}',
                lhablock = 'DECAY',
                lhacode = [ 125 ])

cabi = Parameter(name = 'cabi',
                 nature = 'internal',
                 type = 'real',
                 value = '0.227736',
                 texname = '\\theta _c')

lamCKM = Parameter(name = 'lamCKM',
                   nature = 'internal',
                   type = 'real',
                   value = '0.22506',
                   texname = '\\lambda')

ACKM = Parameter(name = 'ACKM',
                 nature = 'internal',
                 type = 'real',
                 value = '0.811',
                 texname = 'A')

rhobarCKM = Parameter(name = 'rhobarCKM',
                      nature = 'internal',
                      type = 'real',
                      value = '0.124',
                      texname = '\\rho')

etabarCKM = Parameter(name = 'etabarCKM',
                      nature = 'internal',
                      type = 'real',
                      value = '0.356',
                      texname = '\\eta')

s23CKM = Parameter(name = 's23CKM',
                   nature = 'internal',
                   type = 'real',
                   value = '0.0411',
                   texname = '\\text{s23}')

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

vevF = Parameter(name = 'vevF',
                 nature = 'internal',
                 type = 'real',
                 value = '1000.',
                 texname = '\\text{vevF}')

Xi1x1 = Parameter(name = 'Xi1x1',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi1x1}')

Xi1x2 = Parameter(name = 'Xi1x2',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi1x2}')

Xi1x3 = Parameter(name = 'Xi1x3',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi1x3}')

Xi2x1 = Parameter(name = 'Xi2x1',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi2x1}')

Xi2x2 = Parameter(name = 'Xi2x2',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi2x2}')

Xi2x3 = Parameter(name = 'Xi2x3',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi2x3}')

Xi3x1 = Parameter(name = 'Xi3x1',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi3x1}')

Xi3x2 = Parameter(name = 'Xi3x2',
                  nature = 'internal',
                  type = 'real',
                  value = '0',
                  texname = '\\text{Xi3x2}')

Xi3x3 = Parameter(name = 'Xi3x3',
                  nature = 'internal',
                  type = 'real',
                  value = '1',
                  texname = '\\text{Xi3x3}')

Psi1x1 = Parameter(name = 'Psi1x1',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi1x1}')

Psi1x2 = Parameter(name = 'Psi1x2',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi1x2}')

Psi1x3 = Parameter(name = 'Psi1x3',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi1x3}')

Psi2x1 = Parameter(name = 'Psi2x1',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi2x1}')

Psi2x2 = Parameter(name = 'Psi2x2',
                   nature = 'internal',
                   type = 'real',
                   value = '1',
                   texname = '\\text{Psi2x2}')

Psi2x3 = Parameter(name = 'Psi2x3',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi2x3}')

Psi3x1 = Parameter(name = 'Psi3x1',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi3x1}')

Psi3x2 = Parameter(name = 'Psi3x2',
                   nature = 'internal',
                   type = 'real',
                   value = '0',
                   texname = '\\text{Psi3x2}')

Psi3x3 = Parameter(name = 'Psi3x3',
                   nature = 'internal',
                   type = 'real',
                   value = '-2.5',
                   texname = '\\text{Psi3x3}')

Omega1x1 = Parameter(name = 'Omega1x1',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega1x1}')

Omega1x2 = Parameter(name = 'Omega1x2',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega1x2}')

Omega1x3 = Parameter(name = 'Omega1x3',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega1x3}')

Omega2x1 = Parameter(name = 'Omega2x1',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega2x1}')

Omega2x2 = Parameter(name = 'Omega2x2',
                     nature = 'internal',
                     type = 'real',
                     value = '1',
                     texname = '\\text{Omega2x2}')

Omega2x3 = Parameter(name = 'Omega2x3',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega2x3}')

Omega3x1 = Parameter(name = 'Omega3x1',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega3x1}')

Omega3x2 = Parameter(name = 'Omega3x2',
                     nature = 'internal',
                     type = 'real',
                     value = '0',
                     texname = '\\text{Omega3x2}')

Omega3x3 = Parameter(name = 'Omega3x3',
                     nature = 'internal',
                     type = 'real',
                     value = '-0.625',
                     texname = '\\text{Omega3x3}')

Cd1x1 = Parameter(name = 'Cd1x1',
                  nature = 'internal',
                  type = 'complex',
                  value = '0',
                  texname = '\\text{Cd1x1}')

Cd1x2 = Parameter(name = 'Cd1x2',
                  nature = 'internal',
                  type = 'complex',
                  value = '0',
                  texname = '\\text{Cd1x2}')

Cd1x3 = Parameter(name = 'Cd1x3',
                  nature = 'internal',
                  type = 'complex',
                  value = '0',
                  texname = '\\text{Cd1x3}')

Cd2x1 = Parameter(name = 'Cd2x1',
                  nature = 'internal',
                  type = 'complex',
                  value = '0',
                  texname = '\\text{Cd2x1}')

Cd2x2 = Parameter(name = 'Cd2x2',
                  nature = 'internal',
                  type = 'complex',
                  value = 'cmath.sin(tsb)**2',
                  texname = '\\text{Cd2x2}')

Cd2x3 = Parameter(name = 'Cd2x3',
                  nature = 'internal',
                  type = 'complex',
                  value = 'cmath.sin(2*tsb)/2.',
                  texname = '\\text{Cd2x3}')

Cd3x1 = Parameter(name = 'Cd3x1',
                  nature = 'internal',
                  type = 'complex',
                  value = '0',
                  texname = '\\text{Cd3x1}')

Cd3x2 = Parameter(name = 'Cd3x2',
                  nature = 'internal',
                  type = 'complex',
                  value = 'cmath.sin(2*tsb)/2.',
                  texname = '\\text{Cd3x2}')

Cd3x3 = Parameter(name = 'Cd3x3',
                  nature = 'internal',
                  type = 'complex',
                  value = 'cmath.cos(tsb)**2',
                  texname = '\\text{Cd3x3}')

c23CKM = Parameter(name = 'c23CKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'cmath.sqrt(1 - s23CKM**2)',
                   texname = '\\text{c23}')

MW = Parameter(name = 'MW',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(MZ**2/2. + cmath.sqrt(MZ**4/4. - (aEW*cmath.pi*MZ**2)/(Gf*cmath.sqrt(2))))',
               texname = 'M_W')

s12CKM = Parameter(name = 's12CKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'lamCKM',
                   texname = '\\text{s12}')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

c12CKM = Parameter(name = 'c12CKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'cmath.sqrt(1 - s12CKM**2)',
                   texname = '\\text{c12}')

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

s13CKM = Parameter(name = 's13CKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'abs((ACKM*c23CKM*lamCKM**3*(etabarCKM*complex(0,1) + rhobarCKM))/(c12CKM*(1 - (etabarCKM*complex(0,1) + rhobarCKM)*s23CKM**2)))',
                   texname = '\\text{s13}')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

c13CKM = Parameter(name = 'c13CKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'cmath.sqrt(1 - s13CKM**2)',
                   texname = '\\text{c13}')

delCKM = Parameter(name = 'delCKM',
                   nature = 'internal',
                   type = 'real',
                   value = 'cmath.asin(im((ACKM*c23CKM*lamCKM**3*(etabarCKM*complex(0,1) + rhobarCKM))/(c12CKM*(1 - (etabarCKM*complex(0,1) + rhobarCKM)*s23CKM**2)))/s13CKM)',
                   texname = '\\delta')

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
                texname = '\\text{vev}')

CKM1x1 = Parameter(name = 'CKM1x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c12CKM*c13CKM',
                   texname = '\\text{CKM1x1}')

CKM1x2 = Parameter(name = 'CKM1x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c13CKM*s12CKM',
                   texname = '\\text{CKM1x2}')

CKM1x3 = Parameter(name = 'CKM1x3',
                   nature = 'internal',
                   type = 'complex',
                   value = 's13CKM*cmath.exp(-(delCKM*complex(0,1)))',
                   texname = '\\text{CKM1x3}')

CKM2x1 = Parameter(name = 'CKM2x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '-(c23CKM*s12CKM) - c12CKM*s13CKM*s23CKM*cmath.exp(delCKM*complex(0,1))',
                   texname = '\\text{CKM2x1}')

CKM2x2 = Parameter(name = 'CKM2x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c12CKM*c23CKM - s12CKM*s13CKM*s23CKM*cmath.exp(delCKM*complex(0,1))',
                   texname = '\\text{CKM2x2}')

CKM2x3 = Parameter(name = 'CKM2x3',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c13CKM*s23CKM',
                   texname = '\\text{CKM2x3}')

CKM3x1 = Parameter(name = 'CKM3x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 's12CKM*s23CKM - c12CKM*c23CKM*s13CKM*cmath.exp(delCKM*complex(0,1))',
                   texname = '\\text{CKM3x1}')

CKM3x2 = Parameter(name = 'CKM3x2',
                   nature = 'internal',
                   type = 'complex',
                   value = '-(c12CKM*s23CKM) - c23CKM*s12CKM*s13CKM*cmath.exp(delCKM*complex(0,1))',
                   texname = '\\text{CKM3x2}')

CKM3x3 = Parameter(name = 'CKM3x3',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c13CKM*c23CKM',
                   texname = '\\text{CKM3x3}')

sz = Parameter(name = 'sz',
               nature = 'internal',
               type = 'real',
               value = '(gzp*MZ**2)/(MZp**2*cmath.sqrt(g1**2 + gw**2))',
               texname = 's_z')

lam = Parameter(name = 'lam',
                nature = 'internal',
                type = 'real',
                value = 'MH**2/(2.*vev**2)',
                texname = '\\text{lam}')

yb = Parameter(name = 'yb',
               nature = 'internal',
               type = 'real',
               value = '(ymb*cmath.sqrt(2))/vev',
               texname = '\\text{yb}')

yc = Parameter(name = 'yc',
               nature = 'internal',
               type = 'real',
               value = '(ymc*cmath.sqrt(2))/vev',
               texname = '\\text{yc}')

ydo = Parameter(name = 'ydo',
                nature = 'internal',
                type = 'real',
                value = '(ymdo*cmath.sqrt(2))/vev',
                texname = '\\text{ydo}')

ye = Parameter(name = 'ye',
               nature = 'internal',
               type = 'real',
               value = '(yme*cmath.sqrt(2))/vev',
               texname = '\\text{ye}')

ym = Parameter(name = 'ym',
               nature = 'internal',
               type = 'real',
               value = '(ymm*cmath.sqrt(2))/vev',
               texname = '\\text{ym}')

ys = Parameter(name = 'ys',
               nature = 'internal',
               type = 'real',
               value = '(yms*cmath.sqrt(2))/vev',
               texname = '\\text{ys}')

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

yup = Parameter(name = 'yup',
                nature = 'internal',
                type = 'real',
                value = '(ymup*cmath.sqrt(2))/vev',
                texname = '\\text{yup}')

cz = Parameter(name = 'cz',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(1 - sz**2)',
               texname = 'c_z')

muH = Parameter(name = 'muH',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(lam*vev**2)',
                texname = '\\mu')

I1a11 = Parameter(name = 'I1a11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM1x1*complexconjugate(CKM1x1) + Cd2x1*CKM1x2*complexconjugate(CKM1x1) + Cd3x1*CKM1x3*complexconjugate(CKM1x1) + Cd1x2*CKM1x1*complexconjugate(CKM1x2) + Cd2x2*CKM1x2*complexconjugate(CKM1x2) + Cd3x2*CKM1x3*complexconjugate(CKM1x2) + Cd1x3*CKM1x1*complexconjugate(CKM1x3) + Cd2x3*CKM1x2*complexconjugate(CKM1x3) + Cd3x3*CKM1x3*complexconjugate(CKM1x3)',
                  texname = '\\text{I1a11}')

I1a12 = Parameter(name = 'I1a12',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM1x1*complexconjugate(CKM2x1) + Cd2x1*CKM1x2*complexconjugate(CKM2x1) + Cd3x1*CKM1x3*complexconjugate(CKM2x1) + Cd1x2*CKM1x1*complexconjugate(CKM2x2) + Cd2x2*CKM1x2*complexconjugate(CKM2x2) + Cd3x2*CKM1x3*complexconjugate(CKM2x2) + Cd1x3*CKM1x1*complexconjugate(CKM2x3) + Cd2x3*CKM1x2*complexconjugate(CKM2x3) + Cd3x3*CKM1x3*complexconjugate(CKM2x3)',
                  texname = '\\text{I1a12}')

I1a13 = Parameter(name = 'I1a13',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM1x1*complexconjugate(CKM3x1) + Cd2x1*CKM1x2*complexconjugate(CKM3x1) + Cd3x1*CKM1x3*complexconjugate(CKM3x1) + Cd1x2*CKM1x1*complexconjugate(CKM3x2) + Cd2x2*CKM1x2*complexconjugate(CKM3x2) + Cd3x2*CKM1x3*complexconjugate(CKM3x2) + Cd1x3*CKM1x1*complexconjugate(CKM3x3) + Cd2x3*CKM1x2*complexconjugate(CKM3x3) + Cd3x3*CKM1x3*complexconjugate(CKM3x3)',
                  texname = '\\text{I1a13}')

I1a21 = Parameter(name = 'I1a21',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM2x1*complexconjugate(CKM1x1) + Cd2x1*CKM2x2*complexconjugate(CKM1x1) + Cd3x1*CKM2x3*complexconjugate(CKM1x1) + Cd1x2*CKM2x1*complexconjugate(CKM1x2) + Cd2x2*CKM2x2*complexconjugate(CKM1x2) + Cd3x2*CKM2x3*complexconjugate(CKM1x2) + Cd1x3*CKM2x1*complexconjugate(CKM1x3) + Cd2x3*CKM2x2*complexconjugate(CKM1x3) + Cd3x3*CKM2x3*complexconjugate(CKM1x3)',
                  texname = '\\text{I1a21}')

I1a22 = Parameter(name = 'I1a22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM2x1*complexconjugate(CKM2x1) + Cd2x1*CKM2x2*complexconjugate(CKM2x1) + Cd3x1*CKM2x3*complexconjugate(CKM2x1) + Cd1x2*CKM2x1*complexconjugate(CKM2x2) + Cd2x2*CKM2x2*complexconjugate(CKM2x2) + Cd3x2*CKM2x3*complexconjugate(CKM2x2) + Cd1x3*CKM2x1*complexconjugate(CKM2x3) + Cd2x3*CKM2x2*complexconjugate(CKM2x3) + Cd3x3*CKM2x3*complexconjugate(CKM2x3)',
                  texname = '\\text{I1a22}')

I1a23 = Parameter(name = 'I1a23',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM2x1*complexconjugate(CKM3x1) + Cd2x1*CKM2x2*complexconjugate(CKM3x1) + Cd3x1*CKM2x3*complexconjugate(CKM3x1) + Cd1x2*CKM2x1*complexconjugate(CKM3x2) + Cd2x2*CKM2x2*complexconjugate(CKM3x2) + Cd3x2*CKM2x3*complexconjugate(CKM3x2) + Cd1x3*CKM2x1*complexconjugate(CKM3x3) + Cd2x3*CKM2x2*complexconjugate(CKM3x3) + Cd3x3*CKM2x3*complexconjugate(CKM3x3)',
                  texname = '\\text{I1a23}')

I1a31 = Parameter(name = 'I1a31',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM3x1*complexconjugate(CKM1x1) + Cd2x1*CKM3x2*complexconjugate(CKM1x1) + Cd3x1*CKM3x3*complexconjugate(CKM1x1) + Cd1x2*CKM3x1*complexconjugate(CKM1x2) + Cd2x2*CKM3x2*complexconjugate(CKM1x2) + Cd3x2*CKM3x3*complexconjugate(CKM1x2) + Cd1x3*CKM3x1*complexconjugate(CKM1x3) + Cd2x3*CKM3x2*complexconjugate(CKM1x3) + Cd3x3*CKM3x3*complexconjugate(CKM1x3)',
                  texname = '\\text{I1a31}')

I1a32 = Parameter(name = 'I1a32',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM3x1*complexconjugate(CKM2x1) + Cd2x1*CKM3x2*complexconjugate(CKM2x1) + Cd3x1*CKM3x3*complexconjugate(CKM2x1) + Cd1x2*CKM3x1*complexconjugate(CKM2x2) + Cd2x2*CKM3x2*complexconjugate(CKM2x2) + Cd3x2*CKM3x3*complexconjugate(CKM2x2) + Cd1x3*CKM3x1*complexconjugate(CKM2x3) + Cd2x3*CKM3x2*complexconjugate(CKM2x3) + Cd3x3*CKM3x3*complexconjugate(CKM2x3)',
                  texname = '\\text{I1a32}')

I1a33 = Parameter(name = 'I1a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'Cd1x1*CKM3x1*complexconjugate(CKM3x1) + Cd2x1*CKM3x2*complexconjugate(CKM3x1) + Cd3x1*CKM3x3*complexconjugate(CKM3x1) + Cd1x2*CKM3x1*complexconjugate(CKM3x2) + Cd2x2*CKM3x2*complexconjugate(CKM3x2) + Cd3x2*CKM3x3*complexconjugate(CKM3x2) + Cd1x3*CKM3x1*complexconjugate(CKM3x3) + Cd2x3*CKM3x2*complexconjugate(CKM3x3) + Cd3x3*CKM3x3*complexconjugate(CKM3x3)',
                  texname = '\\text{I1a33}')

