# `example_input_run2024d.json` — absolute-norm notes

Fill units: **`luminosity` in pb⁻¹** (`/fb × 1000`), **`xsection` in pb**.
Weight formula: `w = genWeight / sumweights × σ × L`.

## Luminosity (Run2024D) — choose one

From lxplus brilcalc **2026-11-27** (Project store `internal/cdte34-norm-prep-findings.md`):

| Choice | /fb | pb⁻¹ in JSON | Source |
| --- | ---: | ---: | --- |
| **Muon cert (default in JSON)** | **7.703298913** | **7703.3** | `2024D_Muon.json` × `normtag_BRIL` |
| Golden × D run bounds | **7.913979054** | **7914.0** | full Golden + `--begin 380255 --end 380947` × `normtag_BRIL` (matches CRAB golden mask era cut) |

Freeze after user/coord decision. CLI override without editing JSON:

```bash
# Muon (default)
python3 mcvsdata_fill.py ... --data-lumi 7703.3 --mc-lumi 7703.3
# Golden×D
python3 mcvsdata_fill.py ... --data-lumi 7914.0 --mc-lumi 7914.0
```

## DY cross section — TODO-VERIFY

JSON placeholder **2094.2 pb** = MATRIX NNLO per lepton flavor @ 13.6 TeV
(`cmsdb` `dy_m50toinf` / `n_leps`). **Not** GenXSec/XSDB for
`DYto2Mu-2Jets_Bin-MLL-50_…v2-v6`. Override when measured:

```bash
python3 mcvsdata_fill.py ... --mc-xsection <XSDB_or_genXsec_pb>
```

## Sum of weights (hCounter)

Existing slim CRAB ntuples have **no** `hCounter` (Path `DimuonPreFilter` on;
post-filter `ΣgenWeight` ≠ full-sample Σw). Options:

1. **External Σw** (refill now): `--mc-sumweights <full_sample_sumw>` or JSON key `"sumweights"`.
2. **Future CRAB:** `GenWeightCounter` on MC Path *before* the filter writes `hCounter`; v0builder propagates it.
3. Leave unset → fill warns and uses `sumweights=1` (OK for `--normmode range` shape of \(C\), wrong for absolute σ×L).

```bash
python3 mcvsdata_fill.py -i input_run2024d_afs.json ... \
  --mc-sumweights <FULL_SAMPLE_SUMW> \
  --mc-xsection <PB> \
  --data-lumi 7703.3 --mc-lumi 7703.3
```
