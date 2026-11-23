"""CRAB3 stub — DYto2L MLL>50 13p6 MiniAODSIM. Fill from samples/sim_dy_m50_13p6.txt."""
from CRABClient.UserUtilities import config

config = config()
config.General.requestName = "DisplacedV0_DYto2L_MLL50_13p6"
config.General.workArea = "crab_DisplacedV0_mc"
config.General.transferOutputs = True

config.JobType.pluginName = "Analysis"
config.JobType.psetName = "../python/test_mc_onefile_cfg.py"
config.JobType.outputFiles = ["displacedV0_mc.root"]

# PdmV Summer24 naming (not legacy DYJetsToLL). TODO-VERIFY full string on DAS.
# 150X_ token → CMSSW_15_0_X; if only 140X_ exists, switch release + dataset.
config.Data.inputDataset = (
    "/DYto2L-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/"
    "RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM"
)
config.Data.inputDBS = "global"
config.Data.splitting = "FileBased"
config.Data.unitsPerJob = 2
config.Data.publication = False
config.Data.outputDatasetTag = "DisplacedV0_Run3_DY_v0"

config.Site.storageSite = "T2_XX_XXX"  # PLACEHOLDER
