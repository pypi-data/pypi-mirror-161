# This file was automatically created by FeynRules 2.3.24
# Mathematica version: 10.1.0  for Linux x86 (64-bit) (March 24, 2015)
# Date: Wed 16 Nov 2016 12:03:06


from .object_library import all_orders, CouplingOrder


DMS = CouplingOrder(name = 'DMS',
                    expansion_order = 2,
                    hierarchy = 1)

QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 2)

