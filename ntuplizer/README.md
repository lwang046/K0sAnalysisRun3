# Ntuplizer (Run 3)

Minimal CMSSW package **`K0sAnalysis/DisplacedV0`** (scram Subsystem/Package):
trigger filter + AN §5 dimuon pre-filter + muon/jet/PV + custom `V0Analyzer`
(Kalman V0 from `packedPFCandidates` + `lostTracks`) + weights.

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`ntuplizer/heavyNeutrino/multilep` @ `2a132385`:
- **V0Analyzer** — full Kalman body
- **DimuonPreFilter** — lightweight AN §5 DY dimuon EDFilter (Path, ahead of ntuple)
- **TriggerAnalyzer** — configurable dimuon HLT OR (`hltPaths`, Mass3p8 baseline)
- **LeptonAnalyzer** — muon-only medium/loose/tight ID + kinematics/IP/iso
- **JetAnalyzer** — AK4 PUPPI + DeepJet (`Jet_btagDeepFlavB`) + jetId placeholder
- **genWeight / Pileup_nTrue** — small hooks from upstream LheAnalyzer path

Full HNL `heavyNeutrino` stack (electrons/taus/Rochester/JEC sources/MET) is
**not** required for the \(C(\Delta_{2D})\) path and was dropped.

Stay on **MiniAOD**. NanoAOD lacks `lostTracks` / track quality used in AN §6.

**Cut split (matches upstream):** CMSSW `V0Analyzer` keeps loose preselection +
Kalman/mass windows; AN-20-111 §6 tight cuts (pT, hits, χ², DCA<0.2, pointing)
are applied offline in `v0building/v0selections.py`. The Path dimuon filter
mirrors the offline DY muon+mass cuts for early rate reduction; HLT OR and
DeepJet b-veto remain in TriggerAnalyzer / offline v0building.

**Install into a release:**

```bash
cd $CMSSW_BASE/src
ln -s /path/to/K0sAnalysisRun3/ntuplizer/K0sAnalysis K0sAnalysis
scram b -j8
```

Python import: `from K0sAnalysis.DisplacedV0.displacedV0_cfi import ...`
