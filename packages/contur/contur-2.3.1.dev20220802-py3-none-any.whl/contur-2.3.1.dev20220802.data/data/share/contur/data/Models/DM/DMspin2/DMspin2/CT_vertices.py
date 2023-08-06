# This file was automatically created by FeynRules 2.4.43
# Mathematica version: 10.1.0  for Mac OS X x86 (64-bit) (March 24, 2015)
# Date: Wed 1 Jun 2016 20:28:09


from .object_library import all_vertices, all_CTvertices, Vertex, CTVertex
from . import particles as P
from . import CT_couplings as C
from . import lorentz as L


V_1 = CTVertex(name = 'V_1',
               type = 'R2',
               particles = [ P.g, P.g, P.g ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVV2 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(0,0,0):C.R2GC_402_120,(0,0,1):C.R2GC_402_121})

V_2 = CTVertex(name = 'V_2',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.g ],
               color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
               lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(0,1,0):C.R2GC_379_104,(0,1,1):C.R2GC_379_105,(2,1,0):C.R2GC_379_104,(2,1,1):C.R2GC_379_105,(6,1,0):C.R2GC_406_128,(6,1,1):C.R2GC_406_129,(7,1,0):C.R2GC_405_126,(7,1,1):C.R2GC_405_127,(5,1,0):C.R2GC_377_100,(5,1,1):C.R2GC_377_101,(1,1,0):C.R2GC_377_100,(1,1,1):C.R2GC_377_101,(4,1,0):C.R2GC_377_100,(4,1,1):C.R2GC_377_101,(3,1,0):C.R2GC_377_100,(3,1,1):C.R2GC_377_101,(8,1,0):C.R2GC_378_102,(8,1,1):C.R2GC_378_103,(11,0,0):C.R2GC_381_107,(11,0,1):C.R2GC_381_108,(10,0,0):C.R2GC_381_107,(10,0,1):C.R2GC_381_108,(9,0,1):C.R2GC_380_106,(0,2,0):C.R2GC_379_104,(0,2,1):C.R2GC_379_105,(2,2,0):C.R2GC_379_104,(2,2,1):C.R2GC_379_105,(6,2,0):C.R2GC_404_124,(6,2,1):C.R2GC_404_125,(8,2,0):C.R2GC_405_126,(8,2,1):C.R2GC_405_127,(5,2,0):C.R2GC_377_100,(5,2,1):C.R2GC_377_101,(1,2,0):C.R2GC_377_100,(1,2,1):C.R2GC_377_101,(7,2,0):C.R2GC_378_102,(7,2,1):C.R2GC_378_103,(4,2,0):C.R2GC_377_100,(4,2,1):C.R2GC_377_101,(3,2,0):C.R2GC_377_100,(3,2,1):C.R2GC_377_101,(0,3,0):C.R2GC_379_104,(0,3,1):C.R2GC_379_105,(2,3,0):C.R2GC_379_104,(2,3,1):C.R2GC_379_105,(7,3,0):C.R2GC_403_122,(7,3,1):C.R2GC_403_123,(8,3,0):C.R2GC_403_122,(8,3,1):C.R2GC_403_123,(5,3,0):C.R2GC_377_100,(5,3,1):C.R2GC_377_101,(1,3,0):C.R2GC_377_100,(1,3,1):C.R2GC_377_101,(4,3,0):C.R2GC_377_100,(4,3,1):C.R2GC_377_101,(3,3,0):C.R2GC_377_100,(3,3,1):C.R2GC_377_101})

V_3 = CTVertex(name = 'V_3',
               type = 'R2',
               particles = [ P.b__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_416_133})

V_4 = CTVertex(name = 'V_4',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_417_134})

V_5 = CTVertex(name = 'V_5',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS2 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_418_135})

V_6 = CTVertex(name = 'V_6',
               type = 'R2',
               particles = [ P.g, P.g, P.Y2 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.VVT1, L.VVT10, L.VVT11, L.VVT12, L.VVT13, L.VVT15, L.VVT3 ],
               loop_particles = [ [ [P.b], [P.c], [P.u] ], [ [P.d], [P.s] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
               couplings = {(0,4,0):C.R2GC_276_47,(0,4,4):C.R2GC_280_53,(0,2,1):C.R2GC_276_47,(0,5,2):C.R2GC_170_2,(0,6,4):C.R2GC_177_8,(0,1,3):C.R2GC_170_2,(0,3,1):C.R2GC_500_162,(0,0,4):C.R2GC_179_10})

V_7 = CTVertex(name = 'V_7',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.Y2 ],
               color = [ 'd(1,2,3)', 'f(1,2,3)' ],
               lorentz = [ L.VVVT2, L.VVVT5, L.VVVT6, L.VVVT8 ],
               loop_particles = [ [ [P.b], [P.c], [P.u] ], [ [P.d], [P.s] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
               couplings = {(0,0,1):C.R2GC_502_166,(1,2,0):C.R2GC_501_163,(1,2,1):C.R2GC_501_164,(1,2,4):C.R2GC_501_165,(1,3,2):C.R2GC_171_3,(1,1,3):C.R2GC_175_6})

V_8 = CTVertex(name = 'V_8',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.g, P.Y2 ],
               color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
               lorentz = [ L.VVVVT1, L.VVVVT10, L.VVVVT11, L.VVVVT12, L.VVVVT13, L.VVVVT14, L.VVVVT15, L.VVVVT19, L.VVVVT2, L.VVVVT21, L.VVVVT3, L.VVVVT4, L.VVVVT5, L.VVVVT6, L.VVVVT7, L.VVVVT8, L.VVVVT9 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.t] ] ],
               couplings = {(0,0,0):C.R2GC_285_65,(0,0,1):C.R2GC_285_66,(0,0,2):C.R2GC_285_67,(2,0,0):C.R2GC_285_65,(2,0,1):C.R2GC_285_66,(2,0,2):C.R2GC_285_67,(7,0,0):C.R2GC_427_143,(7,0,1):C.R2GC_427_144,(7,0,2):C.R2GC_427_145,(5,0,0):C.R2GC_289_73,(5,0,1):C.R2GC_289_74,(5,0,2):C.R2GC_289_75,(1,0,0):C.R2GC_289_73,(1,0,1):C.R2GC_289_74,(1,0,2):C.R2GC_289_75,(6,0,0):C.R2GC_389_116,(6,0,1):C.R2GC_389_117,(6,0,2):C.R2GC_389_118,(4,0,0):C.R2GC_289_73,(4,0,1):C.R2GC_289_74,(4,0,2):C.R2GC_289_75,(3,0,0):C.R2GC_289_73,(3,0,1):C.R2GC_289_74,(3,0,2):C.R2GC_289_75,(8,0,0):C.R2GC_287_69,(8,0,1):C.R2GC_423_137,(8,0,2):C.R2GC_287_71,(11,9,0):C.R2GC_284_63,(11,9,2):C.R2GC_284_64,(10,9,0):C.R2GC_284_63,(10,9,2):C.R2GC_284_64,(11,7,1):C.R2GC_173_5,(10,7,1):C.R2GC_173_5,(9,7,1):C.R2GC_172_4,(0,8,0):C.R2GC_285_65,(0,8,1):C.R2GC_285_66,(0,8,2):C.R2GC_285_67,(2,8,0):C.R2GC_285_65,(2,8,1):C.R2GC_285_66,(2,8,2):C.R2GC_285_67,(7,8,0):C.R2GC_427_143,(7,8,1):C.R2GC_427_144,(7,8,2):C.R2GC_427_145,(6,8,0):C.R2GC_389_116,(6,8,1):C.R2GC_389_117,(6,8,2):C.R2GC_389_118,(5,8,0):C.R2GC_289_73,(5,8,1):C.R2GC_289_74,(5,8,2):C.R2GC_289_75,(1,8,0):C.R2GC_289_73,(1,8,1):C.R2GC_289_74,(1,8,2):C.R2GC_289_75,(4,8,0):C.R2GC_289_73,(4,8,1):C.R2GC_289_74,(4,8,2):C.R2GC_289_75,(3,8,0):C.R2GC_289_73,(3,8,1):C.R2GC_289_74,(3,8,2):C.R2GC_289_75,(8,8,0):C.R2GC_287_69,(8,8,1):C.R2GC_423_137,(8,8,2):C.R2GC_287_71,(0,10,0):C.R2GC_285_65,(0,10,1):C.R2GC_285_66,(0,10,2):C.R2GC_285_67,(2,10,0):C.R2GC_285_65,(2,10,1):C.R2GC_285_66,(2,10,2):C.R2GC_285_67,(7,10,0):C.R2GC_388_113,(7,10,1):C.R2GC_388_114,(7,10,2):C.R2GC_388_115,(6,10,0):C.R2GC_426_140,(6,10,1):C.R2GC_426_141,(6,10,2):C.R2GC_426_142,(5,10,0):C.R2GC_289_73,(5,10,1):C.R2GC_289_74,(5,10,2):C.R2GC_289_75,(1,10,0):C.R2GC_289_73,(1,10,1):C.R2GC_289_74,(1,10,2):C.R2GC_289_75,(4,10,0):C.R2GC_289_73,(4,10,1):C.R2GC_289_74,(4,10,2):C.R2GC_289_75,(3,10,0):C.R2GC_289_73,(3,10,1):C.R2GC_289_74,(3,10,2):C.R2GC_289_75,(8,10,0):C.R2GC_287_69,(8,10,1):C.R2GC_429_147,(8,10,2):C.R2GC_287_71,(0,11,0):C.R2GC_285_65,(0,11,1):C.R2GC_285_66,(0,11,2):C.R2GC_285_67,(2,11,0):C.R2GC_285_65,(2,11,1):C.R2GC_285_66,(2,11,2):C.R2GC_285_67,(7,11,0):C.R2GC_388_113,(7,11,1):C.R2GC_430_148,(7,11,2):C.R2GC_388_115,(5,11,0):C.R2GC_289_73,(5,11,1):C.R2GC_289_74,(5,11,2):C.R2GC_289_75,(1,11,0):C.R2GC_289_73,(1,11,1):C.R2GC_289_74,(1,11,2):C.R2GC_289_75,(6,11,0):C.R2GC_389_116,(6,11,1):C.R2GC_431_149,(6,11,2):C.R2GC_389_118,(4,11,0):C.R2GC_289_73,(4,11,1):C.R2GC_289_74,(4,11,2):C.R2GC_289_75,(3,11,0):C.R2GC_289_73,(3,11,1):C.R2GC_289_74,(3,11,2):C.R2GC_289_75,(8,11,0):C.R2GC_287_69,(8,11,1):C.R2GC_287_70,(8,11,2):C.R2GC_287_71,(0,12,0):C.R2GC_285_65,(0,12,1):C.R2GC_285_66,(0,12,2):C.R2GC_285_67,(2,12,0):C.R2GC_285_65,(2,12,1):C.R2GC_285_66,(2,12,2):C.R2GC_285_67,(7,12,0):C.R2GC_388_113,(7,12,1):C.R2GC_388_114,(7,12,2):C.R2GC_388_115,(5,12,0):C.R2GC_289_73,(5,12,1):C.R2GC_289_74,(5,12,2):C.R2GC_289_75,(1,12,0):C.R2GC_289_73,(1,12,1):C.R2GC_289_74,(1,12,2):C.R2GC_289_75,(6,12,0):C.R2GC_426_140,(6,12,1):C.R2GC_426_141,(6,12,2):C.R2GC_426_142,(4,12,0):C.R2GC_289_73,(4,12,1):C.R2GC_289_74,(4,12,2):C.R2GC_289_75,(3,12,0):C.R2GC_289_73,(3,12,1):C.R2GC_289_74,(3,12,2):C.R2GC_289_75,(8,12,0):C.R2GC_287_69,(8,12,1):C.R2GC_429_147,(8,12,2):C.R2GC_287_71,(0,13,0):C.R2GC_285_65,(0,13,1):C.R2GC_285_66,(0,13,2):C.R2GC_285_67,(2,13,0):C.R2GC_285_65,(2,13,1):C.R2GC_285_66,(2,13,2):C.R2GC_285_67,(7,13,0):C.R2GC_388_113,(7,13,1):C.R2GC_430_148,(7,13,2):C.R2GC_388_115,(5,13,0):C.R2GC_289_73,(5,13,1):C.R2GC_289_74,(5,13,2):C.R2GC_289_75,(1,13,0):C.R2GC_289_73,(1,13,1):C.R2GC_289_74,(1,13,2):C.R2GC_289_75,(6,13,0):C.R2GC_389_116,(6,13,1):C.R2GC_431_149,(6,13,2):C.R2GC_389_118,(4,13,0):C.R2GC_289_73,(4,13,1):C.R2GC_289_74,(4,13,2):C.R2GC_289_75,(3,13,0):C.R2GC_289_73,(3,13,1):C.R2GC_289_74,(3,13,2):C.R2GC_289_75,(8,13,0):C.R2GC_287_69,(8,13,1):C.R2GC_287_70,(8,13,2):C.R2GC_287_71,(0,14,0):C.R2GC_285_65,(0,14,1):C.R2GC_285_66,(0,14,2):C.R2GC_285_67,(2,14,0):C.R2GC_285_65,(2,14,1):C.R2GC_285_66,(2,14,2):C.R2GC_285_67,(7,14,0):C.R2GC_388_113,(7,14,1):C.R2GC_430_148,(7,14,2):C.R2GC_388_115,(5,14,0):C.R2GC_289_73,(5,14,1):C.R2GC_289_74,(5,14,2):C.R2GC_289_75,(1,14,0):C.R2GC_289_73,(1,14,1):C.R2GC_289_74,(1,14,2):C.R2GC_289_75,(6,14,0):C.R2GC_389_116,(6,14,1):C.R2GC_431_149,(6,14,2):C.R2GC_389_118,(4,14,0):C.R2GC_289_73,(4,14,1):C.R2GC_289_74,(4,14,2):C.R2GC_289_75,(3,14,0):C.R2GC_289_73,(3,14,1):C.R2GC_289_74,(3,14,2):C.R2GC_289_75,(8,14,0):C.R2GC_287_69,(8,14,1):C.R2GC_287_70,(8,14,2):C.R2GC_287_71,(0,15,0):C.R2GC_285_65,(0,15,1):C.R2GC_285_66,(0,15,2):C.R2GC_285_67,(2,15,0):C.R2GC_285_65,(2,15,1):C.R2GC_285_66,(2,15,2):C.R2GC_285_67,(7,15,0):C.R2GC_388_113,(7,15,1):C.R2GC_388_114,(7,15,2):C.R2GC_388_115,(5,15,0):C.R2GC_289_73,(5,15,1):C.R2GC_289_74,(5,15,2):C.R2GC_289_75,(1,15,0):C.R2GC_289_73,(1,15,1):C.R2GC_289_74,(1,15,2):C.R2GC_289_75,(6,15,0):C.R2GC_426_140,(6,15,1):C.R2GC_426_141,(6,15,2):C.R2GC_426_142,(4,15,0):C.R2GC_289_73,(4,15,1):C.R2GC_289_74,(4,15,2):C.R2GC_289_75,(3,15,0):C.R2GC_289_73,(3,15,1):C.R2GC_289_74,(3,15,2):C.R2GC_289_75,(8,15,0):C.R2GC_287_69,(8,15,1):C.R2GC_429_147,(8,15,2):C.R2GC_287_71,(0,16,0):C.R2GC_285_65,(0,16,1):C.R2GC_285_66,(0,16,2):C.R2GC_285_67,(2,16,0):C.R2GC_285_65,(2,16,1):C.R2GC_285_66,(2,16,2):C.R2GC_285_67,(7,16,0):C.R2GC_427_143,(7,16,1):C.R2GC_427_144,(7,16,2):C.R2GC_427_145,(5,16,0):C.R2GC_289_73,(5,16,1):C.R2GC_289_74,(5,16,2):C.R2GC_289_75,(1,16,0):C.R2GC_289_73,(1,16,1):C.R2GC_289_74,(1,16,2):C.R2GC_289_75,(6,16,0):C.R2GC_389_116,(6,16,1):C.R2GC_389_117,(6,16,2):C.R2GC_389_118,(4,16,0):C.R2GC_289_73,(4,16,1):C.R2GC_289_74,(4,16,2):C.R2GC_289_75,(3,16,0):C.R2GC_289_73,(3,16,1):C.R2GC_289_74,(3,16,2):C.R2GC_289_75,(8,16,0):C.R2GC_287_69,(8,16,1):C.R2GC_423_137,(8,16,2):C.R2GC_287_71,(0,1,0):C.R2GC_285_65,(0,1,1):C.R2GC_285_66,(0,1,2):C.R2GC_285_67,(2,1,0):C.R2GC_285_65,(2,1,1):C.R2GC_285_66,(2,1,2):C.R2GC_285_67,(7,1,0):C.R2GC_388_113,(7,1,1):C.R2GC_430_148,(7,1,2):C.R2GC_388_115,(5,1,0):C.R2GC_289_73,(5,1,1):C.R2GC_289_74,(5,1,2):C.R2GC_289_75,(1,1,0):C.R2GC_289_73,(1,1,1):C.R2GC_289_74,(1,1,2):C.R2GC_289_75,(6,1,0):C.R2GC_389_116,(6,1,1):C.R2GC_431_149,(6,1,2):C.R2GC_389_118,(4,1,0):C.R2GC_289_73,(4,1,1):C.R2GC_289_74,(4,1,2):C.R2GC_289_75,(3,1,0):C.R2GC_289_73,(3,1,1):C.R2GC_289_74,(3,1,2):C.R2GC_289_75,(8,1,0):C.R2GC_287_69,(8,1,1):C.R2GC_287_70,(8,1,2):C.R2GC_287_71,(0,2,0):C.R2GC_285_65,(0,2,1):C.R2GC_285_66,(0,2,2):C.R2GC_285_67,(2,2,0):C.R2GC_285_65,(2,2,1):C.R2GC_285_66,(2,2,2):C.R2GC_285_67,(7,2,0):C.R2GC_388_113,(7,2,1):C.R2GC_388_114,(7,2,2):C.R2GC_388_115,(5,2,0):C.R2GC_289_73,(5,2,1):C.R2GC_289_74,(5,2,2):C.R2GC_289_75,(1,2,0):C.R2GC_289_73,(1,2,1):C.R2GC_289_74,(1,2,2):C.R2GC_289_75,(4,2,0):C.R2GC_289_73,(4,2,1):C.R2GC_289_74,(4,2,2):C.R2GC_289_75,(3,2,0):C.R2GC_289_73,(3,2,1):C.R2GC_289_74,(3,2,2):C.R2GC_289_75,(8,2,0):C.R2GC_287_69,(8,2,1):C.R2GC_429_147,(8,2,2):C.R2GC_287_71,(6,2,0):C.R2GC_426_140,(6,2,1):C.R2GC_426_141,(6,2,2):C.R2GC_426_142,(0,3,0):C.R2GC_285_65,(0,3,1):C.R2GC_285_66,(0,3,2):C.R2GC_285_67,(2,3,0):C.R2GC_285_65,(2,3,1):C.R2GC_285_66,(2,3,2):C.R2GC_285_67,(7,3,0):C.R2GC_427_143,(7,3,1):C.R2GC_427_144,(7,3,2):C.R2GC_427_145,(5,3,0):C.R2GC_289_73,(5,3,1):C.R2GC_289_74,(5,3,2):C.R2GC_289_75,(1,3,0):C.R2GC_289_73,(1,3,1):C.R2GC_289_74,(1,3,2):C.R2GC_289_75,(4,3,0):C.R2GC_289_73,(4,3,1):C.R2GC_289_74,(4,3,2):C.R2GC_289_75,(3,3,0):C.R2GC_289_73,(3,3,1):C.R2GC_289_74,(3,3,2):C.R2GC_289_75,(8,3,0):C.R2GC_287_69,(8,3,1):C.R2GC_423_137,(8,3,2):C.R2GC_287_71,(6,3,0):C.R2GC_389_116,(6,3,1):C.R2GC_389_117,(6,3,2):C.R2GC_389_118,(0,4,0):C.R2GC_287_69,(0,4,1):C.R2GC_288_72,(0,4,2):C.R2GC_287_71,(2,4,0):C.R2GC_287_69,(2,4,1):C.R2GC_288_72,(2,4,2):C.R2GC_287_71,(7,4,0):C.R2GC_387_110,(7,4,1):C.R2GC_425_139,(7,4,2):C.R2GC_387_112,(5,4,0):C.R2GC_283_60,(5,4,1):C.R2GC_283_61,(5,4,2):C.R2GC_283_62,(1,4,0):C.R2GC_283_60,(1,4,1):C.R2GC_283_61,(1,4,2):C.R2GC_283_62,(4,4,0):C.R2GC_283_60,(4,4,1):C.R2GC_283_61,(4,4,2):C.R2GC_283_62,(3,4,0):C.R2GC_283_60,(3,4,1):C.R2GC_283_61,(3,4,2):C.R2GC_283_62,(8,4,0):C.R2GC_285_65,(8,4,1):C.R2GC_286_68,(8,4,2):C.R2GC_285_67,(6,4,1):C.R2GC_424_138,(0,5,0):C.R2GC_287_69,(0,5,1):C.R2GC_288_72,(0,5,2):C.R2GC_287_71,(2,5,0):C.R2GC_287_69,(2,5,1):C.R2GC_288_72,(2,5,2):C.R2GC_287_71,(7,5,0):C.R2GC_387_110,(7,5,1):C.R2GC_387_111,(7,5,2):C.R2GC_387_112,(5,5,0):C.R2GC_283_60,(5,5,1):C.R2GC_283_61,(5,5,2):C.R2GC_283_62,(1,5,0):C.R2GC_283_60,(1,5,1):C.R2GC_283_61,(1,5,2):C.R2GC_283_62,(4,5,0):C.R2GC_283_60,(4,5,1):C.R2GC_283_61,(4,5,2):C.R2GC_283_62,(3,5,0):C.R2GC_283_60,(3,5,1):C.R2GC_283_61,(3,5,2):C.R2GC_283_62,(8,5,0):C.R2GC_285_65,(8,5,1):C.R2GC_422_136,(8,5,2):C.R2GC_285_67,(6,5,0):C.R2GC_433_151,(6,5,1):C.R2GC_433_152,(6,5,2):C.R2GC_433_153,(0,6,0):C.R2GC_287_69,(0,6,1):C.R2GC_288_72,(0,6,2):C.R2GC_287_71,(2,6,0):C.R2GC_287_69,(2,6,1):C.R2GC_288_72,(2,6,2):C.R2GC_287_71,(5,6,0):C.R2GC_283_60,(5,6,1):C.R2GC_283_61,(5,6,2):C.R2GC_283_62,(1,6,0):C.R2GC_283_60,(1,6,1):C.R2GC_283_61,(1,6,2):C.R2GC_283_62,(7,6,0):C.R2GC_285_65,(7,6,1):C.R2GC_432_150,(7,6,2):C.R2GC_285_67,(4,6,0):C.R2GC_283_60,(4,6,1):C.R2GC_283_61,(4,6,2):C.R2GC_283_62,(3,6,0):C.R2GC_283_60,(3,6,1):C.R2GC_283_61,(3,6,2):C.R2GC_283_62,(8,6,0):C.R2GC_285_65,(8,6,1):C.R2GC_428_146,(8,6,2):C.R2GC_285_67,(6,6,1):C.R2GC_386_109})

V_9 = CTVertex(name = 'V_9',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.Y2 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFT11, L.FFT12, L.FFT14, L.FFT16, L.FFT8 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,3,0):C.R2GC_183_14,(0,2,0):C.R2GC_243_34,(0,1,0):C.R2GC_246_37,(0,0,0):C.R2GC_247_38,(0,4,0):C.R2GC_443_154})

V_10 = CTVertex(name = 'V_10',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS5 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_415_132})

V_11 = CTVertex(name = 'V_11',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFT24, L.FFT26 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_183_14,(0,0,0):C.R2GC_186_17})

V_12 = CTVertex(name = 'V_12',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFT24, L.FFT26 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_183_14,(0,0,0):C.R2GC_186_17})

V_13 = CTVertex(name = 'V_13',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFT23, L.FFT26, L.FFT5 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_183_14,(0,0,0):C.R2GC_186_17,(0,2,0):C.R2GC_504_171})

V_14 = CTVertex(name = 'V_14',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFT23, L.FFT26, L.FFT5 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,1,0):C.R2GC_183_14,(0,0,0):C.R2GC_186_17,(0,2,0):C.R2GC_504_171})

V_15 = CTVertex(name = 'V_15',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFT24, L.FFT26 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_183_14,(0,0,0):C.R2GC_186_17})

V_16 = CTVertex(name = 'V_16',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT34 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_199_27,(0,1,0):C.R2GC_244_35})

V_17 = CTVertex(name = 'V_17',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT23, L.FFVT28, L.FFVT54, L.FFVT56 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,1,0):C.R2GC_205_30,(0,0,0):C.R2GC_249_39,(0,3,0):C.R2GC_193_24,(0,2,0):C.R2GC_251_40})

V_18 = CTVertex(name = 'V_18',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT34 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_184_15,(0,1,0):C.R2GC_187_18})

V_19 = CTVertex(name = 'V_19',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT23, L.FFVT28, L.FFVT41, L.FFVT44 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_190_21,(0,0,0):C.R2GC_191_22,(0,2,0):C.R2GC_193_24,(0,3,0):C.R2GC_194_25})

V_20 = CTVertex(name = 'V_20',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT34 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_199_27,(0,1,0):C.R2GC_202_28})

V_21 = CTVertex(name = 'V_21',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT33, L.FFVT4 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_184_15,(0,1,0):C.R2GC_187_18,(0,2,0):C.R2GC_505_172})

V_22 = CTVertex(name = 'V_22',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT33, L.FFVT4 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_184_15,(0,1,0):C.R2GC_187_18,(0,2,0):C.R2GC_505_172})

V_23 = CTVertex(name = 'V_23',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT23, L.FFVT28, L.FFVT54, L.FFVT56 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_205_30,(0,0,0):C.R2GC_206_31,(0,3,0):C.R2GC_193_24,(0,2,0):C.R2GC_194_25})

V_24 = CTVertex(name = 'V_24',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT10, L.FFVT28, L.FFVT4, L.FFVT41, L.FFVT43 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_190_21,(0,0,0):C.R2GC_191_22,(0,3,0):C.R2GC_193_24,(0,4,0):C.R2GC_194_25,(0,2,0):C.R2GC_507_174})

V_25 = CTVertex(name = 'V_25',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT10, L.FFVT28, L.FFVT4, L.FFVT41, L.FFVT43 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,1,0):C.R2GC_190_21,(0,0,0):C.R2GC_191_22,(0,3,0):C.R2GC_193_24,(0,4,0):C.R2GC_194_25,(0,2,0):C.R2GC_507_174})

V_26 = CTVertex(name = 'V_26',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.a, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT31, L.FFVT34 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_199_27,(0,1,0):C.R2GC_202_28})

V_27 = CTVertex(name = 'V_27',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT23, L.FFVT28, L.FFVT54, L.FFVT56 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_205_30,(0,0,0):C.R2GC_206_31,(0,3,0):C.R2GC_193_24,(0,2,0):C.R2GC_194_25})

V_28 = CTVertex(name = 'V_28',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT37, L.FFVT39 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_188_19})

V_29 = CTVertex(name = 'V_29',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT36, L.FFVT39, L.FFVT5 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_188_19,(0,2,0):C.R2GC_506_173})

V_30 = CTVertex(name = 'V_30',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT36, L.FFVT39, L.FFVT5 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_188_19,(0,2,0):C.R2GC_506_173})

V_31 = CTVertex(name = 'V_31',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT37, L.FFVT39 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_188_19})

V_32 = CTVertex(name = 'V_32',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT37, L.FFVT39 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_188_19})

V_33 = CTVertex(name = 'V_33',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.g, P.Y2 ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFVT37, L.FFVT39 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,1,0):C.R2GC_185_16,(0,0,0):C.R2GC_245_36})

V_34 = CTVertex(name = 'V_34',
                type = 'R2',
                particles = [ P.d__tilde__, P.u, P.W__minus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT11, L.FFVT28, L.FFVT7 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_267_41,(0,0,0):C.R2GC_268_42,(0,2,0):C.R2GC_513_178})

V_35 = CTVertex(name = 'V_35',
                type = 'R2',
                particles = [ P.s__tilde__, P.u, P.W__minus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT11, L.FFVT28, L.FFVT7 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_489_158,(0,0,0):C.R2GC_490_159,(0,2,0):C.R2GC_535_182})

V_36 = CTVertex(name = 'V_36',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT17, L.FFVT21, L.FFVT28 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,2,0):C.R2GC_267_41,(0,1,0):C.R2GC_269_43,(0,0,0):C.R2GC_514_179})

V_37 = CTVertex(name = 'V_37',
                type = 'R2',
                particles = [ P.u__tilde__, P.s, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT13, L.FFVT2, L.FFVT28 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,2,0):C.R2GC_489_158,(0,0,0):C.R2GC_490_159,(0,1,0):C.R2GC_535_182})

V_38 = CTVertex(name = 'V_38',
                type = 'R2',
                particles = [ P.d__tilde__, P.c, P.W__minus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT11, L.FFVT28, L.FFVT7 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,1,0):C.R2GC_486_155,(0,0,0):C.R2GC_487_156,(0,2,0):C.R2GC_533_180})

V_39 = CTVertex(name = 'V_39',
                type = 'R2',
                particles = [ P.s__tilde__, P.c, P.W__minus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT11, L.FFVT28, L.FFVT7 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,1,0):C.R2GC_267_41,(0,0,0):C.R2GC_268_42,(0,2,0):C.R2GC_513_178})

V_40 = CTVertex(name = 'V_40',
                type = 'R2',
                particles = [ P.c__tilde__, P.d, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT17, L.FFVT21, L.FFVT28 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,2,0):C.R2GC_486_155,(0,1,0):C.R2GC_488_157,(0,0,0):C.R2GC_534_181})

V_41 = CTVertex(name = 'V_41',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT17, L.FFVT21, L.FFVT28 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,2,0):C.R2GC_267_41,(0,1,0):C.R2GC_269_43,(0,0,0):C.R2GC_514_179})

V_42 = CTVertex(name = 'V_42',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT18, L.FFVT25, L.FFVT28 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,2,0):C.R2GC_270_44,(0,0,0):C.R2GC_271_45,(0,1,0):C.R2GC_272_46})

V_43 = CTVertex(name = 'V_43',
                type = 'R2',
                particles = [ P.b__tilde__, P.t, P.W__minus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFVT18, L.FFVT25, L.FFVT28 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,2,0):C.R2GC_270_44,(0,1,0):C.R2GC_271_45,(0,0,0):C.R2GC_272_46})

V_44 = CTVertex(name = 'V_44',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_196_26})

V_45 = CTVertex(name = 'V_45',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_196_26})

V_46 = CTVertex(name = 'V_46',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_196_26})

V_47 = CTVertex(name = 'V_47',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_181_12})

V_48 = CTVertex(name = 'V_48',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_181_12})

V_49 = CTVertex(name = 'V_49',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_181_12})

V_50 = CTVertex(name = 'V_50',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_51 = CTVertex(name = 'V_51',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_52 = CTVertex(name = 'V_52',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_53 = CTVertex(name = 'V_53',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_54 = CTVertex(name = 'V_54',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_55 = CTVertex(name = 'V_55',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_182_13})

V_56 = CTVertex(name = 'V_56',
                type = 'R2',
                particles = [ P.d__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_498_160})

V_57 = CTVertex(name = 'V_57',
                type = 'R2',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_398_119})

V_58 = CTVertex(name = 'V_58',
                type = 'R2',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_412_131})

V_59 = CTVertex(name = 'V_59',
                type = 'R2',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_398_119})

V_60 = CTVertex(name = 'V_60',
                type = 'R2',
                particles = [ P.s__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_499_161})

V_61 = CTVertex(name = 'V_61',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_412_131})

V_62 = CTVertex(name = 'V_62',
                type = 'R2',
                particles = [ P.c__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_498_160})

V_63 = CTVertex(name = 'V_63',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_398_119})

V_64 = CTVertex(name = 'V_64',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_398_119})

V_65 = CTVertex(name = 'V_65',
                type = 'R2',
                particles = [ P.u__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_499_161})

V_66 = CTVertex(name = 'V_66',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV7 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_204_29,(0,1,0):C.R2GC_192_23})

V_67 = CTVertex(name = 'V_67',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV7 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_204_29,(0,1,0):C.R2GC_192_23})

V_68 = CTVertex(name = 'V_68',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV7 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_204_29,(0,1,0):C.R2GC_192_23})

V_69 = CTVertex(name = 'V_69',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_189_20,(0,1,0):C.R2GC_192_23})

V_70 = CTVertex(name = 'V_70',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_189_20,(0,1,0):C.R2GC_192_23})

V_71 = CTVertex(name = 'V_71',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_189_20,(0,1,0):C.R2GC_192_23})

V_72 = CTVertex(name = 'V_72',
                type = 'R2',
                particles = [ P.a, P.a, P.g, P.g, P.Y2 ],
                color = [ 'Identity(3,4)' ],
                lorentz = [ L.VVVVT21 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_281_54,(0,0,1):C.R2GC_281_55,(0,0,2):C.R2GC_281_56})

V_73 = CTVertex(name = 'V_73',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Z, P.Y2 ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVVT21 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_294_84,(0,0,1):C.R2GC_294_85,(0,0,2):C.R2GC_294_86})

V_74 = CTVertex(name = 'V_74',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVVT21 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_298_95,(0,0,1):C.R2GC_298_96,(0,0,2):C.R2GC_298_97})

V_75 = CTVertex(name = 'V_75',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.W__plus__, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVVT21, L.VVVVT25, L.VVVVT26 ],
                loop_particles = [ [ [P.b, P.t] ], [ [P.c, P.d], [P.s, P.u] ], [ [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,1,0):C.R2GC_238_32,(0,2,0):C.R2GC_239_33,(0,0,1):C.R2GC_299_98,(0,0,2):C.R2GC_299_99})

V_76 = CTVertex(name = 'V_76',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.g, P.Y2 ],
                color = [ 'd(2,3,4)' ],
                lorentz = [ L.VVVVT21 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_282_57,(0,0,1):C.R2GC_282_58,(0,0,2):C.R2GC_282_59})

V_77 = CTVertex(name = 'V_77',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Z, P.Y2 ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVVT17, L.VVVVT21 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                couplings = {(1,0,0):C.R2GC_296_90,(1,0,1):C.R2GC_296_91,(1,0,2):C.R2GC_296_92,(0,1,0):C.R2GC_295_87,(0,1,1):C.R2GC_295_88,(0,1,2):C.R2GC_295_89})

V_78 = CTVertex(name = 'V_78',
                type = 'R2',
                particles = [ P.g, P.g ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VV2, L.VV3, L.VV4 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ], [ [P.t] ] ],
                couplings = {(0,2,1):C.R2GC_169_1,(0,0,2):C.R2GC_176_7,(0,1,0):C.R2GC_277_48})

V_79 = CTVertex(name = 'V_79',
                type = 'R2',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_180_11})

V_80 = CTVertex(name = 'V_80',
                type = 'R2',
                particles = [ P.c__tilde__, P.c ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_180_11})

V_81 = CTVertex(name = 'V_81',
                type = 'R2',
                particles = [ P.t__tilde__, P.t ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF2, L.FF3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_411_130,(0,1,0):C.R2GC_180_11})

V_82 = CTVertex(name = 'V_82',
                type = 'R2',
                particles = [ P.d__tilde__, P.d ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_180_11})

V_83 = CTVertex(name = 'V_83',
                type = 'R2',
                particles = [ P.s__tilde__, P.s ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_180_11})

V_84 = CTVertex(name = 'V_84',
                type = 'R2',
                particles = [ P.b__tilde__, P.b ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_180_11})

V_85 = CTVertex(name = 'V_85',
                type = 'R2',
                particles = [ P.g, P.g, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVV1 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_290_76,(0,0,1):C.R2GC_290_77})

V_86 = CTVertex(name = 'V_86',
                type = 'R2',
                particles = [ P.g, P.g, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_178_9})

V_87 = CTVertex(name = 'V_87',
                type = 'R2',
                particles = [ P.a, P.a, P.g, P.g ],
                color = [ 'Identity(3,4)' ],
                lorentz = [ L.VVVV10 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_278_49,(0,0,1):C.R2GC_278_50})

V_88 = CTVertex(name = 'V_88',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Z ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV10 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_291_78,(0,0,1):C.R2GC_291_79})

V_89 = CTVertex(name = 'V_89',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV10 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_297_93,(0,0,1):C.R2GC_297_94})

V_90 = CTVertex(name = 'V_90',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV10 ],
                loop_particles = [ [ [P.b, P.t] ], [ [P.c, P.d], [P.s, P.u] ], [ [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_512_175,(0,0,1):C.R2GC_512_176,(0,0,2):C.R2GC_512_177})

V_91 = CTVertex(name = 'V_91',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.g ],
                color = [ 'd(2,3,4)' ],
                lorentz = [ L.VVVV10 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_279_51,(0,0,1):C.R2GC_279_52})

V_92 = CTVertex(name = 'V_92',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Z ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV10 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_293_82,(1,0,1):C.R2GC_293_83,(0,1,0):C.R2GC_292_80,(0,1,1):C.R2GC_292_81})

V_93 = CTVertex(name = 'V_93',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVT3 ],
                loop_particles = [ [ [P.b] ], [ [P.c], [P.u] ], [ [P.d], [P.s] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_503_167,(0,0,1):C.R2GC_503_168,(0,0,2):C.R2GC_503_169,(0,0,3):C.R2GC_503_170})

V_94 = CTVertex(name = 'V_94',
                type = 'UV',
                particles = [ P.g, P.g, P.g ],
                color = [ 'f(1,2,3)' ],
                lorentz = [ L.VVV2 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.UVGC_402_69,(0,0,1):C.UVGC_402_70,(0,0,2):C.UVGC_402_71,(0,0,3):C.UVGC_402_72})

V_95 = CTVertex(name = 'V_95',
                type = 'UV',
                particles = [ P.g, P.g, P.g, P.g ],
                color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
                lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,1,1):C.UVGC_378_37,(0,1,2):C.UVGC_378_36,(2,1,1):C.UVGC_378_37,(2,1,2):C.UVGC_378_36,(6,1,0):C.UVGC_405_79,(6,1,1):C.UVGC_406_83,(6,1,2):C.UVGC_406_84,(6,1,3):C.UVGC_405_82,(7,1,0):C.UVGC_405_79,(7,1,1):C.UVGC_405_80,(7,1,2):C.UVGC_405_81,(7,1,3):C.UVGC_405_82,(5,1,1):C.UVGC_377_34,(5,1,2):C.UVGC_377_35,(1,1,1):C.UVGC_377_34,(1,1,2):C.UVGC_377_35,(4,1,1):C.UVGC_377_34,(4,1,2):C.UVGC_377_35,(3,1,1):C.UVGC_377_34,(3,1,2):C.UVGC_377_35,(8,1,1):C.UVGC_378_36,(8,1,2):C.UVGC_378_37,(11,0,1):C.UVGC_381_40,(11,0,2):C.UVGC_381_41,(10,0,1):C.UVGC_381_40,(10,0,2):C.UVGC_381_41,(9,0,1):C.UVGC_380_38,(9,0,2):C.UVGC_380_39,(0,2,1):C.UVGC_378_37,(0,2,2):C.UVGC_378_36,(2,2,1):C.UVGC_378_37,(2,2,2):C.UVGC_378_36,(6,2,0):C.UVGC_403_73,(6,2,1):C.UVGC_404_77,(6,2,2):C.UVGC_404_78,(6,2,3):C.UVGC_403_76,(8,2,0):C.UVGC_405_79,(8,2,1):C.UVGC_405_80,(8,2,2):C.UVGC_405_81,(8,2,3):C.UVGC_405_82,(5,2,1):C.UVGC_377_34,(5,2,2):C.UVGC_377_35,(1,2,1):C.UVGC_377_34,(1,2,2):C.UVGC_377_35,(7,2,1):C.UVGC_378_36,(7,2,2):C.UVGC_378_37,(4,2,1):C.UVGC_377_34,(4,2,2):C.UVGC_377_35,(3,2,1):C.UVGC_377_34,(3,2,2):C.UVGC_377_35,(0,3,1):C.UVGC_378_37,(0,3,2):C.UVGC_378_36,(2,3,1):C.UVGC_378_37,(2,3,2):C.UVGC_378_36,(7,3,0):C.UVGC_403_73,(7,3,1):C.UVGC_403_74,(7,3,2):C.UVGC_403_75,(7,3,3):C.UVGC_403_76,(8,3,0):C.UVGC_403_73,(8,3,1):C.UVGC_403_74,(8,3,2):C.UVGC_403_75,(8,3,3):C.UVGC_403_76,(5,3,1):C.UVGC_377_34,(5,3,2):C.UVGC_377_35,(1,3,1):C.UVGC_377_34,(1,3,2):C.UVGC_377_35,(4,3,1):C.UVGC_377_34,(4,3,2):C.UVGC_377_35,(3,3,1):C.UVGC_377_34,(3,3,2):C.UVGC_377_35})

V_96 = CTVertex(name = 'V_96',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.G__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_416_99,(0,0,2):C.UVGC_416_100,(0,0,1):C.UVGC_416_101})

V_97 = CTVertex(name = 'V_97',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_417_102})

V_98 = CTVertex(name = 'V_98',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS2 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_418_103})

V_99 = CTVertex(name = 'V_99',
                type = 'UV',
                particles = [ P.g, P.g, P.Y2 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVT14, L.VVT4, L.VVT5, L.VVT6, L.VVT7, L.VVT8, L.VVT9 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b], [P.c], [P.u] ], [ [P.d], [P.s] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ], [ [P.u] ] ],
                couplings = {(0,2,3):C.UVGC_420_107,(0,2,5):C.UVGC_420_108,(0,2,6):C.UVGC_420_109,(0,6,3):C.UVGC_300_1,(0,0,4):C.UVGC_301_2,(0,3,0):C.UVGC_407_85,(0,3,5):C.UVGC_407_86,(0,1,1):C.UVGC_382_42,(0,1,5):C.UVGC_384_47,(0,4,2):C.UVGC_382_42,(0,5,2):C.UVGC_517_205})

V_100 = CTVertex(name = 'V_100',
                 type = 'UV',
                 particles = [ P.ghG, P.ghG__tilde__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.UUT1 ],
                 loop_particles = [ [ [P.g] ], [ [P.t] ], [ [P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_419_104,(0,0,1):C.UVGC_419_105,(0,0,2):C.UVGC_419_106})

V_101 = CTVertex(name = 'V_101',
                 type = 'UV',
                 particles = [ P.ghG, P.ghG__tilde__, P.g, P.Y2 ],
                 color = [ 'f(1,2,3)' ],
                 lorentz = [ L.UUVT1 ],
                 loop_particles = [ [ [P.g] ], [ [P.t] ], [ [P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_421_110,(0,0,1):C.UVGC_421_111,(0,0,2):C.UVGC_421_112})

V_102 = CTVertex(name = 'V_102',
                 type = 'UV',
                 particles = [ P.g, P.g, P.g, P.Y2 ],
                 color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                 lorentz = [ L.VVVT1, L.VVVT7 ],
                 loop_particles = [ [ [P.b], [P.c] ], [ [P.d], [P.s] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ], [ [P.u] ] ],
                 couplings = {(1,1,0):C.UVGC_518_206,(1,1,1):C.UVGC_518_207,(1,1,2):C.UVGC_518_208,(1,1,3):C.UVGC_518_209,(1,1,4):C.UVGC_518_210,(1,1,5):C.UVGC_518_211,(0,0,1):C.UVGC_519_212})

V_103 = CTVertex(name = 'V_103',
                 type = 'UV',
                 particles = [ P.g, P.g, P.g, P.g, P.Y2 ],
                 color = [ 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)' ],
                 lorentz = [ L.VVVVT1, L.VVVVT10, L.VVVVT11, L.VVVVT12, L.VVVVT13, L.VVVVT14, L.VVVVT15, L.VVVVT2, L.VVVVT3, L.VVVVT4, L.VVVVT5, L.VVVVT6, L.VVVVT7, L.VVVVT8, L.VVVVT9 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s] ], [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.t] ], [ [P.u] ] ],
                 couplings = {(1,0,0):C.UVGC_426_121,(1,0,2):C.UVGC_426_122,(1,0,3):C.UVGC_426_123,(1,0,4):C.UVGC_426_124,(0,0,1):C.UVGC_388_55,(0,0,2):C.UVGC_388_56,(0,0,3):C.UVGC_388_57,(2,0,0):C.UVGC_422_113,(2,0,2):C.UVGC_422_114,(2,0,3):C.UVGC_422_115,(2,0,4):C.UVGC_422_116,(1,7,0):C.UVGC_426_121,(1,7,2):C.UVGC_426_122,(1,7,3):C.UVGC_426_123,(1,7,4):C.UVGC_426_124,(0,7,1):C.UVGC_388_55,(0,7,2):C.UVGC_388_56,(0,7,3):C.UVGC_388_57,(2,7,0):C.UVGC_422_113,(2,7,2):C.UVGC_422_114,(2,7,3):C.UVGC_422_115,(2,7,4):C.UVGC_422_116,(1,8,1):C.UVGC_388_55,(1,8,2):C.UVGC_388_56,(1,8,3):C.UVGC_388_57,(0,8,0):C.UVGC_426_121,(0,8,2):C.UVGC_426_122,(0,8,3):C.UVGC_426_123,(0,8,4):C.UVGC_426_124,(2,8,0):C.UVGC_428_125,(2,8,2):C.UVGC_428_126,(2,8,3):C.UVGC_428_127,(2,8,4):C.UVGC_428_128,(1,9,0):C.UVGC_430_129,(1,9,2):C.UVGC_430_130,(1,9,3):C.UVGC_430_131,(1,9,4):C.UVGC_430_132,(0,9,0):C.UVGC_430_129,(0,9,2):C.UVGC_430_130,(0,9,3):C.UVGC_430_131,(0,9,4):C.UVGC_430_132,(1,10,1):C.UVGC_388_55,(1,10,2):C.UVGC_388_56,(1,10,3):C.UVGC_388_57,(0,10,0):C.UVGC_426_121,(0,10,2):C.UVGC_426_122,(0,10,3):C.UVGC_426_123,(0,10,4):C.UVGC_426_124,(2,10,0):C.UVGC_428_125,(2,10,2):C.UVGC_428_126,(2,10,3):C.UVGC_428_127,(2,10,4):C.UVGC_428_128,(1,11,0):C.UVGC_430_129,(1,11,2):C.UVGC_430_130,(1,11,3):C.UVGC_430_131,(1,11,4):C.UVGC_430_132,(0,11,0):C.UVGC_430_129,(0,11,2):C.UVGC_430_130,(0,11,3):C.UVGC_430_131,(0,11,4):C.UVGC_430_132,(1,12,0):C.UVGC_430_129,(1,12,2):C.UVGC_430_130,(1,12,3):C.UVGC_430_131,(1,12,4):C.UVGC_430_132,(0,12,0):C.UVGC_430_129,(0,12,2):C.UVGC_430_130,(0,12,3):C.UVGC_430_131,(0,12,4):C.UVGC_430_132,(1,13,1):C.UVGC_388_55,(1,13,2):C.UVGC_388_56,(1,13,3):C.UVGC_388_57,(0,13,0):C.UVGC_426_121,(0,13,2):C.UVGC_426_122,(0,13,3):C.UVGC_426_123,(0,13,4):C.UVGC_426_124,(2,13,0):C.UVGC_428_125,(2,13,2):C.UVGC_428_126,(2,13,3):C.UVGC_428_127,(2,13,4):C.UVGC_428_128,(1,14,0):C.UVGC_426_121,(1,14,2):C.UVGC_426_122,(1,14,3):C.UVGC_426_123,(1,14,4):C.UVGC_426_124,(0,14,1):C.UVGC_388_55,(0,14,2):C.UVGC_388_56,(0,14,3):C.UVGC_388_57,(2,14,0):C.UVGC_422_113,(2,14,2):C.UVGC_422_114,(2,14,3):C.UVGC_422_115,(2,14,4):C.UVGC_422_116,(1,1,0):C.UVGC_430_129,(1,1,2):C.UVGC_430_130,(1,1,3):C.UVGC_430_131,(1,1,4):C.UVGC_430_132,(0,1,0):C.UVGC_430_129,(0,1,2):C.UVGC_430_130,(0,1,3):C.UVGC_430_131,(0,1,4):C.UVGC_430_132,(1,2,1):C.UVGC_388_55,(1,2,2):C.UVGC_388_56,(1,2,3):C.UVGC_388_57,(2,2,0):C.UVGC_428_125,(2,2,2):C.UVGC_428_126,(2,2,3):C.UVGC_428_127,(2,2,4):C.UVGC_428_128,(0,2,0):C.UVGC_426_121,(0,2,2):C.UVGC_426_122,(0,2,3):C.UVGC_426_123,(0,2,4):C.UVGC_426_124,(1,3,0):C.UVGC_426_121,(1,3,2):C.UVGC_426_122,(1,3,3):C.UVGC_426_123,(1,3,4):C.UVGC_426_124,(2,3,0):C.UVGC_422_113,(2,3,2):C.UVGC_422_114,(2,3,3):C.UVGC_422_115,(2,3,4):C.UVGC_422_116,(0,3,1):C.UVGC_388_55,(0,3,2):C.UVGC_388_56,(0,3,3):C.UVGC_388_57,(1,4,0):C.UVGC_424_117,(1,4,2):C.UVGC_424_118,(1,4,3):C.UVGC_424_119,(1,4,4):C.UVGC_424_120,(0,4,0):C.UVGC_424_117,(0,4,2):C.UVGC_424_118,(0,4,3):C.UVGC_424_119,(0,4,4):C.UVGC_424_120,(1,5,1):C.UVGC_386_52,(1,5,2):C.UVGC_386_53,(1,5,3):C.UVGC_386_54,(2,5,0):C.UVGC_422_113,(2,5,2):C.UVGC_422_114,(2,5,3):C.UVGC_422_115,(2,5,4):C.UVGC_422_116,(0,5,0):C.UVGC_432_133,(0,5,2):C.UVGC_432_134,(0,5,3):C.UVGC_432_135,(0,5,4):C.UVGC_432_136,(1,6,0):C.UVGC_432_133,(1,6,2):C.UVGC_432_134,(1,6,3):C.UVGC_432_135,(1,6,4):C.UVGC_432_136,(2,6,0):C.UVGC_428_125,(2,6,2):C.UVGC_428_126,(2,6,3):C.UVGC_428_127,(2,6,4):C.UVGC_428_128,(0,6,1):C.UVGC_386_52,(0,6,2):C.UVGC_386_53,(0,6,3):C.UVGC_386_54})

V_104 = CTVertex(name = 'V_104',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.G0, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFST3 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_442_149})

V_105 = CTVertex(name = 'V_105',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.H, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFST4 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_441_148})

V_106 = CTVertex(name = 'V_106',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT10, L.FFT13, L.FFT15, L.FFT17, L.FFT18, L.FFT20, L.FFT8, L.FFT9 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,5,0):C.UVGC_434_137,(0,3,0):C.UVGC_303_4,(0,2,0):C.UVGC_347_19,(0,4,0):C.UVGC_396_64,(0,1,0):C.UVGC_350_22,(0,6,0):C.UVGC_443_150,(0,0,0):C.UVGC_355_25,(0,7,0):C.UVGC_400_67})

V_107 = CTVertex(name = 'V_107',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.t, P.G__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFST1 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_440_147})

V_108 = CTVertex(name = 'V_108',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.b, P.G__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFS5 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_415_96,(0,0,2):C.UVGC_415_97,(0,0,1):C.UVGC_415_98})

V_109 = CTVertex(name = 'V_109',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.b, P.G__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFST2 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_439_146})

V_110 = CTVertex(name = 'V_110',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT20, L.FFT22, L.FFT25 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_444_151,(0,2,0):C.UVGC_303_4,(0,1,0):C.UVGC_306_7})

V_111 = CTVertex(name = 'V_111',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT20, L.FFT22, L.FFT25 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_444_151,(0,2,0):C.UVGC_303_4,(0,1,0):C.UVGC_306_7})

V_112 = CTVertex(name = 'V_112',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT19, L.FFT21, L.FFT25, L.FFT4, L.FFT6 ],
                 loop_particles = [ [ [P.d, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,3,1):C.UVGC_466_174,(0,0,1):C.UVGC_444_151,(0,2,0):C.UVGC_303_4,(0,1,0):C.UVGC_306_7,(0,4,0):C.UVGC_521_217})

V_113 = CTVertex(name = 'V_113',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.d, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT4 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_467_175})

V_114 = CTVertex(name = 'V_114',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.s, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT4 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_476_184})

V_115 = CTVertex(name = 'V_115',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT19, L.FFT21, L.FFT25, L.FFT4, L.FFT7 ],
                 loop_particles = [ [ [P.g, P.s] ], [ [P.g, P.u] ] ],
                 couplings = {(0,3,1):C.UVGC_477_185,(0,0,1):C.UVGC_444_151,(0,2,0):C.UVGC_303_4,(0,1,0):C.UVGC_306_7,(0,4,0):C.UVGC_525_221})

V_116 = CTVertex(name = 'V_116',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFT20, L.FFT22, L.FFT25 ],
                 loop_particles = [ [ [P.c, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_444_151,(0,2,0):C.UVGC_303_4,(0,1,0):C.UVGC_306_7})

V_117 = CTVertex(name = 'V_117',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT30, L.FFVT32, L.FFVT49 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,2,0):C.UVGC_435_138,(0,0,0):C.UVGC_315_14,(0,1,0):C.UVGC_348_20})

V_118 = CTVertex(name = 'V_118',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT24, L.FFVT29, L.FFVT51, L.FFVT55, L.FFVT57 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_437_144,(0,3,0):C.UVGC_438_145,(0,2,0):C.UVGC_320_16,(0,1,0):C.UVGC_352_23,(0,5,0):C.UVGC_311_12,(0,4,0):C.UVGC_354_24})

V_119 = CTVertex(name = 'V_119',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT30, L.FFVT49, L.FFVT59 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,1):C.UVGC_445_152,(0,0,0):C.UVGC_304_5,(0,2,0):C.UVGC_307_8})

V_120 = CTVertex(name = 'V_120',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT20, L.FFVT29, L.FFVT40, L.FFVT42, L.FFVT45 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_458_166,(0,4,1):C.UVGC_460_168,(0,2,0):C.UVGC_309_10,(0,1,0):C.UVGC_310_11,(0,3,0):C.UVGC_311_12,(0,5,0):C.UVGC_312_13})

V_121 = CTVertex(name = 'V_121',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT30, L.FFVT49, L.FFVT59 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,1,0):C.UVGC_446_153,(0,0,0):C.UVGC_315_14,(0,2,0):C.UVGC_318_15})

V_122 = CTVertex(name = 'V_122',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT27, L.FFVT30, L.FFVT48, L.FFVT58 ],
                 loop_particles = [ [ [P.d, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_468_176,(0,3,1):C.UVGC_445_152,(0,2,0):C.UVGC_304_5,(0,4,0):C.UVGC_307_8,(0,1,0):C.UVGC_522_218})

V_123 = CTVertex(name = 'V_123',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.d, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_469_177})

V_124 = CTVertex(name = 'V_124',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.s, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_478_186})

V_125 = CTVertex(name = 'V_125',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT27, L.FFVT30, L.FFVT48, L.FFVT58 ],
                 loop_particles = [ [ [P.g, P.s] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_479_187,(0,3,1):C.UVGC_445_152,(0,2,0):C.UVGC_304_5,(0,4,0):C.UVGC_307_8,(0,1,0):C.UVGC_522_218})

V_126 = CTVertex(name = 'V_126',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT20, L.FFVT29, L.FFVT51, L.FFVT53, L.FFVT57 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_459_167,(0,3,0):C.UVGC_460_168,(0,2,0):C.UVGC_320_16,(0,1,0):C.UVGC_321_17,(0,5,0):C.UVGC_311_12,(0,4,0):C.UVGC_312_13})

V_127 = CTVertex(name = 'V_127',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT10, L.FFVT15, L.FFVT27, L.FFVT29, L.FFVT40, L.FFVT48, L.FFVT52 ],
                 loop_particles = [ [ [P.d, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,1):C.UVGC_474_182,(0,5,1):C.UVGC_461_169,(0,0,0):C.UVGC_391_61,(0,3,0):C.UVGC_309_10,(0,4,0):C.UVGC_311_12,(0,6,0):C.UVGC_333_18,(0,2,0):C.UVGC_524_220})

V_128 = CTVertex(name = 'V_128',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.d, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_475_183})

V_129 = CTVertex(name = 'V_129',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.s, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_484_192})

V_130 = CTVertex(name = 'V_130',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT10, L.FFVT15, L.FFVT27, L.FFVT29, L.FFVT40, L.FFVT48, L.FFVT52 ],
                 loop_particles = [ [ [P.g, P.s] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,1):C.UVGC_485_193,(0,5,1):C.UVGC_461_169,(0,0,0):C.UVGC_391_61,(0,3,0):C.UVGC_309_10,(0,4,0):C.UVGC_311_12,(0,6,0):C.UVGC_333_18,(0,2,0):C.UVGC_524_220})

V_131 = CTVertex(name = 'V_131',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c, P.a, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT30, L.FFVT49, L.FFVT59 ],
                 loop_particles = [ [ [P.c, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,1):C.UVGC_446_153,(0,0,0):C.UVGC_315_14,(0,2,0):C.UVGC_318_15})

V_132 = CTVertex(name = 'V_132',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT20, L.FFVT29, L.FFVT51, L.FFVT53, L.FFVT57 ],
                 loop_particles = [ [ [P.c, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,1):C.UVGC_459_167,(0,3,1):C.UVGC_460_168,(0,2,0):C.UVGC_320_16,(0,1,0):C.UVGC_321_17,(0,5,0):C.UVGC_311_12,(0,4,0):C.UVGC_312_13})

V_133 = CTVertex(name = 'V_133',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT35, L.FFVT47, L.FFVT49 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,2,0):C.UVGC_385_48,(0,2,1):C.UVGC_385_49,(0,2,2):C.UVGC_385_50,(0,2,4):C.UVGC_385_51,(0,2,3):C.UVGC_447_154,(0,0,3):C.UVGC_305_6,(0,1,3):C.UVGC_308_9})

V_134 = CTVertex(name = 'V_134',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT15, L.FFVT35, L.FFVT46, L.FFVT48, L.FFVT49, L.FFVT6 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.d, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,0,4):C.UVGC_470_178,(0,3,4):C.UVGC_447_154,(0,1,1):C.UVGC_305_6,(0,2,1):C.UVGC_308_9,(0,4,0):C.UVGC_385_48,(0,4,2):C.UVGC_385_49,(0,4,3):C.UVGC_385_50,(0,4,5):C.UVGC_385_51,(0,5,1):C.UVGC_523_219})

V_135 = CTVertex(name = 'V_135',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.d, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_471_179})

V_136 = CTVertex(name = 'V_136',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.s, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT15 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_480_188})

V_137 = CTVertex(name = 'V_137',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT15, L.FFVT35, L.FFVT46, L.FFVT48, L.FFVT49, L.FFVT6 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.s] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,0,4):C.UVGC_481_189,(0,3,4):C.UVGC_447_154,(0,1,3):C.UVGC_305_6,(0,2,3):C.UVGC_308_9,(0,4,0):C.UVGC_385_48,(0,4,1):C.UVGC_385_49,(0,4,2):C.UVGC_385_50,(0,4,5):C.UVGC_385_51,(0,5,3):C.UVGC_523_219})

V_138 = CTVertex(name = 'V_138',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT35, L.FFVT47, L.FFVT49 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.c, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,2,0):C.UVGC_385_48,(0,2,2):C.UVGC_385_49,(0,2,3):C.UVGC_385_50,(0,2,5):C.UVGC_385_51,(0,2,4):C.UVGC_447_154,(0,0,1):C.UVGC_305_6,(0,1,1):C.UVGC_308_9})

V_139 = CTVertex(name = 'V_139',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT35, L.FFVT47, L.FFVT49 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,2,0):C.UVGC_385_48,(0,2,2):C.UVGC_385_49,(0,2,3):C.UVGC_385_50,(0,2,5):C.UVGC_385_51,(0,2,4):C.UVGC_447_154,(0,0,1):C.UVGC_305_6,(0,1,1):C.UVGC_308_9})

V_140 = CTVertex(name = 'V_140',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.g, P.Y2 ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFVT35, L.FFVT38, L.FFVT49 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.t] ], [ [P.t] ] ],
                 couplings = {(0,2,0):C.UVGC_436_139,(0,2,1):C.UVGC_436_140,(0,2,2):C.UVGC_436_141,(0,2,4):C.UVGC_436_142,(0,2,3):C.UVGC_436_143,(0,0,3):C.UVGC_305_6,(0,1,3):C.UVGC_349_21})

V_141 = CTVertex(name = 'V_141',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.u, P.W__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT12, L.FFVT15, L.FFVT29, L.FFVT8, L.FFVT9 ],
                 loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ], [ [P.g, P.u] ] ],
                 couplings = {(0,2,0):C.UVGC_393_62,(0,3,1):C.UVGC_367_26,(0,1,1):C.UVGC_368_27,(0,4,1):C.UVGC_529_222,(0,5,2):C.UVGC_450_158,(0,0,2):C.UVGC_451_159})

V_142 = CTVertex(name = 'V_142',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.u, P.W__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT12, L.FFVT15, L.FFVT29, L.FFVT8, L.FFVT9 ],
                 loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ], [ [P.g, P.u] ] ],
                 couplings = {(0,2,0):C.UVGC_497_200,(0,3,1):C.UVGC_494_197,(0,1,1):C.UVGC_495_198,(0,4,1):C.UVGC_538_226,(0,5,2):C.UVGC_452_160,(0,0,2):C.UVGC_453_161})

V_143 = CTVertex(name = 'V_143',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.d, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT15, L.FFVT16, L.FFVT22, L.FFVT29, L.FFVT9 ],
                 loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,0):C.UVGC_393_62,(0,4,1):C.UVGC_367_26,(0,3,1):C.UVGC_369_28,(0,2,1):C.UVGC_530_223,(0,5,2):C.UVGC_462_170,(0,0,2):C.UVGC_463_171})

V_144 = CTVertex(name = 'V_144',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.s, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT14, L.FFVT15, L.FFVT29, L.FFVT3, L.FFVT9 ],
                 loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ], [ [P.g, P.u] ] ],
                 couplings = {(0,2,0):C.UVGC_497_200,(0,3,1):C.UVGC_494_197,(0,1,1):C.UVGC_495_198,(0,4,1):C.UVGC_538_226,(0,5,2):C.UVGC_464_172,(0,0,2):C.UVGC_465_173})

V_145 = CTVertex(name = 'V_145',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.c, P.W__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT12, L.FFVT15, L.FFVT29, L.FFVT8, L.FFVT9 ],
                 loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,2,1):C.UVGC_496_199,(0,3,0):C.UVGC_491_194,(0,1,0):C.UVGC_492_195,(0,4,0):C.UVGC_536_224,(0,5,2):C.UVGC_454_162,(0,0,2):C.UVGC_455_163})

V_146 = CTVertex(name = 'V_146',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.c, P.W__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT12, L.FFVT15, L.FFVT29, L.FFVT8, L.FFVT9 ],
                 loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ], [ [P.g, P.u] ] ],
                 couplings = {(0,2,0):C.UVGC_393_62,(0,3,1):C.UVGC_367_26,(0,1,1):C.UVGC_368_27,(0,4,1):C.UVGC_529_222,(0,5,2):C.UVGC_456_164,(0,0,2):C.UVGC_457_165})

V_147 = CTVertex(name = 'V_147',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.d, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT15, L.FFVT16, L.FFVT22, L.FFVT29, L.FFVT9 ],
                 loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,1):C.UVGC_496_199,(0,4,0):C.UVGC_491_194,(0,3,0):C.UVGC_493_196,(0,2,0):C.UVGC_537_225,(0,5,2):C.UVGC_472_180,(0,0,2):C.UVGC_473_181})

V_148 = CTVertex(name = 'V_148',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.s, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT1, L.FFVT15, L.FFVT16, L.FFVT22, L.FFVT29, L.FFVT9 ],
                 loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ], [ [P.g, P.u] ] ],
                 couplings = {(0,1,0):C.UVGC_393_62,(0,4,1):C.UVGC_367_26,(0,3,1):C.UVGC_369_28,(0,2,1):C.UVGC_530_223,(0,5,2):C.UVGC_482_190,(0,0,2):C.UVGC_483_191})

V_149 = CTVertex(name = 'V_149',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.b, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT19, L.FFVT26, L.FFVT29 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_449_155,(0,0,2):C.UVGC_449_156,(0,0,3):C.UVGC_449_157,(0,3,1):C.UVGC_370_29,(0,1,1):C.UVGC_371_30,(0,2,1):C.UVGC_372_31})

V_150 = CTVertex(name = 'V_150',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.t, P.W__minus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFVT15, L.FFVT19, L.FFVT26, L.FFVT29 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ], [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_449_155,(0,0,2):C.UVGC_449_156,(0,0,3):C.UVGC_449_157,(0,3,1):C.UVGC_370_29,(0,2,1):C.UVGC_371_30,(0,1,1):C.UVGC_372_31})

V_151 = CTVertex(name = 'V_151',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.a ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV1 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_409_88})

V_152 = CTVertex(name = 'V_152',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV4, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.c, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,1):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,2):C.UVGC_383_44,(0,1,3):C.UVGC_383_45,(0,1,4):C.UVGC_383_46})

V_153 = CTVertex(name = 'V_153',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV1, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.t] ], [ [P.t] ] ],
                 couplings = {(0,0,3):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,1):C.UVGC_383_44,(0,1,2):C.UVGC_383_45,(0,1,4):C.UVGC_383_46,(0,1,3):C.UVGC_410_89})

V_154 = CTVertex(name = 'V_154',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV4, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                 couplings = {(0,0,3):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,1):C.UVGC_383_44,(0,1,2):C.UVGC_383_45,(0,1,4):C.UVGC_383_46})

V_155 = CTVertex(name = 'V_155',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV4, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,1):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,2):C.UVGC_383_44,(0,1,3):C.UVGC_383_45,(0,1,4):C.UVGC_383_46})

V_156 = CTVertex(name = 'V_156',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV4, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.d, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,1):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,2):C.UVGC_383_44,(0,1,3):C.UVGC_383_45,(0,1,4):C.UVGC_383_46})

V_157 = CTVertex(name = 'V_157',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s, P.g ],
                 color = [ 'T(3,2,1)' ],
                 lorentz = [ L.FFV4, L.FFV5 ],
                 loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.s] ], [ [P.t] ] ],
                 couplings = {(0,0,3):C.UVGC_302_3,(0,1,0):C.UVGC_383_43,(0,1,1):C.UVGC_383_44,(0,1,2):C.UVGC_383_45,(0,1,4):C.UVGC_383_46})

V_158 = CTVertex(name = 'V_158',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.c, P.W__minus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ] ],
                 couplings = {(0,0,1):C.UVGC_498_201,(0,0,0):C.UVGC_498_202})

V_159 = CTVertex(name = 'V_159',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                 couplings = {(0,0,0):C.UVGC_398_65,(0,0,1):C.UVGC_398_66})

V_160 = CTVertex(name = 'V_160',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_412_91,(0,0,2):C.UVGC_412_92,(0,0,1):C.UVGC_412_93})

V_161 = CTVertex(name = 'V_161',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_398_65,(0,0,1):C.UVGC_398_66})

V_162 = CTVertex(name = 'V_162',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.u, P.W__minus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_499_203,(0,0,1):C.UVGC_499_204})

V_163 = CTVertex(name = 'V_163',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_412_91,(0,0,2):C.UVGC_412_92,(0,0,1):C.UVGC_412_93})

V_164 = CTVertex(name = 'V_164',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.d, P.W__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ] ],
                 couplings = {(0,0,1):C.UVGC_498_201,(0,0,0):C.UVGC_498_202})

V_165 = CTVertex(name = 'V_165',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_398_65,(0,0,1):C.UVGC_398_66})

V_166 = CTVertex(name = 'V_166',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                 couplings = {(0,0,0):C.UVGC_398_65,(0,0,1):C.UVGC_398_66})

V_167 = CTVertex(name = 'V_167',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.s, P.W__plus__ ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2 ],
                 loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_499_203,(0,0,1):C.UVGC_499_204})

V_168 = CTVertex(name = 'V_168',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t, P.Z ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FFV2, L.FFV7 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_413_94,(0,1,0):C.UVGC_414_95})

V_169 = CTVertex(name = 'V_169',
                 type = 'UV',
                 particles = [ P.g, P.g, P.W__minus__, P.W__plus__, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.VVVVT16 ],
                 loop_particles = [ [ [P.b, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_394_63})

V_170 = CTVertex(name = 'V_170',
                 type = 'UV',
                 particles = [ P.g, P.g, P.g, P.Z, P.Y2 ],
                 color = [ 'f(1,2,3)' ],
                 lorentz = [ L.VVVVT16 ],
                 loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.u] ], [ [P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_390_58,(0,0,1):C.UVGC_390_59,(0,0,2):C.UVGC_390_60})

V_171 = CTVertex(name = 'V_171',
                 type = 'UV',
                 particles = [ P.g, P.g ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.VV1, L.VV5 ],
                 loop_particles = [ [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_376_32,(0,0,1):C.UVGC_376_33,(0,1,2):C.UVGC_401_68})

V_172 = CTVertex(name = 'V_172',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF2, L.FF3 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_411_90,(0,1,0):C.UVGC_408_87})

V_173 = CTVertex(name = 'V_173',
                 type = 'UV',
                 particles = [ P.g, P.g, P.Z, P.Y2 ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.VVVT4 ],
                 loop_particles = [ [ [P.b] ], [ [P.c], [P.u] ], [ [P.d], [P.s] ], [ [P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_520_213,(0,0,1):C.UVGC_520_214,(0,0,2):C.UVGC_520_215,(0,0,3):C.UVGC_520_216})

