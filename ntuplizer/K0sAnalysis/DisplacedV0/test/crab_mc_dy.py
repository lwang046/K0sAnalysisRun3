"""CRAB3 — Summer24 inclusive DYto2Mu MLL>50 MiniAODSIM (full / production).

Uses ``crab_common.MC_DAS_DY`` (DYto2Mu, no PTLL). Smoke (PTLL-100): ``crab_mc_dy_smoke.py``.

Before submit on lxplus:
  1. Confirm DAS string in samples/sim_dy_m50_13p6.txt / conditions.md
     — do NOT point this at MC_DAS_DY_SMOKE / PTLL-100 for first-C
  2. Match CMSSW to 150X_ / MiniAODv6 (CMSSW_15_0_22 + el9 on lxplus9)
  3. export CRAB_STORAGE_SITE=<your writeable T2>
  4. crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_mc_dy_config  # noqa: E402

config = build_mc_dy_config(smoke=False)
