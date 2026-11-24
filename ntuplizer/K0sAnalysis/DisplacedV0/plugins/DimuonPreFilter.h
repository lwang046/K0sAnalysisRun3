/*
 Lightweight AN §5-style DY dimuon pre-filter (Neon / CDTE-20).

 Keep events with exactly two medium-ID muons (from the slimmedMuons
 collection after a loose tracker/global+PF preselection matching
 LeptonAnalyzer), leading/trailing pT > 30/25 GeV, |η|<2.4, opposite
 charge, and |mμμ − mZ| < 10 GeV.

 Place ahead of DisplacedV0Ntuple in cms.Path. Cfg switch
 enableDimuonPreFilter=False disables for debugging.
*/
#ifndef K0sAnalysis_DisplacedV0_DimuonPreFilter_h
#define K0sAnalysis_DisplacedV0_DimuonPreFilter_h

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

class DimuonPreFilter : public edm::stream::EDFilter<> {
public:
  explicit DimuonPreFilter(const edm::ParameterSet&);
  ~DimuonPreFilter() override = default;

  bool filter(edm::Event&, const edm::EventSetup&) override;

private:
  edm::EDGetTokenT<std::vector<pat::Muon>> muonToken_;
  double minLeadingPt_;
  double minTrailingPt_;
  double maxAbsEta_;
  double zMassWindow_;
  double zMass_;
};

#endif
