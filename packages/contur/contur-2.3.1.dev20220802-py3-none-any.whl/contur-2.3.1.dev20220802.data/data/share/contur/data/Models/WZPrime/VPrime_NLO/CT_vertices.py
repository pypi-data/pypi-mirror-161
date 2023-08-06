# This file was automatically created by FeynRules 2.3.10
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Thu 19 Jan 2017 16:30:59


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
               couplings = {(0,0,0):C.R2GC_157_29,(0,0,1):C.R2GC_157_30})

V_2 = CTVertex(name = 'V_2',
               type = 'R2',
               particles = [ P.g, P.g, P.g, P.g ],
               color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
               lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
               loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ] ],
               couplings = {(2,1,0):C.R2GC_122_10,(2,1,1):C.R2GC_122_11,(0,1,0):C.R2GC_122_10,(0,1,1):C.R2GC_122_11,(4,1,0):C.R2GC_120_6,(4,1,1):C.R2GC_120_7,(3,1,0):C.R2GC_120_6,(3,1,1):C.R2GC_120_7,(8,1,0):C.R2GC_121_8,(8,1,1):C.R2GC_121_9,(7,1,0):C.R2GC_126_17,(7,1,1):C.R2GC_161_35,(6,1,0):C.R2GC_125_15,(6,1,1):C.R2GC_162_36,(5,1,0):C.R2GC_120_6,(5,1,1):C.R2GC_120_7,(1,1,0):C.R2GC_120_6,(1,1,1):C.R2GC_120_7,(11,0,0):C.R2GC_124_13,(11,0,1):C.R2GC_124_14,(10,0,0):C.R2GC_124_13,(10,0,1):C.R2GC_124_14,(9,0,1):C.R2GC_123_12,(2,2,0):C.R2GC_122_10,(2,2,1):C.R2GC_122_11,(0,2,0):C.R2GC_122_10,(0,2,1):C.R2GC_122_11,(6,2,0):C.R2GC_158_31,(6,2,1):C.R2GC_158_32,(4,2,0):C.R2GC_120_6,(4,2,1):C.R2GC_120_7,(3,2,0):C.R2GC_120_6,(3,2,1):C.R2GC_120_7,(8,2,0):C.R2GC_121_8,(8,2,1):C.R2GC_163_37,(7,2,0):C.R2GC_126_17,(7,2,1):C.R2GC_126_18,(5,2,0):C.R2GC_120_6,(5,2,1):C.R2GC_120_7,(1,2,0):C.R2GC_120_6,(1,2,1):C.R2GC_120_7,(2,3,0):C.R2GC_122_10,(2,3,1):C.R2GC_122_11,(0,3,0):C.R2GC_122_10,(0,3,1):C.R2GC_122_11,(4,3,0):C.R2GC_120_6,(4,3,1):C.R2GC_120_7,(3,3,0):C.R2GC_120_6,(3,3,1):C.R2GC_120_7,(8,3,0):C.R2GC_121_8,(8,3,1):C.R2GC_160_34,(6,3,0):C.R2GC_125_15,(6,3,1):C.R2GC_125_16,(7,3,0):C.R2GC_159_33,(7,3,1):C.R2GC_122_11,(5,3,0):C.R2GC_120_6,(5,3,1):C.R2GC_120_7,(1,3,0):C.R2GC_120_6,(1,3,1):C.R2GC_120_7})

V_3 = CTVertex(name = 'V_3',
               type = 'R2',
               particles = [ P.t__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS5 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_175_42})

V_4 = CTVertex(name = 'V_4',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_177_44})

V_5 = CTVertex(name = 'V_5',
               type = 'R2',
               particles = [ P.t__tilde__, P.t, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS2 ],
               loop_particles = [ [ [P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_178_45})

V_6 = CTVertex(name = 'V_6',
               type = 'R2',
               particles = [ P.b__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_176_43})

V_7 = CTVertex(name = 'V_7',
               type = 'R2',
               particles = [ P.d__tilde__, P.u, P.Wp__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               loop_particles = [ [ [P.d, P.g, P.u] ] ],
               couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_8 = CTVertex(name = 'V_8',
               type = 'R2',
               particles = [ P.s__tilde__, P.c, P.Wp__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               loop_particles = [ [ [P.c, P.g, P.s] ] ],
               couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_9 = CTVertex(name = 'V_9',
               type = 'R2',
               particles = [ P.b__tilde__, P.t, P.Wp__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               loop_particles = [ [ [P.b, P.g, P.t] ] ],
               couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_10 = CTVertex(name = 'V_10',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_11 = CTVertex(name = 'V_11',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_12 = CTVertex(name = 'V_12',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_150_24,(0,1,0):C.R2GC_151_25})

V_13 = CTVertex(name = 'V_13',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_73_49,(0,1,0):C.R2GC_74_50})

V_14 = CTVertex(name = 'V_14',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_73_49,(0,1,0):C.R2GC_74_50})

V_15 = CTVertex(name = 'V_15',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_73_49,(0,1,0):C.R2GC_74_50})

V_16 = CTVertex(name = 'V_16',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_170_39,(0,1,0):C.R2GC_171_40})

V_17 = CTVertex(name = 'V_17',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_170_39,(0,1,0):C.R2GC_171_40})

V_18 = CTVertex(name = 'V_18',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_170_39,(0,1,0):C.R2GC_171_40})

V_19 = CTVertex(name = 'V_19',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_132_22})

V_20 = CTVertex(name = 'V_20',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_132_22})

V_21 = CTVertex(name = 'V_21',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_132_22})

V_22 = CTVertex(name = 'V_22',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_23 = CTVertex(name = 'V_23',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_24 = CTVertex(name = 'V_24',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_25 = CTVertex(name = 'V_25',
                type = 'R2',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_26 = CTVertex(name = 'V_26',
                type = 'R2',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_27 = CTVertex(name = 'V_27',
                type = 'R2',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_28 = CTVertex(name = 'V_28',
                type = 'R2',
                particles = [ P.u__tilde__, P.u, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_101_2,(0,1,0):C.R2GC_174_41})

V_29 = CTVertex(name = 'V_29',
                type = 'R2',
                particles = [ P.c__tilde__, P.c, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_101_2,(0,1,0):C.R2GC_174_41})

V_30 = CTVertex(name = 'V_30',
                type = 'R2',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_101_2,(0,1,0):C.R2GC_174_41})

V_31 = CTVertex(name = 'V_31',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_128_20})

V_32 = CTVertex(name = 'V_32',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_128_20})

V_33 = CTVertex(name = 'V_33',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_128_20})

V_34 = CTVertex(name = 'V_34',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_35 = CTVertex(name = 'V_35',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_36 = CTVertex(name = 'V_36',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_130_21})

V_37 = CTVertex(name = 'V_37',
                type = 'R2',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_38 = CTVertex(name = 'V_38',
                type = 'R2',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_39 = CTVertex(name = 'V_39',
                type = 'R2',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_149_23})

V_40 = CTVertex(name = 'V_40',
                type = 'R2',
                particles = [ P.d__tilde__, P.d, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_100_1,(0,1,0):C.R2GC_75_51})

V_41 = CTVertex(name = 'V_41',
                type = 'R2',
                particles = [ P.s__tilde__, P.s, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_100_1,(0,1,0):C.R2GC_75_51})

V_42 = CTVertex(name = 'V_42',
                type = 'R2',
                particles = [ P.b__tilde__, P.b, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_100_1,(0,1,0):C.R2GC_75_51})

V_43 = CTVertex(name = 'V_43',
                type = 'R2',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_127_19})

V_44 = CTVertex(name = 'V_44',
                type = 'R2',
                particles = [ P.c__tilde__, P.c ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_127_19})

V_45 = CTVertex(name = 'V_45',
                type = 'R2',
                particles = [ P.t__tilde__, P.t ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_167_38,(0,2,0):C.R2GC_167_38,(0,1,0):C.R2GC_127_19,(0,3,0):C.R2GC_127_19})

V_46 = CTVertex(name = 'V_46',
                type = 'R2',
                particles = [ P.d__tilde__, P.d ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_127_19})

V_47 = CTVertex(name = 'V_47',
                type = 'R2',
                particles = [ P.s__tilde__, P.s ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.R2GC_127_19})

V_48 = CTVertex(name = 'V_48',
                type = 'R2',
                particles = [ P.b__tilde__, P.b ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.R2GC_127_19})

V_49 = CTVertex(name = 'V_49',
                type = 'R2',
                particles = [ P.g, P.g ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VV1, L.VV2, L.VV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.g] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.R2GC_156_28,(0,1,2):C.R2GC_70_46,(0,2,0):C.R2GC_155_26,(0,2,1):C.R2GC_155_27})

V_50 = CTVertex(name = 'V_50',
                type = 'R2',
                particles = [ P.g, P.g, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_71_47})

V_51 = CTVertex(name = 'V_51',
                type = 'R2',
                particles = [ P.g, P.g, P.Zp, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_92_58,(0,0,1):C.R2GC_92_59,(0,1,0):C.R2GC_92_58,(0,1,1):C.R2GC_92_59,(0,2,0):C.R2GC_92_58,(0,2,1):C.R2GC_92_59})

V_52 = CTVertex(name = 'V_52',
                type = 'R2',
                particles = [ P.g, P.g, P.W__plus__, P.Wp__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t], [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_105_4,(0,1,0):C.R2GC_105_4,(0,2,0):C.R2GC_105_4})

V_53 = CTVertex(name = 'V_53',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_91_56,(0,0,1):C.R2GC_91_57,(0,1,0):C.R2GC_91_56,(0,1,1):C.R2GC_91_57,(0,2,0):C.R2GC_91_56,(0,2,1):C.R2GC_91_57})

V_54 = CTVertex(name = 'V_54',
                type = 'R2',
                particles = [ P.g, P.g, P.Wp__minus__, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t], [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_106_5,(0,1,0):C.R2GC_106_5,(0,2,0):C.R2GC_106_5})

V_55 = CTVertex(name = 'V_55',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Zp ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_93_60,(0,0,1):C.R2GC_93_61,(0,1,0):C.R2GC_93_60,(0,1,1):C.R2GC_93_61,(0,2,0):C.R2GC_93_60,(0,2,1):C.R2GC_93_61})

V_56 = CTVertex(name = 'V_56',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Zp ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_95_64,(1,0,1):C.R2GC_95_65,(0,1,0):C.R2GC_94_62,(0,1,1):C.R2GC_94_63,(0,2,0):C.R2GC_94_62,(0,2,1):C.R2GC_94_63,(0,3,0):C.R2GC_94_62,(0,3,1):C.R2GC_94_63})

V_57 = CTVertex(name = 'V_57',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t], [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_104_3,(0,1,0):C.R2GC_104_3,(0,2,0):C.R2GC_104_3})

V_58 = CTVertex(name = 'V_58',
                type = 'R2',
                particles = [ P.g, P.g, P.W__minus__, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b, P.t], [P.c, P.s], [P.d, P.u] ] ],
                couplings = {(0,0,0):C.R2GC_105_4,(0,1,0):C.R2GC_105_4,(0,2,0):C.R2GC_105_4})

V_59 = CTVertex(name = 'V_59',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.Z ],
                color = [ 'Identity(2,3)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_96_66,(0,0,1):C.R2GC_96_67,(0,1,0):C.R2GC_96_66,(0,1,1):C.R2GC_96_67,(0,2,0):C.R2GC_96_66,(0,2,1):C.R2GC_96_67})

V_60 = CTVertex(name = 'V_60',
                type = 'R2',
                particles = [ P.g, P.g, P.Z, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_99_72,(0,0,1):C.R2GC_99_73,(0,1,0):C.R2GC_99_72,(0,1,1):C.R2GC_99_73,(0,2,0):C.R2GC_99_72,(0,2,1):C.R2GC_99_73})

V_61 = CTVertex(name = 'V_61',
                type = 'R2',
                particles = [ P.a, P.a, P.g, P.g ],
                color = [ 'Identity(3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_89_52,(0,0,1):C.R2GC_89_53,(0,1,0):C.R2GC_89_52,(0,1,1):C.R2GC_89_53,(0,2,0):C.R2GC_89_52,(0,2,1):C.R2GC_89_53})

V_62 = CTVertex(name = 'V_62',
                type = 'R2',
                particles = [ P.g, P.g, P.g, P.Z ],
                color = [ 'd(1,2,3)', 'f(1,2,3)' ],
                lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(1,0,0):C.R2GC_98_70,(1,0,1):C.R2GC_98_71,(0,1,0):C.R2GC_97_68,(0,1,1):C.R2GC_97_69,(0,2,0):C.R2GC_97_68,(0,2,1):C.R2GC_97_69,(0,3,0):C.R2GC_97_68,(0,3,1):C.R2GC_97_69})

V_63 = CTVertex(name = 'V_63',
                type = 'R2',
                particles = [ P.a, P.g, P.g, P.g ],
                color = [ 'd(2,3,4)' ],
                lorentz = [ L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.d], [P.s] ], [ [P.c], [P.t], [P.u] ] ],
                couplings = {(0,0,0):C.R2GC_90_54,(0,0,1):C.R2GC_90_55,(0,1,0):C.R2GC_90_54,(0,1,1):C.R2GC_90_55,(0,2,0):C.R2GC_90_54,(0,2,1):C.R2GC_90_55})

V_64 = CTVertex(name = 'V_64',
                type = 'R2',
                particles = [ P.g, P.g, P.H, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_72_48})

V_65 = CTVertex(name = 'V_65',
                type = 'R2',
                particles = [ P.g, P.g, P.G0, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.t] ] ],
                couplings = {(0,0,0):C.R2GC_72_48})

V_66 = CTVertex(name = 'V_66',
                type = 'R2',
                particles = [ P.g, P.g, P.G__minus__, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.VVSS1 ],
                loop_particles = [ [ [P.b, P.t] ] ],
                couplings = {(0,0,0):C.R2GC_72_48})

V_67 = CTVertex(name = 'V_67',
                type = 'UV',
                particles = [ P.g, P.g, P.g ],
                color = [ 'f(1,2,3)' ],
                lorentz = [ L.VVV1, L.VVV2, L.VVV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,1,0):C.UVGC_157_37,(0,1,3):C.UVGC_157_38,(0,2,1):C.UVGC_108_1,(0,0,2):C.UVGC_109_2})

V_68 = CTVertex(name = 'V_68',
                type = 'UV',
                particles = [ P.g, P.g, P.g, P.g ],
                color = [ 'd(-1,1,3)*d(-1,2,4)', 'd(-1,1,3)*f(-1,2,4)', 'd(-1,1,4)*d(-1,2,3)', 'd(-1,1,4)*f(-1,2,3)', 'd(-1,2,3)*f(-1,1,4)', 'd(-1,2,4)*f(-1,1,3)', 'f(-1,1,2)*f(-1,3,4)', 'f(-1,1,3)*f(-1,2,4)', 'f(-1,1,4)*f(-1,2,3)', 'Identity(1,2)*Identity(3,4)', 'Identity(1,3)*Identity(2,4)', 'Identity(1,4)*Identity(2,3)' ],
                lorentz = [ L.VVVV10, L.VVVV2, L.VVVV3, L.VVVV5 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.t], [P.u] ], [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(2,1,2):C.UVGC_121_9,(2,1,3):C.UVGC_121_8,(0,1,2):C.UVGC_121_9,(0,1,3):C.UVGC_121_8,(4,1,2):C.UVGC_120_6,(4,1,3):C.UVGC_120_7,(3,1,2):C.UVGC_120_6,(3,1,3):C.UVGC_120_7,(8,1,2):C.UVGC_121_8,(8,1,3):C.UVGC_121_9,(7,1,1):C.UVGC_161_48,(7,1,2):C.UVGC_161_49,(7,1,3):C.UVGC_161_50,(7,1,4):C.UVGC_161_51,(6,1,1):C.UVGC_161_48,(6,1,2):C.UVGC_162_52,(6,1,3):C.UVGC_162_53,(6,1,4):C.UVGC_161_51,(5,1,2):C.UVGC_120_6,(5,1,3):C.UVGC_120_7,(1,1,2):C.UVGC_120_6,(1,1,3):C.UVGC_120_7,(11,0,2):C.UVGC_124_12,(11,0,3):C.UVGC_124_13,(10,0,2):C.UVGC_124_12,(10,0,3):C.UVGC_124_13,(9,0,2):C.UVGC_123_10,(9,0,3):C.UVGC_123_11,(2,2,2):C.UVGC_121_9,(2,2,3):C.UVGC_121_8,(0,2,2):C.UVGC_121_9,(0,2,3):C.UVGC_121_8,(6,2,2):C.UVGC_158_39,(6,2,3):C.UVGC_158_40,(6,2,4):C.UVGC_158_41,(4,2,2):C.UVGC_120_6,(4,2,3):C.UVGC_120_7,(3,2,2):C.UVGC_120_6,(3,2,3):C.UVGC_120_7,(8,2,1):C.UVGC_163_54,(8,2,2):C.UVGC_163_55,(8,2,3):C.UVGC_163_56,(8,2,4):C.UVGC_163_57,(7,2,0):C.UVGC_125_14,(7,2,2):C.UVGC_126_16,(7,2,3):C.UVGC_126_17,(5,2,2):C.UVGC_120_6,(5,2,3):C.UVGC_120_7,(1,2,2):C.UVGC_120_6,(1,2,3):C.UVGC_120_7,(2,3,2):C.UVGC_121_9,(2,3,3):C.UVGC_121_8,(0,3,2):C.UVGC_121_9,(0,3,3):C.UVGC_121_8,(4,3,2):C.UVGC_120_6,(4,3,3):C.UVGC_120_7,(3,3,2):C.UVGC_120_6,(3,3,3):C.UVGC_120_7,(8,3,1):C.UVGC_160_44,(8,3,2):C.UVGC_160_45,(8,3,3):C.UVGC_160_46,(8,3,4):C.UVGC_160_47,(6,3,0):C.UVGC_125_14,(6,3,2):C.UVGC_125_15,(6,3,3):C.UVGC_123_10,(7,3,2):C.UVGC_159_42,(7,3,3):C.UVGC_159_43,(7,3,4):C.UVGC_158_41,(5,3,2):C.UVGC_120_6,(5,3,3):C.UVGC_120_7,(1,3,2):C.UVGC_120_6,(1,3,3):C.UVGC_120_7})

V_69 = CTVertex(name = 'V_69',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.G__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS5 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_175_69,(0,0,2):C.UVGC_175_70,(0,0,1):C.UVGC_175_71})

V_70 = CTVertex(name = 'V_70',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.G0 ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS1 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_177_75})

V_71 = CTVertex(name = 'V_71',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.H ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS2 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_178_76})

V_72 = CTVertex(name = 'V_72',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.G__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFS3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_176_72,(0,0,2):C.UVGC_176_73,(0,0,1):C.UVGC_176_74})

V_73 = CTVertex(name = 'V_73',
                type = 'UV',
                particles = [ P.d__tilde__, P.u, P.Wp__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,1):C.UVGC_151_32})

V_74 = CTVertex(name = 'V_74',
                type = 'UV',
                particles = [ P.s__tilde__, P.c, P.Wp__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,1):C.UVGC_151_32})

V_75 = CTVertex(name = 'V_75',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.Wp__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,2):C.UVGC_169_63,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,2):C.UVGC_172_66,(0,1,1):C.UVGC_151_32})

V_76 = CTVertex(name = 'V_76',
                type = 'UV',
                particles = [ P.u__tilde__, P.d, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,1):C.UVGC_151_32})

V_77 = CTVertex(name = 'V_77',
                type = 'UV',
                particles = [ P.c__tilde__, P.s, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,1):C.UVGC_151_32})

V_78 = CTVertex(name = 'V_78',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.Wp__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_150_29,(0,0,2):C.UVGC_169_63,(0,0,1):C.UVGC_150_30,(0,1,0):C.UVGC_151_31,(0,1,2):C.UVGC_172_66,(0,1,1):C.UVGC_151_32})

V_79 = CTVertex(name = 'V_79',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.Zp ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_170_64,(0,1,0):C.UVGC_171_65})

V_80 = CTVertex(name = 'V_80',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_132_26,(0,1,0):C.UVGC_113_5,(0,2,0):C.UVGC_113_5})

V_81 = CTVertex(name = 'V_81',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.c, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_132_26,(0,1,0):C.UVGC_113_5,(0,2,0):C.UVGC_113_5})

V_82 = CTVertex(name = 'V_82',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_132_26,(0,1,0):C.UVGC_165_59,(0,2,0):C.UVGC_165_59})

V_83 = CTVertex(name = 'V_83',
                type = 'UV',
                particles = [ P.u__tilde__, P.u, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.u] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,1):C.UVGC_129_21,(0,1,2):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,3):C.UVGC_129_24,(0,2,0):C.UVGC_129_20,(0,2,1):C.UVGC_129_21,(0,2,2):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,3):C.UVGC_129_24})

V_84 = CTVertex(name = 'V_84',
                type = 'UV',
                particles = [ P.c__tilde__, P.c, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.c, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,2):C.UVGC_129_21,(0,1,3):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,1):C.UVGC_129_24,(0,2,0):C.UVGC_129_20,(0,2,2):C.UVGC_129_21,(0,2,3):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,1):C.UVGC_129_24})

V_85 = CTVertex(name = 'V_85',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.t] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,1):C.UVGC_129_21,(0,1,2):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,3):C.UVGC_166_60,(0,2,0):C.UVGC_129_20,(0,2,1):C.UVGC_129_21,(0,2,2):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,3):C.UVGC_166_60})

V_86 = CTVertex(name = 'V_86',
                type = 'UV',
                particles = [ P.d__tilde__, P.u, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,1):C.UVGC_149_28})

V_87 = CTVertex(name = 'V_87',
                type = 'UV',
                particles = [ P.s__tilde__, P.c, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,1):C.UVGC_149_28})

V_88 = CTVertex(name = 'V_88',
                type = 'UV',
                particles = [ P.b__tilde__, P.t, P.W__minus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,2):C.UVGC_168_62,(0,0,1):C.UVGC_149_28})

V_89 = CTVertex(name = 'V_89',
                type = 'UV',
                particles = [ P.t__tilde__, P.t, P.Z ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_173_67,(0,1,0):C.UVGC_174_68})

V_90 = CTVertex(name = 'V_90',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.d, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_128_19,(0,1,0):C.UVGC_111_4,(0,2,0):C.UVGC_111_4})

V_91 = CTVertex(name = 'V_91',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_128_19,(0,1,0):C.UVGC_111_4,(0,2,0):C.UVGC_111_4})

V_92 = CTVertex(name = 'V_92',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.a ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b, P.g] ] ],
                couplings = {(0,0,0):C.UVGC_128_19,(0,1,0):C.UVGC_111_4,(0,2,0):C.UVGC_111_4})

V_93 = CTVertex(name = 'V_93',
                type = 'UV',
                particles = [ P.d__tilde__, P.d, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.d, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,2):C.UVGC_129_21,(0,1,3):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,1):C.UVGC_129_24,(0,2,0):C.UVGC_129_20,(0,2,2):C.UVGC_129_21,(0,2,3):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,1):C.UVGC_129_24})

V_94 = CTVertex(name = 'V_94',
                type = 'UV',
                particles = [ P.s__tilde__, P.s, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.g] ], [ [P.ghG] ], [ [P.g, P.s] ], [ [P.t] ] ],
                couplings = {(0,0,3):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,1):C.UVGC_129_21,(0,1,2):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,3):C.UVGC_129_24,(0,2,0):C.UVGC_129_20,(0,2,1):C.UVGC_129_21,(0,2,2):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,3):C.UVGC_129_24})

V_95 = CTVertex(name = 'V_95',
                type = 'UV',
                particles = [ P.b__tilde__, P.b, P.g ],
                color = [ 'T(3,2,1)' ],
                lorentz = [ L.FFV1, L.FFV2, L.FFV3 ],
                loop_particles = [ [ [P.b], [P.c], [P.d], [P.s], [P.u] ], [ [P.b, P.g] ], [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                couplings = {(0,0,1):C.UVGC_130_25,(0,1,0):C.UVGC_129_20,(0,1,2):C.UVGC_129_21,(0,1,3):C.UVGC_129_22,(0,1,4):C.UVGC_129_23,(0,1,1):C.UVGC_129_24,(0,2,0):C.UVGC_129_20,(0,2,2):C.UVGC_129_21,(0,2,3):C.UVGC_129_22,(0,2,4):C.UVGC_129_23,(0,2,1):C.UVGC_129_24})

V_96 = CTVertex(name = 'V_96',
                type = 'UV',
                particles = [ P.u__tilde__, P.d, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.d, P.g], [P.g, P.u] ], [ [P.d, P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,1):C.UVGC_149_28})

V_97 = CTVertex(name = 'V_97',
                type = 'UV',
                particles = [ P.c__tilde__, P.s, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.c, P.g], [P.g, P.s] ], [ [P.c, P.g, P.s] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,1):C.UVGC_149_28})

V_98 = CTVertex(name = 'V_98',
                type = 'UV',
                particles = [ P.t__tilde__, P.b, P.W__plus__ ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FFV2 ],
                loop_particles = [ [ [P.b, P.g] ], [ [P.b, P.g, P.t] ], [ [P.g, P.t] ] ],
                couplings = {(0,0,0):C.UVGC_149_27,(0,0,2):C.UVGC_168_62,(0,0,1):C.UVGC_149_28})

V_99 = CTVertex(name = 'V_99',
                type = 'UV',
                particles = [ P.u__tilde__, P.u ],
                color = [ 'Identity(1,2)' ],
                lorentz = [ L.FF1, L.FF3, L.FF5 ],
                loop_particles = [ [ [P.g, P.u] ] ],
                couplings = {(0,0,0):C.UVGC_127_18,(0,1,0):C.UVGC_110_3,(0,2,0):C.UVGC_110_3})

V_100 = CTVertex(name = 'V_100',
                 type = 'UV',
                 particles = [ P.c__tilde__, P.c ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.c, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_127_18,(0,1,0):C.UVGC_110_3,(0,2,0):C.UVGC_110_3})

V_101 = CTVertex(name = 'V_101',
                 type = 'UV',
                 particles = [ P.t__tilde__, P.t ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF2, L.FF3, L.FF4, L.FF5 ],
                 loop_particles = [ [ [P.g, P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_167_61,(0,2,0):C.UVGC_167_61,(0,1,0):C.UVGC_164_58,(0,3,0):C.UVGC_164_58})

V_102 = CTVertex(name = 'V_102',
                 type = 'UV',
                 particles = [ P.d__tilde__, P.d ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.d, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_127_18,(0,1,0):C.UVGC_110_3,(0,2,0):C.UVGC_110_3})

V_103 = CTVertex(name = 'V_103',
                 type = 'UV',
                 particles = [ P.s__tilde__, P.s ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.g, P.s] ] ],
                 couplings = {(0,0,0):C.UVGC_127_18,(0,1,0):C.UVGC_110_3,(0,2,0):C.UVGC_110_3})

V_104 = CTVertex(name = 'V_104',
                 type = 'UV',
                 particles = [ P.b__tilde__, P.b ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.FF1, L.FF3, L.FF5 ],
                 loop_particles = [ [ [P.b, P.g] ] ],
                 couplings = {(0,0,0):C.UVGC_127_18,(0,1,0):C.UVGC_110_3,(0,2,0):C.UVGC_110_3})

V_105 = CTVertex(name = 'V_105',
                 type = 'UV',
                 particles = [ P.g, P.g ],
                 color = [ 'Identity(1,2)' ],
                 lorentz = [ L.VV1, L.VV3 ],
                 loop_particles = [ [ [P.g] ], [ [P.ghG] ], [ [P.t] ] ],
                 couplings = {(0,0,0):C.UVGC_156_34,(0,0,1):C.UVGC_156_35,(0,0,2):C.UVGC_156_36,(0,1,2):C.UVGC_155_33})

