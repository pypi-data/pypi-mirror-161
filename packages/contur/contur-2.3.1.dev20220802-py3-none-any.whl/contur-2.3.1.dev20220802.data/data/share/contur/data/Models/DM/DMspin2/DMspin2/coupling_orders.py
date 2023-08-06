# This file was automatically created by FeynRules 2.4.43
# Mathematica version: 10.1.0  for Mac OS X x86 (64-bit) (March 24, 2015)
# Date: Wed 1 Jun 2016 20:28:08


from .object_library import all_orders, CouplingOrder


DMT = CouplingOrder(name = 'DMT',
                    expansion_order = 2,
                    hierarchy = 2)

QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 1,
                    perturbative_expansion = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 2)

