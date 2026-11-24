#!/usr/bin/env python3
"""Estimate DisplacedV0 fat→slim ROOT size factor (no CMSSW).

Builds two synthetic ``displacedV0Ntuple/events`` trees with the same event /
object multiplicities: a *fat* schema (pre–CDTE-30 doubles + Lambda + unused
muon/jet leaves) and the *slim* first-C schema (Ks-only floats + kept branches).

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


def build_arrays(n: int, slim: bool, seed: int = 2024):
  rng = np.random.default_rng(seed)
  run = np.full(n, 380000, dtype=np.uint32)
  lumi = np.arange(1, n + 1, dtype=np.uint32)
  event = np.arange(1, n + 1, dtype=np.uint64)
  nPV = rng.integers(15, 45, size=n).astype(np.int32)
  genWeight = np.ones(n, dtype=np.float32)
  Pileup_nTrue = rng.uniform(20, 55, size=n).astype(np.float32)
  passDimuonHLT = np.ones(n, dtype=bool)
  hlt = np.ones(n, dtype=bool)

  # ~2 stored muons after preselection (DY-like)
  nMuon = np.full(n, 2, dtype=np.uint32)
  Muon_pt = rng.uniform(25, 60, size=(n, 2))
  Muon_eta = rng.uniform(-2.4, 2.4, size=(n, 2))
  Muon_phi = rng.uniform(-np.pi, np.pi, size=(n, 2))
  Muon_mass = np.full((n, 2), 0.105658)
  Muon_charge = np.column_stack([np.ones(n), -np.ones(n)]).astype(np.int32)
  Muon_mediumId = np.ones((n, 2), dtype=bool)

  # ~8 jets above soft cut
  nJet = np.full(n, 8, dtype=np.uint32)
  Jet_pt = rng.uniform(15, 120, size=(n, 8))
  Jet_eta = rng.uniform(-4.5, 4.5, size=(n, 8))
  Jet_btag = rng.uniform(0, 0.2, size=(n, 8))
  Jet_jetId = np.full((n, 8), 6, dtype=np.int32)

  # Fat: mix of Ks + Lambda; slim: Ks only. Typical ~30% Lambda-like fraction.
  if slim:
    nV0 = rng.integers(1, 6, size=n).astype(np.uint32)  # Ks-only mean ~3
  else:
    nV0 = rng.integers(2, 9, size=n).astype(np.uint32)  # fat mean ~5
  total = int(nV0.sum())
  v0type = np.ones(total, dtype=np.uint32)
  if not slim:
    # ~30% Lambda / LambdaBar
    lam = rng.random(total) < 0.3
    v0type[lam] = rng.choice([2, 3], size=int(lam.sum()))

  def f64(a):
    return np.asarray(a, dtype=np.float64)

  def f32(a):
    return np.asarray(a, dtype=np.float32)

  cast = f32 if slim else f64

  arrays = {
    "run": run,
    "luminosityBlock": lumi,
    "event": event,
    "nPV": nPV,
    "genWeight": genWeight,
    "Pileup_nTrue": Pileup_nTrue,
    "passDimuonHLT": passDimuonHLT,
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8": hlt,
    "nMuon": nMuon,
    "Muon_pt": cast(Muon_pt),
    "Muon_eta": cast(Muon_eta),
    "Muon_phi": cast(Muon_phi),
    "Muon_mass": cast(Muon_mass),
    "Muon_charge": Muon_charge,
    "Muon_mediumId": Muon_mediumId,
    "nJet": nJet,
    "Jet_pt": cast(Jet_pt),
    "Jet_eta": cast(Jet_eta),
    "Jet_btagDeepFlavB": cast(Jet_btag),
    "Jet_jetId": Jet_jetId,
    "_nV0s": nV0,
    "_beamSpotX": cast(np.zeros(n)),
    "_beamSpotY": cast(np.zeros(n)),
    "_beamSpotZ": cast(np.zeros(n)),
    "_primaryVertexX": cast(np.zeros(n)),
    "_primaryVertexY": cast(np.zeros(n)),
    "_primaryVertexZ": cast(np.zeros(n)),
  }

  if not slim:
    # Unused muon / jet leaves present in pre-slim ntuple
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

  # Shared kept V0 branches
  kept = {
    "_V0Type": v0type,
    "_V0InvMass": rng.normal(0.498, 0.01, size=total),
    "_V0X": rng.uniform(-20, 20, size=total),
    "_V0Y": rng.uniform(-20, 20, size=total),
    "_V0Z": rng.uniform(-50, 50, size=total),
    "_V0RPV": rng.uniform(0.2, 40, size=total),
    "_V0RBS": rng.uniform(0.2, 40, size=total),
    "_V0RPVSig": rng.uniform(2, 80, size=total),
    "_V0RBSSig": rng.uniform(2, 80, size=total),
    "_V0Px": rng.uniform(-5, 5, size=total),
    "_V0Py": rng.uniform(-5, 5, size=total),
    "_V0Pt": rng.uniform(1, 10, size=total),
    "_V0Eta": rng.uniform(-2.5, 2.5, size=total),
    "_V0Phi": rng.uniform(-np.pi, np.pi, size=total),
    "_V0DCA": rng.uniform(0, 0.5, size=total),
    "_V0VtxNormChi2": rng.uniform(0.5, 10, size=total),
    "_V0PtPos": rng.uniform(1, 6, size=total),
    "_V0PtNeg": rng.uniform(1, 6, size=total),
    "_V0EtaPos": rng.uniform(-2.5, 2.5, size=total),
    "_V0EtaNeg": rng.uniform(-2.5, 2.5, size=total),
    "_V0PhiPos": rng.uniform(-np.pi, np.pi, size=total),
    "_V0PhiNeg": rng.uniform(-np.pi, np.pi, size=total),
    "_V0NHitsPos": rng.integers(6, 25, size=total).astype(np.float64),
    "_V0NHitsNeg": rng.integers(6, 25, size=total).astype(np.float64),
    "_V0NormChi2Pos": rng.uniform(0.5, 5, size=total),
    "_V0NormChi2Neg": rng.uniform(0.5, 5, size=total),
    "_V0D0Pos": rng.uniform(0.01, 1, size=total),
    "_V0DzPos": rng.uniform(-2, 2, size=total),
    "_V0D0Neg": rng.uniform(0.01, 1, size=total),
    "_V0DzNeg": rng.uniform(-2, 2, size=total),
  }
  for k, v in kept.items():
    arrays[k] = _jagged(cast(v) if k != "_V0Type" else v, nV0)

  if not slim:
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

  return arrays, int(nV0.sum()), float(nV0.mean())


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("-n", "--nevents", type=int, default=2000)
  parser.add_argument("--out-dir", default="")
  parser.add_argument("--seed", type=int, default=2024)
  args = parser.parse_args()

  try:
    import uproot  # noqa: F401
  except ImportError as exc:
    raise SystemExit("uproot required") from exc

  out_dir = args.out_dir or tempfile.mkdtemp(prefix="ntuple_slim_")
  fat_path = os.path.join(out_dir, "fat_schema.root")
  slim_path = os.path.join(out_dir, "slim_schema.root")

  fat_arr, fat_nv0, fat_mean = build_arrays(args.nevents, slim=False, seed=args.seed)
  slim_arr, slim_nv0, slim_mean = build_arrays(args.nevents, slim=True, seed=args.seed)
  fat_bytes = _write_tree(fat_path, fat_arr)
  slim_bytes = _write_tree(slim_path, slim_arr)
  factor = fat_bytes / slim_bytes if slim_bytes else float("inf")

  print(f"events: {args.nevents}")
  print(f"fat:  {fat_path}")
  print(f"      size={fat_bytes/1e6:.3f} MB  nV0={fat_nv0}  mean_nV0={fat_mean:.2f}")
  print(f"slim: {slim_path}")
  print(f"      size={slim_bytes/1e6:.3f} MB  nV0={slim_nv0}  mean_nV0={slim_mean:.2f}")
  print(f"size factor (fat/slim): {factor:.2f}x")
  print(
    "Note: synthetic multiplicities (2μ, 8 jets, ~30% Λ in fat). "
    "Real CRAB files also gain from ZIP/compression + fewer Λ rows; "
    "resubmit full CRAB after merge — do not delete existing EOS output."
  )


if __name__ == "__main__":
  main()
