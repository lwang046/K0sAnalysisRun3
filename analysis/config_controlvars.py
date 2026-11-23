# DY control plots (AN Fig. 5 style) for Run3.
# Branches filled by adapted v0building/v0builder.py from DisplacedV0
# Muon_* / Jet_* / passDimuonHLT selection.

import numpy as np

config = ({
    'mll':   {'variablename': '_nimloth_Mll',
              'xaxtitle': 'Dilepton invariant mass (GeV)',
              'yaxtitle': 'Events',
              'treename': 'nimloth',
              'extrainfos': ['Run3 / 2024'],
              'bkgmodes': {
                'bkgdefault': {'type': None},
              },
              'bins': {
                'binsdefault': np.linspace(81, 101, num=41, endpoint=True),
              },
              'normalization': {
                'normlumi': {'type': 'lumi'},
              },
    },
    'njets': {'variablename': '_nimloth_nJets',
              'xaxtitle': 'Number of jets',
              'yaxtitle': 'Events',
              'treename': 'nimloth',
              'extrainfos': ['Run3 / 2024'],
              'bkgmodes': {
                'bkgdefault': {'type': None},
              },
              'bins': {
                'binsdefault': np.linspace(-0.5, 6.5, num=8, endpoint=True),
              },
              'normalization': {
                'normlumi': {'type': 'lumi'},
              },
    },
    'lpt':   {'variablename': '_celeborn_lPt',
              'xaxtitle': 'Muon transverse momentum (GeV)',
              'yaxtitle': 'Muons',
              'treename': 'celeborn',
              'extrainfos': ['Run3 / 2024'],
              'bkgmodes': {
                'bkgdefault': {'type': None},
              },
              'bins': {
                'binsdefault': np.linspace(25, 125, num=50, endpoint=True),
              },
              'normalization': {
                'normlumi': {'type': 'lumi'},
              },
    },
    'leta':  {'variablename': '_celeborn_lEta',
              'xaxtitle': 'Muon pseudorapidity',
              'yaxtitle': 'Muons',
              'treename': 'celeborn',
              'extrainfos': ['Run3 / 2024'],
              'bkgmodes': {
                'bkgdefault': {'type': None},
              },
              'bins': {
                'binsdefault': np.linspace(-2.4, 2.4, num=50, endpoint=True),
              },
              'normalization': {
                'normlumi': {'type': 'lumi'},
              },
    },
})
