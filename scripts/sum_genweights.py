#!/usr/bin/env python3
"""Sum signed genWeight over DisplacedV0 ntuple filelists.

**Caveat:** with ``enableDimuonPreFilter=True``, ntuple rows are post-filter.
``ΣgenWeight`` here is **not** a full-sample ``hCounter``. Prefer:

* ``mcvsdata_fill.py --mc-sumweights <full_sample_Σw>`` (external / GenXSec bookkeeping), or
* resubmit MC with ``GenWeightCounter`` on the Path *before* the filter.

This script is for diagnostics and for writing ``hCounter_postfilter``.
Only ``--as-hcounter`` writes a key named ``hCounter`` (loud warning).

Examples:
  python3 scripts/sum_genweights.py -i results/dy_files.txt -o results/dy_postfilter_sumw.json
  python3 scripts/sum_genweights.py -i dy_files.txt --inject results/v0sel_dy_Summer24.root
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

# Allow ``from v0building.v0builder import …`` when run from repo root.
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
  sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "v0building"))

from v0builder import (  # noqa: E402
  _discover_tree,
  _hcounter_from_sum,
  _hist_for_write,
  collect_input_files,
)


def _sum_file(path: str, treename: str) -> tuple[float, int, str]:
  import uproot

  with uproot.open(path) as f:
    fkeys = [k.split(";")[0] for k in f.keys()]
    tree_path, layout = _discover_tree(fkeys, treename)
    tree = f[tree_path]
    n = int(tree.num_entries)
    if layout == "displacedv0":
      if "genWeight" not in tree.keys():
        raise KeyError("{}: no genWeight branch (keys={})".format(path, list(tree.keys())[:20]))
      w = tree["genWeight"].array(library="np")
    else:
      # Upstream already has hCounter; summing event weights is still useful.
      if "genWeight" in tree.keys():
        w = tree["genWeight"].array(library="np")
      elif "_weight" in tree.keys():
        w = tree["_weight"].array(library="np")
      else:
        raise KeyError("{}: no genWeight/_weight".format(path))
    return float(np.sum(w)), n, layout


def _inject_hcounter(
  v0sel: str, sumweights: float, output: str, *, as_hcounter: bool
) -> None:
  import uproot

  tree_names = ("nimloth", "celeborn", "laurelin", "telperion")
  key = "hCounter" if as_hcounter else "hCounter_postfilter"
  if as_hcounter:
    print(
      "WARNING: writing post-filter ΣgenWeight as 'hCounter'. "
      "This is wrong for absolute σ×L when DimuonPreFilter was enabled.",
      file=sys.stderr,
    )
  os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
  with uproot.open(v0sel) as fin, uproot.recreate(output) as fout:
    keys = {k.split(";")[0] for k in fin.keys(recursive=False)}
    for name in tree_names:
      if name not in keys:
        continue
      fout[name] = fin[name].arrays()
    if "nTrueInteractions" in keys:
      try:
        fout["nTrueInteractions"] = fin["nTrueInteractions"].to_numpy()
      except Exception:
        print("WARNING: could not copy nTrueInteractions", file=sys.stderr)
    fout[key] = _hist_for_write(_hcounter_from_sum(sumweights))
  print("Wrote {} with {}={}".format(output, key, sumweights))


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "-i",
    "--input",
    nargs="+",
    required=True,
    help="ROOT path(s), globs, and/or text filelists (same as v0builder -i)",
  )
  parser.add_argument("-t", "--treename", default="displacedV0Ntuple/events")
  parser.add_argument(
    "-o",
    "--output",
    default=None,
    help="Optional JSON summary path (sumweights, nentries, nfiles)",
  )
  parser.add_argument(
    "--inject",
    default=None,
    help="Existing v0sel ROOT to copy + attach hCounter (writes sibling by default)",
  )
  parser.add_argument(
    "--inject-output",
    default=None,
    help="Output path for --inject (default: <inject>_with_hCounter_postfilter.root)",
  )
  parser.add_argument(
    "--as-hcounter",
    action="store_true",
    help="Write key hCounter instead of hCounter_postfilter (dangerous if Path filter on)",
  )
  args = parser.parse_args()

  files = collect_input_files(args.input)
  print("Summing genWeight over {} file(s)...".format(len(files)))
  total_w = 0.0
  total_n = 0
  layout = None
  for i, path in enumerate(files):
    w, n, layout = _sum_file(path, args.treename)
    total_w += w
    total_n += n
    if i < 3 or (i + 1) % 500 == 0 or i + 1 == len(files):
      print("  [{}/{}] {}  n={}  sumw={:.6g}".format(i + 1, len(files), path, n, w))
      sys.stdout.flush()

  summary = {
    "sumweights": total_w,
    "nentries": total_n,
    "nfiles": len(files),
    "layout": layout,
    "treename": args.treename,
  }
  print("TOTAL sumweights={} nentries={} nfiles={}".format(total_w, total_n, len(files)))

  if args.output:
    out = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
      json.dump(summary, fh, indent=2)
      fh.write("\n")
    print("Wrote {}".format(out))

  if args.inject:
    inj_out = args.inject_output
    if inj_out is None:
      base, ext = os.path.splitext(os.path.abspath(args.inject))
      tag = "_with_hCounter" if args.as_hcounter else "_with_hCounter_postfilter"
      inj_out = base + tag + (ext or ".root")
    _inject_hcounter(args.inject, total_w, inj_out, as_hcounter=args.as_hcounter)
    summary["inject_output"] = os.path.abspath(inj_out)
  summary["note"] = (
    "post-filter ΣgenWeight when DimuonPreFilter was on — "
    "use --mc-sumweights for full-sample absolute norm"
  )

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
