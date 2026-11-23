# Minimal KS Δ2D config (Run3). Sideband + low-Δ2D norm only.

import numpy as np

DELTA2D_BINS = [
    0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 16.0, 22.0, 30.0, 40.0, 60.0, 90.0, 120.0
]

config = ({
    'rpv': {'variablename': '_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'laurelin',
            'extrainfos': ['K^{0}_{S} candidates', 'Run3 / 2024'],
            'bkgmodes': {
              'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_mass',
                              'sidebins': np.linspace(0.44, 0.56, num=31, endpoint=True)},
            },
            'bins': {
              'defaultbins': DELTA2D_BINS,
              'finebins': np.linspace(0, 20, num=41, endpoint=True),
            },
            'normalization': {
              'normrange': {'type': 'range', 'info': 'Normalized for low #Delta_{2D}',
                            'normvariable': '_RPV', 'normrange': [0., 2.]},
            },
    }
})
