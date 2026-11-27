"""Local smoke: DY MiniAODSIM one file.

Placeholder for one-file ``cmsRun`` only. CRAB production uses
``displacedV0_mc_cfg.py`` (same DisplacedV0 sequence, ``maxEvents=-1``).

Usage (from $CMSSW_BASE/src after cmsenv + scram b):
  cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaodsim.root maxEvents=200

  cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaodsim.root maxEvents=200 useESMagneticField=True

  cmsRun K0sAnalysis/DisplacedV0/python/test_mc_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaodsim.root maxEvents=200 enableDimuonPreFilter=False

Era: Run3_2024. GT: auto:phase1_2024_realistic.
Expect genWeight / Pileup_nTrue filled; same V0/muon/jet/HLT branches as data.
"""
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.maxEvents = 200
options.inputFiles = "file:PLACEHOLDER_DY_MINIAODSIM.root"
options.register(
    "useESMagneticField",
    False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use IdealMagneticFieldRecord + TransientTrackBuilder instead of UniformMagneticField(3.8)",
)
options.register(
    "enableDimuonPreFilter",
    True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "AN §5 dimuon pre-filter ahead of V0Analyzer (disable for debugging)",
)
options.parseArguments()

process = cms.Process("DisplacedV0MC", eras.Run3_2024)

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles),
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, "auto:phase1_2024_realistic", "")

# See test_data_onefile_cfg.py / docs/cmsrun-smoke-test.md for MagField notes.
if options.useESMagneticField:
    process.load("Configuration.StandardSequences.MagneticField_cff")
    process.load("Configuration.Geometry.GeometryRecoDB_cff")
    process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string("displacedV0_mc_smoke.root")
)

from K0sAnalysis.DisplacedV0.displacedV0_cfi import displacedV0Ntuple
from K0sAnalysis.DisplacedV0.dimuonPreFilter_cfi import dimuonPreFilter
from K0sAnalysis.DisplacedV0.genWeightCounter_cfi import genWeightCounter

process.displacedV0Ntuple = displacedV0Ntuple.clone(
    isData=cms.bool(False),
    useESMagneticField=cms.bool(options.useESMagneticField),
)
process.dimuonPreFilter = dimuonPreFilter.clone()
process.genWeightCounter = genWeightCounter.clone()

if options.enableDimuonPreFilter:
    process.p = cms.Path(
        process.genWeightCounter + process.dimuonPreFilter + process.displacedV0Ntuple
    )
else:
    process.p = cms.Path(process.genWeightCounter + process.displacedV0Ntuple)
