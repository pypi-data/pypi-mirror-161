# This file was automatically created by FeynRules 2.4.43
# Mathematica version: 10.1.0  for Mac OS X x86 (64-bit) (March 24, 2015)
# Date: Wed 1 Jun 2016 20:28:08


from .object_library import all_lorentz, Lorentz

from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot
try:
   import form_factors as ForFac 
except ImportError:
   pass


FF1 = Lorentz(name = 'FF1',
              spins = [ 2, 2 ],
              structure = 'P(-1,1)*Gamma(-1,2,1)')

FF2 = Lorentz(name = 'FF2',
              spins = [ 2, 2 ],
              structure = 'ProjM(2,1) + ProjP(2,1)')

FF3 = Lorentz(name = 'FF3',
              spins = [ 2, 2 ],
              structure = 'P(-1,1)*Gamma(-1,2,-2)*ProjM(-2,1) + P(-1,1)*Gamma(-1,2,-2)*ProjP(-2,1)')

VV1 = Lorentz(name = 'VV1',
              spins = [ 3, 3 ],
              structure = 'P(1,2)*P(2,2)')

VV2 = Lorentz(name = 'VV2',
              spins = [ 3, 3 ],
              structure = 'Metric(1,2)')

VV3 = Lorentz(name = 'VV3',
              spins = [ 3, 3 ],
              structure = 'P(-1,2)**2*Metric(1,2)')

VV4 = Lorentz(name = 'VV4',
              spins = [ 3, 3 ],
              structure = 'P(1,2)*P(2,2) - (3*P(-1,2)**2*Metric(1,2))/2.')

VV5 = Lorentz(name = 'VV5',
              spins = [ 3, 3 ],
              structure = 'P(1,2)*P(2,2) - P(-1,2)**2*Metric(1,2)')

UUS1 = Lorentz(name = 'UUS1',
               spins = [ -1, -1, 1 ],
               structure = '1')

UUV1 = Lorentz(name = 'UUV1',
               spins = [ -1, -1, 3 ],
               structure = 'P(3,2) + P(3,3)')

UUT1 = Lorentz(name = 'UUT1',
               spins = [ -1, -1, 5 ],
               structure = 'P(1003,2)*P(2003,1) + P(1003,1)*P(2003,2) + P(-1,2)**2*Metric(1003,2003)')

SSS1 = Lorentz(name = 'SSS1',
               spins = [ 1, 1, 1 ],
               structure = '1')

SST1 = Lorentz(name = 'SST1',
               spins = [ 1, 1, 5 ],
               structure = 'Metric(1003,2003)')

SST2 = Lorentz(name = 'SST2',
               spins = [ 1, 1, 5 ],
               structure = 'P(1003,2)*P(2003,1) + P(1003,1)*P(2003,2) - P(-1,1)*P(-1,2)*Metric(1003,2003)')

FFS1 = Lorentz(name = 'FFS1',
               spins = [ 2, 2, 1 ],
               structure = 'Gamma5(2,1)')

FFS2 = Lorentz(name = 'FFS2',
               spins = [ 2, 2, 1 ],
               structure = 'Identity(2,1)')

FFS3 = Lorentz(name = 'FFS3',
               spins = [ 2, 2, 1 ],
               structure = 'ProjM(2,1)')

FFS4 = Lorentz(name = 'FFS4',
               spins = [ 2, 2, 1 ],
               structure = 'ProjM(2,1) - ProjP(2,1)')

FFS5 = Lorentz(name = 'FFS5',
               spins = [ 2, 2, 1 ],
               structure = 'ProjP(2,1)')

FFS6 = Lorentz(name = 'FFS6',
               spins = [ 2, 2, 1 ],
               structure = 'ProjM(2,1) + ProjP(2,1)')

FFV1 = Lorentz(name = 'FFV1',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,1)')

FFV2 = Lorentz(name = 'FFV2',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1)')

FFV3 = Lorentz(name = 'FFV3',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) - 2*Gamma(3,2,-1)*ProjP(-1,1)')

FFV4 = Lorentz(name = 'FFV4',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,1) - (4*Gamma(3,2,-1)*ProjM(-1,1))/13. - (4*Gamma(3,2,-1)*ProjP(-1,1))/13.')

FFV5 = Lorentz(name = 'FFV5',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) + Gamma(3,2,-1)*ProjP(-1,1)')

FFV6 = Lorentz(name = 'FFV6',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) + 2*Gamma(3,2,-1)*ProjP(-1,1)')

FFV7 = Lorentz(name = 'FFV7',
               spins = [ 2, 2, 3 ],
               structure = 'Gamma(3,2,-1)*ProjM(-1,1) + 4*Gamma(3,2,-1)*ProjP(-1,1)')

FFT1 = Lorentz(name = 'FFT1',
               spins = [ 2, 2, 5 ],
               structure = 'Identity(2,1)*Metric(1003,2003)')

FFT2 = Lorentz(name = 'FFT2',
               spins = [ 2, 2, 5 ],
               structure = 'P(2003,1)*Gamma(1003,2,1) - P(2003,2)*Gamma(1003,2,1) + P(1003,1)*Gamma(2003,2,1) - P(1003,2)*Gamma(2003,2,1) - 2*P(-1,1)*Gamma(-1,2,1)*Metric(1003,2003) + 2*P(-1,2)*Gamma(-1,2,1)*Metric(1003,2003)')

FFT3 = Lorentz(name = 'FFT3',
               spins = [ 2, 2, 5 ],
               structure = '2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) + P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) - P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1)')

FFT4 = Lorentz(name = 'FFT4',
               spins = [ 2, 2, 5 ],
               structure = '-2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) - P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) - P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1)')

FFT5 = Lorentz(name = 'FFT5',
               spins = [ 2, 2, 5 ],
               structure = '-(P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. - 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2.')

FFT6 = Lorentz(name = 'FFT6',
               spins = [ 2, 2, 5 ],
               structure = 'P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1) + (2*P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/3. - (2*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/3. + P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1) + 2*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + (2*P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/3. - (2*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/3. + 2*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 2*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) - P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) + (P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1))/3. - P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1) - (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/3.')

FFT7 = Lorentz(name = 'FFT7',
               spins = [ 2, 2, 5 ],
               structure = '3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1) + 2*P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) - 2*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) + 3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1) + 6*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + 3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + 2*P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) - 2*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) + 6*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + 3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + 6*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 6*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 6*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 3*P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) - 3*P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) - 3*P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1) - P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1)')

FFT8 = Lorentz(name = 'FFT8',
               spins = [ 2, 2, 5 ],
               structure = 'Metric(1003,2003)*ProjM(2,1) + Metric(1003,2003)*ProjP(2,1)')

FFT9 = Lorentz(name = 'FFT9',
               spins = [ 2, 2, 5 ],
               structure = 'Identity(2,1)*Metric(1003,2003) + Metric(1003,2003)*ProjM(2,1) + Metric(1003,2003)*ProjP(2,1)')

FFT10 = Lorentz(name = 'FFT10',
                spins = [ 2, 2, 5 ],
                structure = 'Identity(2,1)*Metric(1003,2003) + (5*Metric(1003,2003)*ProjM(2,1))/4. + (5*Metric(1003,2003)*ProjP(2,1))/4.')

FFT11 = Lorentz(name = 'FFT11',
                spins = [ 2, 2, 5 ],
                structure = 'Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjM(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjM(-1,1) - 8*Metric(1003,2003)*ProjM(2,1) + Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjP(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjP(-1,1) - 8*Metric(1003,2003)*ProjP(2,1)')

FFT12 = Lorentz(name = 'FFT12',
                spins = [ 2, 2, 5 ],
                structure = 'Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjM(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjM(-1,1) - 6*Metric(1003,2003)*ProjM(2,1) + Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjP(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjP(-1,1) - 6*Metric(1003,2003)*ProjP(2,1)')

FFT13 = Lorentz(name = 'FFT13',
                spins = [ 2, 2, 5 ],
                structure = 'Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjM(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjM(-1,1) - 2*Metric(1003,2003)*ProjM(2,1) + Gamma(1003,2,-2)*Gamma(2003,-2,-1)*ProjP(-1,1) + Gamma(1003,-2,-1)*Gamma(2003,2,-2)*ProjP(-1,1) - 2*Metric(1003,2003)*ProjP(2,1)')

FFT14 = Lorentz(name = 'FFT14',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) - 2*P(-1,1)*Gamma(-1,2,1)*Metric(1003,2003) - P(-1,3)*Gamma(-1,2,1)*Metric(1003,2003) - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (P(2003,3)*Gamma(1003,2,-1)*ProjM(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (P(2003,3)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT15 = Lorentz(name = 'FFT15',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) - 6*P(-1,1)*Gamma(-1,2,1)*Metric(1003,2003) - 3*P(-1,3)*Gamma(-1,2,1)*Metric(1003,2003) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. + (P(2003,3)*Gamma(1003,2,-1)*ProjM(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. + (P(2003,3)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT16 = Lorentz(name = 'FFT16',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + 3*P(-1,1)*Gamma(-1,2,1)*Metric(1003,2003) + (3*P(-1,3)*Gamma(-1,2,1)*Metric(1003,2003))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. + (P(2003,3)*Gamma(1003,2,-1)*ProjM(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. + (P(2003,3)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT17 = Lorentz(name = 'FFT17',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + P(-1,1)*Gamma(-1,2,1)*Metric(1003,2003) + (P(-1,3)*Gamma(-1,2,1)*Metric(1003,2003))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (P(2003,3)*Gamma(1003,2,-1)*ProjM(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (P(2003,3)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT18 = Lorentz(name = 'FFT18',
                spins = [ 2, 2, 5 ],
                structure = '2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) + P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) - P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1) + 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - P(2003,1)*Gamma(1003,2,-1)*ProjP(-1,1) + P(2003,2)*Gamma(1003,2,-1)*ProjP(-1,1) - P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + P(1003,2)*Gamma(2003,2,-1)*ProjP(-1,1)')

FFT19 = Lorentz(name = 'FFT19',
                spins = [ 2, 2, 5 ],
                structure = '-2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + P(2003,1)*Gamma(1003,2,-1)*ProjP(-1,1) - P(2003,2)*Gamma(1003,2,-1)*ProjP(-1,1) + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) - P(1003,2)*Gamma(2003,2,-1)*ProjP(-1,1)')

FFT20 = Lorentz(name = 'FFT20',
                spins = [ 2, 2, 5 ],
                structure = '-2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1) - P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1) + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) - P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1) - 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + 2*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + P(2003,1)*Gamma(1003,2,-1)*ProjP(-1,1) - P(2003,2)*Gamma(1003,2,-1)*ProjP(-1,1) + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) - P(1003,2)*Gamma(2003,2,-1)*ProjP(-1,1)')

FFT21 = Lorentz(name = 'FFT21',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. - 3*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - 3*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - 3*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - (3*P(2003,1)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + (3*P(2003,2)*Gamma(1003,2,-1)*ProjP(-1,1))/2. - (P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1))/2. + (3*P(1003,2)*Gamma(2003,2,-1)*ProjP(-1,1))/2. + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT22 = Lorentz(name = 'FFT22',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1) - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. - 3*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - 3*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - 3*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - (3*P(2003,1)*Gamma(1003,2,-1)*ProjM(-1,1))/2. + (3*P(2003,2)*Gamma(1003,2,-1)*ProjM(-1,1))/2. - (P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1))/2. + (3*P(1003,2)*Gamma(2003,2,-1)*ProjM(-1,1))/2. + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) + P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1) - 3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1) - (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. - 3*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - 3*P(-1,2)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - 3*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - (3*P(2003,1)*Gamma(1003,2,-1)*ProjP(-1,1))/2. + (3*P(2003,2)*Gamma(1003,2,-1)*ProjP(-1,1))/2. - (P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1))/2. + (3*P(1003,2)*Gamma(2003,2,-1)*ProjP(-1,1))/2. + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT23 = Lorentz(name = 'FFT23',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. - 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT24 = Lorentz(name = 'FFT24',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. - 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) - P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (P(-1,1)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. - (P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. - (P(-1,1)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. - 2*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) - P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT25 = Lorentz(name = 'FFT25',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjM(-2,1))/4. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/4. + P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + (P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-3,-2)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,2,-4)*Gamma(2003,-4,-3)*ProjP(-2,1))/4. - (3*P(-1,3)*Gamma(-1,2,-4)*Gamma(1003,-4,-3)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/4. + (3*P(-1,3)*Gamma(-1,-3,-2)*Gamma(1003,-4,-3)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + (3*P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. + (3*P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/4. + P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + (P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

FFT26 = Lorentz(name = 'FFT26',
                spins = [ 2, 2, 5 ],
                structure = 'P(2003,1)*Gamma(1003,2,1) + (P(2003,3)*Gamma(1003,2,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjM(-2,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjM(-2,1))/2. + 3*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1) + (3*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjM(-2,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjM(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjM(-1,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,2,-4)*Gamma(2003,-3,-2)*ProjP(-2,1))/2. + P(-1,1)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1) + (P(-1,3)*Gamma(-1,-4,-3)*Gamma(1003,-3,-2)*Gamma(2003,2,-4)*ProjP(-2,1))/2. + 3*P(-1,1)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1) + (3*P(-1,3)*Gamma(-1,2,-2)*Metric(1003,2003)*ProjP(-2,1))/2. + P(1003,1)*Gamma(2003,2,-1)*ProjP(-1,1) + (P(1003,3)*Gamma(2003,2,-1)*ProjP(-1,1))/2.')

VSS1 = Lorentz(name = 'VSS1',
               spins = [ 3, 1, 1 ],
               structure = 'P(1,2) - P(1,3)')

VST1 = Lorentz(name = 'VST1',
               spins = [ 3, 1, 5 ],
               structure = 'P(2003,2)*Metric(1,1003) + P(1003,2)*Metric(1,2003) - P(1,2)*Metric(1003,2003)')

VVS1 = Lorentz(name = 'VVS1',
               spins = [ 3, 3, 1 ],
               structure = 'Metric(1,2)')

VVV1 = Lorentz(name = 'VVV1',
               spins = [ 3, 3, 3 ],
               structure = '-(Epsilon(1,2,3,-1)*P(-1,1)) + Epsilon(1,2,3,-1)*P(-1,2)')

VVV2 = Lorentz(name = 'VVV2',
               spins = [ 3, 3, 3 ],
               structure = 'P(3,1)*Metric(1,2) - P(3,2)*Metric(1,2) - P(2,1)*Metric(1,3) + P(2,3)*Metric(1,3) + P(1,2)*Metric(2,3) - P(1,3)*Metric(2,3)')

VVT1 = Lorentz(name = 'VVT1',
               spins = [ 3, 3, 5 ],
               structure = 'Metric(1,2)*Metric(1003,2003)')

VVT2 = Lorentz(name = 'VVT2',
               spins = [ 3, 3, 5 ],
               structure = 'Metric(1,2003)*Metric(2,1003) + Metric(1,1003)*Metric(2,2003) - Metric(1,2)*Metric(1003,2003)')

VVT3 = Lorentz(name = 'VVT3',
               spins = [ 3, 3, 5 ],
               structure = 'Metric(1,2003)*Metric(2,1003) + Metric(1,1003)*Metric(2,2003) + Metric(1,2)*Metric(1003,2003)')

VVT4 = Lorentz(name = 'VVT4',
               spins = [ 3, 3, 5 ],
               structure = 'P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) - P(2,1)*P(2003,2)*Metric(1,1003) - P(2,1)*P(1003,2)*Metric(1,2003) - P(1,2)*P(2003,1)*Metric(2,1003) + P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003) - P(1,2)*P(1003,1)*Metric(2,2003) + P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003) + P(1,2)*P(2,1)*Metric(1003,2003) - P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003)')

VVT5 = Lorentz(name = 'VVT5',
               spins = [ 3, 3, 5 ],
               structure = 'P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) - P(2,1)*P(2003,2)*Metric(1,1003) - P(2,2)*P(2003,2)*Metric(1,1003) - P(2,1)*P(1003,2)*Metric(1,2003) - P(2,2)*P(1003,2)*Metric(1,2003) - P(1,1)*P(2003,1)*Metric(2,1003) - P(1,2)*P(2003,1)*Metric(2,1003) + P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003) - P(1,1)*P(1003,1)*Metric(2,2003) - P(1,2)*P(1003,1)*Metric(2,2003) + P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003) + P(1,1)*P(2,1)*Metric(1003,2003) + P(1,2)*P(2,1)*Metric(1003,2003) + P(1,1)*P(2,2)*Metric(1003,2003) + P(1,2)*P(2,2)*Metric(1003,2003) - P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003)')

VVT6 = Lorentz(name = 'VVT6',
               spins = [ 3, 3, 5 ],
               structure = 'P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) + P(2,3)*P(2003,2)*Metric(1,1003) + P(2,3)*P(1003,2)*Metric(1,2003) + P(1,3)*P(2003,1)*Metric(2,1003) + P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003) + P(1,3)*P(1003,1)*Metric(2,2003) + P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003) - P(1,1)*P(2,3)*Metric(1003,2003) - P(1,2)*P(2,3)*Metric(1003,2003) - P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003)')

VVT7 = Lorentz(name = 'VVT7',
               spins = [ 3, 3, 5 ],
               structure = 'P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) - (P(2,1)*P(2003,2)*Metric(1,1003))/2. - (P(2,1)*P(1003,2)*Metric(1,2003))/2. - P(1,2)*P(2003,1)*Metric(2,1003) + (P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003))/2. - P(1,2)*P(1003,1)*Metric(2,2003) + (P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003))/2. + (P(1,2)*P(2,1)*Metric(1003,2003))/2. - (P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003))/2.')

VVT8 = Lorentz(name = 'VVT8',
               spins = [ 3, 3, 5 ],
               structure = 'P(2,1)*P(2003,2)*Metric(1,1003) + P(2,1)*P(1003,2)*Metric(1,2003) - P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003) - P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003) - P(1,2)*P(2,1)*Metric(1003,2003) + P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003)')

VVT9 = Lorentz(name = 'VVT9',
               spins = [ 3, 3, 5 ],
               structure = 'P(1003,1)*P(2003,1)*Metric(1,2) + P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) + P(1003,2)*P(2003,2)*Metric(1,2) + 11*P(2,1)*P(2003,2)*Metric(1,1003) + 11*P(2,3)*P(2003,2)*Metric(1,1003) + 11*P(2,1)*P(1003,2)*Metric(1,2003) + 11*P(2,3)*P(1003,2)*Metric(1,2003) + 11*P(1,2)*P(2003,1)*Metric(2,1003) + 11*P(1,3)*P(2003,1)*Metric(2,1003) + 11*P(1,2)*P(1003,1)*Metric(2,2003) + 11*P(1,3)*P(1003,1)*Metric(2,2003) - 11*P(1,2)*P(2,1)*Metric(1003,2003) - (19*P(1,1)*P(2,3)*Metric(1003,2003))/2. - (19*P(1,2)*P(2,3)*Metric(1003,2003))/2. + (3*P(1,3)*P(2,3)*Metric(1003,2003))/2. - P(-1,1)**2*Metric(1,2)*Metric(1003,2003) - 2*P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003) - P(-1,2)**2*Metric(1,2)*Metric(1003,2003)')

VVT10 = Lorentz(name = 'VVT10',
                spins = [ 3, 3, 5 ],
                structure = 'P(1,2)*P(2,1)*Metric(1003,2003) + (3*P(1,3)*P(2,1)*Metric(1003,2003))/2. + (3*P(1,2)*P(2,3)*Metric(1003,2003))/2. + (3*P(1,3)*P(2,3)*Metric(1003,2003))/2. - (P(-1,1)**2*Metric(1,2)*Metric(1003,2003))/2. - (P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003))/2. - (P(-1,2)**2*Metric(1,2)*Metric(1003,2003))/2.')

VVT11 = Lorentz(name = 'VVT11',
                spins = [ 3, 3, 5 ],
                structure = 'P(1003,1)*P(2003,1)*Metric(1,2) - (P(1003,2)*P(2003,1)*Metric(1,2))/2. - (P(1003,1)*P(2003,2)*Metric(1,2))/2. + (P(1003,2)*P(2003,2)*Metric(1,2))/2. - (P(2,1)*P(2003,1)*Metric(1,1003))/8. + (P(2,3)*P(2003,1)*Metric(1,1003))/4. + (P(2,1)*P(2003,2)*Metric(1,1003))/8. - (P(2,3)*P(2003,2)*Metric(1,1003))/4. - (P(2,1)*P(1003,1)*Metric(1,2003))/8. + (P(2,3)*P(1003,1)*Metric(1,2003))/8. + (P(2,1)*P(1003,2)*Metric(1,2003))/8. - (P(2,3)*P(1003,2)*Metric(1,2003))/4. + (P(1,2)*P(2003,1)*Metric(2,1003))/8. - (P(1,3)*P(2003,1)*Metric(2,1003))/4. - (P(1,2)*P(2003,2)*Metric(2,1003))/8. + (P(1,3)*P(2003,2)*Metric(2,1003))/8. - (P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003))/4. + (P(1,2)*P(1003,1)*Metric(2,2003))/8. - (P(1,3)*P(1003,1)*Metric(2,2003))/4. - (P(1,2)*P(1003,2)*Metric(2,2003))/8. + (P(1,3)*P(1003,2)*Metric(2,2003))/8. - (P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003))/4. + P(1,2)*P(2,1)*Metric(1003,2003) + (P(1,3)*P(2,1)*Metric(1003,2003))/2. + (P(1,2)*P(2,3)*Metric(1003,2003))/2. + (P(1,3)*P(2,3)*Metric(1003,2003))/2. + (P(-1,1)**2*Metric(1,2)*Metric(1003,2003))/4. - (P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003))/4. + (P(-1,2)**2*Metric(1,2)*Metric(1003,2003))/4.')

VVT12 = Lorentz(name = 'VVT12',
                spins = [ 3, 3, 5 ],
                structure = 'P(1003,2)*P(2003,2)*Metric(1,2) - (P(2,1)*P(2003,1)*Metric(1,1003))/4. + (P(2,1)*P(2003,2)*Metric(1,1003))/4. - (P(2,3)*P(2003,2)*Metric(1,1003))/2. - (P(2,1)*P(1003,1)*Metric(1,2003))/4. + (P(2,3)*P(1003,1)*Metric(1,2003))/4. + (P(2,1)*P(1003,2)*Metric(1,2003))/4. - (P(2,3)*P(1003,2)*Metric(1,2003))/2. + (P(1,2)*P(2003,1)*Metric(2,1003))/4. - (P(1,3)*P(2003,1)*Metric(2,1003))/2. - (P(1,2)*P(2003,2)*Metric(2,1003))/4. + (P(1,3)*P(2003,2)*Metric(2,1003))/4. - (P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003))/2. + (P(1,2)*P(1003,1)*Metric(2,2003))/4. - (P(1,3)*P(1003,1)*Metric(2,2003))/2. - (P(1,2)*P(1003,2)*Metric(2,2003))/4. + (P(1,3)*P(1003,2)*Metric(2,2003))/4. - (P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003))/2. + 2*P(1,2)*P(2,1)*Metric(1003,2003) + P(1,3)*P(2,1)*Metric(1003,2003) + P(1,2)*P(2,3)*Metric(1003,2003) + P(1,3)*P(2,3)*Metric(1003,2003) + (P(-1,1)**2*Metric(1,2)*Metric(1003,2003))/2. - (P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003))/2. + (P(-1,2)**2*Metric(1,2)*Metric(1003,2003))/2.')

VVT13 = Lorentz(name = 'VVT13',
                spins = [ 3, 3, 5 ],
                structure = 'P(1003,1)*P(2003,1)*Metric(1,2) - (P(1003,2)*P(2003,1)*Metric(1,2))/2. - (P(1003,1)*P(2003,2)*Metric(1,2))/2. + P(1003,2)*P(2003,2)*Metric(1,2) - (P(2,1)*P(2003,1)*Metric(1,1003))/4. + (P(2,3)*P(2003,1)*Metric(1,1003))/4. + (P(2,1)*P(2003,2)*Metric(1,1003))/4. - (P(2,3)*P(2003,2)*Metric(1,1003))/2. - (P(2,1)*P(1003,1)*Metric(1,2003))/4. + (P(2,3)*P(1003,1)*Metric(1,2003))/4. + (P(2,1)*P(1003,2)*Metric(1,2003))/4. - (P(2,3)*P(1003,2)*Metric(1,2003))/2. + (P(1,2)*P(2003,1)*Metric(2,1003))/4. - (P(1,3)*P(2003,1)*Metric(2,1003))/2. - (P(1,2)*P(2003,2)*Metric(2,1003))/4. + (P(1,3)*P(2003,2)*Metric(2,1003))/4. - (P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003))/2. + (P(1,2)*P(1003,1)*Metric(2,2003))/4. - (P(1,3)*P(1003,1)*Metric(2,2003))/2. - (P(1,2)*P(1003,2)*Metric(2,2003))/4. + (P(1,3)*P(1003,2)*Metric(2,2003))/4. - (P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003))/2. + 2*P(1,2)*P(2,1)*Metric(1003,2003) + P(1,3)*P(2,1)*Metric(1003,2003) + P(1,2)*P(2,3)*Metric(1003,2003) + P(1,3)*P(2,3)*Metric(1003,2003) + (P(-1,1)**2*Metric(1,2)*Metric(1003,2003))/2. - (P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003))/2. + (P(-1,2)**2*Metric(1,2)*Metric(1003,2003))/2.')

VVT14 = Lorentz(name = 'VVT14',
                spins = [ 3, 3, 5 ],
                structure = 'P(1003,1)*P(2003,1)*Metric(1,2) + P(1003,2)*P(2003,1)*Metric(1,2) + P(1003,1)*P(2003,2)*Metric(1,2) + P(1003,2)*P(2003,2)*Metric(1,2) + P(2,1)*P(2003,2)*Metric(1,1003) + P(2,3)*P(2003,2)*Metric(1,1003) + P(2,1)*P(1003,2)*Metric(1,2003) + P(2,3)*P(1003,2)*Metric(1,2003) + P(1,2)*P(2003,1)*Metric(2,1003) + P(1,3)*P(2003,1)*Metric(2,1003) + P(1,2)*P(1003,1)*Metric(2,2003) + P(1,3)*P(1003,1)*Metric(2,2003) - P(1,2)*P(2,1)*Metric(1003,2003) - (3*P(1,3)*P(2,1)*Metric(1003,2003))/2. + (P(1,1)*P(2,3)*Metric(1003,2003))/2. - P(1,2)*P(2,3)*Metric(1003,2003) - (3*P(1,3)*P(2,3)*Metric(1003,2003))/2. + (P(-1,1)**2*Metric(1,2)*Metric(1003,2003))/2. + P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003) + (P(-1,2)**2*Metric(1,2)*Metric(1003,2003))/2.')

VVT15 = Lorentz(name = 'VVT15',
                spins = [ 3, 3, 5 ],
                structure = 'P(1003,1)*P(2003,1)*Metric(1,2) - (21*P(1003,2)*P(2003,1)*Metric(1,2))/2. - (21*P(1003,1)*P(2003,2)*Metric(1,2))/2. + P(1003,2)*P(2003,2)*Metric(1,2) - (5*P(2,1)*P(2003,1)*Metric(1,1003))/4. - (3*P(2,3)*P(2003,1)*Metric(1,1003))/4. + (33*P(2,1)*P(2003,2)*Metric(1,1003))/4. - (7*P(2,3)*P(2003,2)*Metric(1,1003))/2. - (5*P(2,1)*P(1003,1)*Metric(1,2003))/4. - (3*P(2,3)*P(1003,1)*Metric(1,2003))/4. + (33*P(2,1)*P(1003,2)*Metric(1,2003))/4. - (7*P(2,3)*P(1003,2)*Metric(1,2003))/2. + (33*P(1,2)*P(2003,1)*Metric(2,1003))/4. - (7*P(1,3)*P(2003,1)*Metric(2,1003))/2. - (5*P(1,2)*P(2003,2)*Metric(2,1003))/4. - (3*P(1,3)*P(2003,2)*Metric(2,1003))/4. - 3*P(-1,1)**2*Metric(1,2003)*Metric(2,1003) - 15*P(-1,1)*P(-1,2)*Metric(1,2003)*Metric(2,1003) - 3*P(-1,2)**2*Metric(1,2003)*Metric(2,1003) + (33*P(1,2)*P(1003,1)*Metric(2,2003))/4. - (7*P(1,3)*P(1003,1)*Metric(2,2003))/2. - (5*P(1,2)*P(1003,2)*Metric(2,2003))/4. - (3*P(1,3)*P(1003,2)*Metric(2,2003))/4. - 3*P(-1,1)**2*Metric(1,1003)*Metric(2,2003) - 15*P(-1,1)*P(-1,2)*Metric(1,1003)*Metric(2,2003) - 3*P(-1,2)**2*Metric(1,1003)*Metric(2,2003) - 15*P(1,2)*P(2,1)*Metric(1003,2003) + (P(1,3)*P(2,1)*Metric(1003,2003))/2. + (P(1,2)*P(2,3)*Metric(1003,2003))/2. - (5*P(1,3)*P(2,3)*Metric(1003,2003))/2. + 3*P(-1,1)**2*Metric(1,2)*Metric(1003,2003) + 21*P(-1,1)*P(-1,2)*Metric(1,2)*Metric(1003,2003) + 3*P(-1,2)**2*Metric(1,2)*Metric(1003,2003)')

UUVT1 = Lorentz(name = 'UUVT1',
                spins = [ -1, -1, 3, 5 ],
                structure = 'P(2004,1)*Metric(3,1004) + P(1004,1)*Metric(3,2004) + P(3,2)*Metric(1004,2004) + P(3,3)*Metric(1004,2004)')

SSSS1 = Lorentz(name = 'SSSS1',
                spins = [ 1, 1, 1, 1 ],
                structure = '1')

SSST1 = Lorentz(name = 'SSST1',
                spins = [ 1, 1, 1, 5 ],
                structure = 'Metric(1004,2004)')

FFST1 = Lorentz(name = 'FFST1',
                spins = [ 2, 2, 1, 5 ],
                structure = 'Metric(1004,2004)*ProjM(2,1)')

FFST2 = Lorentz(name = 'FFST2',
                spins = [ 2, 2, 1, 5 ],
                structure = 'Metric(1004,2004)*ProjP(2,1)')

FFST3 = Lorentz(name = 'FFST3',
                spins = [ 2, 2, 1, 5 ],
                structure = 'Metric(1004,2004)*ProjM(2,1) - Metric(1004,2004)*ProjP(2,1)')

FFST4 = Lorentz(name = 'FFST4',
                spins = [ 2, 2, 1, 5 ],
                structure = 'Metric(1004,2004)*ProjM(2,1) + Metric(1004,2004)*ProjP(2,1)')

FFVT1 = Lorentz(name = 'FFVT1',
                spins = [ 2, 2, 3, 5 ],
                structure = 'Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT2 = Lorentz(name = 'FFVT2',
                spins = [ 2, 2, 3, 5 ],
                structure = 'Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT3 = Lorentz(name = 'FFVT3',
                spins = [ 2, 2, 3, 5 ],
                structure = '(3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT4 = Lorentz(name = 'FFVT4',
                spins = [ 2, 2, 3, 5 ],
                structure = '-(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1)) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT5 = Lorentz(name = 'FFVT5',
                spins = [ 2, 2, 3, 5 ],
                structure = '(17*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/172. + (17*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/172. + (17*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/43. + (17*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/43. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT6 = Lorentz(name = 'FFVT6',
                spins = [ 2, 2, 3, 5 ],
                structure = '(21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/31. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT7 = Lorentz(name = 'FFVT7',
                spins = [ 2, 2, 3, 5 ],
                structure = 'Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1) + Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT8 = Lorentz(name = 'FFVT8',
                spins = [ 2, 2, 3, 5 ],
                structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1)')

FFVT9 = Lorentz(name = 'FFVT9',
                spins = [ 2, 2, 3, 5 ],
                structure = 'Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1)')

FFVT10 = Lorentz(name = 'FFVT10',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT11 = Lorentz(name = 'FFVT11',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. + (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT12 = Lorentz(name = 'FFVT12',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT13 = Lorentz(name = 'FFVT13',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT14 = Lorentz(name = 'FFVT14',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT15 = Lorentz(name = 'FFVT15',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT16 = Lorentz(name = 'FFVT16',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(-3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT17 = Lorentz(name = 'FFVT17',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. - (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT18 = Lorentz(name = 'FFVT18',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT19 = Lorentz(name = 'FFVT19',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT20 = Lorentz(name = 'FFVT20',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(-3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT21 = Lorentz(name = 'FFVT21',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/16. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/16. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT22 = Lorentz(name = 'FFVT22',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT23 = Lorentz(name = 'FFVT23',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT24 = Lorentz(name = 'FFVT24',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT25 = Lorentz(name = 'FFVT25',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1) + Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT26 = Lorentz(name = 'FFVT26',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT27 = Lorentz(name = 'FFVT27',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. - (Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. - (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. - (Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/3. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT28 = Lorentz(name = 'FFVT28',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/4. + (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/4. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT29 = Lorentz(name = 'FFVT29',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1) + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1)')

FFVT30 = Lorentz(name = 'FFVT30',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) + Gamma(3,2,1)*Metric(1004,2004) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT31 = Lorentz(name = 'FFVT31',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) + 4*Gamma(3,2,1)*Metric(1004,2004) + 2*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1) + 2*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + 2*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) + 2*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT32 = Lorentz(name = 'FFVT32',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT33 = Lorentz(name = 'FFVT33',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) - Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT34 = Lorentz(name = 'FFVT34',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) - Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT35 = Lorentz(name = 'FFVT35',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) + (13*Gamma(3,2,1)*Metric(1004,2004))/4. - (9*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/16. - (9*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/16. - (9*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/16. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - (9*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/16. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - (9*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/16. - (9*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/16. - (9*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/16. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - (9*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/16. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT36 = Lorentz(name = 'FFVT36',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) + (17*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/172. + (17*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/172. + (17*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/43. + (17*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/43. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT37 = Lorentz(name = 'FFVT37',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) + (17*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/172. + (17*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/172. + (17*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/43. + (17*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/43. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + (17*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/172. + (17*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/172. + (17*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/43. + (17*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/172. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/43. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT38 = Lorentz(name = 'FFVT38',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - (107*Gamma(3,2,1)*Metric(1004,2004))/31. + (21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/31. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + (21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/31. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT39 = Lorentz(name = 'FFVT39',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - (34*Gamma(3,2,1)*Metric(1004,2004))/5. + (9*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/40. + (9*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/40. + (9*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/40. - (7*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/10. + (9*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/40. - (7*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/10. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + (9*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/40. + (9*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/40. + (9*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/40. - (7*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/10. + (9*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/40. - (7*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/10. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1)')

FFVT40 = Lorentz(name = 'FFVT40',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1) + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT41 = Lorentz(name = 'FFVT41',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/4. + (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/4. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - (Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1))/2. - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT42 = Lorentz(name = 'FFVT42',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT43 = Lorentz(name = 'FFVT43',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT44 = Lorentz(name = 'FFVT44',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) - Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT45 = Lorentz(name = 'FFVT45',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(-3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/4. + (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/4. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) - 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT46 = Lorentz(name = 'FFVT46',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - (107*Gamma(3,2,1)*Metric(1004,2004))/31. - (12*Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/31. - (12*Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/31. + (24*Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1))/31. + (21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/31. + (19*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1))/31. - (12*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1))/31. + (24*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1))/31.')

FFVT47 = Lorentz(name = 'FFVT47',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - (107*Gamma(3,2,1)*Metric(1004,2004))/31. + (21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/31. + (19*Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/31. - (12*Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/31. + (24*Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1))/31. + (21*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/124. + (21*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1))/31. + (21*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/124. - (12*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1))/31. + (19*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1))/31. - (12*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1))/31. + (24*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1))/31.')

FFVT48 = Lorentz(name = 'FFVT48',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT49 = Lorentz(name = 'FFVT49',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - (Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT50 = Lorentz(name = 'FFVT50',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 2*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT51 = Lorentz(name = 'FFVT51',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT52 = Lorentz(name = 'FFVT52',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '-(Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT53 = Lorentz(name = 'FFVT53',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(-3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/8. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/8. - (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT54 = Lorentz(name = 'FFVT54',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. + (Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/4. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + 2*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) + 2*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) + 2*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) + 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) + 2*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) + 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT55 = Lorentz(name = 'FFVT55',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/4. + (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/4. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/2. - (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/2. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + 3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1) + 3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1) + 3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1) + 6*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) + 3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1) + 6*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 2*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT56 = Lorentz(name = 'FFVT56',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + (Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1))/4. + (Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1))/4. + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + 2*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) + 2*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) + Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT57 = Lorentz(name = 'FFVT57',
                 spins = [ 2, 2, 3, 5 ],
                 structure = '(3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. + (3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1))/2. + Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) + Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1) + Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) + 6*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) + 6*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) + 4*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) + 4*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 4*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT58 = Lorentz(name = 'FFVT58',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 3*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 6*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

FFVT59 = Lorentz(name = 'FFVT59',
                 spins = [ 2, 2, 3, 5 ],
                 structure = 'Gamma(1004,2,1)*Metric(3,2004) - 2*Gamma(3,2,1)*Metric(1004,2004) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjM(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjM(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjM(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjM(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjM(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjM(-1,1) - 3*Gamma(1004,2,-1)*Metric(3,2004)*ProjM(-1,1) + 6*Gamma(3,2,-1)*Metric(1004,2004)*ProjM(-1,1) - (3*Gamma(3,2,-3)*Gamma(1004,-2,-1)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,-2,-1)*Gamma(1004,2,-3)*Gamma(2004,-3,-2)*ProjP(-1,1))/2. - (3*Gamma(3,2,-3)*Gamma(1004,-3,-2)*Gamma(2004,-2,-1)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,2,-3)*Gamma(2004,-2,-1)*ProjP(-1,1) - (3*Gamma(3,-2,-1)*Gamma(1004,-3,-2)*Gamma(2004,2,-3)*ProjP(-1,1))/2. - 3*Gamma(3,-3,-2)*Gamma(1004,-2,-1)*Gamma(2004,2,-3)*ProjP(-1,1) - 2*Gamma(2004,2,-1)*Metric(3,1004)*ProjP(-1,1) - 3*Gamma(1004,2,-1)*Metric(3,2004)*ProjP(-1,1) + 6*Gamma(3,2,-1)*Metric(1004,2004)*ProjP(-1,1)')

VSST1 = Lorentz(name = 'VSST1',
                spins = [ 3, 1, 1, 5 ],
                structure = 'P(2004,2)*Metric(1,1004) - P(2004,3)*Metric(1,1004) + P(1004,2)*Metric(1,2004) - P(1004,3)*Metric(1,2004) - P(1,2)*Metric(1004,2004) + P(1,3)*Metric(1004,2004)')

VVSS1 = Lorentz(name = 'VVSS1',
                spins = [ 3, 3, 1, 1 ],
                structure = 'Metric(1,2)')

VVST1 = Lorentz(name = 'VVST1',
                spins = [ 3, 3, 1, 5 ],
                structure = 'Metric(1,2004)*Metric(2,1004) + Metric(1,1004)*Metric(2,2004) - Metric(1,2)*Metric(1004,2004)')

VVVV1 = Lorentz(name = 'VVVV1',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Epsilon(1,2,3,4)')

VVVV2 = Lorentz(name = 'VVVV2',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,4)*Metric(2,3)')

VVVV3 = Lorentz(name = 'VVVV3',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,3)*Metric(2,4)')

VVVV4 = Lorentz(name = 'VVVV4',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,4)*Metric(2,3) - Metric(1,3)*Metric(2,4)')

VVVV5 = Lorentz(name = 'VVVV5',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,2)*Metric(3,4)')

VVVV6 = Lorentz(name = 'VVVV6',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) - 2*Metric(1,2)*Metric(3,4)')

VVVV7 = Lorentz(name = 'VVVV7',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,4)*Metric(2,3) - Metric(1,2)*Metric(3,4)')

VVVV8 = Lorentz(name = 'VVVV8',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,3)*Metric(2,4) - Metric(1,2)*Metric(3,4)')

VVVV9 = Lorentz(name = 'VVVV9',
                spins = [ 3, 3, 3, 3 ],
                structure = 'Metric(1,4)*Metric(2,3) - (Metric(1,3)*Metric(2,4))/2. - (Metric(1,2)*Metric(3,4))/2.')

VVVV10 = Lorentz(name = 'VVVV10',
                 spins = [ 3, 3, 3, 3 ],
                 structure = 'Metric(1,4)*Metric(2,3) + Metric(1,3)*Metric(2,4) + Metric(1,2)*Metric(3,4)')

VVVT1 = Lorentz(name = 'VVVT1',
                spins = [ 3, 3, 3, 5 ],
                structure = '-(Epsilon(2,3,2004,-1)*P(-1,1)*Metric(1,1004)) - Epsilon(2,3,1004,-1)*P(-1,1)*Metric(1,2004) + Epsilon(1,3,2004,-1)*P(-1,1)*Metric(2,1004) + Epsilon(1,3,1004,-1)*P(-1,1)*Metric(2,2004) - Epsilon(1,2,2004,-1)*P(-1,1)*Metric(3,1004) - Epsilon(1,2,1004,-1)*P(-1,1)*Metric(3,2004) + 2*Epsilon(1,2,3,-1)*P(-1,1)*Metric(1004,2004)')

VVVT2 = Lorentz(name = 'VVVT2',
                spins = [ 3, 3, 3, 5 ],
                structure = '-(Epsilon(2,3,2004,-1)*P(-1,1)*Metric(1,1004)) + (3*Epsilon(2,3,2004,-1)*P(-1,2)*Metric(1,1004))/4. + (21*Epsilon(2,3,2004,-1)*P(-1,3)*Metric(1,1004))/4. - Epsilon(2,3,1004,-1)*P(-1,1)*Metric(1,2004) + (3*Epsilon(2,3,1004,-1)*P(-1,2)*Metric(1,2004))/4. + (21*Epsilon(2,3,1004,-1)*P(-1,3)*Metric(1,2004))/4. + (7*Epsilon(1,3,2004,-1)*P(-1,1)*Metric(2,1004))/4. + (21*Epsilon(1,3,2004,-1)*P(-1,3)*Metric(2,1004))/4. + (7*Epsilon(1,3,1004,-1)*P(-1,1)*Metric(2,2004))/4. + (21*Epsilon(1,3,1004,-1)*P(-1,3)*Metric(2,2004))/4. - (Epsilon(1,2,2004,-1)*P(-1,1)*Metric(3,1004))/4. + (21*Epsilon(1,2,2004,-1)*P(-1,2)*Metric(3,1004))/4. - (Epsilon(1,2,1004,-1)*P(-1,1)*Metric(3,2004))/4. + (21*Epsilon(1,2,1004,-1)*P(-1,2)*Metric(3,2004))/4. - 10*Epsilon(1,2,3,-1)*P(-1,1)*Metric(1004,2004) - 12*Epsilon(1,2,3,-1)*P(-1,2)*Metric(1004,2004)')

VVVT3 = Lorentz(name = 'VVVT3',
                spins = [ 3, 3, 3, 5 ],
                structure = 'Epsilon(1,2,3,2004)*P(1004,3) + Epsilon(1,2,3,1004)*P(2004,3) + (21*Epsilon(2,3,2004,-1)*P(-1,2)*Metric(1,1004))/4. + (7*Epsilon(2,3,2004,-1)*P(-1,3)*Metric(1,1004))/4. + (21*Epsilon(2,3,1004,-1)*P(-1,2)*Metric(1,2004))/4. + (7*Epsilon(2,3,1004,-1)*P(-1,3)*Metric(1,2004))/4. + (21*Epsilon(1,3,2004,-1)*P(-1,1)*Metric(2,1004))/4. - (Epsilon(1,3,2004,-1)*P(-1,3)*Metric(2,1004))/4. + (21*Epsilon(1,3,1004,-1)*P(-1,1)*Metric(2,2004))/4. - (Epsilon(1,3,1004,-1)*P(-1,3)*Metric(2,2004))/4. - (3*Epsilon(1,2,2004,-1)*P(-1,1)*Metric(3,1004))/4. - (21*Epsilon(1,2,2004,-1)*P(-1,2)*Metric(3,1004))/4. + Epsilon(1,2,2004,-1)*P(-1,3)*Metric(3,1004) - (3*Epsilon(1,2,1004,-1)*P(-1,1)*Metric(3,2004))/4. - (21*Epsilon(1,2,1004,-1)*P(-1,2)*Metric(3,2004))/4. + Epsilon(1,2,1004,-1)*P(-1,3)*Metric(3,2004) + 12*Epsilon(1,2,3,-1)*P(-1,1)*Metric(1004,2004) + 10*Epsilon(1,2,3,-1)*P(-1,3)*Metric(1004,2004)')

VVVT4 = Lorentz(name = 'VVVT4',
                spins = [ 3, 3, 3, 5 ],
                structure = 'Epsilon(1,2,3,2004)*P(1004,3) + Epsilon(1,2,3,1004)*P(2004,3) + Epsilon(2,3,2004,-1)*P(-1,3)*Metric(1,1004) + Epsilon(2,3,1004,-1)*P(-1,3)*Metric(1,2004) - Epsilon(1,3,2004,-1)*P(-1,3)*Metric(2,1004) - Epsilon(1,3,1004,-1)*P(-1,3)*Metric(2,2004) + Epsilon(1,2,2004,-1)*P(-1,3)*Metric(3,1004) + Epsilon(1,2,1004,-1)*P(-1,3)*Metric(3,2004) - 2*Epsilon(1,2,3,-1)*P(-1,3)*Metric(1004,2004)')

VVVT5 = Lorentz(name = 'VVVT5',
                spins = [ 3, 3, 3, 5 ],
                structure = 'P(3,1)*Metric(1,2)*Metric(1004,2004) - P(3,2)*Metric(1,2)*Metric(1004,2004) - P(2,1)*Metric(1,3)*Metric(1004,2004) + P(2,3)*Metric(1,3)*Metric(1004,2004) + P(1,2)*Metric(2,3)*Metric(1004,2004) - P(1,3)*Metric(2,3)*Metric(1004,2004)')

VVVT6 = Lorentz(name = 'VVVT6',
                spins = [ 3, 3, 3, 5 ],
                structure = 'P(2004,2)*Metric(1,1004)*Metric(2,3) - P(2004,3)*Metric(1,1004)*Metric(2,3) + P(1004,2)*Metric(1,2004)*Metric(2,3) - P(1004,3)*Metric(1,2004)*Metric(2,3) - P(2004,1)*Metric(1,3)*Metric(2,1004) + P(2004,3)*Metric(1,3)*Metric(2,1004) + (13*P(3,1)*Metric(1,2004)*Metric(2,1004))/15. - (13*P(3,2)*Metric(1,2004)*Metric(2,1004))/15. - P(1004,1)*Metric(1,3)*Metric(2,2004) + P(1004,3)*Metric(1,3)*Metric(2,2004) + (13*P(3,1)*Metric(1,1004)*Metric(2,2004))/15. - (13*P(3,2)*Metric(1,1004)*Metric(2,2004))/15. + P(2004,1)*Metric(1,2)*Metric(3,1004) - P(2004,2)*Metric(1,2)*Metric(3,1004) - (13*P(2,1)*Metric(1,2004)*Metric(3,1004))/15. + (13*P(2,3)*Metric(1,2004)*Metric(3,1004))/15. + (13*P(1,2)*Metric(2,2004)*Metric(3,1004))/15. - (13*P(1,3)*Metric(2,2004)*Metric(3,1004))/15. + P(1004,1)*Metric(1,2)*Metric(3,2004) - P(1004,2)*Metric(1,2)*Metric(3,2004) - (13*P(2,1)*Metric(1,1004)*Metric(3,2004))/15. + (13*P(2,3)*Metric(1,1004)*Metric(3,2004))/15. + (13*P(1,2)*Metric(2,1004)*Metric(3,2004))/15. - (13*P(1,3)*Metric(2,1004)*Metric(3,2004))/15. + (2*P(3,1)*Metric(1,2)*Metric(1004,2004))/5. - (2*P(3,2)*Metric(1,2)*Metric(1004,2004))/5. - (2*P(2,1)*Metric(1,3)*Metric(1004,2004))/5. + (2*P(2,3)*Metric(1,3)*Metric(1004,2004))/5. + (2*P(1,2)*Metric(2,3)*Metric(1004,2004))/5. - (2*P(1,3)*Metric(2,3)*Metric(1004,2004))/5.')

VVVT7 = Lorentz(name = 'VVVT7',
                spins = [ 3, 3, 3, 5 ],
                structure = 'P(2004,2)*Metric(1,1004)*Metric(2,3) - P(2004,3)*Metric(1,1004)*Metric(2,3) + P(1004,2)*Metric(1,2004)*Metric(2,3) - P(1004,3)*Metric(1,2004)*Metric(2,3) - P(2004,1)*Metric(1,3)*Metric(2,1004) + P(2004,3)*Metric(1,3)*Metric(2,1004) + P(3,1)*Metric(1,2004)*Metric(2,1004) - P(3,2)*Metric(1,2004)*Metric(2,1004) - P(1004,1)*Metric(1,3)*Metric(2,2004) + P(1004,3)*Metric(1,3)*Metric(2,2004) + P(3,1)*Metric(1,1004)*Metric(2,2004) - P(3,2)*Metric(1,1004)*Metric(2,2004) + P(2004,1)*Metric(1,2)*Metric(3,1004) - P(2004,2)*Metric(1,2)*Metric(3,1004) - P(2,1)*Metric(1,2004)*Metric(3,1004) + P(2,3)*Metric(1,2004)*Metric(3,1004) + P(1,2)*Metric(2,2004)*Metric(3,1004) - P(1,3)*Metric(2,2004)*Metric(3,1004) + P(1004,1)*Metric(1,2)*Metric(3,2004) - P(1004,2)*Metric(1,2)*Metric(3,2004) - P(2,1)*Metric(1,1004)*Metric(3,2004) + P(2,3)*Metric(1,1004)*Metric(3,2004) + P(1,2)*Metric(2,1004)*Metric(3,2004) - P(1,3)*Metric(2,1004)*Metric(3,2004) - P(3,1)*Metric(1,2)*Metric(1004,2004) + P(3,2)*Metric(1,2)*Metric(1004,2004) + P(2,1)*Metric(1,3)*Metric(1004,2004) - P(2,3)*Metric(1,3)*Metric(1004,2004) - P(1,2)*Metric(2,3)*Metric(1004,2004) + P(1,3)*Metric(2,3)*Metric(1004,2004)')

VVVT8 = Lorentz(name = 'VVVT8',
                spins = [ 3, 3, 3, 5 ],
                structure = 'P(2004,2)*Metric(1,1004)*Metric(2,3) - P(2004,3)*Metric(1,1004)*Metric(2,3) + P(1004,2)*Metric(1,2004)*Metric(2,3) - P(1004,3)*Metric(1,2004)*Metric(2,3) - P(2004,1)*Metric(1,3)*Metric(2,1004) + P(2004,3)*Metric(1,3)*Metric(2,1004) + (159*P(3,1)*Metric(1,2004)*Metric(2,1004))/185. - (159*P(3,2)*Metric(1,2004)*Metric(2,1004))/185. - P(1004,1)*Metric(1,3)*Metric(2,2004) + P(1004,3)*Metric(1,3)*Metric(2,2004) + (159*P(3,1)*Metric(1,1004)*Metric(2,2004))/185. - (159*P(3,2)*Metric(1,1004)*Metric(2,2004))/185. + P(2004,1)*Metric(1,2)*Metric(3,1004) - P(2004,2)*Metric(1,2)*Metric(3,1004) - (159*P(2,1)*Metric(1,2004)*Metric(3,1004))/185. + (159*P(2,3)*Metric(1,2004)*Metric(3,1004))/185. + (159*P(1,2)*Metric(2,2004)*Metric(3,1004))/185. - (159*P(1,3)*Metric(2,2004)*Metric(3,1004))/185. + P(1004,1)*Metric(1,2)*Metric(3,2004) - P(1004,2)*Metric(1,2)*Metric(3,2004) - (159*P(2,1)*Metric(1,1004)*Metric(3,2004))/185. + (159*P(2,3)*Metric(1,1004)*Metric(3,2004))/185. + (159*P(1,2)*Metric(2,1004)*Metric(3,2004))/185. - (159*P(1,3)*Metric(2,1004)*Metric(3,2004))/185. - (202*P(3,1)*Metric(1,2)*Metric(1004,2004))/185. + (202*P(3,2)*Metric(1,2)*Metric(1004,2004))/185. + (202*P(2,1)*Metric(1,3)*Metric(1004,2004))/185. - (202*P(2,3)*Metric(1,3)*Metric(1004,2004))/185. - (202*P(1,2)*Metric(2,3)*Metric(1004,2004))/185. + (202*P(1,3)*Metric(2,3)*Metric(1004,2004))/185.')

SSSST1 = Lorentz(name = 'SSSST1',
                 spins = [ 1, 1, 1, 1, 5 ],
                 structure = 'Metric(1005,2005)')

VVSST1 = Lorentz(name = 'VVSST1',
                 spins = [ 3, 3, 1, 1, 5 ],
                 structure = 'Metric(1,2005)*Metric(2,1005) + Metric(1,1005)*Metric(2,2005) - Metric(1,2)*Metric(1005,2005)')

VVVVT1 = Lorentz(name = 'VVVVT1',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4)')

VVVVT2 = Lorentz(name = 'VVVVT2',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,1005)*Metric(2,2005)*Metric(3,4)')

VVVVT3 = Lorentz(name = 'VVVVT3',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,2005)*Metric(2,4)*Metric(3,1005)')

VVVVT4 = Lorentz(name = 'VVVVT4',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,4)*Metric(2,2005)*Metric(3,1005)')

VVVVT5 = Lorentz(name = 'VVVVT5',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,1005)*Metric(2,4)*Metric(3,2005)')

VVVVT6 = Lorentz(name = 'VVVVT6',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,4)*Metric(2,1005)*Metric(3,2005)')

VVVVT7 = Lorentz(name = 'VVVVT7',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,2005)*Metric(2,3)*Metric(4,1005)')

VVVVT8 = Lorentz(name = 'VVVVT8',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,3)*Metric(2,2005)*Metric(4,1005)')

VVVVT9 = Lorentz(name = 'VVVVT9',
                 spins = [ 3, 3, 3, 3, 5 ],
                 structure = 'Metric(1,2)*Metric(3,2005)*Metric(4,1005)')

VVVVT10 = Lorentz(name = 'VVVVT10',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,1005)*Metric(2,3)*Metric(4,2005)')

VVVVT11 = Lorentz(name = 'VVVVT11',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,3)*Metric(2,1005)*Metric(4,2005)')

VVVVT12 = Lorentz(name = 'VVVVT12',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2)*Metric(3,1005)*Metric(4,2005)')

VVVVT13 = Lorentz(name = 'VVVVT13',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,4)*Metric(2,3)*Metric(1005,2005)')

VVVVT14 = Lorentz(name = 'VVVVT14',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,3)*Metric(2,4)*Metric(1005,2005)')

VVVVT15 = Lorentz(name = 'VVVVT15',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT16 = Lorentz(name = 'VVVVT16',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Epsilon(2,3,4,2005)*Metric(1,1005) + Epsilon(2,3,4,1005)*Metric(1,2005) - Epsilon(1,3,4,2005)*Metric(2,1005) - Epsilon(1,3,4,1005)*Metric(2,2005) + Epsilon(1,2,4,2005)*Metric(3,1005) + Epsilon(1,2,4,1005)*Metric(3,2005) - Epsilon(1,2,3,2005)*Metric(4,1005) - Epsilon(1,2,3,1005)*Metric(4,2005) + 2*Epsilon(1,2,3,4)*Metric(1005,2005)')

VVVVT17 = Lorentz(name = 'VVVVT17',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Epsilon(2,3,4,2005)*Metric(1,1005) + Epsilon(2,3,4,1005)*Metric(1,2005) - Epsilon(1,3,4,2005)*Metric(2,1005) - Epsilon(1,3,4,1005)*Metric(2,2005) + Epsilon(1,2,4,2005)*Metric(3,1005) + Epsilon(1,2,4,1005)*Metric(3,2005) + (5*Epsilon(1,2,3,2005)*Metric(4,1005))/3. + (5*Epsilon(1,2,3,1005)*Metric(4,2005))/3. + (26*Epsilon(1,2,3,4)*Metric(1005,2005))/3.')

VVVVT18 = Lorentz(name = 'VVVVT18',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,4)*Metric(3,1005) - Metric(1,4)*Metric(2,2005)*Metric(3,1005) + Metric(1,1005)*Metric(2,4)*Metric(3,2005) - Metric(1,4)*Metric(2,1005)*Metric(3,2005) - Metric(1,2005)*Metric(2,3)*Metric(4,1005) + Metric(1,3)*Metric(2,2005)*Metric(4,1005) - Metric(1,1005)*Metric(2,3)*Metric(4,2005) + Metric(1,3)*Metric(2,1005)*Metric(4,2005) + Metric(1,4)*Metric(2,3)*Metric(1005,2005) - Metric(1,3)*Metric(2,4)*Metric(1005,2005)')

VVVVT19 = Lorentz(name = 'VVVVT19',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) + Metric(1,2005)*Metric(2,4)*Metric(3,1005) + Metric(1,4)*Metric(2,2005)*Metric(3,1005) + Metric(1,1005)*Metric(2,4)*Metric(3,2005) + Metric(1,4)*Metric(2,1005)*Metric(3,2005) + Metric(1,2005)*Metric(2,3)*Metric(4,1005) + Metric(1,3)*Metric(2,2005)*Metric(4,1005) + Metric(1,2)*Metric(3,2005)*Metric(4,1005) + Metric(1,1005)*Metric(2,3)*Metric(4,2005) + Metric(1,3)*Metric(2,1005)*Metric(4,2005) + Metric(1,2)*Metric(3,1005)*Metric(4,2005) - (6*Metric(1,4)*Metric(2,3)*Metric(1005,2005))/5. - (6*Metric(1,3)*Metric(2,4)*Metric(1005,2005))/5. - (6*Metric(1,2)*Metric(3,4)*Metric(1005,2005))/5.')

VVVVT20 = Lorentz(name = 'VVVVT20',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) - Metric(1,4)*Metric(2,2005)*Metric(3,1005) - Metric(1,4)*Metric(2,1005)*Metric(3,2005) - Metric(1,2005)*Metric(2,3)*Metric(4,1005) + Metric(1,2)*Metric(3,2005)*Metric(4,1005) - Metric(1,1005)*Metric(2,3)*Metric(4,2005) + Metric(1,2)*Metric(3,1005)*Metric(4,2005) + Metric(1,4)*Metric(2,3)*Metric(1005,2005) - Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT21 = Lorentz(name = 'VVVVT21',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) + Metric(1,2005)*Metric(2,4)*Metric(3,1005) + Metric(1,4)*Metric(2,2005)*Metric(3,1005) + Metric(1,1005)*Metric(2,4)*Metric(3,2005) + Metric(1,4)*Metric(2,1005)*Metric(3,2005) + Metric(1,2005)*Metric(2,3)*Metric(4,1005) + Metric(1,3)*Metric(2,2005)*Metric(4,1005) + Metric(1,2)*Metric(3,2005)*Metric(4,1005) + Metric(1,1005)*Metric(2,3)*Metric(4,2005) + Metric(1,3)*Metric(2,1005)*Metric(4,2005) + Metric(1,2)*Metric(3,1005)*Metric(4,2005) - Metric(1,4)*Metric(2,3)*Metric(1005,2005) - Metric(1,3)*Metric(2,4)*Metric(1005,2005) - Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT22 = Lorentz(name = 'VVVVT22',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) + Metric(1,2005)*Metric(2,4)*Metric(3,1005) - 2*Metric(1,4)*Metric(2,2005)*Metric(3,1005) + Metric(1,1005)*Metric(2,4)*Metric(3,2005) - 2*Metric(1,4)*Metric(2,1005)*Metric(3,2005) - 2*Metric(1,2005)*Metric(2,3)*Metric(4,1005) + Metric(1,3)*Metric(2,2005)*Metric(4,1005) + Metric(1,2)*Metric(3,2005)*Metric(4,1005) - 2*Metric(1,1005)*Metric(2,3)*Metric(4,2005) + Metric(1,3)*Metric(2,1005)*Metric(4,2005) + Metric(1,2)*Metric(3,1005)*Metric(4,2005) + 2*Metric(1,4)*Metric(2,3)*Metric(1005,2005) - Metric(1,3)*Metric(2,4)*Metric(1005,2005) - Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT23 = Lorentz(name = 'VVVVT23',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) - (Metric(1,2005)*Metric(2,4)*Metric(3,1005))/2. - (Metric(1,4)*Metric(2,2005)*Metric(3,1005))/2. - (Metric(1,1005)*Metric(2,4)*Metric(3,2005))/2. - (Metric(1,4)*Metric(2,1005)*Metric(3,2005))/2. - (Metric(1,2005)*Metric(2,3)*Metric(4,1005))/2. - (Metric(1,3)*Metric(2,2005)*Metric(4,1005))/2. + Metric(1,2)*Metric(3,2005)*Metric(4,1005) - (Metric(1,1005)*Metric(2,3)*Metric(4,2005))/2. - (Metric(1,3)*Metric(2,1005)*Metric(4,2005))/2. + Metric(1,2)*Metric(3,1005)*Metric(4,2005) + (Metric(1,4)*Metric(2,3)*Metric(1005,2005))/2. + (Metric(1,3)*Metric(2,4)*Metric(1005,2005))/2. - Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT24 = Lorentz(name = 'VVVVT24',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Metric(1,2005)*Metric(2,1005)*Metric(3,4) + Metric(1,1005)*Metric(2,2005)*Metric(3,4) - Metric(1,2005)*Metric(2,4)*Metric(3,1005) - Metric(1,1005)*Metric(2,4)*Metric(3,2005) - Metric(1,3)*Metric(2,2005)*Metric(4,1005) + Metric(1,2)*Metric(3,2005)*Metric(4,1005) - Metric(1,3)*Metric(2,1005)*Metric(4,2005) + Metric(1,2)*Metric(3,1005)*Metric(4,2005) + Metric(1,3)*Metric(2,4)*Metric(1005,2005) - Metric(1,2)*Metric(3,4)*Metric(1005,2005)')

VVVVT25 = Lorentz(name = 'VVVVT25',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Epsilon(2,3,4,2005)*Metric(1,1005) + Epsilon(2,3,4,1005)*Metric(1,2005) - (5*Epsilon(1,3,4,2005)*Metric(2,1005))/9. - (5*Epsilon(1,3,4,1005)*Metric(2,2005))/9. + (2*complex(0,1)*Metric(1,2005)*Metric(2,1005)*Metric(3,4))/9. + (2*complex(0,1)*Metric(1,1005)*Metric(2,2005)*Metric(3,4))/9. + (7*Epsilon(1,2,4,2005)*Metric(3,1005))/9. + (2*complex(0,1)*Metric(1,2005)*Metric(2,4)*Metric(3,1005))/9. + (2*complex(0,1)*Metric(1,4)*Metric(2,2005)*Metric(3,1005))/9. + (7*Epsilon(1,2,4,1005)*Metric(3,2005))/9. + (2*complex(0,1)*Metric(1,1005)*Metric(2,4)*Metric(3,2005))/9. + (2*complex(0,1)*Metric(1,4)*Metric(2,1005)*Metric(3,2005))/9. - (7*Epsilon(1,2,3,2005)*Metric(4,1005))/9. + (2*complex(0,1)*Metric(1,2005)*Metric(2,3)*Metric(4,1005))/9. + (2*complex(0,1)*Metric(1,3)*Metric(2,2005)*Metric(4,1005))/9. + (2*complex(0,1)*Metric(1,2)*Metric(3,2005)*Metric(4,1005))/9. - (7*Epsilon(1,2,3,1005)*Metric(4,2005))/9. + (2*complex(0,1)*Metric(1,1005)*Metric(2,3)*Metric(4,2005))/9. + (2*complex(0,1)*Metric(1,3)*Metric(2,1005)*Metric(4,2005))/9. + (2*complex(0,1)*Metric(1,2)*Metric(3,1005)*Metric(4,2005))/9. - (34*Epsilon(1,2,3,4)*Metric(1005,2005))/9. - (2*complex(0,1)*Metric(1,4)*Metric(2,3)*Metric(1005,2005))/9. - (2*complex(0,1)*Metric(1,3)*Metric(2,4)*Metric(1005,2005))/9. - (2*complex(0,1)*Metric(1,2)*Metric(3,4)*Metric(1005,2005))/9.')

VVVVT26 = Lorentz(name = 'VVVVT26',
                  spins = [ 3, 3, 3, 3, 5 ],
                  structure = 'Epsilon(2,3,4,2005)*Metric(1,1005) + Epsilon(2,3,4,1005)*Metric(1,2005) - (5*Epsilon(1,3,4,2005)*Metric(2,1005))/9. - (5*Epsilon(1,3,4,1005)*Metric(2,2005))/9. - (2*complex(0,1)*Metric(1,2005)*Metric(2,1005)*Metric(3,4))/9. - (2*complex(0,1)*Metric(1,1005)*Metric(2,2005)*Metric(3,4))/9. + (7*Epsilon(1,2,4,2005)*Metric(3,1005))/9. - (2*complex(0,1)*Metric(1,2005)*Metric(2,4)*Metric(3,1005))/9. - (2*complex(0,1)*Metric(1,4)*Metric(2,2005)*Metric(3,1005))/9. + (7*Epsilon(1,2,4,1005)*Metric(3,2005))/9. - (2*complex(0,1)*Metric(1,1005)*Metric(2,4)*Metric(3,2005))/9. - (2*complex(0,1)*Metric(1,4)*Metric(2,1005)*Metric(3,2005))/9. - (7*Epsilon(1,2,3,2005)*Metric(4,1005))/9. - (2*complex(0,1)*Metric(1,2005)*Metric(2,3)*Metric(4,1005))/9. - (2*complex(0,1)*Metric(1,3)*Metric(2,2005)*Metric(4,1005))/9. - (2*complex(0,1)*Metric(1,2)*Metric(3,2005)*Metric(4,1005))/9. - (7*Epsilon(1,2,3,1005)*Metric(4,2005))/9. - (2*complex(0,1)*Metric(1,1005)*Metric(2,3)*Metric(4,2005))/9. - (2*complex(0,1)*Metric(1,3)*Metric(2,1005)*Metric(4,2005))/9. - (2*complex(0,1)*Metric(1,2)*Metric(3,1005)*Metric(4,2005))/9. - (34*Epsilon(1,2,3,4)*Metric(1005,2005))/9. + (2*complex(0,1)*Metric(1,4)*Metric(2,3)*Metric(1005,2005))/9. + (2*complex(0,1)*Metric(1,3)*Metric(2,4)*Metric(1005,2005))/9. + (2*complex(0,1)*Metric(1,2)*Metric(3,4)*Metric(1005,2005))/9.')

