# CRAB / local tests

**Full local smoke path (setup, package placement, MagField notes, branch checklist):**  
[`/cursor/stores/self/docs/cmsrun-smoke-test.md`](/cursor/stores/self/docs/cmsrun-smoke-test.md)

| File | Role |
| --- | --- |
| `../python/test_data_onefile_cfg.py` | Local cmsRun data smoke (`VarParsing` `inputFiles` / `maxEvents`) |
| `../python/test_mc_onefile_cfg.py` | Local cmsRun MC smoke |
| `crab_data_2024.py` | CRAB data (placeholder dataset) |
| `crab_mc_dy.py` | CRAB DY MC (placeholder dataset) |

### Quick start (on a CMSSW host)

```bash
# after cmsrel / cmsenv and linking DisplacedV0 into $CMSSW_BASE/src/
scram b -j8
cmsRun DisplacedV0/python/test_data_onefile_cfg.py \
  inputFiles=file:/path/to/miniaod.root maxEvents=200
cmsRun DisplacedV0/python/test_mc_onefile_cfg.py \
  inputFiles=file:/path/to/miniaodsim.root maxEvents=200
```

Import is `from DisplacedV0.displacedV0_cfi import ...` (CMSSW strips `python/`).

**This Project VM has no CMSSW** — run the steps on lxplus/CMSLPC; see the smoke-test doc.

### M3 exit criterion

Trees with HLT bits, muons, DeepJet jets, V0s, and a \(K_S\) mass peak near
0.498 GeV (`_V0Type==1`, `_V0InvMass`). V0 + Trigger/Lepton/Jet bodies are ported;
needs `cmsRun` on a CMSSW machine.
