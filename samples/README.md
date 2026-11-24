# Samples

Concrete **2024** DAS strings for Run2024D PromptReco + matching DY MiniAODSIM.

| File | Role |
| --- | --- |
| `data_muon_2024.txt` | **Frozen** Muon0/Muon1 Run2024D PromptReco-v1 (+ other-era stubs) |
| `sim_dy_m50_13p6.txt` | Production inclusive **TODO-VERIFY** (0 files last check) + **smoke-only** PTLL-100 |
| `hlt_paths_2024.txt` | Baseline `Mass3p8`; optional `Mass8`; exclusions |
| `cert/README.md` | `Cert_Collisions2024_378981_386951_Golden.json` + PU / lumi pointers |
| `deepjet_wp_2024.md` | Loose WP placeholder + CVMFS/BTV lookup paths |

**Data (FROZEN):** `/Muon{0,1}/Run2024D-PromptReco-v1/MINIAOD` after lxplus M3.

**DY production (TODO-VERIFY):** inclusive `Bin-MLL-50` …`v2-v2` — exists but **0 files** (2026-11-24). Re-query on lxplus before first-C; do not silently use PTLL-100 vs inclusive data (`v0builder` has no pT(ℓℓ) cut).

**DY smoke-only:** `Bin-MLL-50-PTLL-100` …`v2-v3` → `crab_common.MC_DAS_DY_SMOKE` / `crab_mc_dy_smoke.py` only.

Build MiniAODv6 with `CMSSW_15_0_22` + `el9_amd64_gcc12`. Do not invent `CRAB_STORAGE_SITE` / T2 in git.
