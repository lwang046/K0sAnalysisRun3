/*
 AK4 PUPPI + DeepJet score for loose b-veto (Run3 replaces DeepCSV).

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/JetAnalyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations:
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Single jet collection (cfi: slimmedJetsPuppi); DeepFlavour → Jet_btagDeepFlavB
   - Dropped JEC/JER source maps, MET, Puppi duplicate collection, PF-candidate dump
   - Jet ID: 2018-style tight / tightLepVeto as Run3 placeholder (re-validate vs BTV)
   - Loose WP number stays offline: samples/deepjet_wp_2024.md
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
  static const unsigned nJet_max = 50;
  unsigned _nJet{0};
  double _Jet_pt[nJet_max]{};
  double _Jet_eta[nJet_max]{};
  double _Jet_phi[nJet_max]{};
  double _Jet_mass[nJet_max]{};
  double _Jet_btagDeepFlavB[nJet_max]{};
  int _Jet_jetId[nJet_max]{};
  int _Jet_hadronFlavour[nJet_max]{};
  DisplacedV0Ntuple* ntuple_{nullptr};

  // 2018 UL JetID used as Run3 starting point (same family as upstream is2018=true)
  bool jetIsTight(const pat::Jet& jet) const;
  bool jetIsTightLepVeto(const pat::Jet& jet) const;

public:
  JetAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~JetAnalyzer() = default;

  void beginJob(TTree* outputTree);
  void analyze(const edm::Event& iEvent);
};

#endif
