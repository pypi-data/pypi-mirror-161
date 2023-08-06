# This file was automatically created by FeynRules 2.3.3
# Mathematica version: 10.0 for Linux x86 (64-bit) (December 4, 2014)
# Date: Sat 17 Jun 2017 13:56:33



from .object_library import all_parameters, Parameter


from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
beta = Parameter(name = 'beta',
                 nature = 'external',
                 type = 'real',
                 value = 0.1,
                 texname = '\\beta',
                 lhablock = 'Higgs',
                 lhacode = [ 1 ])

mixh = Parameter(name = 'mixh',
                 nature = 'external',
                 type = 'real',
                 value = 0.3,
                 texname = '\\theta _{\\text{h1}}',
                 lhablock = 'Higgs',
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
               value = 0.000011663900000000002,
               texname = '\\text{Gf}',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.118,
               texname = '\\text{aS}',
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
                 value = 0.00255,
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
                value = 0.000511,
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

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

Me = Parameter(name = 'Me',
               nature = 'external',
               type = 'real',
               value = 0.000511,
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
               value = 0.00255,
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

mhc = Parameter(name = 'mhc',
                nature = 'external',
                type = 'real',
                value = 150,
                texname = '\\text{mhc}',
                lhablock = 'MASS',
                lhacode = [ 37 ])

mh1 = Parameter(name = 'mh1',
                nature = 'external',
                type = 'real',
                value = 120,
                texname = '\\text{mh1}',
                lhablock = 'MASS',
                lhacode = [ 25 ])

mh2 = Parameter(name = 'mh2',
                nature = 'external',
                type = 'real',
                value = 130,
                texname = '\\text{mh2}',
                lhablock = 'MASS',
                lhacode = [ 35 ])

mh3 = Parameter(name = 'mh3',
                nature = 'external',
                type = 'real',
                value = 140,
                texname = '\\text{mh3}',
                lhablock = 'MASS',
                lhacode = [ 36 ])

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

whc = Parameter(name = 'whc',
                nature = 'external',
                type = 'real',
                value = 0.0001171330098724816,
                texname = '\\text{whc}',
                lhablock = 'DECAY',
                lhacode = [ 37 ])

Wh1 = Parameter(name = 'Wh1',
                nature = 'external',
                type = 'real',
                value = 0.005633571201255796,
                texname = '\\text{Wh1}',
                lhablock = 'DECAY',
                lhacode = [ 25 ])

Wh2 = Parameter(name = 'Wh2',
                nature = 'external',
                type = 'real',
                value = 0.00034273859041504334,
                texname = '\\text{Wh2}',
                lhablock = 'DECAY',
                lhacode = [ 35 ])

Wh3 = Parameter(name = 'Wh3',
                nature = 'external',
                type = 'real',
                value = 0.00017048635837303477,
                texname = '\\text{Wh3}',
                lhablock = 'DECAY',
                lhacode = [ 36 ])

TH1x1 = Parameter(name = 'TH1x1',
                  nature = 'internal',
                  type = 'real',
                  value = 'cmath.cos(mixh)',
                  texname = '\\text{TH1x1}')

TH1x2 = Parameter(name = 'TH1x2',
                  nature = 'internal',
                  type = 'real',
                  value = 'cmath.sin(mixh)',
                  texname = '\\text{TH1x2}')

TH2x1 = Parameter(name = 'TH2x1',
                  nature = 'internal',
                  type = 'real',
                  value = '-cmath.sin(mixh)',
                  texname = '\\text{TH2x1}')

TH2x2 = Parameter(name = 'TH2x2',
                  nature = 'internal',
                  type = 'real',
                  value = 'cmath.cos(mixh)',
                  texname = '\\text{TH2x2}')

TH3x3 = Parameter(name = 'TH3x3',
                  nature = 'internal',
                  type = 'real',
                  value = '1',
                  texname = '\\text{TH3x3}')

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\text{aEW}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

lI5 = Parameter(name = 'lI5',
                nature = 'internal',
                type = 'real',
                value = '0',
                texname = '\\text{lI5}')

lI6 = Parameter(name = 'lI6',
                nature = 'internal',
                type = 'real',
                value = '0',
                texname = '\\text{lI6}')

MW = Parameter(name = 'MW',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(MZ**2/2. + cmath.sqrt(MZ**4/4. - (aEW*cmath.pi*MZ**2)/(Gf*cmath.sqrt(2))))',
               texname = '\\text{MW}')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

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
                texname = '\\text{vev}')

l1 = Parameter(name = 'l1',
               nature = 'internal',
               type = 'real',
               value = '-(-(mh1**2*cmath.cos(mixh)**2) - mh2**2*cmath.sin(mixh)**2)/(2.*vev**2)',
               texname = '\\lambda _1')

l2 = Parameter(name = 'l2',
               nature = 'internal',
               type = 'real',
               value = '-((-10*mh1**2 - 10*mh2**2 + 16*mh3**2 - 6*mh1**2*cmath.cos(4*beta) - 6*mh2**2*cmath.cos(4*beta) + 16*mh3**2*cmath.cos(4*beta) - 9*(-mh1**2 + mh2**2)*cmath.cos(4*beta - 2*mixh) - 6*(-mh1**2 + mh2**2)*cmath.cos(2*mixh) - (-mh1**2 + mh2**2)*cmath.cos(4*beta + 2*mixh))/cmath.sin(2*beta)**2)/(16.*vev**2)',
               texname = '\\text{l2}')

l3 = Parameter(name = 'l3',
               nature = 'internal',
               type = 'real',
               value = '((1./cmath.sin(2*beta))*(2*(mh1**2 + mh2**2 - 4*mh3**2 + 4*mhc**2)*cmath.sin(2*beta) + 3*(-mh1**2 + mh2**2)*cmath.sin(2*(-beta + mixh)) + (-mh1**2 + mh2**2)*cmath.sin(2*(beta + mixh))))/(4.*vev**2)',
               texname = '\\text{l3}')

l4 = Parameter(name = 'l4',
               nature = 'internal',
               type = 'real',
               value = '(2*mh1**2 + 2*mh2**2 + 4*mh3**2 - 8*mhc**2 + 2*(-mh1**2 + mh2**2)*cmath.cos(2*mixh))/(4.*vev**2)',
               texname = '\\lambda _4')

lR5 = Parameter(name = 'lR5',
                nature = 'internal',
                type = 'real',
                value = '(2*(mh1**2 + mh2**2 - 2*mh3**2) - 2*(mh1 - mh2)*(mh1 + mh2)*cmath.cos(2*mixh))/(8.*vev**2)',
                texname = '\\text{lR5}')

lR6 = Parameter(name = 'lR6',
                nature = 'internal',
                type = 'real',
                value = '((-mh1**2 + mh2**2)*cmath.cos(mixh)*cmath.sin(mixh))/vev**2',
                texname = '\\text{lR6}')

lR7 = Parameter(name = 'lR7',
                nature = 'internal',
                type = 'real',
                value = '((4*(mh1**2 + mh2**2 - 2*mh3**2)*cmath.cos(2*beta) + 3*(-mh1**2 + mh2**2)*cmath.cos(2*(-beta + mixh)) + (-mh1**2 + mh2**2)*cmath.cos(2*(beta + mixh)))/cmath.sin(2*beta))/(4.*vev**2)',
                texname = '\\text{lR7}')

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

mu1 = Parameter(name = 'mu1',
                nature = 'internal',
                type = 'real',
                value = '-(l1*vev**2)',
                texname = '\\text{mu1}')

mu2 = Parameter(name = 'mu2',
                nature = 'internal',
                type = 'real',
                value = 'mhc**2 - (l3*vev**2)/2.',
                texname = '\\text{mu2}')

GDR1x1 = Parameter(name = 'GDR1x1',
                   nature = 'internal',
                   type = 'real',
                   value = '-(ydo*cmath.tan(beta))',
                   texname = '\\text{GDR1x1}')

GDR2x2 = Parameter(name = 'GDR2x2',
                   nature = 'internal',
                   type = 'real',
                   value = '-(ys*cmath.tan(beta))',
                   texname = '\\text{GDR2x2}')

GDR3x3 = Parameter(name = 'GDR3x3',
                   nature = 'internal',
                   type = 'real',
                   value = '-(yb*cmath.tan(beta))',
                   texname = '\\text{GDR3x3}')

GLR1x1 = Parameter(name = 'GLR1x1',
                   nature = 'internal',
                   type = 'real',
                   value = 'ye/cmath.tan(beta)',
                   texname = '\\text{GLR1x1}')

GLR2x2 = Parameter(name = 'GLR2x2',
                   nature = 'internal',
                   type = 'real',
                   value = 'ym/cmath.tan(beta)',
                   texname = '\\text{GLR2x2}')

GLR3x3 = Parameter(name = 'GLR3x3',
                   nature = 'internal',
                   type = 'real',
                   value = '-(ytau*cmath.tan(beta))',
                   texname = '\\text{GLR3x3}')

GUR1x1 = Parameter(name = 'GUR1x1',
                   nature = 'internal',
                   type = 'real',
                   value = '-(yup*cmath.tan(beta))',
                   texname = '\\text{GUR1x1}')

GUR2x2 = Parameter(name = 'GUR2x2',
                   nature = 'internal',
                   type = 'real',
                   value = '-(yc*cmath.tan(beta))',
                   texname = '\\text{GUR2x2}')

GUR3x3 = Parameter(name = 'GUR3x3',
                   nature = 'internal',
                   type = 'real',
                   value = '-(yt*cmath.tan(beta))',
                   texname = '\\text{GUR3x3}')

l5 = Parameter(name = 'l5',
               nature = 'internal',
               type = 'complex',
               value = 'complex(0,1)*lI5 + lR5',
               texname = '\\lambda _5')

l6 = Parameter(name = 'l6',
               nature = 'internal',
               type = 'complex',
               value = 'complex(0,1)*lI6 + lR6',
               texname = '\\lambda _6')

l7 = Parameter(name = 'l7',
               nature = 'internal',
               type = 'complex',
               value = 'lR7',
               texname = '\\text{l7}')

mu3 = Parameter(name = 'mu3',
                nature = 'internal',
                type = 'complex',
                value = '-(l6*vev**2)/2.',
                texname = '\\text{mu3}')

GD1x1 = Parameter(name = 'GD1x1',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GDR1x1',
                  texname = '\\text{GD1x1}')

GD2x2 = Parameter(name = 'GD2x2',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GDR2x2',
                  texname = '\\text{GD2x2}')

GD3x3 = Parameter(name = 'GD3x3',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GDR3x3',
                  texname = '\\text{GD3x3}')

GL1x1 = Parameter(name = 'GL1x1',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GLR1x1',
                  texname = '\\text{GL1x1}')

GL2x2 = Parameter(name = 'GL2x2',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GLR2x2',
                  texname = '\\text{GL2x2}')

GL3x3 = Parameter(name = 'GL3x3',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GLR3x3',
                  texname = '\\text{GL3x3}')

GU1x1 = Parameter(name = 'GU1x1',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GUR1x1',
                  texname = '\\text{GU1x1}')

GU2x2 = Parameter(name = 'GU2x2',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GUR2x2',
                  texname = '\\text{GU2x2}')

GU3x3 = Parameter(name = 'GU3x3',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GUR3x3',
                  texname = '\\text{GU3x3}')

I1b11 = Parameter(name = 'I1b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GD1x1)',
                  texname = '\\text{I1b11}')

I1b22 = Parameter(name = 'I1b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GD2x2)',
                  texname = '\\text{I1b22}')

I1b33 = Parameter(name = 'I1b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GD3x3)',
                  texname = '\\text{I1b33}')

I2b11 = Parameter(name = 'I2b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GU1x1',
                  texname = '\\text{I2b11}')

I2b22 = Parameter(name = 'I2b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GU2x2',
                  texname = '\\text{I2b22}')

I2b33 = Parameter(name = 'I2b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GU3x3',
                  texname = '\\text{I2b33}')

I3b11 = Parameter(name = 'I3b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GU1x1)',
                  texname = '\\text{I3b11}')

I3b22 = Parameter(name = 'I3b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GU2x2)',
                  texname = '\\text{I3b22}')

I3b33 = Parameter(name = 'I3b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'complexconjugate(GU3x3)',
                  texname = '\\text{I3b33}')

I4b11 = Parameter(name = 'I4b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GD1x1',
                  texname = '\\text{I4b11}')

I4b22 = Parameter(name = 'I4b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GD2x2',
                  texname = '\\text{I4b22}')

I4b33 = Parameter(name = 'I4b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'GD3x3',
                  texname = '\\text{I4b33}')

I5b11 = Parameter(name = 'I5b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ydo',
                  texname = '\\text{I5b11}')

I5b22 = Parameter(name = 'I5b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ys',
                  texname = '\\text{I5b22}')

I5b33 = Parameter(name = 'I5b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yb',
                  texname = '\\text{I5b33}')

I6b11 = Parameter(name = 'I6b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yup',
                  texname = '\\text{I6b11}')

I6b22 = Parameter(name = 'I6b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yc',
                  texname = '\\text{I6b22}')

I6b33 = Parameter(name = 'I6b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt',
                  texname = '\\text{I6b33}')

I7b11 = Parameter(name = 'I7b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yup',
                  texname = '\\text{I7b11}')

I7b22 = Parameter(name = 'I7b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yc',
                  texname = '\\text{I7b22}')

I7b33 = Parameter(name = 'I7b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt',
                  texname = '\\text{I7b33}')

I8b11 = Parameter(name = 'I8b11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ydo',
                  texname = '\\text{I8b11}')

I8b22 = Parameter(name = 'I8b22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ys',
                  texname = '\\text{I8b22}')

I8b33 = Parameter(name = 'I8b33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yb',
                  texname = '\\text{I8b33}')

