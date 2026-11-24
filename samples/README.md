# Samples

Concrete **2024** DAS strings for Run2024D PromptReco + matching DY MiniAODSIM.

| File | Role |
| --- | --- |
| `data_muon_2024.txt` | **Frozen** Muon0/Muon1 Run2024D PromptReco-v1 (+ other-era stubs) |
| `sim_dy_m50_13p6.txt` | **Frozen** inclusive `DYto2Mu` MLL-50 + **smoke-only** PTLL-100 DYto2L |
| `hlt_paths_2024.txt` | Baseline `Mass3p8`; optional `Mass8`; exclusions |
| `cert/README.md` | `Cert_Collisions2024_378981_386951_Golden.json` + PU / lumi pointers |
| `deepjet_wp_2024.md` | Loose WP placeholder + CVMFS/BTV lookup paths |

**Data (FROZEN):** `/Muon{0,1}/Run2024D-PromptReco-v1/MINIAOD` after lxplus M3.

**DY production (FROZEN):** `/DYto2Mu-2Jets_Bin-MLL-50_…/RunIII2024Summer24MiniAODv6-150X_…-v6/MINIAODSIM` — inclusive (no PTLL); 13462 files. Combined `DYto2L` Bin-MLL-50 Summer24 still **0 files** (do not use).

**DY smoke-only:** `DYto2L` `Bin-MLL-50-PTLL-100` …`v2-v3` → `MC_DAS_DY_SMOKE` / `crab_mc_dy_smoke.py` only.

Build MiniAODv6 with `CMSSW_15_0_22` + `el9_amd64_gcc12`. Do not invent `CRAB_STORAGE_SITE` / T2 in git.
