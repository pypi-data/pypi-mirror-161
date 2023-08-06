# This file was automatically created by FeynRules 2.3.10
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Thu 19 Jan 2017 16:30:59



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# This is a default parameter object representing the renormalization scale (MU_R).
MU_R = Parameter(name = 'MU_R',
                 nature = 'external',
                 type = 'real',
                 value = 91.188,
                 texname = '\\text{\\mu_r}',
                 lhablock = 'LOOP',
                 lhacode = [1])

# User-defined parameters.
aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.94,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.0000117456,
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

kL = Parameter(name = 'kL',
               nature = 'external',
               type = 'real',
               value = 1.,
               texname = '\\kappa _L',
               lhablock = 'SSMCOUP',
               lhacode = [ 1 ])

kR = Parameter(name = 'kR',
               nature = 'external',
               type = 'real',
               value = 0.,
               texname = '\\kappa _R',
               lhablock = 'SSMCOUP',
               lhacode = [ 2 ])

ymt = Parameter(name = 'ymt',
                nature = 'external',
                type = 'real',
                value = 173.3,
                texname = '\\text{ymt}',
                lhablock = 'YUKAWA',
                lhacode = [ 6 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 173.3,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MH = Parameter(name = 'MH',
               nature = 'external',
               type = 'real',
               value = 125.7,
               texname = '\\text{MH}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

MZp = Parameter(name = 'MZp',
                nature = 'external',
                type = 'real',
                value = 3000.,
                texname = '\\text{MZp}',
                lhablock = 'MASS',
                lhacode = [ 32 ])

MWp = Parameter(name = 'MWp',
                nature = 'external',
                type = 'real',
                value = 3000.,
                texname = '\\text{MWp}',
                lhablock = 'MASS',
                lhacode = [ 34 ])

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
               value = 1.35,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00417,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

WZp = Parameter(name = 'WZp',
                nature = 'external',
                type = 'real',
                value = 89.59,
                texname = '\\text{WZp}',
                lhablock = 'DECAY',
                lhacode = [ 32 ])

WWp = Parameter(name = 'WWp',
                nature = 'external',
                type = 'real',
                value = 101.27,
                texname = '\\text{WWp}',
                lhablock = 'DECAY',
                lhacode = [ 34 ])

gZpdA = Parameter(name = 'gZpdA',
                  nature = 'internal',
                  type = 'real',
                  value = '0.25',
                  texname = '\\text{gZpdA}')

gZpeA = Parameter(name = 'gZpeA',
                  nature = 'internal',
                  type = 'real',
                  value = '0.25',
                  texname = '\\text{gZpeA}')

gZpuA = Parameter(name = 'gZpuA',
                  nature = 'internal',
                  type = 'real',
                  value = '-0.25',
                  texname = '\\text{gZpuA}')

gZpvA = Parameter(name = 'gZpvA',
                  nature = 'internal',
                  type = 'real',
                  value = '-0.25',
                  texname = '\\text{gZpvA}')

gZpvV = Parameter(name = 'gZpvV',
                  nature = 'internal',
                  type = 'real',
                  value = '0.25',
                  texname = '\\text{gZpvV}')

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

gZpvL = Parameter(name = 'gZpvL',
                  nature = 'internal',
                  type = 'real',
                  value = '-gZpvA + gZpvV',
                  texname = '\\text{gZpvL}')

gZpvR = Parameter(name = 'gZpvR',
                  nature = 'internal',
                  type = 'real',
                  value = 'gZpvA + gZpvV',
                  texname = '\\text{gZpvR}')

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

gZpdV = Parameter(name = 'gZpdV',
                  nature = 'internal',
                  type = 'real',
                  value = '-0.25 + sw2/3.',
                  texname = '\\text{gZpdV}')

gZpeV = Parameter(name = 'gZpeV',
                  nature = 'internal',
                  type = 'real',
                  value = '-0.25 + sw2',
                  texname = '\\text{gZpeV}')

gZpuV = Parameter(name = 'gZpuV',
                  nature = 'internal',
                  type = 'real',
                  value = '0.25 - (2*sw2)/3.',
                  texname = '\\text{gZpuV}')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

gZpdL = Parameter(name = 'gZpdL',
                  nature = 'internal',
                  type = 'real',
                  value = '-gZpdA + gZpdV',
                  texname = '\\text{gZpdL}')

gZpdR = Parameter(name = 'gZpdR',
                  nature = 'internal',
                  type = 'real',
                  value = 'gZpdA + gZpdV',
                  texname = '\\text{gZpdR}')

gZpeL = Parameter(name = 'gZpeL',
                  nature = 'internal',
                  type = 'real',
                  value = '-gZpeA + gZpeV',
                  texname = '\\text{gZpeL}')

gZpeR = Parameter(name = 'gZpeR',
                  nature = 'internal',
                  type = 'real',
                  value = 'gZpeA + gZpeV',
                  texname = '\\text{gZpeR}')

gZpuL = Parameter(name = 'gZpuL',
                  nature = 'internal',
                  type = 'real',
                  value = '-gZpuA + gZpuV',
                  texname = '\\text{gZpuL}')

gZpuR = Parameter(name = 'gZpuR',
                  nature = 'internal',
                  type = 'real',
                  value = 'gZpuA + gZpuV',
                  texname = '\\text{gZpuR}')

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

lam = Parameter(name = 'lam',
                nature = 'internal',
                type = 'real',
                value = 'MH**2/(2.*vev**2)',
                texname = '\\text{lam}')

yt = Parameter(name = 'yt',
               nature = 'internal',
               type = 'real',
               value = '(ymt*cmath.sqrt(2))/vev',
               texname = '\\text{yt}')

muH = Parameter(name = 'muH',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(lam*vev**2)',
                texname = '\\mu')

I2a33 = Parameter(name = 'I2a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt',
                  texname = '\\text{I2a33}')

I3a33 = Parameter(name = 'I3a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt',
                  texname = '\\text{I3a33}')

