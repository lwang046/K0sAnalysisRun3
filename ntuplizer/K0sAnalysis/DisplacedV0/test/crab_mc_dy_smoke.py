"""CRAB3 smoke — Summer24 DY PTLL-100 (MC_DAS_DY_SMOKE), few files.

Pipeline / plumbing only — gen pT(ℓℓ)>100 ≠ inclusive data. Not for first-C physics.
Full production: ``crab_mc_dy.py`` (inclusive MC_DAS_DY after TODO-VERIFY files).

  export CRAB_STORAGE_SITE=<your writeable T2>
  crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_mc_dy_config  # noqa: E402

config = build_mc_dy_config(smoke=True)
