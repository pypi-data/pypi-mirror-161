# This file was automatically created by FeynRules 2.3.29
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Fri 11 Dec 2020 18:33:57



from .object_library import all_parameters, Parameter


from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
aEW = Parameter(name = 'aEW',
                nature = 'external',
                type = 'real',
                value = 0.007818608287724784,
                texname = '\\alpha _{\\text{EW}}',
                lhablock = 'SMINPUTS',
                lhacode = [ 1 ])

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

kWL = Parameter(name = 'kWL',
                nature = 'external',
                type = 'real',
                value = 0.1,
                texname = '\\text{kWL}',
                lhablock = 'FRBlock',
                lhacode = [ 1 ])

kWR = Parameter(name = 'kWR',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{kWR}',
                lhablock = 'FRBlock',
                lhacode = [ 2 ])

kZL = Parameter(name = 'kZL',
                nature = 'external',
                type = 'real',
                value = 0.1,
                texname = '\\text{kZL}',
                lhablock = 'FRBlock',
                lhacode = [ 3 ])

kZR = Parameter(name = 'kZR',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{kZR}',
                lhablock = 'FRBlock',
                lhacode = [ 4 ])

kG = Parameter(name = 'kG',
               nature = 'external',
               type = 'real',
               value = 1.,
               texname = '\\text{kG}',
               lhablock = 'FRBlock',
               lhacode = [ 5 ])

CZdL1x1 = Parameter(name = 'CZdL1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZdL1x1}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 1, 1 ])

CZdL1x2 = Parameter(name = 'CZdL1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CZdL1x2}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 1, 2 ])

CZdL1x3 = Parameter(name = 'CZdL1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CZdL1x3}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 1, 3 ])

CZdL2x1 = Parameter(name = 'CZdL2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CZdL2x1}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 2, 1 ])

CZdL2x2 = Parameter(name = 'CZdL2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZdL2x2}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 2, 2 ])

CZdL2x3 = Parameter(name = 'CZdL2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CZdL2x3}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 2, 3 ])

CZdL3x1 = Parameter(name = 'CZdL3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CZdL3x1}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 3, 1 ])

CZdL3x2 = Parameter(name = 'CZdL3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CZdL3x2}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 3, 2 ])

CZdL3x3 = Parameter(name = 'CZdL3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CZdL3x3}',
                    lhablock = 'FRBlock10',
                    lhacode = [ 3, 3 ])

CZlL1x1 = Parameter(name = 'CZlL1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZlL1x1}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 1, 1 ])

CZlL1x2 = Parameter(name = 'CZlL1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CZlL1x2}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 1, 2 ])

CZlL1x3 = Parameter(name = 'CZlL1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CZlL1x3}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 1, 3 ])

CZlL2x1 = Parameter(name = 'CZlL2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CZlL2x1}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 2, 1 ])

CZlL2x2 = Parameter(name = 'CZlL2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZlL2x2}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 2, 2 ])

CZlL2x3 = Parameter(name = 'CZlL2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CZlL2x3}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 2, 3 ])

CZlL3x1 = Parameter(name = 'CZlL3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CZlL3x1}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 3, 1 ])

CZlL3x2 = Parameter(name = 'CZlL3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CZlL3x2}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 3, 2 ])

CZlL3x3 = Parameter(name = 'CZlL3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CZlL3x3}',
                    lhablock = 'FRBlock11',
                    lhacode = [ 3, 3 ])

CKM1x1 = Parameter(name = 'CKM1x1',
                   nature = 'external',
                   type = 'complex',
                   value = 0.974604,
                   texname = '\\text{CKM1x1}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 1, 1 ])

CKM1x2 = Parameter(name = 'CKM1x2',
                   nature = 'external',
                   type = 'complex',
                   value = 0.22537,
                   texname = '\\text{CKM1x2}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 1, 2 ])

CKM1x3 = Parameter(name = 'CKM1x3',
                   nature = 'external',
                   type = 'complex',
                   value = 0.00109018,
                   texname = '\\text{CKM1x3}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 1, 3 ])

CKM2x1 = Parameter(name = 'CKM2x1',
                   nature = 'external',
                   type = 'complex',
                   value = -0.22537,
                   texname = '\\text{CKM2x1}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 2, 1 ])

CKM2x2 = Parameter(name = 'CKM2x2',
                   nature = 'external',
                   type = 'complex',
                   value = 0.974604,
                   texname = '\\text{CKM2x2}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 2, 2 ])

CKM2x3 = Parameter(name = 'CKM2x3',
                   nature = 'external',
                   type = 'complex',
                   value = 0.0413444,
                   texname = '\\text{CKM2x3}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 2, 3 ])

CKM3x1 = Parameter(name = 'CKM3x1',
                   nature = 'external',
                   type = 'complex',
                   value = 0.0082276,
                   texname = '\\text{CKM3x1}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 3, 1 ])

CKM3x2 = Parameter(name = 'CKM3x2',
                   nature = 'external',
                   type = 'complex',
                   value = -0.0413444,
                   texname = '\\text{CKM3x2}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 3, 2 ])

CKM3x3 = Parameter(name = 'CKM3x3',
                   nature = 'external',
                   type = 'complex',
                   value = 1.,
                   texname = '\\text{CKM3x3}',
                   lhablock = 'FRBlock12',
                   lhacode = [ 3, 3 ])

CWqR1x1 = Parameter(name = 'CWqR1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWqR1x1}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 1, 1 ])

CWqR1x2 = Parameter(name = 'CWqR1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CWqR1x2}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 1, 2 ])

CWqR1x3 = Parameter(name = 'CWqR1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CWqR1x3}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 1, 3 ])

CWqR2x1 = Parameter(name = 'CWqR2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CWqR2x1}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 2, 1 ])

CWqR2x2 = Parameter(name = 'CWqR2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWqR2x2}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 2, 2 ])

CWqR2x3 = Parameter(name = 'CWqR2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CWqR2x3}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 2, 3 ])

CWqR3x1 = Parameter(name = 'CWqR3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CWqR3x1}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 3, 1 ])

CWqR3x2 = Parameter(name = 'CWqR3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CWqR3x2}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 3, 2 ])

CWqR3x3 = Parameter(name = 'CWqR3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CWqR3x3}',
                    lhablock = 'FRBlock2',
                    lhacode = [ 3, 3 ])

CWlR1x1 = Parameter(name = 'CWlR1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWlR1x1}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 1, 1 ])

CWlR1x2 = Parameter(name = 'CWlR1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CWlR1x2}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 1, 2 ])

CWlR1x3 = Parameter(name = 'CWlR1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CWlR1x3}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 1, 3 ])

CWlR2x1 = Parameter(name = 'CWlR2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CWlR2x1}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 2, 1 ])

CWlR2x2 = Parameter(name = 'CWlR2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWlR2x2}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 2, 2 ])

CWlR2x3 = Parameter(name = 'CWlR2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CWlR2x3}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 2, 3 ])

CWlR3x1 = Parameter(name = 'CWlR3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CWlR3x1}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 3, 1 ])

CWlR3x2 = Parameter(name = 'CWlR3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CWlR3x2}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 3, 2 ])

CWlR3x3 = Parameter(name = 'CWlR3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CWlR3x3}',
                    lhablock = 'FRBlock3',
                    lhacode = [ 3, 3 ])

CWqL1x1 = Parameter(name = 'CWqL1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWqL1x1}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 1, 1 ])

CWqL1x2 = Parameter(name = 'CWqL1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CWqL1x2}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 1, 2 ])

CWqL1x3 = Parameter(name = 'CWqL1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CWqL1x3}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 1, 3 ])

CWqL2x1 = Parameter(name = 'CWqL2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CWqL2x1}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 2, 1 ])

CWqL2x2 = Parameter(name = 'CWqL2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWqL2x2}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 2, 2 ])

CWqL2x3 = Parameter(name = 'CWqL2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CWqL2x3}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 2, 3 ])

CWqL3x1 = Parameter(name = 'CWqL3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CWqL3x1}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 3, 1 ])

CWqL3x2 = Parameter(name = 'CWqL3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CWqL3x2}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 3, 2 ])

CWqL3x3 = Parameter(name = 'CWqL3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CWqL3x3}',
                    lhablock = 'FRBlock4',
                    lhacode = [ 3, 3 ])

CWlL1x1 = Parameter(name = 'CWlL1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWlL1x1}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 1, 1 ])

CWlL1x2 = Parameter(name = 'CWlL1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CWlL1x2}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 1, 2 ])

CWlL1x3 = Parameter(name = 'CWlL1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CWlL1x3}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 1, 3 ])

CWlL2x1 = Parameter(name = 'CWlL2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CWlL2x1}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 2, 1 ])

CWlL2x2 = Parameter(name = 'CWlL2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CWlL2x2}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 2, 2 ])

CWlL2x3 = Parameter(name = 'CWlL2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CWlL2x3}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 2, 3 ])

CWlL3x1 = Parameter(name = 'CWlL3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CWlL3x1}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 3, 1 ])

CWlL3x2 = Parameter(name = 'CWlL3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CWlL3x2}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 3, 2 ])

CWlL3x3 = Parameter(name = 'CWlL3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CWlL3x3}',
                    lhablock = 'FRBlock5',
                    lhacode = [ 3, 3 ])

CZuR1x1 = Parameter(name = 'CZuR1x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR1x1}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 1, 1 ])

CZuR1x2 = Parameter(name = 'CZuR1x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR1x2}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 1, 2 ])

CZuR1x3 = Parameter(name = 'CZuR1x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR1x3}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 1, 3 ])

CZuR2x1 = Parameter(name = 'CZuR2x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR2x1}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 2, 1 ])

CZuR2x2 = Parameter(name = 'CZuR2x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR2x2}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 2, 2 ])

CZuR2x3 = Parameter(name = 'CZuR2x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR2x3}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 2, 3 ])

CZuR3x1 = Parameter(name = 'CZuR3x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR3x1}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 3, 1 ])

CZuR3x2 = Parameter(name = 'CZuR3x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR3x2}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 3, 2 ])

CZuR3x3 = Parameter(name = 'CZuR3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZuR3x3}',
                    lhablock = 'FRBlock6',
                    lhacode = [ 3, 3 ])

CZdR1x1 = Parameter(name = 'CZdR1x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR1x1}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 1, 1 ])

CZdR1x2 = Parameter(name = 'CZdR1x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR1x2}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 1, 2 ])

CZdR1x3 = Parameter(name = 'CZdR1x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR1x3}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 1, 3 ])

CZdR2x1 = Parameter(name = 'CZdR2x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR2x1}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 2, 1 ])

CZdR2x2 = Parameter(name = 'CZdR2x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR2x2}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 2, 2 ])

CZdR2x3 = Parameter(name = 'CZdR2x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR2x3}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 2, 3 ])

CZdR3x1 = Parameter(name = 'CZdR3x1',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR3x1}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 3, 1 ])

CZdR3x2 = Parameter(name = 'CZdR3x2',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR3x2}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 3, 2 ])

CZdR3x3 = Parameter(name = 'CZdR3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1,
                    texname = '\\text{CZdR3x3}',
                    lhablock = 'FRBlock7',
                    lhacode = [ 3, 3 ])

CZlR1x1 = Parameter(name = 'CZlR1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZlR1x1}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 1, 1 ])

CZlR1x2 = Parameter(name = 'CZlR1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CZlR1x2}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 1, 2 ])

CZlR1x3 = Parameter(name = 'CZlR1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CZlR1x3}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 1, 3 ])

CZlR2x1 = Parameter(name = 'CZlR2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CZlR2x1}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 2, 1 ])

CZlR2x2 = Parameter(name = 'CZlR2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZlR2x2}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 2, 2 ])

CZlR2x3 = Parameter(name = 'CZlR2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CZlR2x3}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 2, 3 ])

CZlR3x1 = Parameter(name = 'CZlR3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CZlR3x1}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 3, 1 ])

CZlR3x2 = Parameter(name = 'CZlR3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CZlR3x2}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 3, 2 ])

CZlR3x3 = Parameter(name = 'CZlR3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CZlR3x3}',
                    lhablock = 'FRBlock8',
                    lhacode = [ 3, 3 ])

CZuL1x1 = Parameter(name = 'CZuL1x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZuL1x1}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 1, 1 ])

CZuL1x2 = Parameter(name = 'CZuL1x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.22537,
                    texname = '\\text{CZuL1x2}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 1, 2 ])

CZuL1x3 = Parameter(name = 'CZuL1x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.00109018,
                    texname = '\\text{CZuL1x3}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 1, 3 ])

CZuL2x1 = Parameter(name = 'CZuL2x1',
                    nature = 'external',
                    type = 'real',
                    value = -0.22537,
                    texname = '\\text{CZuL2x1}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 2, 1 ])

CZuL2x2 = Parameter(name = 'CZuL2x2',
                    nature = 'external',
                    type = 'real',
                    value = 0.974604,
                    texname = '\\text{CZuL2x2}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 2, 2 ])

CZuL2x3 = Parameter(name = 'CZuL2x3',
                    nature = 'external',
                    type = 'real',
                    value = 0.0413444,
                    texname = '\\text{CZuL2x3}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 2, 3 ])

CZuL3x1 = Parameter(name = 'CZuL3x1',
                    nature = 'external',
                    type = 'real',
                    value = 0.0082276,
                    texname = '\\text{CZuL3x1}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 3, 1 ])

CZuL3x2 = Parameter(name = 'CZuL3x2',
                    nature = 'external',
                    type = 'real',
                    value = -0.0413444,
                    texname = '\\text{CZuL3x2}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 3, 2 ])

CZuL3x3 = Parameter(name = 'CZuL3x3',
                    nature = 'external',
                    type = 'real',
                    value = 1.,
                    texname = '\\text{CZuL3x3}',
                    lhablock = 'FRBlock9',
                    lhacode = [ 3, 3 ])

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
                value = 2100.,
                texname = '\\text{MZp}',
                lhablock = 'MASS',
                lhacode = [ 9000001 ])

MW = Parameter(name = 'MW',
               nature = 'external',
               type = 'real',
               value = 80.399,
               texname = '\\text{MW}',
               lhablock = 'MASS',
               lhacode = [ 24 ])

MWp = Parameter(name = 'MWp',
                nature = 'external',
                type = 'real',
                value = 2000.,
                texname = '\\text{MWp}',
                lhablock = 'MASS',
                lhacode = [ 9000002 ])

ME = Parameter(name = 'ME',
               nature = 'external',
               type = 'real',
               value = 0.000511,
               texname = '\\text{ME}',
               lhablock = 'MASS',
               lhacode = [ 11 ])

MM = Parameter(name = 'MM',
               nature = 'external',
               type = 'real',
               value = 0.10566,
               texname = '\\text{MM}',
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

MH = Parameter(name = 'MH',
               nature = 'external',
               type = 'real',
               value = 120,
               texname = '\\text{MH}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

WZ = Parameter(name = 'WZ',
               nature = 'external',
               type = 'real',
               value = 2.4952,
               texname = '\\text{WZ}',
               lhablock = 'DECAY',
               lhacode = [ 23 ])

WZp = Parameter(name = 'WZp',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{WZp}',
                lhablock = 'DECAY',
                lhacode = [ 9000001 ])

WW = Parameter(name = 'WW',
               nature = 'external',
               type = 'real',
               value = 2.085,
               texname = '\\text{WW}',
               lhablock = 'DECAY',
               lhacode = [ 24 ])

WWp = Parameter(name = 'WWp',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{WWp}',
                lhablock = 'DECAY',
                lhacode = [ 9000002 ])

WM = Parameter(name = 'WM',
               nature = 'external',
               type = 'real',
               value = 0.01,
               texname = '\\text{WM}',
               lhablock = 'DECAY',
               lhacode = [ 13 ])

WTA = Parameter(name = 'WTA',
                nature = 'external',
                type = 'real',
                value = 0.01,
                texname = '\\text{WTA}',
                lhablock = 'DECAY',
                lhacode = [ 15 ])

WC = Parameter(name = 'WC',
               nature = 'external',
               type = 'real',
               value = 0.01,
               texname = '\\text{WC}',
               lhablock = 'DECAY',
               lhacode = [ 4 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WB = Parameter(name = 'WB',
               nature = 'external',
               type = 'real',
               value = 0.01,
               texname = '\\text{WB}',
               lhablock = 'DECAY',
               lhacode = [ 5 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00575308848,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

sw2 = Parameter(name = 'sw2',
                nature = 'internal',
                type = 'real',
                value = '1 - MW**2/MZ**2',
                texname = '\\text{sw2}')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

gs = Parameter(name = 'gs',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
               texname = 'g_s')

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
               value = '-ee/(2.*cw)',
               texname = 'g_1')

gw = Parameter(name = 'gw',
               nature = 'internal',
               type = 'real',
               value = 'ee/sw',
               texname = 'g_w')

gz = Parameter(name = 'gz',
               nature = 'internal',
               type = 'real',
               value = 'ee/(cw*sw)',
               texname = '\\text{gz}')

vev = Parameter(name = 'vev',
                nature = 'internal',
                type = 'real',
                value = '(2*MW*sw)/ee',
                texname = '\\text{vev}')

lam = Parameter(name = 'lam',
                nature = 'internal',
                type = 'real',
                value = '(2*MH**2)/vev**2',
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

muH2 = Parameter(name = 'muH2',
                 nature = 'internal',
                 type = 'real',
                 value = '(lam*vev**2)/4.',
                 texname = '\\text{muH2}')

I1a11 = Parameter(name = 'I1a11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ydo*complexconjugate(CKM1x1)',
                  texname = '\\text{I1a11}')

I1a12 = Parameter(name = 'I1a12',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ydo*complexconjugate(CKM2x1)',
                  texname = '\\text{I1a12}')

I1a13 = Parameter(name = 'I1a13',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ydo*complexconjugate(CKM3x1)',
                  texname = '\\text{I1a13}')

I1a21 = Parameter(name = 'I1a21',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ys*complexconjugate(CKM1x2)',
                  texname = '\\text{I1a21}')

I1a22 = Parameter(name = 'I1a22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ys*complexconjugate(CKM2x2)',
                  texname = '\\text{I1a22}')

I1a23 = Parameter(name = 'I1a23',
                  nature = 'internal',
                  type = 'complex',
                  value = 'ys*complexconjugate(CKM3x2)',
                  texname = '\\text{I1a23}')

I1a31 = Parameter(name = 'I1a31',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yb*complexconjugate(CKM1x3)',
                  texname = '\\text{I1a31}')

I1a32 = Parameter(name = 'I1a32',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yb*complexconjugate(CKM2x3)',
                  texname = '\\text{I1a32}')

I1a33 = Parameter(name = 'I1a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yb*complexconjugate(CKM3x3)',
                  texname = '\\text{I1a33}')

I2a11 = Parameter(name = 'I2a11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yup*complexconjugate(CKM1x1)',
                  texname = '\\text{I2a11}')

I2a12 = Parameter(name = 'I2a12',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yc*complexconjugate(CKM2x1)',
                  texname = '\\text{I2a12}')

I2a13 = Parameter(name = 'I2a13',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt*complexconjugate(CKM3x1)',
                  texname = '\\text{I2a13}')

I2a21 = Parameter(name = 'I2a21',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yup*complexconjugate(CKM1x2)',
                  texname = '\\text{I2a21}')

I2a22 = Parameter(name = 'I2a22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yc*complexconjugate(CKM2x2)',
                  texname = '\\text{I2a22}')

I2a23 = Parameter(name = 'I2a23',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt*complexconjugate(CKM3x2)',
                  texname = '\\text{I2a23}')

I2a31 = Parameter(name = 'I2a31',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yup*complexconjugate(CKM1x3)',
                  texname = '\\text{I2a31}')

I2a32 = Parameter(name = 'I2a32',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yc*complexconjugate(CKM2x3)',
                  texname = '\\text{I2a32}')

I2a33 = Parameter(name = 'I2a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'yt*complexconjugate(CKM3x3)',
                  texname = '\\text{I2a33}')

I3a11 = Parameter(name = 'I3a11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x1*yup',
                  texname = '\\text{I3a11}')

I3a12 = Parameter(name = 'I3a12',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x2*yup',
                  texname = '\\text{I3a12}')

I3a13 = Parameter(name = 'I3a13',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x3*yup',
                  texname = '\\text{I3a13}')

I3a21 = Parameter(name = 'I3a21',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x1*yc',
                  texname = '\\text{I3a21}')

I3a22 = Parameter(name = 'I3a22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x2*yc',
                  texname = '\\text{I3a22}')

I3a23 = Parameter(name = 'I3a23',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x3*yc',
                  texname = '\\text{I3a23}')

I3a31 = Parameter(name = 'I3a31',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x1*yt',
                  texname = '\\text{I3a31}')

I3a32 = Parameter(name = 'I3a32',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x2*yt',
                  texname = '\\text{I3a32}')

I3a33 = Parameter(name = 'I3a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x3*yt',
                  texname = '\\text{I3a33}')

I4a11 = Parameter(name = 'I4a11',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x1*ydo',
                  texname = '\\text{I4a11}')

I4a12 = Parameter(name = 'I4a12',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x2*ys',
                  texname = '\\text{I4a12}')

I4a13 = Parameter(name = 'I4a13',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM1x3*yb',
                  texname = '\\text{I4a13}')

I4a21 = Parameter(name = 'I4a21',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x1*ydo',
                  texname = '\\text{I4a21}')

I4a22 = Parameter(name = 'I4a22',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x2*ys',
                  texname = '\\text{I4a22}')

I4a23 = Parameter(name = 'I4a23',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM2x3*yb',
                  texname = '\\text{I4a23}')

I4a31 = Parameter(name = 'I4a31',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x1*ydo',
                  texname = '\\text{I4a31}')

I4a32 = Parameter(name = 'I4a32',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x2*ys',
                  texname = '\\text{I4a32}')

I4a33 = Parameter(name = 'I4a33',
                  nature = 'internal',
                  type = 'complex',
                  value = 'CKM3x3*yb',
                  texname = '\\text{I4a33}')

