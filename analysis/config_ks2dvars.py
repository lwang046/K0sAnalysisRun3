# KS 2D (Δ2D vs pT) config for Run3 / 2024.
# Ported from LukaLambrecht/K0sAnalysis analysis/config_ks2dvars.py
# (commit 2a132385); bins from method §2.6.

import numpy as np

DELTA2D_BINS = [
    0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 16.0, 22.0, 30.0, 40.0, 60.0, 90.0, 120.0
]
PT_BINS = [1.0, 2.0, 3.0, 5.0, 8.0, 20.0]
NORM_DELTA2D = [0.0, 2.0]

config = ({
  'rpv_vs_pt': {'variablename': '_RPV',
                'xaxtitle': '#Delta_{2D} (cm)',
                'yvariablename': '_pt',
                'yaxtitle': 'p_{T} (GeV)',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates', 'Run3 / 2024'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
                  'defaultbins': {'xbins': DELTA2D_BINS, 'ybins': PT_BINS},
                  'anlikebins': {'xbins': [0., 0.5, 1.5, 4.5, 20.],
                                 'ybins': [0., 5., 10., 20.]},
                  'finexbins': {'xbins': [0., 0.5, 1., 1.5, 2., 5., 10., 15., 20.],
                                'ybins': PT_BINS},
                },
                'normalization': {
                  'normrange': {'type': 'range',
                                'info': 'Normalized for low #Delta_{2D}',
                                'normvariable': '_RPV',
                                'normrange': NORM_DELTA2D},
                }
  },
  'rpvsig_vs_pt': {'variablename': '_RPVSig',
                'xaxtitle': '#Delta_{2D} significance',
                'yvariablename': '_pt',
                'yaxtitle': 'p_{T} (GeV)',
                'treename': 'laurelin',
                'extrainfos': ['K^{0}_{S} candidates', 'Run3 / 2024'],
                'bkgmodes': {
                  'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                  'sidevariable': '_mass',
                                  'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)}
                },
                'bins': {
                  'finexbins': {'xbins': [0., 100., 200., 300., 400., 500., 600.],
                                'ybins': PT_BINS},
                },
                'normalization': {
                  'normrange': {'type': 'range',
                                'info': 'Normalized for low #Delta_{2D}',
                                'normvariable': '_RPV',
                                'normrange': NORM_DELTA2D},
                }
  }
})
