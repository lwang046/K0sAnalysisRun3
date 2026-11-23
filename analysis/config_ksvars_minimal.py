# Minimal KS Δ2D config (Run3). Sideband + low-Δ2D norm only.

from config_defaults_run3 import (
    BRANCH_DELTA2D,
    BRANCH_MASS,
    DELTA2D_BINS,
    ERA_LABEL,
    MASS_SIDE_BINS,
    NORM_DELTA2D,
    TREE_KS,
)
import numpy as np

config = ({
    'rpv': {'variablename': BRANCH_DELTA2D,
            'xaxtitle': '#Delta_{2D} (cm)',
            'yaxtitle': 'Reconstructed vertices',
            'treename': TREE_KS,
            'extrainfos': ['K^{0}_{S} candidates', ERA_LABEL],
            'bkgmodes': {
              'bkgsideband': {'type': 'sideband', 'info': 'Background subtracted',
                              'sidevariable': BRANCH_MASS,
                              'sidebins': MASS_SIDE_BINS},
            },
            'bins': {
              'defaultbins': DELTA2D_BINS,
              'finebins': np.linspace(0, 20, num=41, endpoint=True),
            },
            'normalization': {
              'normrange': {'type': 'range', 'info': 'Normalized for low #Delta_{2D}',
                            'normvariable': BRANCH_DELTA2D, 'normrange': NORM_DELTA2D},
            },
    }
})
