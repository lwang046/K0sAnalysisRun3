# Lambda diagnostic config (Run3). Not used for v1 C(Δ2D).

import numpy as np

config = ({
    'rpv': {'variablename': '_RPV',
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': 'telperion',
            'extrainfos': ['#Lambda^{0} candidates', 'Run3 / 2024'],
            'bkgmodes': {
              'bkgdefault': {'type': None, 'info': 'Background not subtracted'},
              'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                              'sidevariable': '_mass',
                              'sidebins': np.linspace(1.08, 1.15, num=31, endpoint=True)},
            },
            'bins': {
              'finebins': np.linspace(0, 20, num=41, endpoint=True),
              'defaultbins': [
                  0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 16.0, 22.0, 30.0, 40.0, 60.0, 90.0, 120.0
              ],
            },
            'normalization': {
              'normlumi': {'type': 'lumi', 'info': 'Normalized to luminosity'},
              'normeventyield': {'type': 'eventyield', 'info': 'Normalized to data events'},
              'normrange': {'type': 'range', 'info': 'Normalized for low #Delta_{2D}',
                            'normvariable': '_RPV', 'normrange': [0., 2.]},
            },
    }
})
