# K0sAnalysisRun3 scaffold status (M0–M3 + analyzer ports)

**Date:** 2026-11-23  
**Workers:** scaffold `bc-265d0870-0e0c-59b8-a256-e1f8ca0d169c`; V0 port `bc-7f1255ab-c1f3-55e7-b57f-ee434d87b2b9`; Trigger/Lepton/Jet `bc-44f5edb1-be76-5660-85bc-e4405919c164`; cmsRun smoke docs `bc-8f7a2f29-bf08-59ec-958b-47c3ddd3a58c`; samples stubs `bc-9a1ce0b2-114f-5465-bc40-93e38dd4952a`; offline fitting/analysis/v0building `bc-4b344982-5a02-56fa-89c4-1a52974a70d2`; GitHub push/PR `bc-7846fe27-5713-52b8-8345-4ff9a13f0cb7`  
**Outcome:** Package pushed to GitHub. **Kalman `V0Analyzer` + lean Trigger / Lepton / Jet + genWeight/PU hooks** are real upstream ports. **Offline `fitting/`, `analysis/`, `v0building/` ported** (RooFit path; DisplacedV0 branch adaptations; AN sideband + low-Δ2D norm). Local **cmsRun/scram smoke path** documented (`docs/cmsrun-smoke-test.md`); VM has no CMSSW so build was not executed. **M2 sample/cert/HLT/DeepJet stubs filled with concrete 2024 DAS/JSON patterns** (full names marked `TODO-VERIFY`). **PR open:** https://github.com/lwang046/K0sAnalysisRun3/pull/1. HepTools untouched.

---

## Location (Context)

Context copy (source of truth during scaffold):

```text
/cursor/stores/self/code/K0sAnalysisRun3/
```

GitHub tree: `https://github.com/lwang046/K0sAnalysisRun3` (branch `cursor/push-context-package-0cb7` → PR #1). Repo `docs/` mirrors the method/plan/smoke/status docs below.

Canonical docs remain:

- `/cursor/stores/self/docs/displaced-track-efficiency-run3-2024.md`
- `/cursor/stores/self/docs/displaced-track-efficiency-implementation-plan.md`
- `/cursor/stores/self/docs/cmsrun-smoke-test.md`
- `/cursor/stores/self/preferences.md`

---

## Repo / PR

| Item | Status |
| --- | --- |
| Context tree | **`/cursor/stores/self/code/K0sAnalysisRun3/`** — M0–M3 + V0/Trigger/Lepton/Jet + offline fitting/analysis/v0building |
| Target GitHub | `https://github.com/lwang046/K0sAnalysisRun3` — **exists** |
| Branch | `cursor/push-context-package-0cb7` |
| PR URL | **https://github.com/lwang046/K0sAnalysisRun3/pull/1** |
| HepTools | Untouched |

### Push / PR (2026-11-23, worker `bc-7846fe27-5713-52b8-8345-4ff9a13f0cb7`)

- Copied Context package into repo root; added docs under `docs/`.
- Commit `6a7381b` on `cursor/push-context-package-0cb7`; pushed; opened PR #1.

### Prior create attempt (2026-11-23, worker `bc-05827a22-30d5-5f32-9788-a72f8c0ef676`)

Previously blocked by GitHub App permissions (`createRepository` / fork 403). Repo was created outside the agent; push/PR succeeded once the App had access.

---

## Milestone checklist

| Deliverable | Status | Notes |
| --- | --- | --- |
| **M0** plan defaults | Done | Locked in `preferences.md`; restated in package `README.md` |
| **M1** README + tree | Done | Attribution to AN-20-111 / LukaLambrecht/K0sAnalysis |
| **M2** samples / HLT / cert / conditions | **Concrete stubs** | Muon0/1 PromptReco C–I; DYto2L FxFx Summer24; Cert_…_378981_386951; Mass3p8; DeepJet lookup paths. Full DAS/WP still **TODO-VERIFY** on DAS/CVMFS |
| **M3** `ntuplizer/DisplacedV0` | **Analyzers ported; smoke docs ready** | V0 + Trigger + Lepton + Jet + genWeight/PU; plugin + cfi wired; local cmsRun path in `docs/cmsrun-smoke-test.md` (build not run — no CMSSW on VM) |
| Offline `fitting/` + `analysis/` | **Ported** | RooFit/TF1 path; Run3 bins + sideband + low-Δ2D norm |
| Offline `v0building/` AN cuts | **Ported + adapted** | `v0selections.py` + DisplacedV0-aware `v0builder.py` |
| GitHub PR | **Open** | https://github.com/lwang046/K0sAnalysisRun3/pull/1 |

---

## What was ported (Trigger / Lepton / Jet update)

**Upstream source:** https://github.com/LukaLambrecht/K0sAnalysis  
**Commit:** `2a132385aec7e15d1bbdfb038edf0534bb4855b8` (2024-08-20) — same family as V0Analyzer port

| File | Status |
| --- | --- |
| `interface/TriggerAnalyzer.h` + `src/TriggerAnalyzer.cc` | **Lean port** — configurable `hltPaths`, TriggerResults index/accept, `passDimuonHLT` OR |
| `interface/LeptonAnalyzer.h` + `src/LeptonAnalyzer.cc` | **Muon-only port** — medium/loose/tight ID, kinematics, IP, PF iso04 |
| `interface/JetAnalyzer.h` + `src/JetAnalyzer.cc` | **Lean port** — PUPPI jets, DeepFlavour→`Jet_btagDeepFlavB`, jetId (2018 tight placeholder) |
| `plugins/DisplacedV0Ntuple.{h,cc}` | Wired helpers; **genWeight + Pileup_nTrue** from GenEventInfo / pileupSummary |
| `python/displacedV0_cfi.py` | `hltPaths`, `genEventInfo`, `pileupInfo` InputTags |
| `BuildFile.xml` | Added `SimDataFormats/{GeneratorProducts,PileupSummaryInfo}` |
| `interface/V0Analyzer.h` + `src/V0Analyzer.cc` | Unchanged (prior Kalman port) |

**Adaptations vs upstream (lean DY+V0):**

- Include/package rename: `heavyNeutrino/multilep` → `DisplacedV0`; `multilep*` → `DisplacedV0Ntuple*`
- **Trigger:** dropped year-by-year HNL cocktail, MET filters, Ele32 emulation, trigger objects / prescales; HLT list from PSet (baseline `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`)
- **Lepton:** muons only; dropped electrons/taus/Rochester/lepton MVAs/EffectiveAreas. Offline applies exactly-2 medium, \(p_T>30/25\), \(|m_{\mu\mu}-m_Z|<10\,\mathrm{GeV}\)
- **Jet:** single collection (`slimmedJetsPuppi`); DeepJet score stored; WP veto offline (`samples/deepjet_wp_2024.md`). Dropped JEC source maps, MET, PF-candidate dump. Jet ID = upstream 2018 tight/tightLepVeto as Run3 placeholder
- **Weights:** genWeight + true PU interactions only; full LHE/PS weight histograms still deferred
- Attribution headers cite upstream path + commit SHA

**M2 samples fill (2026-11-23, worker `bc-9a1ce0b2-114f-5465-bc40-93e38dd4952a`):**

| Path | What was filled |
| --- | --- |
| `samples/data_muon_2024.txt` | `/Muon{0,1}/Run2024[C–I]-PromptReco-v1/MINIAOD` stubs; DoubleMuon noted likely empty; all **TODO-VERIFY** |
| `samples/sim_dy_m50_13p6.txt` | PdmV `DYto2L-2Jets_Bin-MLL-50_…_amcatnloFXFX` + MiniAODv6/`150X_` template; legacy `DYJetsToLL` query-only |
| `samples/hlt_paths_2024.txt` | Baseline `HLT_Mu17_…_Mass3p8`; companion Mass8 TODO-VERIFY; bias-path exclusions |
| `samples/cert/README.md` | `Cert_Collisions2024_378981_386951_Golden.json` EOS + web pointers; PU/lumi |
| `samples/deepjet_wp_2024.md` | Loose WP mistag def; CVMFS jsonpog + DP-2024/025 lookup; numeric cut **TODO-VERIFY** |
| `conditions.md` | Snapshot table with concrete stub values + freeze columns |
| `scripts/das_discover.sh` | Muon/DoubleMuon + DYto2L/legacy/fallback queries |
| `ntuplizer/.../crab_{data_2024,mc_dy}.py` | Point at Run2024F Muon0 + DYto2L MiniAODv6 stubs |

## What was ported (offline fitting / analysis / v0building)

**Worker:** `bc-4b344982-5a02-56fa-89c4-1a52974a70d2`  
**Upstream source:** https://github.com/LukaLambrecht/K0sAnalysis @ `2a132385aec7e15d1bbdfb038edf0534bb4855b8`  
**Preference:** RooFit / upstream ROOT TF1 `fitting/` (not scipy/iminuit)

### Ported as-is (with attribution / 13.6 TeV labels)

| Path | Notes |
| --- | --- |
| `fitting/count_peak.py`, `fitinvmass*.py`, `testing/`, `variables/` | Sideband poly + double-Gaussian; peak count modes |
| `analysis/mcvsdata_{fill,getfiles,submit,submit_all}.py`, `runtest.py`, `v0variableplots/` | \(C(\Delta_{2D})\) fill/submit + control plots helpers |
| `v0building/v0selections.py` | AN §6 `selection_legacy` (hits, \(p_T\), \(\chi^2\), DCA, pointing) |
| `v0building/merge*.py`, `v0builder_submit.py` | Merge / batch helpers |
| `tools/fittools.py` (+ job/lumi helpers) | Minimal deps so fitting imports resolve |
| `plotting/plotfit.py`, `plottools.py`, `mcvsdataplotter*.py`, … | Minimal plot deps |

### Adapted for DisplacedV0 / Run3

| Change | Detail |
| --- | --- |
| `v0building/v0builder.py` | Reads `events` tree; maps `run`/`luminosityBlock`/`event`, `genWeight`→`_weight`, `Pileup_nTrue`→`_nTrueInt`; optional `--apply-dy-selection` (`passDimuonHLT`, 2 medium muons \(30/25\), \(\|m_{\mu\mu}-m_Z\|<10\), `Jet_btagDeepFlavB` veto); builds `_nimloth_*` / `_celeborn_*` from `Muon_*`/`Jet_*`; keeps laurelin/telperion `_RPV`/`_mass` schema; still accepts upstream `blackJackAndHookers` |
| `analysis/config_ksvars*.py`, `config_ks2dvars*.py`, `config_lavars.py` | Method §2.6 Phase-1 \(\Delta_{2D}\) bins; low-\(\Delta_{2D}\) `normrange` `[0, 2]` cm; sideband `_mass` windows unchanged |
| `analysis/config_controlvars.py` | DY controls from adapted v0building trees; 13.6 TeV era tag |
| `analysis/mcvsdata_fill.py` | Soft PU import; default `--nopileup` until Collisions24 profiles; `--weightvar`/`--ntrueintvar` |
| `fitting/fitinvmass.py` | Explicit `--weightvar`/`--hcounter` defaults (`_weight`, `hCounter`); 13.6 TeV labels |
| `fitting/variables/variable_*_rpv.json`, `variable_norm_rpv.json` | Run3 \(\Delta_{2D}\) + low-\(\Delta_{2D}\) norm bins |
| `reweighting/pileup/pileupreweighter.py` | Stub (`AVAILABLE=False`) so imports do not hard-fail |

**Kept AN-20-111 flow:** sideband linear bkg → subtract under peak → normalize MC in low-\(\Delta_{2D}\) → \(C_i = N_i^{\mathrm{data}}/(k N_i^{\mathrm{MC}})\).

**Still stub / deferred:**

- Full `reweighting/pileup` with Collisions24 profiles; `skimming/` DY skim (partially covered by `v0builder --apply-dy-selection`)
- Numeric DeepJet WP freeze; live DAS confirmation; CRAB smoke under real CMSSW
- Rochester muon momentum corrections; MET filters; HLT prescales
- Full LHE/PS weight counters (`LheAnalyzer` bulk)
- Run3 JetID re-validation vs BTV 2024 recipe
- **Executing** `cmsrel` / `scram b` / `cmsRun` (VM has no CMSSW) — instructions + cfg fixes delivered; first green build still on lxplus/CMSLPC

---

## Key files

| Path | Role |
| --- | --- |
| `/cursor/stores/self/docs/cmsrun-smoke-test.md` | Local cmsRun / scram smoke path (M3) |
| `/cursor/stores/self/code/K0sAnalysisRun3/README.md` | Package entry + M0 decisions |
| `/cursor/stores/self/code/K0sAnalysisRun3/conditions.md` | GT / era / DeepJet / HLT snapshot table |
| `/cursor/stores/self/code/K0sAnalysisRun3/samples/` | Data/MC DAS stubs, HLT, cert pointers |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/interface/V0Analyzer.h` | Ported V0 helper API |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/src/V0Analyzer.cc` | Ported Kalman V0 body |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/interface/{Trigger,Lepton,Jet}Analyzer.h` | Ported helper APIs |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/src/{Trigger,Lepton,Jet}Analyzer.cc` | Ported helper bodies |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/plugins/DisplacedV0Ntuple.{h,cc}` | EDAnalyzer plugin |
| `/cursor/stores/self/code/K0sAnalysisRun3/ntuplizer/DisplacedV0/python/displacedV0_cfi.py` | cfi + HLT list + MC weight tags |
| `/cursor/stores/self/code/K0sAnalysisRun3/fitting/fitinvmass.py` | RooFit/TF1 sideband fits (ported) |
| `/cursor/stores/self/code/K0sAnalysisRun3/fitting/count_peak.py` | Peak yield after sideband subtract |
| `/cursor/stores/self/code/K0sAnalysisRun3/analysis/config_ksvars.py` | Run3 Δ2D bins + sideband + low-Δ2D norm |
| `/cursor/stores/self/code/K0sAnalysisRun3/analysis/mcvsdata_fill.py` | \(C(\Delta_{2D})\) fill (ported + PU soft-skip) |
| `/cursor/stores/self/code/K0sAnalysisRun3/v0building/v0builder.py` | DisplacedV0→laurelin; AN §5/§6 |
| `/cursor/stores/self/code/K0sAnalysisRun3/v0building/v0selections.py` | AN §6 `selection_legacy` |

---

## Run3 API / compile risks (before first `scram b`)

Not verified in this environment (no CMSSW). Watch on lxplus/`CMSSW_14_0_X`:

1. **`OAEParametrizedMagneticField`** — include is `MagneticField/ParametrizedEngine/src/OAEParametrizedMagneticField.h` (upstream path). Some releases prefer `interface/` or EventSetup `MagneticField` via `ESGetToken`; hard-coded `"3_8T"` remains correct for Run 3 but is not the modern ES pattern.
2. **`reco::TransientTrack(track, MagneticField*)`** — still available; prefer TransientTrackBuilder from ES if MagField ctor is removed or deprecated in 14_0/15_0.
3. **`pat::PackedCandidate::bestTrack()` / `hasTrackDetails()`** — still MiniAOD API; confirm product labels (`packedPFCandidates`, `lostTracks`) for the chosen MiniAOD campaign.
4. **`TMatrixDSym::EigenVectors`** in `fixTrackCovariance` — TrackingPOG recipe; rare NaN/inf handling kept from upstream.
5. **DeepFlavour discriminator labels** — `pfDeepFlavourJetTags:probb/bb/lepb` as upstream; confirm MiniAOD campaign still uses these names (vs ParticleNet rename).
6. **Jet ID** — 2018 UL tight used as placeholder; freeze Run3 JetID before M5 skim.
7. **`slimmedAddPileupInfo`** — standard MiniAOD PU tag; confirm for Summer24 campaign.
8. **Library ↔ plugin header** — helpers include `plugins/DisplacedV0Ntuple.h` (same pattern as upstream `multilep.h`); first `scram b` should confirm plugin/lib link order.
9. **No `cmsrel` / `scram b` / `cmsRun` on this VM** — runnable smoke path documented in `/cursor/stores/self/docs/cmsrun-smoke-test.md`; execute on a CMSSW host for M3 exit.

---

## How to push to GitHub later (when connect works)

**Prerequisite:** create empty public repo `lwang046/K0sAnalysisRun3` (UI or personal PAT) **and** grant the Cursor GitHub App access to it. The cloud agent installation currently sees only `lwang046/HepTools` and cannot `createRepository` / fork.

Do **not** push this tree into HepTools.

```bash
# On a machine with write access to lwang046/K0sAnalysisRun3:
cd /cursor/stores/self/code/K0sAnalysisRun3   # or copy the tree out of Context first
git init
git checkout -b main
git add -A
git commit -m "M0–M3 Run3 displaced-V0 scaffold + V0/Trigger/Lepton/Jet ports"

git remote add origin git@github.com:lwang046/K0sAnalysisRun3.git
git push -u origin main
```

### Prior GitHub App errors (for reference)

Earlier attempt failed with:

- GraphQL `createRepository`: Resource not accessible by integration  
- REST `/user/repos`: 403 needing `administration=write; repository_creation=write`  
- Fork `LukaLambrecht/K0sAnalysis`: 403  
- Installation repos: only `lwang046/HepTools`

---

## Intentionally not done

- No push / PR (create + fork both failed with App permissions; stopped per instructions)  
- No commits to `lwang046/HepTools`  
- No HepTools modifications  
- No CMSSW build / cmsRun execution in this environment (instructions + one-file cfg smoke fixes landed; see `docs/cmsrun-smoke-test.md`)
