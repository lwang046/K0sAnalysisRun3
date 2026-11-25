###########################################################
# Build dedicated V0 trees from DisplacedV0 Run3 ntuples  #
###########################################################
# Ported from LukaLambrecht/K0sAnalysis v0building/v0builder.py
# (commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8) and adapted
# for the slim DisplacedV0 ntuple branch names.
#
# Input tree:  displacedV0Ntuple/events  (DisplacedV0Ntuple / TFileService)
# Output trees (unchanged AN analysis schema):
#   nimloth   — per-event DY controls
#   celeborn  — per-muon kinematics
#   laurelin  — K_S^0 candidates (AN §6 selection applied)
#   telperion — Lambda candidates (diagnostic)
#
# Prefer CMSSW V0Analyzer for Kalman fitting; this step applies
# AN-20-111 §6 tight cuts (v0selections.selection_legacy) and
# optional offline DY reference selection (AN §5).
#
# Input (-i / --inputfile): one or more of
#   - a single ROOT file
#   - a text filelist (one path per line; blank lines and # comments ignored)
#   - multiple ROOT paths and/or shell globs
# Events are read file-by-file (TChain-like over a filelist/glob) so CRAB
# shards on EOS need not be hadd'ed first; peak RAM stays near one shard plus
# the selected output. Example:
#   python3 v0builder.py -i dy_files.txt -o v0sel_dy.root --apply-dy-selection

from __future__ import annotations

import argparse
import glob
import os
import sys

import awkward as ak
import numpy as np
import uproot
import vector

from v0selections import cospointing, selection

MZ = 91.1876
# Keep in sync with analysis/config_defaults_run3.py DEEPJET_LOOSE_WP.
# TBD: freeze from BTV 2024 JSON (samples/deepjet_wp_2024.md / conditions.md).
DEEPJET_LOOSE_WP_PLACEHOLDER = 0.0494


def _normalize_path(path: str, base_dir: str | None = None) -> str:
  """Absolute-ize local paths; leave root:// / xrootd URLs unchanged."""
  path = path.strip()
  if not path:
    return path
  if path.startswith(("root://", "http://", "https://")):
    return path
  if os.path.isabs(path):
    return os.path.abspath(path)
  if base_dir:
    return os.path.abspath(os.path.join(base_dir, path))
  return os.path.abspath(path)


def _is_root_file(path: str) -> bool:
  return path.rstrip("/").endswith(".root")


def _read_filelist(list_path: str) -> list[str]:
  """Read ROOT paths from a text filelist (one per line)."""
  list_path = os.path.abspath(list_path)
  base_dir = os.path.dirname(list_path)
  out: list[str] = []
  with open(list_path, "r", encoding="utf-8") as fh:
    for lineno, raw in enumerate(fh, 1):
      line = raw.strip()
      if not line or line.startswith("#"):
        continue
      # Allow optional "file:" prefix from some CMS tools.
      if line.startswith("file:"):
        line = line[5:]
      resolved = _normalize_path(line, base_dir=base_dir)
      if not _is_root_file(resolved) and not resolved.startswith("root://"):
        raise ValueError(
          "filelist {}:{}: expected a .root path, got {!r}".format(
            list_path, lineno, line
          )
        )
      out.append(resolved)
  if not out:
    raise ValueError("filelist {!r} contains no ROOT paths".format(list_path))
  return out


def collect_input_files(specs: list[str]) -> list[str]:
  """Resolve ``-i`` tokens into an ordered list of ROOT files.

  Each token may be:
  - a ``.root`` path (local or ``root://``),
  - a glob matching ``.root`` files,
  - a text filelist (one path per line).
  """
  files: list[str] = []
  for spec in specs:
    spec = spec.strip()
    if not spec:
      continue
    # Glob first when the token has wildcards (even if it looks like a list).
    if any(ch in spec for ch in ("*", "?", "[")):
      matches = sorted(glob.glob(spec))
      if not matches:
        raise FileNotFoundError("glob {!r} matched no files".format(spec))
      root_matches = [m for m in matches if _is_root_file(m)]
      if not root_matches:
        raise FileNotFoundError(
          "glob {!r} matched files but none end in .root".format(spec)
        )
      files.extend(_normalize_path(m) for m in root_matches)
      continue

    # root:// URLs are always treated as a single ROOT source.
    if spec.startswith("root://"):
      files.append(spec)
      continue

    path = _normalize_path(spec)
    if _is_root_file(path):
      if not os.path.isfile(path):
        raise FileNotFoundError("input ROOT file not found: {!r}".format(path))
      files.append(path)
      continue

    if os.path.isfile(path):
      files.extend(_read_filelist(path))
      continue

    raise FileNotFoundError(
      "input {!r} is neither a .root file, an existing filelist, nor a glob".format(
        spec
      )
    )

  # Preserve order; drop exact duplicates (common when mixing globs + lists).
  seen: set[str] = set()
  unique: list[str] = []
  for f in files:
    if f not in seen:
      seen.add(f)
      unique.append(f)
  if not unique:
    raise FileNotFoundError("no input ROOT files resolved from {!r}".format(specs))
  return unique


def _discover_tree(fkeys: list[str], treename: str):
  """Pick tree path + layout from open-file keys."""
  for candidate in (treename, "displacedV0Ntuple/events", "events"):
    if candidate in fkeys:
      return candidate, "displacedv0"
  if "blackJackAndHookers" in fkeys:
    return "blackJackAndHookers/blackJackAndHookersTree", "upstream"
  raise KeyError(
    "Neither DisplacedV0 tree {!r} (or displacedV0Ntuple/events / events) "
    "nor upstream blackJackAndHookers found. Keys: {}".format(treename, fkeys)
  )


def _accumulate_hist(acc, hist):
  """Sum TH1-like objects across input files (MC counters).

  Uproot TH1 models do not implement ``+``; convert via ``to_numpy`` and sum
  bin contents (no extra hist/boost-histogram dependency).
  """
  if hist is None:
    return acc
  values, edges = hist.to_numpy(flow=False)
  values = np.asarray(values, dtype=np.float64)
  edges = np.asarray(edges, dtype=np.float64)
  # Preserve underflow/overflow when present (values(flow=True)).
  try:
    flow = np.asarray(hist.values(flow=True), dtype=np.float64)
    under = float(flow[0])
    over = float(flow[-1])
  except Exception:
    under = 0.0
    over = 0.0
  if acc is None:
    return {
      "values": values.copy(),
      "edges": edges,
      "underflow": under,
      "overflow": over,
    }
  if acc["values"].shape != values.shape or not np.allclose(acc["edges"], edges):
    raise ValueError("histogram binning mismatch across input files")
  acc["values"] = acc["values"] + values
  acc["underflow"] += under
  acc["overflow"] += over
  return acc


def _hist_for_write(acc):
  """Convert accumulated hist dict to an uproot-writable (counts, edges) pair.

  Interior bins are written as-is. Under/overflow are summed in ``acc`` for
  bookkeeping; embedding them needs a full TH1 writer and is left aside so
  bin contents stay correct without hist/boost-histogram.
  """
  if acc is None:
    return None
  return (acc["values"], acc["edges"])


def _merge_tree_dicts(chunks: list[dict]) -> dict:
  """Concatenate per-chunk output tree dicts (awkward / numpy columns)."""
  chunks = [c for c in chunks if c]
  if not chunks:
    return {}
  keys = list(chunks[0].keys())
  out = {}
  for key in keys:
    parts = [c[key] for c in chunks if key in c]
    if not parts:
      continue
    try:
      out[key] = ak.concatenate(parts)
    except Exception:
      out[key] = np.concatenate([np.asarray(p) for p in parts])
  return out


def build_selected_trees(
  branches,
  layout: str,
  selection_name: str,
  apply_dy: bool,
  deepjet_wp: float | None,
  isdata: bool,
  verbose: bool = True,
):
  """Run rename / DY / AN §6 selection and fill output tree dicts for one chunk."""
  # --- normalize event / weight / ID branch names to a common internal schema ---
  if layout == "displacedv0":
    rename = {}
    if "run" in branches.fields:
      rename["run"] = "_runNb"
    if "luminosityBlock" in branches.fields:
      rename["luminosityBlock"] = "_lumiBlock"
    if "event" in branches.fields:
      rename["event"] = "_eventNb"
    for src, dst in rename.items():
      branches[dst] = branches[src]

    if "genWeight" in branches.fields:
      branches["_weight"] = branches["genWeight"]
      isdata = False
    elif "_weight" not in branches.fields:
      isdata = True
    if "Pileup_nTrue" in branches.fields:
      branches["_nTrueInt"] = branches["Pileup_nTrue"]

  # DisplacedV0 already stores _V0RPVSig / _V0RBSSig (new naming)
  vnametype = "new"
  if "_V0RPVSig" not in branches.fields and "_V0RSigPV" in branches.fields:
    vnametype = "old"
  if vnametype == "new":
    rpvsigkey = "RPVSig"
    rbssigkey = "RBSSig"
  else:
    rpvsigkey = "RSigPV"
    rbssigkey = "RSigBS"
    branches["_V0NormChi2Pos"] = branches["_V0PtPos"] * 0.0
    branches["_V0NormChi2Neg"] = branches["_V0PtNeg"] * 0.0

  n_before = len(branches)
  if apply_dy and layout == "displacedv0":
    if verbose:
      print("Applying AN §5 DY selection on DisplacedV0 branches...")
    evmask, mll = dy_event_mask(branches, deepjet_wp=deepjet_wp)
    n_after = int(np.sum(evmask))
    if verbose:
      print("  Events before: {}".format(n_before))
      print("  Events after:  {}".format(n_after))
    branches = branches[evmask]
    mll = mll[evmask]
  elif layout == "displacedv0" and "nMuon" in branches.fields:
    mll = _dimuon_mass(branches)
    n_after = n_before
  else:
    mll = branches["_nimloth_Mll"] if "_nimloth_Mll" in branches.fields else None
    n_after = n_before

  if layout == "displacedv0":
    branches["_nimloth_Mll"] = mll if mll is not None else ak.zeros_like(branches["_runNb"])
    branches["_nimloth_nJets"] = count_jets(branches)
    if "Muon_pt" in branches.fields:
      branches["_celeborn_lPt"] = branches["Muon_pt"]
      branches["_celeborn_lEta"] = branches["Muon_eta"]
      branches["_celeborn_lPhi"] = branches["Muon_phi"]
      branches["_celeborn_lCharge"] = branches["Muon_charge"]

  ksmask = branches["_V0Type"] == 1
  lmask = (branches["_V0Type"] == 2) | (branches["_V0Type"] == 3)

  if verbose:
    print("Constructing auxiliary variables")
  cospointingPV = cospointing(branches, reference="primaryVertex")
  cospointingBS = cospointing(branches, reference="beamSpot")
  ptSum = branches["_V0PtPos"] + branches["_V0PtNeg"]

  has_daughter_angles = all(
    k in branches.fields
    for k in ("_V0EtaPos", "_V0EtaNeg", "_V0PhiPos", "_V0PhiNeg")
  )
  if has_daughter_angles:
    posp4 = vector.zip(
      {
        "pt": branches["_V0PtPos"],
        "eta": branches["_V0EtaPos"],
        "phi": branches["_V0PhiPos"],
        "mass": 0.0,
      }
    )
    negp4 = vector.zip(
      {
        "pt": branches["_V0PtNeg"],
        "eta": branches["_V0EtaNeg"],
        "phi": branches["_V0PhiNeg"],
        "mass": 0.0,
      }
    )
    trackdR = posp4.deltaR(negp4)
  else:
    trackdR = None

  if verbose:
    print("Performing selections")
  extra = {"cospointingPV": cospointingPV, "cospointingBS": cospointingBS}
  (selmask, allmasks) = selection(branches, selection_name, extra=extra, cutflow=True)
  if verbose:
    print("Selection summary:")
    print("  Before selection: {} candidates".format(ak.count(selmask)))
    for maskname, mask in allmasks.items():
      print("  - {}: {}".format(maskname, np.sum(mask)))
    print("  -> Candidates passing all selections: {}".format(np.sum(selmask)))

  nimloth = {}
  nimlothvars = [
    "_nimloth_Mll",
    "_nimloth_nJets",
    "_beamSpotX",
    "_beamSpotY",
    "_beamSpotZ",
    "_primaryVertexX",
    "_primaryVertexY",
    "_primaryVertexZ",
    "_runNb",
    "_lumiBlock",
    "_eventNb",
  ]
  if not isdata:
    nimlothvars += ["_weight", "_nTrueInt"]
  for var in nimlothvars:
    if var in branches.fields:
      nimloth[var] = branches[var]

  celeborn = {}
  if "_celeborn_lPt" in branches.fields:
    for var in (
      "_celeborn_lPt",
      "_celeborn_lEta",
      "_celeborn_lPhi",
      "_celeborn_lCharge",
    ):
      celeborn[var] = ak.flatten(branches[var])
    nlep = ak.num(branches["_celeborn_lPt"], axis=1)
    celeborn["_runNb"] = np.repeat(ak.to_numpy(branches["_runNb"]), ak.to_numpy(nlep))
    celeborn["_lumiBlock"] = np.repeat(
      ak.to_numpy(branches["_lumiBlock"]), ak.to_numpy(nlep)
    )
    celeborn["_eventNb"] = np.repeat(ak.to_numpy(branches["_eventNb"]), ak.to_numpy(nlep))
    if not isdata:
      celeborn["_weight"] = np.repeat(ak.to_numpy(branches["_weight"]), ak.to_numpy(nlep))
      if "_nTrueInt" in branches.fields:
        celeborn["_nTrueInt"] = np.repeat(
          ak.to_numpy(branches["_nTrueInt"]), ak.to_numpy(nlep)
        )

  def fill_v0_tree(mask):
    out = {}
    out["_mass"] = ak.flatten(branches["_V0InvMass"][mask])
    out["_vertexX"] = ak.flatten(branches["_V0X"][mask])
    out["_vertexY"] = ak.flatten(branches["_V0Y"][mask])
    out["_vertexZ"] = ak.flatten(branches["_V0Z"][mask])
    out["_RPV"] = ak.flatten(branches["_V0RPV"][mask])
    if "_V0RBS" in branches.fields:
      out["_RBS"] = ak.flatten(branches["_V0RBS"][mask])
    out["_RPVSig"] = ak.flatten(branches["_V0" + rpvsigkey][mask])
    if "_V0" + rbssigkey in branches.fields:
      out["_RBSSig"] = ak.flatten(branches["_V0" + rbssigkey][mask])
    out["_pt"] = ak.flatten(branches["_V0Pt"][mask])
    out["_ptSum"] = ak.flatten(ptSum[mask])
    if "_V0Eta" in branches.fields:
      out["_eta"] = ak.flatten(branches["_V0Eta"][mask])
    if "_V0Phi" in branches.fields:
      out["_phi"] = ak.flatten(branches["_V0Phi"][mask])
    out["_nHitsPos"] = ak.flatten(branches["_V0NHitsPos"][mask])
    out["_nHitsNeg"] = ak.flatten(branches["_V0NHitsNeg"][mask])
    out["_ptPos"] = ak.flatten(branches["_V0PtPos"][mask])
    out["_ptNeg"] = ak.flatten(branches["_V0PtNeg"][mask])
    out["_normChi2Pos"] = ak.flatten(branches["_V0NormChi2Pos"][mask])
    out["_normChi2Neg"] = ak.flatten(branches["_V0NormChi2Neg"][mask])
    flat_ones = ak.flatten(branches["_V0Pt"][mask] > -1.0)
    nan_hook = ak.full_like(ak.values_astype(flat_ones, np.float64), np.nan)
    if trackdR is not None:
      out["_trackdR"] = ak.flatten(trackdR[mask])
    else:
      out["_trackdR"] = nan_hook
    if "_V0D0Pos" in branches.fields:
      out["_d0Pos"] = ak.flatten(branches["_V0D0Pos"][mask])
      out["_dzPos"] = ak.flatten(branches["_V0DzPos"][mask])
      out["_d0Neg"] = ak.flatten(branches["_V0D0Neg"][mask])
      out["_dzNeg"] = ak.flatten(branches["_V0DzNeg"][mask])
    if "_V0IsoPos" in branches.fields:
      out["_isoPos"] = ak.flatten(branches["_V0IsoPos"][mask])
      out["_isoNeg"] = ak.flatten(branches["_V0IsoNeg"][mask])
    if (
      "_V0NearestChgDRPos" in branches.fields
      and "_V0NearestChgStatusPos" in branches.fields
    ):
      st_pos = ak.flatten(branches["_V0NearestChgStatusPos"][mask])
      st_neg = ak.flatten(branches["_V0NearestChgStatusNeg"][mask])
      dr_pos = ak.flatten(branches["_V0NearestChgDRPos"][mask])
      dr_neg = ak.flatten(branches["_V0NearestChgDRNeg"][mask])
      out["_trkNearestJetDistPos"] = ak.where(st_pos > 0, dr_pos, nan_hook)
      out["_trkNearestJetDistNeg"] = ak.where(st_neg > 0, dr_neg, nan_hook)
    else:
      out["_trkNearestJetDistPos"] = nan_hook
      out["_trkNearestJetDistNeg"] = nan_hook
    ones = branches["_V0Pt"][mask] > -1.0
    out["_runNb"] = ak.flatten(ones * branches["_runNb"])
    out["_lumiBlock"] = ak.flatten(ones * branches["_lumiBlock"])
    out["_eventNb"] = ak.flatten(ones * branches["_eventNb"])
    if not isdata:
      out["_weight"] = ak.flatten(ones * branches["_weight"])
      if "_nTrueInt" in branches.fields:
        out["_nTrueInt"] = ak.flatten(ones * branches["_nTrueInt"])
    return out

  laurelinmask = ksmask & selmask
  telperionmask = lmask & selmask
  n_ks = int(np.sum(laurelinmask))
  n_lam = int(np.sum(telperionmask))
  if verbose:
    print("Found {} K0s candidates".format(n_ks))
    print("Found {} Lambda candidates".format(n_lam))

  return {
    "nimloth": nimloth,
    "celeborn": celeborn,
    "laurelin": fill_v0_tree(laurelinmask),
    "telperion": fill_v0_tree(telperionmask),
    "isdata": isdata,
    "n_before": n_before,
    "n_after": n_after,
    "n_ks": n_ks,
    "n_lam": n_lam,
  }


def _dimuon_mass(branches):
  """Dimuon invariant mass: prefer Sol ``Dimuon_mass``, else from Muon_*."""
  if "Dimuon_mass" in branches.fields:
    return ak.fill_none(branches["Dimuon_mass"], 0.0)
  pt = ak.pad_none(branches["Muon_pt"], 2, axis=1)
  eta = ak.pad_none(branches["Muon_eta"], 2, axis=1)
  phi = ak.pad_none(branches["Muon_phi"], 2, axis=1)
  if "Muon_mass" in branches.fields:
    mass = ak.pad_none(branches["Muon_mass"], 2, axis=1)
  else:
    mass = ak.pad_none(ak.zeros_like(branches["Muon_pt"]) + 0.105658, 2, axis=1)
  mu1 = vector.zip(
    {"pt": pt[:, 0], "eta": eta[:, 0], "phi": phi[:, 0], "mass": mass[:, 0]}
  )
  mu2 = vector.zip(
    {"pt": pt[:, 1], "eta": eta[:, 1], "phi": phi[:, 1], "mass": mass[:, 1]}
  )
  return ak.fill_none((mu1 + mu2).mass, 0.0)


def dy_event_mask(branches, deepjet_wp: float | None):
  """AN §5 DY reference selection on DisplacedV0 branches."""
  n = len(branches)
  mask = np.ones(n, dtype=bool)
  mll = np.zeros(n)

  if "passDimuonHLT" in branches.fields:
    mask = mask & ak.to_numpy(branches["passDimuonHLT"])

  if "nMuon" not in branches.fields:
    return mask, mll

  nmu = branches["nMuon"]
  pt = branches["Muon_pt"]
  medium = branches["Muon_mediumId"]
  charge = ak.pad_none(branches["Muon_charge"], 2, axis=1)
  eta = branches["Muon_eta"]

  exactly2 = ak.to_numpy(nmu == 2)
  mask = mask & exactly2

  # medium ID on both; leading/trailing pT > 30/25; |eta|<2.4
  both_medium = ak.to_numpy((ak.num(medium, axis=1) == 2) & ak.all(medium, axis=1))
  ptsorted = ak.pad_none(ak.sort(pt, axis=1, ascending=False), 2, axis=1)
  leading_ok = ak.to_numpy(ak.fill_none(ptsorted[:, 0] > 30.0, False))
  trailing_ok = ak.to_numpy(ak.fill_none(ptsorted[:, 1] > 25.0, False))
  eta_ok = ak.to_numpy(ak.all(np.abs(eta) < 2.4, axis=1) & (ak.num(eta, axis=1) == 2))
  mask = mask & both_medium & leading_ok & trailing_ok & eta_ok

  mll = _dimuon_mass(branches)
  opp = ak.to_numpy(ak.fill_none(charge[:, 0] * charge[:, 1] < 0, False))
  mass_ok = ak.to_numpy(np.abs(mll - MZ) < 10.0)
  mask = mask & opp & mass_ok

  # loose DeepJet b-veto: prefer CDTE-31 scalar passDeepJetLooseVeto; fall back
  # to Jet_* arrays (pre–CDTE-31 ntuples). WP TBD → placeholder when arrays used.
  if deepjet_wp is not None:
    if "passDeepJetLooseVeto" in branches.fields:
      mask = mask & ak.to_numpy(branches["passDeepJetLooseVeto"])
    elif "Jet_btagDeepFlavB" in branches.fields:
      jpt = branches["Jet_pt"]
      jeta = branches["Jet_eta"]
      jbtag = branches["Jet_btagDeepFlavB"]
      jet_sel = (jpt > 30.0) & (np.abs(jeta) < 2.5) & (jbtag > deepjet_wp)
      if "Jet_jetId" in branches.fields:
        jet_sel = jet_sel & (branches["Jet_jetId"] >= 2)
      has_btag = ak.to_numpy(ak.any(jet_sel, axis=1))
      mask = mask & (~has_btag)

  return mask, mll


def count_jets(branches):
  # Prefer CDTE-31 nJetSel scalar; else count from Jet_* arrays (legacy).
  if "nJetSel" in branches.fields:
    return ak.values_astype(branches["nJetSel"], np.int32)
  if "nJet" not in branches.fields:
    ref = branches["run"] if "run" in branches.fields else branches["_runNb"]
    return ak.zeros_like(ref)
  # Prefer ak.sum on the boolean mask so we do not flatten RegularArray / 2D
  # Jet_* branches (ak.num(jpt[mask], axis=1) fails once boolean indexing
  # collapses the jet axis).
  jpt = branches["Jet_pt"]
  jeta = branches["Jet_eta"]
  jet_sel = (jpt > 30.0) & (np.abs(jeta) < 2.5)
  if "Jet_jetId" in branches.fields:
    jet_sel = jet_sel & (branches["Jet_jetId"] >= 2)
  return ak.values_astype(ak.sum(jet_sel, axis=-1), np.int32)


if __name__ == "__main__":
  sys.stderr.write("###starting###\n")

  parser = argparse.ArgumentParser(
    description=(
      "Perform V0 candidate selection (Run3). "
      "Accepts a single ROOT file, a text filelist, multiple files, and/or globs "
      "via -i (file-by-file / TChain-like; no hadd of CRAB shards required)."
    )
  )
  parser.add_argument(
    "-i",
    "--inputfile",
    required=True,
    nargs="+",
    metavar="PATH",
    help=(
      "Input ROOT file(s), glob(s), and/or a text filelist "
      "(one .root path per line; # comments / blank lines skipped). "
      "Files are processed one at a time (bounded RAM) without merging "
      "inputs on disk. Example: -i dy_crab_files.txt"
    ),
  )
  parser.add_argument("-o", "--outputfile", required=True, type=os.path.abspath)
  parser.add_argument("-s", "--selection", default="legacy")
  parser.add_argument("-n", "--nevents", default=-1, type=int)
  parser.add_argument(
    "--transfer",
    default=False,
    action="store_true",
    help="Copy a single local input ROOT to $TMPDIR before reading (multi-file unsupported)",
  )
  parser.add_argument(
    "--treename",
    default="displacedV0Ntuple/events",
    help="DisplacedV0 tree path (TFileService: displacedV0Ntuple/events)",
  )
  parser.add_argument(
    "--apply-dy-selection",
    default=False,
    action="store_true",
    help="Apply AN §5 DY selection (passDimuonHLT, 2 medium muons, mZ window, DeepJet veto)",
  )
  parser.add_argument(
    "--deepjet-loose-wp",
    type=float,
    default=DEEPJET_LOOSE_WP_PLACEHOLDER,
    help="Loose DeepJet WP for b-veto (placeholder until BTV 2024 JSON frozen)",
  )
  parser.add_argument(
    "--no-bveto",
    default=False,
    action="store_true",
    help="Skip DeepJet b-veto even when --apply-dy-selection is set",
  )
  args = parser.parse_args()

  if args.selection not in ("legacy",):
    raise Exception("ERROR: selection " + args.selection + " not recognized.")

  input_files = collect_input_files(args.inputfile)
  print("Resolved {} input file(s)".format(len(input_files)))
  for _ifp in input_files[:5]:
    print("  {}".format(_ifp))
  if len(input_files) > 5:
    print("  ... ({} more)".format(len(input_files) - 5))

  if args.transfer:
    if len(input_files) != 1:
      raise RuntimeError(
        "--transfer only supports a single local ROOT file "
        "({} inputs resolved)".format(len(input_files))
      )
    if input_files[0].startswith("root://"):
      raise RuntimeError("--transfer does not support root:// URLs")
    tmpdir = os.environ.get("TMPDIR", "/tmp")
    tmpfile = os.path.join(tmpdir, input_files[0].strip("/").replace("/", "_"))
    cmd = "cp {} {}".format(input_files[0], tmpfile)
    print("Transfering input file to {}...".format(tmpdir))
    print(cmd)
    os.system(cmd)
    input_files = [tmpfile]
    origoutputfile = args.outputfile
    args.outputfile = tmpfile.replace(".root", "_out.root")

  # Discover tree/layout from the first file; process shards one-by-one so
  # EOS CRAB outputs need not be hadd'ed and peak RAM stays near one file.
  with uproot.open(input_files[0]) as f0:
    fkeys0 = [key.split(";")[0] for key in f0.keys()]
    resolved_treename, layout = _discover_tree(fkeys0, args.treename)

  isdata = False
  hcounter = None
  ntrueint_hist = None
  total_entries = 0
  file_entries: list[int] = []
  for fpath in input_files:
    with uproot.open(fpath) as f:
      fkeys = [key.split(";")[0] for key in f.keys()]
      try:
        this_tree, this_layout = _discover_tree(fkeys, args.treename)
      except KeyError as exc:
        raise KeyError("In file {}: {}".format(fpath, exc)) from exc
      if this_layout != layout or this_tree != resolved_treename:
        raise RuntimeError(
          "mixed tree layouts/paths across inputs: "
          "{!r} ({}) vs first-file {!r} ({}) in {}".format(
            this_tree, this_layout, resolved_treename, layout, fpath
          )
        )
      nent = int(f[resolved_treename].num_entries)
      file_entries.append(nent)
      total_entries += nent

      if layout == "upstream":
        hcounterkey = "blackJackAndHookers/hCounter"
        ntrueintkey = "blackJackAndHookers/nTrueInteractions"
        if hcounterkey in fkeys and ntrueintkey in fkeys:
          hcounter = _accumulate_hist(hcounter, f[hcounterkey])
          ntrueint_hist = _accumulate_hist(ntrueint_hist, f[ntrueintkey])
      else:
        if "hCounter" in fkeys:
          hcounter = _accumulate_hist(hcounter, f["hCounter"])
        if "nTrueInteractions" in fkeys:
          ntrueint_hist = _accumulate_hist(ntrueint_hist, f["nTrueInteractions"])

  if layout == "upstream" and (hcounter is None or ntrueint_hist is None):
    print("No valid hCounter or nTrueInt found; assuming data...")
    isdata = True
    hcounter = None
    ntrueint_hist = None

  n_to_read = total_entries if args.nevents <= 0 else min(args.nevents, total_entries)
  print(
    "Tree is found to have {} entries across {} file(s) of which {} will be read".format(
      total_entries, len(input_files), n_to_read
    )
  )
  print(
    "Reading branches file-by-file (layout={}, tree={})".format(
      layout, resolved_treename
    )
  )
  sys.stdout.flush()
  sys.stderr.flush()

  deepjet_wp = None if args.no_bveto else args.deepjet_loose_wp
  remaining = None if args.nevents <= 0 else int(args.nevents)
  nimloth_chunks: list[dict] = []
  celeborn_chunks: list[dict] = []
  laurelin_chunks: list[dict] = []
  telperion_chunks: list[dict] = []
  sum_before = 0
  sum_after = 0
  sum_ks = 0
  sum_lam = 0

  for ifile, fpath in enumerate(input_files):
    if remaining is not None and remaining <= 0:
      break
    nent = file_entries[ifile]
    stop = nent if remaining is None else min(remaining, nent)
    verbose = len(input_files) == 1 or ifile == 0
    print(
      "File {}/{}: {} (reading {}/{})".format(
        ifile + 1, len(input_files), fpath, stop, nent
      )
    )
    sys.stdout.flush()
    with uproot.open(fpath) as f:
      branches = f[resolved_treename].arrays(
        entry_stop=None if stop >= nent else stop
      )
    if remaining is not None:
      remaining -= stop

    result = build_selected_trees(
      branches,
      layout=layout,
      selection_name=args.selection,
      apply_dy=args.apply_dy_selection,
      deepjet_wp=deepjet_wp,
      isdata=isdata,
      verbose=verbose,
    )
    isdata = result["isdata"]
    sum_before += result["n_before"]
    sum_after += result["n_after"]
    sum_ks += result["n_ks"]
    sum_lam += result["n_lam"]
    if not verbose:
      print(
        "  DY {} -> {}; Ks {}; Lambda {}".format(
          result["n_before"], result["n_after"], result["n_ks"], result["n_lam"]
        )
      )
    nimloth_chunks.append(result["nimloth"])
    celeborn_chunks.append(result["celeborn"])
    laurelin_chunks.append(result["laurelin"])
    telperion_chunks.append(result["telperion"])
    # Drop raw arrays before the next shard.
    del branches, result

  if len(input_files) > 1:
    print(
      "Totals: DY {} -> {}; Ks {}; Lambda {}".format(
        sum_before, sum_after, sum_ks, sum_lam
      )
    )

  print("Writing trees to output file")
  with uproot.recreate(args.outputfile) as f:
    f["nimloth"] = _merge_tree_dicts(nimloth_chunks)
    f["celeborn"] = _merge_tree_dicts(celeborn_chunks)
    f["laurelin"] = _merge_tree_dicts(laurelin_chunks)
    f["telperion"] = _merge_tree_dicts(telperion_chunks)
    hcounter_out = _hist_for_write(hcounter)
    ntrueint_out = _hist_for_write(ntrueint_hist)
    if hcounter_out is not None:
      f["hCounter"] = hcounter_out
    if ntrueint_out is not None:
      f["nTrueInteractions"] = ntrueint_out

  if args.transfer:
    cmd = "mv {} {}".format(args.outputfile, origoutputfile)
    print("Transfering output file...")
    print(cmd)
    os.system(cmd)
    cmd = "rm {}".format(tmpfile)
    print("Removing temporary file {}".format(tmpfile))
    os.system(cmd)

  sys.stderr.write("###done###\n")
