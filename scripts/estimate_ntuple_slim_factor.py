#!/usr/bin/env python3
"""Estimate DisplacedV0 ntuple size factors (no CMSSW).

Builds synthetic ``displacedV0Ntuple/events`` trees with shared multiplicities:

* *fat* — pre–CDTE-30 (doubles + Lambda + unused muon/jet leaves)
* *slim14* — post–#14 / CDTE-30 (Ks-only floats + Jet_* arrays, all events)
* *slim31* — CDTE-31 (skip empty V0, jet scalars, deferred daughter leaves)
* *sol32* — Sol production after #15 (keep empty Z rows; restore daughter /
  pointing / provenance; compact jets; Dimuon_* scalars)

Usage:
  python3 scripts/estimate_ntuple_slim_factor.py
  python3 scripts/estimate_ntuple_slim_factor.py -n 2000 --out-dir /tmp/ntuple_slim
"""
from __future__ import annotations

import argparse
import os
import tempfile

import numpy as np


def _jagged(flat: np.ndarray, counts: np.ndarray):
  out = []
  i = 0
  for n in counts:
    out.append(flat[i : i + int(n)])
    i += int(n)
  return out


def _write_tree(path: str, arrays: dict) -> int:
  import uproot

  os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
  with uproot.recreate(path) as f:
    f["displacedV0Ntuple/events"] = arrays
  return os.path.getsize(path)


def build_arrays(n: int, schema: str, seed: int = 2024, empty_frac: float = 0.35):
  """schema in {fat, slim14, slim31, sol32}."""
  rng = np.random.default_rng(seed)
  run = np.full(n, 380000, dtype=np.uint32)
  lumi = np.arange(1, n + 1, dtype=np.uint32)
  event = np.arange(1, n + 1, dtype=np.uint64)
  nPV = rng.integers(15, 45, size=n).astype(np.int32)
  genWeight = np.ones(n, dtype=np.float32)
  genWeight[::11] = -1.0
  Pileup_nTrue = rng.uniform(20, 55, size=n).astype(np.float32)
  passDimuonHLT = np.ones(n, dtype=bool)
  hlt = np.ones(n, dtype=bool)

  nMuon = np.full(n, 2, dtype=np.uint32)
  Muon_pt = rng.uniform(25, 60, size=(n, 2))
  Muon_eta = rng.uniform(-2.4, 2.4, size=(n, 2))
  Muon_phi = rng.uniform(-np.pi, np.pi, size=(n, 2))
  Muon_mass = np.full((n, 2), 0.105658)
  Muon_charge = np.column_stack([np.ones(n), -np.ones(n)]).astype(np.int32)
  Muon_mediumId = np.ones((n, 2), dtype=bool)
  Dimuon_mass = rng.normal(91.2, 2.5, size=n)
  Dimuon_pt = rng.uniform(5, 80, size=n)
  Dimuon_y = rng.uniform(-2.4, 2.4, size=n)

  nJet = np.full(n, 8, dtype=np.uint32)
  Jet_pt = rng.uniform(15, 120, size=(n, 8))
  Jet_eta = rng.uniform(-4.5, 4.5, size=(n, 8))
  Jet_btag = rng.uniform(0, 0.2, size=(n, 8))
  Jet_jetId = np.full((n, 8), 6, dtype=np.int32)
  # Selected-jet count matching JetAnalyzer (pT>30, |η|<2.5)
  nJetSel = np.sum((Jet_pt > 30.0) & (np.abs(Jet_eta) < 2.5), axis=1).astype(np.uint32)
  nJetSelStatus = (nJetSel > 0).astype(np.uint8)
  maxDeepJet = np.where(nJetSel > 0, Jet_btag.max(axis=1), -1.0)
  passDeepJetLooseVeto = np.ones(n, dtype=bool)

  # Shared V0 multiplicities: empty_frac zeros, else 1–5 (Codex P2 alignment)
  nV0_raw = rng.integers(1, 6, size=n).astype(np.uint32)
  empty = rng.random(n) < empty_frac
  nV0_raw[empty] = 0

  if schema == "fat":
    nV0 = rng.integers(2, 9, size=n).astype(np.uint32)
  elif schema == "slim31":
    keep = nV0_raw > 0
    run, lumi, event = run[keep], lumi[keep], event[keep]
    nPV, genWeight, Pileup_nTrue = nPV[keep], genWeight[keep], Pileup_nTrue[keep]
    passDimuonHLT, hlt = passDimuonHLT[keep], hlt[keep]
    nMuon = nMuon[keep]
    Muon_pt, Muon_eta, Muon_phi = Muon_pt[keep], Muon_eta[keep], Muon_phi[keep]
    Muon_mass, Muon_charge = Muon_mass[keep], Muon_charge[keep]
    Muon_mediumId = Muon_mediumId[keep]
    Dimuon_mass, Dimuon_pt, Dimuon_y = Dimuon_mass[keep], Dimuon_pt[keep], Dimuon_y[keep]
    nJet, Jet_pt, Jet_eta = nJet[keep], Jet_pt[keep], Jet_eta[keep]
    Jet_btag, Jet_jetId = Jet_btag[keep], Jet_jetId[keep]
    nJetSel, nJetSelStatus = nJetSel[keep], nJetSelStatus[keep]
    maxDeepJet, passDeepJetLooseVeto = maxDeepJet[keep], passDeepJetLooseVeto[keep]
    nV0 = nV0_raw[keep]
    n = int(keep.sum())
  else:
    # slim14 + sol32: keep all Z rows (including empty V0)
    nV0 = nV0_raw if schema in ("slim14", "sol32") else nV0_raw

  total = int(nV0.sum())
  v0type = np.ones(total, dtype=np.uint32)
  if schema == "fat":
    lam = rng.random(total) < 0.3
    v0type[lam] = rng.choice([2, 3], size=int(lam.sum()))

  use_f32 = schema != "fat"

  def cast(a):
    return np.asarray(a, dtype=np.float32 if use_f32 else np.float64)

  arrays = {
    "run": run,
    "luminosityBlock": lumi,
    "event": event,
    "nPV": nPV,
    "genWeight": genWeight,
    "Pileup_nTrue": Pileup_nTrue,
    "passDimuonHLT": passDimuonHLT,
    "nMuon": nMuon,
    "Muon_pt": cast(Muon_pt),
    "Muon_eta": cast(Muon_eta),
    "Muon_phi": cast(Muon_phi),
    "Muon_charge": Muon_charge,
    "Muon_mediumId": Muon_mediumId,
    "_nV0s": nV0,
    "_beamSpotX": cast(np.zeros(n)),
    "_beamSpotY": cast(np.zeros(n)),
    "_beamSpotZ": cast(np.zeros(n)),
    "_primaryVertexX": cast(np.zeros(n)),
    "_primaryVertexY": cast(np.zeros(n)),
    "_primaryVertexZ": cast(np.zeros(n)),
  }

  if schema == "fat" or schema == "slim14":
    arrays["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"] = hlt
    arrays["Muon_mass"] = cast(Muon_mass)
    arrays["nJet"] = nJet
    arrays["Jet_pt"] = cast(Jet_pt)
    arrays["Jet_eta"] = cast(Jet_eta)
    arrays["Jet_btagDeepFlavB"] = cast(Jet_btag)
    arrays["Jet_jetId"] = Jet_jetId
  else:
    # slim31 / sol32: compact jet scalars
    arrays["nJetSel"] = nJetSel
    arrays["passDeepJetLooseVeto"] = passDeepJetLooseVeto
    if schema == "sol32":
      arrays["Dimuon_mass"] = cast(Dimuon_mass)
      arrays["Dimuon_pt"] = cast(Dimuon_pt)
      arrays["Dimuon_y"] = cast(Dimuon_y)
      arrays["maxDeepJet"] = cast(maxDeepJet)
      arrays["nJetSelStatus"] = nJetSelStatus

  if schema == "fat":
    arrays["Muon_looseId"] = np.ones((n, 2), dtype=bool)
    arrays["Muon_tightId"] = np.zeros((n, 2), dtype=bool)
    arrays["Muon_isPF"] = np.ones((n, 2), dtype=bool)
    arrays["Muon_isGlobal"] = np.ones((n, 2), dtype=bool)
    arrays["Muon_isTracker"] = np.ones((n, 2), dtype=bool)
    arrays["Muon_dxy"] = cast(rng.normal(0, 0.01, size=(n, 2)))
    arrays["Muon_dz"] = cast(rng.normal(0, 0.05, size=(n, 2)))
    arrays["Muon_sip3d"] = cast(rng.uniform(0, 5, size=(n, 2)))
    arrays["Muon_pfRelIso04_all"] = cast(rng.uniform(0, 0.3, size=(n, 2)))
    arrays["Jet_phi"] = cast(rng.uniform(-np.pi, np.pi, size=(n, 8)))
    arrays["Jet_mass"] = cast(rng.uniform(5, 40, size=(n, 8)))
    arrays["Jet_hadronFlavour"] = rng.integers(0, 5, size=(n, 8)).astype(np.int32)
    arrays["_primaryVertexXUnc"] = cast(np.full(n, 0.001))
    arrays["_primaryVertexYUnc"] = cast(np.full(n, 0.001))
    arrays["_primaryVertexZUnc"] = cast(np.full(n, 0.01))

  # Core V0 branches (all schemas)
  kept = {
    "_V0Type": v0type,
    "_V0InvMass": rng.normal(0.498, 0.01, size=total),
    "_V0X": rng.uniform(-20, 20, size=total),
    "_V0Y": rng.uniform(-20, 20, size=total),
    "_V0Z": rng.uniform(-50, 50, size=total),
    "_V0RPV": rng.uniform(0.2, 40, size=total),
    "_V0RPVSig": rng.uniform(2, 80, size=total),
    "_V0Px": rng.uniform(-5, 5, size=total),
    "_V0Py": rng.uniform(-5, 5, size=total),
    "_V0Pt": rng.uniform(1, 10, size=total),
    "_V0DCA": rng.uniform(0, 0.5, size=total),
    "_V0VtxNormChi2": rng.uniform(0.5, 10, size=total),
    "_V0PtPos": rng.uniform(1, 6, size=total),
    "_V0PtNeg": rng.uniform(1, 6, size=total),
    "_V0NHitsPos": rng.integers(6, 25, size=total).astype(np.float64),
    "_V0NHitsNeg": rng.integers(6, 25, size=total).astype(np.float64),
    "_V0NormChi2Pos": rng.uniform(0.5, 5, size=total),
    "_V0NormChi2Neg": rng.uniform(0.5, 5, size=total),
  }
  if schema != "slim31":
    kept.update(
      {
        "_V0Eta": rng.uniform(-2.5, 2.5, size=total),
        "_V0Phi": rng.uniform(-np.pi, np.pi, size=total),
        "_V0EtaPos": rng.uniform(-2.5, 2.5, size=total),
        "_V0EtaNeg": rng.uniform(-2.5, 2.5, size=total),
        "_V0PhiPos": rng.uniform(-np.pi, np.pi, size=total),
        "_V0PhiNeg": rng.uniform(-np.pi, np.pi, size=total),
        "_V0D0Pos": rng.uniform(0.01, 1, size=total),
        "_V0DzPos": rng.uniform(-2, 2, size=total),
        "_V0D0Neg": rng.uniform(0.01, 1, size=total),
        "_V0DzNeg": rng.uniform(-2, 2, size=total),
      }
    )
  if schema in ("fat", "slim14"):
    kept.update(
      {
        "_V0RBS": rng.uniform(0.2, 40, size=total),
        "_V0RBSSig": rng.uniform(2, 80, size=total),
      }
    )
  if schema == "sol32":
    kept.update(
      {
        "_V0CosPointingPV": np.ones(total),
        "_V0CosPointingBS": np.ones(total),
        "_V0NearestChgDRPos": np.full(total, np.nan),
        "_V0NearestChgDRNeg": np.full(total, np.nan),
      }
    )
  for k, v in kept.items():
    arrays[k] = _jagged(cast(v) if k != "_V0Type" else v, nV0)

  if schema == "sol32" and total > 0:
    arrays["_V0SrcPos"] = _jagged(rng.integers(0, 2, size=total).astype(np.uint8), nV0)
    arrays["_V0SrcNeg"] = _jagged(rng.integers(0, 2, size=total).astype(np.uint8), nV0)
    arrays["_V0IdxPos"] = _jagged(rng.integers(0, 200, size=total).astype(np.int32), nV0)
    arrays["_V0IdxNeg"] = _jagged(rng.integers(0, 200, size=total).astype(np.int32), nV0)
    arrays["_V0NearestChgStatusPos"] = _jagged(np.zeros(total, dtype=np.uint8), nV0)
    arrays["_V0NearestChgStatusNeg"] = _jagged(np.zeros(total, dtype=np.uint8), nV0)
    arrays["_V0NChgDR01Pos"] = _jagged(np.full(total, -1, dtype=np.int32), nV0)
    arrays["_V0NChgDR01Neg"] = _jagged(np.full(total, -1, dtype=np.int32), nV0)

  if schema == "fat":
    dropped = {
      "_V0XUnc": rng.uniform(0.01, 0.1, size=total),
      "_V0YUnc": rng.uniform(0.01, 0.1, size=total),
      "_V0ZUnc": rng.uniform(0.01, 0.2, size=total),
      "_V0RPVUnc": rng.uniform(0.01, 0.2, size=total),
      "_V0RBSUnc": rng.uniform(0.01, 0.2, size=total),
      "_V0Pz": rng.uniform(-5, 5, size=total),
      "_V0PCAX": rng.uniform(-20, 20, size=total),
      "_V0PCAY": rng.uniform(-20, 20, size=total),
      "_V0PCAZ": rng.uniform(-50, 50, size=total),
      "_V0PxPos": rng.uniform(-5, 5, size=total),
      "_V0PyPos": rng.uniform(-5, 5, size=total),
      "_V0PzPos": rng.uniform(-5, 5, size=total),
      "_V0PxNeg": rng.uniform(-5, 5, size=total),
      "_V0PyNeg": rng.uniform(-5, 5, size=total),
      "_V0PzNeg": rng.uniform(-5, 5, size=total),
      "_V0IsoPos": rng.uniform(0, 2, size=total),
      "_V0IsoNeg": rng.uniform(0, 2, size=total),
    }
    for k, v in dropped.items():
      arrays[k] = _jagged(cast(v), nV0)

  return arrays, n, total, float(nV0.mean()) if n else 0.0


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("-n", "--nevents", type=int, default=2000)
  parser.add_argument("--out-dir", default="")
  parser.add_argument("--seed", type=int, default=2024)
  parser.add_argument(
    "--empty-frac",
    type=float,
    default=0.35,
    help="Fraction of events with _nV0s==0 (shared for slim14/slim31/sol32)",
  )
  args = parser.parse_args()

  try:
    import uproot  # noqa: F401
  except ImportError as exc:
    raise SystemExit("uproot required") from exc

  out_dir = args.out_dir or tempfile.mkdtemp(prefix="ntuple_slim_")
  paths = {}
  stats = {}
  schemas = ("fat", "slim14", "slim31", "sol32")
  for schema in schemas:
    arr, n_kept, nv0, mean = build_arrays(
      args.nevents, schema, seed=args.seed, empty_frac=args.empty_frac
    )
    path = os.path.join(out_dir, f"{schema}_schema.root")
    nbytes = _write_tree(path, arr)
    paths[schema] = path
    stats[schema] = (nbytes, n_kept, nv0, mean)

  fat_b, _, _, _ = stats["fat"]
  s14_b, _, _, _ = stats["slim14"]
  s31_b, n31, _, _ = stats["slim31"]
  sol_b, nsol, _, _ = stats["sol32"]

  print(f"input events (before skipFill): {args.nevents}")
  for schema in schemas:
    nbytes, n_kept, nv0, mean = stats[schema]
    print(f"{schema}: {paths[schema]}")
    print(
      f"      size={nbytes/1e6:.3f} MB  events_written={n_kept}  "
      f"nV0={nv0}  mean_nV0={mean:.2f}"
    )
  print(f"size factor fat/slim14 (#14):        {fat_b / s14_b:.2f}x")
  print(f"size factor slim14/slim31 (CDTE-31): {s14_b / s31_b:.2f}x")
  print(f"size factor slim31/sol32 (Sol):      {s31_b / sol_b:.2f}x  "
        f"(sol keeps empty Z rows → usually >1 if comparing file sizes)")
  print(f"size factor slim14/sol32:            {s14_b / sol_b:.2f}x")
  print(f"bytes/event slim31: {s31_b / max(n31,1):.0f}  "
        f"sol32: {sol_b / max(nsol,1):.0f}  "
        f"(sol32/slim31 per-event ≈ {(sol_b/max(nsol,1))/(s31_b/max(n31,1)):.2f}x)")
  print(
    f"Note: slim31 drops empty_frac={args.empty_frac} events; sol32 keeps them. "
    "Shared V0 multiplicities for slim14/slim31/sol32. Synthetic (2μ, 8 jets). "
    "Resubmit full CRAB after merge — do not delete existing EOS output."
  )


if __name__ == "__main__":
  main()
