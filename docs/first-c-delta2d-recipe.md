# First \(C(\Delta_{2D})\) recipe — Run2024D + Summer24 DY

Ordered commands for the first data/MC calibration factor on **one 2024 era**
(**Run2024D**) plus matching Summer24 DY MiniAODSIM. Uses existing scripts in
this repo. Physics method: [`displaced-track-efficiency-run3-2024.md`](displaced-track-efficiency-run3-2024.md).

**Host:** steps 1–4 need lxplus / CMSLPC (CVMFS + CMS VO + CRAB). Steps 5–8
run offline with ROOT/PyROOT/uproot once ntuples exist (or use the dummy
fixture dry-run in §0).

---

## Frozen analysis defaults (DisplacedV0 branch names)

| Setting | Value | Where |
| --- | --- | --- |
| First era | **Run2024D** | `samples/data_muon_2024.txt`, `conditions.md` |
| Data DAS (PromptReco stub) | `/Muon{0,1}/Run2024D-PromptReco-v1/MINIAOD` | **TODO-VERIFY** on DAS |
| MC DAS (FxFx stub) | `/DYto2L-2Jets_Bin-MLL-50_…/RunIII2024Summer24MiniAODv6-150X_…/MINIAODSIM` | **TODO-VERIFY** |
| HLT (OR) | `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` | `displacedV0_cfi.py` → `hltPaths`; tree: `passDimuonHLT`, `HLT_Mu17_…` |
| DeepJet veto | loose WP placeholder **`0.0494`** on `Jet_btagDeepFlavB` | `v0builder.py --deepjet-loose-wp`; **TODO-VERIFY** BTV JSON |
| Δ2D bins [cm] | `0,1,2,3,5,7,11,16,22,30,40,60,90,120` | `analysis/config_ksvars.py` → laurelin `_RPV` |
| Low-Δ2D norm \(\mathcal{N}\) | `[0, 2]` cm | `config_ksvars.py` `normrange`; `fitting/variables/variable_norm_rpv.json` |
| Sideband mass | `_mass` in `[0.44, 0.56]` (31 bins) | `config_ksvars.py` `bkgsideband` |
| MagField (ntuple) | `useESMagneticField=False` (OAE `3_8T`) by default; ES MagField+TTBuilder via `True` | `displacedV0_cfi.py` |
| Dimuon Path filter | `enableDimuonPreFilter=True` (2 medium, pT>30/25, \|mμμ−mZ\|<10) | production + smoke cfgs |

---

## 0. Offline dry-run (no CMSSW / no DAS)

Sanity-check v0building → analysis config wiring on a tiny dummy ntuple:

```bash
cd /path/to/K0sAnalysisRun3
python3 scripts/make_dummy_displacedv0_ntuple.py -o /tmp/dummy_displacedv0.root
python3 v0building/v0builder.py -i /tmp/dummy_displacedv0.root -o /tmp/dummy_v0sel.root \
  --apply-dy-selection --no-bveto --nevents 50
# Optional: inspect laurelin branches (_RPV, _mass, _weight)
```

Full fill/fit needs real sideband stats; the dummy only proves the DisplacedV0
branch map and DY preselection path.

---

## 1. Resolve samples (lxplus + CMS VO)

```bash
cd /path/to/K0sAnalysisRun3
bash scripts/das_discover.sh
# Focus:
dasgoclient -query='dataset=/Muon*/Run2024D*/MINIAOD' | sort
dasgoclient -query='parent dataset=/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD'
dasgoclient -query='dataset=/DYto2L*13p6TeV*amcatnloFXFX*/Run*2024*MiniAOD*/MINIAODSIM' | sort
```

Freeze confirmed strings into `samples/*.txt` and `conditions.md`. Copy golden JSON
from `samples/cert/README.md`.

---

## 2. scram smoke (M3)

Follow [`cmsrun-smoke-test.md`](cmsrun-smoke-test.md):

```bash
export SCRAM_ARCH=el8_amd64_gcc12   # verify for release
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_14_0_19                 # or 15_0_X if MiniAODv6 / 150X_
cd CMSSW_14_0_19/src && cmsenv
ln -s /path/to/K0sAnalysisRun3/ntuplizer/K0sAnalysis K0sAnalysis
scram b -j8

# One MiniAOD file each (xrdcp / dasgoclient)
cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:$PWD/data_one.root maxEvents=200
cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:$PWD/dy_one.root maxEvents=200

# Optional ES MagField + TransientTrackBuilder path:
# cmsRun … useESMagneticField=True
# Optional: enableDimuonPreFilter=False to debug without AN §5 Path filter
```

Exit: tree `displacedV0Ntuple/events` with muons + `_V0Type==1` mass near 0.498.

---

## 3. CRAB (M4) — Run2024D + DY

Production psets (wrap the same DisplacedV0 sequence as the one-file smoke cfgs):

- `ntuplizer/K0sAnalysis/DisplacedV0/python/displacedV0_data_cfg.py`
- `ntuplizer/K0sAnalysis/DisplacedV0/python/displacedV0_mc_cfg.py`

Shared CRAB builders + PLACEHOLDER `storageSite`: `ntuplizer/K0sAnalysis/DisplacedV0/test/crab_common.py`  
(details: `ntuplizer/K0sAnalysis/DisplacedV0/test/README.md`).

```bash
# On lxplus / CMSLPC after cmsenv + scram b (K0sAnalysis linked into $CMSSW_BASE/src):
#
# 1) TODO-VERIFY DAS + golden JSON (samples/*.txt, samples/cert/README.md, conditions.md)
# 2) Set your writeable site — do NOT invent a T2 in git:
export CRAB_STORAGE_SITE=T2_CH_CERN   # replace with *your* site

# 3) Smoke first (few lumis / few files):
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024_smoke.py   # Muon0, totalUnits=20
crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy_smoke.py        # DY, totalUnits=2

# 4) Full submit (Muon0 + Muon1 twin + DY):
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024.py          # Muon0
crab submit -c K0sAnalysis/DisplacedV0/test/crab_data_2024_muon1.py    # Muon1
crab submit -c K0sAnalysis/DisplacedV0/test/crab_mc_dy.py
```

| Config | `requestName` / `outputDatasetTag` | Job `outputFiles` |
| --- | --- | --- |
| Muon0 | `DisplacedV0_Muon0_Run2024D` | `DisplacedV0_Muon0_Run2024D.root` |
| Muon1 | `DisplacedV0_Muon1_Run2024D` | `DisplacedV0_Muon1_Run2024D.root` |
| DY | `DisplacedV0_DY_Summer24` | `DisplacedV0_DY_Summer24.root` |

Smoke jobs append `_smoke` to `requestName` only. Merged EOS paths for v0building
still look like `displacedV0_Muon0_Run2024D.root` / `displacedV0_DY_Summer24.root`
after hadd / rename as needed.

---

## 4. v0building (AN §5 + §6)

On ntuples under EOS/T2 (adjust paths):

```bash
cd /path/to/K0sAnalysisRun3/v0building
# DeepJet WP: use frozen value from conditions.md when available
DJWP=0.0494   # TODO-VERIFY

python3 v0builder.py \
  -i /eos/.../DisplacedV0_Muon0_Run2024D.root \
  -o /eos/.../v0sel_data_Run2024D.root \
  --apply-dy-selection --deepjet-loose-wp $DJWP --selection legacy
# Also process Muon1 (DisplacedV0_Muon1_Run2024D.root) the same way; merge eras later.

python3 v0builder.py \
  -i /eos/.../DisplacedV0_DY_Summer24.root \
  -o /eos/.../v0sel_dy_Summer24.root \
  --apply-dy-selection --deepjet-loose-wp $DJWP --selection legacy
```

Output trees: `nimloth` / `celeborn` / `laurelin` / `telperion` with `_RPV`, `_mass`, `_weight`.

---

## 5. Sideband fits (M6)

```bash
cd /path/to/K0sAnalysisRun3
# Per-bin / unbinned sideband fits (RooFit / TF1 path — preference locked)
python3 fitting/fitinvmass.py -h   # confirm flags for your batch
# Typical: fit m_ππ sidebands in each Δ2D bin; write yields for count_peak
python3 fitting/count_peak.py -h
```

Use `fitting/variables/variable_ks_invmass.json` + `variable_ks_rpv.json`
(Run3 Δ2D edges). Gallery of mass fits is an M6 exit criterion.

---

## 6. Fill \(C(\Delta_{2D})\) (M7)

```bash
cd /path/to/K0sAnalysisRun3/analysis

# Build an input JSON (datain / mcin paths + luminosities), e.g. from
# analysis/example_input_run2024d.json after editing file paths:
python3 mcvsdata_fill.py \
  -i example_input_run2024d.json \
  -t laurelin \
  -v ../fitting/variables/variable_ks_rpv.json \
  -o /eos/.../C_delta2D_Run2024D.root \
  --bkgmode sideband \
  --sidevariable ../fitting/variables/variable_ks_invmass.json \
  --normmode range \
  --normvariable ../fitting/variables/variable_norm_rpv.json \
  --norm-stability-uppers 1.0,3.0 \
  --peak-halfwidth-frac 0.25 \
  --weightvar _weight \
  --ntrueintvar _nTrueInt \
  --nopileup
```

Config reference: `config_ksvars.py` (bins, sideband `_mass`, `normrange=[0,2]`).
Batch wrapper: `mcvsdata_submit.py` with `--config config_ksvars.py`.
Output writes shared `norm_scale=[k, σ_k/k]`, `normshared_up/down` (correlated;
single-token syst name for the plotter), and `norm_scale_alt_upper_*` when
`--norm-stability-uppers` is set (CDTE-25).


---

## 7. Plot + export

```bash
# Upstream-style plots (after fill outputs exist)
python3 -c "from plotting import plotfit; print('plotting OK')"  # env check
# SF table for LLP analyses:
python3 scripts/make_sf_json.py -h
```

Deliverable: `C_i` vs Δ2D with stats errors; record era + JSON path in `conditions.md`.

---

## 8. Validation (before freezing v1 SF)

Execute plan §6 items 1–8 (DY controls, Ks mass, low-Δ2D \(C\approx1\), pixel
layer features, norm ±1 bin, sideband degree, era/PU checks as stats allow).

---

## Still needs lxplus / CRAB / CMS VO

| Step | Why |
| --- | --- |
| Live `dasgoclient` | Confirm PromptReco vs MiniAODv6 parent; freeze exact DAS strings |
| Golden / PU JSON + `brilcalc` | Era run bounds + \(\mathcal{L}\) + PU profile |
| DeepJet WP on CVMFS | Replace `0.0494` placeholder |
| `cmsrel` / `scram b` / `cmsRun` | M3 smoke (this VM has no CMSSW) |
| CRAB submit + EOS/T2 | M4 ntuples |
| Full fill/fit on real stats | First physics \(C(\Delta_{2D})\) |

---

## Related docs

- Method: `docs/displaced-track-efficiency-run3-2024.md`
- Plan: `docs/displaced-track-efficiency-implementation-plan.md` (M2–M7)
- Smoke: `docs/cmsrun-smoke-test.md`
- **lxplus ordered runbook:** `docs/lxplus-first-c-runbook.md`
- **Run 3 (2024) audit checklist:** [`run3-2024-audit-checklist.md`](run3-2024-audit-checklist.md)
- Status: `docs/k0s-run3-scaffold-status.md`
