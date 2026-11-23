# Samples (M2)

Concrete **2024 stubs** for one PromptReco era + matching DY MiniAODSIM.
Names follow published DAS / PdmV patterns; every full dataset string is
**TODO-VERIFY** with `scripts/das_discover.sh` before CRAB.

| File | Role |
| --- | --- |
| `data_muon_2024.txt` | Muon0/Muon1 MiniAOD stubs (PromptReco C–I; DoubleMuon noted as likely empty) |
| `sim_dy_m50_13p6.txt` | `DYto2L` 13p6 TeV FxFx MiniAODSIM stubs (+ legacy DYJetsToLL query) |
| `hlt_paths_2024.txt` | Baseline `Mass3p8`; optional `Mass8`; exclusions |
| `cert/README.md` | `Cert_Collisions2024_378981_386951_Golden.json` + PU / lumi pointers |
| `deepjet_wp_2024.md` | Loose WP placeholder + CVMFS/BTV lookup paths |

Prefer MiniAOD (not Nano) so `lostTracks` remain available.
Pin verified names + GT + JSON date in `../conditions.md` when freezing.
