/*
 Muon helper for DY tag selection (AN §5 / method §2.4).

 Ported (muon-only subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/LeptonAnalyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations:
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Muons only: medium/loose/tight POG ID, kinematics, IP, PF iso04
   - Dropped electrons, taus, Rochester, lepton MVAs, EffectiveAreas helpers
   - Offline applies exactly-2 medium, pT>30/25, |mμμ−mZ|<10 GeV (store branches)
*/
#ifndef DisplacedV0_LeptonAnalyzer_h
#define DisplacedV0_LeptonAnalyzer_h

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "TTree.h"

class DisplacedV0Ntuple;

class LeptonAnalyzer {
private:
  static const unsigned nMuon_max = 20;
  unsigned _nMuon{0};
  double _Muon_pt[nMuon_max]{};
  double _Muon_eta[nMuon_max]{};
  double _Muon_phi[nMuon_max]{};
  double _Muon_mass[nMuon_max]{};
  int _Muon_charge[nMuon_max]{};
  bool _Muon_looseId[nMuon_max]{};
  bool _Muon_mediumId[nMuon_max]{};
  bool _Muon_tightId[nMuon_max]{};
  bool _Muon_isPF[nMuon_max]{};
  bool _Muon_isGlobal[nMuon_max]{};
  bool _Muon_isTracker[nMuon_max]{};
  double _Muon_dxy[nMuon_max]{};
  double _Muon_dz[nMuon_max]{};
  double _Muon_sip3d[nMuon_max]{};
  double _Muon_pfRelIso04_all[nMuon_max]{};
  DisplacedV0Ntuple* ntuple_{nullptr};

public:
  LeptonAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~LeptonAnalyzer() = default;

  void beginJob(TTree* outputTree);
  void analyze(const edm::Event& iEvent, const reco::Vertex& primaryVertex);
};

#endif
