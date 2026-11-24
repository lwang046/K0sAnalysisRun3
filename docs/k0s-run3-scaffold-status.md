# K0sAnalysisRun3 scaffold status (M0–M3 + first \(C(\Delta_{2D})\) prep)

**Date:** 2026-11-23  
**Workers:** scaffold `bc-265d0870-…`; V0 / Trigger/Lepton/Jet / smoke / samples / offline / push workers (see prior revisions); first-\(C\) prep `bc-d63dd8f2-017a-5772-8087-69778afa241d`  
**Outcome:** Package on GitHub. Analyzers + offline fitting/analysis/v0building ported. **M2 first-era freeze:** **Run2024D** + Summer24 DY stubs; MagField ES switch; **`docs/first-c-delta2d-recipe.md`**; dummy ROOT dry-run path. **PR #1** (scaffold) still open; this work stacks as a follow-up PR. HepTools untouched.

---

## Location

GitHub: `https://github.com/lwang046/K0sAnalysisRun3`  
Context mirror: `/cursor/stores/self/code/K0sAnalysisRun3/` and `/cursor/stores/self/docs/`

Canonical docs:

- `/cursor/stores/self/docs/displaced-track-efficiency-run3-2024.md`
- `/cursor/stores/self/docs/displaced-track-efficiency-implementation-plan.md`
- `/cursor/stores/self/docs/cmsrun-smoke-test.md`
- `/cursor/stores/self/docs/first-c-delta2d-recipe.md` *(new)*
- `/cursor/stores/self/docs/k0s-run3-scaffold-status.md`
- `/cursor/stores/self/preferences.md`

---

## Repo / PR

| Item | Status |
| --- | --- |
| Target GitHub | `https://github.com/lwang046/K0sAnalysisRun3` |
| Base / parent PR | **#1** open — `cursor/push-context-package-0cb7` |
| This work branch | `cursor/first-c-delta2d-prep-241d` (stacked on #1) |
| This PR | **https://github.com/lwang046/K0sAnalysisRun3/pull/2** |
| HepTools | Untouched |

---

## Milestone checklist

| Deliverable | Status | Notes |
| --- | --- | --- |
| **M0** plan defaults | Done | `preferences.md` / README |
| **M1** README + tree | Done | Attribution to AN-20-111 / K0sAnalysis |
| **M2** samples / HLT / cert / conditions | **First-era freeze (best-effort)** | **Run2024D** PromptReco Muon0/1 + Summer24 DYto2L FxFx; Nano parent lookup documented; DeepJet placeholder `0.0494`; full DAS/WP still **TODO-VERIFY** |
| **M3** DisplacedV0 | Analyzers + MagField hardening | `useESMagneticField` cfg/ES token; OAE default; smoke docs updated; **no cmsRun on VM** |
| Offline fitting / analysis / v0building | Ported + dry-run | `count_jets` fix; dummy ntuple script; `config_defaults_run3.py` |
| First \(C(\Delta_{2D})\) recipe | **Done (doc)** | `docs/first-c-delta2d-recipe.md` — scram → CRAB → v0building → fit → fill |
| **M4** CRAB configs | **Prep tightened** | Production psets + Muon0/1 + smoke knobs; `storageSite` PLACEHOLDER / `CRAB_STORAGE_SITE`; DAS/lumiMask still **TODO-VERIFY**; **no crab submit** — [PR #4](https://github.com/lwang046/K0sAnalysisRun3/pull/4) |

---

## This turn (CRAB submit prep)

| Change | Detail |
| --- | --- |
| Production psets | `displacedV0_{data,mc}_cfg.py` wrap same sequence as one-file smoke placeholders |
| CRAB builders | `test/crab_common.py`; Muon0 / Muon1 twin / DY + smoke variants |
| Naming | `DisplacedV0_Muon{0,1}_Run2024D` / `DisplacedV0_DY_Summer24` request + output files |
| Docs | Recipe §3, `test/README.md`, smoke-test related paths |

---

## Still needs lxplus / CRAB / CMS VO

1. Live `dasgoclient` — confirm Run2024D PromptReco vs MiniAODv6 parent; freeze exact DAS strings  
2. Golden / PU JSON + `brilcalc` — era run bounds, \(\mathcal{L}\), PU profile  
3. DeepJet loose WP from CVMFS BTV JSON (replace `0.0494`)  
4. `cmsrel` / `scram b` / `cmsRun` smoke (OAE + optional ES MagField)  
5. CRAB smoke → full ntuple for Run2024D Muon0/1 + DY  
6. Sideband fits + `mcvsdata_fill` → first physics \(C(\Delta_{2D})\)

---

## Intentionally not done here

- No CMSSW build / cmsRun execution (no CVMFS on this VM)  
- No live DAS queries (no CMS VO)  
- No CRAB submit / EOS writes  
- No HepTools modifications  
