/*
 Muon helper for DY tag selection.

 Ported (muon-only subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/LeptonAnalyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Upstream muon loop preselection + CutBasedIdMedium/Loose/Tight retained.
 Rochester / MVA / electron / tau paths omitted for lean DY+V0 package.
 Offline: exactly 2 medium, pT>30/25, |mμμ−mZ|<10 GeV (method §2.4).
*/

#include "DisplacedV0/interface/LeptonAnalyzer.h"
#include "DisplacedV0/plugins/DisplacedV0Ntuple.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

#include <cmath>

namespace {
constexpr double kMuonMass = 0.1056583745;
}

LeptonAnalyzer::LeptonAnalyzer(const edm::ParameterSet& /*iConfig*/, DisplacedV0Ntuple* ntuple)
    : ntuple_(ntuple) {}

void LeptonAnalyzer::beginJob(TTree* outputTree) {
  outputTree->Branch("nMuon", &_nMuon, "nMuon/i");
  outputTree->Branch("Muon_pt", &_Muon_pt, "Muon_pt[nMuon]/D");
  outputTree->Branch("Muon_eta", &_Muon_eta, "Muon_eta[nMuon]/D");
  outputTree->Branch("Muon_phi", &_Muon_phi, "Muon_phi[nMuon]/D");
  outputTree->Branch("Muon_mass", &_Muon_mass, "Muon_mass[nMuon]/D");
  outputTree->Branch("Muon_charge", &_Muon_charge, "Muon_charge[nMuon]/I");
  outputTree->Branch("Muon_looseId", &_Muon_looseId, "Muon_looseId[nMuon]/O");
  outputTree->Branch("Muon_mediumId", &_Muon_mediumId, "Muon_mediumId[nMuon]/O");
  outputTree->Branch("Muon_tightId", &_Muon_tightId, "Muon_tightId[nMuon]/O");
  outputTree->Branch("Muon_isPF", &_Muon_isPF, "Muon_isPF[nMuon]/O");
  outputTree->Branch("Muon_isGlobal", &_Muon_isGlobal, "Muon_isGlobal[nMuon]/O");
  outputTree->Branch("Muon_isTracker", &_Muon_isTracker, "Muon_isTracker[nMuon]/O");
  outputTree->Branch("Muon_dxy", &_Muon_dxy, "Muon_dxy[nMuon]/D");
  outputTree->Branch("Muon_dz", &_Muon_dz, "Muon_dz[nMuon]/D");
  outputTree->Branch("Muon_sip3d", &_Muon_sip3d, "Muon_sip3d[nMuon]/D");
  outputTree->Branch("Muon_pfRelIso04_all", &_Muon_pfRelIso04_all, "Muon_pfRelIso04_all[nMuon]/D");
}

void LeptonAnalyzer::analyze(const edm::Event& iEvent, const reco::Vertex& /*primaryVertex*/) {
  _nMuon = 0;

  edm::Handle<std::vector<pat::Muon>> muons;
  iEvent.getByToken(ntuple_->muonToken, muons);
  if (!muons.isValid()) return;

  // Upstream muon loop (LeptonAnalyzer.cc): tracker/global + PF, pT>5, |η|<2.4
  for (const pat::Muon& mu : *muons) {
    if (_nMuon >= nMuon_max) break;
    if (mu.innerTrack().isNull()) continue;
    if (mu.pt() < 5.) continue;
    if (std::fabs(mu.eta()) > 2.4) continue;
    if (!mu.isPFMuon()) continue;
    if (!(mu.isTrackerMuon() || mu.isGlobalMuon())) continue;

    const unsigned i = _nMuon;
    _Muon_pt[i] = mu.pt();
    _Muon_eta[i] = mu.eta();
    _Muon_phi[i] = mu.phi();
    _Muon_mass[i] = kMuonMass;
    _Muon_charge[i] = mu.charge();
    _Muon_isPF[i] = mu.isPFMuon();
    _Muon_isGlobal[i] = mu.isGlobalMuon();
    _Muon_isTracker[i] = mu.isTrackerMuon();

    // POG cut-based IDs (same selectors as upstream _lPOG*)
    _Muon_looseId[i] = mu.passed(reco::Muon::CutBasedIdLoose);
    _Muon_mediumId[i] = mu.passed(reco::Muon::CutBasedIdMedium);
    _Muon_tightId[i] = mu.passed(reco::Muon::CutBasedIdTight);

    // Impact parameters (upstream fillLeptonImpactParameters for muons)
    _Muon_dxy[i] = mu.dB(pat::Muon::PV2D);
    _Muon_dz[i] = mu.dB(pat::Muon::PVDZ);
    const double ip3d = mu.dB(pat::Muon::PV3D);
    const double eip3d = mu.edB(pat::Muon::PV3D);
    _Muon_sip3d[i] = (eip3d > 0.) ? std::fabs(ip3d / eip3d) : -1.;

    // PF relative isolation R=0.4 (Δβ-corrected), NanoAOD-style name
    const auto& iso04 = mu.pfIsolationR04();
    const double absIso =
        iso04.sumChargedHadronPt +
        std::max(0., iso04.sumNeutralHadronEt + iso04.sumPhotonEt - 0.5 * iso04.sumPUPt);
    _Muon_pfRelIso04_all[i] = (mu.pt() > 0.) ? absIso / mu.pt() : 999.;

    ++_nMuon;
  }
}
