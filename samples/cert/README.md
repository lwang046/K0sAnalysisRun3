# Certification / luminosity / PU (2024)

Do not commit large JSON blobs here unless needed for a frozen reproducibility tag.
Record the **exact filename + run range + download date** in `conditions.md`
when freezing an era.

## First era (Run2024D)

Use the full Collisions24 golden JSON and restrict CRAB / brilcalc to the
Run2024D run range after looking up era boundaries (OMS / DQM / PdmV).

| Item | Value |
| --- | --- |
| First analysis era | **Run2024D** |
| Golden JSON (stub) | `Cert_Collisions2024_378981_386951_Golden.json` |
| CRAB `lumiMask` | EOS path below (or a local copy) |
| Era run bounds | **TODO-VERIFY** on OMS / golden JSON before brilcalc |

## Golden / muon JSON (Collisions24)

| File | Concrete pointer |
| --- | --- |
| Golden JSON (default) | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json` |
| Pattern (if range updates) | `Cert_Collisions2024_*_Golden.json` in the same directory |
| Muon JSON (optional) | same dir — `Cert_Collisions2024_*_Muon.json` if present; prefer for muon-only certified analyses |
| Web mirror | `https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/` |
| CVMFS (when available) | `/cvmfs/.../CAF/certification/Collisions24/latest/` — **TODO-VERIFY** site-local path |

**Run range in the filename above:** `378981`–`386951` (full 2024 golden as commonly cited).  
**TODO-VERIFY** that this is still the latest file before CRAB; DQM may publish a wider or replacement range. Prefer the golden with the largest valid run span that covers Run2024D (and later eras you process).

CRAB: set `config.Data.lumiMask` to the local/EOS path of the chosen JSON.

## Pileup

| File | Location |
| --- | --- |
| PU JSON / `pileup_JSON.txt` | `/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/PileUp/` |
| Per-era profiles | Often built with `brilcalc` / recommended `pileupCalc` or correctionlib recipe for Collisions24 |

**TODO-VERIFY** the exact PU profile filename for Run2024D (and later frozen eras). Offline fill defaults to `--nopileup` until profiles are wired under `reweighting/pileup/`.

## Luminosity

```bash
# Example — fill normtag + JSON path from current CMS lumi recommendations
brilcalc lumi -u /fb --normtag <current_normtag> \
  -i Cert_Collisions2024_378981_386951_Golden.json \
  --begin <Run2024D_first_run> --end <Run2024D_last_run>
```

Record integrated luminosity for Run2024D in `conditions.md`.

## DeepJet / BTV (cross-link)

Loose WP + correctionlib path: see `../deepjet_wp_2024.md`.  
Replace Run 2 DeepCSV veto with DeepJet (method §2.2).
