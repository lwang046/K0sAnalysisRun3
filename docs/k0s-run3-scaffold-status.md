# K0sAnalysisRun3 scaffold status (M0–M4 prep + first-\(C\) measurement handoff)

**Date:** 2026-11-24 (Asia/Shanghai)  
**Workers:** scaffold / prep / CRAB / VarParsing workers (prior); measurement handoff `bc-cb47e4bb-c55e-53fc-9150-ce025e1aaa6b`  
**Outcome:** Package on GitHub `main` through **PR #4** (CRAB) + **PR #5** (VarParsing) + **PR #6** (lxplus runbook). Offline §0 dry-run **passed**. First physics \(C(\Delta_{2D})\) blocked without CMS VO/CVMFS — Long follows `docs/lxplus-first-c-runbook.md`. HepTools untouched.

---

## Location

GitHub: `https://github.com/lwang046/K0sAnalysisRun3`

Canonical docs (in-repo `docs/`):

- `docs/displaced-track-efficiency-run3-2024.md`
- `docs/displaced-track-efficiency-implementation-plan.md`
- `docs/cmsrun-smoke-test.md`
- `docs/first-c-delta2d-recipe.md`
- `docs/lxplus-first-c-runbook.md` *(lxplus ordered commands)*
- `docs/run3-2024-audit-checklist.md` *(Neon Run 3 physics gates)*
- `docs/k0s-run3-scaffold-status.md`

---

## Repo / PR

| Item | Status |
| --- | --- |
| Target GitHub | `https://github.com/lwang046/K0sAnalysisRun3` |
| `main` tip | `5bc44a5` — Add lxplus first-C runbook and measurement status (#6) |
| Merged | [#2](https://github.com/lwang046/K0sAnalysisRun3/pull/2) prep · [#4](https://github.com/lwang046/K0sAnalysisRun3/pull/4) CRAB · [#5](https://github.com/lwang046/K0sAnalysisRun3/pull/5) VarParsing · [#6](https://github.com/lwang046/K0sAnalysisRun3/pull/6) lxplus runbook |
| HepTools | Untouched |

---

## Milestone checklist

| Deliverable | Status | Notes |
| --- | --- | --- |
| **M0** plan defaults | Done | README M0 table / plan §8 |
| **M1** README + tree | Done | Attribution to AN-20-111 / K0sAnalysis |
| **M2** samples / HLT / cert / conditions | **First-era freeze (best-effort)** | **Run2024D** PromptReco Muon0/1 + Summer24 DYto2L FxFx stubs; DeepJet placeholder `0.0494`; full DAS/WP still **TODO-VERIFY** |
| **M3** DisplacedV0 | Analyzers + MagField hardening | `useESMagneticField`; OAE default; **no cmsRun on VM** |
| Offline fitting / analysis / v0building | Ported + **dry-run passed** | dummy ntuple → v0builder DY path (2026-11-24) |
| First \(C(\Delta_{2D})\) recipe | Done (doc) | `docs/first-c-delta2d-recipe.md` |
| **M4** CRAB configs | **Merged prep** | Production psets + smoke/full + `CRAB_STORAGE_SITE`; DAS/lumiMask **TODO-VERIFY**; **no crab submit** — #4 + #5 |
| lxplus runbook | **Merged** | `docs/lxplus-first-c-runbook.md` — DAS → SF export ([#6](https://github.com/lwang046/K0sAnalysisRun3/pull/6)) |
| First physics \(C(\Delta_{2D})\) | **Blocked** | Needs Long's lxplus session (DAS/brilcalc/cmsRun/CRAB/fit/fill) |

---

## This turn (measurement handoff — offline + runbook)

| Change | Detail |
| --- | --- |
| Offline §0 | `make_dummy_displacedv0_ntuple` → `v0builder --apply-dy-selection --no-bveto`: **PASS** (40→13 events; laurelin 12 with `_RPV`/`_mass`/`_weight`) |
| Code fixes | None required for dry-run; did not touch production psets (PR #5 already on `main`) |
| lxplus runbook | New user-facing ordered commands; Context + repo `docs/` |
| Status | Measurement = offline dry-run done; remainder = lxplus |

---

## Still needs lxplus / CRAB / CMS VO (Long)

1. Live `dasgoclient` — freeze exact DAS strings  
2. Golden / PU JSON + `brilcalc` — era \(\mathcal{L}\)  
3. DeepJet loose WP from CVMFS BTV JSON (replace `0.0494`)  
4. `cmsrel` / `scram b` / `cmsRun` smoke  
5. CRAB smoke → full (Muon0/1 + DY) with `export CRAB_STORAGE_SITE=…`  
6. v0building → sideband fits → `mcvsdata_fill` → SF export  

Follow: `docs/lxplus-first-c-runbook.md`. Physics gates: `docs/run3-2024-audit-checklist.md`.

---

## Intentionally not done here

- No CMSSW build / cmsRun execution (no CVMFS on this VM)  
- No live DAS queries (no CMS VO)  
- No CRAB submit / EOS writes  
- No invented DAS strings, T2 sites, or luminosities  
- No HepTools modifications  
