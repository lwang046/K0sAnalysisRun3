/*
 AK4 PUPPI + DeepJet for loose b-veto (Run3 replaces DeepCSV).

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/JetAnalyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations:
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Single jet collection (cfi: slimmedJetsPuppi); DeepFlavour sum in-memory
   - CDTE-31: store only event scalars passDeepJetLooseVeto + nJetSel
     (drop Jet_* / nJet arrays — heavy vs first-C need)
*/
#ifndef DisplacedV0_JetAnalyzer_h
#define DisplacedV0_JetAnalyzer_h

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "TTree.h"

class DisplacedV0Ntuple;

class JetAnalyzer {
private:
  // Selection matching v0builder dy_event_mask / count_jets (pT>30, |η|<2.5, jetId≥2)
  float deepJetLooseWP_{0.0494f};
  unsigned _nJetSel{0};
  bool _passDeepJetLooseVeto{true};
  DisplacedV0Ntuple* ntuple_{nullptr};

  // 2018 UL JetID used as Run3 starting point (same family as upstream is2018=true)
  bool jetIsTight(const pat::Jet& jet) const;
  bool jetIsTightLepVeto(const pat::Jet& jet) const;
  int jetIdBits(const pat::Jet& jet) const;

public:
  JetAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~JetAnalyzer() = default;

  void beginJob(TTree* outputTree);
  void analyze(const edm::Event& iEvent);
};

#endif
