# Conditions snapshot (fill exact GT strings on first CRAB submit)

Do **not** hardcode stale global tags in production configs. Prefer autoCond aliases
in `python/*.py`; pin exact strings here on the day of the first successful smoke job.

| Item | Alias / stub value | Exact string (freeze later) | Date / notes |
| --- | --- | --- | --- |
| CMSSW release | `CMSSW_15_0_X` for MiniAODv6 / `150X_` | **`CMSSW_15_0_22`** | FROZEN for M3 smoke 2026-11-24 |
| SCRAM_ARCH | `el9_amd64_gcc12` on lxplus9 (RHEL9) | **`el9_amd64_gcc12`** | Do not build `el8_*` on bare lxplus9 |
| Data GT | `auto:run3_data` / `auto:run3_data_prompt` | | PromptReco vs rereco |
| MC GT | `auto:phase1_2024_realistic` | e.g. `150X_mcRun3_2024_realistic_v2` | From MiniAODSIM name |
| Data era (cmsDriver) | `Run3` | | |
| MC era | `Run3_2024` | | |
| **First data era** | **Run2024D** | PromptReco `/Muon{0,1}/Run2024D-PromptReco-v1/MINIAOD` | **FROZEN** 2026-11-24 |
| Data DAS | see `samples/data_muon_2024.txt` | `/Muon0/Run2024D-PromptReco-v1/MINIAOD` + Muon1 sibling | **FROZEN** — 1978 files (Muon0); 200-evt cmsRun OK |
| MC DAS production | see `samples/sim_dy_m50_13p6.txt` → `crab_common.MC_DAS_DY` | `/DYto2L-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM` | **TODO-VERIFY** — inclusive target for first-C; lxplus 2026-11-24: **0 files**. Cloud VM DAS = 401 (no VO). Do **not** use PTLL-100 as production default. |
| MC DAS smoke-only | `crab_common.MC_DAS_DY_SMOKE` | `/DYto2L-2Jets_Bin-MLL-50-PTLL-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v3/MINIAODSIM` | Populated (7346 files); M3 cmsRun OK. Gen pT(ℓℓ)>100 ≠ inclusive data — **smoke / CRAB plumbing only**. |
| Golden JSON | `Cert_Collisions2024_*_Golden.json` | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json` **TODO-VERIFY latest** | samples/cert/ |
| Muon JSON (optional) | same Collisions24 dir | `Cert_Collisions2024_*_Muon.json` **TODO-VERIFY** | muon-only analyses |
| PU JSON | Collisions24 `PileUp/` | **TODO-VERIFY** filename for Run2024D | samples/cert/; offline `--nopileup` until wired |
| DeepJet loose WP | BTV 2024 correctionlib | Placeholder **`0.0494`** — **TODO-VERIFY** on CVMFS (`samples/deepjet_wp_2024.md`) | Do not reuse Run 2 numbers as final |
| DeepJet JSON path | `/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/` | era subdir **TODO-VERIFY** | `btagging.json` / `deepJet_wp_values` |
| Baseline HLT | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` | confirm in Run2024D menu | `samples/hlt_paths_2024.txt` |
| Companion HLT | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` | include in OR only if present **TODO-VERIFY** | |
| MagField mode | `useESMagneticField=False` (OAE `3_8T` default) | Set `True` after MagField_cff + TransientTrackBuilder smoke (`esConsumes` MagField + TTBuilder) | `displacedV0_cfi.py` / docs/cmsrun-smoke-test.md |
| Dimuon Path filter | `enableDimuonPreFilter=True` (2 medium, pT>30/25, \|mμμ−mZ\|<10) | Set `False` to debug without AN §5 pre-filter | production + smoke cfgs |
| Package path | `$CMSSW_BASE/src/K0sAnalysis/DisplacedV0` | Symlink `ntuplizer/K0sAnalysis` → `src/K0sAnalysis` | docs/cmsrun-smoke-test.md |
| DY σ (M>50, 13.6 TeV) | XSDB / genXsecAnalyzer | **TODO-VERIFY** — do not reuse 6077.22 pb; match chosen sample (inclusive vs PTLL bin) | |
| Δ2D bins / norm | method §2.6 / `analysis/config_ksvars.py` | bins `[0,1,2,3,5,7,11,16,22,30,40,60,90,120]` cm; `normrange=[0,2]` | Wired to laurelin `_RPV`; cannot fix DY phase-space mismatch |
| `CRAB_STORAGE_SITE` | set on lxplus only | — | **Never invent a T2 in git** |

## Lookup commands

```bash
# Samples
bash scripts/das_discover.sh
dasgoclient -query='dataset=/Muon*/Run2024D*/MINIAOD' | sort
dasgoclient -query='parent dataset=/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD'
# Inclusive DY with files (required before first-C production):
dasgoclient -query='dataset=/DYto2L-2Jets_Bin-MLL-50*_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6*/MINIAODSIM' | sort

# GT aliases inside a release
python -c "from Configuration.AlCa.autoCond import autoCond; \
  print(autoCond['run3_data']); print(autoCond['phase1_2024_realistic'])"
```

Source: implementation plan §2–3; method doc §2.2–2.3; M2 freeze 2026-11-23; M3 smoke 2026-11-24; **Codex P1 on #13** — demote PTLL-100 to smoke-only; production MC remains TODO-VERIFY inclusive.
