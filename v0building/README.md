# V0 building / AN cut selection (offline)

Preferred path: build V0 candidates in CMSSW (`DisplacedV0` / `V0Analyzer`).
The Kalman fitter stores a **superset** of candidates; AN-20-111 §6 tight cuts
live in `v0selections.py` (`selection_legacy`: hits≥6, daughter \(p_T>1\),
track \(\chi^2/\mathrm{ndof}<5\), DCA < 0.2, vtx \(\chi^2<7\),
\(\cos\theta_{\mathrm{pointing}}>0.99\)).

Ported from [LukaLambrecht/K0sAnalysis](https://github.com/LukaLambrecht/K0sAnalysis)
`v0building/` @ `2a132385`, **adapted for DisplacedV0 Run3 ntuples**.

### Input (DisplacedV0 `displacedV0Ntuple/events` tree)

First-C slim schema (`storeKsOnly=True`, `skipFillIfNoV0=True`, float leaves):

| Branch | Use |
| --- | --- |
| `_V0InvMass`, `_V0Type`, `_V0RPV` (+Sig), `_V0X/Y/Z`, `_V0Px/Py`, `_V0Pt`, `_V0DCA`, `_V0VtxNormChi2`, daughter pt/hits/χ² | Ks kinematics + AN §6 + C(Δ2D) |
| `_beamSpot*`, `_primaryVertexX/Y/Z` | cosθ_pointing |
| `passDimuonHLT` | Dimuon HLT OR |
| `Muon_pt/eta/phi/charge/mediumId` | DY tag / celeborn (`Muon_mass` optional / PDG offline) |
| `passDeepJetLooseVeto`, `nJetSel` | DeepJet b-veto + nJets (Jet_* arrays dropped) |
| `genWeight`, `Pileup_nTrue` | MC weights / PU (→ `_weight`, `_nTrueInt`) |
| `run`, `luminosityBlock`, `event` | Event ID |

**Sol production (post-#15):** empty-V0 Z rows kept (`skipFillIfNoV0=False`);
daughter η/φ + dxy/dz + packed/lost provenance restored; pointing cosines
stored; neighbour charged-ΔR stubs status=0. Still omit Λ/Λ̄ rows when
`storeKsOnly`; no full `Jet_*` / unused fat leaves. Legacy ntuples without
restored leaves still work (η/φ/`_trackdR`/IPs → NaN hooks).
(until trackingEff); unc/PCA/Iso/PxPyPz; unused muon leaves; `Muon_mass`;
per-path `HLT_*`; `Jet_*` / `nJet` arrays.

Pre–CDTE-31 ntuples with `Jet_*` / `_V0RBS` / daughter ηφ still work
(`v0builder` falls back).

### Output (analysis schema)

`nimloth` / `celeborn` / `laurelin` / `telperion` with `_RPV`, `_mass`, `_weight`, …
(`telperion` is empty when the ntuple was produced with `storeKsOnly=True`.)

**Tracking nuisances (CDTE-26 / Sol):** when DisplacedV0 still has
`_V0D0*`/`_V0Dz*` and daughter η/φ, laurelin keeps `_d0*`/`_dz*` and
`_trackdR`; otherwise those are omitted / NaN. Nearest charged-track distance
in the matched jet is **not** computed yet (`_trkNearestJetDistPos/Neg` are
NaN schema hooks).

### Usage

```bash
# Single ROOT file (unchanged)
python3 v0builder.py -i displacedv0_ntuple.root -o selected.root \
  --apply-dy-selection --selection legacy
# DeepJet WP only matters for legacy Jet_* ntuples; CDTE-31 uses the scalar:
#   --deepjet-loose-wp 0.0494   or  --no-bveto

# Text filelist (one EOS/local .root path per line) — no hadd of CRAB shards
python3 v0builder.py -i dy_crab_files.txt -o v0sel_dy.root \
  --apply-dy-selection --no-bveto

# Multiple files and/or globs
python3 v0builder.py -i file1.root file2.root 'dir/*.root' -o selected.root
```

`-i` accepts a single ROOT file, a text filelist (`#` comments / blank lines
skipped), multiple paths, and shell globs. Events are read with
`uproot.concatenate` (TChain-like) so inputs are not merged on disk.

Upstream `blackJackAndHookers` layout is still accepted as a fallback.
Merge helpers (`merge.py`, `mergeeras.py`, …) are ported as-is.
