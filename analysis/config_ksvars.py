# KS Δ2D (rpv) config for Run3 / 2024.
# Ported from LukaLambrecht/K0sAnalysis analysis/config_ksvars.py
# (commit 2a132385) and adapted for DisplacedV0 → v0building output.
#
# Tree schema (after v0building/v0builder.py):
#   laurelin: _RPV (=Δ2D), _mass (=m_ππ), _pt, _weight, _nTrueInt
# Sideband + low-Δ2D normalization follow AN-20-111 §7 / method §2.5–2.6.
# Defaults (bins, HLT, DeepJet WP) live in config_defaults_run3.py.

import numpy as np

from config_defaults_run3 import (
    BRANCH_DELTA2D,
    BRANCH_MASS,
    DELTA2D_BINS,
    DEEPJET_BRANCH,
    DEEPJET_LOOSE_WP,
    ERA_LABEL,
    FIRST_ERA,
    HLT_BASELINE,
    MASS_SIDE_BINS,
    NORM_DELTA2D,
    TREE_KS,
)

config = ({
    'rpv': {'variablename': BRANCH_DELTA2D,
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': TREE_KS,
            'extrainfos': [
              'K^{0}_{S} candidates',
              ERA_LABEL,
              'HLT: ' + HLT_BASELINE,
              'DeepJet loose WP {:.4f} ({})'.format(DEEPJET_LOOSE_WP, DEEPJET_BRANCH),
              'First era: ' + FIRST_ERA,
            ],
            'bkgmodes': {
              'bkgdefault': {'type': None, 'info': 'Background not subtracted'},
              'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                              'sidevariable': BRANCH_MASS,
                              'sidebins': MASS_SIDE_BINS},
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
                            'normvariable': BRANCH_DELTA2D,
                            'normrange': NORM_DELTA2D},
            },
    },
    'rpvsig': {'variablename': '_RPVSig',
               'xaxtitle': '#Delta_{2D} significance',
               'yaxtitle': 'Reconstructed vertices',
               'treename': TREE_KS,
               'extrainfos': ['K^{0}_{S} candidates', ERA_LABEL],
               'bkgmodes': {
                 'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                                 'sidevariable': BRANCH_MASS,
                                 'sidebins': MASS_SIDE_BINS}
               },
               'bins': {
                 'finebins': np.linspace(0, 600, num=61, endpoint=True),
               },
               'normalization': {
                 'normrange': {'type': 'range',
                               'info': 'Normalized for low #Delta_{2D}',
                               'normvariable': BRANCH_DELTA2D,
                               'normrange': NORM_DELTA2D},
               },
    }
})
