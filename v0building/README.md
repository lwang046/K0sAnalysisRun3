# V0 building / AN cut selection (offline)

Preferred path: build V0 candidates in CMSSW (`DisplacedV0` / `V0Analyzer`).
The Kalman fitter stores a **superset** of candidates; AN-20-111 §6 tight cuts
live in `v0selections.py` (`selection_legacy`: hits≥6, daughter \(p_T>1\),
track \(\chi^2/\mathrm{ndof}<5\), DCA < 0.2, vtx \(\chi^2<7\),
\(\cos\theta_{\mathrm{pointing}}>0.99\)).

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`v0building/` @ `2a132385`, **adapted for DisplacedV0 Run3 ntuples**.

### Input (DisplacedV0 `displacedV0Ntuple/events` tree)

First-C slim schema (`storeKsOnly=True`, float leaves). Kept vs dropped:

| Branch | Use |
| --- | --- |
| `_V0InvMass`, `_V0Type`, `_V0RPV`/`_V0RBS` (+Sig), `_V0X/Y/Z`, `_V0Px/Py`, `_V0Pt/Eta/Phi`, `_V0DCA`, `_V0VtxNormChi2`, daughter pt/η/φ/hits/χ²/`_V0D0*`/`_V0Dz*` | Ks kinematics + AN §6 |
| `_beamSpot*`, `_primaryVertexX/Y/Z` | cosθ_pointing |
| `passDimuonHLT` | Dimuon HLT OR |
| `Muon_pt/eta/phi/charge/mediumId` (+ optional `Muon_mass`) | DY tag / celeborn |
| `Jet_pt/eta`, `Jet_btagDeepFlavB`, `Jet_jetId` | DeepJet b-veto + nJets |
| `genWeight`, `Pileup_nTrue` | MC weights / PU (→ `_weight`, `_nTrueInt`) |
| `run`, `luminosityBlock`, `event` | Event ID |

**Dropped at source (unused by this path):** Λ/Λ̄ rows, `_V0*Unc`, `_V0PCA*`,
`_V0Pz`, daughter Cartesian `_V0P{x,y,z}{Pos,Neg}`, `_V0Iso*`, PV unc,
`Muon_{loose,tight}Id` / isPF/Global/Tracker / dxy/dz/sip3d / pfRelIso,
`Jet_phi` / `Jet_mass` / `Jet_hadronFlavour`.

### Output (analysis schema)

`nimloth` / `celeborn` / `laurelin` / `telperion` with `_RPV`, `_mass`, `_weight`, …
(`telperion` is empty when the ntuple was produced with `storeKsOnly=True`.)

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
