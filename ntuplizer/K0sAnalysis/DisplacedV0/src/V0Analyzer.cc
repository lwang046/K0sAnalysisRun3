/*
 Custom analyzer for secondary vertices from Light Neutral Hadron (V0) decays.

 Ported from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/V0Analyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations (minimal):
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Tokens: ntuple_->packedCandidatesToken / lostTracksToken / beamSpotToken
   - Unused ele/muon getByToken calls from upstream analyze() dropped
   - MagField: UniformMagneticField(3.8 T) by default; optional ES IdealMagneticFieldRecord
     + TransientTrackBuilder (TransientTrackRecord) when useESMagneticField_
   - Tracks: hasTrackDetails() + pseudoTrack() (was bestTrack()); see TODO-VERIFY
   - CMSSW preselection unchanged (loose quality + IP sig>2; DCA/cylinder/
     Kalman χ²/mass windows as upstream). AN-20-111 §6 tight cuts stay offline
     in v0building/v0selections.py (same as K0sAnalysis).
   - Do not apply Δ2D/σ cut (matches AN §6 / upstream).
   - CDTE-30 slim: storeKsOnly (default), float leaves, drop unc/PCA/Iso/PxPyPz
     daughter Cartesian / PV-unc; skip getTrackRelIso (unused by first-C).
*/

#include "K0sAnalysis/DisplacedV0/interface/V0Analyzer.h"
#include "K0sAnalysis/DisplacedV0/interface/DisplacedV0Ntuple.h"

#include "MagneticField/UniformEngine/interface/UniformMagneticField.h"

#include <cmath>

// constructor //
V0Analyzer::V0Analyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple)
    : storeKsOnly_(iConfig.existsAs<bool>("storeKsOnly")
                       ? iConfig.getParameter<bool>("storeKsOnly")
                       : true),
      ntuple_(ntuple) {}

// destructor //
V0Analyzer::~V0Analyzer() {}

// beginJob //
void V0Analyzer::beginJob(TTree* outputTree) {
  // First-C slim schema: only branches read by v0builder / v0selections /
  // --apply-dy-selection / mcvsdata_fill (via laurelin). Dropped (unused):
  //   _V0{X,Y,Z}Unc, _V0R{PV,BS}Unc, _V0PCA{X,Y,Z}, _V0Pz,
  //   _V0P{x,y,z}{Pos,Neg}, _V0Iso{Pos,Neg}, _primaryVertex{X,Y,Z}Unc
  // Float (/F) is enough for GeV / cm kinematics at analysis precision.

  outputTree->Branch("_beamSpotX", &_beamSpotX, "_beamSpotX/F");
  outputTree->Branch("_beamSpotY", &_beamSpotY, "_beamSpotY/F");
  outputTree->Branch("_beamSpotZ", &_beamSpotZ, "_beamSpotZ/F");
  outputTree->Branch("_primaryVertexX", &_primaryVertexX, "_primaryVertexX/F");
  outputTree->Branch("_primaryVertexY", &_primaryVertexY, "_primaryVertexY/F");
  outputTree->Branch("_primaryVertexZ", &_primaryVertexZ, "_primaryVertexZ/F");

  outputTree->Branch("_nV0s", &_nV0s, "_nV0s/i");
  outputTree->Branch("_V0InvMass", &_V0InvMass, "_V0InvMass[_nV0s]/F");
  outputTree->Branch("_V0Type", &_V0Type, "_V0Type[_nV0s]/i");
  outputTree->Branch("_V0X", &_V0X, "_V0X[_nV0s]/F");
  outputTree->Branch("_V0Y", &_V0Y, "_V0Y[_nV0s]/F");
  outputTree->Branch("_V0Z", &_V0Z, "_V0Z[_nV0s]/F");
  outputTree->Branch("_V0RPV", &_V0RPV, "_V0RPV[_nV0s]/F");
  outputTree->Branch("_V0RBS", &_V0RBS, "_V0RBS[_nV0s]/F");
  outputTree->Branch("_V0RPVSig", &_V0RPVSig, "_V0RPVSig[_nV0s]/F");
  outputTree->Branch("_V0RBSSig", &_V0RBSSig, "_V0RBSSig[_nV0s]/F");
  outputTree->Branch("_V0Px", &_V0Px, "_V0Px[_nV0s]/F");
  outputTree->Branch("_V0Py", &_V0Py, "_V0Py[_nV0s]/F");
  outputTree->Branch("_V0Pt", &_V0Pt, "_V0Pt[_nV0s]/F");
  outputTree->Branch("_V0Eta", &_V0Eta, "_V0Eta[_nV0s]/F");
  outputTree->Branch("_V0Phi", &_V0Phi, "_V0Phi[_nV0s]/F");
  outputTree->Branch("_V0DCA", &_V0DCA, "_V0DCA[_nV0s]/F");
  outputTree->Branch("_V0VtxNormChi2", &_V0VtxNormChi2, "_V0VtxNormChi2[_nV0s]/F");
  outputTree->Branch("_V0PtPos", &_V0PtPos, "_V0PtPos[_nV0s]/F");
  outputTree->Branch("_V0PtNeg", &_V0PtNeg, "_V0PtNeg[_nV0s]/F");
  outputTree->Branch("_V0EtaPos", &_V0EtaPos, "_V0EtaPos[_nV0s]/F");
  outputTree->Branch("_V0EtaNeg", &_V0EtaNeg, "_V0EtaNeg[_nV0s]/F");
  outputTree->Branch("_V0PhiPos", &_V0PhiPos, "_V0PhiPos[_nV0s]/F");
  outputTree->Branch("_V0PhiNeg", &_V0PhiNeg, "_V0PhiNeg[_nV0s]/F");
  outputTree->Branch("_V0NHitsPos", &_V0NHitsPos, "_V0NHitsPos[_nV0s]/F");
  outputTree->Branch("_V0NHitsNeg", &_V0NHitsNeg, "_V0NHitsNeg[_nV0s]/F");
  outputTree->Branch("_V0NormChi2Pos", &_V0NormChi2Pos, "_V0NormChi2Pos[_nV0s]/F");
  outputTree->Branch("_V0NormChi2Neg", &_V0NormChi2Neg, "_V0NormChi2Neg[_nV0s]/F");
  // Daughter IPs (dxy/dz w.r.t. PV) — keep for trackingEff nuisances (CDTE-26).
  outputTree->Branch("_V0D0Pos", &_V0D0Pos, "_V0D0Pos[_nV0s]/F");
  outputTree->Branch("_V0DzPos", &_V0DzPos, "_V0DzPos[_nV0s]/F");
  outputTree->Branch("_V0D0Neg", &_V0D0Neg, "_V0D0Neg[_nV0s]/F");
  outputTree->Branch("_V0DzNeg", &_V0DzNeg, "_V0DzNeg[_nV0s]/F");
}

void V0Analyzer::clear() {
  _nV0s = 0;
  _primaryVertexX = 0.f;
  _primaryVertexY = 0.f;
  _primaryVertexZ = 0.f;
  _beamSpotX = 0.f;
  _beamSpotY = 0.f;
  _beamSpotZ = 0.f;
}

// analyze (main method) //
void V0Analyzer::analyze(const edm::Event& iEvent,
                         const edm::EventSetup& iSetup,
                         const reco::Vertex& primaryVertex) {
  edm::Handle<std::vector<pat::PackedCandidate>> packedCandidates;
  iEvent.getByToken(ntuple_->packedCandidatesToken, packedCandidates);
  edm::Handle<std::vector<pat::PackedCandidate>> lostTracks;
  iEvent.getByToken(ntuple_->lostTracksToken, lostTracks);
  edm::Handle<reco::BeamSpot> beamSpotHandle;
  iEvent.getByToken(ntuple_->beamSpotToken, beamSpotHandle);

  // MagField / TransientTrackBuilder resolution (Run3 / Neon hardening):
  //   useESMagneticField=True  → IdealMagneticFieldRecord + TransientTrackBuilder
  //                              via esConsumes (load MagneticField_cff + Geometry
  //                              + TransientTrackBuilder_cfi in the cfg).
  //   useESMagneticField=False → UniformMagneticField(3.8 T) smoke fallback.
  //                              (OAEParametrizedMagneticField lives under
  //                              ParametrizedEngine/src/ and is a scram private
  //                              header on CMSSW_15_0_X — do not include it.)
  // TODO-VERIFY on lxplus: both modes compile/link on CMSSW_14_0_X / 15_0_X;
  //   TransientTrackBuilder label "TransientTrackBuilder" still valid.
  std::unique_ptr<MagneticField> ownedBField;
  const MagneticField* bfield = nullptr;
  const TransientTrackBuilder* ttBuilder = nullptr;
  if (ntuple_->useESMagneticField_) {
    bfield = &iSetup.getData(ntuple_->bFieldToken_);
    ttBuilder = &iSetup.getData(ntuple_->ttBuilderToken_);
  } else {
    ownedBField = std::make_unique<UniformMagneticField>(3.8f);
    bfield = ownedBField.get();
  }

  _primaryVertexX = primaryVertex.position().x();
  _primaryVertexY = primaryVertex.position().y();
  _primaryVertexZ = primaryVertex.position().z();

  _beamSpotX = beamSpotHandle->position().x();
  _beamSpotY = beamSpotHandle->position().y();
  _beamSpotZ = beamSpotHandle->position().z();

  // preselect PackedCandidates and lost tracks (see help function below).
  // TODO-VERIFY (docs-level certainty without scram): for 2024 MiniAODv4/v6,
  //   pat::PackedCandidate::hasTrackDetails() + pseudoTrack() remain the MiniAOD
  //   track API; lostTracks InputTag remains "lostTracks" (cfi default).
  //   Confirm on lxplus smoke that packedPFCandidates + lostTracks both yield tracks.
  std::vector<reco::Track> seltracks;
  for (const pat::PackedCandidate& pc : *packedCandidates) {
    if (pc.hasTrackDetails()) {
      reco::Track tr = pc.pseudoTrack();
      std::unordered_map<std::string, double> temp = getTrackVariables(tr, beamSpotHandle, bfield);
      if (temp["pass"] > 0.5) seltracks.push_back(tr);
    }
  }
  for (const pat::PackedCandidate& pc : *lostTracks) {
    if (pc.hasTrackDetails()) {
      reco::Track tr = pc.pseudoTrack();
      std::unordered_map<std::string, double> temp = getTrackVariables(tr, beamSpotHandle, bfield);
      if (temp["pass"] > 0.5) seltracks.push_back(tr);
    }
  }

  _nV0s = 0;

  for (unsigned i = 0; i < seltracks.size(); i++) {
    for (unsigned j = i + 1; j < seltracks.size(); j++) {
      const reco::Track tr1 = seltracks.at(i);
      const reco::Track tr2 = seltracks.at(j);
      // temporary try catch for 2018D files giving a strange
      // "BasicSingleVertexState::could not invert weight matrix" error
      // that presumably has something to do with the kalman fitter
      std::unordered_map<std::string, double> temp;
      try {
        temp = VZeroFitter(tr1, tr2, beamSpotHandle, primaryVertex, bfield, ttBuilder, iEvent);
      } catch (...) {
        continue;
      }

      if (temp.at("type") < 0.5) continue;
      // storeKsOnly: skip Λ / Λ̄ rows (type 2/3) — first-C only needs Ks
      if (storeKsOnly_ && temp.at("type") > 1.5) continue;

      _V0InvMass[_nV0s] = static_cast<float>(temp.at("invmass"));
      _V0Type[_nV0s] = static_cast<unsigned>(temp.at("type"));
      _V0X[_nV0s] = static_cast<float>(temp.at("vtxx"));
      _V0Y[_nV0s] = static_cast<float>(temp.at("vtxy"));
      _V0Z[_nV0s] = static_cast<float>(temp.at("vtxz"));
      _V0RPV[_nV0s] = static_cast<float>(temp.at("vtxr_pv"));
      _V0RBS[_nV0s] = static_cast<float>(temp.at("vtxr_bs"));
      _V0RPVSig[_nV0s] = static_cast<float>(temp.at("vtxrsig_pv"));
      _V0RBSSig[_nV0s] = static_cast<float>(temp.at("vtxrsig_bs"));
      _V0Px[_nV0s] = static_cast<float>(temp.at("px"));
      _V0Py[_nV0s] = static_cast<float>(temp.at("py"));
      _V0Pt[_nV0s] = static_cast<float>(temp.at("pt"));
      _V0Eta[_nV0s] = static_cast<float>(temp.at("eta"));
      _V0Phi[_nV0s] = static_cast<float>(temp.at("phi"));
      _V0DCA[_nV0s] = static_cast<float>(temp.at("dca"));
      _V0VtxNormChi2[_nV0s] = static_cast<float>(temp.at("vtxnormchi2"));
      _V0PtPos[_nV0s] = static_cast<float>(temp.at("ptpos"));
      _V0PtNeg[_nV0s] = static_cast<float>(temp.at("ptneg"));
      _V0EtaPos[_nV0s] = static_cast<float>(temp.at("etapos"));
      _V0EtaNeg[_nV0s] = static_cast<float>(temp.at("etaneg"));
      _V0PhiPos[_nV0s] = static_cast<float>(temp.at("phipos"));
      _V0PhiNeg[_nV0s] = static_cast<float>(temp.at("phineg"));
      _V0NHitsPos[_nV0s] = static_cast<float>(temp.at("nhitspos"));
      _V0NHitsNeg[_nV0s] = static_cast<float>(temp.at("nhitsneg"));
      _V0NormChi2Pos[_nV0s] = static_cast<float>(temp.at("normchi2pos"));
      _V0NormChi2Neg[_nV0s] = static_cast<float>(temp.at("normchi2neg"));
      _V0D0Pos[_nV0s] = static_cast<float>(temp.at("d0pos"));
      _V0DzPos[_nV0s] = static_cast<float>(temp.at("dzpos"));
      _V0D0Neg[_nV0s] = static_cast<float>(temp.at("d0neg"));
      _V0DzNeg[_nV0s] = static_cast<float>(temp.at("dzneg"));

      ++_nV0s;
      if (_nV0s == nV0s_max) break;
    }
    if (_nV0s == nV0s_max) break;
  }
}

reco::TransientTrack V0Analyzer::makeTransientTrack(
    const reco::Track& tr,
    const MagneticField* bfield,
    const TransientTrackBuilder* ttBuilder) const {
  if (ttBuilder) {
    return ttBuilder->build(tr);
  }
  return reco::TransientTrack(tr, bfield);
}

std::unordered_map<std::string, double> V0Analyzer::getTrackVariables(
    const reco::Track& tr,
    edm::Handle<reco::BeamSpot> beamSpotHandle,
    const MagneticField* bfield) {
  std::unordered_map<std::string, double> outputmap = {
      {"loosequality", 0.},
      {"transip", 0.},
      {"pass", 0.}};
  outputmap["loosequality"] = (tr.quality(reco::TrackBase::qualityByName("loose"))) ? 1. : 0.;
  if (outputmap["loosequality"] < 0.5) return outputmap;
  FreeTrajectoryState initialFTS = trajectoryStateTransform::initialFreeState(tr, bfield);
  TSCBLBuilderNoMaterial blsBuilder;
  TrajectoryStateClosestToBeamLine tscb(blsBuilder(initialFTS, *beamSpotHandle));
  if (!tscb.isValid()) {
    outputmap["pass"] = 0.;
    return outputmap;
  }
  outputmap["transip"] = tscb.transverseImpactParameter().significance();
  if (outputmap["transip"] < 2.) return outputmap;
  outputmap["pass"] = 1.;
  return outputmap;
}

namespace {
reco::Track fixTrackCovariance(const reco::Track& tk, double delta = 1e-6) {
  // see here: https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackingPOGRecommendations
  unsigned int i, j;
  double min_eig = 1;
  reco::TrackBase::CovarianceMatrix cov = tk.covariance();
  TMatrixDSym new_cov(cov.kRows);
  for (i = 0; i < cov.kRows; i++) {
    for (j = 0; j < cov.kRows; j++) {
      if (std::isnan(cov(i, j)) || std::isinf(cov(i, j))) cov(i, j) = 1e-6;
      new_cov(i, j) = cov(i, j);
    }
  }
  TVectorD eig(cov.kRows);
  new_cov.EigenVectors(eig);
  for (i = 0; i < cov.kRows; i++) {
    if (eig(i) < min_eig) {
      min_eig = eig(i);
    }
  }
  if (min_eig < 0) {
    for (i = 0; i < cov.kRows; i++) {
      cov(i, i) -= min_eig - delta;
    }
  }
  return reco::Track(tk.chi2(),
                     tk.ndof(),
                     tk.referencePoint(),
                     tk.momentum(),
                     tk.charge(),
                     cov,
                     tk.algo(),
                     (reco::TrackBase::TrackQuality)tk.qualityMask());
}
}  // namespace

std::unordered_map<std::string, double> V0Analyzer::VZeroFitter(
    const reco::Track& tr1,
    const reco::Track& tr2,
    edm::Handle<reco::BeamSpot> beamSpotHandle,
    const reco::Vertex& primaryVertex,
    const MagneticField* bfield,
    const TransientTrackBuilder* ttBuilder,
    const edm::Event& /*iEvent*/) {
  // FIT AND SELECT V0 VERTICES FROM TWO TRACKS AND CALCULATE PROPERTIES
  std::unordered_map<std::string, double> outputmap = {
      {"type", -1.}, {"invmass", 0.},
      {"vtxx", 0.}, {"vtxy", 0.}, {"vtxz", 0.},
      {"vtxr_pv", 0.}, {"vtxr_bs", 0.},
      {"vtxrsig_pv", 0.}, {"vtxrsig_bs", 0.},
      {"px", 0.}, {"py", 0.}, {"pt", 0.},
      {"eta", 0.}, {"phi", 0.},
      {"dca", 0.},
      {"vtxnormchi2", 0.},
      {"ptpos", 0.}, {"ptneg", 0.},
      {"etapos", 0.}, {"etaneg", 0.},
      {"phipos", 0.}, {"phineg", 0.},
      {"nhitspos", 0.}, {"nhitsneg", 0.},
      {"normchi2pos", 0.}, {"normchi2neg", 0.},
      {"d0pos", 0.}, {"dzpos", 0.}, {"d0neg", 0.}, {"dzneg", 0.}};

  if (tr1.charge() * tr2.charge() > 0) return outputmap;

  reco::TransientTrack trtr1 = makeTransientTrack(tr1, bfield, ttBuilder);
  reco::TransientTrack trtr2 = makeTransientTrack(tr2, bfield, ttBuilder);
  if (!trtr1.impactPointTSCP().isValid() or !trtr2.impactPointTSCP().isValid()) return outputmap;
  FreeTrajectoryState state1 = trtr1.impactPointTSCP().theState();
  FreeTrajectoryState state2 = trtr2.impactPointTSCP().theState();
  ClosestApproachInRPhi capp;
  capp.calculate(state1, state2);
  if (!capp.status()) return outputmap;
  double dca = fabs(capp.distance());
  outputmap["dca"] = dca;
  GlobalPoint cxpt = capp.crossingPoint();
  if (dca < 0. or dca > 1.) return outputmap;
  if (std::sqrt(cxpt.x() * cxpt.x() + cxpt.y() * cxpt.y()) > 120. or std::abs(cxpt.z()) > 300.)
    return outputmap;

  TrajectoryStateClosestToPoint tscp1 = trtr1.trajectoryStateClosestToPoint(cxpt);
  TrajectoryStateClosestToPoint tscp2 = trtr2.trajectoryStateClosestToPoint(cxpt);
  if (!tscp1.isValid() or !tscp2.isValid()) return outputmap;

  reco::Track tr1fix = fixTrackCovariance(tr1);
  reco::Track tr2fix = fixTrackCovariance(tr2);
  std::vector<reco::TransientTrack> transtracks;
  transtracks.push_back(makeTransientTrack(tr1fix, bfield, ttBuilder));
  transtracks.push_back(makeTransientTrack(tr2fix, bfield, ttBuilder));
  KalmanVertexFitter vtxFitter(true);
  TransientVertex v0vtx = vtxFitter.vertex(transtracks);
  if (!v0vtx.isValid()) return outputmap;
  if (v0vtx.normalisedChiSquared() > 15.) return outputmap;
  if (v0vtx.normalisedChiSquared() < 0.) return outputmap;
  outputmap["vtxnormchi2"] = v0vtx.normalisedChiSquared();
  std::vector<reco::TransientTrack> refittedTracks;
  if (v0vtx.hasRefittedTracks())
    refittedTracks = v0vtx.refittedTracks();
  else
    return outputmap;

  reco::Vertex v0recovtx = v0vtx;
  outputmap["vtxx"] = v0recovtx.position().x();
  outputmap["vtxy"] = v0recovtx.position().y();
  outputmap["vtxz"] = v0recovtx.position().z();
  GlobalPoint vtxXYZ(v0vtx.position().x(), v0vtx.position().y(), v0vtx.position().z());
  GlobalPoint beamSpotXYZ(beamSpotHandle->position().x(),
                          beamSpotHandle->position().y(),
                          beamSpotHandle->position().z());
  GlobalPoint primaryVertexXYZ(primaryVertex.position().x(),
                               primaryVertex.position().y(),
                               primaryVertex.position().z());

  ROOT::Math::SVector<double, 3> vtxrvec_bs(vtxXYZ.x() - beamSpotXYZ.x(), vtxXYZ.y() - beamSpotXYZ.y(), 0.);
  double vtxr_bs = ROOT::Math::Mag(vtxrvec_bs);
  ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3>> totalcovmat_bs =
      beamSpotHandle->rotatedCovariance3D() + v0recovtx.covariance();
  double vtxrunc_bs = sqrt(ROOT::Math::Similarity(totalcovmat_bs, vtxrvec_bs)) / vtxr_bs;
  double vtxrsig_bs = vtxr_bs / vtxrunc_bs;
  outputmap["vtxr_bs"] = vtxr_bs;
  outputmap["vtxrsig_bs"] = vtxrsig_bs;

  ROOT::Math::SVector<double, 3> vtxrvec_pv(vtxXYZ.x() - primaryVertexXYZ.x(),
                                           vtxXYZ.y() - primaryVertexXYZ.y(),
                                           0.);
  double vtxr_pv = ROOT::Math::Mag(vtxrvec_pv);
  ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3>> totalcovmat_pv =
      primaryVertex.covariance() + v0recovtx.covariance();
  double vtxrunc_pv = sqrt(ROOT::Math::Similarity(totalcovmat_pv, vtxrvec_pv)) / vtxr_pv;
  double vtxrsig_pv = vtxr_pv / vtxrunc_pv;
  outputmap["vtxr_pv"] = vtxr_pv;
  outputmap["vtxrsig_pv"] = vtxrsig_pv;

  reco::Track postrack;
  reco::Track negtrack;
  reco::TransientTrack posrefittedtranstrack;
  reco::TransientTrack negrefittedtranstrack;
  if (tr1.charge() > 0. and tr2.charge() < 0) {
    postrack = tr1;
    negtrack = tr2;
    posrefittedtranstrack = refittedTracks.at(0);
    negrefittedtranstrack = refittedTracks.at(1);
  } else if (tr1.charge() < 0. and tr2.charge() > 0) {
    postrack = tr2;
    negtrack = tr1;
    posrefittedtranstrack = refittedTracks.at(1);
    negrefittedtranstrack = refittedTracks.at(0);
  } else
    return outputmap;
  TrajectoryStateClosestToPoint postscp = posrefittedtranstrack.trajectoryStateClosestToPoint(vtxXYZ);
  TrajectoryStateClosestToPoint negtscp = negrefittedtranstrack.trajectoryStateClosestToPoint(vtxXYZ);
  if (!postscp.isValid() or !negtscp.isValid()) return outputmap;
  GlobalVector positiveP(postscp.momentum());
  outputmap["ptpos"] = positiveP.transverse();
  outputmap["etapos"] = positiveP.eta();
  outputmap["phipos"] = positiveP.phi();
  GlobalVector negativeP(negtscp.momentum());
  outputmap["ptneg"] = negativeP.transverse();
  outputmap["etaneg"] = negativeP.eta();
  outputmap["phineg"] = negativeP.phi();
  GlobalVector totalP(positiveP + negativeP);
  outputmap["px"] = totalP.x();
  outputmap["py"] = totalP.y();
  outputmap["pt"] = totalP.transverse();
  outputmap["eta"] = totalP.eta();
  outputmap["phi"] = totalP.phi();

  double piPlusE = sqrt(positiveP.mag2() + pimass2);
  double piMinE = sqrt(negativeP.mag2() + pimass2);
  double pE = sqrt(positiveP.mag2() + pmass2);
  double pBarE = sqrt(negativeP.mag2() + pmass2);
  double KsETot = piPlusE + piMinE;
  double LambdaETot = pE + piMinE;
  double LambdaBarETot = pBarE + piPlusE;
  math::XYZTLorentzVector KsP4(totalP.x(), totalP.y(), totalP.z(), KsETot);
  double KsInvMass = KsP4.M();
  math::XYZTLorentzVector LambdaP4(totalP.x(), totalP.y(), totalP.z(), LambdaETot);
  double LambdaInvMass = LambdaP4.M();
  math::XYZTLorentzVector LambdaBarP4(totalP.x(), totalP.y(), totalP.z(), LambdaBarETot);
  double LambdaBarInvMass = LambdaBarP4.M();

  // Mass window: storeKsOnly keeps any pair in the Ks window as type=1
  // (do not discard when closer to Λ — first-C only needs the ππ hypothesis).
  if (storeKsOnly_) {
    if (std::abs(KsInvMass - ksmass) > 0.07) return outputmap;
  } else if (std::abs(KsInvMass - ksmass) > 0.07 and std::abs(LambdaInvMass - lambdamass) > 0.05 and
             std::abs(LambdaBarInvMass - lambdamass) > 0.05) {
    return outputmap;
  }

  outputmap["nhitspos"] = postrack.numberOfValidHits();
  outputmap["nhitsneg"] = negtrack.numberOfValidHits();
  outputmap["normchi2pos"] = postrack.normalizedChi2();
  outputmap["normchi2neg"] = negtrack.normalizedChi2();
  reco::TrackBase::Point refPoint(
      primaryVertex.position().x(), primaryVertex.position().y(), primaryVertex.position().z());
  outputmap["d0pos"] = postrack.dxy(refPoint);
  outputmap["dzpos"] = postrack.dz(refPoint);
  outputmap["d0neg"] = negtrack.dxy(refPoint);
  outputmap["dzneg"] = negtrack.dz(refPoint);
  // Isolation intentionally not computed (unused by first-C / v0builder).

  if (storeKsOnly_) {
    outputmap["invmass"] = KsInvMass;
    outputmap["type"] = 1.;
    return outputmap;
  }

  if (std::abs(KsInvMass - ksmass) < 0.07 and
      std::abs(KsInvMass - ksmass) < std::abs(LambdaInvMass - lambdamass) and
      std::abs(KsInvMass - ksmass) < std::abs(LambdaBarInvMass - lambdamass)) {
    outputmap["invmass"] = KsInvMass;
    outputmap["type"] = 1.;
    return outputmap;
  }
  if (std::abs(LambdaInvMass - lambdamass) < 0.05 and
      std::abs(LambdaInvMass - lambdamass) < std::abs(KsInvMass - ksmass) and
      std::abs(LambdaInvMass - lambdamass) < std::abs(LambdaBarInvMass - lambdamass)) {
    outputmap["invmass"] = LambdaInvMass;
    outputmap["type"] = 2.;
    return outputmap;
  }
  if (std::abs(LambdaBarInvMass - lambdamass) < 0.05 and
      std::abs(LambdaBarInvMass - lambdamass) < std::abs(KsInvMass - ksmass) and
      std::abs(LambdaBarInvMass - lambdamass) < std::abs(LambdaInvMass - lambdamass)) {
    outputmap["invmass"] = LambdaBarInvMass;
    outputmap["type"] = 3.;
    return outputmap;
  }
  return outputmap;
}
