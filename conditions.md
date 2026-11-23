# Conditions snapshot (fill exact GT strings on first CRAB submit)

Do **not** hardcode stale global tags in production configs. Prefer autoCond aliases
in `python/*.py`; pin exact strings here on the day of the first successful smoke job.

| Item | Alias / stub value | Exact string (freeze later) | Date / notes |
| --- | --- | --- | --- |
| CMSSW release | `CMSSW_14_0_X` if dataset has `140X_`; `CMSSW_15_0_X` if `150X_` / MiniAODv6 | | Match token in DAS processed dataset |
| SCRAM_ARCH | `el8_amd64_gcc12` (14_0) — verify for 15_0 | | |
| Data GT | `auto:run3_data` / `auto:run3_data_prompt` | | PromptReco vs rereco |
| MC GT | `auto:phase1_2024_realistic` | e.g. `150X_mcRun3_2024_realistic_v2` **TODO-VERIFY** | From MiniAODSIM name |
| Data era (cmsDriver) | `Run3` | | |
| MC era | `Run3_2024` | | |
| First data era | **Run2024F or Run2024G** (plan default: mid-year) | | Freeze after DAS + JSON + lumi |
| Data DAS (PromptReco stubs) | see `samples/data_muon_2024.txt` | `/Muon{0,1}/Run2024F-PromptReco-v1/MINIAOD` **TODO-VERIFY** | Prefer Muon0+Muon1 |
| MC DAS (FxFx stub) | see `samples/sim_dy_m50_13p6.txt` | `/DYto2L-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM` **TODO-VERIFY** | PdmV name, not legacy DYJetsToLL |
| Golden JSON | `Cert_Collisions2024_*_Golden.json` | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json` **TODO-VERIFY latest** | samples/cert/ |
| Muon JSON (optional) | same Collisions24 dir | `Cert_Collisions2024_*_Muon.json` **TODO-VERIFY** | muon-only analyses |
| PU JSON | Collisions24 `PileUp/` | **TODO-VERIFY** filename for frozen eras | samples/cert/ |
| DeepJet loose WP | BTV 2024 correctionlib | **TODO-VERIFY** numeric cut — see `samples/deepjet_wp_2024.md` | Do not reuse Run 2 numbers |
| DeepJet JSON path | `/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/` | era subdir **TODO-VERIFY** | `btagging.json` / `deepJet_wp_values` |
| Baseline HLT | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` | confirm in era menu | `samples/hlt_paths_2024.txt` |
| Companion HLT | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8` | include in OR only if present **TODO-VERIFY** | |
| DY σ (M>50, 13.6 TeV) | XSDB / genXsecAnalyzer | **TODO-VERIFY** — do not reuse 6077.22 pb | |

## Lookup commands

```bash
# Samples
bash scripts/das_discover.sh

# GT aliases inside a release
python -c "from Configuration.AlCa.autoCond import autoCond; \
  print(autoCond['run3_data']); print(autoCond['phase1_2024_realistic'])"
```

Source: implementation plan §2–3; method doc §2.2–2.3; samples/ stubs filled 2026-11-23.
