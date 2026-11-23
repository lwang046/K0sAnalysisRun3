# K0sAnalysisRun3

Run 3 / 2024 port of the AN-20-111 displaced-track / V0 calibration pipeline
(\(C(\Delta_{2D})\) from \(K_S^0\) yields in DY \(\mu\mu\) events).

**Status:** Context-only (M0–M3 + offline). **`V0Analyzer` + lean Trigger/Lepton/Jet**
ported from upstream K0sAnalysis (`2a132385`); genWeight/PU hooks filled.
**Offline `fitting/`, `analysis/`, `v0building/` ported** (RooFit/TF1 path;
DisplacedV0 branch adaptations; AN sideband + low-Δ2D normalization).
Not yet on GitHub.

## Attribution

- Physics method: CMS AN-20-111 v4; public DP-2024-010
- Reference implementation: [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
  (`V0Analyzer`, `fitting/`, `analysis/`). This tree is a slim Run 3 fork/port,
  not a rewrite of the physics.

## Docs (Project Context)

| Doc | Path |
| --- | --- |
| Method | `/cursor/stores/self/docs/displaced-track-efficiency-run3-2024.md` |
| Implementation plan | `/cursor/stores/self/docs/displaced-track-efficiency-implementation-plan.md` |
| Preferences (M0 defaults) | `/cursor/stores/self/preferences.md` |
| Scaffold status | `/cursor/stores/self/docs/k0s-run3-scaffold-status.md` |
| cmsRun smoke test | `/cursor/stores/self/docs/cmsrun-smoke-test.md` |

Copies under `docs/` in this tree point at those Context paths.

## Layout

```text
K0sAnalysisRun3/
├── README.md
├── conditions.md                 # GT / era aliases (fill on first CRAB)
├── samples/                      # DAS stubs, HLT, cert pointers (M2)
├── ntuplizer/DisplacedV0/        # slim CMSSW package (V0/Trigger/Lepton/Jet)
├── skimming/                     # DY skim (still thin; v0builder can apply AN §5)
├── v0building/                   # AN §6 selection + DisplacedV0→laurelin
├── fitting/                      # RooFit/TF1 sideband fits (ported)
├── analysis/                     # C(Δ2D) fill/plot configs (Run3 bins)
├── tools/, plotting/             # Minimal deps for offline imports
├── scripts/                      # DAS discovery, submit helpers
└── docs/                         # pointers to Context method/plan
```

## M0 decisions (locked)

From `preferences.md` / plan §8 defaults:

| Decision | Choice |
| --- | --- |
| Reuse path | Fork/extend K0sAnalysis → `K0sAnalysisRun3` |
| V0 where | CMSSW `V0Analyzer` (MiniAOD) |
| Reco | PromptReco OK to start |
| Fitting | ROOT **RooFit** (upstream `fitting/`) |
| Release | `CMSSW_14_0_X` (or `15_0_X` if MiniAODv6) |
| SF export | JSON + ROOT; correctionlib if consumer needs it |
| v1 scope | \(K_S^0 + \mu\mu\) only |

## Build sketch (when CMSSW available)

Full steps, MagField notes, and branch checklist:
[`/cursor/stores/self/docs/cmsrun-smoke-test.md`](/cursor/stores/self/docs/cmsrun-smoke-test.md)

```bash
cmsrel CMSSW_14_0_X   # match MiniAOD campaign token
cd CMSSW_*/src && cmsenv
# symlink/copy as $CMSSW_BASE/src/DisplacedV0 (not under ntuplizer/)
ln -s /path/to/K0sAnalysisRun3/ntuplizer/DisplacedV0 DisplacedV0
scram b -j8
cmsRun DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:/path/to/miniaod.root maxEvents=200
cmsRun DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:/path/to/miniaodsim.root maxEvents=200
```

This Project VM has no CMSSW — run the above on lxplus/CMSLPC.

## Later: push to GitHub

See `/cursor/stores/self/docs/k0s-run3-scaffold-status.md` § “How to push later”.
When `lwang046/K0sAnalysisRun3` exists and the Cursor GitHub App can access it:

```bash
cd /cursor/stores/self/code/K0sAnalysisRun3
git init
git remote add origin git@github.com:lwang046/K0sAnalysisRun3.git
# optionally: merge/seed from LukaLambrecht/K0sAnalysis history
git add -A && git commit -m "M0–M3 Run3 scaffold"
git push -u origin main
```

Do **not** push into `lwang046/HepTools`.
