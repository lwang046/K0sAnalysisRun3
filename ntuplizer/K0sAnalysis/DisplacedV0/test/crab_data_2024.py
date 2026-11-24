"""CRAB3 — Run2024D Muon0 MiniAOD (full submit settings).

Shared pattern: ``crab_common.build_data_config``. Twin: ``crab_data_2024_muon1.py``.
Smoke (few lumis): ``crab_data_2024_smoke.py`` or set smoke via common builder.

Before submit on lxplus:
  1. TODO-VERIFY DAS string (samples/data_muon_2024.txt, conditions.md)
  2. TODO-VERIFY golden lumiMask (samples/cert/README.md)
  3. export CRAB_STORAGE_SITE=<your writeable T2>   # required; placeholder otherwise
  4. crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_data_config  # noqa: E402

config = build_data_config(muon_pd="Muon0", smoke=False)
