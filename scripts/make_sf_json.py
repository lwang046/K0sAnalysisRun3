#!/usr/bin/env python3
"""Export C(Δ2D) scale factors to JSON / correctionlib-friendly tables.

Reads ``mcvsdata_fill`` output (data + MC ``*_nominal`` TH1s), forms
``C = data / MC`` bin-by-bin (MC already range-normalized when fill used
``--normmode range``), and writes:

* schema ``displaced_track_C_delta2D_v1`` (bins + C ± err), and
* optional correctionlib v2 payload (``--correctionlib``).

Attribution: method from AN-20-111; Run3 recipe in Project method doc.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any


def _ratio_err(n: float, dn: float, d: float, dd: float) -> float:
  """Propagate statistical errors for n/d (uncorrelated)."""
  if d == 0:
    return 0.0
  return abs(n / d) * math.sqrt((dn / n) ** 2 + (dd / d) ** 2) if n != 0 else abs(dn / d)


def _read_pair(path: str, data_hist: str | None, mc_hist: str | None):
  import uproot
  import numpy as np

  with uproot.open(path) as f:
    keys = [k.split(";")[0] for k in f.keys()]
    nominals = [k for k in keys if k.endswith("_nominal")]
    if not nominals:
      raise SystemExit("No '*_nominal' histograms in {}".format(path))

    def pick(explicit: str | None, prefer_substr: tuple[str, ...], fallback_idx: int) -> str:
      if explicit:
        if explicit not in keys:
          raise SystemExit("Histogram {!r} not in file; have {}".format(explicit, keys))
        return explicit
      for k in nominals:
        low = k.lower()
        if any(s in low for s in prefer_substr):
          return k
      if len(nominals) <= fallback_idx:
        raise SystemExit("Need data and MC nominal hists; found {}".format(nominals))
      return nominals[fallback_idx]

    # Data labels usually contain "data" / "Muon" / "Run2024"; MC: "sim" / "DY".
    dname = pick(data_hist, ("data", "muon", "run2024"), 0)
    mname = pick(mc_hist, ("sim", "dy", "mc", "summer"), 1 if nominals[0] == dname else 0)
    if dname == mname:
      others = [k for k in nominals if k != dname]
      if not others:
        raise SystemExit("Could not separate data vs MC nominals: {}".format(nominals))
      mname = others[0]

    dvals, dedges = f[dname].to_numpy()
    mvals, medges = f[mname].to_numpy()
    if not np.allclose(dedges, medges):
      raise SystemExit("Data/MC bin edges differ: {} vs {}".format(dedges, medges))
    derr = f[dname].errors()
    merr = f[mname].errors()
    meta = {
      "data_hist": dname,
      "mc_hist": mname,
      "keys": keys,
    }
    if "norm_scale" in keys:
      try:
        ns = f["norm_scale"]
        meta["norm_scale"] = [float(ns[0]), float(ns[1])]
      except Exception:
        pass
    if "lumi" in keys:
      try:
        meta["lumi_pb"] = float(f["lumi"][0])
      except Exception:
        pass
    return (
      [float(x) for x in dedges],
      [float(x) for x in dvals],
      [float(x) for x in derr],
      [float(x) for x in mvals],
      [float(x) for x in merr],
      meta,
    )


def _correctionlib_payload(
  era: str,
  edges: list[float],
  c_vals: list[float],
  description: str,
) -> dict[str, Any]:
  return {
    "schema_version": 2,
    "description": description,
    "corrections": [
      {
        "name": "C_delta2D_{}".format(era),
        "description": "Displaced-track efficiency scale factor C(Δ2D) for {}".format(era),
        "version": 1,
        "inputs": [
          {
            "name": "Delta2D",
            "type": "real",
            "description": "2D transverse displacement Δ2D [cm]",
          }
        ],
        "output": {
          "name": "C",
          "type": "real",
          "description": "data/MC scale factor after low-Δ2D normalization",
        },
        "data": {
          "nodetype": "binning",
          "input": "Delta2D",
          "edges": edges,
          "content": c_vals,
          "flow": "clamp",
        },
      }
    ],
  }


def main() -> int:
  parser = argparse.ArgumentParser(
    description="C(Δ2D) → JSON / correctionlib export"
  )
  parser.add_argument("-i", "--input", required=True, help="ROOT file with C fill histograms")
  parser.add_argument("-o", "--output", required=True, help="Output JSON path")
  parser.add_argument("--era", default="Run2024D")
  parser.add_argument("--data-hist", default=None, help="Override data TH1 name")
  parser.add_argument("--mc-hist", default=None, help="Override MC TH1 name")
  parser.add_argument(
    "--correctionlib",
    action="store_true",
    help="Also write <output>.correctionlib.json (schema_version 2)",
  )
  args = parser.parse_args()

  edges, dvals, derr, mvals, merr, meta = _read_pair(
    args.input, args.data_hist, args.mc_hist
  )
  c_vals: list[float] = []
  c_errs: list[float] = []
  for n, dn, d, dd in zip(dvals, derr, mvals, merr):
    if d == 0:
      c_vals.append(0.0)
      c_errs.append(0.0)
    else:
      c_vals.append(float(n / d))
      c_errs.append(float(_ratio_err(n, dn, d, dd)))

  payload: dict[str, Any] = {
    "schema": "displaced_track_C_delta2D_v1",
    "era": args.era,
    "source": "AN-20-111 / K0sAnalysisRun3",
    "input": args.input,
    "data_hist": meta["data_hist"],
    "mc_hist": meta["mc_hist"],
    "bins_cm": edges,
    "C": c_vals,
    "C_err": c_errs,
    "note": (
      "C_i = data_i / MC_i from mcvsdata_fill *_nominal TH1s "
      "(MC already scaled when fill used --normmode range)."
    ),
  }
  if "norm_scale" in meta:
    payload["norm_scale"] = meta["norm_scale"]
  if "lumi_pb" in meta:
    payload["lumi_pb"] = meta["lumi_pb"]

  with open(args.output, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
    f.write("\n")
  print(
    "Wrote SF JSON to {} ({} bins, data={}, mc={})".format(
      args.output, len(c_vals), meta["data_hist"], meta["mc_hist"]
    ),
    file=sys.stderr,
  )

  if args.correctionlib:
    cl_path = args.output
    if cl_path.endswith(".json"):
      cl_path = cl_path[:-5] + ".correctionlib.json"
    else:
      cl_path = cl_path + ".correctionlib.json"
    cl = _correctionlib_payload(
      args.era,
      edges,
      c_vals,
      payload["note"],
    )
    with open(cl_path, "w", encoding="utf-8") as f:
      json.dump(cl, f, indent=2)
      f.write("\n")
    print("Wrote correctionlib JSON to {}".format(cl_path), file=sys.stderr)

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
