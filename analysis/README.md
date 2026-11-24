# Analysis — \(C(\Delta_{2D})\)

Fill data/MC V0 yields vs `rpv` / \(\Delta_{2D}\), **sideband-subtract**,
**normalize at low \(\Delta_{2D}\)**, form \(C\).

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`analysis/` @ `2a132385`, adapted for Run3 / DisplacedV0 → v0building trees.

| File | Role |
| --- | --- |
| `config_defaults_run3.py` | Shared bins, `normrange`, HLT, DeepJet WP, first era |
| `config_ksvars.py` | 1D \(\Delta_{2D}\) bins (method §2.6) + sideband + `normrange` |
| `config_ks2dvars.py` | 2D \(C(\Delta_{2D},p_T)\) |
| `config_controlvars.py` | DY controls (`_nimloth_Mll`, muon \(p_T/\eta\)) |
| `config_lavars.py` | \(\Lambda\) diagnostic |
| `example_input_run2024d.json` | Template `datain`/`mcin` for `mcvsdata_fill.py` |
| `mcvsdata_fill.py` | Core fill: sideband → yields → low-\(\Delta_{2D}\) scale |
| `mcvsdata_submit*.py` | Condor/local batch |

Ordered first-era commands: [`docs/first-c-delta2d-recipe.md`](../docs/first-c-delta2d-recipe.md).

### Branch schema (post-v0building)

| Tree | Key branches |
| --- | --- |
| `laurelin` | `_RPV`, `_mass`, `_pt`, `_weight`, `_nTrueInt`, `_d0Pos/Neg`, `_dzPos/Neg`, `_trackdR` |
| `nimloth` | `_nimloth_Mll`, `_nimloth_nJets`, … |
| `celeborn` | `_celeborn_lPt`, `_celeborn_lEta`, … |

`_weight` / `_nTrueInt` are mapped from DisplacedV0 `genWeight` / `Pileup_nTrue`.
Daughter IPs (`_d0*`/`_dz*`) come from DisplacedV0 `_V0D0*`/`_V0Dz*` (CDTE-26).
`_trkNearestJetDistPos/Neg` are NaN schema hooks until jet↔V0 matching exists.

Default: `--nopileup` until Collisions24 PU profiles are under `reweighting/pileup/`.
Use `--normmode range` with `fitting/variables/variable_norm_rpv.json` (or config `normrange`) for AN low-\(\Delta_{2D}\) normalization.
Shared scale + correlated envelope: output `norm_scale`, `norm_shared_up/down`.
Stability knob: `--norm-stability-uppers 1.0,3.0`. Peak window: `--peak-halfwidth-frac 0.25`.

