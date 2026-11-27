#ifndef K0sAnalysis_DisplacedV0_GenWeightCounter_h
#define K0sAnalysis_DisplacedV0_GenWeightCounter_h

/*
 * MC-only: fill TH1 hCounter with signed genWeight *before* DimuonPreFilter.
 * Place first on the Path so rejected events still contribute to Σw.
 * Downstream fill uses f["hCounter"].values()[0] as the MC denominator.
 */

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

#include "TH1D.h"

class GenWeightCounter : public edm::one::EDAnalyzer<edm::one::SharedResources> {
 public:
  explicit GenWeightCounter(const edm::ParameterSet&);
  ~GenWeightCounter() override = default;

  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

 private:
  edm::EDGetTokenT<GenEventInfoProduct> genEventInfoToken_;
  TH1D* hCounter_{nullptr};
};

#endif
