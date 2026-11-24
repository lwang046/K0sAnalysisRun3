"""CRAB3 — Run2024D Muon1 MiniAOD twin of ``crab_data_2024.py``.

Same era, lumiMask, pset, and output naming pattern as Muon0. Submit both PDs
for the first C(Delta_2D) (see samples/data_muon_2024.txt).

  export CRAB_STORAGE_SITE=<your writeable T2>
  crab submit -c DisplacedV0/test/crab_data_2024_muon1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_data_config  # noqa: E402

config = build_data_config(muon_pd="Muon1", smoke=False)
