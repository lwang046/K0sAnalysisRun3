#!/usr/bin/env python3
"""Write a tiny DisplacedV0-like ROOT file for offline dry-runs (no CMSSW).

Creates tree ``displacedV0Ntuple/events`` with the branch names expected by
``v0building/v0builder.py`` (DY selection + V0 AN §6 path).

Usage:
  python3 scripts/make_dummy_displacedv0_ntuple.py -o /tmp/dummy_displacedv0.root
  python3 v0building/v0builder.py -i /tmp/dummy_displacedv0.root -o /tmp/out.root \\
    --apply-dy-selection --no-bveto
"""
from __future__ import annotations

import argparse
import os

import numpy as np


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("-o", "--output", default="dummy_displacedv0.root")
  parser.add_argument("-n", "--nevents", type=int, default=40)
  parser.add_argument("--seed", type=int, default=2024)
  args = parser.parse_args()

  try:
    import uproot
  except ImportError as exc:
    raise SystemExit("uproot is required to write the dummy ntuple") from exc

  rng = np.random.default_rng(args.seed)
  n = args.nevents

  # Event-level
  run = np.full(n, 380000, dtype=np.uint32)
  lumi = np.arange(1, n + 1, dtype=np.uint32)
  event = np.arange(1, n + 1, dtype=np.uint64)
  nPV = np.full(n, 25, dtype=np.int32)
  genWeight = np.ones(n, dtype=np.float32)
  Pileup_nTrue = rng.uniform(20, 50, size=n).astype(np.float32)
  passDimuonHLT = np.ones(n, dtype=bool)
  hlt = np.ones(n, dtype=bool)

  # Exactly 2 medium OS muons near mZ (for DY selection)
  nMuon = np.full(n, 2, dtype=np.int32)
  Muon_pt = np.column_stack(
    [rng.uniform(35, 60, n), rng.uniform(26, 45, n)]
  ).astype(np.float32)
  Muon_eta = rng.uniform(-1.5, 1.5, size=(n, 2)).astype(np.float32)
  Muon_phi = rng.uniform(-np.pi, np.pi, size=(n, 2)).astype(np.float32)
  Muon_charge = np.column_stack([np.ones(n), -np.ones(n)]).astype(np.int32)
  Muon_mediumId = np.ones((n, 2), dtype=bool)
  Muon_mass = np.full((n, 2), 0.105658, dtype=np.float32)

  # A few jets below / above DeepJet WP for mask testing
  nJet = np.full(n, 2, dtype=np.int32)
  Jet_pt = np.column_stack([rng.uniform(40, 80, n), rng.uniform(35, 70, n)]).astype(
    np.float32
  )
  Jet_eta = rng.uniform(-2.0, 2.0, size=(n, 2)).astype(np.float32)
  Jet_btagDeepFlavB = rng.uniform(0.0, 0.03, size=(n, 2)).astype(np.float32)
  Jet_jetId = np.full((n, 2), 6, dtype=np.int32)

  # Variable-length V0 candidates: 0–3 per event; type 1 = Ks near PDG mass
  nV0 = rng.integers(0, 4, size=n, dtype=np.uint32)
  total = int(nV0.sum())

  def flat_per_v0(draw_evt):
    """Expand per-event draw to per-V0 length."""
    return np.repeat(draw_evt, nV0)

  _V0Type = np.ones(total, dtype=np.uint32)
  # CDTE-30 slim schema: float32 V0/PV/BS (matches DisplacedV0 /F leaves)
  _V0InvMass = rng.normal(0.4976, 0.006, size=total).astype(np.float32)
  _V0RPV = rng.uniform(0.2, 25.0, size=total).astype(np.float32)
  _V0RBS = (_V0RPV * 0.98).astype(np.float32)
  _V0RPVSig = (_V0RPV / 0.05).astype(np.float32)
  _V0RBSSig = (_V0RBS / 0.05).astype(np.float32)
  _V0DCA = rng.uniform(0.01, 0.15, size=total).astype(np.float32)
  _V0VtxNormChi2 = rng.uniform(0.5, 5.0, size=total).astype(np.float32)
  _V0Pt = rng.uniform(1.5, 8.0, size=total).astype(np.float32)
  _V0Eta = rng.uniform(-2.0, 2.0, size=total).astype(np.float32)
  _V0Phi = rng.uniform(-np.pi, np.pi, size=total).astype(np.float32)
  _V0PtPos = rng.uniform(1.1, 5.0, size=total).astype(np.float32)
  _V0PtNeg = rng.uniform(1.1, 5.0, size=total).astype(np.float32)
  _V0EtaPos = rng.uniform(-2.0, 2.0, size=total).astype(np.float32)
  _V0EtaNeg = rng.uniform(-2.0, 2.0, size=total).astype(np.float32)
  _V0PhiPos = rng.uniform(-np.pi, np.pi, size=total).astype(np.float32)
  _V0PhiNeg = rng.uniform(-np.pi, np.pi, size=total).astype(np.float32)
  _V0NHitsPos = rng.integers(8, 20, size=total).astype(np.float32)
  _V0NHitsNeg = rng.integers(8, 20, size=total).astype(np.float32)
  _V0NormChi2Pos = rng.uniform(0.5, 3.0, size=total).astype(np.float32)
  _V0NormChi2Neg = rng.uniform(0.5, 3.0, size=total).astype(np.float32)
  _V0D0Pos = rng.uniform(0.05, 0.5, size=total).astype(np.float32)
  _V0DzPos = rng.uniform(-1, 1, size=total).astype(np.float32)
  _V0D0Neg = rng.uniform(0.05, 0.5, size=total).astype(np.float32)
  _V0DzNeg = rng.uniform(-1, 1, size=total).astype(np.float32)
  # Position + momentum aligned so cosθ_pointing ≈ 1 (passes AN > 0.99 cut)
  _V0X = rng.uniform(1.0, 20.0, size=total).astype(np.float32)
  _V0Y = rng.uniform(1.0, 20.0, size=total).astype(np.float32)
  _V0Z = rng.uniform(-50, 50, size=total).astype(np.float32)
  _V0Px = _V0X.copy()
  _V0Py = _V0Y.copy()
  _beamSpotX = np.zeros(n, dtype=np.float32)
  _beamSpotY = np.zeros(n, dtype=np.float32)
  _beamSpotZ = np.zeros(n, dtype=np.float32)
  _primaryVertexX = np.zeros(n, dtype=np.float32)
  _primaryVertexY = np.zeros(n, dtype=np.float32)
  _primaryVertexZ = np.zeros(n, dtype=np.float32)

  # uproot jagged: list of arrays per event for V0 branches
  def jagged(flat):
    out = []
    i = 0
    for nv in nV0:
      out.append(flat[i : i + nv])
      i += nv
    return out

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
    "Muon_pt": Muon_pt,
    "Muon_eta": Muon_eta,
    "Muon_phi": Muon_phi,
    "Muon_charge": Muon_charge,
    "Muon_mediumId": Muon_mediumId,
    "Muon_mass": Muon_mass,
    "nJet": nJet,
    "Jet_pt": Jet_pt,
    "Jet_eta": Jet_eta,
    "Jet_btagDeepFlavB": Jet_btagDeepFlavB,
    "Jet_jetId": Jet_jetId,
    "_nV0s": nV0,
    "_V0Type": jagged(_V0Type),
    "_V0InvMass": jagged(_V0InvMass),
    "_V0RPV": jagged(_V0RPV),
    "_V0RBS": jagged(_V0RBS),
    "_V0RPVSig": jagged(_V0RPVSig),
    "_V0RBSSig": jagged(_V0RBSSig),
    "_V0DCA": jagged(_V0DCA),
    "_V0VtxNormChi2": jagged(_V0VtxNormChi2),
    "_V0Pt": jagged(_V0Pt),
    "_V0Eta": jagged(_V0Eta),
    "_V0Phi": jagged(_V0Phi),
    "_V0PtPos": jagged(_V0PtPos),
    "_V0PtNeg": jagged(_V0PtNeg),
    "_V0EtaPos": jagged(_V0EtaPos),
    "_V0EtaNeg": jagged(_V0EtaNeg),
    "_V0PhiPos": jagged(_V0PhiPos),
    "_V0PhiNeg": jagged(_V0PhiNeg),
    "_V0NHitsPos": jagged(_V0NHitsPos),
    "_V0NHitsNeg": jagged(_V0NHitsNeg),
    "_V0NormChi2Pos": jagged(_V0NormChi2Pos),
    "_V0NormChi2Neg": jagged(_V0NormChi2Neg),
    "_V0D0Pos": jagged(_V0D0Pos),
    "_V0DzPos": jagged(_V0DzPos),
    "_V0D0Neg": jagged(_V0D0Neg),
    "_V0DzNeg": jagged(_V0DzNeg),
    "_V0X": jagged(_V0X),
    "_V0Y": jagged(_V0Y),
    "_V0Z": jagged(_V0Z),
    "_V0Px": jagged(_V0Px),
    "_V0Py": jagged(_V0Py),
    "_beamSpotX": _beamSpotX,
    "_beamSpotY": _beamSpotY,
    "_beamSpotZ": _beamSpotZ,
    "_primaryVertexX": _primaryVertexX,
    "_primaryVertexY": _primaryVertexY,
    "_primaryVertexZ": _primaryVertexZ,
  }

  out = os.path.abspath(args.output)
  os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
  with uproot.recreate(out) as f:
    f["displacedV0Ntuple/events"] = arrays
  print(f"Wrote {out} with {n} events, {total} V0 candidates")


if __name__ == "__main__":
  main()
