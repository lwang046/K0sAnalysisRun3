# V0 building / AN cut selection (offline)

Preferred path: build V0 candidates in CMSSW (`DisplacedV0` / `V0Analyzer`).
The Kalman fitter stores a **superset** of candidates; AN-20-111 §6 tight cuts
live in `v0selections.py` (`selection_legacy`: hits≥6, daughter \(p_T>1\),
track \(\chi^2/\mathrm{ndof}<5\), DCA < 0.2, vtx \(\chi^2<7\),
\(\cos\theta_{\mathrm{pointing}}>0.99\)).

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`v0building/` @ `2a132385`, **adapted for DisplacedV0 Run3 ntuples**.

### Input (DisplacedV0 `displacedV0Ntuple/events` tree)

| Branch | Use |
| --- | --- |
| `_V0*` | Kalman V0 candidates (same names as upstream V0Analyzer) |
| `passDimuonHLT` | Dimuon HLT OR |
| `Muon_*` | DY tag (medium ID, \(p_T\), charge) |
| `Jet_btagDeepFlavB` | Loose DeepJet \(b\)-veto |
| `genWeight`, `Pileup_nTrue` | MC weights / PU (→ `_weight`, `_nTrueInt` in output) |
| `run`, `luminosityBlock`, `event` | Event ID |

### Output (analysis schema)

`nimloth` / `celeborn` / `laurelin` / `telperion` with `_RPV`, `_mass`, `_weight`, …

**Tracking nuisances (CDTE-26 / Sol):** laurelin/telperion keep each daughter's
impact parameters (`_d0Pos`, `_dzPos`, `_d0Neg`, `_dzNeg` from DisplacedV0
`_V0D0*` / `_V0Dz*`) and daughter–daughter `_trackdR`. Nearest charged-track
distance in the matched jet is **not** computed yet (`_trkNearestJetDistPos/Neg`
are NaN schema hooks — needs jet↔V0 matching upstream; do not invent values).

### Usage

```bash
python3 v0builder.py -i displacedv0_ntuple.root -o selected.root \
  --apply-dy-selection --selection legacy
# DeepJet WP is a placeholder until BTV 2024 JSON is frozen:
#   --deepjet-loose-wp 0.0494   or  --no-bveto
```

Upstream `blackJackAndHookers` layout is still accepted as a fallback.
Merge helpers (`merge.py`, `mergeeras.py`, …) are ported as-is.
