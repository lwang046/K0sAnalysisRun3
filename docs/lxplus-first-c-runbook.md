# lxplus runbook — first \(C(\Delta_{2D})\) (Run2024D + Summer24 DY)

**Audience:** Long on lxplus / CMSLPC (CVMFS + CMS VO + CRAB + ROOT).  
**Companion:** [`first-c-delta2d-recipe.md`](first-c-delta2d-recipe.md) (physics defaults + offline §0).  
**Repo:** `https://github.com/lwang046/K0sAnalysisRun3` — use **`main`** (CRAB prep [#4](https://github.com/lwang046/K0sAnalysisRun3/pull/4) + VarParsing `outputFile` fix [#5](https://github.com/lwang046/K0sAnalysisRun3/pull/5)).

---

## What already completed offline (Project VM — 2026-11-24 Asia/Shanghai)

| Step | Result |
| --- | --- |
| Checkout `main` @ `55743ff` (#4 + #5) | Done |
| `python3 scripts/make_dummy_displacedv0_ntuple.py -o /tmp/dummy_displacedv0.root` | **Passed** — 40 events, 54 V0s |
| `v0builder.py … --apply-dy-selection --no-bveto --nevents 50` | **Passed** — 13 events after DY; laurelin 12 Ks with `_RPV`, `_mass`, `_weight` |
| Live `dasgoclient` / golden / brilcalc / DeepJet CVMFS | **Not run** (no CMS VO / CVMFS) |
| `cmsrel` / `scram` / `cmsRun` / `crab submit` | **Not run** (no CMSSW) |
| Sideband fits / `mcvsdata_fill` / SF on real stats | **Not run** (need ntuples + ROOT) |

**Do not claim** crab or cmsRun succeeded from the Project VM.

Production psets on `main` set `options.outputFile` without re-registering (PR #5). No local VarParsing patch needed.

---

## Frozen stubs (use as-is; mark TODO-VERIFY until you confirm)

| Item | Stub value | Verify |
| --- | --- | --- |
| Era | **Run2024D** | — |
| Data DAS | `/Muon{0,1}/Run2024D-PromptReco-v1/MINIAOD` | **TODO-VERIFY** DAS |
| MC DAS | `/DYto2L-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM` | **TODO-VERIFY** DAS |
| HLT | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` | menu |
| DeepJet loose WP | `0.0494` | **TODO-VERIFY** BTV JSON |
| Golden JSON | `Cert_Collisions2024_378981_386951_Golden.json` | **TODO-VERIFY** latest |
| Golden EOS | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json` | **TODO-VERIFY** |
| CMSSW | `CMSSW_14_0_19` if `140X_`; **`CMSSW_15_0_X`** if MiniAODv6 / `150X_` | match DAS token |
| SCRAM_ARCH | `el8_amd64_gcc12` (14_0) — verify for 15_0 | |
| `CRAB_STORAGE_SITE` | **your** writeable T2 — never invent in git | set on lxplus |
| Δ2D bins / norm | recipe table; `normrange=[0,2]` cm | — |

Replace `/path/to/K0sAnalysisRun3` and `/eos/...` below with your clone and EOS area.

---

## Ordered lxplus session

### A. Clone + identity

```bash
git clone https://github.com/lwang046/K0sAnalysisRun3.git
cd K0sAnalysisRun3
git checkout main && git pull   # includes #4 CRAB prep + #5 VarParsing fix
export REPO=$PWD
```

### B. DAS freeze (**TODO-VERIFY** — required before CRAB)

```bash
cd $REPO
bash scripts/das_discover.sh
dasgoclient -query='dataset=/Muon*/Run2024D*/MINIAOD' | sort
dasgoclient -query='parent dataset=/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD'
dasgoclient -query='parent dataset=/Muon1/Run2024D-MINIv6NANOv15-v1/NANOAOD'
dasgoclient -query='dataset=/DYto2L*13p6TeV*amcatnloFXFX*/Run*2024*MiniAOD*/MINIAODSIM' | sort
```

Freeze confirmed strings into `samples/data_muon_2024.txt`, `samples/sim_dy_m50_13p6.txt`, and `conditions.md`.  
If PromptReco MiniAOD is gone, use the MiniAODv6 **parent** of the NanoAOD datasets above — update `ntuplizer/K0sAnalysis/DisplacedV0/test/crab_common.py` `DATA_DAS` / `MC_DAS_DY` to match.

### C. Golden / PU / brilcalc (**TODO-VERIFY**)

```bash
ls /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_*_Golden.json
# Prefer latest that covers Run2024D; record filename + download date in conditions.md
export GOLDEN=/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json

# Run2024D run bounds: OMS / DQM / PdmV — then:
# brilcalc lumi -u /fb --normtag <current_normtag> -i $GOLDEN --begin <D_start> --end <D_end>
# Record L(/fb) in conditions.md and analysis/example_input_run2024d.json

ls /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/PileUp/
# Wire PU later; fill path may use --nopileup until ready
```

Update `crab_common.py` `GOLDEN_LUMIMASK` if the golden filename changed.

### D. DeepJet loose WP (**TODO-VERIFY**)

```bash
# On CVMFS (path era subdir TODO-VERIFY):
# /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/
# Read deepJet_wp_values / btagging.json for 2024 loose; replace 0.0494
export DJWP=0.0494   # placeholder until verified — see samples/deepjet_wp_2024.md
# Record verified cut in conditions.md
```

### E. cmsrel / scram / cmsRun smoke (M3)

Match release to the **frozen** MiniAOD GT token (`140X_` → 14_0; `150X_` → 15_0):

```bash
export SCRAM_ARCH=el8_amd64_gcc12   # verify for chosen release
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_14_0_19                 # or CMSSW_15_0_X if MiniAODv6 / 150X_
cd CMSSW_14_0_19/src && cmsenv
# Preferred symlink (Subsystem directory). Do NOT link bare DisplacedV0 at src/.
ln -s $REPO/ntuplizer/K0sAnalysis K0sAnalysis   # → src/K0sAnalysis/DisplacedV0
# Verify before scram: test -d K0sAnalysis/DisplacedV0/plugins && ls K0sAnalysis/DisplacedV0/BuildFile.xml
# Confirm no flat leftover: test ! -e DisplacedV0 || echo 'REMOVE flat src/DisplacedV0'
scram b -j8

# One file each (after DAS freeze):
dasgoclient -query='file dataset=/Muon0/Run2024D-PromptReco-v1/MINIAOD' | head
# xrdcp root://cms-xrd-global.cern.ch//store/... data_one.root
dasgoclient -query='file dataset=<FROZEN_DY_DAS>' | head
# xrdcp … dy_one.root

cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:$PWD/data_one.root maxEvents=200
cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:$PWD/dy_one.root maxEvents=200
# Optional: useESMagneticField=True after MagField_cff loads (see docs/cmsrun-smoke-test.md)
# Optional: enableDimuonPreFilter=False to debug without AN §5 Path filter
```

**Exit:** tree `displacedV0Ntuple/events`; `_V0Type==1` mass near 0.498. Pin exact release + GT in `conditions.md`.

### F. CRAB smoke → full (M4)

From `$CMSSW_BASE/src` after green smoke (`K0sAnalysis` still linked):

```bash
# REQUIRED — your writeable site (example only; do not invent a T2 in git):
export CRAB_STORAGE_SITE=T2_CH_CERN   # replace with *your* site

# Smoke first:
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024_smoke.py   # Muon0, totalUnits=20
crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy_smoke.py        # DY, totalUnits=2
# crab status -d <workArea>/<request> until done; check one output ROOT

# Full:
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024.py          # Muon0
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024_muon1.py    # Muon1
crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy.py
```

| Config | requestName / outputDatasetTag | Job outputFiles |
| --- | --- | --- |
| Muon0 | `DisplacedV0_Muon0_Run2024D` | `DisplacedV0_Muon0_Run2024D.root` |
| Muon1 | `DisplacedV0_Muon1_Run2024D` | `DisplacedV0_Muon1_Run2024D.root` |
| DY | `DisplacedV0_DY_Summer24` | `DisplacedV0_DY_Summer24.root` |

Smoke appends `_smoke` to `requestName` only. After hadd/merge on EOS, point v0building at the merged files.

### G. v0building

```bash
cd $REPO/v0building
# DJWP from §D (still TODO-VERIFY until CVMFS lookup done)
python3 v0builder.py \
  -i /eos/.../DisplacedV0_Muon0_Run2024D.root \
  -o /eos/.../v0sel_data_Muon0_Run2024D.root \
  --apply-dy-selection --deepjet-loose-wp $DJWP --selection legacy

python3 v0builder.py \
  -i /eos/.../DisplacedV0_Muon1_Run2024D.root \
  -o /eos/.../v0sel_data_Muon1_Run2024D.root \
  --apply-dy-selection --deepjet-loose-wp $DJWP --selection legacy
# hadd / merge Muon0+Muon1 → v0sel_data_Run2024D.root as needed

python3 v0builder.py \
  -i /eos/.../DisplacedV0_DY_Summer24.root \
  -o /eos/.../v0sel_dy_Summer24.root \
  --apply-dy-selection --deepjet-loose-wp $DJWP --selection legacy
```

Trees: `nimloth` / `celeborn` / `laurelin` / `telperion` with `_RPV`, `_mass`, `_weight`.

### H. Sideband fits (M6) — needs ROOT/PyROOT

```bash
cd $REPO
# Gallery / mass plots (RooFit preference locked):
python3 fitting/fitinvmass.py \
  -i /eos/.../v0sel_data_Run2024D.root \
  -t laurelin \
  -v fitting/variables/variable_ks_invmass.json \
  -o /eos/.../fit_mass_data_Run2024D.root \
  --isdata --doplot --show_sideband --polydegree 1

python3 fitting/fitinvmass.py \
  -i /eos/.../v0sel_dy_Summer24.root \
  -t laurelin \
  -v fitting/variables/variable_ks_invmass.json \
  -o /eos/.../fit_mass_dy_Summer24.root \
  --doplot --show_sideband --polydegree 1 \
  --xsection <TODO-VERIFY_XS> --lumi <TODO-VERIFY_LUMI>
```

`fitting/count_peak.py` is a **library** (sideband subtract / hybrid) used by the fill path — not a standalone CLI. Mass-fit gallery is an M6 exit criterion.

### I. Fill \(C(\Delta_{2D})\) (M7)

```bash
cd $REPO/analysis
# Edit example_input_run2024d.json: real v0sel paths.
# Luminosity pb^-1 (default Muon 7703.3; alt Golden×D 7914.0) — see example_input_run2024d.md
# DY xsection still TODO-VERIFY — override with --mc-xsection when XSDB/genXsec ready.
# Full-sample Σw: --mc-sumweights (existing slim CRAB has no pre-filter hCounter).

python3 mcvsdata_fill.py \
  -i /afs/.../results/input_run2024d_afs.json \
  -t laurelin \
  -v ../fitting/variables/variable_ks_rpv.json \
  -o /afs/.../results/C_delta2D_Run2024D.root \
  --bkgmode sideband \
  --sidevariable ../fitting/variables/variable_ks_invmass.json \
  --normmode range \
  --normvariable ../fitting/variables/variable_norm_rpv.json \
  --norm-stability-uppers 1.0,3.0 \
  --peak-halfwidth-frac 0.25 \
  --weightvar _weight \
  --ntrueintvar _nTrueInt \
  --nopileup \
  --data-lumi 7703.3 --mc-lumi 7703.3 \
  --mc-xsection 2094.2 \
  --mc-sumweights <FULL_SAMPLE_SUMW_OR_OMIT>
```

Config: `config_ksvars.py` (Δ2D bins, sideband `_mass`, `normrange=[0,2]`).
Writes `norm_scale`, `normshared_up/down`, optional `norm_scale_alt_upper_*` (CDTE-25).
CLI overrides: `--data-lumi`, `--mc-lumi`, `--mc-xsection`, `--mc-sumweights` (also JSON keys `luminosity` / `xsection` / `sumweights`).


### J. SF export

```bash
cd $REPO
python3 scripts/make_sf_json.py \
  -i /afs/.../results/C_delta2D_Run2024D.root \
  -o /afs/.../results/C_delta2D_Run2024D.json \
  --era Run2024D \
  --correctionlib
# Forms C = data/MC from *_nominal TH1s; optional .correctionlib.json
# Record era + JSON path in conditions.md
```

### K. Validation (before freezing v1 SF)

Plan §6 items 1–8: DY controls, Ks mass, low-Δ2D \(C\approx1\), pixel-layer features, norm ±1 bin, sideband degree, era/PU checks as stats allow.

---

## Checklist (copy into session notes)

- [ ] DAS strings frozen (not stubs) in `samples/*.txt` + `conditions.md` + `crab_common.py`
- [ ] Golden + Run2024D \(\mathcal{L}\) from brilcalc; PU path noted
- [ ] DeepJet WP verified on CVMFS (not `0.0494` placeholder)
- [ ] On `main` with #5 (VarParsing `outputFile` set, not re-registered)
- [ ] `scram b` + data/MC one-file `cmsRun` green
- [ ] `export CRAB_STORAGE_SITE=…` set to **your** site
- [ ] CRAB smoke green → full Muon0/1 + DY
- [ ] v0builder DY+legacy on data+MC
- [ ] Mass-fit gallery; `mcvsdata_fill` → `C_delta2D_Run2024D.root`
- [ ] SF JSON + `conditions.md` updated

---

## Related

- Recipe: `docs/first-c-delta2d-recipe.md`
- Smoke detail: `docs/cmsrun-smoke-test.md`
- **Run 3 (2024) audit checklist:** [`run3-2024-audit-checklist.md`](run3-2024-audit-checklist.md)
- CRAB table: `ntuplizer/K0sAnalysis/DisplacedV0/test/README.md`
- Status: `docs/k0s-run3-scaffold-status.md`
- Method / plan: `docs/displaced-track-efficiency-run3-2024.md`, `docs/displaced-track-efficiency-implementation-plan.md`
