# Ntuplizer (Run 3)

Minimal CMSSW package **`K0sAnalysis/DisplacedV0`** (scram Subsystem/Package):
trigger filter + AN §5 dimuon pre-filter + muon/jet/PV + custom `V0Analyzer`
(Kalman V0 from `packedPFCandidates` + `lostTracks`) + weights.

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`ntuplizer/heavyNeutrino/multilep` @ `2a132385`:
- **V0Analyzer** — full Kalman body
- **DimuonPreFilter** — lightweight AN §5 DY dimuon EDFilter (Path, ahead of ntuple)
- **TriggerAnalyzer** — configurable dimuon HLT OR (`hltPaths`, Mass3p8 baseline);
  stores `passDimuonHLT` only (no per-path `HLT_*` leaf)
- **LeptonAnalyzer** — muon kinematics + `Muon_mediumId` (first-C DY tag)
- **JetAnalyzer** — AK4 PUPPI DeepJet → `passDeepJetLooseVeto` + `nJetSel`
- **genWeight / Pileup_nTrue** — small hooks from upstream LheAnalyzer path

**Ntuple slim (CDTE-30 / CDTE-31 / first-C):**
- `storeKsOnly=True` (no Λ/Λ̄ rows); kinematics as `float`
- `skipFillIfNoV0=True` — do not `Fill` when `_nV0s==0` (trade-off: nimloth
  loses zero-Ks DY control events; Path dimuon filter unchanged)
- Jets: scalars only (`passDeepJetLooseVeto`, `nJetSel`); no `Jet_*` arrays
- Deferred V0 leaves: `_V0RBS*`, mother `_V0Eta/_V0Phi`, daughter η/φ, `_V0D0*/_V0Dz*`
- Dropped: unc/PCA/Iso/daughter-PxPyPz, unused muon leaves, `Muon_mass`, per-path HLT

After merging, **resubmit** CRAB for new output — do **not** delete existing EOS
files. Size estimate: `python3 scripts/estimate_ntuple_slim_factor.py`.

Full HNL `heavyNeutrino` stack (electrons/taus/Rochester/JEC sources/MET) is
**not** required for the \(C(\Delta_{2D})\) path and was dropped.

Stay on **MiniAOD**. NanoAOD lacks `lostTracks` / track quality used in AN §6.

**Cut split (matches upstream):** CMSSW `V0Analyzer` keeps loose preselection +
Kalman/mass windows; AN-20-111 §6 tight cuts (pT, hits, χ², DCA<0.2, pointing)
are applied offline in `v0building/v0selections.py`. The Path dimuon filter
mirrors the offline DY muon+mass cuts for early rate reduction; HLT OR and
DeepJet b-veto: TriggerAnalyzer / JetAnalyzer scalars (also readable offline).

**Install into a release:**

```bash
cd $CMSSW_BASE/src
ln -s /path/to/K0sAnalysisRun3/ntuplizer/K0sAnalysis K0sAnalysis
scram b -j8
```

Python import: `from K0sAnalysis.DisplacedV0.displacedV0_cfi import ...`
