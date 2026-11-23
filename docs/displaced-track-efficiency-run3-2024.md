# Displaced track / vertex reconstruction efficiency for CMS Run 3 (2024)

**Reference:** CMS AN-20-111 v4, *Study of displaced vertex reconstruction using light neutral hadrons in Drell-Yan events* (L. Lambrecht; archive 2024/02/21). Related public DP: CERN-CMS-DP-2024-010. Reference implementation: [K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis).

**Scope of this note:** Adapt the AN-20-111 method to measure (more precisely: *calibrate*) displaced tracking and secondary-vertex reconstruction for **2024 Run 3** \(pp\) data at \(\sqrt{s}=13.6\,\mathrm{TeV}\), and provide an actionable recipe for a CMS analyzer.

**Important conceptual point (AN §§1, 3):** Classic Drell–Yan lepton tag-and-probe is **not** suitable for heavily displaced tracks. AN-20-111 instead uses an **unbiased reference event** (\(Z\to\mu^+\mu^-\)) plus **SM V\(^0\) probes** (\(K_S^0\to\pi^+\pi^-\), optionally \(\Lambda^0\to p\pi^-\)) whose reconstructed yields vs radial displacement \(\Delta_{2D}\) calibrate data/MC modeling of displaced tracking+vertexing. That mapping is retained below; where this document says “tag / probe”, it means that reference-event / V\(^0\)-probe construction, not lepton T&P.

---

## 1. Summary of the AN-20-111 method (what to adapt)

### 1.1 Physics goal

Analyses of long-lived particles (LLPs), especially heavy neutral leptons (HNLs), rely on simulated efficiencies for tracks and secondary vertices with large transverse displacement from the beamline / primary vertex (PV). Simulation of displaced objects is not guaranteed to match data. AN-20-111 therefore measures **data/MC ratios of reconstructed \(K_S^0\) (and \(\Lambda^0\)) vertex yields vs \(\Delta_{2D}\)** and promotes those ratios to **correction factors and/or systematic uncertainties** on displaced tracking+vertexing [AN §§1, 8–9].

Typical Run 2 UL result: agreement within ~10–15% at large \(\Delta_{2D}\) (worse in early-2016 APV-saturation data) [AN §8].

### 1.2 Reference object (“tag”) and probes

| Role | Object | Purpose |
| --- | --- | --- |
| **Reference / tag event** | \(Z\to\mu^+\mu^-\) (exactly two medium-ID muons near \(m_Z\)) | Clean, well-modeled sample; dimuon triggers are **unbiased w.r.t. hadronic V\(^0\)s** [AN §3] |
| **Primary probe** | \(K_S^0\to\pi^+\pi^-\) | Dominant probe; mean \(\Delta_{2D}\sim 16\,\mathrm{cm}\) at typical \(p_T\) [AN Tab. 1] |
| **Cross-check probe** | \(\Lambda^0\to p\pi^-\) (\(\bar\Lambda^0\to\bar p\pi^+\)) | Same vertexing chain; discarded as main result in AN because of large low-\(\Delta_{2D}\) background / low stats [AN §7] |

Probes are reconstructed from **underlying-event / jet tracks** in the same DY events, not from the tagging muons.

### 1.3 Event selection (AN §5)

- Dataset: Run 2 `DoubleMuon` primary datasets; cocktail of dimuon HLTs (logical OR) [AN Tab. 4].
- Exactly **2** muons with Muon-POG **medium** ID.
- Leading (trailing) muon \(p_T > 30\,(25)\,\mathrm{GeV}\).
- \(|m_{\mu\mu}-m_Z| < 10\,\mathrm{GeV}\).
- Veto ≥1 **loose** \(b\)-tagged jet (DeepCSV WP of the era).
- Control plots: muon \(p_T\), \(\eta\), \(m_{\mu\mu}\) data/MC [AN Fig. 5].
- Cross-check: analogous \(Z\to e^+e^-\) selection (no systematic difference observed) [AN §5].

### 1.4 Probe (V\(^0\)) reconstruction (AN §6)

Tiered selection on MiniAOD (not RECO), starting from `packedPFCandidates` + `lostTracks`:

**Tracks**

- Tracking-POG **loose** quality.
- Track-fit \(\chi^2/\mathrm{ndof} < 5\).
- ≥ 6 valid hits.
- \(p_T > 1\,\mathrm{GeV}\) (added vs stock V0 fitter to mimic LLP selections).
- Transverse IP significance \(> 2\).

**Pairs**

- Opposite charge.
- Distance of closest approach (DCA) \(< 0.2\,\mathrm{cm}\).
- Point of closest approach inside cylinder \(R < 120\,\mathrm{cm}\), \(|z| < 150\,\mathrm{cm}\) (length 300 cm).

**Vertices (Kalman fitter)**

- Vertex \(\chi^2/\mathrm{ndof} < 7\).
- \(\cos\theta_{\mathrm{pointing}} > 0.99\) (pointing angle between transverse SV position vector and sum-\(p_T\) of the two tracks) — replaces RECO-only “inner hit” cut.
- Mass windows: \(|m_{\pi\pi}-m_{K_S^0}| < 70\,\mathrm{MeV}\) or \(|m_{p\pi}-m_{\Lambda}| < 50\,\mathrm{MeV}\); assign \(K_S^0\) vs \(\Lambda\) by which hypothesis is closer.
- Deliberately **omit** \(\Delta_{2D}/\sigma(\Delta_{2D})\) cut used in stock V0 fitter to keep low-displacement candidates for normalization [AN §6].

### 1.5 Background subtraction, normalization, “efficiency” definition (AN §7)

**Background:** Per \(\Delta_{2D}\) bin, fit a **linear** polynomial to the invariant-mass **sidebands**, subtract under the peak, count remaining signal in the peak window [AN Figs. 10–11]. (Tighter mass windows alone were tried and abandoned.)

**Normalization:** Do **not** normalize to total event count. Instead normalize MC \(K_S^0\) yield to data using **small-\(\Delta_{2D}\)** bins only, so overall \(K_S^0\) production mismodeling factors out and the residual vs \(\Delta_{2D}\) isolates displaced reco mismodeling [AN §7].

**Calibration factor (the working “efficiency” observable):**

\[
C(\Delta_{2D}) \;=\; \frac{N^{\mathrm{data}}_{K_S^0}(\Delta_{2D})}{N^{\mathrm{MC}}_{K_S^0}(\Delta_{2D})}\Bigg|_{\text{bkg-sub.},\;\text{norm. at low }\Delta_{2D}}.
\]

Optionally extend to 2D: \(C(\Delta_{2D},\,p_T^{K_S^0})\) [AN Figs. 18–19]. Absolute per-track reconstruction efficiency is **not** measured in data; absolute \(\varepsilon(\Delta_{2D})\) still comes from signal MC, with \(C\) (or \(1-C\)) applied as SF / uncertainty [AN §§1, 8–9].

**Displacement variable:** \(\Delta_{2D}\) = transverse distance of the fitted secondary vertex from the PV (same convention as the HNL analyses using this calibration). Also monitor \(\Delta_{2D}/\sigma(\Delta_{2D})\) and pixel-layer structure in the \(\Delta_{2D}\) spectrum [AN §§8, Figs. 15–17].

### 1.6 Systematics / limitations called out in the AN

AN quotes primarily **statistical** uncertainties on \(C\); recommended improvements [AN §9]:

- Full POG muon/jet/PU corrections + their variations (expected small after in-situ low-\(\Delta_{2D}\) norm).
- Sideband-fit / peak-window / normalization-bin choice.
- Probe \(p_T\) spectrum much softer than LLP leptons → 2D \((\Delta_{2D},p_T)\) factors; outlook: non-prompt \(J/\psi\to\ell\ell\) from \(B\) decays.
- Custom V0 selection vs analysis-specific DV algorithm (data/MC ratio expected more robust than absolute \(\varepsilon\)).
- APV saturation (2016-specific; irrelevant for 2024).
- Pre-legacy vs UL reprocessing differences (lessons for Run 3 prompt vs rereco).

---

## 2. Run 3 / 2024 adaptation

### 2.1 What stays the same

- Core logic: DY dimuon reference + MiniAOD custom V0 fitter + sideband bkg + low-\(\Delta_{2D}\) normalization → \(C(\Delta_{2D})\) [AN §§3, 6–7].
- Probe particles: \(K_S^0\) primary; \(\Lambda^0\) as diagnostic only unless V0 cuts are re-optimized.
- Track / pair / vertex cut skeleton in §1.4 (re-validate thresholds; do not invent a new method).
- Pixel barrel radii defining geometric features in \(\Delta_{2D}\): Phase-1 layers at **29, 68, 109, 160 mm** (same as 2017–2018) [AN §1, Fig. 2].
- Unbiased-trigger principle: select on prompt dimuons, never on the V0.
- Deliverable use of \(C\): scale factors and/or LLP analysis systematics on displaced tracks/vertices.

### 2.2 What must change for Run 3 / 2024

| Topic | Run 2 (AN) | Run 3 / 2024 proposal |
| --- | --- | --- |
| Collision energy | 13 TeV | **13.6 TeV** |
| Geometry | Phase-0 (2016) / Phase-1 (2017–18) | **Phase-1** (same as 2017–18); no Phase-2 tracker yet |
| Conditions / APV | Early-2016 APV saturation dominant [AN §4, 8] | **No APV saturation**; watch Run 3 strip/pixel dynamic inefficiencies + alignment campaigns instead |
| Pileup | Run 2 (~20–50) | **Higher average PU**; PU reweighting mandatory; study \(C\) vs PU bins |
| Tracking | Run 2 iterations | **Run 3 CMSSW tracking** (updated seeding/iterations, displaced/low-\(p_T\) improvements). Re-measure \(C\); do not inherit Run 2 UL numbers |
| Triggers | Tab. 4 cocktail | Prefer **`HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`** (+ document any era-specific companions in the 2024 HLT menu); drop obsolete `TkMu*` paths |
| Primary datasets | `DoubleMuon` | **`/Muon*/Run2024*-*MiniAOD*`** and/or `/DoubleMuon*/...` as present in DAS for each era — **look up exact DAS names**; do not invent |
| MC | `DYJetsToLL_M-50` 13 TeV amc@NLO FxFx + Pythia8 CP5 | Matching **13p6TeV** DY MiniAODSIM (Summer24 / Winter24-style campaign); CP5 (or current Run 3 recommendation) |
| Formats | MiniAOD (packed PF + lost tracks) | **Stay on MiniAOD** for the V0 chain. NanoAOD lacks the track content used in AN §6 unless a custom Nano is produced |
| \(b\)-veto | DeepCSV loose | **DeepJet** (or ParticleNet) loose WP recommended for 2024 by BTV |
| Muon ID / SFs | Medium ID | Keep medium (or tight if analysis requires); apply **2024 muon ID/ISO/trigger SFs** via correctionlib |
| Lumi / JSON | Run 2 golden JSONs | **`Cert_Collisions2024_*_Golden.json`** (e.g. run range ~378981–386951; refresh from DQM CAF). Prefer muon JSON if analysis is muon-only |
| Eras | 2016/17/18 (+ HIPM split) | Split **Run2024 eras (B–I/…)** and any mid-year alignment / HLT / reconstruction breaks; combine only after per-era agreement |
| Absolute \(\varepsilon\) MC | Signal MC with Run 2 geometry | Recompute LLP \(\varepsilon(\Delta_{2D})\) with **Run 3 geometry + 2024 conditions**; apply 2024 \(C\) |

### 2.3 Proposed datasets and triggers (lookup required)

**Data (patterns — resolve on DAS / PdmV):**

- `/Muon*/Run2024[B-I]-*MiniAOD*/NANOAOD` → use the **MiniAOD** parent, not NanoAOD, for this measurement.
- Apply golden JSON: `/eos/.../Collisions24/Cert_Collisions2024_*_Golden.json`.
- Integrated luminosity: from brilcalc on the certified lumisections used.

**MC (pattern):**

- `/DYJetsToLL_M-50_TuneCP5_13p6TeV-amcatnloFXFX-pythia8/Run3Summer24MiniAODv*.../MINIAODSIM` (exact string from DAS).
- Cross section: use current genXsec / XSDB value for \(M_{\ell\ell}>50\,\mathrm{GeV}\) at 13.6 TeV (do not reuse 6077.22 pb blindly).
- Weights: `genWeight` × \(\sigma\) × \(\mathcal{L}\) / \(\sum w\); pileup weights to data PU profile.

**Triggers (logical OR if multiple exist in menu):**

- Baseline: `HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8`
- Confirm 2024 menu for any `Mass8`, parking, or scouting variants; **do not** include displaced-dimuon LLP triggers in the reference selection (would bias the sample).

### 2.4 Object definitions (2024)

**Muons (tag event)**

- PF / slimmed muons, Muon-POG **medium** ID, \(p_T > 30 / 25\,\mathrm{GeV}\), \(|\eta|<2.4\).
- Prefer tracker+global quality consistent with medium ID; apply Rochester (or current muon momentum) corrections if recommended for 2024.
- Isolation: not required beyond what medium ID implies for DY purity; optional tight ISO for a purity cross-check.

**Jets / \(b\)-veto**

- AK4 PUPPI (Run 3 default) jets, \(p_T>30\,\mathrm{GeV}\), \(|\eta|<2.5\), jet ID pass.
- Veto events with ≥1 jet above the **loose DeepJet** WP (era-specific; BTV JSON).

**Tracks / V0 probes**

- Collections: `packedPFCandidates` charged tracks + `lostTracks` (high-purity tracks not in PF), as in AN §6.
- Same numerical cuts as §1.4 initially; re-optimize only if 2024 PU forces it (document any change).
- Primary vertex: hardest PV (standard CMS definition); \(\Delta_{2D}\) w.r.t. that PV.

**Matching / assignment**

- Between mass hypotheses: assign \(K_S^0\) if \(\lvert m_{\pi\pi}-m_{K_S}\rvert\) is smaller than both \(\lvert m_{p\pi}-m_{\Lambda}\rvert\) hypotheses (AN §6).
- Optional purity check in MC: match both daughter tracks to gen \(\pi^\pm\) from \(K_S^0\) within \(\Delta R<0.03\) and compare gen vs reco \(\Delta_{2D}\) (closure only; not used in data formula).

### 2.5 Efficiency / calibration formula

Per bin \(i\) in \(\Delta_{2D}\) (and optionally \(p_T^{K_S}\), \(|\eta^{K_S}|\), PU):

1. Fit \(m_{\pi\pi}\) sidebands → subtract under peak → \(N_i^{\mathrm{data}}\), \(N_i^{\mathrm{MC}}\) (MC after all SFs and PU weights, before low-\(\Delta_{2D}\) norm).
2. Define normalization region \(\mathcal{N}\): first 1–2 well-populated bins with manageable background (AN used near-PV bins; re-choose if 2024 PU worsens bin 1). Require \(\sum_{i\in\mathcal{N}} N_i^{\mathrm{data}}\) and MC both statistically healthy.
3. Scale factor for all MC yields: \(k = \sum_{i\in\mathcal{N}} N_i^{\mathrm{data}} / \sum_{i\in\mathcal{N}} N_i^{\mathrm{MC}}\).
4. Calibration:

\[
C_i = \frac{N_i^{\mathrm{data}}}{k\,N_i^{\mathrm{MC}}}.
\]

5. For an LLP analysis: either weight each simulated displaced vertex by \(C(\Delta_{2D},p_T,\ldots)\) or assign a systematic \(\delta = |C_i-1|\) (or envelope over systematic variants of \(C\)).

**Absolute efficiency** (MC-only, for documentation):

\[
\varepsilon_{\mathrm{trk+vtx}}^{\mathrm{MC}}(\Delta_{2D}) = \frac{N_{\mathrm{reco\,matched}}}{N_{\mathrm{gen\,fiducial}}},
\]

then \(\varepsilon^{\mathrm{data}}\approx C\cdot\varepsilon^{\mathrm{MC}}\) under the AN modeling assumption.

### 2.6 Binning (starting proposal)

Re-tune after first look at 2024 stats; start from AN-like granularity with Phase-1 layer edges visible:

| Variable | Suggested bins |
| --- | --- |
| \(\Delta_{2D}\) [cm] | \(0\)–\(1\), \(1\)–\(2\), \(2\)–\(3\), \(3\)–\(5\), \(5\)–\(7\), \(7\)–\(11\) (L1–L2), \(11\)–\(16\) (L2–L3), \(16\)–\(22\) (L3–L4), \(22\)–\(30\), \(30\)–\(40\), \(40\)–\(60\), \(60\)–\(90\), \(>90\) (edges near 2.9 / 6.8 / 10.9 / 16.0 cm) |
| \(p_T^{K_S}\) [GeV] | \(1\)–\(2\), \(2\)–\(3\), \(3\)–\(5\), \(5\)–\(8\), \(>8\) (2D with \(\Delta_{2D}\)) |
| \(\lvert\eta^{K_S}\rvert\) | \(0\)–\(0.9\), \(0.9\)–\(1.5\), \(1.5\)–\(2.4\) (control; barrel vs endcap tracker) |
| Track \(d_0\) or IP sig. (daughters) | Optional diagnostic histograms; primary observable remains **vertex** \(\Delta_{2D}\) |
| PU (\(\mu\) or \(n_{\mathrm{PV}}\)) | Tertiles of 2024 data PU distribution |

### 2.7 Control and closure tests

1. **DY control:** data/MC for muon \(p_T\), \(\eta\), \(m_{\mu\mu}\), \(n_{\mathrm{PV}}\) after selection (AN Fig. 5 analogue).
2. **V0 kinematics:** \(p_T\), \(\eta\), \(m_{\pi\pi}\) of \(K_S^0\) candidates (AN Fig. 8); fitted peak mass vs PDG (AN Fig. 9).
3. **Normalization stability:** vary \(\mathcal{N}\) by ±1 bin; \(C_i\) at large \(\Delta_{2D}\) must be stable within quoted systematics.
4. **Background method:** sideband polynomial degree 0 vs 1; alternate peak windows (\(\pm10\,\mathrm{MeV}\) tight count vs sideband).
5. **Pixel structure:** peaks/steps in \(\mathrm{d}N/\mathrm{d}\Delta_{2D}\) at layer radii (AN Fig. 15); data and MC should show the same Phase-1 pattern.
6. **\(\Lambda^0\) diagnostic:** same pipeline; expect worse S/B at low \(\Delta_{2D}\) (AN §7).
7. **\(Z\to ee\) cross-check:** Electron PD + dielectron triggers; same V0 chain (AN §5).
8. **MC closure:** inject known displaced-track inefficiency in MC, re-extract \(C\), recover injected shape.
9. **PU stress test:** measure \(C(\Delta_{2D})\) in low vs high PU; inflate systematic if they disagree.
10. **Optional Run 3 extension (AN outlook):** non-prompt \(J/\psi\to\mu\mu\) from \(B\) decays as higher-\(p_T\) lepton probe (separate analysis path; not required for the \(K_S^0\) deliverable).

### 2.8 Main systematic uncertainties (2024 list)

Propagate into an envelope on \(C_i\) (AN itself was stats-dominated; Run 3 should quote these explicitly):

1. **Normalization-region choice** (dominant methodological).
2. **Mass sideband / peak definition** (fit range, poly degree, peak window).
3. **V0 selection variation:** track \(p_T>0.8/1.0/1.2\,\mathrm{GeV}\); \(\cos\theta_{\mathrm{pointing}}>0.98/0.99\); DCA \(<0.15/0.20/0.25\,\mathrm{cm}\).
4. **Pileup reweighting** up/down.
5. **Muon ID / trigger SFs** up/down (affects event yield; largely cancels in low-\(\Delta_{2D}\) norm but keep).
6. **\(b\)-tag WP / SF** (event veto efficiency).
7. **Luminosity** (overall; cancels in ratio after norm — quote for absolute yields only).
8. **Tracking / alignment conditions:** split eras across major tracker alignment or reconstruction updates; take difference as systematic.
9. **MC modeling residual:** CP5 vs alternative UE tune or herwig7 shower if available (overall \(K_S^0\) rate cancels; shape vs \(\Delta_{2D}\) might not).
10. **Extrapolation to LLP kinematics:** difference between inclusive \(C(\Delta_{2D})\) and high-\(p_T^{K_S}\) slice; or MC difference hadronic vs leptonic displaced vertices (document as analysis-use caveat per AN §9).

---

## 3. Step-by-step measurement recipe

1. **Resolve samples.** Query DAS for 2024 Muon/DoubleMuon MiniAOD eras and matching `DYJetsToLL_M-50` 13.6 TeV MiniAODSIM; record exact names, GT, and CMSSW release. Fetch golden JSON + PU JSON for Collisions24.

2. **Skim.** Keep events firing the dimuon HLT OR; slim to muons, jets, PVs, `packedPFCandidates`, `lostTracks`. Apply MET/filters recommended for 2024 muon analyses if applicable.

3. **Select DY tags.** Exactly two medium muons, \(p_T>30/25\,\mathrm{GeV}\), \(|m_{\mu\mu}-m_Z|<10\,\mathrm{GeV}\), loose DeepJet \(b\)-veto. Fill DY control histograms (data vs PU-weighted MC).

4. **Build track list.** Charged packed PF + lost tracks; apply AN track preselection (§1.4).

5. **Form OS pairs.** DCA and cylinder cuts; Kalman-fit vertices; apply \(\chi^2\), pointing, and mass-window cuts; classify \(K_S^0\) / \(\Lambda\).

6. **Compute \(\Delta_{2D}\).** Transverse distance of SV from the selected PV; store \(p_T\), \(\eta\), mass, \(\sigma(\Delta_{2D})\), daughter track hits / `d_0`.

7. **Background-subtract.** In each \(\Delta_{2D}\) (and 2D) bin, fit linear sidebands of \(m_{\pi\pi}\); subtract; count peak. Validate with Fig. 9-style mass fits.

8. **Normalize MC** using the low-\(\Delta_{2D}\) region \(\mathcal{N}\); form \(C_i\).

9. **Systematics.** Re-run steps 7–8 under each variation in §2.8; build envelope.

10. **Controls / closure.** Execute §2.7; freeze cuts only after DY and low-\(\Delta_{2D}\) agreement are acceptable.

11. **Export.** Tables/histograms of \(C(\Delta_{2D})\), \(C(\Delta_{2D},p_T)\), per-era and combined 2024; document JSON/correctionlib-friendly SF file for LLP analyses.

12. **Apply.** In the target LLP analysis, multiply simulated displaced-vertex weights by \(C\) and/or assign \(\lvert C-1\rvert\) (plus envelope) as a dedicated displaced-tracking systematic — same use case as AN §§8–9 / DP-2024-010.

**Implementation tips:** Reuse the structure of [K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis); port only conditions, GT, triggers, b-tagger, and PU weights for Run 3. Prefer CMSSW EDAnalyzer or Nano-style flat ntuples **seeded from MiniAOD** so `lostTracks` remain available.

---

## 4. Mapping checklist (AN → 2024)

| AN ingredient | Keep? | 2024 action |
| --- | --- | --- |
| DY \(\mu\mu\) reference | Yes | Update HLT + muon SFs + 13.6 TeV MC |
| \(K_S^0\) probe | Yes | Primary result |
| \(\Lambda^0\) probe | Optional | Diagnostic only unless re-optimized |
| MiniAOD V0 fitter | Yes | Same cuts to start; validate under high PU |
| Sideband + low-\(\Delta_{2D}\) norm | Yes | Re-choose \(\mathcal{N}\) if needed |
| \(C(\Delta_{2D})\) as SF/unc. | Yes | Produce 2024 eras + combined |
| APV/HIP treatment | No | Not applicable |
| DeepCSV \(b\)-veto | Replace | DeepJet loose |
| Run 2 UL \(C\) values | Do not reuse | Re-measure with 2024 reconstruction |
| Phase-1 layer interpretation | Yes | Same radii |
| Non-prompt \(J/\psi\) outlook | Future | Optional high-\(p_T\) lepton follow-up |

---

## 5. References

1. CMS AN-20-111 v4 (this adaptation’s source).
2. CMS Collaboration, *Displaced tracking and vertexing calibration using neutral K mesons*, CERN-CMS-DP-2024-010.
3. Reference code: https://github.com/LukaLambrecht/K0sAnalysis.
4. CMS Muon HLT Run 3 performance (double-muon 17/8 GeV): CMSPublic Run3MuonHLT / DP-2023/017.
5. 2024 golden JSON path pattern: `Cert_Collisions2024_*_Golden.json` under Collisions24 certification.
