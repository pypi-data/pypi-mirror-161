# This file was automatically created by FeynRules 2.3.26
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Tue 24 Jan 2017 14:52:59


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
               couplings = {(0,0,0):C.R2GC_201_97,(0,0,1):C.R2GC_201_98})

V_2 = CTVertex(name = 'V_2',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.g ],
               color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
               lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(2,1,0):C.R2GC_176_74,(2,1,1):C.R2GC_176_75,(0,1,0):C.R2GC_176_74,(0,1,1):C.R2GC_176_75,(4,1,0):C.R2GC_174_70,(4,1,1):C.R2GC_174_71,(3,1,0):C.R2GC_174_70,(3,1,1):C.R2GC_174_71,(8,1,0):C.R2GC_175_72,(8,1,1):C.R2GC_175_73,(7,1,0):C.R2GC_181_81,(7,1,1):C.R2GC_205_103,(6,1,0):C.R2GC_180_79,(6,1,1):C.R2GC_206_104,(5,1,0):C.R2GC_174_70,(5,1,1):C.R2GC_174_71,(1,1,0):C.R2GC_174_70,(1,1,1):C.R2GC_174_71,(11,0,0):C.R2GC_178_77,(11,0,1):C.R2GC_178_78,(10,0,0):C.R2GC_178_77,(10,0,1):C.R2GC_178_78,(9,0,1):C.R2GC_177_76,(2,2,0):C.R2GC_176_74,(2,2,1):C.R2GC_176_75,(0,2,0):C.R2GC_176_74,(0,2,1):C.R2GC_176_75,(6,2,0):C.R2GC_202_99,(6,2,1):C.R2GC_202_100,(4,2,0):C.R2GC_174_70,(4,2,1):C.R2GC_174_71,(3,2,0):C.R2GC_174_70,(3,2,1):C.R2GC_174_71,(8,2,0):C.R2GC_175_72,(8,2,1):C.R2GC_207_105,(7,2,0):C.R2GC_181_81,(7,2,1):C.R2GC_181_82,(5,2,0):C.R2GC_174_70,(5,2,1):C.R2GC_174_71,(1,2,0):C.R2GC_174_70,(1,2,1):C.R2GC_174_71,(2,3,0):C.R2GC_176_74,(2,3,1):C.R2GC_176_75,(0,3,0):C.R2GC_176_74,(0,3,1):C.R2GC_176_75,(4,3,0):C.R2GC_174_70,(4,3,1):C.R2GC_174_71,(3,3,0):C.R2GC_174_70,(3,3,1):C.R2GC_174_71,(8,3,0):C.R2GC_175_72,(8,3,1):C.R2GC_204_102,(6,3,0):C.R2GC_180_79,(6,3,1):C.R2GC_180_80,(7,3,0):C.R2GC_203_101,(7,3,1):C.R2GC_176_75,(5,3,0):C.R2GC_174_70,(5,3,1):C.R2GC_174_71,(1,3,0):C.R2GC_174_70,(1,3,1):C.R2GC_174_71})

V_3 = CTVertex(name = 'V_3',
               type = 'R2',
               particles = [ P.t__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS5 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_219_112})

V_4 = CTVertex(name = 'V_4',
               type = 'R2',
               particles = [ P.b__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_220_113})

V_5 = CTVertex(name = 'V_5',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_221_114})

V_6 = CTVertex(name = 'V_6',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS2 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_222_115})

V_7 = CTVertex(name = 'V_7',
               type = 'R2',
               particles = [ P.b__tilde__, P.b, P.Y1 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV6, L.FFV8 ],
               loop_particles = [ [ [P.b, P.g] ] ],
               couplings = {(0,0,0):C.R2GC_116_6,(0,1,0):C.R2GC_117_7})

V_8 = CTVertex(name = 'V_8',
               type = 'R2',
               particles = [ P.d__tilde__, P.b, P.Y1 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV6, L.FFV8 ],
               loop_particles = [ [ [P.b, P.d, P.g] ] ],
               couplings = {(0,0,0):C.R2GC_193_88,(0,1,0):C.R2GC_194_89})

V_9 = CTVertex(name = 'V_9',
               type = 'R2',
               particles = [ P.c__tilde__, P.c, P.Y1 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV6, L.FFV8 ],
               loop_particles = [ [ [P.c, P.g] ] ],
               couplings = {(0,0,0):C.R2GC_121_10,(0,1,0):C.R2GC_122_11})

V_10 = CTVertex(name = 'V_10',
                type = 'R2',
                particles = [ P.b__tilde__, P.d, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.b, P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_193_88,(0,1,0):C.R2GC_194_89})

V_11 = CTVertex(name = 'V_11',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_126_13,(0,1,0):C.R2GC_127_14})

V_12 = CTVertex(name = 'V_12',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_131_15,(0,1,0):C.R2GC_132_16})

V_13 = CTVertex(name = 'V_13',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_212_107,(0,1,0):C.R2GC_214_109})

V_14 = CTVertex(name = 'V_14',
                type = 'R2',
                particles = [ P.u__tilde__, P.t, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_211_106,(0,1,0):C.R2GC_213_108})

V_15 = CTVertex(name = 'V_15',
                type = 'R2',
                particles = [ P.t__tilde__, P.u, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_211_106,(0,1,0):C.R2GC_213_108})

V_16 = CTVertex(name = 'V_16',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_137_17,(0,1,0):C.R2GC_138_18})

V_17 = CTVertex(name = 'V_17',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_119_9})

V_18 = CTVertex(name = 'V_18',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_119_9})

V_19 = CTVertex(name = 'V_19',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_119_9})

V_20 = CTVertex(name = 'V_20',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_114_4})

V_21 = CTVertex(name = 'V_21',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_114_4})

V_22 = CTVertex(name = 'V_22',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_114_4})

V_23 = CTVertex(name = 'V_23',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_24 = CTVertex(name = 'V_24',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_25 = CTVertex(name = 'V_25',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_26 = CTVertex(name = 'V_26',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_27 = CTVertex(name = 'V_27',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_28 = CTVertex(name = 'V_28',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_115_5})

V_29 = CTVertex(name = 'V_29',
                type = 'R2',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_195_90})

V_30 = CTVertex(name = 'V_30',
                type = 'R2',
                particles = [ P.s__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_197_92})

V_31 = CTVertex(name = 'V_31',
                type = 'R2',
                particles = [ P.d__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_189_84})

V_32 = CTVertex(name = 'V_32',
                type = 'R2',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_191_86})

V_33 = CTVertex(name = 'V_33',
                type = 'R2',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_216_111})

V_34 = CTVertex(name = 'V_34',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_196_91})

V_35 = CTVertex(name = 'V_35',
                type = 'R2',
                particles = [ P.c__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_190_85})

V_36 = CTVertex(name = 'V_36',
                type = 'R2',
                particles = [ P.u__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_198_93})

V_37 = CTVertex(name = 'V_37',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_192_87})

V_38 = CTVertex(name = 'V_38',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_216_111})

V_39 = CTVertex(name = 'V_39',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_151_56,(0,1,0):C.R2GC_123_12})

V_40 = CTVertex(name = 'V_40',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_151_56,(0,1,0):C.R2GC_123_12})

V_41 = CTVertex(name = 'V_41',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_151_56,(0,1,0):C.R2GC_123_12})

V_42 = CTVertex(name = 'V_42',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_150_55,(0,1,0):C.R2GC_118_8})

V_43 = CTVertex(name = 'V_43',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_150_55,(0,1,0):C.R2GC_118_8})

V_44 = CTVertex(name = 'V_44',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_150_55,(0,1,0):C.R2GC_118_8})

V_45 = CTVertex(name = 'V_45',
                type = 'R2',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_182_83})

V_46 = CTVertex(name = 'V_46',
                type = 'R2',
                particles = [ P.c__tilde__, P.c ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_83})

V_47 = CTVertex(name = 'V_47',
                type = 'R2',
                particles = [ P.t__tilde__, P.t ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_215_110,(0,2,0):C.R2GC_215_110,(0,1,0):C.R2GC_182_83,(0,3,0):C.R2GC_182_83})

V_48 = CTVertex(name = 'V_48',
                type = 'R2',
                particles = [ P.d__tilde__, P.d ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_83})

V_49 = CTVertex(name = 'V_49',
                type = 'R2',
                particles = [ P.s__tilde__, P.s ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_182_83})

V_50 = CTVertex(name = 'V_50',
                type = 'R2',
                particles = [ P.b__tilde__, P.b ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_182_83})

V_51 = CTVertex(name = 'V_51',
                type = 'R2',
                particles = [ P.g, P.g ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VV1, L.VV2, L.VV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.R2GC_200_96,(0,1,2):C.R2GC_111_1,(0,2,0):C.R2GC_199_94,(0,2,1):C.R2GC_199_95})

V_52 = CTVertex(name = 'V_52',
                type = 'R2',
                particles = [ P.g, P.g, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_112_2})

V_53 = CTVertex(name = 'V_53',
                type = 'R2',
                particles = [ P.g, P.g, P.Y1, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b] ], [ [P.b, P.d] ], [ [P.c] ], [ [P.d] ], [ [P.s] ], [ [P.t] ], [ [P.t, P.u] ], [ [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_156_62,(0,0,2):C.R2GC_156_63,(0,0,3):C.R2GC_156_64,(0,0,4):C.R2GC_156_65,(0,0,5):C.R2GC_156_66,(0,0,7):C.R2GC_156_67,(0,0,1):C.R2GC_156_68,(0,0,6):C.R2GC_156_69,(0,1,0):C.R2GC_156_62,(0,1,2):C.R2GC_156_63,(0,1,3):C.R2GC_156_64,(0,1,4):C.R2GC_156_65,(0,1,5):C.R2GC_156_66,(0,1,7):C.R2GC_156_67,(0,1,1):C.R2GC_156_68,(0,1,6):C.R2GC_156_69,(0,2,0):C.R2GC_156_62,(0,2,2):C.R2GC_156_63,(0,2,3):C.R2GC_156_64,(0,2,4):C.R2GC_156_65,(0,2,5):C.R2GC_156_66,(0,2,7):C.R2GC_156_67,(0,2,1):C.R2GC_156_68,(0,2,6):C.R2GC_156_69})

V_54 = CTVertex(name = 'V_54',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Y1 ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b] ], [ [P.c] ], [ [P.d] ], [ [P.s] ], [ [P.t] ], [ [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_143_29,(0,0,1):C.R2GC_143_30,(0,0,2):C.R2GC_143_31,(0,0,3):C.R2GC_143_32,(0,0,4):C.R2GC_143_33,(0,0,5):C.R2GC_143_34,(0,1,0):C.R2GC_143_29,(0,1,1):C.R2GC_143_30,(0,1,2):C.R2GC_143_31,(0,1,3):C.R2GC_143_32,(0,1,4):C.R2GC_143_33,(0,1,5):C.R2GC_143_34,(0,2,0):C.R2GC_143_29,(0,2,1):C.R2GC_143_30,(0,2,2):C.R2GC_143_31,(0,2,3):C.R2GC_143_32,(0,2,4):C.R2GC_143_33,(0,2,5):C.R2GC_143_34})

V_55 = CTVertex(name = 'V_55',
                type = 'R2',
                particles = [ P.g, P.g, P.Y1, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b] ], [ [P.c] ], [ [P.d] ], [ [P.s] ], [ [P.t] ], [ [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_148_47,(0,0,1):C.R2GC_148_48,(0,0,2):C.R2GC_148_49,(0,0,3):C.R2GC_148_50,(0,0,4):C.R2GC_148_51,(0,0,5):C.R2GC_148_52,(0,1,0):C.R2GC_148_47,(0,1,1):C.R2GC_148_48,(0,1,2):C.R2GC_148_49,(0,1,3):C.R2GC_148_50,(0,1,4):C.R2GC_148_51,(0,1,5):C.R2GC_148_52,(0,2,0):C.R2GC_148_47,(0,2,1):C.R2GC_148_48,(0,2,2):C.R2GC_148_49,(0,2,3):C.R2GC_148_50,(0,2,4):C.R2GC_148_51,(0,2,5):C.R2GC_148_52})

V_56 = CTVertex(name = 'V_56',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Y1 ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b] ], [ [P.c] ], [ [P.d] ], [ [P.s] ], [ [P.t] ], [ [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_142_23,(1,0,1):C.R2GC_142_24,(1,0,2):C.R2GC_142_25,(1,0,3):C.R2GC_142_26,(1,0,4):C.R2GC_142_27,(1,0,5):C.R2GC_142_28,(0,1,0):C.R2GC_144_35,(0,1,1):C.R2GC_144_36,(0,1,2):C.R2GC_144_37,(0,1,3):C.R2GC_144_38,(0,1,4):C.R2GC_144_39,(0,1,5):C.R2GC_144_40,(0,2,0):C.R2GC_144_35,(0,2,1):C.R2GC_144_36,(0,2,2):C.R2GC_144_37,(0,2,3):C.R2GC_144_38,(0,2,4):C.R2GC_144_39,(0,2,5):C.R2GC_144_40,(0,3,0):C.R2GC_144_35,(0,3,1):C.R2GC_144_36,(0,3,2):C.R2GC_144_37,(0,3,3):C.R2GC_144_38,(0,3,4):C.R2GC_144_39,(0,3,5):C.R2GC_144_40})

V_57 = CTVertex(name = 'V_57',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t] ], [ [P.c, P.d] ], [ [P.c, P.s] ], [ [P.d, P.u] ], [ [P.s, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_155_57,(0,0,1):C.R2GC_155_58,(0,0,2):C.R2GC_155_59,(0,0,3):C.R2GC_155_60,(0,0,4):C.R2GC_155_61,(0,1,0):C.R2GC_155_57,(0,1,1):C.R2GC_155_58,(0,1,2):C.R2GC_155_59,(0,1,3):C.R2GC_155_60,(0,1,4):C.R2GC_155_61,(0,2,0):C.R2GC_155_57,(0,2,1):C.R2GC_155_58,(0,2,2):C.R2GC_155_59,(0,2,3):C.R2GC_155_60,(0,2,4):C.R2GC_155_61})

V_58 = CTVertex(name = 'V_58',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Z ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_145_41,(0,0,1):C.R2GC_145_42,(0,1,0):C.R2GC_145_41,(0,1,1):C.R2GC_145_42,(0,2,0):C.R2GC_145_41,(0,2,1):C.R2GC_145_42})

V_59 = CTVertex(name = 'V_59',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_149_53,(0,0,1):C.R2GC_149_54,(0,1,0):C.R2GC_149_53,(0,1,1):C.R2GC_149_54,(0,2,0):C.R2GC_149_53,(0,2,1):C.R2GC_149_54})

V_60 = CTVertex(name = 'V_60',
                type = 'R2',
                particles = [ P.a, P.a, P.g, P.g ],
                color = [ 'Identity(3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_140_19,(0,0,1):C.R2GC_140_20,(0,1,0):C.R2GC_140_19,(0,1,1):C.R2GC_140_20,(0,2,0):C.R2GC_140_19,(0,2,1):C.R2GC_140_20})

V_61 = CTVertex(name = 'V_61',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Z ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_147_45,(1,0,1):C.R2GC_147_46,(0,1,0):C.R2GC_146_43,(0,1,1):C.R2GC_146_44,(0,2,0):C.R2GC_146_43,(0,2,1):C.R2GC_146_44,(0,3,0):C.R2GC_146_43,(0,3,1):C.R2GC_146_44})

V_62 = CTVertex(name = 'V_62',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.g ],
                color = [ 'd(2,3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_141_21,(0,0,1):C.R2GC_141_22,(0,1,0):C.R2GC_141_21,(0,1,1):C.R2GC_141_22,(0,2,0):C.R2GC_141_21,(0,2,1):C.R2GC_141_22})

V_63 = CTVertex(name = 'V_63',
                type = 'R2',
                particles = [ P.g, P.g, P.H, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_113_3})

V_64 = CTVertex(name = 'V_64',
                type = 'R2',
                particles = [ P.g, P.g, P.G0, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_113_3})

V_65 = CTVertex(name = 'V_65',
                type = 'R2',
                particles = [ P.g, P.g, P.G__minus__, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.b, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_113_3})

V_66 = CTVertex(name = 'V_66',
                type = 'UV',
                particles = [ P.g, P.g, P.g ],
                color = [ 'f(1,2,3)' ],
                lorentz = [ L.VVV1, L.VVV2, L.VVV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,1,0):C.UVGC_201_48,(0,1,3):C.UVGC_201_49,(0,2,1):C.UVGC_157_1,(0,0,2):C.UVGC_158_2})

V_67 = CTVertex(name = 'V_67',
                type = 'UV',
                particles = [ P.g, P.g, P.g, P.g ],
                color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
                lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(2,1,2):C.UVGC_175_10,(2,1,3):C.UVGC_175_9,(0,1,2):C.UVGC_175_10,(0,1,3):C.UVGC_175_9,(4,1,2):C.UVGC_174_7,(4,1,3):C.UVGC_174_8,(3,1,2):C.UVGC_174_7,(3,1,3):C.UVGC_174_8,(8,1,2):C.UVGC_175_9,(8,1,3):C.UVGC_175_10,(7,1,1):C.UVGC_205_59,(7,1,2):C.UVGC_205_60,(7,1,3):C.UVGC_205_61,(7,1,4):C.UVGC_205_62,(6,1,1):C.UVGC_205_59,(6,1,2):C.UVGC_206_63,(6,1,3):C.UVGC_206_64,(6,1,4):C.UVGC_205_62,(5,1,2):C.UVGC_174_7,(5,1,3):C.UVGC_174_8,(1,1,2):C.UVGC_174_7,(1,1,3):C.UVGC_174_8,(11,0,2):C.UVGC_178_13,(11,0,3):C.UVGC_178_14,(10,0,2):C.UVGC_178_13,(10,0,3):C.UVGC_178_14,(9,0,2):C.UVGC_177_11,(9,0,3):C.UVGC_177_12,(2,2,2):C.UVGC_175_10,(2,2,3):C.UVGC_175_9,(0,2,2):C.UVGC_175_10,(0,2,3):C.UVGC_175_9,(6,2,2):C.UVGC_202_50,(6,2,3):C.UVGC_202_51,(6,2,4):C.UVGC_202_52,(4,2,2):C.UVGC_174_7,(4,2,3):C.UVGC_174_8,(3,2,2):C.UVGC_174_7,(3,2,3):C.UVGC_174_8,(8,2,1):C.UVGC_207_65,(8,2,2):C.UVGC_207_66,(8,2,3):C.UVGC_207_67,(8,2,4):C.UVGC_207_68,(7,2,0):C.UVGC_180_19,(7,2,2):C.UVGC_181_21,(7,2,3):C.UVGC_181_22,(5,2,2):C.UVGC_174_7,(5,2,3):C.UVGC_174_8,(1,2,2):C.UVGC_174_7,(1,2,3):C.UVGC_174_8,(2,3,2):C.UVGC_175_10,(2,3,3):C.UVGC_175_9,(0,3,2):C.UVGC_175_10,(0,3,3):C.UVGC_175_9,(4,3,2):C.UVGC_174_7,(4,3,3):C.UVGC_174_8,(3,3,2):C.UVGC_174_7,(3,3,3):C.UVGC_174_8,(8,3,1):C.UVGC_204_55,(8,3,2):C.UVGC_204_56,(8,3,3):C.UVGC_204_57,(8,3,4):C.UVGC_204_58,(6,3,0):C.UVGC_180_19,(6,3,2):C.UVGC_180_20,(6,3,3):C.UVGC_177_11,(7,3,2):C.UVGC_203_53,(7,3,3):C.UVGC_203_54,(7,3,4):C.UVGC_202_52,(5,3,2):C.UVGC_174_7,(5,3,3):C.UVGC_174_8,(1,3,2):C.UVGC_174_7,(1,3,3):C.UVGC_174_8})

V_68 = CTVertex(name = 'V_68',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS5 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_219_86,(0,0,2):C.UVGC_219_87,(0,0,1):C.UVGC_219_88})

V_69 = CTVertex(name = 'V_69',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.G__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_220_89,(0,0,2):C.UVGC_220_90,(0,0,1):C.UVGC_220_91})

V_70 = CTVertex(name = 'V_70',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_221_92})

V_71 = CTVertex(name = 'V_71',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS2 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_222_93})

V_72 = CTVertex(name = 'V_72',
                type = 'UV',
                particles = [ P.d__tilde__, P.b, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.b, P.d, P.g] ], [ [P.b, P.g], [P.d, P.g] ] ],
                couplings = {(0,0,1):C.UVGC_193_32,(0,0,0):C.UVGC_193_33,(0,1,1):C.UVGC_194_34,(0,1,0):C.UVGC_194_35})

V_73 = CTVertex(name = 'V_73',
                type = 'UV',
                particles = [ P.b__tilde__, P.d, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.b, P.d, P.g] ], [ [P.b, P.g], [P.d, P.g] ] ],
                couplings = {(0,0,1):C.UVGC_193_32,(0,0,0):C.UVGC_193_33,(0,1,1):C.UVGC_194_34,(0,1,0):C.UVGC_194_35})

V_74 = CTVertex(name = 'V_74',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_212_75,(0,1,0):C.UVGC_214_79})

V_75 = CTVertex(name = 'V_75',
                type = 'UV',
                particles = [ P.u__tilde__, P.t, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t] ], [ [P.g, P.t, P.u] ], [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_211_72,(0,0,2):C.UVGC_211_73,(0,0,1):C.UVGC_211_74,(0,1,0):C.UVGC_213_76,(0,1,2):C.UVGC_213_77,(0,1,1):C.UVGC_213_78})

V_76 = CTVertex(name = 'V_76',
                type = 'UV',
                particles = [ P.t__tilde__, P.u, P.Y1 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV6, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t] ], [ [P.g, P.t, P.u] ], [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_211_72,(0,0,2):C.UVGC_211_73,(0,0,1):C.UVGC_211_74,(0,1,0):C.UVGC_213_76,(0,1,2):C.UVGC_213_77,(0,1,1):C.UVGC_213_78})

V_77 = CTVertex(name = 'V_77',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV5 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_163_6})

V_78 = CTVertex(name = 'V_78',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV5 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_163_6})

V_79 = CTVertex(name = 'V_79',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV8 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_163_6,(0,1,0):C.UVGC_209_70})

V_80 = CTVertex(name = 'V_80',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV5 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_160_4})

V_81 = CTVertex(name = 'V_81',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV5 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_160_4})

V_82 = CTVertex(name = 'V_82',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV5 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_160_4})

V_83 = CTVertex(name = 'V_83',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV7, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,1):C.UVGC_179_16,(0,1,2):C.UVGC_179_17,(0,1,4):C.UVGC_179_18})

V_84 = CTVertex(name = 'V_84',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV7, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.c, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,2):C.UVGC_179_16,(0,1,3):C.UVGC_179_17,(0,1,4):C.UVGC_179_18})

V_85 = CTVertex(name = 'V_85',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.t] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,1):C.UVGC_179_16,(0,1,2):C.UVGC_179_17,(0,1,4):C.UVGC_179_18,(0,1,3):C.UVGC_210_71})

V_86 = CTVertex(name = 'V_86',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV7, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.d, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,2):C.UVGC_179_16,(0,1,3):C.UVGC_179_17,(0,1,4):C.UVGC_179_18})

V_87 = CTVertex(name = 'V_87',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV7, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.s] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,1):C.UVGC_179_16,(0,1,2):C.UVGC_179_17,(0,1,4):C.UVGC_179_18})

V_88 = CTVertex(name = 'V_88',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV7, L.FFV8 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_161_5,(0,1,0):C.UVGC_179_15,(0,1,2):C.UVGC_179_16,(0,1,3):C.UVGC_179_17,(0,1,4):C.UVGC_179_18})

V_89 = CTVertex(name = 'V_89',
                type = 'UV',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_195_36,(0,0,1):C.UVGC_195_37})

V_90 = CTVertex(name = 'V_90',
                type = 'UV',
                particles = [ P.s__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_197_40,(0,0,1):C.UVGC_197_41})

V_91 = CTVertex(name = 'V_91',
                type = 'UV',
                particles = [ P.d__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ] ],
                couplings = {(0,0,1):C.UVGC_189_24,(0,0,0):C.UVGC_189_25})

V_92 = CTVertex(name = 'V_92',
                type = 'UV',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_191_28,(0,0,1):C.UVGC_191_29})

V_93 = CTVertex(name = 'V_93',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_216_81,(0,0,2):C.UVGC_216_82,(0,0,1):C.UVGC_216_83})

V_94 = CTVertex(name = 'V_94',
                type = 'UV',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_196_38,(0,0,1):C.UVGC_196_39})

V_95 = CTVertex(name = 'V_95',
                type = 'UV',
                particles = [ P.c__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.d, P.g] ], [ [P.c, P.g], [P.d, P.g] ] ],
                couplings = {(0,0,1):C.UVGC_190_26,(0,0,0):C.UVGC_190_27})

V_96 = CTVertex(name = 'V_96',
                type = 'UV',
                particles = [ P.u__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.g, P.s], [P.g, P.u] ], [ [P.g, P.s, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_198_42,(0,0,1):C.UVGC_198_43})

V_97 = CTVertex(name = 'V_97',
                type = 'UV',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_192_30,(0,0,1):C.UVGC_192_31})

V_98 = CTVertex(name = 'V_98',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_216_81,(0,0,2):C.UVGC_216_82,(0,0,1):C.UVGC_216_83})

V_99 = CTVertex(name = 'V_99',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV3, L.FFV4 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_217_84,(0,1,0):C.UVGC_218_85})

V_100 = CTVertex(name = 'V_100',
                 type = 'UV',
                 particles = [ P.u__tilde__, P.u ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.g, P.u] ] ],
                 couplings = {(0,0,0):C.UVGC_182_23,(0,1,0):C.UVGC_159_3,(0,2,0):C.UVGC_159_3})

V_101 = CTVertex(name = 'V_101',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.c, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_182_23,(0,1,0):C.UVGC_159_3,(0,2,0):C.UVGC_159_3})

V_102 = CTVertex(name = 'V_102',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_215_80,(0,2,0):C.UVGC_215_80,(0,1,0):C.UVGC_208_69,(0,3,0):C.UVGC_208_69})

V_103 = CTVertex(name = 'V_103',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.d, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_182_23,(0,1,0):C.UVGC_159_3,(0,2,0):C.UVGC_159_3})

V_104 = CTVertex(name = 'V_104',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.g, P.s] ] ],
                 couplings = {(0,0,0):C.UVGC_182_23,(0,1,0):C.UVGC_159_3,(0,2,0):C.UVGC_159_3})

V_105 = CTVertex(name = 'V_105',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.b, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_182_23,(0,1,0):C.UVGC_159_3,(0,2,0):C.UVGC_159_3})

V_106 = CTVertex(name = 'V_106',
                 type = 'UV',
                 particles = [ P.g, P.g ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.VV1, L.VV3 ],
                 loop_particles = [ [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_200_45,(0,0,1):C.UVGC_200_46,(0,0,2):C.UVGC_200_47,(0,1,2):C.UVGC_199_44})

