/*
 EDAnalyzer: event loop + TTree fill for Run3 displaced-V0 ntuples.
 Owns helper analyzers (V0 / Trigger / Lepton / Jet). Tokens for MiniAOD
 collections listed in implementation plan §4.1.
 V0Analyzer (friend) reads packedCandidatesToken, lostTracksToken, beamSpotToken.
 Trigger/Lepton/Jet use triggerToken / muonToken / jetToken.
 genWeight / Pileup_nTrue filled here from generator + pileupSummary (MC).
*/
#ifndef DisplacedV0_DisplacedV0Ntuple_h
#define DisplacedV0_DisplacedV0Ntuple_h

#include <memory>

#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "TTree.h"

class V0Analyzer;
class TriggerAnalyzer;
class LeptonAnalyzer;
class JetAnalyzer;

class DisplacedV0Ntuple : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit DisplacedV0Ntuple(const edm::ParameterSet&);
  ~DisplacedV0Ntuple() override;

  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // Tokens shared with helper classes (friend access)
  edm::EDGetTokenT<std::vector<pat::Muon>> muonToken;
  edm::EDGetTokenT<std::vector<pat::Jet>> jetToken;
  edm::EDGetTokenT<std::vector<pat::PackedCandidate>> packedCandidatesToken;
  edm::EDGetTokenT<std::vector<pat::PackedCandidate>> lostTracksToken;
  edm::EDGetTokenT<reco::VertexCollection> pvToken;
  edm::EDGetTokenT<reco::BeamSpot> beamSpotToken;
  edm::EDGetTokenT<edm::TriggerResults> triggerToken;
  edm::EDGetTokenT<GenEventInfoProduct> genEventInfoToken;
  edm::EDGetTokenT<std::vector<PileupSummaryInfo>> pileUpToken;

  friend class V0Analyzer;
  friend class TriggerAnalyzer;
  friend class LeptonAnalyzer;
  friend class JetAnalyzer;

private:
  TTree* tree_{nullptr};
  bool isData_{true};

  unsigned long long event_{0};
  unsigned int run_{0}, luminosityBlock_{0};
  int nPV_{0};
  float genWeight_{1.f}, Pileup_nTrue_{-1.f};

  std::unique_ptr<V0Analyzer> v0Analyzer_;
  std::unique_ptr<TriggerAnalyzer> triggerAnalyzer_;
  std::unique_ptr<LeptonAnalyzer> leptonAnalyzer_;
  std::unique_ptr<JetAnalyzer> jetAnalyzer_;
};

#endif
