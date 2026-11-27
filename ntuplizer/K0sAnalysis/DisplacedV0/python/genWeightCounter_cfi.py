"""MC-only pre-filter genWeight counter → TH1 ``hCounter``.

Must run *before* ``dimuonPreFilter`` on the Path so rejected events still
enter Σw. Wire only on MC cfgs (data has no GenEventInfoProduct).
"""
import FWCore.ParameterSet.Config as cms

genWeightCounter = cms.EDAnalyzer(
    "GenWeightCounter",
    genEventInfo=cms.InputTag("generator"),
)
