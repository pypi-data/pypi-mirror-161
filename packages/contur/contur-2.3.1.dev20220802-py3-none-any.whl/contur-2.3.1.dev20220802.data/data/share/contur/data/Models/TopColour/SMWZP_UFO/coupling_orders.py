# This file was automatically created by FeynRules 2.3.29
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Fri 11 Dec 2020 18:33:58


from .object_library import all_orders, CouplingOrder


QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 2)

WZP = CouplingOrder(name = 'WZP',
                    expansion_order = 99,
                    hierarchy = 2)

