# K0sAnalysisRun3

Run 3 / 2024 port of the AN-20-111 displaced-track / V0 calibration pipeline
(\(C(\Delta_{2D})\) from \(K_S^0\) yields in DY \(\mu\mu\) events).

**Status:** On GitHub [`lwang046/K0sAnalysisRun3`](https://github.com/lwang046/K0sAnalysisRun3)
(`main`). Context M0–M3 + offline ports done; **`V0Analyzer` + lean Trigger/Lepton/Jet**
ported from upstream K0sAnalysis (`2a132385`); genWeight/PU hooks filled.
**Offline `fitting/`, `analysis/`, `v0building/` ported** (RooFit/TF1 path;
DisplacedV0 branch adaptations; AN sideband + low-Δ2D normalization).
**No `scram` / `cmsRun` claimed from the Project VM** — run those on lxplus/CMSLPC.

## Attribution

- Physics method: CMS AN-20-111 v4; public DP-2024-010
- Reference implementation: [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
  (`V0Analyzer`, `fitting/`, `analysis/`). This tree is a slim Run 3 fork/port,
  not a rewrite of the physics.

## Docs

| Doc | Path |
| --- | --- |
| Method | [`docs/displaced-track-efficiency-run3-2024.md`](docs/displaced-track-efficiency-run3-2024.md) |
| Implementation plan | [`docs/displaced-track-efficiency-implementation-plan.md`](docs/displaced-track-efficiency-implementation-plan.md) |
| First \(C(\Delta_{2D})\) recipe | [`docs/first-c-delta2d-recipe.md`](docs/first-c-delta2d-recipe.md) |
| lxplus runbook | [`docs/lxplus-first-c-runbook.md`](docs/lxplus-first-c-runbook.md) |
| Run 3 (2024) audit checklist | [`docs/run3-2024-audit-checklist.md`](docs/run3-2024-audit-checklist.md) |
| cmsRun smoke test | [`docs/cmsrun-smoke-test.md`](docs/cmsrun-smoke-test.md) |
| Scaffold status | [`docs/k0s-run3-scaffold-status.md`](docs/k0s-run3-scaffold-status.md) |
| Docs index | [`docs/README.md`](docs/README.md) |

M0 defaults are summarized in the table below (also in the plan §8).

## Layout

```text
K0sAnalysisRun3/
├── README.md
├── conditions.md                 # GT / era aliases (fill on first CRAB)
├── samples/                      # DAS stubs, HLT, cert pointers (M2)
├── ntuplizer/K0sAnalysis/DisplacedV0/        # slim CMSSW package (V0/Trigger/Lepton/Jet)
├── skimming/                     # DY skim (still thin; v0builder can apply AN §5)
├── v0building/                   # AN §6 selection + DisplacedV0→laurelin
├── fitting/                      # RooFit/TF1 sideband fits (ported)
├── analysis/                     # C(Δ2D) fill/plot configs (Run3 bins)
├── tools/, plotting/             # Minimal deps for offline imports
├── scripts/                      # DAS discovery, submit helpers
└── docs/                         # method, plan, recipe, runbook, audit
```

## M0 decisions (locked)

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
[`docs/cmsrun-smoke-test.md`](docs/cmsrun-smoke-test.md).
Run 3 physics gates before freezing SF:
[`docs/run3-2024-audit-checklist.md`](docs/run3-2024-audit-checklist.md).

Neon two-level scram layout: `$CMSSW_BASE/src/K0sAnalysis/DisplacedV0`
(repo path `ntuplizer/K0sAnalysis/DisplacedV0`). Example:

```bash
cmsrel CMSSW_14_0_X   # match MiniAOD campaign token
cd CMSSW_*/src && cmsenv
# scram needs Subsystem/Package: $CMSSW_BASE/src/K0sAnalysis/DisplacedV0
ln -s /path/to/K0sAnalysisRun3/ntuplizer/K0sAnalysis K0sAnalysis
scram b -j8
cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:/path/to/miniaod.root maxEvents=200
cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:/path/to/miniaodsim.root maxEvents=200
```

This Project VM has no CMSSW — run the above on lxplus/CMSLPC.
Ordered lxplus session: [`docs/lxplus-first-c-runbook.md`](docs/lxplus-first-c-runbook.md).
