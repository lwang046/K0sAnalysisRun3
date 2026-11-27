# Ntuplizer (Run 3)

Minimal CMSSW package **`K0sAnalysis/DisplacedV0`** (scram Subsystem/Package):
trigger filter + AN §5 dimuon pre-filter + muon/jet/PV + custom `V0Analyzer`
(Kalman V0 from `packedPFCandidates` + `lostTracks`) + weights.

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`ntuplizer/heavyNeutrino/multilep` @ `2a132385`:
- **V0Analyzer** — full Kalman body
- **DimuonPreFilter** — lightweight AN §5 DY dimuon EDFilter (Path, ahead of ntuple)
- **GenWeightCounter** — MC-only TH1 `hCounter` = ΣgenWeight **before** the Path filter
  (required for absolute σ×L when `enableDimuonPreFilter=True`)
- **TriggerAnalyzer** — configurable dimuon HLT OR (`hltPaths`, Mass3p8 baseline);
  stores `passDimuonHLT` only (no per-path `HLT_*` leaf)
- **LeptonAnalyzer** — muon kinematics + `Muon_mediumId` + `Dimuon_mass/pt/y`
- **JetAnalyzer** — AK4 PUPPI DeepJet → `nJetSel`, `passDeepJetLooseVeto`,
  `maxDeepJet`, `nJetSelStatus` (no `Jet_*` arrays)
- **genWeight / Pileup_nTrue** — signed weight + in-time (BX=0) true PU

**Sol production schema (after #14/#15):**
- `skipFillIfNoV0=False` — **one row per Path-selected Z→μμ event**, including
  `_nV0s==0` (nimloth DY controls). Set `True` only for size-debug CRAB.
- `storeKsOnly=True` — Ks rows only **after** Λ/Λ̄ classification; float32
- Jets: compact scalars only (no full `Jet_*` arrays)
- Per Ks: mass, pt/η/φ, RPV(+Sig), DCA, vtx χ²/ndf, pointing cosines PV+BS
- Per daughter: pt/η/φ, dxy/dz, hits, track χ²/ndf, packed/lost src+index
- Neighbour charged-ΔR stubs (`_V0NearestChg*`, status=0) until jet association
- Still dropped vs fat: unc/PCA/Iso/daughter-PxPyPz, unused muon leaves,
  `Muon_mass`, per-path HLT, full `Jet_*`

Prefer Path `genWeightCounter + dimuonPreFilter + displacedV0Ntuple` (MC) so
Σw is filled before the filter and the vertex analyzer only runs on baseline Z
events. After merging, **resubmit** CRAB — do **not** delete existing EOS files.
Size estimate: `python3 scripts/estimate_ntuple_slim_factor.py`.

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
