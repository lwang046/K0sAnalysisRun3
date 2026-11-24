"""CRAB3 — Summer24 DYto2L MLL>50 MiniAODSIM (full submit settings).

Shared pattern: ``crab_common.build_mc_dy_config``.
Smoke (few files): ``crab_mc_dy_smoke.py``.

Before submit on lxplus:
  1. TODO-VERIFY DAS string (samples/sim_dy_m50_13p6.txt, conditions.md)
  2. Match CMSSW to 140X_ / 150X_ token in the chosen dataset
  3. export CRAB_STORAGE_SITE=<your writeable T2>
  4. crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_mc_dy_config  # noqa: E402

config = build_mc_dy_config(smoke=False)
