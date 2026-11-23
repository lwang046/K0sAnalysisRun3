# KS Δ2D (rpv) config for Run3 / 2024.
# Ported from LukaLambrecht/K0sAnalysis analysis/config_ksvars.py
# (commit 2a132385) and adapted for DisplacedV0 → v0building output.
#
# Tree schema (after v0building/v0builder.py):
#   laurelin: _RPV (=Δ2D), _mass (=m_ππ), _pt, _weight, _nTrueInt
# Sideband + low-Δ2D normalization follow AN-20-111 §7 / method §2.5–2.6.

import numpy as np

# Phase-1 layer-aware Δ2D bins [cm] (method §2.6 starting proposal)
DELTA2D_BINS = [
    0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 16.0, 22.0, 30.0, 40.0, 60.0, 90.0, 120.0
]

# Low-Δ2D normalization region N (method §2.5): first well-populated bins.
# Revisit after first 2024 look (AN used ~[0, 0.5]; Run3 PU may prefer [0, 2]).
NORM_DELTA2D = [0.0, 2.0]

config = ({
    'rpv': {'variablename': '_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates', 'Run3 / 2024'],
            'bkgmodes': {
              'bkgdefault': {'type': None, 'info': 'Background not subtracted'},
              'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_mass',
                              'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)},
            },
            'bins': {
              'finebins': np.linspace(0, 20, num=41, endpoint=True),
              'defaultbins': DELTA2D_BINS,
              'anlikebins': [0., 0.5, 1.5, 4., 10., 20.],
            },
            'normalization': {
              'normlumi': {'type': 'lumi', 'info': 'Normalized to luminosity'},
              'normeventyield': {'type': 'eventyield', 'info': 'Normalized to data events'},
              'normrange': {'type': 'range',
                            'info': 'Normalized for low #Delta_{2D}',
                            'normvariable': '_RPV',
                            'normrange': NORM_DELTA2D},
            },
    },
    'rpvsig': {'variablename': '_RPVSig',
               'xaxtitle': '#Delta_{2D} significance',
               'yaxtitle': 'Reconstructed vertices',
               'treename': 'laurelin',
               'extrainfos': ['K^{0}_{S} candidates', 'Run3 / 2024'],
               'bkgmodes': {
                 'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                 'sidevariable': '_mass',
                                 'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
               },
               'bins': {
                 'finebins': np.linspace(0, 600, num=61, endpoint=True),
               },
               'normalization': {
                 'normrange': {'type': 'range',
                               'info': 'Normalized for low #Delta_{2D}',
                               'normvariable': '_RPV',
                               'normrange': NORM_DELTA2D},
               },
    }
})
