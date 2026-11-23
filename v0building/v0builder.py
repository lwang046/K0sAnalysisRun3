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

from __future__ import annotations

import argparse
import os
import sys

import awkward as ak
import numpy as np
import uproot
import vector

from v0selections import cospointing, selection

MZ = 91.1876
DEEPJET_LOOSE_WP_PLACEHOLDER = 0.0494  # TBD: freeze from BTV 2024 JSON


def _dimuon_mass(branches):
  """Dimuon invariant mass from Muon_* branches (padded; invalid → 0)."""
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

  # loose DeepJet b-veto (Jet_btagDeepFlavB); WP TBD → placeholder
  if deepjet_wp is not None and "Jet_btagDeepFlavB" in branches.fields:
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
  if "nJet" not in branches.fields:
    return ak.zeros_like(branches["run"])
  jpt = branches["Jet_pt"]
  jeta = branches["Jet_eta"]
  jet_sel = (jpt > 30.0) & (np.abs(jeta) < 2.5)
  if "Jet_jetId" in branches.fields:
    jet_sel = jet_sel & (branches["Jet_jetId"] >= 2)
  return ak.num(jpt[jet_sel], axis=1)


if __name__ == "__main__":
  sys.stderr.write("###starting###\n")

  parser = argparse.ArgumentParser(description="Perform V0 candidate selection (Run3)")
  parser.add_argument("-i", "--inputfile", required=True, type=os.path.abspath)
  parser.add_argument("-o", "--outputfile", required=True, type=os.path.abspath)
  parser.add_argument("-s", "--selection", default="legacy")
  parser.add_argument("-n", "--nevents", default=-1, type=int)
  parser.add_argument("--transfer", default=False, action="store_true")
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

  if args.transfer:
    tmpdir = os.environ.get("TMPDIR", "/tmp")
    tmpfile = os.path.join(tmpdir, args.inputfile.strip("/").replace("/", "_"))
    cmd = "cp {} {}".format(args.inputfile, tmpfile)
    print("Transfering input file to {}...".format(tmpdir))
    print(cmd)
    os.system(cmd)
    args.inputfile = tmpfile
    origoutputfile = args.outputfile
    args.outputfile = tmpfile.replace(".root", "_out.root")

  with uproot.open(args.inputfile) as f:
    fkeys = [key.split(";")[0] for key in f.keys()]

    # DisplacedV0: TFileService nests the tree under the module label.
    # Fall back to a bare 'events' tree, then upstream heavyNeutrino layout.
    tree = None
    layout = None
    for candidate in (args.treename, "displacedV0Ntuple/events", "events"):
      if candidate in fkeys:
        tree = f[candidate]
        layout = "displacedv0"
        break
    if tree is None and "blackJackAndHookers" in fkeys:
      tree = f["blackJackAndHookers"]["blackJackAndHookersTree"]
      layout = "upstream"
    if tree is None:
      raise KeyError(
        "Neither DisplacedV0 tree {!r} (or displacedV0Ntuple/events / events) "
        "nor upstream blackJackAndHookers found. Keys: {}".format(
          args.treename, fkeys
        )
      )

    isdata = False
    hcounter = None
    ntrueint_hist = None
    if layout == "upstream":
      hcounterkey = "blackJackAndHookers/hCounter"
      ntrueintkey = "blackJackAndHookers/nTrueInteractions"
      if hcounterkey not in fkeys or ntrueintkey not in fkeys:
        print("No valid hCounter or nTrueInt found; assuming data...")
        isdata = True
      else:
        hcounter = f[hcounterkey]
        ntrueint_hist = f[ntrueintkey]
    else:
      # DisplacedV0: no hCounter yet; detect MC via genWeight presence later
      if "hCounter" in fkeys:
        hcounter = f["hCounter"]
      if "nTrueInteractions" in fkeys:
        ntrueint_hist = f["nTrueInteractions"]

    entry_stop = None
    if args.nevents > 0 and args.nevents < tree.num_entries:
      entry_stop = args.nevents
    msg = "Tree is found to have {} entries".format(tree.num_entries)
    msg += " of which {} will be read".format(
      entry_stop if entry_stop is not None else tree.num_entries
    )
    print(msg)
    print("Reading branches (layout={})".format(layout))
    sys.stdout.flush()
    sys.stderr.flush()
    branches = tree.arrays(entry_stop=entry_stop)

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

  # Optional AN §5 DY selection (when skimming/ not yet applied)
  deepjet_wp = None if args.no_bveto else args.deepjet_loose_wp
  if args.apply_dy_selection and layout == "displacedv0":
    print("Applying AN §5 DY selection on DisplacedV0 branches...")
    evmask, mll = dy_event_mask(branches, deepjet_wp=deepjet_wp)
    print("  Events before: {}".format(len(evmask)))
    print("  Events after:  {}".format(np.sum(evmask)))
    branches = branches[evmask]
    mll = mll[evmask]
  elif layout == "displacedv0" and "nMuon" in branches.fields:
    # still compute mll for control tree even if selection deferred to skim
    mll = _dimuon_mass(branches)
  else:
    mll = branches["_nimloth_Mll"] if "_nimloth_Mll" in branches.fields else None

  # Build / map control quantities for nimloth / celeborn
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

  print("Constructing auxiliary variables")
  cospointingPV = cospointing(branches, reference="primaryVertex")
  cospointingBS = cospointing(branches, reference="beamSpot")
  ptSum = branches["_V0PtPos"] + branches["_V0PtNeg"]

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

  print("Performing selections")
  extra = {"cospointingPV": cospointingPV, "cospointingBS": cospointingBS}
  (selmask, allmasks) = selection(branches, args.selection, extra=extra, cutflow=True)
  print("Selection summary:")
  print("  Before selection: {} candidates".format(ak.count(selmask)))
  for maskname, mask in allmasks.items():
    print("  - {}: {}".format(maskname, np.sum(mask)))
  print("  -> Candidates passing all selections: {}".format(np.sum(selmask)))

  print("Filling per-event tree")
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

  print("Filling per-lepton tree")
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
    out["_RBS"] = ak.flatten(branches["_V0RBS"][mask])
    out["_RPVSig"] = ak.flatten(branches["_V0" + rpvsigkey][mask])
    out["_RBSSig"] = ak.flatten(branches["_V0" + rbssigkey][mask])
    out["_pt"] = ak.flatten(branches["_V0Pt"][mask])
    out["_ptSum"] = ak.flatten(ptSum[mask])
    out["_eta"] = ak.flatten(branches["_V0Eta"][mask])
    out["_phi"] = ak.flatten(branches["_V0Phi"][mask])
    out["_nHitsPos"] = ak.flatten(branches["_V0NHitsPos"][mask])
    out["_nHitsNeg"] = ak.flatten(branches["_V0NHitsNeg"][mask])
    out["_ptPos"] = ak.flatten(branches["_V0PtPos"][mask])
    out["_ptNeg"] = ak.flatten(branches["_V0PtNeg"][mask])
    out["_normChi2Pos"] = ak.flatten(branches["_V0NormChi2Pos"][mask])
    out["_normChi2Neg"] = ak.flatten(branches["_V0NormChi2Neg"][mask])
    out["_trackdR"] = ak.flatten(trackdR[mask])
    ones = branches["_V0Pt"][mask] > -1.0
    out["_runNb"] = ak.flatten(ones * branches["_runNb"])
    out["_lumiBlock"] = ak.flatten(ones * branches["_lumiBlock"])
    out["_eventNb"] = ak.flatten(ones * branches["_eventNb"])
    if not isdata:
      out["_weight"] = ak.flatten(ones * branches["_weight"])
      if "_nTrueInt" in branches.fields:
        out["_nTrueInt"] = ak.flatten(ones * branches["_nTrueInt"])
    return out

  print("Filling K0s tree")
  laurelinmask = ksmask & selmask
  print("Found {} K0s candidates".format(np.sum(laurelinmask)))
  laurelin = fill_v0_tree(laurelinmask)

  print("Filling Lambda tree")
  telperionmask = lmask & selmask
  print("Found {} Lambda candidates".format(np.sum(telperionmask)))
  telperion = fill_v0_tree(telperionmask)

  print("Writing trees to output file")
  with uproot.recreate(args.outputfile) as f:
    f["nimloth"] = nimloth
    f["celeborn"] = celeborn
    f["laurelin"] = laurelin
    f["telperion"] = telperion
    if hcounter is not None:
      f["hCounter"] = hcounter
    if ntrueint_hist is not None:
      f["nTrueInteractions"] = ntrueint_hist

  if args.transfer:
    cmd = "mv {} {}".format(args.outputfile, origoutputfile)
    print("Transfering output file...")
    print(cmd)
    os.system(cmd)
    cmd = "rm {}".format(tmpfile)
    print("Removing temporary file {}".format(tmpfile))
    os.system(cmd)

  sys.stderr.write("###done###\n")
