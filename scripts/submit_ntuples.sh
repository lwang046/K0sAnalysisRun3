#!/usr/bin/env bash
# Wrapper stub for CRAB ntuple submit (fill after M3 local cmsRun works).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Submit stubs live under: $ROOT/ntuplizer/K0sAnalysis/DisplacedV0/test/"
echo "  crab_data_2024.py  crab_mc_dy.py"
echo "scram layout: ln -s \$REPO/ntuplizer/K0sAnalysis \$CMSSW_BASE/src/K0sAnalysis"
echo "Edit datasets from samples/*.txt before crab submit."
exit 1
