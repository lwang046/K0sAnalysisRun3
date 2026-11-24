/*
 Lightweight AN §5-style DY dimuon pre-filter.

 Defaults match v0building/v0builder.py dy_event_mask (without HLT / b-veto,
 which remain offline or in TriggerAnalyzer bits): 2 medium muons, pT>30/25,
 |η|<2.4, OS, |mμμ−mZ|<10 GeV.
*/
#include "K0sAnalysis/DisplacedV0/plugins/DimuonPreFilter.h"

#include "DataFormats/MuonReco/interface/Muon.h"

#include <cmath>
#include <vector>
#include <algorithm>

DimuonPreFilter::DimuonPreFilter(const edm::ParameterSet& iConfig)
    : muonToken_(consumes<std::vector<pat::Muon>>(iConfig.getParameter<edm::InputTag>("muons"))),
      minLeadingPt_(iConfig.getParameter<double>("minLeadingPt")),
      minTrailingPt_(iConfig.getParameter<double>("minTrailingPt")),
      maxAbsEta_(iConfig.getParameter<double>("maxAbsEta")),
      zMassWindow_(iConfig.getParameter<double>("zMassWindow")),
      zMass_(iConfig.getParameter<double>("zMass")) {}

bool DimuonPreFilter::filter(edm::Event& iEvent, const edm::EventSetup& /*iSetup*/) {
  edm::Handle<std::vector<pat::Muon>> muons;
  iEvent.getByToken(muonToken_, muons);
  if (!muons.isValid()) return false;

  // Same loose preselection as LeptonAnalyzer, then require medium ID.
  std::vector<const pat::Muon*> medium;
  medium.reserve(4);
  for (const pat::Muon& mu : *muons) {
    if (mu.innerTrack().isNull()) continue;
    if (mu.pt() < 5.) continue;
    if (std::fabs(mu.eta()) > maxAbsEta_) continue;
    if (!mu.isPFMuon()) continue;
    if (!(mu.isTrackerMuon() || mu.isGlobalMuon())) continue;
    if (!mu.passed(reco::Muon::CutBasedIdMedium)) continue;
    medium.push_back(&mu);
  }

  if (medium.size() != 2) return false;

  // Leading / trailing pT (sorted descending), both |η|<maxAbsEta already.
  std::sort(medium.begin(), medium.end(),
            [](const pat::Muon* a, const pat::Muon* b) { return a->pt() > b->pt(); });
  if (medium[0]->pt() <= minLeadingPt_) return false;
  if (medium[1]->pt() <= minTrailingPt_) return false;

  if (medium[0]->charge() * medium[1]->charge() >= 0) return false;

  const double mll = (medium[0]->p4() + medium[1]->p4()).M();
  if (std::fabs(mll - zMass_) >= zMassWindow_) return false;

  return true;
}

DEFINE_FWK_MODULE(DimuonPreFilter);
