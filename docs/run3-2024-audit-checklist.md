# Run 3 (2024) physics audit checklist

Durable checklist from the Gemini Neon review (2026-11-24 Asia/Shanghai).
Use before freezing a 2024 \(C(\Delta_{2D})\) SF. Status labels are honest about
what this **repository documents / wires** vs what still needs **lxplus / CMS VO /
live DAS / CVMFS** verification. **No `scram` / `cmsRun` has been claimed from
this Project VM.**

| Status | Meaning |
| --- | --- |
| **DONE (docs/code)** | Documented and/or wired in-repo; physics intent matches Neon / AN-20-111 Run 3 update |
| **TODO-VERIFY** | Stub, placeholder, or unexecuted live check — do not freeze SF until closed |
| **TODO (later)** | Intentionally deferred (systematic, diagnostic, optional study) |

Cross-links: [first-C recipe](first-c-delta2d-recipe.md) · [lxplus runbook](lxplus-first-c-runbook.md) · [method](displaced-track-efficiency-run3-2024.md) · [plan](displaced-track-efficiency-implementation-plan.md) · [smoke](cmsrun-smoke-test.md).

---

## Neon table → repo status

| Component | AN-20-111 | Verify for 2024 | Repo status | Where |
| --- | --- | --- | --- | --- |
| Primary datasets | DoubleMuon | **Muon0 and Muon1** (not DoubleMuon) | **DONE (docs/code)** stubs + CRAB twins; DAS strings **TODO-VERIFY** | `samples/data_muon_2024.txt`; `ntuplizer/K0sAnalysis/DisplacedV0/test/crab_data_2024*.py` |
| HLT | Run 2 double-μ / TkMu | Unprescaled `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`; **drop TkMu** | **DONE (docs/code)** baseline wired; menu presence **TODO-VERIFY**; TkMu not listed | `samples/hlt_paths_2024.txt`; `displacedV0_cfi.py` → `hltPaths` |
| \(b\)-jet veto | Loose DeepCSV on CHS | **DeepJet** (or ParticleNet / UParT) on AK4 **Puppi**, not CHS; 2024 loose WP | **DONE (docs/code)** `slimmedJetsPuppi` + `Jet_btagDeepFlavB`; WP `0.0494` **TODO-VERIFY** | `JetAnalyzer`; `samples/deepjet_wp_2024.md`; `v0builder.py --deepjet-loose-wp` |
| MC & pileup | DYJetsToLL 13 TeV | Summer24 **13.6 TeV** DY; **genWeight** signs; **2024 PU** reweight | **DONE (docs/code)** Summer24 stub + `genWeight`/`Pileup_nTrue` hooks; live DAS/PU JSON/σ **TODO-VERIFY**; offline fill often `--nopileup` until wired | `samples/sim_dy_m50_13p6.txt`; `DisplacedV0Ntuple`; `conditions.md`; `reweighting/pileup/` |
| Low-Δ2D norm & fits | Linear sideband; norm Δ2D ≲ 0.5–2 cm | Higher PU → check lowest-bin fit; consider **bkg-shape systematic** | **DONE (docs/code)** sideband poly + `normrange`; bkg-shape variation **TODO (later)** | `fitting/`; `analysis/config_ksvars.py`; method §2.6–2.8 |
| Era splitting | 2016 pre/post-APV | Split **2024 C–I** as diagnostic (not required for first-C) | **DONE (docs)** C–I stubs listed; first freeze = Run2024D; multi-era combine **TODO (later)** | `samples/data_muon_2024.txt`; plan M9 |
| Efficiency vs SF | \(C(\Delta_{2D})\) Data/MC | `efficiencystudy/`: absolute ε needs custom GEN with **all gen \(K_S\)** | **DONE (docs)** caveat recorded; absolute ε **TODO (later)** / optional M11 | `efficiencystudy/README.md`; plan M11 |

---

## Item-by-item notes

### 1. Muon0 + Muon1

- Run 3 primary datasets for this analysis are **Muon0** and **Muon1**. DoubleMuon is legacy and expected empty for 2024.
- Repo has PromptReco stubs for eras **C–I** and CRAB configs for Muon0 + Muon1 twin submit.
- **TODO-VERIFY** exact DAS processed-dataset strings (PromptReco vs MiniAODv6 parent) with `dasgoclient` before CRAB.

### 2. HLT path

- Baseline OR list starts with `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8` (no TkMu in the exclusion/include lists).
- Optional companion `…_Mass8` only if present in the era menu (**TODO-VERIFY**).
- Confirm unprescaled status for the frozen era on ConfDB / HLT menu.

### 3. DeepJet / Puppi (not CHS / DeepCSV)

- Ntuplizer jet tag is `slimmedJetsPuppi`; discriminator → `Jet_btagDeepFlavB` (DeepFlavour sum).
- Offline DY veto: `v0builder.py --apply-dy-selection --deepjet-loose-wp <cut>`.
- Loose WP placeholder **`0.0494`** remains **TODO-VERIFY** against 2024 BTV `btagging.json` / `deepJet_wp_values` on CVMFS.
- Do **not** reinstate DeepCSV or CHS jets for the default veto.

### 4. Summer24 DY + genWeight + 2024 PU

- MC stub: Summer24 `DYto2L` FxFx MiniAODSIM at 13.6 TeV (`samples/sim_dy_m50_13p6.txt`) — **TODO-VERIFY** on DAS.
- `genWeight` and `Pileup_nTrue` are filled in the ntuple on MC (data keeps defaults). Sign / sum-of-weights bookkeeping for FxFx must be checked on the first MC smoke (**TODO-VERIFY**; no cmsRun claimed here).
- PU reweight machinery exists under `reweighting/pileup/`; Collisions24 PU JSON path and first-era profile are **TODO-VERIFY**. Until then, fill recipes may use `--nopileup`.
- DY σ (M>50, 13.6 TeV) is **TODO-VERIFY** — do not reuse 13 TeV 6077.22 pb.

### 5. Low-Δ2D sideband / bkg-shape systematic

- Default: linear poly on mass sidebands; low-Δ2D normalization via `normrange` (recipe: `[0, 2]` cm; AN historically also discusses ≲ 0.5 cm — keep configs consistent with method §2.6).
- Higher 2024 PU can stress the lowest Δ2D bin: inspect fit quality / χ² there before freezing.
- **TODO (later):** vary sideband poly degree and/or sideband windows as a **background-shape systematic** in the SF envelope (method §2.8 / plan §6).

### 6. Era C–I split diagnostic

- Sample list already enumerates Muon0/1 PromptReco stubs for **Run2024C–I**.
- First \(C(\Delta_{2D})\) freeze target remains **Run2024D** only.
- **TODO (later):** produce per-era \(C\) as a diagnostic (stability vs era) before combining; do not silently merge C–I without that check.

### 7. `efficiencystudy/` absolute ε vs \(C(\Delta_{2D})\)

- v1 deliverable is the **Data/MC calibration factor** \(C(\Delta_{2D})\), not absolute tracking efficiency.
- Absolute ε in `efficiencystudy/` needs **custom GEN** (or equivalent) that retains **all generated \(K_S^0\)**, not only those that match the reco selection — otherwise GEN denominators are biased.
- Treat absolute ε as optional M11; do not confuse it with \(C(\Delta_{2D})\) SF export.

---

## Pre-freeze gate (honest)

Do **not** claim these until executed on lxplus / CMSLPC:

- [ ] Live DAS freeze for Muon0/1 + Summer24 DY
- [ ] Golden / PU JSON + `brilcalc` \(\mathcal{L}\) for the frozen era
- [ ] DeepJet loose WP from CVMFS BTV JSON (not `0.0494`)
- [ ] `cmsrel` / `scram b` / one-file `cmsRun` data + MC (see [cmsrun-smoke-test.md](cmsrun-smoke-test.md))
- [ ] CRAB smoke → full; sideband fits; `mcvsdata_fill`; SF JSON

Package placement for scram (Neon):
`$CMSSW_BASE/src/K0sAnalysis/DisplacedV0`
(two-level Subsystem/Package). Repo path:
`ntuplizer/K0sAnalysis/DisplacedV0`. Symlink:
`ln -s …/ntuplizer/K0sAnalysis K0sAnalysis` under `$CMSSW_BASE/src`.

Source: Project Context `docs/gemini-neon-review-2026-11-24.md` (Neon paste); AN-20-111; this repo’s method/plan docs.
