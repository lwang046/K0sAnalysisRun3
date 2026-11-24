# CRAB / local tests

**Full local smoke path (setup, package placement, MagField notes, branch checklist):**  
[`docs/cmsrun-smoke-test.md`](../../../docs/cmsrun-smoke-test.md)

**First \(C(\Delta_{2D})\) submit recipe §3:**  
[`docs/first-c-delta2d-recipe.md`](../../../docs/first-c-delta2d-recipe.md)

| File | Role |
| --- | --- |
| `../python/test_data_onefile_cfg.py` | Local cmsRun data smoke only (`VarParsing` `inputFiles` / `maxEvents`) |
| `../python/test_mc_onefile_cfg.py` | Local cmsRun MC smoke only |
| `../python/displacedV0_data_cfg.py` | **Production** data pset for CRAB (wraps same sequence) |
| `../python/displacedV0_mc_cfg.py` | **Production** MC pset for CRAB |
| `crab_common.py` | Shared builders + DAS / golden / `storageSite` PLACEHOLDER |
| `crab_data_2024.py` | Full Run2024D **Muon0** |
| `crab_data_2024_muon1.py` | Full Run2024D **Muon1** twin |
| `crab_data_2024_smoke.py` | Muon0 smoke (few lumis: `unitsPerJob=5`, `totalUnits=20`) |
| `crab_mc_dy.py` | Full Summer24 DY |
| `crab_mc_dy_smoke.py` | DY smoke (few files: `unitsPerJob=1`, `totalUnits=2`) |

### Naming (aligned with recipe / v0building)

| Submit | `requestName` / `outputDatasetTag` | Job output file |
| --- | --- | --- |
| Muon0 | `DisplacedV0_Muon0_Run2024D` | `DisplacedV0_Muon0_Run2024D.root` |
| Muon1 | `DisplacedV0_Muon1_Run2024D` | `DisplacedV0_Muon1_Run2024D.root` |
| DY | `DisplacedV0_DY_Summer24` | `DisplacedV0_DY_Summer24.root` |

Smoke requests append `_smoke` to `requestName` only.

### storageSite (lxplus — required)

Configs default to **`T2_XX_PLACEHOLDER`**. Do **not** invent a T2 in git. On lxplus:

```bash
export CRAB_STORAGE_SITE=T2_CH_CERN   # replace with *your* writeable site
# optional: also set outLFNDirBase in crab_common if your site requires it
```

### TODO-VERIFY before any submit

| Item | Where |
| --- | --- |
| Data DAS (`/Muon{0,1}/Run2024D-…`) | `samples/data_muon_2024.txt`, `conditions.md` |
| MC DAS (FxFx Summer24) | `samples/sim_dy_m50_13p6.txt`, `conditions.md` |
| Golden `lumiMask` | `samples/cert/README.md` |
| `CRAB_STORAGE_SITE` | env on lxplus (see above) |

### Quick start (on a CMSSW + CRAB host)

```bash
# after cmsrel / cmsenv and linking DisplacedV0 into $CMSSW_BASE/src/
scram b -j8

# Local one-file smoke (not CRAB):
cmsRun DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:/path/to/miniaod.root maxEvents=200
cmsRun DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:/path/to/miniaodsim.root maxEvents=200

# CRAB smoke → full (set CRAB_STORAGE_SITE first):
crab submit -c DisplacedV0/test/crab_data_2024_smoke.py
crab submit -c DisplacedV0/test/crab_mc_dy_smoke.py
# then:
crab submit -c DisplacedV0/test/crab_data_2024.py
crab submit -c DisplacedV0/test/crab_data_2024_muon1.py
crab submit -c DisplacedV0/test/crab_mc_dy.py
```

Import is `from DisplacedV0.displacedV0_cfi import ...` (CMSSW strips `python/`).

**This Project VM has no CMSSW / CRAB** — configs are prep-only; run submits on lxplus/CMSLPC.

### M3 / M4 exit criteria

- **M3:** Trees with HLT bits, muons, DeepJet jets, V0s, and a \(K_S\) mass peak near 0.498 GeV (`_V0Type==1`, `_V0InvMass`) from local `cmsRun`.
- **M4:** CRAB smoke then full ntuples for Run2024D Muon0+Muon1 + DY on EOS/T2.
