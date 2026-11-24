import FWCore.ParameterSet.Config as cms

# Slim DisplacedV0 ntuple producer (Run3 / 2024 MiniAOD).
# GTs: prefer autoCond aliases; pin exact strings in conditions.md on first CRAB.

displacedV0Ntuple = cms.EDAnalyzer(
    "DisplacedV0Ntuple",
    isData=cms.bool(True),
    # MagField: False = UniformMagneticField(3.8 T) in V0Analyzer (smoke-friendly; no MagField ES).
    # True  = IdealMagneticFieldRecord + TransientTrackBuilder via esConsumes
    #         (load MagneticField_cff + Geometry + TransientTrackBuilder_cfi;
    #         see docs/cmsrun-smoke-test.md).
    useESMagneticField=cms.bool(False),
    # First-C / CDTE-30: write only Ks (V0Type==1). Set False to also store Λ/Λ̄.
    storeKsOnly=cms.bool(True),
    # CDTE-31: skip tree Fill when _nV0s==0 (size win). Trade-off: nimloth loses
    # zero-Ks DY control events; set False to keep them. Path dimuon filter stays.
    skipFillIfNoV0=cms.bool(True),
    # DeepJet loose WP for passDeepJetLooseVeto (keep in sync with
    # analysis/config_defaults_run3.py DEEPJET_LOOSE_WP; TODO-VERIFY BTV JSON).
    deepJetLooseWP=cms.double(0.0494),
    muons=cms.InputTag("slimmedMuons"),
    jets=cms.InputTag("slimmedJetsPuppi"),  # AK4 PUPPI; confirm era default
    packedCandidates=cms.InputTag("packedPFCandidates"),
    # TODO-VERIFY on lxplus: tag remains "lostTracks" for 2024 MiniAODv4/v6.
    lostTracks=cms.InputTag("lostTracks"),
    vertices=cms.InputTag("offlineSlimmedPrimaryVertices"),
    beamSpot=cms.InputTag("offlineBeamSpot"),
    triggerResults=cms.InputTag("TriggerResults", "", "HLT"),
    # MC-only (consumed when isData=False); safe to leave set for data configs
    genEventInfo=cms.InputTag("generator"),
    pileupInfo=cms.InputTag("slimmedAddPileupInfo"),
    # Dimuon HLT OR list — baseline Mass3p8; add Mass8 if present in era menu.
    # Per-path HLT_* leaves are not stored (passDimuonHLT only).
    hltPaths=cms.vstring(
        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
        # "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
    ),
)
