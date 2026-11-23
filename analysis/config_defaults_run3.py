# Shared Run3 / 2024 analysis defaults for DisplacedV0 → v0building → C(Δ2D).
# Imported by config_ksvars*.py so bins / norm / HLT / DeepJet stay consistent
# with samples/ and docs/first-c-delta2d-recipe.md.

import numpy as np

# First era for first C(Δ2D)
FIRST_ERA = "Run2024D"
ERA_LABEL = "Run3 / 2024D"

# Dimuon HLT (must match displacedV0_cfi.py hltPaths / samples/hlt_paths_2024.txt)
HLT_BASELINE = "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"
HLT_BRANCH_PASS = "passDimuonHLT"

# DeepJet loose WP placeholder (TODO-VERIFY on CVMFS BTV JSON)
DEEPJET_LOOSE_WP = 0.0494
DEEPJET_BRANCH = "Jet_btagDeepFlavB"

# Tree / branch names after v0building/v0builder.py
TREE_KS = "laurelin"
BRANCH_DELTA2D = "_RPV"
BRANCH_MASS = "_mass"
BRANCH_WEIGHT = "_weight"
BRANCH_NTRUEINT = "_nTrueInt"

# Phase-1 layer-aware Δ2D bins [cm] (method §2.6)
DELTA2D_BINS = [
    0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 16.0, 22.0, 30.0, 40.0, 60.0, 90.0, 120.0
]

# Low-Δ2D normalization region N (method §2.5 / AN §7)
NORM_DELTA2D = [0.0, 2.0]

# Ks sideband mass window
MASS_SIDE_BINS = np.linspace(0.44, 0.56, num=31, endpoint=True)
