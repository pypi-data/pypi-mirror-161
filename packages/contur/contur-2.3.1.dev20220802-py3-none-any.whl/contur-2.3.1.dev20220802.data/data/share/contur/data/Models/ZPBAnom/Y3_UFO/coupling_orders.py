# This file was automatically created by FeynRules 2.3.47
# Mathematica version: 12.2.0 for Mac OS X x86 (64-bit) (December 12, 2020)
# Date: Mon 2 Aug 2021 09:44:29


from .object_library import all_orders, CouplingOrder


QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 2)

