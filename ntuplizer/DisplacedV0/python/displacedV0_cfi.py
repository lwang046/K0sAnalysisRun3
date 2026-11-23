import FWCore.ParameterSet.Config as cms

# Slim DisplacedV0 ntuple producer (Run3 / 2024 MiniAOD).
# GTs: prefer autoCond aliases; pin exact strings in conditions.md on first CRAB.

displacedV0Ntuple = cms.EDAnalyzer(
    "DisplacedV0Ntuple",
    isData=cms.bool(True),
    # MagField: False = OAEParametrizedMagneticField("3_8T") in V0Analyzer (smoke-friendly).
    # True  = IdealMagneticFieldRecord via ESGetToken (load MagneticField_cff + Geometry
    #         in the cfg; see docs/cmsrun-smoke-test.md). Next step if needed:
    #         TransientTrackBuilder from TransientTrackRecord.
    useESMagneticField=cms.bool(False),
    muons=cms.InputTag("slimmedMuons"),
    jets=cms.InputTag("slimmedJetsPuppi"),  # AK4 PUPPI; confirm era default
    packedCandidates=cms.InputTag("packedPFCandidates"),
    lostTracks=cms.InputTag("lostTracks"),
    vertices=cms.InputTag("offlineSlimmedPrimaryVertices"),
    beamSpot=cms.InputTag("offlineBeamSpot"),
    triggerResults=cms.InputTag("TriggerResults", "", "HLT"),
    # MC-only (consumed when isData=False); safe to leave set for data configs
    genEventInfo=cms.InputTag("generator"),
    pileupInfo=cms.InputTag("slimmedAddPileupInfo"),
    # Dimuon HLT OR list — baseline Mass3p8; add Mass8 if present in era menu
    hltPaths=cms.vstring(
        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
        # "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8",
    ),
)
