#!/usr/bin/env bash
# Discover 2024 Muon MiniAOD + DY MiniAODSIM candidates (plan §3.4).
# Requires dasgoclient on lxplus / CMS VO environment.
# Writes nothing — copy confirmed lines into samples/*.txt and conditions.md.
set -euo pipefail

echo "=== Muon MiniAOD 2024 (Muon0/Muon1 PromptReco + re-MiniAOD) ==="
dasgoclient -query='dataset=/Muon*/Run2024*/MINIAOD' | sort || true

echo "=== DoubleMuon MiniAOD 2024 (likely empty — confirm) ==="
dasgoclient -query='dataset=/DoubleMuon*/Run2024*/MINIAOD' | sort || true

echo "=== DY M-50 / DYto2L 13p6 TeV MiniAODSIM (PdmV + legacy names) ==="
dasgoclient -query='dataset=/DYto2L*13p6TeV*amcatnloFXFX*/Run*2024*MiniAOD*/MINIAODSIM' | sort || true
dasgoclient -query='dataset=/DYto2L*Bin-MLL-50*13p6TeV*/Run*2024*MiniAOD*/MINIAODSIM' | sort || true
dasgoclient -query='dataset=/DYJetsToLL_M-50*13p6TeV*/Run*2024*MiniAOD*/MINIAODSIM' | sort || true

echo "=== Optional fallbacks (document if used) ==="
dasgoclient -query='dataset=/DYto2L*13p6TeV*madgraphMLM*/Run*2024*MiniAOD*/MINIAODSIM' | sort || true
dasgoclient -query='dataset=/DYto2Mu*13p6TeV*/Run*2024*MiniAOD*/MINIAODSIM' | sort || true

echo "=== First-era focus: Run2024D Muon MiniAOD + Nano parent ==="
dasgoclient -query='dataset=/Muon*/Run2024D*/MINIAOD' | sort || true
dasgoclient -query='parent dataset=/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD' || true
dasgoclient -query='parent dataset=/Muon1/Run2024D-MINIv6NANOv15-v1/NANOAOD' || true

echo ""
echo "Next steps:"
echo "  1) Freeze first era Run2024D: Muon0 + Muon1 (PromptReco or MiniAODv6 parent)"
echo "  2) Pick matching DY MiniAODSIM campaign (140X_ → CMSSW_14_0_X; 150X_ → 15_0_X)"
echo "  3) dasgoclient -query='site dataset=<NAME>'"
echo "  4) Confirm MiniAOD (not Nano) and GT token in the processed-dataset name"
echo "  5) Golden JSON: /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_*_Golden.json"
echo "     (current stub: Cert_Collisions2024_378981_386951_Golden.json — TODO-VERIFY latest)"
echo "  6) brilcalc lumi -u /fb --normtag <current> -i Cert_....json --begin/--end (Run2024D runs)"
echo "  7) Freeze samples/data_muon_2024.txt + samples/sim_dy_m50_13p6.txt + conditions.md"
echo "  8) Confirm HLT Mass3p8 (+ optional Mass8) in the Run2024D menu → samples/hlt_paths_2024.txt"
