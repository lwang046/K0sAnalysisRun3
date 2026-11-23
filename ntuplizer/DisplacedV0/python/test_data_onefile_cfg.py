"""Local smoke: 100–1000 events of 2024 Muon MiniAOD.

Usage (from $CMSSW_BASE/src after cmsenv + scram b):
  cmsRun DisplacedV0/python/test_data_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaod.root maxEvents=200

Era: Run3. GT: auto:run3_data.
Expect tree displacedV0Ntuple/events with nMuon, _nV0s, _V0InvMass peak near 0.498
for _V0Type==1 (Ks).
"""
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.maxEvents = 200
options.inputFiles = "file:PLACEHOLDER_DATA_MINIAOD.root"
options.parseArguments()

process = cms.Process("DisplacedV0Data", eras.Run3)

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles),
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, "auto:run3_data", "")

# MagField / Geometry / TransientTrackBuilder are NOT loaded here on purpose:
# V0Analyzer currently constructs OAEParametrizedMagneticField("3_8T") in-process
# (see docs/cmsrun-smoke-test.md). Load MagneticField_cff + GeometryRecoDB_cff +
# TransientTrackBuilder_cfi only if migrating to ESGetToken / TransientTrackBuilder.

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string("displacedV0_data_smoke.root")
)

# CMSSW maps Package/python/foo.py → Package.foo (not Package.python.foo)
from DisplacedV0.displacedV0_cfi import displacedV0Ntuple

process.displacedV0Ntuple = displacedV0Ntuple.clone(isData=cms.bool(True))
process.p = cms.Path(process.displacedV0Ntuple)
