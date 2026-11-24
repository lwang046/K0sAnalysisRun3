/*
 Custom analyzer for secondary vertices from light neutral hadron (V0) decays.

 Ported from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/V0Analyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Adapted for K0sAnalysisRun3 slim package:
   - friend/owner class: DisplacedV0Ntuple (was multilep)
   - include paths: K0sAnalysis/DisplacedV0/... (scram Subsystem/Package)
   - MagField: default UniformMagneticField(3.8 T) smoke fallback; optional ES
     IdealMagneticFieldRecord + TransientTrackBuilder/TransientTrackRecord
     via DisplacedV0Ntuple::useESMagneticField_
   - Sol schema (after CDTE-30/31): keep compact event layout (no Jet_* /
     unused fat leaves); restore daughter ηφ/dxy/dz + packed/lost provenance;
     parent ηφ + pointing cosines; neighbour charged-ΔR stubs (TODO)
 Physics / Kalman logic matches upstream; AN-20-111 §6 tight cuts remain in
 offline v0building/v0selections.py.
*/
#ifndef DisplacedV0_V0Analyzer_h
#define DisplacedV0_V0Analyzer_h

// system include files
#include <memory>
#include <unordered_map>
#include <Math/SVector.h>
#include <Math/SMatrix.h>
#include "TMatrixDSym.h"
#include "TVectorD.h"

// main include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

// general include files
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "TTree.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/Math/interface/deltaR.h"

// vertex fitter include files
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateTransform.h"
#include "TrackingTools/PatternTools/interface/TSCBLBuilderNoMaterial.h"
#include "TrackingTools/PatternTools/interface/ClosestApproachInRPhi.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"

// data format include files
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/Candidate/interface/VertexCompositeCandidate.h"
#include "DataFormats/Candidate/interface/VertexCompositeCandidateFwd.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/Candidate/interface/VertexCompositePtrCandidate.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

class DisplacedV0Ntuple;

class V0Analyzer {
  friend class DisplacedV0Ntuple;
private:
  // constants
  static constexpr double pimass = 0.13957;
  static constexpr double pimass2 = pimass * pimass;
  static constexpr double pmass = 0.93827;
  static constexpr double pmass2 = pmass * pmass;
  static constexpr double emass = 0.000511;
  static constexpr double emass2 = emass * emass;
  static constexpr double mumass = 0.1057;
  static constexpr double mumass2 = mumass * mumass;
  static constexpr double ksmass = 0.49761;
  static constexpr double lambdamass = 1.1157;
  static constexpr double jpsimass = 3.0969;
  // Root tree variable declarations
  static const unsigned nV0s_max = 50;
  // First-C / Sol default: only write Ks after Λ/Λ̄ classification.
  bool storeKsOnly_{true};
  // beamspot / PV (float — GeV-scale precision is enough for cosθ_pointing)
  float _beamSpotX{0.f};
  float _beamSpotY{0.f};
  float _beamSpotZ{0.f};
  float _primaryVertexX{0.f};
  float _primaryVertexY{0.f};
  float _primaryVertexZ{0.f};
  // variables from customized V0 fitter
  unsigned _nV0s = 0;
  float _V0InvMass[nV0s_max]{};
  unsigned _V0Type[nV0s_max]{};
  float _V0X[nV0s_max]{};
  float _V0Y[nV0s_max]{};
  float _V0Z[nV0s_max]{};
  float _V0RPV[nV0s_max]{};
  float _V0RPVSig[nV0s_max]{};
  float _V0Px[nV0s_max]{};
  float _V0Py[nV0s_max]{};
  float _V0Pt[nV0s_max]{};
  float _V0Eta[nV0s_max]{};
  float _V0Phi[nV0s_max]{};
  float _V0DCA[nV0s_max]{};
  float _V0VtxNormChi2[nV0s_max]{};
  float _V0CosPointingPV[nV0s_max]{};
  float _V0CosPointingBS[nV0s_max]{};
  float _V0PtPos[nV0s_max]{};
  float _V0PtNeg[nV0s_max]{};
  float _V0EtaPos[nV0s_max]{};
  float _V0EtaNeg[nV0s_max]{};
  float _V0PhiPos[nV0s_max]{};
  float _V0PhiNeg[nV0s_max]{};
  float _V0NHitsPos[nV0s_max]{};
  float _V0NHitsNeg[nV0s_max]{};
  float _V0NormChi2Pos[nV0s_max]{};
  float _V0NormChi2Neg[nV0s_max]{};
  float _V0D0Pos[nV0s_max]{};
  float _V0DzPos[nV0s_max]{};
  float _V0D0Neg[nV0s_max]{};
  float _V0DzNeg[nV0s_max]{};
  // Daughter provenance: 0=packedPFCandidates, 1=lostTracks; index in that collection
  unsigned char _V0SrcPos[nV0s_max]{};
  unsigned char _V0SrcNeg[nV0s_max]{};
  int _V0IdxPos[nV0s_max]{};
  int _V0IdxNeg[nV0s_max]{};
  // Neighbour charged-track summary stubs (jet association not implemented yet)
  float _V0NearestChgDRPos[nV0s_max]{};
  float _V0NearestChgDRNeg[nV0s_max]{};
  unsigned char _V0NearestChgStatusPos[nV0s_max]{};
  unsigned char _V0NearestChgStatusNeg[nV0s_max]{};
  int _V0NChgDR01Pos[nV0s_max]{};
  int _V0NChgDR01Neg[nV0s_max]{};

  unsigned debugcounter = 0;

  DisplacedV0Ntuple* ntuple_{nullptr};

  /** Selected MiniAOD track with provenance for daughter source leaves. */
  struct SelTrack {
    reco::Track track;
    unsigned char src{0};  // 0=packed, 1=lost
    int idx{-1};
  };

public:
  V0Analyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~V0Analyzer();
  void beginJob(TTree*);
  void analyze(const edm::Event&, const edm::EventSetup&, const reco::Vertex&);
  /** Clear per-event V0/PV state so Fill() does not reuse the previous event. */
  void clear();
  /** Build TransientTrack via TransientTrackBuilder when non-null, else MagField*. */
  reco::TransientTrack makeTransientTrack(const reco::Track&,
                                          const MagneticField*,
                                          const TransientTrackBuilder*) const;
  std::unordered_map<std::string, double> getTrackVariables(
      const reco::Track&, edm::Handle<reco::BeamSpot>, const MagneticField*);
  std::unordered_map<std::string, double> VZeroFitter(
      const reco::Track&, const reco::Track&,
      edm::Handle<reco::BeamSpot>,
      const reco::Vertex&,
      const MagneticField*,
      const TransientTrackBuilder*,
      const edm::Event&);
};

#endif
