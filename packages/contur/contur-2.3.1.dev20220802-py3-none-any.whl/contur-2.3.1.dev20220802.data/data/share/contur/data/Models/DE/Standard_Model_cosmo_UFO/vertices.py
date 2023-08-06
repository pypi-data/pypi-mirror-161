# This file was automatically created by FeynRules 2.0.33
# Mathematica version: 7.0 for Mac OS X x86 (64-bit) (February 19, 2009)
# Date: Tue 19 Jan 2016 17:07:07


from .object_library import all_vertices, Vertex
from . import particles as P
from . import couplings as C
from . import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.G0, P.G0, P.G0, P.G0 ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_172})

V_2 = Vertex(name = 'V_2',
             particles = [ P.G0, P.G0, P.G__minus__, P.G__plus__ ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_170})

V_3 = Vertex(name = 'V_3',
             particles = [ P.G__minus__, P.G__minus__, P.G__plus__, P.G__plus__ ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_171})

V_4 = Vertex(name = 'V_4',
             particles = [ P.G0, P.G0, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_170})

V_5 = Vertex(name = 'V_5',
             particles = [ P.G__minus__, P.G__plus__, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_170})

V_6 = Vertex(name = 'V_6',
             particles = [ P.H, P.H, P.H, P.H ],
             color = [ '1' ],
             lorentz = [ L.SSSS1 ],
             couplings = {(0,0):C.GC_172})

V_7 = Vertex(name = 'V_7',
             particles = [ P.G0, P.G0, P.G0, P.G0, P.phinew ],
             color = [ '1' ],
             lorentz = [ L.SSSSS1 ],
             couplings = {(0,0):C.GC_175})

V_8 = Vertex(name = 'V_8',
             particles = [ P.G0, P.G0, P.G__minus__, P.G__plus__, P.phinew ],
             color = [ '1' ],
             lorentz = [ L.SSSSS1 ],
             couplings = {(0,0):C.GC_173})

V_9 = Vertex(name = 'V_9',
             particles = [ P.G__minus__, P.G__minus__, P.G__plus__, P.G__plus__, P.phinew ],
             color = [ '1' ],
             lorentz = [ L.SSSSS1 ],
             couplings = {(0,0):C.GC_174})

V_10 = Vertex(name = 'V_10',
              particles = [ P.G0, P.G0, P.H, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1 ],
              couplings = {(0,0):C.GC_173})

V_11 = Vertex(name = 'V_11',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1 ],
              couplings = {(0,0):C.GC_173})

V_12 = Vertex(name = 'V_12',
              particles = [ P.H, P.H, P.H, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1 ],
              couplings = {(0,0):C.GC_175})

V_13 = Vertex(name = 'V_13',
              particles = [ P.G0, P.G0, P.G0, P.G0, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_178,(0,1):C.GC_187})

V_14 = Vertex(name = 'V_14',
              particles = [ P.G0, P.G0, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_176,(0,1):C.GC_185})

V_15 = Vertex(name = 'V_15',
              particles = [ P.G__minus__, P.G__minus__, P.G__plus__, P.G__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_177,(0,1):C.GC_186})

V_16 = Vertex(name = 'V_16',
              particles = [ P.G0, P.G0, P.H, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_176,(0,1):C.GC_185})

V_17 = Vertex(name = 'V_17',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_176,(0,1):C.GC_185})

V_18 = Vertex(name = 'V_18',
              particles = [ P.H, P.H, P.H, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS3 ],
              couplings = {(0,0):C.GC_178,(0,1):C.GC_187})

V_19 = Vertex(name = 'V_19',
              particles = [ P.G0, P.G0, P.G0, P.G0, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_181})

V_20 = Vertex(name = 'V_20',
              particles = [ P.G0, P.G0, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_179})

V_21 = Vertex(name = 'V_21',
              particles = [ P.G__minus__, P.G__minus__, P.G__plus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_180})

V_22 = Vertex(name = 'V_22',
              particles = [ P.G0, P.G0, P.H, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_179})

V_23 = Vertex(name = 'V_23',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_179})

V_24 = Vertex(name = 'V_24',
              particles = [ P.H, P.H, P.H, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_181})

V_25 = Vertex(name = 'V_25',
              particles = [ P.G0, P.G0, P.G0, P.G0, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS2 ],
              couplings = {(0,0):C.GC_184,(0,1):C.GC_190})

V_26 = Vertex(name = 'V_26',
              particles = [ P.G0, P.G0, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS3 ],
              couplings = {(0,0):C.GC_182,(0,1):C.GC_188})

V_27 = Vertex(name = 'V_27',
              particles = [ P.G__minus__, P.G__minus__, P.G__plus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS3 ],
              couplings = {(0,0):C.GC_183,(0,1):C.GC_189})

V_28 = Vertex(name = 'V_28',
              particles = [ P.G0, P.G0, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS3 ],
              couplings = {(0,0):C.GC_182,(0,1):C.GC_188})

V_29 = Vertex(name = 'V_29',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS3 ],
              couplings = {(0,0):C.GC_182,(0,1):C.GC_188})

V_30 = Vertex(name = 'V_30',
              particles = [ P.H, P.H, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1, L.SSSSSSSS3 ],
              couplings = {(0,0):C.GC_184,(0,1):C.GC_190})

V_31 = Vertex(name = 'V_31',
              particles = [ P.phinew, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1, L.SSSSS4 ],
              couplings = {(0,0):C.GC_123,(0,1):C.GC_119})

V_32 = Vertex(name = 'V_32',
              particles = [ P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS5 ],
              couplings = {(0,0):C.GC_135,(0,1):C.GC_93})

V_33 = Vertex(name = 'V_33',
              particles = [ P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1 ],
              couplings = {(0,0):C.GC_148})

V_34 = Vertex(name = 'V_34',
              particles = [ P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSSS1 ],
              couplings = {(0,0):C.GC_160})

V_35 = Vertex(name = 'V_35',
              particles = [ P.G0, P.G0, P.H ],
              color = [ '1' ],
              lorentz = [ L.SSS1 ],
              couplings = {(0,0):C.GC_492})

V_36 = Vertex(name = 'V_36',
              particles = [ P.G__minus__, P.G__plus__, P.H ],
              color = [ '1' ],
              lorentz = [ L.SSS1 ],
              couplings = {(0,0):C.GC_492})

V_37 = Vertex(name = 'V_37',
              particles = [ P.H, P.H, P.H ],
              color = [ '1' ],
              lorentz = [ L.SSS1 ],
              couplings = {(0,0):C.GC_493})

V_38 = Vertex(name = 'V_38',
              particles = [ P.G0, P.G0, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS1 ],
              couplings = {(0,0):C.GC_494})

V_39 = Vertex(name = 'V_39',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS1 ],
              couplings = {(0,0):C.GC_494})

V_40 = Vertex(name = 'V_40',
              particles = [ P.H, P.H, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS1 ],
              couplings = {(0,0):C.GC_495})

V_41 = Vertex(name = 'V_41',
              particles = [ P.G0, P.G0, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1, L.SSSSS3 ],
              couplings = {(0,0):C.GC_496,(0,1):C.GC_546})

V_42 = Vertex(name = 'V_42',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1, L.SSSSS3 ],
              couplings = {(0,0):C.GC_496,(0,1):C.GC_546})

V_43 = Vertex(name = 'V_43',
              particles = [ P.H, P.H, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1, L.SSSSS3 ],
              couplings = {(0,0):C.GC_497,(0,1):C.GC_547})

V_44 = Vertex(name = 'V_44',
              particles = [ P.G0, P.G0, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1 ],
              couplings = {(0,0):C.GC_498})

V_45 = Vertex(name = 'V_45',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1 ],
              couplings = {(0,0):C.GC_498})

V_46 = Vertex(name = 'V_46',
              particles = [ P.H, P.H, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1 ],
              couplings = {(0,0):C.GC_499})

V_47 = Vertex(name = 'V_47',
              particles = [ P.G0, P.G0, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1, L.SSSSSSS2 ],
              couplings = {(0,0):C.GC_500,(0,1):C.GC_548})

V_48 = Vertex(name = 'V_48',
              particles = [ P.G__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1, L.SSSSSSS2 ],
              couplings = {(0,0):C.GC_500,(0,1):C.GC_548})

V_49 = Vertex(name = 'V_49',
              particles = [ P.H, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSSS1, L.SSSSSSS2 ],
              couplings = {(0,0):C.GC_501,(0,1):C.GC_549})

V_50 = Vertex(name = 'V_50',
              particles = [ P.H, P.H, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSS1, L.SSS2 ],
              couplings = {(0,0):C.GC_540,(0,1):C.GC_120})

V_51 = Vertex(name = 'V_51',
              particles = [ P.H, P.H, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS1, L.SSSS2, L.SSSS3, L.SSSS5, L.SSSS6 ],
              couplings = {(0,0):C.GC_541,(0,1):C.GC_132,(0,4):C.GC_61,(0,2):C.GC_572,(0,3):C.GC_56})

V_52 = Vertex(name = 'V_52',
              particles = [ P.H, P.H, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS1, L.SSSSS2 ],
              couplings = {(0,0):C.GC_542,(0,1):C.GC_145})

V_53 = Vertex(name = 'V_53',
              particles = [ P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS1, L.SSSSSS2, L.SSSSSS4, L.SSSSSS6, L.SSSSSS7 ],
              couplings = {(0,0):C.GC_543,(0,1):C.GC_157,(0,3):C.GC_88,(0,2):C.GC_573,(0,4):C.GC_84})

V_54 = Vertex(name = 'V_54',
              particles = [ P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSS1, L.SSS3, L.SSS4, L.SSS5 ],
              couplings = {(0,0):C.GC_544,(0,1):C.GC_52,(0,3):C.GC_54,(0,2):C.GC_55})

V_55 = Vertex(name = 'V_55',
              particles = [ P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS1, L.SSSS10, L.SSSS4, L.SSSS5, L.SSSS7, L.SSSS8, L.SSSS9 ],
              couplings = {(0,0):C.GC_545,(0,2):C.GC_53,(0,5):C.GC_59,(0,4):C.GC_590,(0,1):C.GC_83,(0,6):C.GC_119,(0,3):C.GC_63})

V_56 = Vertex(name = 'V_56',
              particles = [ P.a, P.a, P.G__minus__, P.G__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VVSS3 ],
              couplings = {(0,0):C.GC_7})

V_57 = Vertex(name = 'V_57',
              particles = [ P.a, P.a, P.G__minus__, P.G__plus__, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSS2 ],
              couplings = {(0,0):C.GC_127})

V_58 = Vertex(name = 'V_58',
              particles = [ P.a, P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
              couplings = {(0,2):C.GC_72,(0,0):C.GC_140,(0,1):C.GC_71})

V_59 = Vertex(name = 'V_59',
              particles = [ P.a, P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSSS1 ],
              couplings = {(0,0):C.GC_152})

V_60 = Vertex(name = 'V_60',
              particles = [ P.a, P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
              couplings = {(0,0):C.GC_165,(0,1):C.GC_105,(0,2):C.GC_104})

V_61 = Vertex(name = 'V_61',
              particles = [ P.G0, P.G0, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSS2 ],
              couplings = {(0,0):C.GC_120})

V_62 = Vertex(name = 'V_62',
              particles = [ P.G0, P.G0, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS2, L.SSSS5, L.SSSS6 ],
              couplings = {(0,0):C.GC_132,(0,2):C.GC_61,(0,1):C.GC_56})

V_63 = Vertex(name = 'V_63',
              particles = [ P.G0, P.G0, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS2 ],
              couplings = {(0,0):C.GC_145})

V_64 = Vertex(name = 'V_64',
              particles = [ P.G0, P.G0, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS2, L.SSSSSS6, L.SSSSSS7 ],
              couplings = {(0,0):C.GC_157,(0,1):C.GC_88,(0,2):C.GC_84})

V_65 = Vertex(name = 'V_65',
              particles = [ P.a, P.G__minus__, P.G__plus__ ],
              color = [ '1' ],
              lorentz = [ L.VSS2 ],
              couplings = {(0,0):C.GC_4})

V_66 = Vertex(name = 'V_66',
              particles = [ P.a, P.G__minus__, P.G__plus__, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VSSS2 ],
              couplings = {(0,0):C.GC_124})

V_67 = Vertex(name = 'V_67',
              particles = [ P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
              couplings = {(0,0):C.GC_138,(0,2):C.GC_70,(0,1):C.GC_65})

V_68 = Vertex(name = 'V_68',
              particles = [ P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VSSSSS2 ],
              couplings = {(0,0):C.GC_149})

V_69 = Vertex(name = 'V_69',
              particles = [ P.a, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
              couplings = {(0,0):C.GC_163,(0,2):C.GC_100,(0,1):C.GC_96})

V_70 = Vertex(name = 'V_70',
              particles = [ P.G__minus__, P.G__plus__, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSS2 ],
              couplings = {(0,0):C.GC_120})

V_71 = Vertex(name = 'V_71',
              particles = [ P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSS2, L.SSSS5, L.SSSS6 ],
              couplings = {(0,0):C.GC_132,(0,2):C.GC_61,(0,1):C.GC_56})

V_72 = Vertex(name = 'V_72',
              particles = [ P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSS2 ],
              couplings = {(0,0):C.GC_145})

V_73 = Vertex(name = 'V_73',
              particles = [ P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.SSSSSS2, L.SSSSSS6, L.SSSSSS7 ],
              couplings = {(0,0):C.GC_157,(0,1):C.GC_88,(0,2):C.GC_84})

V_74 = Vertex(name = 'V_74',
              particles = [ P.a, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSS1, L.VVSSSS12, L.VVSSSS15, L.VVSSSS2 ],
              couplings = {(0,0):C.GC_159,(0,2):C.GC_92,(0,1):C.GC_89,(0,3):C.GC_86})

V_75 = Vertex(name = 'V_75',
              particles = [ P.a, P.a, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_122})

V_76 = Vertex(name = 'V_76',
              particles = [ P.a, P.a, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSS1, L.VVSS2, L.VVSS7 ],
              couplings = {(0,0):C.GC_134,(0,2):C.GC_62,(0,1):C.GC_58})

V_77 = Vertex(name = 'V_77',
              particles = [ P.a, P.a, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSS1 ],
              couplings = {(0,0):C.GC_147})

V_78 = Vertex(name = 'V_78',
              particles = [ P.g, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVSSSS1, L.VVSSSS13, L.VVSSSS15, L.VVSSSS2 ],
              couplings = {(0,0):C.GC_159,(0,2):C.GC_92,(0,1):C.GC_89,(0,3):C.GC_86})

V_79 = Vertex(name = 'V_79',
              particles = [ P.g, P.g, P.phinew ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVS1 ],
              couplings = {(0,0):C.GC_122})

V_80 = Vertex(name = 'V_80',
              particles = [ P.g, P.g, P.phinew, P.phinew ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVSS1, L.VVSS2, L.VVSS7 ],
              couplings = {(0,0):C.GC_134,(0,2):C.GC_62,(0,1):C.GC_58})

V_81 = Vertex(name = 'V_81',
              particles = [ P.g, P.g, P.phinew, P.phinew, P.phinew ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVSSS1 ],
              couplings = {(0,0):C.GC_147})

V_82 = Vertex(name = 'V_82',
              particles = [ P.g, P.g, P.H ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.VVS3 ],
              couplings = {(0,0):C.GC_1})

V_83 = Vertex(name = 'V_83',
              particles = [ P.W__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSS11, L.VVSSSS14, L.VVSSSS3, L.VVSSSS7, L.VVSSSS8, L.VVSSSS9 ],
              couplings = {(0,2):C.GC_581,(0,3):C.GC_577,(0,5):C.GC_209,(0,0):C.GC_89,(0,1):C.GC_91,(0,4):C.GC_576})

V_84 = Vertex(name = 'V_84',
              particles = [ P.W__minus__, P.W__plus__, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVS2 ],
              couplings = {(0,0):C.GC_578})

V_85 = Vertex(name = 'V_85',
              particles = [ P.W__minus__, P.W__plus__, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSS3, L.VVSS4, L.VVSS5, L.VVSS6 ],
              couplings = {(0,2):C.GC_575,(0,0):C.GC_579,(0,3):C.GC_62,(0,1):C.GC_574})

V_86 = Vertex(name = 'V_86',
              particles = [ P.W__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSS2 ],
              couplings = {(0,0):C.GC_580})

V_87 = Vertex(name = 'V_87',
              particles = [ P.Z, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSSS10, L.VVSSSS11, L.VVSSSS3, L.VVSSSS6, L.VVSSSS7, L.VVSSSS8 ],
              couplings = {(0,2):C.GC_589,(0,4):C.GC_585,(0,3):C.GC_210,(0,1):C.GC_89,(0,0):C.GC_91,(0,5):C.GC_584})

V_88 = Vertex(name = 'V_88',
              particles = [ P.Z, P.Z, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVS2 ],
              couplings = {(0,0):C.GC_586})

V_89 = Vertex(name = 'V_89',
              particles = [ P.Z, P.Z, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSS3, L.VVSS4, L.VVSS5, L.VVSS6 ],
              couplings = {(0,2):C.GC_583,(0,0):C.GC_587,(0,3):C.GC_62,(0,1):C.GC_582})

V_90 = Vertex(name = 'V_90',
              particles = [ P.Z, P.Z, P.phinew, P.phinew, P.phinew ],
              color = [ '1' ],
              lorentz = [ L.VVSSS2 ],
              couplings = {(0,0):C.GC_588})

V_91 = Vertex(name = 'V_91',
              particles = [ P.ghA, P.ghWm__tilde__, P.W__minus__ ],
              color = [ '1' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_4})

V_92 = Vertex(name = 'V_92',
              particles = [ P.ghA, P.ghWp__tilde__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_5})

V_93 = Vertex(name = 'V_93',
              particles = [ P.ghWm, P.ghA__tilde__, P.G__plus__ ],
              color = [ '1' ],
              lorentz = [ L.UUS1 ],
              couplings = {(0,0):C.GC_515})

V_94 = Vertex(name = 'V_94',
              particles = [ P.ghWm, P.ghA__tilde__, P.W__plus__ ],
              color = [ '1' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_4})

V_95 = Vertex(name = 'V_95',
              particles = [ P.ghWm, P.ghWm__tilde__, P.G0 ],
              color = [ '1' ],
              lorentz = [ L.UUS1 ],
              couplings = {(0,0):C.GC_502})

V_96 = Vertex(name = 'V_96',
              particles = [ P.ghWm, P.ghWm__tilde__, P.H ],
              color = [ '1' ],
              lorentz = [ L.UUS1 ],
              couplings = {(0,0):C.GC_503})

V_97 = Vertex(name = 'V_97',
              particles = [ P.ghWm, P.ghWm__tilde__, P.a ],
              color = [ '1' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_5})

V_98 = Vertex(name = 'V_98',
              particles = [ P.ghWm, P.ghWm__tilde__, P.Z ],
              color = [ '1' ],
              lorentz = [ L.UUV1 ],
              couplings = {(0,0):C.GC_238})

V_99 = Vertex(name = 'V_99',
              particles = [ P.ghWm, P.ghZ__tilde__, P.G__plus__ ],
              color = [ '1' ],
              lorentz = [ L.UUS1 ],
              couplings = {(0,0):C.GC_552})

V_100 = Vertex(name = 'V_100',
               particles = [ P.ghWm, P.ghZ__tilde__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_237})

V_101 = Vertex(name = 'V_101',
               particles = [ P.ghWp, P.ghA__tilde__, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_514})

V_102 = Vertex(name = 'V_102',
               particles = [ P.ghWp, P.ghA__tilde__, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_5})

V_103 = Vertex(name = 'V_103',
               particles = [ P.ghWp, P.ghWp__tilde__, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_505})

V_104 = Vertex(name = 'V_104',
               particles = [ P.ghWp, P.ghWp__tilde__, P.H ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_503})

V_105 = Vertex(name = 'V_105',
               particles = [ P.ghWp, P.ghWp__tilde__, P.a ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_4})

V_106 = Vertex(name = 'V_106',
               particles = [ P.ghWp, P.ghWp__tilde__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_237})

V_107 = Vertex(name = 'V_107',
               particles = [ P.ghWp, P.ghZ__tilde__, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_551})

V_108 = Vertex(name = 'V_108',
               particles = [ P.ghWp, P.ghZ__tilde__, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_238})

V_109 = Vertex(name = 'V_109',
               particles = [ P.ghZ, P.ghWm__tilde__, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_553})

V_110 = Vertex(name = 'V_110',
               particles = [ P.ghZ, P.ghWm__tilde__, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_237})

V_111 = Vertex(name = 'V_111',
               particles = [ P.ghZ, P.ghWp__tilde__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_550})

V_112 = Vertex(name = 'V_112',
               particles = [ P.ghZ, P.ghWp__tilde__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_238})

V_113 = Vertex(name = 'V_113',
               particles = [ P.ghZ, P.ghZ__tilde__, P.H ],
               color = [ '1' ],
               lorentz = [ L.UUS1 ],
               couplings = {(0,0):C.GC_562})

V_114 = Vertex(name = 'V_114',
               particles = [ P.b__tilde__, P.b, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4, L.FFSSSS5, L.FFSSSS6 ],
               couplings = {(0,4):C.GC_194,(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,5):C.GC_196,(0,2):C.GC_85})

V_115 = Vertex(name = 'V_115',
               particles = [ P.b__tilde__, P.b, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3, L.FFSS4, L.FFSS5 ],
               couplings = {(0,3):C.GC_192,(0,0):C.GC_133,(0,2):C.GC_60,(0,4):C.GC_195,(0,1):C.GC_57})

V_116 = Vertex(name = 'V_116',
               particles = [ P.b__tilde__, P.b, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1, L.FFSSS2 ],
               couplings = {(0,1):C.GC_193,(0,0):C.GC_146})

V_117 = Vertex(name = 'V_117',
               particles = [ P.b__tilde__, P.b, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1, L.FFS2 ],
               couplings = {(0,1):C.GC_191,(0,0):C.GC_121})

V_118 = Vertex(name = 'V_118',
               particles = [ P.ta__plus__, P.ta__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1, L.FFSSS2 ],
               couplings = {(0,1):C.GC_205,(0,0):C.GC_146})

V_119 = Vertex(name = 'V_119',
               particles = [ P.ta__plus__, P.ta__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1, L.FFS2 ],
               couplings = {(0,1):C.GC_203,(0,0):C.GC_121})

V_120 = Vertex(name = 'V_120',
               particles = [ P.ta__plus__, P.ta__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4, L.FFSSSS5, L.FFSSSS6 ],
               couplings = {(0,4):C.GC_206,(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,5):C.GC_208,(0,2):C.GC_85})

V_121 = Vertex(name = 'V_121',
               particles = [ P.ta__plus__, P.ta__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3, L.FFSS4, L.FFSS5 ],
               couplings = {(0,3):C.GC_204,(0,0):C.GC_133,(0,2):C.GC_60,(0,4):C.GC_207,(0,1):C.GC_57})

V_122 = Vertex(name = 'V_122',
               particles = [ P.t__tilde__, P.t, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3, L.FFSS4, L.FFSS5 ],
               couplings = {(0,3):C.GC_198,(0,0):C.GC_133,(0,2):C.GC_60,(0,4):C.GC_201,(0,1):C.GC_57})

V_123 = Vertex(name = 'V_123',
               particles = [ P.t__tilde__, P.t, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4, L.FFSSSS5, L.FFSSSS6 ],
               couplings = {(0,4):C.GC_200,(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,5):C.GC_202,(0,2):C.GC_85})

V_124 = Vertex(name = 'V_124',
               particles = [ P.t__tilde__, P.t, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1, L.FFS2 ],
               couplings = {(0,1):C.GC_197,(0,0):C.GC_121})

V_125 = Vertex(name = 'V_125',
               particles = [ P.t__tilde__, P.t, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1, L.FFSSS2 ],
               couplings = {(0,1):C.GC_199,(0,0):C.GC_146})

V_126 = Vertex(name = 'V_126',
               particles = [ P.ghG, P.ghG__tilde__, P.g ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.UUV1 ],
               couplings = {(0,0):C.GC_11})

V_127 = Vertex(name = 'V_127',
               particles = [ P.g, P.g, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVVSSSS1, L.VVVSSSS2 ],
               couplings = {(0,0):C.GC_113,(0,1):C.GC_115})

V_128 = Vertex(name = 'V_128',
               particles = [ P.g, P.g, P.g ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVV1 ],
               couplings = {(0,0):C.GC_11})

V_129 = Vertex(name = 'V_129',
               particles = [ P.g, P.g, P.g, P.g ],
               color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
               lorentz = [ L.VVVV1, L.VVVV3, L.VVVV4 ],
               couplings = {(1,1):C.GC_14,(0,0):C.GC_14,(2,2):C.GC_14})

V_130 = Vertex(name = 'V_130',
               particles = [ P.g, P.g, P.g, P.H ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVVS1 ],
               couplings = {(0,0):C.GC_13})

V_131 = Vertex(name = 'V_131',
               particles = [ P.g, P.g, P.g, P.g, P.H ],
               color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
               lorentz = [ L.VVVVS1, L.VVVVS2, L.VVVVS3 ],
               couplings = {(1,1):C.GC_15,(0,0):C.GC_15,(2,2):C.GC_15})

V_132 = Vertex(name = 'V_132',
               particles = [ P.g, P.g, P.g, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
               lorentz = [ L.VVVVSSSS1, L.VVVVSSSS2, L.VVVVSSSS3, L.VVVVSSSS4, L.VVVVSSSS5, L.VVVVSSSS6 ],
               couplings = {(2,5):C.GC_117,(2,3):C.GC_118,(1,4):C.GC_117,(1,2):C.GC_118,(0,1):C.GC_117,(0,0):C.GC_118})

V_133 = Vertex(name = 'V_133',
               particles = [ P.g, P.g, P.g, P.phinew, P.phinew ],
               color = [ 'f(1,2,3)' ],
               lorentz = [ L.VVVSS1 ],
               couplings = {(0,0):C.GC_81})

V_134 = Vertex(name = 'V_134',
               particles = [ P.g, P.g, P.g, P.g, P.phinew, P.phinew ],
               color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
               lorentz = [ L.VVVVSS1, L.VVVVSS2, L.VVVVSS3 ],
               couplings = {(2,2):C.GC_82,(1,1):C.GC_82,(0,0):C.GC_82})

V_135 = Vertex(name = 'V_135',
               particles = [ P.d__tilde__, P.d, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_136 = Vertex(name = 'V_136',
               particles = [ P.s__tilde__, P.s, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_137 = Vertex(name = 'V_137',
               particles = [ P.e__plus__, P.e__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_138 = Vertex(name = 'V_138',
               particles = [ P.mu__plus__, P.mu__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_139 = Vertex(name = 'V_139',
               particles = [ P.u__tilde__, P.u, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_140 = Vertex(name = 'V_140',
               particles = [ P.c__tilde__, P.c, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_141 = Vertex(name = 'V_141',
               particles = [ P.ve__tilde__, P.ve, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_142 = Vertex(name = 'V_142',
               particles = [ P.vm__tilde__, P.vm, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_143 = Vertex(name = 'V_143',
               particles = [ P.vt__tilde__, P.vt, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSSS1, L.FFSSSS2, L.FFSSSS3, L.FFSSSS4 ],
               couplings = {(0,0):C.GC_158,(0,3):C.GC_87,(0,1):C.GC_90,(0,2):C.GC_85})

V_144 = Vertex(name = 'V_144',
               particles = [ P.d__tilde__, P.d, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_145 = Vertex(name = 'V_145',
               particles = [ P.s__tilde__, P.s, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_146 = Vertex(name = 'V_146',
               particles = [ P.d__tilde__, P.d, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_147 = Vertex(name = 'V_147',
               particles = [ P.s__tilde__, P.s, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_148 = Vertex(name = 'V_148',
               particles = [ P.d__tilde__, P.d, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_149 = Vertex(name = 'V_149',
               particles = [ P.s__tilde__, P.s, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_150 = Vertex(name = 'V_150',
               particles = [ P.e__plus__, P.e__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_151 = Vertex(name = 'V_151',
               particles = [ P.mu__plus__, P.mu__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_152 = Vertex(name = 'V_152',
               particles = [ P.e__plus__, P.e__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_153 = Vertex(name = 'V_153',
               particles = [ P.mu__plus__, P.mu__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_154 = Vertex(name = 'V_154',
               particles = [ P.e__plus__, P.e__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_155 = Vertex(name = 'V_155',
               particles = [ P.mu__plus__, P.mu__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_156 = Vertex(name = 'V_156',
               particles = [ P.u__tilde__, P.u, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_157 = Vertex(name = 'V_157',
               particles = [ P.c__tilde__, P.c, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_158 = Vertex(name = 'V_158',
               particles = [ P.u__tilde__, P.u, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_159 = Vertex(name = 'V_159',
               particles = [ P.c__tilde__, P.c, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_160 = Vertex(name = 'V_160',
               particles = [ P.u__tilde__, P.u, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_161 = Vertex(name = 'V_161',
               particles = [ P.c__tilde__, P.c, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_162 = Vertex(name = 'V_162',
               particles = [ P.ve__tilde__, P.ve, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_163 = Vertex(name = 'V_163',
               particles = [ P.vm__tilde__, P.vm, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_164 = Vertex(name = 'V_164',
               particles = [ P.vt__tilde__, P.vt, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSSS1 ],
               couplings = {(0,0):C.GC_146})

V_165 = Vertex(name = 'V_165',
               particles = [ P.ve__tilde__, P.ve, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_166 = Vertex(name = 'V_166',
               particles = [ P.vm__tilde__, P.vm, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_167 = Vertex(name = 'V_167',
               particles = [ P.vt__tilde__, P.vt, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFS1 ],
               couplings = {(0,0):C.GC_121})

V_168 = Vertex(name = 'V_168',
               particles = [ P.ve__tilde__, P.ve, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_169 = Vertex(name = 'V_169',
               particles = [ P.vm__tilde__, P.vm, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_170 = Vertex(name = 'V_170',
               particles = [ P.vt__tilde__, P.vt, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFSS1, L.FFSS2, L.FFSS3 ],
               couplings = {(0,0):C.GC_133,(0,2):C.GC_60,(0,1):C.GC_57})

V_171 = Vertex(name = 'V_171',
               particles = [ P.u__tilde__, P.d, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_16,(0,1):C.GC_25})

V_172 = Vertex(name = 'V_172',
               particles = [ P.c__tilde__, P.d, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_17,(0,1):C.GC_26})

V_173 = Vertex(name = 'V_173',
               particles = [ P.t__tilde__, P.d, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_18,(0,1):C.GC_27})

V_174 = Vertex(name = 'V_174',
               particles = [ P.u__tilde__, P.s, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_19,(0,1):C.GC_28})

V_175 = Vertex(name = 'V_175',
               particles = [ P.c__tilde__, P.s, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_20,(0,1):C.GC_29})

V_176 = Vertex(name = 'V_176',
               particles = [ P.t__tilde__, P.s, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_21,(0,1):C.GC_30})

V_177 = Vertex(name = 'V_177',
               particles = [ P.u__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_22,(0,1):C.GC_31})

V_178 = Vertex(name = 'V_178',
               particles = [ P.c__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_23,(0,1):C.GC_32})

V_179 = Vertex(name = 'V_179',
               particles = [ P.t__tilde__, P.b, P.G__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_24,(0,1):C.GC_33})

V_180 = Vertex(name = 'V_180',
               particles = [ P.d__tilde__, P.d, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_595})

V_181 = Vertex(name = 'V_181',
               particles = [ P.s__tilde__, P.s, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_605})

V_182 = Vertex(name = 'V_182',
               particles = [ P.b__tilde__, P.b, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_591})

V_183 = Vertex(name = 'V_183',
               particles = [ P.d__tilde__, P.d, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_596})

V_184 = Vertex(name = 'V_184',
               particles = [ P.s__tilde__, P.s, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_606})

V_185 = Vertex(name = 'V_185',
               particles = [ P.b__tilde__, P.b, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_592})

V_186 = Vertex(name = 'V_186',
               particles = [ P.ve__tilde__, P.e__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS3 ],
               couplings = {(0,0):C.GC_598})

V_187 = Vertex(name = 'V_187',
               particles = [ P.vm__tilde__, P.mu__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS3 ],
               couplings = {(0,0):C.GC_602})

V_188 = Vertex(name = 'V_188',
               particles = [ P.vt__tilde__, P.ta__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS3 ],
               couplings = {(0,0):C.GC_610})

V_189 = Vertex(name = 'V_189',
               particles = [ P.e__plus__, P.e__minus__, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_599})

V_190 = Vertex(name = 'V_190',
               particles = [ P.mu__plus__, P.mu__minus__, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_603})

V_191 = Vertex(name = 'V_191',
               particles = [ P.ta__plus__, P.ta__minus__, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_611})

V_192 = Vertex(name = 'V_192',
               particles = [ P.e__plus__, P.e__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_600})

V_193 = Vertex(name = 'V_193',
               particles = [ P.mu__plus__, P.mu__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_604})

V_194 = Vertex(name = 'V_194',
               particles = [ P.ta__plus__, P.ta__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_612})

V_195 = Vertex(name = 'V_195',
               particles = [ P.u__tilde__, P.u, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_614})

V_196 = Vertex(name = 'V_196',
               particles = [ P.c__tilde__, P.c, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_594})

V_197 = Vertex(name = 'V_197',
               particles = [ P.t__tilde__, P.t, P.G0 ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS4 ],
               couplings = {(0,0):C.GC_608})

V_198 = Vertex(name = 'V_198',
               particles = [ P.u__tilde__, P.u, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_613})

V_199 = Vertex(name = 'V_199',
               particles = [ P.c__tilde__, P.c, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_593})

V_200 = Vertex(name = 'V_200',
               particles = [ P.t__tilde__, P.t, P.H ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS6 ],
               couplings = {(0,0):C.GC_607})

V_201 = Vertex(name = 'V_201',
               particles = [ P.d__tilde__, P.u, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_34,(0,1):C.GC_43})

V_202 = Vertex(name = 'V_202',
               particles = [ P.s__tilde__, P.u, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_35,(0,1):C.GC_44})

V_203 = Vertex(name = 'V_203',
               particles = [ P.b__tilde__, P.u, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_36,(0,1):C.GC_45})

V_204 = Vertex(name = 'V_204',
               particles = [ P.d__tilde__, P.c, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_37,(0,1):C.GC_46})

V_205 = Vertex(name = 'V_205',
               particles = [ P.s__tilde__, P.c, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_38,(0,1):C.GC_47})

V_206 = Vertex(name = 'V_206',
               particles = [ P.b__tilde__, P.c, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_39,(0,1):C.GC_48})

V_207 = Vertex(name = 'V_207',
               particles = [ P.d__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_40,(0,1):C.GC_49})

V_208 = Vertex(name = 'V_208',
               particles = [ P.s__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_41,(0,1):C.GC_50})

V_209 = Vertex(name = 'V_209',
               particles = [ P.b__tilde__, P.t, P.G__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFS3, L.FFS5 ],
               couplings = {(0,0):C.GC_42,(0,1):C.GC_51})

V_210 = Vertex(name = 'V_210',
               particles = [ P.u__tilde__, P.u, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_211 = Vertex(name = 'V_211',
               particles = [ P.c__tilde__, P.c, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_212 = Vertex(name = 'V_212',
               particles = [ P.t__tilde__, P.t, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_213 = Vertex(name = 'V_213',
               particles = [ P.u__tilde__, P.u, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_214 = Vertex(name = 'V_214',
               particles = [ P.c__tilde__, P.c, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_215 = Vertex(name = 'V_215',
               particles = [ P.t__tilde__, P.t, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_216 = Vertex(name = 'V_216',
               particles = [ P.d__tilde__, P.d, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_217 = Vertex(name = 'V_217',
               particles = [ P.s__tilde__, P.s, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_218 = Vertex(name = 'V_218',
               particles = [ P.b__tilde__, P.b, P.g, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSSS1, L.FFVSSSS2, L.FFVSSSS3, L.FFVSSSS4 ],
               couplings = {(0,0):C.GC_169,(0,2):C.GC_114,(0,3):C.GC_116,(0,1):C.GC_112})

V_219 = Vertex(name = 'V_219',
               particles = [ P.d__tilde__, P.d, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_220 = Vertex(name = 'V_220',
               particles = [ P.s__tilde__, P.s, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_221 = Vertex(name = 'V_221',
               particles = [ P.b__tilde__, P.b, P.g, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSS1, L.FFVSS2, L.FFVSS3 ],
               couplings = {(0,0):C.GC_144,(0,2):C.GC_80,(0,1):C.GC_79})

V_222 = Vertex(name = 'V_222',
               particles = [ P.u__tilde__, P.u, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_223 = Vertex(name = 'V_223',
               particles = [ P.c__tilde__, P.c, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_224 = Vertex(name = 'V_224',
               particles = [ P.t__tilde__, P.t, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_225 = Vertex(name = 'V_225',
               particles = [ P.u__tilde__, P.u, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_226 = Vertex(name = 'V_226',
               particles = [ P.c__tilde__, P.c, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_227 = Vertex(name = 'V_227',
               particles = [ P.t__tilde__, P.t, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_228 = Vertex(name = 'V_228',
               particles = [ P.d__tilde__, P.d, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_229 = Vertex(name = 'V_229',
               particles = [ P.s__tilde__, P.s, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_230 = Vertex(name = 'V_230',
               particles = [ P.b__tilde__, P.b, P.g, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_131})

V_231 = Vertex(name = 'V_231',
               particles = [ P.d__tilde__, P.d, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_232 = Vertex(name = 'V_232',
               particles = [ P.s__tilde__, P.s, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_233 = Vertex(name = 'V_233',
               particles = [ P.b__tilde__, P.b, P.g, P.phinew, P.phinew, P.phinew ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_156})

V_234 = Vertex(name = 'V_234',
               particles = [ P.a, P.W__minus__, P.G0, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_240})

V_235 = Vertex(name = 'V_235',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_239})

V_236 = Vertex(name = 'V_236',
               particles = [ P.a, P.W__minus__, P.G0, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_343})

V_237 = Vertex(name = 'V_237',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_344})

V_238 = Vertex(name = 'V_238',
               particles = [ P.a, P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_277,(0,0):C.GC_361,(0,1):C.GC_274})

V_239 = Vertex(name = 'V_239',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_278,(0,0):C.GC_362,(0,1):C.GC_273})

V_240 = Vertex(name = 'V_240',
               particles = [ P.a, P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_379})

V_241 = Vertex(name = 'V_241',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_380})

V_242 = Vertex(name = 'V_242',
               particles = [ P.a, P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_397,(0,1):C.GC_325,(0,2):C.GC_322})

V_243 = Vertex(name = 'V_243',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_398,(0,1):C.GC_324,(0,2):C.GC_323})

V_244 = Vertex(name = 'V_244',
               particles = [ P.a, P.W__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_514})

V_245 = Vertex(name = 'V_245',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_530})

V_246 = Vertex(name = 'V_246',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_521,(0,0):C.GC_533,(0,1):C.GC_518})

V_247 = Vertex(name = 'V_247',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_536})

V_248 = Vertex(name = 'V_248',
               particles = [ P.a, P.W__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_539,(0,1):C.GC_526,(0,2):C.GC_525})

V_249 = Vertex(name = 'V_249',
               particles = [ P.W__minus__, P.G0, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_224})

V_250 = Vertex(name = 'V_250',
               particles = [ P.W__minus__, P.G0, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_327})

V_251 = Vertex(name = 'V_251',
               particles = [ P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_345,(0,2):C.GC_247,(0,1):C.GC_245})

V_252 = Vertex(name = 'V_252',
               particles = [ P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_363})

V_253 = Vertex(name = 'V_253',
               particles = [ P.W__minus__, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_381,(0,2):C.GC_285,(0,1):C.GC_279})

V_254 = Vertex(name = 'V_254',
               particles = [ P.W__minus__, P.G__plus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_222})

V_255 = Vertex(name = 'V_255',
               particles = [ P.W__minus__, P.G__plus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_329})

V_256 = Vertex(name = 'V_256',
               particles = [ P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_347,(0,2):C.GC_249,(0,1):C.GC_243})

V_257 = Vertex(name = 'V_257',
               particles = [ P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_365})

V_258 = Vertex(name = 'V_258',
               particles = [ P.W__minus__, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_383,(0,2):C.GC_283,(0,1):C.GC_281})

V_259 = Vertex(name = 'V_259',
               particles = [ P.W__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSS1 ],
               couplings = {(0,0):C.GC_528})

V_260 = Vertex(name = 'V_260',
               particles = [ P.W__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS1, L.VSSS3, L.VSSS4 ],
               couplings = {(0,0):C.GC_531,(0,2):C.GC_517,(0,1):C.GC_516})

V_261 = Vertex(name = 'V_261',
               particles = [ P.W__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS1 ],
               couplings = {(0,0):C.GC_534})

V_262 = Vertex(name = 'V_262',
               particles = [ P.W__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS1, L.VSSSSS3, L.VSSSSS4 ],
               couplings = {(0,0):C.GC_537,(0,1):C.GC_523,(0,2):C.GC_522})

V_263 = Vertex(name = 'V_263',
               particles = [ P.a, P.W__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVV1 ],
               couplings = {(0,0):C.GC_5})

V_264 = Vertex(name = 'V_264',
               particles = [ P.a, P.W__plus__, P.G0, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_240})

V_265 = Vertex(name = 'V_265',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_241})

V_266 = Vertex(name = 'V_266',
               particles = [ P.a, P.W__plus__, P.G0, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_343})

V_267 = Vertex(name = 'V_267',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_342})

V_268 = Vertex(name = 'V_268',
               particles = [ P.a, P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_277,(0,0):C.GC_361,(0,1):C.GC_274})

V_269 = Vertex(name = 'V_269',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_276,(0,0):C.GC_360,(0,1):C.GC_275})

V_270 = Vertex(name = 'V_270',
               particles = [ P.a, P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_379})

V_271 = Vertex(name = 'V_271',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_378})

V_272 = Vertex(name = 'V_272',
               particles = [ P.a, P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_397,(0,1):C.GC_325,(0,2):C.GC_322})

V_273 = Vertex(name = 'V_273',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_396,(0,1):C.GC_326,(0,2):C.GC_321})

V_274 = Vertex(name = 'V_274',
               particles = [ P.a, P.W__plus__, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_515})

V_275 = Vertex(name = 'V_275',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_529})

V_276 = Vertex(name = 'V_276',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_520,(0,0):C.GC_532,(0,1):C.GC_519})

V_277 = Vertex(name = 'V_277',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_535})

V_278 = Vertex(name = 'V_278',
               particles = [ P.a, P.W__plus__, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_538,(0,1):C.GC_527,(0,2):C.GC_524})

V_279 = Vertex(name = 'V_279',
               particles = [ P.W__plus__, P.G0, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_223})

V_280 = Vertex(name = 'V_280',
               particles = [ P.W__plus__, P.G0, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_328})

V_281 = Vertex(name = 'V_281',
               particles = [ P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_346,(0,2):C.GC_248,(0,1):C.GC_244})

V_282 = Vertex(name = 'V_282',
               particles = [ P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_364})

V_283 = Vertex(name = 'V_283',
               particles = [ P.W__plus__, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_382,(0,2):C.GC_284,(0,1):C.GC_280})

V_284 = Vertex(name = 'V_284',
               particles = [ P.W__plus__, P.G__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_222})

V_285 = Vertex(name = 'V_285',
               particles = [ P.W__plus__, P.G__minus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_329})

V_286 = Vertex(name = 'V_286',
               particles = [ P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_347,(0,2):C.GC_249,(0,1):C.GC_243})

V_287 = Vertex(name = 'V_287',
               particles = [ P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_365})

V_288 = Vertex(name = 'V_288',
               particles = [ P.W__plus__, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_383,(0,2):C.GC_283,(0,1):C.GC_281})

V_289 = Vertex(name = 'V_289',
               particles = [ P.W__plus__, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSS1 ],
               couplings = {(0,0):C.GC_528})

V_290 = Vertex(name = 'V_290',
               particles = [ P.W__plus__, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS1, L.VSSS3, L.VSSS4 ],
               couplings = {(0,0):C.GC_531,(0,2):C.GC_517,(0,1):C.GC_516})

V_291 = Vertex(name = 'V_291',
               particles = [ P.W__plus__, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS1 ],
               couplings = {(0,0):C.GC_534})

V_292 = Vertex(name = 'V_292',
               particles = [ P.W__plus__, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS1, L.VSSSSS3, L.VSSSSS4 ],
               couplings = {(0,0):C.GC_537,(0,1):C.GC_523,(0,2):C.GC_522})

V_293 = Vertex(name = 'V_293',
               particles = [ P.W__minus__, P.W__plus__, P.G0, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_211})

V_294 = Vertex(name = 'V_294',
               particles = [ P.W__minus__, P.W__plus__, P.G__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_211})

V_295 = Vertex(name = 'V_295',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_211})

V_296 = Vertex(name = 'V_296',
               particles = [ P.W__minus__, P.W__plus__, P.G0, P.G0, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_218})

V_297 = Vertex(name = 'V_297',
               particles = [ P.W__minus__, P.W__plus__, P.G__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_218})

V_298 = Vertex(name = 'V_298',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_218})

V_299 = Vertex(name = 'V_299',
               particles = [ P.W__minus__, P.W__plus__, P.G0, P.G0, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_215,(0,0):C.GC_219,(0,1):C.GC_214})

V_300 = Vertex(name = 'V_300',
               particles = [ P.W__minus__, P.W__plus__, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_215,(0,0):C.GC_219,(0,1):C.GC_214})

V_301 = Vertex(name = 'V_301',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_215,(0,0):C.GC_219,(0,1):C.GC_214})

V_302 = Vertex(name = 'V_302',
               particles = [ P.W__minus__, P.W__plus__, P.G0, P.G0, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_220})

V_303 = Vertex(name = 'V_303',
               particles = [ P.W__minus__, P.W__plus__, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_220})

V_304 = Vertex(name = 'V_304',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_220})

V_305 = Vertex(name = 'V_305',
               particles = [ P.W__minus__, P.W__plus__, P.G0, P.G0, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_221,(0,1):C.GC_217,(0,2):C.GC_216})

V_306 = Vertex(name = 'V_306',
               particles = [ P.W__minus__, P.W__plus__, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_221,(0,1):C.GC_217,(0,2):C.GC_216})

V_307 = Vertex(name = 'V_307',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_221,(0,1):C.GC_217,(0,2):C.GC_216})

V_308 = Vertex(name = 'V_308',
               particles = [ P.W__minus__, P.W__plus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_504})

V_309 = Vertex(name = 'V_309',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_510})

V_310 = Vertex(name = 'V_310',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_507,(0,0):C.GC_511,(0,1):C.GC_506})

V_311 = Vertex(name = 'V_311',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_512})

V_312 = Vertex(name = 'V_312',
               particles = [ P.W__minus__, P.W__plus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_513,(0,1):C.GC_509,(0,2):C.GC_508})

V_313 = Vertex(name = 'V_313',
               particles = [ P.a, P.a, P.W__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVVV2 ],
               couplings = {(0,0):C.GC_6})

V_314 = Vertex(name = 'V_314',
               particles = [ P.W__minus__, P.W__plus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.VVV1 ],
               couplings = {(0,0):C.GC_238})

V_315 = Vertex(name = 'V_315',
               particles = [ P.W__minus__, P.W__minus__, P.W__plus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVVV2 ],
               couplings = {(0,0):C.GC_212})

V_316 = Vertex(name = 'V_316',
               particles = [ P.e__plus__, P.ve, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS5 ],
               couplings = {(0,0):C.GC_597})

V_317 = Vertex(name = 'V_317',
               particles = [ P.mu__plus__, P.vm, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS5 ],
               couplings = {(0,0):C.GC_601})

V_318 = Vertex(name = 'V_318',
               particles = [ P.ta__plus__, P.vt, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFS5 ],
               couplings = {(0,0):C.GC_609})

V_319 = Vertex(name = 'V_319',
               particles = [ P.a, P.Z, P.G__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_422})

V_320 = Vertex(name = 'V_320',
               particles = [ P.a, P.Z, P.G__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_443})

V_321 = Vertex(name = 'V_321',
               particles = [ P.a, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_430,(0,0):C.GC_447,(0,1):C.GC_429})

V_322 = Vertex(name = 'V_322',
               particles = [ P.a, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_451})

V_323 = Vertex(name = 'V_323',
               particles = [ P.a, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_455,(0,1):C.GC_439,(0,2):C.GC_438})

V_324 = Vertex(name = 'V_324',
               particles = [ P.Z, P.G0, P.H ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_419})

V_325 = Vertex(name = 'V_325',
               particles = [ P.Z, P.G0, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_442})

V_326 = Vertex(name = 'V_326',
               particles = [ P.Z, P.G0, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_446,(0,2):C.GC_428,(0,1):C.GC_423})

V_327 = Vertex(name = 'V_327',
               particles = [ P.Z, P.G0, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_450})

V_328 = Vertex(name = 'V_328',
               particles = [ P.Z, P.G0, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_454,(0,2):C.GC_434,(0,1):C.GC_433})

V_329 = Vertex(name = 'V_329',
               particles = [ P.Z, P.G0, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSS1 ],
               couplings = {(0,0):C.GC_558})

V_330 = Vertex(name = 'V_330',
               particles = [ P.Z, P.G0, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS1, L.VSSS3, L.VSSS4 ],
               couplings = {(0,0):C.GC_559,(0,2):C.GC_555,(0,1):C.GC_554})

V_331 = Vertex(name = 'V_331',
               particles = [ P.Z, P.G0, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS1 ],
               couplings = {(0,0):C.GC_560})

V_332 = Vertex(name = 'V_332',
               particles = [ P.Z, P.G0, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS1, L.VSSSSS3, L.VSSSSS4 ],
               couplings = {(0,0):C.GC_561,(0,1):C.GC_557,(0,2):C.GC_556})

V_333 = Vertex(name = 'V_333',
               particles = [ P.Z, P.G__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VSS2 ],
               couplings = {(0,0):C.GC_420})

V_334 = Vertex(name = 'V_334',
               particles = [ P.Z, P.G__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSS2 ],
               couplings = {(0,0):C.GC_440})

V_335 = Vertex(name = 'V_335',
               particles = [ P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSS2, L.VSSSS3, L.VSSSS4 ],
               couplings = {(0,0):C.GC_444,(0,2):C.GC_427,(0,1):C.GC_424})

V_336 = Vertex(name = 'V_336',
               particles = [ P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSS2 ],
               couplings = {(0,0):C.GC_448})

V_337 = Vertex(name = 'V_337',
               particles = [ P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VSSSSSS1, L.VSSSSSS2, L.VSSSSSS3 ],
               couplings = {(0,0):C.GC_452,(0,2):C.GC_435,(0,1):C.GC_431})

V_338 = Vertex(name = 'V_338',
               particles = [ P.W__minus__, P.Z, P.G0, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_9})

V_339 = Vertex(name = 'V_339',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_10})

V_340 = Vertex(name = 'V_340',
               particles = [ P.W__minus__, P.Z, P.G0, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_129})

V_341 = Vertex(name = 'V_341',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_128})

V_342 = Vertex(name = 'V_342',
               particles = [ P.W__minus__, P.Z, P.G0, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_77,(0,0):C.GC_142,(0,1):C.GC_74})

V_343 = Vertex(name = 'V_343',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_76,(0,0):C.GC_141,(0,1):C.GC_75})

V_344 = Vertex(name = 'V_344',
               particles = [ P.W__minus__, P.Z, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_154})

V_345 = Vertex(name = 'V_345',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_153})

V_346 = Vertex(name = 'V_346',
               particles = [ P.W__minus__, P.Z, P.G0, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_167,(0,1):C.GC_110,(0,2):C.GC_107})

V_347 = Vertex(name = 'V_347',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_166,(0,1):C.GC_111,(0,2):C.GC_106})

V_348 = Vertex(name = 'V_348',
               particles = [ P.W__minus__, P.Z, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_475})

V_349 = Vertex(name = 'V_349',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_484})

V_350 = Vertex(name = 'V_350',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_478,(0,0):C.GC_486,(0,1):C.GC_477})

V_351 = Vertex(name = 'V_351',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_488})

V_352 = Vertex(name = 'V_352',
               particles = [ P.W__minus__, P.Z, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_490,(0,1):C.GC_483,(0,2):C.GC_480})

V_353 = Vertex(name = 'V_353',
               particles = [ P.W__plus__, P.Z, P.G0, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_9})

V_354 = Vertex(name = 'V_354',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_8})

V_355 = Vertex(name = 'V_355',
               particles = [ P.W__plus__, P.Z, P.G0, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_129})

V_356 = Vertex(name = 'V_356',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_130})

V_357 = Vertex(name = 'V_357',
               particles = [ P.W__plus__, P.Z, P.G0, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_77,(0,0):C.GC_142,(0,1):C.GC_74})

V_358 = Vertex(name = 'V_358',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_78,(0,0):C.GC_143,(0,1):C.GC_73})

V_359 = Vertex(name = 'V_359',
               particles = [ P.W__plus__, P.Z, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_154})

V_360 = Vertex(name = 'V_360',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_155})

V_361 = Vertex(name = 'V_361',
               particles = [ P.W__plus__, P.Z, P.G0, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_167,(0,1):C.GC_110,(0,2):C.GC_107})

V_362 = Vertex(name = 'V_362',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_168,(0,1):C.GC_109,(0,2):C.GC_108})

V_363 = Vertex(name = 'V_363',
               particles = [ P.W__plus__, P.Z, P.G__minus__ ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_474})

V_364 = Vertex(name = 'V_364',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_485})

V_365 = Vertex(name = 'V_365',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_479,(0,0):C.GC_487,(0,1):C.GC_476})

V_366 = Vertex(name = 'V_366',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_489})

V_367 = Vertex(name = 'V_367',
               particles = [ P.W__plus__, P.Z, P.G__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_491,(0,1):C.GC_482,(0,2):C.GC_481})

V_368 = Vertex(name = 'V_368',
               particles = [ P.a, P.W__minus__, P.W__plus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.VVVV5 ],
               couplings = {(0,0):C.GC_242})

V_369 = Vertex(name = 'V_369',
               particles = [ P.Z, P.Z, P.G0, P.G0 ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_457})

V_370 = Vertex(name = 'V_370',
               particles = [ P.Z, P.Z, P.G__minus__, P.G__plus__ ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_456})

V_371 = Vertex(name = 'V_371',
               particles = [ P.Z, P.Z, P.H, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_457})

V_372 = Vertex(name = 'V_372',
               particles = [ P.Z, P.Z, P.G0, P.G0, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_466})

V_373 = Vertex(name = 'V_373',
               particles = [ P.Z, P.Z, P.G__minus__, P.G__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_467})

V_374 = Vertex(name = 'V_374',
               particles = [ P.Z, P.Z, P.H, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2 ],
               couplings = {(0,0):C.GC_466})

V_375 = Vertex(name = 'V_375',
               particles = [ P.Z, P.Z, P.G0, P.G0, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_460,(0,0):C.GC_468,(0,1):C.GC_459})

V_376 = Vertex(name = 'V_376',
               particles = [ P.Z, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_461,(0,0):C.GC_469,(0,1):C.GC_458})

V_377 = Vertex(name = 'V_377',
               particles = [ P.Z, P.Z, P.H, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3, L.VVSSSS4, L.VVSSSS5 ],
               couplings = {(0,2):C.GC_460,(0,0):C.GC_468,(0,1):C.GC_459})

V_378 = Vertex(name = 'V_378',
               particles = [ P.Z, P.Z, P.G0, P.G0, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_470})

V_379 = Vertex(name = 'V_379',
               particles = [ P.Z, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_471})

V_380 = Vertex(name = 'V_380',
               particles = [ P.Z, P.Z, P.H, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1 ],
               couplings = {(0,0):C.GC_470})

V_381 = Vertex(name = 'V_381',
               particles = [ P.Z, P.Z, P.G0, P.G0, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_472,(0,1):C.GC_465,(0,2):C.GC_462})

V_382 = Vertex(name = 'V_382',
               particles = [ P.Z, P.Z, P.G__minus__, P.G__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_473,(0,1):C.GC_464,(0,2):C.GC_463})

V_383 = Vertex(name = 'V_383',
               particles = [ P.Z, P.Z, P.H, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSSS1, L.VVSSSSSS2, L.VVSSSSSS3 ],
               couplings = {(0,0):C.GC_472,(0,1):C.GC_465,(0,2):C.GC_462})

V_384 = Vertex(name = 'V_384',
               particles = [ P.Z, P.Z, P.H ],
               color = [ '1' ],
               lorentz = [ L.VVS2 ],
               couplings = {(0,0):C.GC_563})

V_385 = Vertex(name = 'V_385',
               particles = [ P.Z, P.Z, P.H, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSS3 ],
               couplings = {(0,0):C.GC_568})

V_386 = Vertex(name = 'V_386',
               particles = [ P.Z, P.Z, P.H, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSS2, L.VVSSS3, L.VVSSS4 ],
               couplings = {(0,2):C.GC_565,(0,0):C.GC_569,(0,1):C.GC_564})

V_387 = Vertex(name = 'V_387',
               particles = [ P.Z, P.Z, P.H, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSS3 ],
               couplings = {(0,0):C.GC_570})

V_388 = Vertex(name = 'V_388',
               particles = [ P.Z, P.Z, P.H, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.VVSSSSS1, L.VVSSSSS2, L.VVSSSSS3 ],
               couplings = {(0,0):C.GC_571,(0,1):C.GC_567,(0,2):C.GC_566})

V_389 = Vertex(name = 'V_389',
               particles = [ P.W__minus__, P.W__plus__, P.Z, P.Z ],
               color = [ '1' ],
               lorentz = [ L.VVVV2 ],
               couplings = {(0,0):C.GC_213})

V_390 = Vertex(name = 'V_390',
               particles = [ P.d__tilde__, P.d, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_161,(0,2):C.GC_98,(0,3):C.GC_101,(0,1):C.GC_94})

V_391 = Vertex(name = 'V_391',
               particles = [ P.s__tilde__, P.s, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_161,(0,2):C.GC_98,(0,3):C.GC_101,(0,1):C.GC_94})

V_392 = Vertex(name = 'V_392',
               particles = [ P.b__tilde__, P.b, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_161,(0,2):C.GC_98,(0,3):C.GC_101,(0,1):C.GC_94})

V_393 = Vertex(name = 'V_393',
               particles = [ P.d__tilde__, P.d, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS13, L.FFVSSSS17, L.FFVSSSS18, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8, L.FFVSSSS9 ],
               couplings = {(0,3):C.GC_395,(0,7):C.GC_417,(0,5):C.GC_317,(0,6):C.GC_320,(0,2):C.GC_407,(0,1):C.GC_409,(0,4):C.GC_316,(0,0):C.GC_405})

V_394 = Vertex(name = 'V_394',
               particles = [ P.s__tilde__, P.s, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS13, L.FFVSSSS17, L.FFVSSSS18, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8, L.FFVSSSS9 ],
               couplings = {(0,3):C.GC_395,(0,7):C.GC_417,(0,5):C.GC_317,(0,6):C.GC_320,(0,2):C.GC_407,(0,1):C.GC_409,(0,4):C.GC_316,(0,0):C.GC_405})

V_395 = Vertex(name = 'V_395',
               particles = [ P.b__tilde__, P.b, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS13, L.FFVSSSS17, L.FFVSSSS18, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8, L.FFVSSSS9 ],
               couplings = {(0,3):C.GC_395,(0,7):C.GC_417,(0,5):C.GC_317,(0,6):C.GC_320,(0,2):C.GC_407,(0,1):C.GC_409,(0,4):C.GC_316,(0,0):C.GC_405})

V_396 = Vertex(name = 'V_396',
               particles = [ P.ve__tilde__, P.ve, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_453,(0,2):C.GC_436,(0,3):C.GC_437,(0,1):C.GC_432})

V_397 = Vertex(name = 'V_397',
               particles = [ P.vm__tilde__, P.vm, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_453,(0,2):C.GC_436,(0,3):C.GC_437,(0,1):C.GC_432})

V_398 = Vertex(name = 'V_398',
               particles = [ P.vt__tilde__, P.vt, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_453,(0,2):C.GC_436,(0,3):C.GC_437,(0,1):C.GC_432})

V_399 = Vertex(name = 'V_399',
               particles = [ P.u__tilde__, P.u, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_162,(0,2):C.GC_99,(0,3):C.GC_102,(0,1):C.GC_95})

V_400 = Vertex(name = 'V_400',
               particles = [ P.c__tilde__, P.c, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_162,(0,2):C.GC_99,(0,3):C.GC_102,(0,1):C.GC_95})

V_401 = Vertex(name = 'V_401',
               particles = [ P.t__tilde__, P.t, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_162,(0,2):C.GC_99,(0,3):C.GC_102,(0,1):C.GC_95})

V_402 = Vertex(name = 'V_402',
               particles = [ P.u__tilde__, P.u, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS12, L.FFVSSSS16, L.FFVSSSS23, L.FFVSSSS24, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_394,(0,0):C.GC_417,(0,6):C.GC_318,(0,7):C.GC_319,(0,2):C.GC_407,(0,3):C.GC_409,(0,5):C.GC_315,(0,1):C.GC_405})

V_403 = Vertex(name = 'V_403',
               particles = [ P.c__tilde__, P.c, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS12, L.FFVSSSS16, L.FFVSSSS23, L.FFVSSSS24, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_394,(0,0):C.GC_417,(0,6):C.GC_318,(0,7):C.GC_319,(0,2):C.GC_407,(0,3):C.GC_409,(0,5):C.GC_315,(0,1):C.GC_405})

V_404 = Vertex(name = 'V_404',
               particles = [ P.t__tilde__, P.t, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS12, L.FFVSSSS16, L.FFVSSSS23, L.FFVSSSS24, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_394,(0,0):C.GC_417,(0,6):C.GC_318,(0,7):C.GC_319,(0,2):C.GC_407,(0,3):C.GC_409,(0,5):C.GC_315,(0,1):C.GC_405})

V_405 = Vertex(name = 'V_405',
               particles = [ P.e__plus__, P.e__minus__, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_164,(0,2):C.GC_100,(0,3):C.GC_103,(0,1):C.GC_97})

V_406 = Vertex(name = 'V_406',
               particles = [ P.mu__plus__, P.mu__minus__, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_164,(0,2):C.GC_100,(0,3):C.GC_103,(0,1):C.GC_97})

V_407 = Vertex(name = 'V_407',
               particles = [ P.ta__plus__, P.ta__minus__, P.a, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS10, L.FFVSSSS14, L.FFVSSSS19, L.FFVSSSS20 ],
               couplings = {(0,0):C.GC_164,(0,2):C.GC_100,(0,3):C.GC_103,(0,1):C.GC_97})

V_408 = Vertex(name = 'V_408',
               particles = [ P.e__plus__, P.e__minus__, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS11, L.FFVSSSS15, L.FFVSSSS21, L.FFVSSSS22, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_395,(0,0):C.GC_418,(0,6):C.GC_317,(0,7):C.GC_320,(0,2):C.GC_408,(0,3):C.GC_410,(0,5):C.GC_316,(0,1):C.GC_406})

V_409 = Vertex(name = 'V_409',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS11, L.FFVSSSS15, L.FFVSSSS21, L.FFVSSSS22, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_395,(0,0):C.GC_418,(0,6):C.GC_317,(0,7):C.GC_320,(0,2):C.GC_408,(0,3):C.GC_410,(0,5):C.GC_316,(0,1):C.GC_406})

V_410 = Vertex(name = 'V_410',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS11, L.FFVSSSS15, L.FFVSSSS21, L.FFVSSSS22, L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,4):C.GC_395,(0,0):C.GC_418,(0,6):C.GC_317,(0,7):C.GC_320,(0,2):C.GC_408,(0,3):C.GC_410,(0,5):C.GC_316,(0,1):C.GC_406})

V_411 = Vertex(name = 'V_411',
               particles = [ P.e__plus__, P.ve, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_412 = Vertex(name = 'V_412',
               particles = [ P.mu__plus__, P.vm, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_413 = Vertex(name = 'V_413',
               particles = [ P.ta__plus__, P.vt, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_414 = Vertex(name = 'V_414',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_415 = Vertex(name = 'V_415',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_416 = Vertex(name = 'V_416',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_384,(0,2):C.GC_286,(0,3):C.GC_287,(0,1):C.GC_282})

V_417 = Vertex(name = 'V_417',
               particles = [ P.d__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_385,(0,2):C.GC_289,(0,3):C.GC_290,(0,1):C.GC_288})

V_418 = Vertex(name = 'V_418',
               particles = [ P.s__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_386,(0,2):C.GC_292,(0,3):C.GC_293,(0,1):C.GC_291})

V_419 = Vertex(name = 'V_419',
               particles = [ P.b__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_387,(0,2):C.GC_295,(0,3):C.GC_296,(0,1):C.GC_294})

V_420 = Vertex(name = 'V_420',
               particles = [ P.d__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_388,(0,2):C.GC_298,(0,3):C.GC_299,(0,1):C.GC_297})

V_421 = Vertex(name = 'V_421',
               particles = [ P.s__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_389,(0,2):C.GC_301,(0,3):C.GC_302,(0,1):C.GC_300})

V_422 = Vertex(name = 'V_422',
               particles = [ P.b__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_390,(0,2):C.GC_304,(0,3):C.GC_305,(0,1):C.GC_303})

V_423 = Vertex(name = 'V_423',
               particles = [ P.d__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_391,(0,2):C.GC_307,(0,3):C.GC_308,(0,1):C.GC_306})

V_424 = Vertex(name = 'V_424',
               particles = [ P.s__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_392,(0,2):C.GC_310,(0,3):C.GC_311,(0,1):C.GC_309})

V_425 = Vertex(name = 'V_425',
               particles = [ P.b__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_393,(0,2):C.GC_313,(0,3):C.GC_314,(0,1):C.GC_312})

V_426 = Vertex(name = 'V_426',
               particles = [ P.u__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_624,(0,2):C.GC_619,(0,3):C.GC_620,(0,1):C.GC_618})

V_427 = Vertex(name = 'V_427',
               particles = [ P.c__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_654,(0,2):C.GC_649,(0,3):C.GC_650,(0,1):C.GC_648})

V_428 = Vertex(name = 'V_428',
               particles = [ P.t__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_684,(0,2):C.GC_679,(0,3):C.GC_680,(0,1):C.GC_678})

V_429 = Vertex(name = 'V_429',
               particles = [ P.u__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_634,(0,2):C.GC_629,(0,3):C.GC_630,(0,1):C.GC_628})

V_430 = Vertex(name = 'V_430',
               particles = [ P.c__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_664,(0,2):C.GC_659,(0,3):C.GC_660,(0,1):C.GC_658})

V_431 = Vertex(name = 'V_431',
               particles = [ P.t__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_694,(0,2):C.GC_689,(0,3):C.GC_690,(0,1):C.GC_688})

V_432 = Vertex(name = 'V_432',
               particles = [ P.u__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_644,(0,2):C.GC_639,(0,3):C.GC_640,(0,1):C.GC_638})

V_433 = Vertex(name = 'V_433',
               particles = [ P.c__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_674,(0,2):C.GC_669,(0,3):C.GC_670,(0,1):C.GC_668})

V_434 = Vertex(name = 'V_434',
               particles = [ P.t__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSSS5, L.FFVSSSS6, L.FFVSSSS7, L.FFVSSSS8 ],
               couplings = {(0,0):C.GC_704,(0,2):C.GC_699,(0,3):C.GC_700,(0,1):C.GC_698})

V_435 = Vertex(name = 'V_435',
               particles = [ P.d__tilde__, P.d, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_136,(0,1):C.GC_68,(0,0):C.GC_64})

V_436 = Vertex(name = 'V_436',
               particles = [ P.s__tilde__, P.s, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_136,(0,1):C.GC_68,(0,0):C.GC_64})

V_437 = Vertex(name = 'V_437',
               particles = [ P.b__tilde__, P.b, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_136,(0,1):C.GC_68,(0,0):C.GC_64})

V_438 = Vertex(name = 'V_438',
               particles = [ P.d__tilde__, P.d, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS11, L.FFVSS15, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS7 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_413,(0,4):C.GC_272,(0,1):C.GC_403,(0,3):C.GC_269,(0,0):C.GC_401})

V_439 = Vertex(name = 'V_439',
               particles = [ P.s__tilde__, P.s, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS11, L.FFVSS15, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS7 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_413,(0,4):C.GC_272,(0,1):C.GC_403,(0,3):C.GC_269,(0,0):C.GC_401})

V_440 = Vertex(name = 'V_440',
               particles = [ P.b__tilde__, P.b, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS11, L.FFVSS15, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS7 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_413,(0,4):C.GC_272,(0,1):C.GC_403,(0,3):C.GC_269,(0,0):C.GC_401})

V_441 = Vertex(name = 'V_441',
               particles = [ P.e__plus__, P.e__minus__, P.a, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_139,(0,1):C.GC_70,(0,0):C.GC_67})

V_442 = Vertex(name = 'V_442',
               particles = [ P.mu__plus__, P.mu__minus__, P.a, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_139,(0,1):C.GC_70,(0,0):C.GC_67})

V_443 = Vertex(name = 'V_443',
               particles = [ P.ta__plus__, P.ta__minus__, P.a, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_139,(0,1):C.GC_70,(0,0):C.GC_67})

V_444 = Vertex(name = 'V_444',
               particles = [ P.e__plus__, P.e__minus__, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS13, L.FFVSS17, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS9 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_414,(0,4):C.GC_272,(0,1):C.GC_404,(0,3):C.GC_269,(0,0):C.GC_402})

V_445 = Vertex(name = 'V_445',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS13, L.FFVSS17, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS9 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_414,(0,4):C.GC_272,(0,1):C.GC_404,(0,3):C.GC_269,(0,0):C.GC_402})

V_446 = Vertex(name = 'V_446',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS13, L.FFVSS17, L.FFVSS4, L.FFVSS5, L.FFVSS6, L.FFVSS9 ],
               couplings = {(0,2):C.GC_359,(0,5):C.GC_414,(0,4):C.GC_272,(0,1):C.GC_404,(0,3):C.GC_269,(0,0):C.GC_402})

V_447 = Vertex(name = 'V_447',
               particles = [ P.e__plus__, P.e__minus__, P.a, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_126})

V_448 = Vertex(name = 'V_448',
               particles = [ P.mu__plus__, P.mu__minus__, P.a, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_126})

V_449 = Vertex(name = 'V_449',
               particles = [ P.ta__plus__, P.ta__minus__, P.a, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_126})

V_450 = Vertex(name = 'V_450',
               particles = [ P.e__plus__, P.e__minus__, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2, L.FFVS4 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_412})

V_451 = Vertex(name = 'V_451',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2, L.FFVS4 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_412})

V_452 = Vertex(name = 'V_452',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2, L.FFVS4 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_412})

V_453 = Vertex(name = 'V_453',
               particles = [ P.d__tilde__, P.d, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_124})

V_454 = Vertex(name = 'V_454',
               particles = [ P.s__tilde__, P.s, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_124})

V_455 = Vertex(name = 'V_455',
               particles = [ P.b__tilde__, P.b, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_124})

V_456 = Vertex(name = 'V_456',
               particles = [ P.d__tilde__, P.d, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS3 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_411})

V_457 = Vertex(name = 'V_457',
               particles = [ P.s__tilde__, P.s, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS3 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_411})

V_458 = Vertex(name = 'V_458',
               particles = [ P.b__tilde__, P.b, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS3 ],
               couplings = {(0,0):C.GC_341,(0,1):C.GC_411})

V_459 = Vertex(name = 'V_459',
               particles = [ P.u__tilde__, P.u, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_150})

V_460 = Vertex(name = 'V_460',
               particles = [ P.c__tilde__, P.c, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_150})

V_461 = Vertex(name = 'V_461',
               particles = [ P.t__tilde__, P.t, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_150})

V_462 = Vertex(name = 'V_462',
               particles = [ P.u__tilde__, P.u, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS5 ],
               couplings = {(0,0):C.GC_376,(0,1):C.GC_415})

V_463 = Vertex(name = 'V_463',
               particles = [ P.c__tilde__, P.c, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS5 ],
               couplings = {(0,0):C.GC_376,(0,1):C.GC_415})

V_464 = Vertex(name = 'V_464',
               particles = [ P.t__tilde__, P.t, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS5 ],
               couplings = {(0,0):C.GC_376,(0,1):C.GC_415})

V_465 = Vertex(name = 'V_465',
               particles = [ P.u__tilde__, P.u, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_137,(0,1):C.GC_69,(0,0):C.GC_66})

V_466 = Vertex(name = 'V_466',
               particles = [ P.c__tilde__, P.c, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_137,(0,1):C.GC_69,(0,0):C.GC_66})

V_467 = Vertex(name = 'V_467',
               particles = [ P.t__tilde__, P.t, P.a, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS12, L.FFVSS16, L.FFVSS8 ],
               couplings = {(0,2):C.GC_137,(0,1):C.GC_69,(0,0):C.GC_66})

V_468 = Vertex(name = 'V_468',
               particles = [ P.u__tilde__, P.u, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS10, L.FFVSS14, L.FFVSS18, L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,3):C.GC_358,(0,0):C.GC_413,(0,5):C.GC_271,(0,2):C.GC_403,(0,4):C.GC_270,(0,1):C.GC_401})

V_469 = Vertex(name = 'V_469',
               particles = [ P.c__tilde__, P.c, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS10, L.FFVSS14, L.FFVSS18, L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,3):C.GC_358,(0,0):C.GC_413,(0,5):C.GC_271,(0,2):C.GC_403,(0,4):C.GC_270,(0,1):C.GC_401})

V_470 = Vertex(name = 'V_470',
               particles = [ P.t__tilde__, P.t, P.Z, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS10, L.FFVSS14, L.FFVSS18, L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,3):C.GC_358,(0,0):C.GC_413,(0,5):C.GC_271,(0,2):C.GC_403,(0,4):C.GC_270,(0,1):C.GC_401})

V_471 = Vertex(name = 'V_471',
               particles = [ P.ve__tilde__, P.ve, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_449})

V_472 = Vertex(name = 'V_472',
               particles = [ P.vm__tilde__, P.vm, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_449})

V_473 = Vertex(name = 'V_473',
               particles = [ P.vt__tilde__, P.vt, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_449})

V_474 = Vertex(name = 'V_474',
               particles = [ P.ve__tilde__, P.ve, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_445,(0,2):C.GC_426,(0,1):C.GC_425})

V_475 = Vertex(name = 'V_475',
               particles = [ P.vm__tilde__, P.vm, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_445,(0,2):C.GC_426,(0,1):C.GC_425})

V_476 = Vertex(name = 'V_476',
               particles = [ P.vt__tilde__, P.vt, P.Z, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_445,(0,2):C.GC_426,(0,1):C.GC_425})

V_477 = Vertex(name = 'V_477',
               particles = [ P.ve__tilde__, P.ve, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_441})

V_478 = Vertex(name = 'V_478',
               particles = [ P.vm__tilde__, P.vm, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_441})

V_479 = Vertex(name = 'V_479',
               particles = [ P.vt__tilde__, P.vt, P.Z, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_441})

V_480 = Vertex(name = 'V_480',
               particles = [ P.d__tilde__, P.d, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_149})

V_481 = Vertex(name = 'V_481',
               particles = [ P.s__tilde__, P.s, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_149})

V_482 = Vertex(name = 'V_482',
               particles = [ P.b__tilde__, P.b, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_149})

V_483 = Vertex(name = 'V_483',
               particles = [ P.d__tilde__, P.d, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS3 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_415})

V_484 = Vertex(name = 'V_484',
               particles = [ P.s__tilde__, P.s, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS3 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_415})

V_485 = Vertex(name = 'V_485',
               particles = [ P.b__tilde__, P.b, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS3 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_415})

V_486 = Vertex(name = 'V_486',
               particles = [ P.u__tilde__, P.u, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_125})

V_487 = Vertex(name = 'V_487',
               particles = [ P.c__tilde__, P.c, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_125})

V_488 = Vertex(name = 'V_488',
               particles = [ P.t__tilde__, P.t, P.a, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS1 ],
               couplings = {(0,0):C.GC_125})

V_489 = Vertex(name = 'V_489',
               particles = [ P.u__tilde__, P.u, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS5 ],
               couplings = {(0,0):C.GC_340,(0,1):C.GC_411})

V_490 = Vertex(name = 'V_490',
               particles = [ P.c__tilde__, P.c, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS5 ],
               couplings = {(0,0):C.GC_340,(0,1):C.GC_411})

V_491 = Vertex(name = 'V_491',
               particles = [ P.t__tilde__, P.t, P.Z, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2, L.FFVS5 ],
               couplings = {(0,0):C.GC_340,(0,1):C.GC_411})

V_492 = Vertex(name = 'V_492',
               particles = [ P.e__plus__, P.e__minus__, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_151})

V_493 = Vertex(name = 'V_493',
               particles = [ P.mu__plus__, P.mu__minus__, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_151})

V_494 = Vertex(name = 'V_494',
               particles = [ P.ta__plus__, P.ta__minus__, P.a, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS1 ],
               couplings = {(0,0):C.GC_151})

V_495 = Vertex(name = 'V_495',
               particles = [ P.e__plus__, P.e__minus__, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS4 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_416})

V_496 = Vertex(name = 'V_496',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS4 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_416})

V_497 = Vertex(name = 'V_497',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2, L.FFVSSS4 ],
               couplings = {(0,0):C.GC_377,(0,1):C.GC_416})

V_498 = Vertex(name = 'V_498',
               particles = [ P.d__tilde__, P.u, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_349,(0,2):C.GC_252,(0,1):C.GC_251})

V_499 = Vertex(name = 'V_499',
               particles = [ P.s__tilde__, P.u, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_350,(0,2):C.GC_254,(0,1):C.GC_253})

V_500 = Vertex(name = 'V_500',
               particles = [ P.b__tilde__, P.u, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_351,(0,2):C.GC_256,(0,1):C.GC_255})

V_501 = Vertex(name = 'V_501',
               particles = [ P.d__tilde__, P.c, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_352,(0,2):C.GC_258,(0,1):C.GC_257})

V_502 = Vertex(name = 'V_502',
               particles = [ P.s__tilde__, P.c, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_353,(0,2):C.GC_260,(0,1):C.GC_259})

V_503 = Vertex(name = 'V_503',
               particles = [ P.b__tilde__, P.c, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_354,(0,2):C.GC_262,(0,1):C.GC_261})

V_504 = Vertex(name = 'V_504',
               particles = [ P.d__tilde__, P.t, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_355,(0,2):C.GC_264,(0,1):C.GC_263})

V_505 = Vertex(name = 'V_505',
               particles = [ P.s__tilde__, P.t, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_356,(0,2):C.GC_266,(0,1):C.GC_265})

V_506 = Vertex(name = 'V_506',
               particles = [ P.b__tilde__, P.t, P.W__minus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_357,(0,2):C.GC_268,(0,1):C.GC_267})

V_507 = Vertex(name = 'V_507',
               particles = [ P.e__plus__, P.ve, P.W__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_508 = Vertex(name = 'V_508',
               particles = [ P.mu__plus__, P.vm, P.W__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_509 = Vertex(name = 'V_509',
               particles = [ P.ta__plus__, P.vt, P.W__minus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_510 = Vertex(name = 'V_510',
               particles = [ P.e__plus__, P.ve, P.W__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_511 = Vertex(name = 'V_511',
               particles = [ P.mu__plus__, P.vm, P.W__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_512 = Vertex(name = 'V_512',
               particles = [ P.ta__plus__, P.vt, P.W__minus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_513 = Vertex(name = 'V_513',
               particles = [ P.e__plus__, P.ve, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_514 = Vertex(name = 'V_514',
               particles = [ P.mu__plus__, P.vm, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_515 = Vertex(name = 'V_515',
               particles = [ P.ta__plus__, P.vt, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_516 = Vertex(name = 'V_516',
               particles = [ P.d__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_367})

V_517 = Vertex(name = 'V_517',
               particles = [ P.s__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_368})

V_518 = Vertex(name = 'V_518',
               particles = [ P.b__tilde__, P.u, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_369})

V_519 = Vertex(name = 'V_519',
               particles = [ P.d__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_370})

V_520 = Vertex(name = 'V_520',
               particles = [ P.s__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_371})

V_521 = Vertex(name = 'V_521',
               particles = [ P.b__tilde__, P.c, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_372})

V_522 = Vertex(name = 'V_522',
               particles = [ P.d__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_373})

V_523 = Vertex(name = 'V_523',
               particles = [ P.s__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_374})

V_524 = Vertex(name = 'V_524',
               particles = [ P.b__tilde__, P.t, P.W__minus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_375})

V_525 = Vertex(name = 'V_525',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_526 = Vertex(name = 'V_526',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_527 = Vertex(name = 'V_527',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_348,(0,2):C.GC_250,(0,1):C.GC_246})

V_528 = Vertex(name = 'V_528',
               particles = [ P.u__tilde__, P.d, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_621})

V_529 = Vertex(name = 'V_529',
               particles = [ P.c__tilde__, P.d, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_651})

V_530 = Vertex(name = 'V_530',
               particles = [ P.t__tilde__, P.d, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_681})

V_531 = Vertex(name = 'V_531',
               particles = [ P.u__tilde__, P.s, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_631})

V_532 = Vertex(name = 'V_532',
               particles = [ P.c__tilde__, P.s, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_661})

V_533 = Vertex(name = 'V_533',
               particles = [ P.t__tilde__, P.s, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_691})

V_534 = Vertex(name = 'V_534',
               particles = [ P.u__tilde__, P.b, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_641})

V_535 = Vertex(name = 'V_535',
               particles = [ P.c__tilde__, P.b, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_671})

V_536 = Vertex(name = 'V_536',
               particles = [ P.t__tilde__, P.b, P.W__plus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_701})

V_537 = Vertex(name = 'V_537',
               particles = [ P.u__tilde__, P.d, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_622,(0,2):C.GC_617,(0,1):C.GC_616})

V_538 = Vertex(name = 'V_538',
               particles = [ P.c__tilde__, P.d, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_652,(0,2):C.GC_647,(0,1):C.GC_646})

V_539 = Vertex(name = 'V_539',
               particles = [ P.t__tilde__, P.d, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_682,(0,2):C.GC_677,(0,1):C.GC_676})

V_540 = Vertex(name = 'V_540',
               particles = [ P.u__tilde__, P.s, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_632,(0,2):C.GC_627,(0,1):C.GC_626})

V_541 = Vertex(name = 'V_541',
               particles = [ P.c__tilde__, P.s, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_662,(0,2):C.GC_657,(0,1):C.GC_656})

V_542 = Vertex(name = 'V_542',
               particles = [ P.t__tilde__, P.s, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_692,(0,2):C.GC_687,(0,1):C.GC_686})

V_543 = Vertex(name = 'V_543',
               particles = [ P.u__tilde__, P.b, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_642,(0,2):C.GC_637,(0,1):C.GC_636})

V_544 = Vertex(name = 'V_544',
               particles = [ P.c__tilde__, P.b, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_672,(0,2):C.GC_667,(0,1):C.GC_666})

V_545 = Vertex(name = 'V_545',
               particles = [ P.t__tilde__, P.b, P.W__plus__, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSS4, L.FFVSS5, L.FFVSS6 ],
               couplings = {(0,0):C.GC_702,(0,2):C.GC_697,(0,1):C.GC_696})

V_546 = Vertex(name = 'V_546',
               particles = [ P.d__tilde__, P.u, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_331})

V_547 = Vertex(name = 'V_547',
               particles = [ P.s__tilde__, P.u, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_332})

V_548 = Vertex(name = 'V_548',
               particles = [ P.b__tilde__, P.u, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_333})

V_549 = Vertex(name = 'V_549',
               particles = [ P.d__tilde__, P.c, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_334})

V_550 = Vertex(name = 'V_550',
               particles = [ P.s__tilde__, P.c, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_335})

V_551 = Vertex(name = 'V_551',
               particles = [ P.b__tilde__, P.c, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_336})

V_552 = Vertex(name = 'V_552',
               particles = [ P.d__tilde__, P.t, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_337})

V_553 = Vertex(name = 'V_553',
               particles = [ P.s__tilde__, P.t, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_338})

V_554 = Vertex(name = 'V_554',
               particles = [ P.b__tilde__, P.t, P.W__minus__, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_339})

V_555 = Vertex(name = 'V_555',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_556 = Vertex(name = 'V_556',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_557 = Vertex(name = 'V_557',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVS2 ],
               couplings = {(0,0):C.GC_330})

V_558 = Vertex(name = 'V_558',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_559 = Vertex(name = 'V_559',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_560 = Vertex(name = 'V_560',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ '1' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_366})

V_561 = Vertex(name = 'V_561',
               particles = [ P.u__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_623})

V_562 = Vertex(name = 'V_562',
               particles = [ P.c__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_653})

V_563 = Vertex(name = 'V_563',
               particles = [ P.t__tilde__, P.d, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_683})

V_564 = Vertex(name = 'V_564',
               particles = [ P.u__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_633})

V_565 = Vertex(name = 'V_565',
               particles = [ P.c__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_663})

V_566 = Vertex(name = 'V_566',
               particles = [ P.t__tilde__, P.s, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_693})

V_567 = Vertex(name = 'V_567',
               particles = [ P.u__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_643})

V_568 = Vertex(name = 'V_568',
               particles = [ P.c__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_673})

V_569 = Vertex(name = 'V_569',
               particles = [ P.t__tilde__, P.b, P.W__plus__, P.phinew, P.phinew, P.phinew ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFVSSS2 ],
               couplings = {(0,0):C.GC_703})

V_570 = Vertex(name = 'V_570',
               particles = [ P.e__plus__, P.ve, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_571 = Vertex(name = 'V_571',
               particles = [ P.mu__plus__, P.vm, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_572 = Vertex(name = 'V_572',
               particles = [ P.ta__plus__, P.vt, P.W__minus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_573 = Vertex(name = 'V_573',
               particles = [ P.ve__tilde__, P.ve, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_421})

V_574 = Vertex(name = 'V_574',
               particles = [ P.vm__tilde__, P.vm, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_421})

V_575 = Vertex(name = 'V_575',
               particles = [ P.vt__tilde__, P.vt, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_421})

V_576 = Vertex(name = 'V_576',
               particles = [ P.e__plus__, P.e__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_4})

V_577 = Vertex(name = 'V_577',
               particles = [ P.mu__plus__, P.mu__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_4})

V_578 = Vertex(name = 'V_578',
               particles = [ P.ta__plus__, P.ta__minus__, P.a ],
               color = [ '1' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_4})

V_579 = Vertex(name = 'V_579',
               particles = [ P.ve__tilde__, P.e__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_580 = Vertex(name = 'V_580',
               particles = [ P.vm__tilde__, P.mu__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_581 = Vertex(name = 'V_581',
               particles = [ P.vt__tilde__, P.ta__minus__, P.W__plus__ ],
               color = [ '1' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_225})

V_582 = Vertex(name = 'V_582',
               particles = [ P.e__plus__, P.e__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_400})

V_583 = Vertex(name = 'V_583',
               particles = [ P.mu__plus__, P.mu__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_400})

V_584 = Vertex(name = 'V_584',
               particles = [ P.ta__plus__, P.ta__minus__, P.Z ],
               color = [ '1' ],
               lorentz = [ L.FFV2, L.FFV4 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_400})

V_585 = Vertex(name = 'V_585',
               particles = [ P.u__tilde__, P.u, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_586 = Vertex(name = 'V_586',
               particles = [ P.c__tilde__, P.c, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_587 = Vertex(name = 'V_587',
               particles = [ P.t__tilde__, P.t, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_3})

V_588 = Vertex(name = 'V_588',
               particles = [ P.u__tilde__, P.u, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_589 = Vertex(name = 'V_589',
               particles = [ P.c__tilde__, P.c, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_590 = Vertex(name = 'V_590',
               particles = [ P.t__tilde__, P.t, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_591 = Vertex(name = 'V_591',
               particles = [ P.d__tilde__, P.u, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_226})

V_592 = Vertex(name = 'V_592',
               particles = [ P.s__tilde__, P.u, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_227})

V_593 = Vertex(name = 'V_593',
               particles = [ P.b__tilde__, P.u, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_228})

V_594 = Vertex(name = 'V_594',
               particles = [ P.d__tilde__, P.c, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_229})

V_595 = Vertex(name = 'V_595',
               particles = [ P.s__tilde__, P.c, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_230})

V_596 = Vertex(name = 'V_596',
               particles = [ P.b__tilde__, P.c, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_231})

V_597 = Vertex(name = 'V_597',
               particles = [ P.d__tilde__, P.t, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_232})

V_598 = Vertex(name = 'V_598',
               particles = [ P.s__tilde__, P.t, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_233})

V_599 = Vertex(name = 'V_599',
               particles = [ P.b__tilde__, P.t, P.W__minus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_234})

V_600 = Vertex(name = 'V_600',
               particles = [ P.u__tilde__, P.u, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_236,(0,1):C.GC_399})

V_601 = Vertex(name = 'V_601',
               particles = [ P.c__tilde__, P.c, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_236,(0,1):C.GC_399})

V_602 = Vertex(name = 'V_602',
               particles = [ P.t__tilde__, P.t, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV5 ],
               couplings = {(0,0):C.GC_236,(0,1):C.GC_399})

V_603 = Vertex(name = 'V_603',
               particles = [ P.d__tilde__, P.d, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_604 = Vertex(name = 'V_604',
               particles = [ P.s__tilde__, P.s, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_605 = Vertex(name = 'V_605',
               particles = [ P.b__tilde__, P.b, P.a ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_2})

V_606 = Vertex(name = 'V_606',
               particles = [ P.d__tilde__, P.d, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_607 = Vertex(name = 'V_607',
               particles = [ P.s__tilde__, P.s, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_608 = Vertex(name = 'V_608',
               particles = [ P.b__tilde__, P.b, P.g ],
               color = [ 'T(3,2,1)' ],
               lorentz = [ L.FFV1 ],
               couplings = {(0,0):C.GC_12})

V_609 = Vertex(name = 'V_609',
               particles = [ P.u__tilde__, P.d, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_615})

V_610 = Vertex(name = 'V_610',
               particles = [ P.c__tilde__, P.d, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_645})

V_611 = Vertex(name = 'V_611',
               particles = [ P.t__tilde__, P.d, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_675})

V_612 = Vertex(name = 'V_612',
               particles = [ P.u__tilde__, P.s, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_625})

V_613 = Vertex(name = 'V_613',
               particles = [ P.c__tilde__, P.s, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_655})

V_614 = Vertex(name = 'V_614',
               particles = [ P.t__tilde__, P.s, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_685})

V_615 = Vertex(name = 'V_615',
               particles = [ P.u__tilde__, P.b, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_635})

V_616 = Vertex(name = 'V_616',
               particles = [ P.c__tilde__, P.b, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_665})

V_617 = Vertex(name = 'V_617',
               particles = [ P.t__tilde__, P.b, P.W__plus__ ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2 ],
               couplings = {(0,0):C.GC_695})

V_618 = Vertex(name = 'V_618',
               particles = [ P.d__tilde__, P.d, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_399})

V_619 = Vertex(name = 'V_619',
               particles = [ P.s__tilde__, P.s, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_399})

V_620 = Vertex(name = 'V_620',
               particles = [ P.b__tilde__, P.b, P.Z ],
               color = [ 'Identity(1,2)' ],
               lorentz = [ L.FFV2, L.FFV3 ],
               couplings = {(0,0):C.GC_235,(0,1):C.GC_399})

