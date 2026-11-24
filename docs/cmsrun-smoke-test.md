# Local cmsRun / scram smoke test — `K0sAnalysis/DisplacedV0`

**Package:** `ntuplizer/K0sAnalysis/DisplacedV0/` (scram Subsystem/Package)  
**Audience:** lxplus / CMSLPC / any machine with CVMFS + a Run-3 CMSSW release  
**Goal:** first successful `scram b` + one-file `cmsRun` (data + MC) before CRAB

---

## Environment note (this Project VM)

This Cursor cloud / Project worker **does not have CMSSW** (`cmsrel`, `scram`, `cmsRun`, and `/cvmfs/cms.cern.ch` are absent; `CMSSW_BASE` unset). The steps below are **runnable on a CMSSW host**; they were not executed here. One-file cfgs were still corrected for smoke (Python import path + VarParsing `inputFiles` / `maxEvents`).

---

## 1. Pick release + arch

Match the MiniAOD campaign token (from DAS / PdmV), not a guess:

| Campaign clue | Start with |
| --- | --- |
| Summer24 / `140X_*` MiniAOD | `CMSSW_14_0_X` (latest patch with the dataset’s GT series) |
| MiniAODv6+ / later JECs | `CMSSW_15_0_X` |

Typical SCRAM_ARCH (verify on the release page / `scram list`): `el8_amd64_gcc12` for 14_0.

Pin exact release + GT strings in `conditions.md` (repo root) on the first green smoke.

Aliases already in the one-file cfgs:

- Data: era `Run3`, GT `auto:run3_data`
- MC: era `Run3_2024`, GT `auto:phase1_2024_realistic`

---

## 2. Setup + place the package

On lxplus (or equivalent):

```bash
export SCRAM_ARCH=el8_amd64_gcc12   # verify for chosen release
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_14_0_19                 # example — use the patch that matches MiniAOD
cd CMSSW_14_0_19/src
cmsenv

# scram expects two-level Subsystem/Package: $CMSSW_BASE/src/K0sAnalysis/DisplacedV0
# Link the Subsystem directory (preferred):
ln -s /path/to/K0sAnalysisRun3/ntuplizer/K0sAnalysis K0sAnalysis
# OR: mkdir -p K0sAnalysis && ln -s .../ntuplizer/K0sAnalysis/DisplacedV0 K0sAnalysis/DisplacedV0

scram b -j8
```

**Layout check after link/copy (Neon-recommended):**

```text
$CMSSW_BASE/src/K0sAnalysis/DisplacedV0/
├── BuildFile.xml
├── interface/
├── plugins/          # EDM plugins DisplacedV0Ntuple + DimuonPreFilter
├── python/           # displacedV0_cfi.py, dimuonPreFilter_cfi.py, test_* / production cfgs
├── src/              # V0 / Trigger / Lepton / Jet analyzers
└── test/             # CRAB configs (crab_common + data/MC/smoke) + README
```

Do **not** symlink bare `DisplacedV0` at `$CMSSW_BASE/src/DisplacedV0` — scram needs the `K0sAnalysis/` subsystem level. Do **not** leave the package under `ntuplizer/` inside `src/`.

Python import: `from K0sAnalysis.DisplacedV0.displacedV0_cfi import …`
(CMSSW maps `Subsystem/Package/python/foo.py` → `Subsystem.Package.foo`).

---

## 3. Get one MiniAOD file each

Resolve DAS names from `samples/data_muon_2024.txt` and `samples/sim_dy_m50_13p6.txt` (patterns only until filled), then pull one file:

```bash
# example — replace with a real LFN from dasgoclient
dasgoclient -query='file dataset=/Muon0/Run2024F-PromptReco-v1/MINIAOD' | head
xrdcp root://cms-xrd-global.cern.ch//store/.../miniaod.root data_one.root

dasgoclient -query='file dataset=/DYJetsToLL_M-50_.../MINIAODSIM' | head
xrdcp root://cms-xrd-global.cern.ch//store/.../miniaodsim.root dy_one.root
```

Remote `root://...` in `inputFiles` is fine if the site/proxy works; local `file:` is simpler for first smoke.

---

## 4. Run one-file cfgs

From `$CMSSW_BASE/src` (after `cmsenv`):

```bash
cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:$PWD/data_one.root maxEvents=200

cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:$PWD/dy_one.root maxEvents=200

# Debug: skip AN §5 dimuon Path filter
# cmsRun … enableDimuonPreFilter=False
```

Outputs (cwd):

- `displacedV0_data_smoke.root`
- `displacedV0_mc_smoke.root`

Tree path inside each file: **`displacedV0Ntuple/events`** (TFileService uses the module label).

Python import used by the cfgs is `from K0sAnalysis.DisplacedV0.displacedV0_cfi import ...` — CMSSW maps `Subsystem/Package/python/foo.py` → `Subsystem.Package.foo`.

Default `cms.Path` is `dimuonPreFilter + displacedV0Ntuple` (AN §5: 2 medium muons, pT>30/25, |mμμ−mZ|<10 GeV). Set `enableDimuonPreFilter=False` to run the analyzer alone.

---

## 5. MagField / TransientTrackBuilder (V0 port)

**Default (smoke-friendly):** `useESMagneticField=False` in `displacedV0_cfi.py`.
`V0Analyzer` owns an `OAEParametrizedMagneticField("3_8T")` via `unique_ptr` and
builds `reco::TransientTrack(track, bfield)`. No MagField ES products are required.

**Optional ES path:** set `useESMagneticField=True` (cfi or VarParsing).
`DisplacedV0Ntuple` then `esConsumes` both `IdealMagneticFieldRecord` and
`TransientTrackBuilder` / `TransientTrackRecord`; V0 fitter prefers
`ttBuilder->build(track)`. Load in the cfg:

```python
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
```

**MiniAOD track API (compile-ready; TODO-VERIFY on lxplus without scram here):**
`hasTrackDetails()` + `pseudoTrack()` on `packedPFCandidates` and `lostTracks`
(InputTag `"lostTracks"`). Confirm both collections yield tracks on 2024 MiniAODv4/v6.

Include hardening: `__has_include` prefers
`MagneticField/ParametrizedEngine/interface/OAEParametrizedMagneticField.h`,
else the upstream `…/src/…` path.

| Risk on 14_0 / 15_0 | What to try |
| --- | --- |
| Compile fails on OAE header | `__has_include` switch already in `V0Analyzer.h`; confirm release tree |
| `reco::TransientTrack(Track, MagField*)` removed/deprecated | ES path uses `TransientTrackBuilder` (`esConsumes`); pass `useESMagneticField=True` |
| Smoke cfg “missing MagField” with default False | Expected OK — OAE is in-process |
| ES path fails without MagField_cff | Pass `useESMagneticField=True` only after loading sequences above |
| Zero tracks from packed/lost | TODO-VERIFY `hasTrackDetails`/`pseudoTrack` + `lostTracks` tag on era MiniAOD |

`"3_8T"` remains the correct Run-3 nominal for the parametric engine. Prefer the
ES MagField + TransientTrackBuilder for production CRAB once smoke passes both modes.

`BuildFile.xml` `<use>`s `MagneticField/{Engine,ParametrizedEngine,Records}` and
`TrackingTools/{TransientTrack,Records}`.

---

## 6. Expected ROOT branches (smoke checklist)

Quick inspect:

```bash
python3 - <<'PY'
import ROOT
f = ROOT.TFile.Open("displacedV0_data_smoke.root")
t = f.Get("displacedV0Ntuple/events")
assert t, "missing tree displacedV0Ntuple/events"
names = {b.GetName() for b in t.GetListOfBranches()}
need = [
    "run", "luminosityBlock", "event", "nPV",
    "genWeight", "Pileup_nTrue",
    "passDimuonHLT", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
    "nMuon", "Muon_pt", "Muon_mediumId",
    "nJet", "Jet_pt", "Jet_btagDeepFlavB",
    "_nV0s", "_V0InvMass", "_V0Type", "_V0RPV", "_V0DCA",
]
missing = [n for n in need if n not in names]
print("entries", t.GetEntries(), "missing", missing)
# Ks mass peak (type 1) — coarse check on ≥ few hundred events
h = ROOT.TH1F("hks", "", 60, 0.44, 0.56)
t.Draw("_V0InvMass>>hks", "_V0Type==1", "goff")
print("Ks candidates drawn", int(h.GetEntries()), "mean", h.GetMean())
PY
```

| Group | Branches to see |
| --- | --- |
| Event | `run`, `luminosityBlock`, `event`, `nPV` |
| Weights | `genWeight` (=1 on data), `Pileup_nTrue` (−1 on data; filled on MC) |
| Trigger | `passDimuonHLT`, `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` |
| Muons | `nMuon`, `Muon_pt/eta/phi`, `Muon_mediumId`, `Muon_pfRelIso04_all`, … |
| Jets | `nJet`, `Jet_pt`, `Jet_btagDeepFlavB`, `Jet_jetId` |
| V0 | `_nV0s`, `_V0InvMass`, `_V0Type` (1=Ks, 2=Λ, 3=Λ̄), `_V0RPV` / `_V0RBS`, `_V0DCA`, daughter `_V0PtPos/Neg`, … |

**Physics smoke:** among `_V0Type==1`, `_V0InvMass` should pile near **0.498 GeV** (CMSSW preselection is loose; AN §6 tight cuts are offline). Zero V0s on 200 DY events is a red flag (MagField / track tokens / crash-and-empty); a visible Ks peak is the M3 exit criterion.

---

## 7. Pass / fail checklist

- [ ] `cmsrel` + `cmsenv` on `CMSSW_14_0_X` or `15_0_X` matching MiniAOD
- [ ] `K0sAnalysis` linked so `$CMSSW_BASE/src/K0sAnalysis/DisplacedV0` exists
- [ ] `scram b -j8` succeeds (watch MagField include + plugin link)
- [ ] Data `cmsRun` writes `displacedV0_data_smoke.root` with tree `displacedV0Ntuple/events`
- [ ] MC `cmsRun` same; `genWeight` / `Pileup_nTrue` not stuck at defaults on every event
- [ ] Branch checklist above present
- [ ] `_V0Type==1` mass near 0.498 visible
- [ ] Optional: `useESMagneticField=True` smoke also green
- [ ] Exact release + resolved GT recorded in `conditions.md`

When all boxes pass, M3 local smoke is done; next is CRAB under
`K0sAnalysis/DisplacedV0/test/` (see `docs/first-c-delta2d-recipe.md` §3 and
`ntuplizer/K0sAnalysis/DisplacedV0/test/README.md`).
Also run the physics gates in [`run3-2024-audit-checklist.md`](run3-2024-audit-checklist.md).

---

## Related paths

| Path | Role |
| --- | --- |
| `ntuplizer/K0sAnalysis/DisplacedV0/` | CMSSW Subsystem/Package source |
| `.../python/test_data_onefile_cfg.py` | Local data smoke cfg (placeholder) |
| `.../python/test_mc_onefile_cfg.py` | Local MC smoke cfg (placeholder) |
| `.../python/displacedV0_data_cfg.py` | Production data pset for CRAB |
| `.../python/displacedV0_mc_cfg.py` | Production MC pset for CRAB |
| `.../python/dimuonPreFilter_cfi.py` | AN §5 Path filter |
| `.../test/README.md` | CRAB submit table + storageSite instructions |
| `conditions.md` | GT / release snapshot |
| `docs/k0s-run3-scaffold-status.md` | Scaffold status |
| `docs/first-c-delta2d-recipe.md` | First-C ordered recipe (§3 = CRAB) |
