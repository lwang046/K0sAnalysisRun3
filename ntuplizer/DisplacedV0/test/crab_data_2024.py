"""CRAB3 stub — first era Run2024D Muon MiniAOD. Fill from samples/data_muon_2024.txt."""
from CRABClient.UserUtilities import config

config = config()
# First C(Δ2D) era: Run2024D (see samples/data_muon_2024.txt / conditions.md).
config.General.requestName = "DisplacedV0_Muon0_Run2024D"  # TODO-VERIFY on DAS
config.General.workArea = "crab_DisplacedV0_data"
config.General.transferOutputs = True

config.JobType.pluginName = "Analysis"
config.JobType.psetName = "../python/test_data_onefile_cfg.py"  # replace with production cfg
config.JobType.outputFiles = ["displacedV0_data.root"]

# TODO-VERIFY on DAS; also submit Muon1 with the same era / lumiMask.
# If PromptReco missing, use MiniAODv6 parent of MINIv6NANOv15 (das parent query).
config.Data.inputDataset = "/Muon0/Run2024D-PromptReco-v1/MINIAOD"
config.Data.inputDBS = "global"
config.Data.splitting = "LumiBased"
config.Data.unitsPerJob = 50
# TODO-VERIFY latest: samples/cert/README.md
config.Data.lumiMask = (
    "/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/"
    "Cert_Collisions2024_378981_386951_Golden.json"
)
config.Data.publication = False
config.Data.outputDatasetTag = "DisplacedV0_Run3_v0"

config.Site.storageSite = "T2_XX_XXX"  # PLACEHOLDER
