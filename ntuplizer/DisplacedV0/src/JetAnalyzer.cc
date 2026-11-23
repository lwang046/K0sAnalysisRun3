/*
 AK4 PUPPI + DeepJet (DeepFlavour) for loose b-veto.

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/JetAnalyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 DeepFlavour discriminator labels match upstream; Jet_btagDeepFlavB = b+bb+lepb.
 Jet ID uses upstream 2018 tight / tightLepVeto as Run3 placeholder.
 JEC/MET/substructure bulk dropped. Loose WP applied offline (M5).
*/

#include "DisplacedV0/interface/JetAnalyzer.h"
#include "DisplacedV0/plugins/DisplacedV0Ntuple.h"

#include <cmath>

JetAnalyzer::JetAnalyzer(const edm::ParameterSet& /*iConfig*/, DisplacedV0Ntuple* ntuple)
    : ntuple_(ntuple) {}

void JetAnalyzer::beginJob(TTree* outputTree) {
  outputTree->Branch("nJet", &_nJet, "nJet/i");
  outputTree->Branch("Jet_pt", &_Jet_pt, "Jet_pt[nJet]/D");
  outputTree->Branch("Jet_eta", &_Jet_eta, "Jet_eta[nJet]/D");
  outputTree->Branch("Jet_phi", &_Jet_phi, "Jet_phi[nJet]/D");
  outputTree->Branch("Jet_mass", &_Jet_mass, "Jet_mass[nJet]/D");
  outputTree->Branch("Jet_btagDeepFlavB", &_Jet_btagDeepFlavB, "Jet_btagDeepFlavB[nJet]/D");
  outputTree->Branch("Jet_jetId", &_Jet_jetId, "Jet_jetId[nJet]/I");
  outputTree->Branch("Jet_hadronFlavour", &_Jet_hadronFlavour, "Jet_hadronFlavour[nJet]/I");
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

void JetAnalyzer::analyze(const edm::Event& iEvent) {
  _nJet = 0;

  edm::Handle<std::vector<pat::Jet>> jets;
  iEvent.getByToken(ntuple_->jetToken, jets);
  if (!jets.isValid()) return;

  for (const pat::Jet& jet : *jets) {
    if (_nJet >= nJet_max) break;
    // Soft storage cut (offline b-veto uses pT>30, |η|<2.5)
    if (jet.pt() < 15.) continue;
    if (std::fabs(jet.eta()) > 5.) continue;

    const unsigned i = _nJet;
    _Jet_pt[i] = jet.pt();
    _Jet_eta[i] = jet.eta();
    _Jet_phi[i] = jet.phi();
    _Jet_mass[i] = jet.mass();

    // DeepFlavour (DeepJet) — same discriminator labels as upstream
    const double b = jet.bDiscriminator("pfDeepFlavourJetTags:probb");
    const double bb = jet.bDiscriminator("pfDeepFlavourJetTags:probbb");
    const double lepb = jet.bDiscriminator("pfDeepFlavourJetTags:problepb");
    double deepFlav = b + bb + lepb;
    if (std::isnan(deepFlav)) deepFlav = 0.;
    _Jet_btagDeepFlavB[i] = deepFlav;

    // NanoAOD-style jetId: bit1=tight (2), bit2=tightLepVeto (4)
    const bool tight = jetIsTight(jet);
    const bool tightLepVeto = jetIsTightLepVeto(jet);
    _Jet_jetId[i] = (tight ? 2 : 0) + (tightLepVeto ? 4 : 0);

    _Jet_hadronFlavour[i] = ntuple_->isData_ ? -1 : static_cast<int>(jet.hadronFlavour());

    ++_nJet;
  }
}
