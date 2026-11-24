"""Production DisplacedV0 cfg for Summer24 DY MiniAODSIM (CRAB).

Wraps the same ``displacedV0Ntuple`` sequence as ``test_mc_onefile_cfg.py``.
The one-file smoke cfg remains the local ``cmsRun`` placeholder; this file is
the CRAB ``psetName`` (``maxEvents=-1``, production output name).

Usage (CRAB sets input via PoolSource rewrite):
  # see ntuplizer/DisplacedV0/test/crab_mc_dy*.py
  cmsRun DisplacedV0/python/displacedV0_mc_cfg.py \\
    inputFiles=file:/path/to/miniaodsim.root maxEvents=200 \\
    outputFile=displacedV0_DY_Summer24.root

Era: Run3_2024. GT: auto:phase1_2024_realistic (pin in conditions.md on first submit).
"""
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing("analysis")
options.maxEvents = -1
options.inputFiles = "file:PLACEHOLDER_DY_MINIAODSIM.root"
options.register(
    "outputFile",
    "displacedV0_mc.root",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "TFileService output; must match CRAB JobType.outputFiles",
)
options.register(
    "useESMagneticField",
    False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use IdealMagneticFieldRecord instead of OAEParametrizedMagneticField(3_8T)",
)
options.parseArguments()

process = cms.Process("DisplacedV0MC", eras.Run3_2024)

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles),
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, "auto:phase1_2024_realistic", "")

# See displacedV0_data_cfg.py / docs/cmsrun-smoke-test.md for MagField notes.
if options.useESMagneticField:
    process.load("Configuration.StandardSequences.MagneticField_cff")
    process.load("Configuration.Geometry.GeometryRecoDB_cff")
    process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string(options.outputFile)
)

from DisplacedV0.displacedV0_cfi import displacedV0Ntuple

process.displacedV0Ntuple = displacedV0Ntuple.clone(
    isData=cms.bool(False),
    useESMagneticField=cms.bool(options.useESMagneticField),
)
process.p = cms.Path(process.displacedV0Ntuple)
