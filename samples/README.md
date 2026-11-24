# Samples

Concrete **2024** DAS strings for Run2024D PromptReco + matching DY MiniAODSIM.
Data + DY frozen after lxplus M3 smoke (2026-11-24 Asia/Shanghai).

| File | Role |
| --- | --- |
| `data_muon_2024.txt` | **Frozen** Muon0/Muon1 Run2024D PromptReco-v1 (+ other-era stubs) |
| `sim_dy_m50_13p6.txt` | **Frozen** `Bin-MLL-50-PTLL-100` Summer24 MiniAODv6 (inclusive `Bin-MLL-50` stub empty) |
| `hlt_paths_2024.txt` | Baseline `Mass3p8`; optional `Mass8`; exclusions |
| `cert/README.md` | `Cert_Collisions2024_378981_386951_Golden.json` + PU / lumi pointers |
| `deepjet_wp_2024.md` | Loose WP placeholder + CVMFS/BTV lookup paths |

**Freeze notes (M3):** inclusive `/DYto2L-2Jets_Bin-MLL-50_…/…v2-v2/MINIAODSIM` has **0 files** on DAS; use PTLL-100 `…v2-v3`. Build with `CMSSW_15_0_22` + `el9_amd64_gcc12`. Do not invent `CRAB_STORAGE_SITE` / T2 in git.

Prefer MiniAOD (not Nano) so `lostTracks` remain available.
Pin verified names + GT + JSON date in `../conditions.md`.
