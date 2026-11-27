#include "K0sAnalysis/DisplacedV0/plugins/GenWeightCounter.h"

#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

GenWeightCounter::GenWeightCounter(const edm::ParameterSet& iConfig) {
  usesResource("TFileService");
  genEventInfoToken_ = consumes<GenEventInfoProduct>(
      iConfig.getParameter<edm::InputTag>("genEventInfo"));
}

void GenWeightCounter::beginJob() {
  edm::Service<TFileService> fs;
  // 1-bin hist: values()[0] == Σ genWeight (matches upstream / mcvsdata_fill).
  hCounter_ = fs->make<TH1D>("hCounter", "sum of genWeights;bin;sumw", 1, 0., 1.);
  hCounter_->Sumw2();
}

void GenWeightCounter::analyze(const edm::Event& iEvent, const edm::EventSetup&) {
  if (iEvent.isRealData()) {
    return;
  }
  edm::Handle<GenEventInfoProduct> genEventInfo;
  iEvent.getByToken(genEventInfoToken_, genEventInfo);
  const double w = (genEventInfo.isValid()) ? genEventInfo->weight() : 1.0;
  hCounter_->Fill(0.5, w);
}

DEFINE_FWK_MODULE(GenWeightCounter);
