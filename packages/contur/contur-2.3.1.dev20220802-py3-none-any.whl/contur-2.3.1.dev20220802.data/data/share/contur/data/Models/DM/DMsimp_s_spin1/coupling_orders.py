# This file was automatically created by FeynRules 2.3.26
# Mathematica version: 9.0 for Linux x86 (64-bit) (November 20, 2012)
# Date: Tue 24 Jan 2017 14:52:59


from .object_library import all_orders, CouplingOrder


DMV = CouplingOrder(name = 'DMV',
                    expansion_order = 2,
                    hierarchy = 2)

QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 1,
                    perturbative_expansion = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 2)

