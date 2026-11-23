# Ntuplizer (Run 3)

Minimal CMSSW package **`DisplacedV0`**: trigger filter + muon/jet/PV + custom
`V0Analyzer` (Kalman V0 from `packedPFCandidates` + `lostTracks`) + weights.

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`ntuplizer/heavyNeutrino/multilep` @ `2a132385`:
- **V0Analyzer** — full Kalman body
- **TriggerAnalyzer** — configurable dimuon HLT OR (`hltPaths`, Mass3p8 baseline)
- **LeptonAnalyzer** — muon-only medium/loose/tight ID + kinematics/IP/iso
- **JetAnalyzer** — AK4 PUPPI + DeepJet (`Jet_btagDeepFlavB`) + jetId placeholder
- **genWeight / Pileup_nTrue** — small hooks from upstream LheAnalyzer path

Full HNL `heavyNeutrino` stack (electrons/taus/Rochester/JEC sources/MET) is
**not** required for the \(C(\Delta_{2D})\) path and was dropped.

Stay on **MiniAOD**. NanoAOD lacks `lostTracks` / track quality used in AN §6.

**Cut split (matches upstream):** CMSSW `V0Analyzer` keeps loose preselection +
Kalman/mass windows; AN-20-111 §6 tight cuts (pT, hits, χ², DCA<0.2, pointing)
are applied offline in `v0building/v0selections.py`.
