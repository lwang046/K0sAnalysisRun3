"""Local smoke: 100–1000 events of 2024 Muon MiniAOD.

Placeholder for one-file ``cmsRun`` only. CRAB production uses
``displacedV0_data_cfg.py`` (same DisplacedV0 sequence, ``maxEvents=-1``).

Usage (from $CMSSW_BASE/src after cmsenv + scram b):
  cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaod.root maxEvents=200

  # Optional ES MagField + TransientTrackBuilder path:
  cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaod.root maxEvents=200 useESMagneticField=True

  # Disable AN §5 dimuon pre-filter (debug / efficiency studies):
  cmsRun K0sAnalysis/DisplacedV0/python/test_data_onefile_cfg.py \\
    inputFiles=file:/path/to/miniaod.root maxEvents=200 enableDimuonPreFilter=False

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

# MagField / Geometry / TransientTrackBuilder:
# Default (useESMagneticField=False): UniformMagneticField(3.8 T) in C++ —
# no MagField ES products required (see docs/cmsrun-smoke-test.md).
# ES path: IdealMagneticFieldRecord + TransientTrackBuilder tokens.
if options.useESMagneticField:
    process.load("Configuration.StandardSequences.MagneticField_cff")
    process.load("Configuration.Geometry.GeometryRecoDB_cff")
    process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string("displacedV0_data_smoke.root")
)

# CMSSW maps Subsystem/Package/python/foo.py → Subsystem.Package.foo
from K0sAnalysis.DisplacedV0.displacedV0_cfi import displacedV0Ntuple
from K0sAnalysis.DisplacedV0.dimuonPreFilter_cfi import dimuonPreFilter

process.displacedV0Ntuple = displacedV0Ntuple.clone(
    isData=cms.bool(True),
    useESMagneticField=cms.bool(options.useESMagneticField),
)
process.dimuonPreFilter = dimuonPreFilter.clone()

if options.enableDimuonPreFilter:
    process.p = cms.Path(process.dimuonPreFilter + process.displacedV0Ntuple)
else:
    process.p = cms.Path(process.displacedV0Ntuple)
