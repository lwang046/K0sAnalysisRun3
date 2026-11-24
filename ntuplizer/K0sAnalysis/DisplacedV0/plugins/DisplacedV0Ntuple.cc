/*
 EDAnalyzer plugin: event loop + TTree fill for Run3 displaced-V0 ntuples.
 Helpers: V0 / Trigger / Lepton / Jet (ported lean from LukaLambrecht/K0sAnalysis
 @2a132385). MiniAOD-only.

 genWeight / Pileup_nTrue: small hooks from upstream LheAnalyzer path
 (GenEventInfoProduct::weight + PileupSummaryInfo::getTrueNumInteractions).
 Full LHE/PS weight histograms still deferred.
*/
#include "K0sAnalysis/DisplacedV0/plugins/DisplacedV0Ntuple.h"
#include "K0sAnalysis/DisplacedV0/interface/V0Analyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/TriggerAnalyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/LeptonAnalyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/JetAnalyzer.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "FWCore/Framework/interface/MakerMacros.h"

DisplacedV0Ntuple::DisplacedV0Ntuple(const edm::ParameterSet& iConfig)
    : isData_(iConfig.getParameter<bool>("isData")),
      useESMagneticField_(iConfig.getParameter<bool>("useESMagneticField")) {
  usesResource("TFileService");

  muonToken = consumes<std::vector<pat::Muon>>(iConfig.getParameter<edm::InputTag>("muons"));
  jetToken = consumes<std::vector<pat::Jet>>(iConfig.getParameter<edm::InputTag>("jets"));
  packedCandidatesToken =
      consumes<std::vector<pat::PackedCandidate>>(iConfig.getParameter<edm::InputTag>("packedCandidates"));
  lostTracksToken =
      consumes<std::vector<pat::PackedCandidate>>(iConfig.getParameter<edm::InputTag>("lostTracks"));
  pvToken = consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"));
  beamSpotToken = consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("beamSpot"));
  triggerToken = consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerResults"));

  // MC-only weight / PU tokens (same products as upstream LheAnalyzer)
  if (!isData_) {
    genEventInfoToken =
        consumes<GenEventInfoProduct>(iConfig.getParameter<edm::InputTag>("genEventInfo"));
    pileUpToken =
        consumes<std::vector<PileupSummaryInfo>>(iConfig.getParameter<edm::InputTag>("pileupInfo"));
  }

  // Optional ES MagField + TransientTrackBuilder. Requires MagneticField_cff,
  // GeometryRecoDB_cff, and TransientTrackBuilder_cfi in the cfg when enabled.
  // Neon / CMSSW_14_0_X–15_0_X: prefer esConsumes over Run-2 iSetup.get<>.
  if (useESMagneticField_) {
    bFieldToken_ = esConsumes<MagneticField, IdealMagneticFieldRecord>();
    ttBuilderToken_ = esConsumes<TransientTrackBuilder, TransientTrackRecord>(
        edm::ESInputTag("", "TransientTrackBuilder"));
  }

  v0Analyzer_ = std::make_unique<V0Analyzer>(iConfig, this);
  triggerAnalyzer_ = std::make_unique<TriggerAnalyzer>(iConfig, this);
  leptonAnalyzer_ = std::make_unique<LeptonAnalyzer>(iConfig, this);
  jetAnalyzer_ = std::make_unique<JetAnalyzer>(iConfig, this);
}

DisplacedV0Ntuple::~DisplacedV0Ntuple() = default;

void DisplacedV0Ntuple::beginJob() {
  edm::Service<TFileService> fs;
  tree_ = fs->make<TTree>("events", "DisplacedV0 Run3 ntuple");
  tree_->Branch("run", &run_, "run/i");
  tree_->Branch("luminosityBlock", &luminosityBlock_, "luminosityBlock/i");
  tree_->Branch("event", &event_, "event/l");
  tree_->Branch("nPV", &nPV_, "nPV/I");
  tree_->Branch("genWeight", &genWeight_, "genWeight/F");
  tree_->Branch("Pileup_nTrue", &Pileup_nTrue_, "Pileup_nTrue/F");

  v0Analyzer_->beginJob(tree_);
  triggerAnalyzer_->beginJob(tree_);
  leptonAnalyzer_->beginJob(tree_);
  jetAnalyzer_->beginJob(tree_);
}

void DisplacedV0Ntuple::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  run_ = iEvent.id().run();
  luminosityBlock_ = iEvent.luminosityBlock();
  event_ = iEvent.id().event();

  edm::Handle<reco::VertexCollection> vertices;
  iEvent.getByToken(pvToken, vertices);
  nPV_ = vertices.isValid() ? static_cast<int>(vertices->size()) : 0;
  reco::Vertex pv = (vertices.isValid() && !vertices->empty()) ? vertices->front() : reco::Vertex();

  // genWeight / true PU interactions (MC); data keeps defaults
  genWeight_ = 1.f;
  Pileup_nTrue_ = -1.f;
  if (!isData_) {
    edm::Handle<GenEventInfoProduct> genEventInfo;
    iEvent.getByToken(genEventInfoToken, genEventInfo);
    if (genEventInfo.isValid()) {
      genWeight_ = static_cast<float>(genEventInfo->weight());
    }
    edm::Handle<std::vector<PileupSummaryInfo>> pileUpInfo;
    iEvent.getByToken(pileUpToken, pileUpInfo);
    if (pileUpInfo.isValid() && !pileUpInfo->empty()) {
      // getTrueNumInteractions is the same for all bunch crossings (upstream LheAnalyzer)
      Pileup_nTrue_ = pileUpInfo->begin()->getTrueNumInteractions();
    }
  }

  triggerAnalyzer_->analyze(iEvent);
  leptonAnalyzer_->analyze(iEvent, pv);
  jetAnalyzer_->analyze(iEvent);
  if (vertices.isValid() && !vertices->empty()) {
    v0Analyzer_->analyze(iEvent, iSetup, pv);
  } else {
    // Avoid carrying previous-event V0/PV branches into Fill()
    v0Analyzer_->clear();
  }

  tree_->Fill();
}

void DisplacedV0Ntuple::endJob() {}

DEFINE_FWK_MODULE(DisplacedV0Ntuple);
