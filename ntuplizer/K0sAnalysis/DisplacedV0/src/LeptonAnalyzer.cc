/*
 Muon helper for DY tag selection.

 Ported (muon-only subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/LeptonAnalyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Upstream muon loop preselection + CutBasedIdMedium retained.
 Rochester / MVA / electron / tau paths omitted for lean DY+V0 package.
 Offline: exactly 2 medium, pT>30/25, |mμμ−mZ|<10 GeV (method §2.4).
 Also fills Dimuon_mass / Dimuon_pt / Dimuon_y for the OS medium pair when
 present (Sol Z-row schema). Muon_mass leaf not stored (PDG const offline).
*/

#include "K0sAnalysis/DisplacedV0/interface/LeptonAnalyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/DisplacedV0Ntuple.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

#include <cmath>
#include <vector>
#include <limits>

LeptonAnalyzer::LeptonAnalyzer(const edm::ParameterSet& /*iConfig*/, DisplacedV0Ntuple* ntuple)
    : ntuple_(ntuple) {}

void LeptonAnalyzer::beginJob(TTree* outputTree) {
  outputTree->Branch("nMuon", &_nMuon, "nMuon/i");
  outputTree->Branch("Muon_pt", &_Muon_pt, "Muon_pt[nMuon]/F");
  outputTree->Branch("Muon_eta", &_Muon_eta, "Muon_eta[nMuon]/F");
  outputTree->Branch("Muon_phi", &_Muon_phi, "Muon_phi[nMuon]/F");
  outputTree->Branch("Muon_charge", &_Muon_charge, "Muon_charge[nMuon]/I");
  outputTree->Branch("Muon_mediumId", &_Muon_mediumId, "Muon_mediumId[nMuon]/O");
  outputTree->Branch("Dimuon_mass", &_Dimuon_mass, "Dimuon_mass/F");
  outputTree->Branch("Dimuon_pt", &_Dimuon_pt, "Dimuon_pt/F");
  outputTree->Branch("Dimuon_y", &_Dimuon_y, "Dimuon_y/F");
}

void LeptonAnalyzer::analyze(const edm::Event& iEvent, const reco::Vertex& /*primaryVertex*/) {
  _nMuon = 0;
  _Dimuon_mass = std::numeric_limits<float>::quiet_NaN();
  _Dimuon_pt = std::numeric_limits<float>::quiet_NaN();
  _Dimuon_y = std::numeric_limits<float>::quiet_NaN();

  edm::Handle<std::vector<pat::Muon>> muons;
  iEvent.getByToken(ntuple_->muonToken, muons);
  if (!muons.isValid()) return;

  std::vector<const pat::Muon*> medium;
  medium.reserve(4);

  // Upstream muon loop (LeptonAnalyzer.cc): tracker/global + PF, pT>5, |η|<2.4
  for (const pat::Muon& mu : *muons) {
    if (_nMuon >= nMuon_max) break;
    if (mu.innerTrack().isNull()) continue;
    if (mu.pt() < 5.) continue;
    if (std::fabs(mu.eta()) > 2.4) continue;
    if (!mu.isPFMuon()) continue;
    if (!(mu.isTrackerMuon() || mu.isGlobalMuon())) continue;

    const unsigned i = _nMuon;
    _Muon_pt[i] = static_cast<float>(mu.pt());
    _Muon_eta[i] = static_cast<float>(mu.eta());
    _Muon_phi[i] = static_cast<float>(mu.phi());
    _Muon_charge[i] = mu.charge();
    _Muon_mediumId[i] = mu.passed(reco::Muon::CutBasedIdMedium);
    if (_Muon_mediumId[i]) {
      medium.push_back(&mu);
    }
    ++_nMuon;
  }

  // Baseline Z→μμ kinematics from exactly two medium OS muons (matches Path filter intent)
  if (medium.size() == 2 && medium[0]->charge() * medium[1]->charge() < 0) {
    const auto p4 = medium[0]->p4() + medium[1]->p4();
    _Dimuon_mass = static_cast<float>(p4.M());
    _Dimuon_pt = static_cast<float>(p4.Pt());
    _Dimuon_y = static_cast<float>(p4.Rapidity());
  }
}
