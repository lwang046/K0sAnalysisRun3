"""Shared CRAB3 builders for DisplacedV0 Run2024D + Summer24 DY.

Import from the thin submit scripts in this directory. Does **not** run CRAB;
set ``CRAB_STORAGE_SITE`` on lxplus before ``crab submit``.

storageSite
-----------
Do **not** invent a T2. Set one of:

  export CRAB_STORAGE_SITE=T2_CH_CERN   # example — use *your* writeable site
  # or edit STORAGE_SITE_PLACEHOLDER / pass storage_site=...

Samples / golden JSON
---------------------
Data + production DY frozen 2026-11-24 (lxplus): ``samples/data_muon_2024.txt``,
``samples/sim_dy_m50_13p6.txt``, ``conditions.md``.
PTLL-100 DYto2L is smoke-only (``MC_DAS_DY_SMOKE``).
Lumi mask: ``samples/cert/README.md`` (golden still TODO-VERIFY latest).
"""
from __future__ import annotations

import os

from CRABClient.UserUtilities import config as crab_config

# Single clearly marked placeholder — never a guessed real T2.
STORAGE_SITE_PLACEHOLDER = "T2_XX_PLACEHOLDER"

# TODO-VERIFY latest golden on DQM / samples/cert/README.md before submit.
GOLDEN_LUMIMASK = (
    "/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/"
    "Cert_Collisions2024_378981_386951_Golden.json"
)

# FROZEN 2026-11-24 (lxplus M3 smoke; see samples/data_muon_2024.txt).
DATA_DAS = {
    "Muon0": "/Muon0/Run2024D-PromptReco-v1/MINIAOD",
    "Muon1": "/Muon1/Run2024D-PromptReco-v1/MINIAOD",
}

# FROZEN 2026-11-24: inclusive DYto2Mu MLL>50 MiniAODv6 (no PTLL cut).
# Combined DYto2L Bin-MLL-50 Summer24 remains empty in DAS; PTLL-binned DYto2L
# only — do NOT use those for first-C. See samples/sim_dy_m50_13p6.txt.
# CMSSW_15_0_22 + el9_amd64_gcc12. 13462 files / ~4.89e8 events (lxplus DAS).
MC_DAS_DY = (
    "/DYto2Mu-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/"
    "RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v6/MINIAODSIM"
)

# Smoke-only: populated DYto2L PTLL-100 (7346 files) from M3 cmsRun.
# Gen-level pT(ℓℓ)>100 — NOT phase-space matched to inclusive Run2024D data.
MC_DAS_DY_SMOKE = (
    "/DYto2L-2Jets_Bin-MLL-50-PTLL-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/"
    "RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v3/MINIAODSIM"
)

# Production psets (smoke one-file cfgs are local cmsRun only).
PSET_DATA = "../python/displacedV0_data_cfg.py"
PSET_MC = "../python/displacedV0_mc_cfg.py"


def resolve_storage_site(explicit: str | None = None) -> str:
    """Prefer explicit arg, then CRAB_STORAGE_SITE env, else PLACEHOLDER."""
    if explicit:
        return explicit
    return os.environ.get("CRAB_STORAGE_SITE", STORAGE_SITE_PLACEHOLDER)


def build_data_config(
    muon_pd: str = "Muon0",
    *,
    smoke: bool = False,
    storage_site: str | None = None,
):
    """CRAB config for Run2024D Muon0 or Muon1 MiniAOD.

    Naming aligns with the first-C recipe / v0building paths:
      requestName / outputDatasetTag / output file → DisplacedV0_Muon{0,1}_Run2024D
    """
    if muon_pd not in DATA_DAS:
        raise ValueError(f"muon_pd must be one of {sorted(DATA_DAS)}, got {muon_pd!r}")

    tag = f"DisplacedV0_{muon_pd}_Run2024D"
    out_file = f"{tag}.root"
    site = resolve_storage_site(storage_site)

    cfg = crab_config()
    cfg.General.requestName = f"{tag}_smoke" if smoke else tag
    cfg.General.workArea = "crab_DisplacedV0_data"
    cfg.General.transferOutputs = True
    cfg.General.transferLogs = True

    cfg.JobType.pluginName = "Analysis"
    cfg.JobType.psetName = PSET_DATA
    cfg.JobType.pyCfgParams = [f"outputFile={out_file}"]
    cfg.JobType.outputFiles = [out_file]

    # Frozen DAS — samples/data_muon_2024.txt + conditions.md.
    cfg.Data.inputDataset = DATA_DAS[muon_pd]
    cfg.Data.inputDBS = "global"
    cfg.Data.splitting = "LumiBased"
    # TODO-VERIFY latest: samples/cert/README.md
    cfg.Data.lumiMask = GOLDEN_LUMIMASK
    cfg.Data.publication = False
    cfg.Data.outputDatasetTag = tag

    if smoke:
        # Few lumis: small jobs + capped totalUnits. Full submit: unset totalUnits.
        cfg.Data.unitsPerJob = 5
        cfg.Data.totalUnits = 20
    else:
        cfg.Data.unitsPerJob = 50

    cfg.Site.storageSite = site
    return cfg


def build_mc_dy_config(
    *,
    smoke: bool = False,
    storage_site: str | None = None,
):
    """CRAB config for Summer24 DY MLL>50 MiniAODSIM.

    smoke=True → ``MC_DAS_DY_SMOKE`` (DYto2L PTLL-100, pipeline only).
    smoke=False → ``MC_DAS_DY`` (inclusive DYto2Mu MLL-50, first-C production).
    """
    tag = "DisplacedV0_DY_Summer24"
    out_file = f"{tag}.root"
    site = resolve_storage_site(storage_site)

    cfg = crab_config()
    cfg.General.requestName = f"{tag}_smoke" if smoke else tag
    cfg.General.workArea = "crab_DisplacedV0_mc"
    cfg.General.transferOutputs = True
    cfg.General.transferLogs = True

    cfg.JobType.pluginName = "Analysis"
    cfg.JobType.psetName = PSET_MC
    cfg.JobType.pyCfgParams = [f"outputFile={out_file}"]
    cfg.JobType.outputFiles = [out_file]

    if smoke:
        # Smoke-only PTLL-100 — not for first-C physics (phase-space mismatch).
        cfg.Data.inputDataset = MC_DAS_DY_SMOKE
        cfg.Data.unitsPerJob = 1
        cfg.Data.totalUnits = 2
    else:
        # Inclusive DYto2Mu — frozen production (no PTLL cut).
        cfg.Data.inputDataset = MC_DAS_DY
        cfg.Data.unitsPerJob = 2

    cfg.Data.inputDBS = "global"
    cfg.Data.splitting = "FileBased"
    cfg.Data.publication = False
    cfg.Data.outputDatasetTag = tag

    cfg.Site.storageSite = site
    return cfg
