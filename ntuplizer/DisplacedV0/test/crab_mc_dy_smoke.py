"""CRAB3 smoke — Summer24 DY, few files (unitsPerJob=1, totalUnits=2).

Use this before the full ``crab_mc_dy.py`` submit.

  export CRAB_STORAGE_SITE=<your writeable T2>
  crab submit -c DisplacedV0/test/crab_mc_dy_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crab_common import build_mc_dy_config  # noqa: E402

config = build_mc_dy_config(smoke=True)
