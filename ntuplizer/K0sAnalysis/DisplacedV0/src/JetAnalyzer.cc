/*
 AK4 PUPPI + DeepJet (DeepFlavour) for loose b-veto.

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/JetAnalyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 DeepFlavour discriminator labels match upstream; score = b+bb+lepb.
 Jet ID uses upstream 2018 tight / tightLepVeto as Run3 placeholder.
 CDTE-30: dropped Jet_phi / Jet_mass / Jet_hadronFlavour.
 CDTE-31: drop Jet_* arrays; store passDeepJetLooseVeto + nJetSel only
   (same pT/η/jetId/WP cuts as v0builder --apply-dy-selection).
*/

#include "K0sAnalysis/DisplacedV0/interface/JetAnalyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/DisplacedV0Ntuple.h"

#include <cmath>

JetAnalyzer::JetAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple)
    : deepJetLooseWP_(iConfig.existsAs<double>("deepJetLooseWP")
                          ? static_cast<float>(iConfig.getParameter<double>("deepJetLooseWP"))
                          : 0.0494f),
      ntuple_(ntuple) {}

void JetAnalyzer::beginJob(TTree* outputTree) {
  outputTree->Branch("nJetSel", &_nJetSel, "nJetSel/i");
  outputTree->Branch("passDeepJetLooseVeto", &_passDeepJetLooseVeto, "passDeepJetLooseVeto/O");
}

bool JetAnalyzer::jetIsTight(const pat::Jet& jet) const {
  // Upstream JetAnalyzer::jetIsTight(..., is2018=true)
  if (std::fabs(jet.eta()) <= 2.7) {
    if (jet.neutralHadronEnergyFraction() >= 0.9) return false;
    if (jet.neutralEmEnergyFraction() >= 0.9) return false;
    if (jet.chargedMultiplicity() + jet.neutralMultiplicity() <= 1) return false;
    if (jet.chargedHadronEnergyFraction() <= 0. && std::fabs(jet.eta()) <= 2.6) return false;
    if (jet.chargedMultiplicity() <= 0) return false;
  } else if (std::fabs(jet.eta()) <= 3.0) {
    if (jet.neutralHadronEnergyFraction() >= 0.99) return false;
    if (jet.neutralEmEnergyFraction() <= 0.02) return false;
    if (jet.neutralMultiplicity() <= 2) return false;
  } else {
    if (jet.neutralEmEnergyFraction() >= 0.90) return false;
    if (jet.neutralMultiplicity() <= 10) return false;
    if (jet.neutralHadronEnergyFraction() <= 0.02) return false;
  }
  return true;
}

bool JetAnalyzer::jetIsTightLepVeto(const pat::Jet& jet) const {
  // Upstream JetAnalyzer::jetIsTightLepVeto(..., is2018=true)
  if (!jetIsTight(jet)) return false;
  if (std::fabs(jet.eta()) <= 2.7) {
    if (jet.chargedMuEnergyFraction() >= 0.8) return false;
    if (jet.chargedEmEnergyFraction() >= 0.8) return false;
  }
  return true;
}

int JetAnalyzer::jetIdBits(const pat::Jet& jet) const {
  const bool tight = jetIsTight(jet);
  const bool tightLepVeto = jetIsTightLepVeto(jet);
  return (tight ? 2 : 0) + (tightLepVeto ? 4 : 0);
}

void JetAnalyzer::analyze(const edm::Event& iEvent) {
  _nJetSel = 0;
  _passDeepJetLooseVeto = true;

  edm::Handle<std::vector<pat::Jet>> jets;
  iEvent.getByToken(ntuple_->jetToken, jets);
  if (!jets.isValid()) return;

  bool hasBtag = false;
  for (const pat::Jet& jet : *jets) {
    // Same offline selection as v0builder count_jets / dy b-veto
    if (jet.pt() <= 30.) continue;
    if (std::fabs(jet.eta()) >= 2.5) continue;
    if (jetIdBits(jet) < 2) continue;

    ++_nJetSel;

    const double b = jet.bDiscriminator("pfDeepFlavourJetTags:probb");
    const double bb = jet.bDiscriminator("pfDeepFlavourJetTags:probbb");
    const double lepb = jet.bDiscriminator("pfDeepFlavourJetTags:problepb");
    double deepFlav = b + bb + lepb;
    if (std::isnan(deepFlav)) deepFlav = 0.;
    if (deepFlav > deepJetLooseWP_) {
      hasBtag = true;
    }
  }
  _passDeepJetLooseVeto = !hasBtag;
}
