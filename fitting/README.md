# Fitting (RooFit / ROOT TF1 path)

Sideband background subtraction for \(K_S^0\) (\(m_{\pi\pi}\)) per \(\Delta_{2D}\) bin
(AN-20-111 §7). **Keep upstream ROOT TF1 / fittools style** (M0 preference).

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`fitting/` @ `2a132385`.

| Script | Role |
| --- | --- |
| `fitinvmass.py` | Fill inv-mass histograms (optionally vs \(\Delta_{2D}\)); sideband poly + double-Gaussian |
| `count_peak.py` | Background-subtracted peak yield (`subtract` / `hybrid` / `gfit`) |
| `fitinvmass_fancy_*.py` | Legacy gallery / batch helpers |
| `variables/*.json` | Binning for `_mass`, `_RPV` (post-`v0building` laurelin schema) |

Depends on package-local `tools/fittools.py` and `plotting/plotfit.py`.

### Typical flow (after v0building)

```bash
python fitting/fitinvmass.py \
  -i selected_data.root -t laurelin \
  -v fitting/variables/variable_ks_invmass.json \
  --yvariable fitting/variables/variable_ks_rpv.json \
  -o out/ks_data --isdata --doplot --show_bkg_fit --polydegree 1

# Yields for C(Δ2D) are produced via analysis/mcvsdata_fill.py --bkgmode sideband --normmode range
```

Run3 label: \(13.6\,\mathrm{TeV}\). Weight default `_weight` (mapped from `genWeight` in v0building).
