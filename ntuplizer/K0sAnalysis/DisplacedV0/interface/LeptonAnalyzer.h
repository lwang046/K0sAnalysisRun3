/*
 Muon helper for DY tag selection (AN §5 / method §2.4).

 Ported (muon-only subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/LeptonAnalyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations:
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Muon_* arrays for offline DY; plus Dimuon_mass/pt/y for the baseline
     OS medium pair when present (Sol Z-row schema)
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
  float _Muon_pt[nMuon_max]{};
  float _Muon_eta[nMuon_max]{};
  float _Muon_phi[nMuon_max]{};
  int _Muon_charge[nMuon_max]{};
  bool _Muon_mediumId[nMuon_max]{};
  // Baseline Z→μμ scalars (NaN when no valid OS medium pair)
  float _Dimuon_mass{-1.f};
  float _Dimuon_pt{-1.f};
  float _Dimuon_y{-1.f};
  DisplacedV0Ntuple* ntuple_{nullptr};

public:
  LeptonAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~LeptonAnalyzer() = default;

  void beginJob(TTree* outputTree);
  void analyze(const edm::Event& iEvent, const reco::Vertex& primaryVertex);
};

#endif
