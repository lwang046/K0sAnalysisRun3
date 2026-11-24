#!/usr/bin/env python3
"""Write a tiny DisplacedV0-like ROOT file for offline dry-runs (no CMSSW).

Creates tree ``displacedV0Ntuple/events`` with the Sol production branch names
expected by ``v0building/v0builder.py`` (DY selection + V0 AN §6 path).

Usage:
  python3 scripts/make_dummy_displacedv0_ntuple.py -o /tmp/dummy_displacedv0.root
  python3 v0building/v0builder.py -i /tmp/dummy_displacedv0.root -o /tmp/out.root \\
    --apply-dy-selection
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
  # Mix of signs for signed-weight bookkeeping smoke
  genWeight[::7] = -1.0
  Pileup_nTrue = rng.uniform(20, 50, size=n).astype(np.float32)
  passDimuonHLT = np.ones(n, dtype=bool)

  # Exactly 2 medium OS muons near mZ (for DY selection)
  nMuon = np.full(n, 2, dtype=np.int32)
  Muon_pt = np.column_stack(
    [rng.uniform(35, 60, n), rng.uniform(26, 45, n)]
  ).astype(np.float32)
  Muon_eta = rng.uniform(-1.5, 1.5, size=(n, 2)).astype(np.float32)
  Muon_phi = rng.uniform(-np.pi, np.pi, size=(n, 2)).astype(np.float32)
  Muon_charge = np.column_stack([np.ones(n), -np.ones(n)]).astype(np.int32)
  Muon_mediumId = np.ones((n, 2), dtype=bool)

  # Dimuon scalars (Sol Z-row)
  import vector

  mu1 = vector.zip(
    {"pt": Muon_pt[:, 0], "eta": Muon_eta[:, 0], "phi": Muon_phi[:, 0], "mass": 0.105658}
  )
  mu2 = vector.zip(
    {"pt": Muon_pt[:, 1], "eta": Muon_eta[:, 1], "phi": Muon_phi[:, 1], "mass": 0.105658}
  )
  ll = mu1 + mu2
  Dimuon_mass = np.asarray(ll.mass, dtype=np.float32)
  Dimuon_pt = np.asarray(ll.pt, dtype=np.float32)
  Dimuon_y = np.asarray(ll.rapidity, dtype=np.float32)

  # Compact jet scalars (no Jet_* arrays); include some zero-jet events
  nJetSel = rng.integers(0, 4, size=n).astype(np.uint32)
  nJetSelStatus = (nJetSel > 0).astype(np.uint8)
  maxDeepJet = np.where(
    nJetSel > 0, rng.uniform(0.0, 0.04, size=n), -1.0
  ).astype(np.float32)
  passDeepJetLooseVeto = np.ones(n, dtype=bool)

  # Sol: keep empty-V0 Z rows (~20% with _nV0s==0)
  nV0 = rng.integers(0, 4, size=n, dtype=np.uint32)
  total = int(nV0.sum())

  _V0Type = np.ones(total, dtype=np.uint32)
  _V0InvMass = rng.normal(0.4976, 0.006, size=total).astype(np.float32)
  _V0RPV = rng.uniform(0.2, 25.0, size=total).astype(np.float32)
  _V0RPVSig = (_V0RPV / 0.05).astype(np.float32)
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
  _V0D0Pos = rng.uniform(0.05, 0.8, size=total).astype(np.float32)
  _V0DzPos = rng.uniform(-1.5, 1.5, size=total).astype(np.float32)
  _V0D0Neg = rng.uniform(0.05, 0.8, size=total).astype(np.float32)
  _V0DzNeg = rng.uniform(-1.5, 1.5, size=total).astype(np.float32)
  _V0SrcPos = rng.integers(0, 2, size=total, dtype=np.uint8)
  _V0SrcNeg = rng.integers(0, 2, size=total, dtype=np.uint8)
  _V0IdxPos = rng.integers(0, 200, size=total, dtype=np.int32)
  _V0IdxNeg = rng.integers(0, 200, size=total, dtype=np.int32)
  # Position + momentum aligned so cosθ_pointing ≈ 1 (passes AN > 0.99 cut)
  _V0X = rng.uniform(1.0, 20.0, size=total).astype(np.float32)
  _V0Y = rng.uniform(1.0, 20.0, size=total).astype(np.float32)
  _V0Z = rng.uniform(-50, 50, size=total).astype(np.float32)
  _V0Px = _V0X.copy()
  _V0Py = _V0Y.copy()
  _V0CosPointingPV = np.ones(total, dtype=np.float32)
  _V0CosPointingBS = np.ones(total, dtype=np.float32)
  # Neighbour stubs (status=0)
  _V0NearestChgDRPos = np.full(total, np.nan, dtype=np.float32)
  _V0NearestChgDRNeg = np.full(total, np.nan, dtype=np.float32)
  _V0NearestChgStatusPos = np.zeros(total, dtype=np.uint8)
  _V0NearestChgStatusNeg = np.zeros(total, dtype=np.uint8)
  _V0NChgDR01Pos = np.full(total, -1, dtype=np.int32)
  _V0NChgDR01Neg = np.full(total, -1, dtype=np.int32)
  _beamSpotX = np.zeros(n, dtype=np.float32)
  _beamSpotY = np.zeros(n, dtype=np.float32)
  _beamSpotZ = np.zeros(n, dtype=np.float32)
  _primaryVertexX = np.zeros(n, dtype=np.float32)
  _primaryVertexY = np.zeros(n, dtype=np.float32)
  _primaryVertexZ = np.zeros(n, dtype=np.float32)

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
    "nMuon": nMuon,
    "Muon_pt": Muon_pt,
    "Muon_eta": Muon_eta,
    "Muon_phi": Muon_phi,
    "Muon_charge": Muon_charge,
    "Muon_mediumId": Muon_mediumId,
    "Dimuon_mass": Dimuon_mass,
    "Dimuon_pt": Dimuon_pt,
    "Dimuon_y": Dimuon_y,
    "nJetSel": nJetSel,
    "nJetSelStatus": nJetSelStatus,
    "maxDeepJet": maxDeepJet,
    "passDeepJetLooseVeto": passDeepJetLooseVeto,
    "_nV0s": nV0,
    "_V0Type": jagged(_V0Type),
    "_V0InvMass": jagged(_V0InvMass),
    "_V0RPV": jagged(_V0RPV),
    "_V0RPVSig": jagged(_V0RPVSig),
    "_V0DCA": jagged(_V0DCA),
    "_V0VtxNormChi2": jagged(_V0VtxNormChi2),
    "_V0Pt": jagged(_V0Pt),
    "_V0Eta": jagged(_V0Eta),
    "_V0Phi": jagged(_V0Phi),
    "_V0CosPointingPV": jagged(_V0CosPointingPV),
    "_V0CosPointingBS": jagged(_V0CosPointingBS),
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
    "_V0SrcPos": jagged(_V0SrcPos),
    "_V0SrcNeg": jagged(_V0SrcNeg),
    "_V0IdxPos": jagged(_V0IdxPos),
    "_V0IdxNeg": jagged(_V0IdxNeg),
    "_V0NearestChgDRPos": jagged(_V0NearestChgDRPos),
    "_V0NearestChgDRNeg": jagged(_V0NearestChgDRNeg),
    "_V0NearestChgStatusPos": jagged(_V0NearestChgStatusPos),
    "_V0NearestChgStatusNeg": jagged(_V0NearestChgStatusNeg),
    "_V0NChgDR01Pos": jagged(_V0NChgDR01Pos),
    "_V0NChgDR01Neg": jagged(_V0NChgDR01Neg),
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
  n_empty = int(np.sum(nV0 == 0))
  print(
    f"Wrote {out} with {n} events ({n_empty} with _nV0s==0), {total} V0 candidates"
  )


if __name__ == "__main__":
  main()
