# DeepJet \(b\)-veto (2024 placeholders)

AN-20-111 used DeepCSV loose. For Run 3 / 2024 use **DeepJet** (BTV default for
this analysis; ParticleNet / robustParT are alternatives — freeze one tagger).

## Event veto (method §2.4)

| Item | Value |
| --- | --- |
| Jet collection | AK4 PUPPI (`slimmedJetsPuppi`) |
| \(p_T\), \(\lvert\eta\rvert\) | \(>30\,\mathrm{GeV}\), \(<2.5\); jet ID pass |
| Discriminator (MiniAOD) | `pfDeepFlavourJetTags:probb+probbb+problepb` → branch `Jet_btagDeepFlavB` |
| Working point | **loose** (L) — light-jet mistag ≈ 10% by BTV definition |
| Veto | ≥1 jet above loose WP |

## Numeric WP — TODO-VERIFY (do not invent)

| WP | Mistag definition | Threshold for 2024 DeepJet |
| --- | --- | --- |
| Loose (L) | ~10% light-jet mistag | **TODO-VERIFY** — look up (do not copy Run 2 / 2016 Open Data numbers) |
| Medium (M) | ~1% | TODO-VERIFY (systematic variation only) |
| Tight (T) | ~0.1% | TODO-VERIFY (not used for AN-style veto) |

Run 3 also defines XT (~0.05%) and XXT (~0.01%); not needed for the DY \(b\)-veto.

## Where to look up official WPs / SFs

1. **correctionlib / jsonpog-integration (authoritative for analysis code)**  
   On CVMFS (typical layout — confirm year folder names on the day of freeze):
   ```text
   /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/
   ```
   Expect era folders such as `2024_*/btagging.json` (or `Summer24` / `2024_Prompt` —
   **TODO-VERIFY exact subdirectory**). Keys of interest: `deepJet_wp_values` (or
   equivalent) and fixed-WP SF corrections for flavour `5/4/0`.

2. **BTV / CMS performance notes**  
   - CMS-DP-2024/025 (2022 AK4 \(b\)-tagging summary; documents L/M/T/XT/XXT mistag defs)  
   - Later 2024 BTV DPs / POG talks for the **2024** DeepJet thresholds  
   - CMS BTV TWiki (internal): search “DeepJet working points Run 3 / 2024”

3. **NanoAOD Tools / common POG JSON summaries**  
   https://opendata.cern.ch/eos/opendata/cms/corrections/jsonpog-integration-summary/  
   (Open Data mirror may lag; prefer CVMFS for 2024).

## Freeze checklist (before M5 skim)

- [ ] Exact DeepJet loose cut value recorded in `conditions.md`
- [ ] Path to BTV `btagging.json` (or equivalent) recorded
- [ ] Confirm MiniAOD discriminator label still `pfDeepFlavourJetTags:*` for the chosen campaign
- [ ] Jet ID: replace 2018 UL placeholder in `JetAnalyzer` with Run 3 recipe if BTV/JME requires it
- [ ] Offline veto uses the frozen WP; SF variations enter the systematic envelope (method §2.8)
