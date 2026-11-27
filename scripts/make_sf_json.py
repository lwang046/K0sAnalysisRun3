#!/usr/bin/env python3
"""Export C(Δ2D) scale factors to JSON / correctionlib-friendly tables.

Reads ``mcvsdata_fill`` output (data + MC ``*_nominal`` TH1s), forms
``C = data / MC`` bin-by-bin (MC already range-normalized when fill used
``--normmode range``), and writes:

* schema ``displaced_track_C_delta2D_v1`` (bins + C ± err), and
* optional correctionlib v2 payload (``--correctionlib``).

When multiple data or MC ``*_nominal`` histograms exist (e.g. Muon0+Muon1),
they are **summed** (errors in quadrature) before the ratio — matching how
``mcvsdata_fill`` normalizes across ``datain`` / ``mcin``.

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


def _classify_nominals(
  nominals: list[str],
  data_hist: str | None,
  mc_hist: str | None,
) -> tuple[list[str], list[str]]:
  """Split ``*_nominal`` names into data vs MC groups."""
  if data_hist or mc_hist:
    # Explicit overrides: optional single hist each; remaining go to the other side.
    data_names = [data_hist] if data_hist else []
    mc_names = [mc_hist] if mc_hist else []
    if data_hist and data_hist not in nominals:
      raise SystemExit("data hist {!r} not in {}".format(data_hist, nominals))
    if mc_hist and mc_hist not in nominals:
      raise SystemExit("mc hist {!r} not in {}".format(mc_hist, nominals))
    if not data_names:
      data_names = [k for k in nominals if k not in mc_names]
    if not mc_names:
      mc_names = [k for k in nominals if k not in data_names]
    return data_names, mc_names

  data_sub = ("data", "muon", "run2024")
  mc_sub = ("sim", "dy", "mc", "summer")
  data_names = [k for k in nominals if any(s in k.lower() for s in data_sub)]
  mc_names = [k for k in nominals if any(s in k.lower() for s in mc_sub)]
  # Drop accidental overlaps (prefer exclusive assignment).
  overlap = set(data_names) & set(mc_names)
  if overlap:
    # Ambiguous labels: keep in neither auto set; require explicit flags.
    data_names = [k for k in data_names if k not in overlap]
    mc_names = [k for k in mc_names if k not in overlap]
  leftover = [k for k in nominals if k not in data_names and k not in mc_names]
  if leftover and (not data_names or not mc_names):
    # Fallback: first leftover → empty side.
    for k in leftover:
      if not data_names:
        data_names.append(k)
      elif not mc_names:
        mc_names.append(k)
  if not data_names or not mc_names:
    raise SystemExit(
      "Could not classify data vs MC nominals (data={}, mc={}, all={}). "
      "Pass --data-hist / --mc-hist.".format(data_names, mc_names, nominals)
    )
  return data_names, mc_names


def _sum_hists(f, names: list[str]):
  import numpy as np

  vals = None
  errs2 = None
  edges = None
  for name in names:
    v, e = f[name].to_numpy()
    err = np.asarray(f[name].errors(), dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    if edges is None:
      edges = np.asarray(e, dtype=np.float64)
      vals = v.copy()
      errs2 = err * err
    else:
      if not np.allclose(edges, e):
        raise SystemExit(
          "Bin edges differ for {}: {} vs {}".format(name, e, edges)
        )
      vals = vals + v
      errs2 = errs2 + err * err
  return edges, vals, np.sqrt(errs2)


def _read_pair(path: str, data_hist: str | None, mc_hist: str | None):
  import uproot

  with uproot.open(path) as f:
    keys = [k.split(";")[0] for k in f.keys()]
    nominals = [k for k in keys if k.endswith("_nominal")]
    if not nominals:
      raise SystemExit("No '*_nominal' histograms in {}".format(path))

    data_names, mc_names = _classify_nominals(nominals, data_hist, mc_hist)
    dedges, dvals, derr = _sum_hists(f, data_names)
    medges, mvals, merr = _sum_hists(f, mc_names)
    if not (dedges == medges).all():
      raise SystemExit("Data/MC bin edges differ: {} vs {}".format(dedges, medges))

    meta = {
      "data_hists": data_names,
      "mc_hists": mc_names,
      "data_hist": "+".join(data_names),
      "mc_hist": "+".join(mc_names),
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
  parser.add_argument(
    "--data-hist",
    default=None,
    help="Optional single data TH1 name (otherwise sum all data-like *_nominal)",
  )
  parser.add_argument(
    "--mc-hist",
    default=None,
    help="Optional single MC TH1 name (otherwise sum all MC-like *_nominal)",
  )
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
    "data_hists": meta["data_hists"],
    "mc_hists": meta["mc_hists"],
    "bins_cm": edges,
    "C": c_vals,
    "C_err": c_errs,
    "note": (
      "C_i = (sum data_i) / (sum MC_i) from mcvsdata_fill *_nominal TH1s "
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
