# Implementation plan: displaced-track efficiency (Run 3 / 2024)

**Physics method (do not re-derive):** [`docs/displaced-track-efficiency-run3-2024.md`](displaced-track-efficiency-run3-2024.md)  
**Source AN:** AN-20-111 v4; public DP-2024-010; reference code [K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis).

This document is an **actionable build plan** for a CMS analyzer: packages, releases, samples, ntuple → offline stages, validation, milestones, and open decisions for Long Wang. It assumes the method doc is approved.

---

## 0. Recommended strategy (one paragraph)

**Fork and extend K0sAnalysis**, do not rewrite the physics pipeline from scratch. That repo already encodes AN-20-111 end-to-end: MiniAOD `V0Analyzer` (Kalman V0 from `packedPFCandidates` + `lostTracks`), CRAB submission, DY skimming, V0 building, sideband fits, and data/MC \(C(\Delta_{2D})\) filling/plotting. The Run 3 job is to (1) port the CMSSW ntuplizer into a **2024 MiniAOD** release, (2) retarget datasets/triggers/JSON/PU/DeepJet/SFs, and (3) keep the offline Python analysis largely intact with config updates. A greenfield CMSSW analyzer only makes sense if the HNL/LLP group already has a maintained MiniAOD ntuplizer and prefers to **transplant** `V0Analyzer.cc` into that framework (K0sAnalysis README explicitly allows this).

---

## 1. Repo / package layout

### 1.1 Recommendation

| Option | When to choose | Verdict |
| --- | --- | --- |
| **A. Fork K0sAnalysis → `K0sAnalysisRun3` (or group gitlab)** | Default; want AN-faithful \(C(\Delta_{2D})\) fast | **Preferred** |
| **B. Transplant `V0Analyzer` into existing LLP ntuplizer** | Group already CRAB-produces MiniAOD ntuples for HNLs | OK if V0 branches match §4 |
| **C. New standalone CMSSW package** | Only if A/B are blocked (license/ownership/arch) | Avoid for first pass |

### 1.2 Proposed tree (fork of K0sAnalysis, Run 3 naming)

```text
K0sAnalysisRun3/                    # git fork; main branch = Run3 port
├── README.md                       # point to method doc + this plan
├── docs/
│   ├── method.md                   # symlink/copy of approved method
│   └── implementation-plan.md      # this file
├── ntuplizer/
│   └── DisplacedV0/                # slim CMSSW package (see §1.3)
│       ├── plugins/DisplacedV0Ntuple.cc
│       ├── src/V0Analyzer.cc       # port from K0sAnalysis/.../V0Analyzer.cc
│       ├── interface/V0Analyzer.h
│       ├── python/displacedV0_cfi.py
│       └── test/crab_common.py, crab_data_2024{,_muon1,_smoke}.py, crab_mc_dy{,_smoke}.py
├── skimming/                       # keep K0sAnalysis skim scripts; update triggers
├── v0building/                     # if present upstream; else keep offline rebuild
├── fitting/                        # fitinvmass*, count_peak — reuse
├── analysis/                       # mcvsdata_* + configs — update eras
├── efficiencystudy/                # optional absolute ε from signal MC (later)
├── samples/                        # NEW: DAS lists, JSON pointers, HLT lists
│   ├── data_muon_2024.txt
│   ├── sim_dy_m50_13p6.txt
│   └── cert/README.md              # where to fetch golden + PU JSON
└── scripts/
    ├── das_discover.sh             # §3 checklist automation
    ├── submit_ntuples.sh
    └── make_sf_json.py             # C(Δ2D) → correctionlib/JSON export
```

Upstream K0sAnalysis already has: `ntuplizer/heavyNeutrino/multilep` (full HNL ntuplizer + `V0Analyzer`), `skimming/`, `analysis/`, `fitting/`, `efficiencystudy/`, `dps/`. For Run 3, **either** keep the heavyNeutrino submodule layout **or** extract a minimal `DisplacedV0` package that only runs trigger filter + muon/jet/PV + V0 + weights. Minimal package is easier to scram-build on `CMSSW_14_0_X` / `15_0_X`.

### 1.3 CMSSW modules (names)

| Module | Type | Role |
| --- | --- | --- |
| `DisplacedV0Ntuple` | `EDAnalyzer` or `EDFilter`+`EDAnalyzer` | Event loop, TTree fill |
| `V0Analyzer` | helper class (as upstream) | Track preselection, OS pairs, Kalman SV, \(K_S/\Lambda\) hyp. |
| `TriggerAnalyzer` | helper | HLT bits for dimuon paths |
| `LeptonAnalyzer` (subset) | helper | Medium muon ID, \(p_T,\eta\), Rochester if available |
| `JetAnalyzer` (subset) | helper | AK4 PUPPI + DeepJet score |
| `crab_*.py` | CRAB3 configs | Per-era data + DY MC |

### 1.4 Offline scripts (reuse / rename)

| Upstream | Keep for Run 3? | Notes |
| --- | --- | --- |
| `fitting/fitinvmass*.py`, `count_peak.py` | Yes | Sideband linear bkg per \(\Delta_{2D}\) bin |
| `analysis/mcvsdata_fill.py` | Yes | Fill yields vs `rpv` / \(\Delta_{2D}\) |
| `analysis/config_ksvars*.py` | Yes | Point paths to 2024 ntuples; binning from method §2.6 |
| `analysis/config_ks2dvars*.py` | Yes | \(C(\Delta_{2D},p_T)\) |
| `analysis/mcvsdata_submit*.py` | Yes | Condor/local batch |
| `dps/` | Later | Public-style plots after first \(C\) exists |

---

## 2. CMSSW / release / campaign

### 2.1 What to look up (do not hardcode stale GTs in production configs)

At implementation start, resolve from **PdmV / cms-talk / `Configuration/AlCa/python/autoCond.py`** in the chosen release:

| Item | Where to look | Typical 2024 pointer (verify!) |
| --- | --- | --- |
| CMSSW release matching MiniAOD campaign | Dataset name contains `140X_…` or `MiniAODv6` → release series | **`CMSSW_14_0_X`** for Summer24 MiniAOD/`140X_*`; **`CMSSW_15_0_X`** if reading MiniAODv6+ later JECs |
| Data GT | `auto:run3_data` or `auto:run3_data_prompt` | e.g. historically `140X_dataRun3_v*` — **use autoCond alias** |
| MC GT | `auto:phase1_2024_realistic` | e.g. `140X_mcRun3_2024_realistic_v26` (and successors in 15_0) |
| Era | cmsDriver / PdmV | Data: `Run3`; MC: `Run3_2024` |
| SCRAM_ARCH | release notes | `el8_amd64_gcc12` (14_0) or current for 15_0 |

**Rule:** store aliases (`auto:run3_data`, `auto:phase1_2024_realistic`) in configs; pin exact GT strings only in a `conditions.md` snapshot filled on the day of first CRAB submit.

### 2.2 Suggested starting point

1. Identify the **exact MiniAOD dataset** for one 2024 era (PromptReco or rereco) on DAS.
2. Read the `140X_…` / `150X_…` token in the dataset name → choose matching `cmsrel`.
3. `cmsrel` + check out minimal `DisplacedV0` package + `scram b`.
4. Local `cmsRun` on **one** data file and **one** DY file before CRAB.

### 2.3 Campaign labels (patterns)

- Data: `Run2024B` … `Run2024I` (and any later letters) PromptReco and/or re-MiniAOD campaigns.
- MC: `RunIII2024Summer24MiniAOD` / `Run3Summer24MiniAODv*` with `13p6TeV` in the primary dataset name.

Split analysis **per data-taking era** (and per reco campaign if both Prompt and rereco exist); combine only after §6 checks.

---

## 3. Input samples

### 3.1 Dataset name patterns (resolve exact strings on DAS)

**Data**

```text
/Muon*/Run2024*-PromptReco-v*/MINIAOD
/Muon*/Run2024*-*MiniAOD*/MINIAOD          # if central re-MiniAOD exists
/DoubleMuon*/Run2024*-*/MINIAOD            # only if still published; prefer Muon PD in Run 3
```

**MC**

```text
/DYJetsToLL_M-50_TuneCP5_13p6TeV-amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD*/MINIAODSIM
/DYJetsToLL_M-50_TuneCP5_13p6TeV-amcatnloFXFX-pythia8/Run3Summer24MiniAOD*/MINIAODSIM
```

(If FxFx sample missing for the reco campaign, fall back to the PdmV-recommended DY alternative — document the choice; do not mix generators in one \(C\) without a dedicated systematic.)

**Do not invent full DAS names.** Commit the resolved list under `samples/*.txt`.

### 3.2 JSON / luminosity / PU

| File | Pattern / location |
| --- | --- |
| Golden JSON | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_*_Golden.json` |
| Muon JSON (optional) | same directory; use if analysis is muon-only certified |
| PU profile | Collisions24 `PileUp/` JSON / `pileup_JSON.txt`; build MC weights with recommended `pileupCalc` / correctionlib recipe |
| Lumi | `brilcalc` on certified LS of processed eras |

### 3.3 HLT paths

**Baseline (logical OR of whatever exists in the era menu):**

- `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`

**Check and document if present:**

- `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8`
- Any non-`TkMu` companions in the 2024 GRun menu for Muon PD

**Exclude:** displaced-dimuon / LLP parking / scouting paths (bias).

### 3.4 CRAB / dataset discovery checklist

```bash
# 1) List candidates
dasgoclient -query="dataset=/Muon*/Run2024*/MINIAOD" | sort
dasgoclient -query="dataset=/DYJetsToLL_M-50*13p6TeV*amcatnloFXFX*/Run*2024*MiniAOD*/MINIAODSIM" | sort

# 2) Pick one era + matching MC campaign; record site availability
dasgoclient -query="site dataset=<NAME>"

# 3) Confirm MiniAOD (not Nano) and GT token in name
# 4) Download golden JSON for the run range of that era
# 5) brilcalc lumi -u /fb --normtag <current> -i Cert_....json --begin/--end
# 6) Crab: one smoke job (≤ few 1/fb or 50k MC events) → full submit
# 7) Freeze samples/data_muon_2024.txt + samples/sim_dy_m50_13p6.txt + conditions.md
```

---

## 4. Ntuple / producer stage

### 4.1 Collections to read (MiniAOD)

| Collection | Product | Use |
| --- | --- | --- |
| `slimmedMuons` | muons | DY tag |
| `slimmedJets` / PUPPI jets | jets | DeepJet \(b\)-veto |
| `offlineSlimmedPrimaryVertices` | PV | hardest PV; \(\Delta_{2D}\) |
| `packedPFCandidates` | tracks | V0 daughters |
| `lostTracks` | tracks | AN §6 high-purity non-PF tracks |
| `TriggerResults` + HLT prescales if needed | bits | dimuon HLT |
| `GenInfo` / pileupSummary / `generator` | MC | `genWeight`, \(\mu\), xsec bookkeeping |
| (optional) `prunedGenParticles` | MC | V0 truth-match closure |

**Stay on MiniAOD.** Standard NanoAOD does not expose `lostTracks` / full track quality needed for the AN V0 fitter unless a custom Nano is produced from the same MiniAOD.

### 4.2 Skim cuts: CMSSW vs offline

| Cut | Where | Rationale |
| --- | --- | --- |
| HLT dimuon OR | **CMSSW filter** | Huge rate reduction for CRAB |
| ≥2 muons loose \(p_T>20\), \(\lvert\eta\rvert<2.4\) | **CMSSW** (optional soft preselection) | Shrink ntuples |
| Exact medium ID, \(30/25\), \(\lvert m_{\mu\mu}-m_Z\rvert<10\), \(b\)-veto | **Offline skim** | Easy to vary for systematics |
| V0 reconstruction | **CMSSW (`V0Analyzer`)** preferred | Kalman vertexing + track DCA tools already in CMSSW; matches upstream |
| Sideband fits / \(C\) | **Offline** | RooFit/scipy iteration without re-ntupling |

Alternative (open decision §8): write only tracks+muons+jets and rebuild V0 offline — more flexible, slower, higher ntuple size; only if porting `V0Analyzer` stalls.

### 4.3 Objects / branch list sketch

**Event**

- `run`, `luminosityBlock`, `event`
- `nPV`, `PV_x,y,z`, `PV_ndof`
- `Pileup_nTrue` (MC), `genWeight` (MC)
- HLT flags: `HLT_Mu17_…_Mass3p8`, …
- `eventWeight` (placeholder filled offline with PU×SF)

**Muons** (variable length)

- `Muon_pt,eta,phi,charge,dxy,dz`
- `Muon_mediumId`, `Muon_pfIso…` (if kept)
- `nMuon`

**Jets**

- `Jet_pt,eta,phi`, `Jet_btagDeepFlavB` (or Run 3 DeepJet branch name), `Jet_jetId`
- `nJet`

**V0 candidates** (filled by `V0Analyzer`; one entry per fitted candidate)

- `V0_pt,eta,phi,mass_pipi,mass_ppi,mass_pip`
- `V0_vx,vy,vz`, `V0_delta2D` (\(\Delta_{2D}\)), `V0_delta2DErr`, `V0_delta2DSig`
- `V0_chi2ndof`, `V0_cosPointing`, `V0_dca`
- `V0_category` (`KS` / `LA` / `LABAR`)
- Daughter: `V0_trk1_pt,…`, hits, \(\chi^2\), IP sig, charge; same for `trk2`
- (MC) `V0_isMatched`, `V0_genDelta2D`

Keep ntuple lean: do **not** dump all packed PF candidates after V0 is built in CMSSW.

### 4.4 Local smoke test

```text
cmsRun python/test_data_onefile_cfg.py   # 100–1000 events
cmsRun python/test_mc_onefile_cfg.py
→ inspect Tree: nMuon, nV0, mass_pipi peak near 0.498
```

---

## 5. Offline analysis stages

### 5.1 Pipeline

```text
MiniAOD ──(CRAB/DisplacedV0Ntuple)──► ntuple ROOT
         ──(skimming: DY selection)──► skimmed ROOT
         ──(optional v0building)─────► V0 trees (if not done in CMSSW)
         ──(fitting: sidebands)──────► per-bin yields N_data, N_MC
         ──(analysis: norm + C)──────► C(Δ2D), C(Δ2D,pT)
         ──(plots + SF export)───────► PNG/PDF + JSON/correctionlib
```

### 5.2 Stage details

1. **Event selection (skim)**  
   Exactly 2 medium muons; \(p_T>30/25\); \(\lvert m_{\mu\mu}-m_Z\rvert<10\,\mathrm{GeV}\); veto loose DeepJet; apply golden JSON (data); apply PU + muon ID/trig SFs (MC). Fill DY controls: muon \(p_T,\eta\), \(m_{\mu\mu}\), \(n_{\mathrm{PV}}\).

2. **V0 selection**  
   Apply AN numerical cuts (method §1.4) if not already applied in CMSSW; classify \(K_S^0\); keep \(\Lambda\) in a parallel tree for diagnostics.

3. **Mass sideband fits per \(\Delta_{2D}\) bin**  
   Reuse `fitting/fitinvmass*.py`: linear poly on sidebands, subtract under peak, `count_peak`. Produce `yields_ks_<era>.root` with data and MC histograms vs \(\Delta_{2D}\) (and 2D vs \(p_T\)).

4. **Low-\(\Delta_{2D}\) normalization**  
   Choose \(\mathcal{N}\) (start: first 1–2 bins with healthy S/B); \(k=\sum_{\mathcal{N}} N^{\mathrm{data}}/\sum_{\mathcal{N}} N^{\mathrm{MC}}\); scale MC.

5. **Form \(C\)**  
   \(C_i=N_i^{\mathrm{data}}/(k N_i^{\mathrm{MC}})\); statistical errors from subtracted yields; write `C_delta2D_<era>.{root,json}`.

6. **Plots + SF tables**  
   AN-style: yields vs \(\Delta_{2D}\) (data/MC), ratio \(C\), mass fits gallery, pixel-layer markers at 2.9/6.8/10.9/16.0 cm. Export SF JSON for LLP analyses.

### 5.3 Tooling preference (rationale)

| Layer | Preference | Why |
| --- | --- | --- |
| Ntuple | **CMSSW C++** (`V0Analyzer`) | Kalman vertex + track tools; proven in AN code |
| Skim / histogram fill | **PyROOT / uproot + awkward** *or* keep upstream PyROOT scripts | uproot scales on lxplus/condor; upstream scripts already match AN plots — **port configs first, migrate to uproot only if I/O is painful** |
| Sideband fits | **ROOT RooFit** (as in `fitting/`) **or** `scipy`/`iminuit` | RooFit matches AN; scipy fine if team prefers pure Python — **open decision** |
| Batch plots | mplhep + CMS style **or** upstream ROOT plots | Either OK; freeze one style early |
| RDataFrame / coffea | Optional later | Good for large skims; not required to reproduce AN path |

**Default recommendation:** keep **K0sAnalysis Python+ROOT fitting** for v1 \(C(\Delta_{2D})\); introduce coffea/RDataFrame only if ntuple volume forces it.

---

## 6. Validation / closure

Execute before declaring a 2024-era \(C\) usable:

| # | Test | Pass criterion |
| --- | --- | --- |
| 1 | DY controls (muon \(p_T,\eta\), \(m_{\mu\mu}\), \(n_{\mathrm{PV}}\)) | Data/MC flat within ~10–20% before V0 norm; no pathological holes |
| 2 | \(K_S\) mass peak | Fitted mass ~ PDG; width sane; sideband fit \(\chi^2\) OK |
| 3 | Low-\(\Delta_{2D}\) agreement after norm | \(C\approx 1\) in \(\mathcal{N}\) by construction; neighboring bins stable |
| 4 | Pixel layer structure | Steps/features at Phase-1 radii in data **and** MC |
| 5 | Norm-region ±1 bin | Large-\(\Delta_{2D}\) \(C\) moves within planned systematic |
| 6 | Sideband degree 0 vs 1 / peak window | Envelope assigned as systematic |
| 7 | Era split (e.g. early vs late 2024) | Compare \(C\); difference → conditions systematic |
| 8 | PU tertiles | \(C(\Delta_{2D})\) compatible or inflate PU unc. |
| 9 | \(\Lambda^0\) diagnostic | Runs; expect worse low-\(\Delta_{2D}\) S/B (AN) |
| 10 | MC closure | Inject known \(\varepsilon(\Delta_{2D})\) loss in MC copy; recovered \(C\) tracks injection |
| 11 | Optional \(Z\to ee\) | No large systematic difference vs \(\mu\mu\) (AN) |

---

## 7. Milestones (ordered checklist)

Effort is **relative** (S / M / L) plus dependencies — not calendar duration.

| ID | Milestone | Effort | Depends on | Exit criterion |
| --- | --- | --- | --- | --- |
| **M0** | Decisions locked (§8) | S | Method doc approved | Written answers from Long Wang |
| **M1** | Empty fork + README pointing to method/plan | S | M0 | Repo exists; CI optional |
| **M2** | Resolve DAS samples + JSON + HLT list for **one** era (e.g. Run2024F or current best-certified) | S | M0 | `samples/*.txt` + `conditions.md` filled |
| **M3** | `cmsrel` + `DisplacedV0` builds; local `cmsRun` on 1 data + 1 MC file | M | M2 | Trees with muons + V0 mass peak visible |
| **M4** | CRAB smoke (small) → full ntuple for **one** data era + DY MC | M–L | M3 | Skim-ready ntuples on EOS/T2 |
| **M5** | Offline DY skim + control plots | S–M | M4 | AN Fig. 5-style controls signed off |
| **M6** | Sideband fits → background-subtracted yields vs \(\Delta_{2D}\) | M | M5 | Mass-fit gallery; yield histograms |
| **M7** | Low-\(\Delta_{2D}\) norm → **first \(C(\Delta_{2D})\)** for that era | S | M6 | Plot + table of \(C_i\) with stats errors |
| **M8** | Validation pack (§6 items 1–8) | M | M7 | Short validation note; freeze v1 SFs |
| **M9** | Add remaining 2024 eras; era-combine; 2D \(C(\Delta_{2D},p_T)\) | L | M8 | Combined 2024 SF file |
| **M10** | Systematics envelope + correctionlib/JSON export | M | M9 | Usable by LLP analysis |
| **M11** (optional) | Absolute \(\varepsilon\) on signal MC; \(J/\psi\) outlook | L | M8+ | Separate from v1 deliverable |

**Critical path to “first \(C(\Delta_{2D})\) on a 2024 era”:** M0 → M2 → M3 → M4 → M5 → M6 → **M7**.

---

## 8. Open decisions (Long Wang)

Please decide before M3/M4 full submit:

1. **Reuse path:** Fork K0sAnalysis (A) vs transplant `V0Analyzer` into existing HNL ntuplizer (B)?  
   - *Default if no answer:* **A**.

2. **V0 where?** Build V0 in CMSSW (recommended) vs store tracks and rebuild offline?  
   - *Default:* **CMSSW `V0Analyzer`**.

3. **Reco campaign:** PromptReco MiniAOD vs wait for central re-MiniAOD (MiniAODv6 / equivalent) for the first era?  
   - *Default for speed:* **PromptReco for first \(C\)**, repeat on rereco when available as systematic.

4. **Fitting language:** Keep ROOT RooFit scripts vs pure Python (`iminuit`/`scipy`)?  
   - *Default:* **keep RooFit / upstream `fitting/`**.

5. **Which first era?** Pick one well-certified 2024 era with good lumi and stable HLT (suggest mid-year era with largest certified \(\mathcal{L}\)).  
   - *Needs:* DAS + golden JSON check.

6. **Group hosting:** GitHub personal fork vs CMS GitLab under EXO/B2G/LLP subgroup?  
   - Affects CRAB code visibility and authorship.

7. **SF consumer format:** plain ROOT TH1, JSON table, or correctionlib?  
   - *Default:* **JSON + ROOT**; correctionlib if LLP framework already uses it.

8. **Scope freeze for v1:** \(K_S^0\) + \(\mu\mu\) only (yes/no to \(\Lambda\), \(ee\), \(J/\psi\) in v1)?  
   - *Default:* **\(K_S+\mu\mu\) only** for M7–M8.

---

## 9. Immediate next actions (this week’s work queue)

1. Answer §8 decisions (esp. 1, 3, 5).  
2. Run §3.4 DAS discovery; commit sample lists.  
3. `cmsrel` matching the chosen MiniAOD; drop in `V0Analyzer` and prove local mass peak.  
4. CRAB smoke on that era + DY.  
5. Port `fitting/` + `analysis/config_ksvars*.py` paths → produce first \(C(\Delta_{2D})\).

---

## 10. References

- Method: `docs/displaced-track-efficiency-run3-2024.md`
- AN-20-111 v4; DP-2024-010
- https://github.com/LukaLambrecht/K0sAnalysis (`V0Analyzer`, `fitting/`, `analysis/`)
- CMSSW autoCond / PdmV for GTs; Collisions24 golden JSON under DQM CAF
