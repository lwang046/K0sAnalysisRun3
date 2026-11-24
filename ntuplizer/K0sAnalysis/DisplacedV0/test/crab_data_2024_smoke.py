"""CRAB3 smoke — Run2024D Muon0, few lumis (unitsPerJob=5, totalUnits=20).

Use this before the full ``crab_data_2024.py`` submit. Does not change DAS /
lumiMask / storageSite rules — still TODO-VERIFY + set CRAB_STORAGE_SITE.

  export CRAB_STORAGE_SITE=<your writeable T2>
  crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_data_config  # noqa: E402

config = build_data_config(muon_pd="Muon0", smoke=True)
