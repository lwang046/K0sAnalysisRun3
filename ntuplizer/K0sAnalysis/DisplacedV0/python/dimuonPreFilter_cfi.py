import FWCore.ParameterSet.Config as cms

# AN §5-style DY dimuon pre-filter (Neon / CDTE-20).
# Defaults match v0building/v0builder.py dy_event_mask muon+mass cuts
# (HLT OR and DeepJet b-veto stay outside this lightweight Path filter).

dimuonPreFilter = cms.EDFilter(
    "DimuonPreFilter",
    muons=cms.InputTag("slimmedMuons"),
    minLeadingPt=cms.double(30.0),
    minTrailingPt=cms.double(25.0),
    maxAbsEta=cms.double(2.4),
    zMassWindow=cms.double(10.0),
    zMass=cms.double(91.1876),
)
