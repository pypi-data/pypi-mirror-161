# This file was automatically created by FeynRules 2.3.10
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Tue 28 Jun 2016 11:09:04


from object_library import all_vertices, all_CTvertices, Vertex, CTVertex
import particles as P
import CT_couplings as C
import lorentz as L


V_1 = CTVertex(name = 'V_1',
               type = 'R2',
               particles = [ P.g, P.g, P.g ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVV2 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(0,0,0):C.R2GC_189_42,(0,0,1):C.R2GC_189_43})

V_2 = CTVertex(name = 'V_2',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.g ],
               color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
               lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(2,1,0):C.R2GC_158_25,(2,1,1):C.R2GC_158_26,(0,1,0):C.R2GC_158_25,(0,1,1):C.R2GC_158_26,(4,1,0):C.R2GC_156_21,(4,1,1):C.R2GC_156_22,(3,1,0):C.R2GC_156_21,(3,1,1):C.R2GC_156_22,(8,1,0):C.R2GC_157_23,(8,1,1):C.R2GC_157_24,(7,1,0):C.R2GC_162_32,(7,1,1):C.R2GC_193_48,(6,1,0):C.R2GC_161_30,(6,1,1):C.R2GC_194_49,(5,1,0):C.R2GC_156_21,(5,1,1):C.R2GC_156_22,(1,1,0):C.R2GC_156_21,(1,1,1):C.R2GC_156_22,(11,0,0):C.R2GC_160_28,(11,0,1):C.R2GC_160_29,(10,0,0):C.R2GC_160_28,(10,0,1):C.R2GC_160_29,(9,0,1):C.R2GC_159_27,(2,2,0):C.R2GC_158_25,(2,2,1):C.R2GC_158_26,(0,2,0):C.R2GC_158_25,(0,2,1):C.R2GC_158_26,(6,2,0):C.R2GC_190_44,(6,2,1):C.R2GC_190_45,(4,2,0):C.R2GC_156_21,(4,2,1):C.R2GC_156_22,(3,2,0):C.R2GC_156_21,(3,2,1):C.R2GC_156_22,(8,2,0):C.R2GC_157_23,(8,2,1):C.R2GC_195_50,(7,2,0):C.R2GC_162_32,(7,2,1):C.R2GC_162_33,(5,2,0):C.R2GC_156_21,(5,2,1):C.R2GC_156_22,(1,2,0):C.R2GC_156_21,(1,2,1):C.R2GC_156_22,(2,3,0):C.R2GC_158_25,(2,3,1):C.R2GC_158_26,(0,3,0):C.R2GC_158_25,(0,3,1):C.R2GC_158_26,(4,3,0):C.R2GC_156_21,(4,3,1):C.R2GC_156_22,(3,3,0):C.R2GC_156_21,(3,3,1):C.R2GC_156_22,(8,3,0):C.R2GC_157_23,(8,3,1):C.R2GC_192_47,(6,3,0):C.R2GC_161_30,(6,3,1):C.R2GC_161_31,(7,3,0):C.R2GC_191_46,(7,3,1):C.R2GC_158_26,(5,3,0):C.R2GC_156_21,(5,3,1):C.R2GC_156_22,(1,3,0):C.R2GC_156_21,(1,3,1):C.R2GC_156_22})

V_3 = CTVertex(name = 'V_3',
               type = 'R2',
               particles = [ P.t__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS5 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_203_52})

V_4 = CTVertex(name = 'V_4',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_205_54})

V_5 = CTVertex(name = 'V_5',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS2 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_206_55})

V_6 = CTVertex(name = 'V_6',
               type = 'R2',
               particles = [ P.b__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_204_53})

V_7 = CTVertex(name = 'V_7',
               type = 'R2',
               particles = [ P.u__tilde__, P.u, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               loop_particles = [ [ [P.g, P.u] ] ],
               couplings = {(0,0,0):C.R2GC_168_37})

V_8 = CTVertex(name = 'V_8',
               type = 'R2',
               particles = [ P.c__tilde__, P.c, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               loop_particles = [ [ [P.c, P.g] ] ],
               couplings = {(0,0,0):C.R2GC_168_37})

V_9 = CTVertex(name = 'V_9',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_168_37})

V_10 = CTVertex(name = 'V_10',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_11 = CTVertex(name = 'V_11',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_12 = CTVertex(name = 'V_12',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_13 = CTVertex(name = 'V_13',
                type = 'R2',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_14 = CTVertex(name = 'V_14',
                type = 'R2',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_15 = CTVertex(name = 'V_15',
                type = 'R2',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_16 = CTVertex(name = 'V_16',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_139_19,(0,1,0):C.R2GC_127_5})

V_17 = CTVertex(name = 'V_17',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_139_19,(0,1,0):C.R2GC_127_5})

V_18 = CTVertex(name = 'V_18',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_139_19,(0,1,0):C.R2GC_127_5})

V_19 = CTVertex(name = 'V_19',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_164_35})

V_20 = CTVertex(name = 'V_20',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_164_35})

V_21 = CTVertex(name = 'V_21',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_164_35})

V_22 = CTVertex(name = 'V_22',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_23 = CTVertex(name = 'V_23',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_24 = CTVertex(name = 'V_24',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_166_36})

V_25 = CTVertex(name = 'V_25',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_26 = CTVertex(name = 'V_26',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_27 = CTVertex(name = 'V_27',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_185_38})

V_28 = CTVertex(name = 'V_28',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_138_18,(0,1,0):C.R2GC_126_4})

V_29 = CTVertex(name = 'V_29',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_138_18,(0,1,0):C.R2GC_126_4})

V_30 = CTVertex(name = 'V_30',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_138_18,(0,1,0):C.R2GC_126_4})

V_31 = CTVertex(name = 'V_31',
                type = 'R2',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_163_34})

V_32 = CTVertex(name = 'V_32',
                type = 'R2',
                particles = [ P.c__tilde__, P.c ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_163_34})

V_33 = CTVertex(name = 'V_33',
                type = 'R2',
                particles = [ P.t__tilde__, P.t ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_199_51,(0,2,0):C.R2GC_199_51,(0,1,0):C.R2GC_163_34,(0,3,0):C.R2GC_163_34})

V_34 = CTVertex(name = 'V_34',
                type = 'R2',
                particles = [ P.d__tilde__, P.d ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_163_34})

V_35 = CTVertex(name = 'V_35',
                type = 'R2',
                particles = [ P.s__tilde__, P.s ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_163_34})

V_36 = CTVertex(name = 'V_36',
                type = 'R2',
                particles = [ P.b__tilde__, P.b ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_163_34})

V_37 = CTVertex(name = 'V_37',
                type = 'R2',
                particles = [ P.g, P.g ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VV1, L.VV2, L.VV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.R2GC_188_41,(0,1,2):C.R2GC_123_1,(0,2,0):C.R2GC_187_39,(0,2,1):C.R2GC_187_40})

V_38 = CTVertex(name = 'V_38',
                type = 'R2',
                particles = [ P.g, P.g, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_124_2})

V_39 = CTVertex(name = 'V_39',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t], [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_142_20,(0,1,0):C.R2GC_142_20,(0,2,0):C.R2GC_142_20})

V_40 = CTVertex(name = 'V_40',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Z ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_134_10,(0,0,1):C.R2GC_134_11,(0,1,0):C.R2GC_134_10,(0,1,1):C.R2GC_134_11,(0,2,0):C.R2GC_134_10,(0,2,1):C.R2GC_134_11})

V_41 = CTVertex(name = 'V_41',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_137_16,(0,0,1):C.R2GC_137_17,(0,1,0):C.R2GC_137_16,(0,1,1):C.R2GC_137_17,(0,2,0):C.R2GC_137_16,(0,2,1):C.R2GC_137_17})

V_42 = CTVertex(name = 'V_42',
                type = 'R2',
                particles = [ P.a, P.a, P.g, P.g ],
                color = [ 'Identity(3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_132_6,(0,0,1):C.R2GC_132_7,(0,1,0):C.R2GC_132_6,(0,1,1):C.R2GC_132_7,(0,2,0):C.R2GC_132_6,(0,2,1):C.R2GC_132_7})

V_43 = CTVertex(name = 'V_43',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Z ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_136_14,(1,0,1):C.R2GC_136_15,(0,1,0):C.R2GC_135_12,(0,1,1):C.R2GC_135_13,(0,2,0):C.R2GC_135_12,(0,2,1):C.R2GC_135_13,(0,3,0):C.R2GC_135_12,(0,3,1):C.R2GC_135_13})

V_44 = CTVertex(name = 'V_44',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.g ],
                color = [ 'd(2,3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_133_8,(0,0,1):C.R2GC_133_9,(0,1,0):C.R2GC_133_8,(0,1,1):C.R2GC_133_9,(0,2,0):C.R2GC_133_8,(0,2,1):C.R2GC_133_9})

V_45 = CTVertex(name = 'V_45',
                type = 'R2',
                particles = [ P.g, P.g, P.H, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_125_3})

V_46 = CTVertex(name = 'V_46',
                type = 'R2',
                particles = [ P.g, P.g, P.G0, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_125_3})

V_47 = CTVertex(name = 'V_47',
                type = 'R2',
                particles = [ P.g, P.g, P.G__minus__, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.b, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_125_3})

V_48 = CTVertex(name = 'V_48',
                type = 'UV',
                particles = [ P.g, P.g, P.g ],
                color = [ 'f(1,2,3)' ],
                lorentz = [ L.VVV1, L.VVV2, L.VVV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,1,0):C.UVGC_189_33,(0,1,3):C.UVGC_189_34,(0,2,1):C.UVGC_144_1,(0,0,2):C.UVGC_145_2})

V_49 = CTVertex(name = 'V_49',
                type = 'UV',
                particles = [ P.g, P.g, P.g, P.g ],
                color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
                lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(2,1,2):C.UVGC_157_9,(2,1,3):C.UVGC_157_8,(0,1,2):C.UVGC_157_9,(0,1,3):C.UVGC_157_8,(4,1,2):C.UVGC_156_6,(4,1,3):C.UVGC_156_7,(3,1,2):C.UVGC_156_6,(3,1,3):C.UVGC_156_7,(8,1,2):C.UVGC_157_8,(8,1,3):C.UVGC_157_9,(7,1,1):C.UVGC_193_44,(7,1,2):C.UVGC_193_45,(7,1,3):C.UVGC_193_46,(7,1,4):C.UVGC_193_47,(6,1,1):C.UVGC_193_44,(6,1,2):C.UVGC_194_48,(6,1,3):C.UVGC_194_49,(6,1,4):C.UVGC_193_47,(5,1,2):C.UVGC_156_6,(5,1,3):C.UVGC_156_7,(1,1,2):C.UVGC_156_6,(1,1,3):C.UVGC_156_7,(11,0,2):C.UVGC_160_12,(11,0,3):C.UVGC_160_13,(10,0,2):C.UVGC_160_12,(10,0,3):C.UVGC_160_13,(9,0,2):C.UVGC_159_10,(9,0,3):C.UVGC_159_11,(2,2,2):C.UVGC_157_9,(2,2,3):C.UVGC_157_8,(0,2,2):C.UVGC_157_9,(0,2,3):C.UVGC_157_8,(6,2,2):C.UVGC_190_35,(6,2,3):C.UVGC_190_36,(6,2,4):C.UVGC_190_37,(4,2,2):C.UVGC_156_6,(4,2,3):C.UVGC_156_7,(3,2,2):C.UVGC_156_6,(3,2,3):C.UVGC_156_7,(8,2,1):C.UVGC_195_50,(8,2,2):C.UVGC_195_51,(8,2,3):C.UVGC_195_52,(8,2,4):C.UVGC_195_53,(7,2,0):C.UVGC_161_14,(7,2,2):C.UVGC_162_16,(7,2,3):C.UVGC_162_17,(5,2,2):C.UVGC_156_6,(5,2,3):C.UVGC_156_7,(1,2,2):C.UVGC_156_6,(1,2,3):C.UVGC_156_7,(2,3,2):C.UVGC_157_9,(2,3,3):C.UVGC_157_8,(0,3,2):C.UVGC_157_9,(0,3,3):C.UVGC_157_8,(4,3,2):C.UVGC_156_6,(4,3,3):C.UVGC_156_7,(3,3,2):C.UVGC_156_6,(3,3,3):C.UVGC_156_7,(8,3,1):C.UVGC_192_40,(8,3,2):C.UVGC_192_41,(8,3,3):C.UVGC_192_42,(8,3,4):C.UVGC_192_43,(6,3,0):C.UVGC_161_14,(6,3,2):C.UVGC_161_15,(6,3,3):C.UVGC_159_10,(7,3,2):C.UVGC_191_38,(7,3,3):C.UVGC_191_39,(7,3,4):C.UVGC_190_37,(5,3,2):C.UVGC_156_6,(5,3,3):C.UVGC_156_7,(1,3,2):C.UVGC_156_6,(1,3,3):C.UVGC_156_7})

V_50 = CTVertex(name = 'V_50',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS5 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_203_61,(0,0,2):C.UVGC_203_62,(0,0,1):C.UVGC_203_63})

V_51 = CTVertex(name = 'V_51',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_205_67})

V_52 = CTVertex(name = 'V_52',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS2 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_206_68})

V_53 = CTVertex(name = 'V_53',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.G__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_204_64,(0,0,2):C.UVGC_204_65,(0,0,1):C.UVGC_204_66})

V_54 = CTVertex(name = 'V_54',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_168_26,(0,1,0):C.UVGC_149_5,(0,2,0):C.UVGC_149_5})

V_55 = CTVertex(name = 'V_55',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_168_26,(0,1,0):C.UVGC_149_5,(0,2,0):C.UVGC_149_5})

V_56 = CTVertex(name = 'V_56',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_168_26,(0,1,0):C.UVGC_197_55,(0,2,0):C.UVGC_197_55})

V_57 = CTVertex(name = 'V_57',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,1):C.UVGC_165_21,(0,1,2):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,3):C.UVGC_165_24,(0,2,0):C.UVGC_165_20,(0,2,1):C.UVGC_165_21,(0,2,2):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,3):C.UVGC_165_24})

V_58 = CTVertex(name = 'V_58',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.c, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,2):C.UVGC_165_21,(0,1,3):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,1):C.UVGC_165_24,(0,2,0):C.UVGC_165_20,(0,2,2):C.UVGC_165_21,(0,2,3):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,1):C.UVGC_165_24})

V_59 = CTVertex(name = 'V_59',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.t] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,1):C.UVGC_165_21,(0,1,2):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,3):C.UVGC_198_56,(0,2,0):C.UVGC_165_20,(0,2,1):C.UVGC_165_21,(0,2,2):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,3):C.UVGC_198_56})

V_60 = CTVertex(name = 'V_60',
                type = 'UV',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,1):C.UVGC_185_28})

V_61 = CTVertex(name = 'V_61',
                type = 'UV',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,1):C.UVGC_185_28})

V_62 = CTVertex(name = 'V_62',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,2):C.UVGC_200_58,(0,0,1):C.UVGC_185_28})

V_63 = CTVertex(name = 'V_63',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_201_59,(0,1,0):C.UVGC_202_60})

V_64 = CTVertex(name = 'V_64',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_164_19,(0,1,0):C.UVGC_147_4,(0,2,0):C.UVGC_147_4})

V_65 = CTVertex(name = 'V_65',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_164_19,(0,1,0):C.UVGC_147_4,(0,2,0):C.UVGC_147_4})

V_66 = CTVertex(name = 'V_66',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_164_19,(0,1,0):C.UVGC_147_4,(0,2,0):C.UVGC_147_4})

V_67 = CTVertex(name = 'V_67',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.d, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,2):C.UVGC_165_21,(0,1,3):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,1):C.UVGC_165_24,(0,2,0):C.UVGC_165_20,(0,2,2):C.UVGC_165_21,(0,2,3):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,1):C.UVGC_165_24})

V_68 = CTVertex(name = 'V_68',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.s] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,1):C.UVGC_165_21,(0,1,2):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,3):C.UVGC_165_24,(0,2,0):C.UVGC_165_20,(0,2,1):C.UVGC_165_21,(0,2,2):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,3):C.UVGC_165_24})

V_69 = CTVertex(name = 'V_69',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_166_25,(0,1,0):C.UVGC_165_20,(0,1,2):C.UVGC_165_21,(0,1,3):C.UVGC_165_22,(0,1,4):C.UVGC_165_23,(0,1,1):C.UVGC_165_24,(0,2,0):C.UVGC_165_20,(0,2,2):C.UVGC_165_21,(0,2,3):C.UVGC_165_22,(0,2,4):C.UVGC_165_23,(0,2,1):C.UVGC_165_24})

V_70 = CTVertex(name = 'V_70',
                type = 'UV',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,1):C.UVGC_185_28})

V_71 = CTVertex(name = 'V_71',
                type = 'UV',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,1):C.UVGC_185_28})

V_72 = CTVertex(name = 'V_72',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_185_27,(0,0,2):C.UVGC_200_58,(0,0,1):C.UVGC_185_28})

V_73 = CTVertex(name = 'V_73',
                type = 'UV',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_163_18,(0,1,0):C.UVGC_146_3,(0,2,0):C.UVGC_146_3})

V_74 = CTVertex(name = 'V_74',
                type = 'UV',
                particles = [ P.c__tilde__, P.c ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_163_18,(0,1,0):C.UVGC_146_3,(0,2,0):C.UVGC_146_3})

V_75 = CTVertex(name = 'V_75',
                type = 'UV',
                particles = [ P.t__tilde__, P.t ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_199_57,(0,2,0):C.UVGC_199_57,(0,1,0):C.UVGC_196_54,(0,3,0):C.UVGC_196_54})

V_76 = CTVertex(name = 'V_76',
                type = 'UV',
                particles = [ P.d__tilde__, P.d ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_163_18,(0,1,0):C.UVGC_146_3,(0,2,0):C.UVGC_146_3})

V_77 = CTVertex(name = 'V_77',
                type = 'UV',
                particles = [ P.s__tilde__, P.s ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_163_18,(0,1,0):C.UVGC_146_3,(0,2,0):C.UVGC_146_3})

V_78 = CTVertex(name = 'V_78',
                type = 'UV',
                particles = [ P.b__tilde__, P.b ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_163_18,(0,1,0):C.UVGC_146_3,(0,2,0):C.UVGC_146_3})

V_79 = CTVertex(name = 'V_79',
                type = 'UV',
                particles = [ P.g, P.g ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VV1, L.VV3 ],
                loop_particles = [ [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,0):C.UVGC_188_30,(0,0,1):C.UVGC_188_31,(0,0,2):C.UVGC_188_32,(0,1,2):C.UVGC_187_29})

