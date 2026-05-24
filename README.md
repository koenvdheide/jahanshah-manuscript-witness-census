# Jahanshah Qaraqoyunlu Manuscript Witness Census

Dispersed manuscript traditions are difficult to census because their catalogue surface is inconsistent, multilingual, fragmentary, and unevenly searchable. This repository documents one response to that problem for Jahanshah Qaraqoyunlu's Dīvān tradition (d. 872 AH / 1467 CE; pen name Ḥaqīqī / Hakîkî): a manuscript witness census built through source-based verification and an LLM-assisted search workflow.

The release records 11 census entries and the workflow used to find, check, and delimit them across inconsistent multilingual catalogues, printed references, private and community archives, blocked or non-searchable portals, and lost or unlocated reports. LLM tools helped expand multilingual search terms, reconcile catalogue variants, surface homonyms and false positives, and map access gaps; they did not classify witnesses or decide attributions. Witness classifications and attribution decisions remain source-based and human-reviewed.

The census contains 7 verified witnesses, 2 witnesses verified with attribution caveats, 1 attribution-disputed candidate, and 1 lost-attested entry. The package also includes 10 ancillary reference extracts, 4 structured extract or concordance artifacts, and 37 indexed search-session and action records. Use it as an inspection agenda for future manuscript work; it is not a critical edition or a substitute for physical manuscript examination.

Authors:

- Koen van der Heide, Independent Scholar (ORCID [0009-0008-9855-3848](https://orcid.org/0009-0008-9855-3848))
- Negar Kazemipourleilabadi, Ludwig-Maximilians-Universität München, Department of Art History (ORCID [0009-0008-2289-7492](https://orcid.org/0009-0008-2289-7492))

License: [CC BY 4.0](LICENSE)

DOI: [10.5281/zenodo.20467142](https://doi.org/10.5281/zenodo.20467142)

## Witnesses At A Glance

| Shelfmark | Date (CE) | Holding | Folios | Verification | Access/evidence | Material data |
| --- | --- | --- | --- | --- | --- | --- |
| BL Or 9493 | 1488 | British Library, London | 85 | verified | scholarly/catalogue attestation | partial: dimensions; qualitative Minorsky description |
| Matenadaran MS 965 | 1474-75 | Matenadaran, Yerevan | 54 | verified | scholarly/catalogue attestation | unrecovered |
| Süleymaniye Fatih 3808 | 20th c. | Süleymaniye, Istanbul | 107 | verified | scholarly/catalogue attestation | partial: dimensions and Mahmud I waqf seal |
| Ankara DTCF İsmail Saib I/2221 | 19th c. | Ankara DTCF or Atatürk Üniv. Erzurum (disputed) | 26 | verified with caveat | scholarly/catalogue attestation | partial: dimensions and writing area |
| Tehran University Ktp. 8198 | 16th c. | Tehran University Central Library | 133 | verified | scholarly/catalogue attestation | unrecovered |
| Ankara MK A 5252 | 20th c. | Milli Kütüphane, Ankara | 204 (fragment ff. 183a-196a) | verified | scholarly/catalogue attestation | unrecovered |
| Diyarbakır Ulutürk cönk | 1860s | İmam Zeynel Abidin Ocağı (Abbas Önen) | unknown | verified | direct image/plate evidence | negative: undecorated village rika notebook |
| Ilkhchi Kırklar Ocağı pirs' archive | unknown | Kırklar Ocağı, Ilkhchi (East Azerbaijan, Iran) | unknown | verified with caveat | reported unexamined; private/community access | unrecovered |
| Ilkhchi cem cönks | unknown | Kırklar Ocağı performance archive | unknown | verified | scholarly attestation; private/community access | unrecovered |
| Diyarbakır Yazma Eserler (former) | unknown | Diyarbakır Y.E. (reported lost per Cunbur 1999) | unknown | lost-attested only | scholarly attestation; lost/unlocated | unrecovered |
| Konya Hacı Bektaş BY0000010729 | unknown | Konya Hacı Bektaş Dergahı (via YEK) | 150 | candidate: probably non-Cihanşah | scholarly/catalogue attestation | unrecovered |


## Findings

1. The reported contents divide the institutional witnesses into fuller copies with masnavīs and a BL Or 9493 group without masnavīs. Jāmī's contemporary Munshaʾāt describes Cihanşah's lifetime divan as containing both ghazals and masnavīs, so the masnavī-bearing form is probably closer to the lifetime layer. No stemmatic collation has been done.
2. The Alevi shrine corpus extends the textual range. Anatolian and Iranian Azerbaijani Ocak lineages preserve eleven published ghazals not present in the institutional editions examined, and they report a complete divan codex in the Ilkhchi Kırklar Ocağı pirs' archive that has not yet been examined by scholars outside the shrine community.
3. The surviving witness map is Ottoman-leaning rather than Turkmen-centred. Six of the 11 census entries are held in Turkey, one in Armenia, three in Iran, and one in the United Kingdom. The closest fifteenth-century witnesses are BL Or 9493 and Matenadaran MS 965; much of the corpus reflects later Ottoman and Anatolian-Alevi transmission.

## Material Evidence

The `Material data` column summarizes the `material_data_level` axis defined in [`data/spec.md`](data/spec.md). The project records paper, binding, illumination, seals, dimensions, and image-based negative evidence when recovered. Most entries still require direct inspection, institutional image requests, interlibrary loan of base-text editions, or field correspondence before material or codicological claims can be strengthened.

## Methodology

### Method Outputs

The release includes method records for:

- a 257-string multilingual search-key matrix spanning 14 language/script or orthographic traditions plus Alevi-community route terms;
- 37 indexed search-session and action records with current or superseded status;
- normalized search-surface counting rules that distinguish raw portal labels, distinct search surfaces, and component-expanded named surfaces;
- a verification-status system for verified, caveated, candidate, and lost-attested records, with false-positive and access-gap dispositions documented in the search logs;
- explicit access-gap logging for blocked, non-searchable, on-site-only, and private/community-controlled sources.

The search work used union-catalogue sweeps, printed-catalogue and OCR backchains, tezkire extraction, modern-edition source tracing, Alevi field-literature review, mecmua and cönk context analysis, auction-archive checks, and scribe-name searches. The search-key matrix includes five base traditions plus nine additional script-family blocks added after the Alevi and regional follow-up passes.

### LLM-Assisted Workflow

Large language model tools were used as search and synthesis assistants, not as evidence authorities. They helped expand multilingual search terms, reconcile catalogue variants, surface homonyms and false positives, trace bibliography and edition backchains, and map access gaps across dispersed catalogues. Witness classifications, attribution decisions, colophon readings, and material or codicological judgments remain source-based and human-reviewed.

Known failure modes for this use case include over-definitive coverage claims, wrong shelfmarks for real manuscripts, and hallucinated bibliographic entries. For example, a model may describe a catalogue route as exhausted when only part of the search surface was tested. The mitigation used here pairs human source review with cross-model LLM review; model agreement is treated as a check on wording and consistency, not as evidence by itself.

The checkable record is the evidence chain: register entries, search-session JSON records, source extracts, and cited catalogue or scholarly references. Prompt-level replay is not preserved, and this release does not claim the LLM workflow can be reproduced as a sequence of model interactions. See [`docs/llm-use.md`](docs/llm-use.md) and [`docs/limitations-and-recovery-plan.md`](docs/limitations-and-recovery-plan.md).

## Search Depth And Breadth

[`data/searches/`](data/searches/) holds 37 search-session and action records: 8 initial scope sweeps from 2026-05-02 and 29 follow-up records from 2026-05-10 through 2026-05-21. The follow-ups include Iranian portal re-tests, Marashi-Najafi and Tehran University checks, regional avenue probes, Turkish-repository sub-investigations, a Digital Orientalist resource cross-check, tool/access-gap dispositions, witness-specific follow-ups, the Teece 2016 Pir Budaq corpus probe, Patna and South Asian homonym work, modern-edition source-apparatus work, Barqi/Akhtar acquisition work, Alevi-community continuation records, and the Ersal-Ceylan Alevi-Bektashi catalogue probe.

The search logs preserve 88 raw portal/search labels, normalized in [`docs/search-scope-statistics.md`](docs/search-scope-statistics.md) to 62 distinct search surfaces, or 68 component-expanded named surfaces when compound labels are split into named catalogues or institutions. Blocked, geo-restricted, on-site-only, and non-searchable routes are counted as handled access gaps, not completed catalogue searches.

## Repository Contents

- [`data/witness_register.json`](data/witness_register.json): the canonical register.
- [`data/metadata.json`](data/metadata.json): canonical publication metadata used to render `.zenodo.json` and `CITATION.cff`.
- [`data/spec.md`](data/spec.md): field-by-field description of the register format.
- [`data/search_keys.json`](data/search_keys.json): search-key matrix with base script families, additional regional script-family extensions, South Asian homonym terms, and Alevi-community route/contact terms.
- [`data/searches/`](data/searches/): 37 search-session and action records, with current or superseded status summarized in [`data/searches/index.json`](data/searches/index.json).
- [`data/tezkire_extracts/`](data/tezkire_extracts/): 5 indexed tezkire or tezkire-adjacent reference extracts on Hakîkî.
- [`data/research_log/`](data/research_log/): 5 source extracts and methodological assessments.
- [`data/extracts/`](data/extracts/): 4 structured extract or concordance artifacts indexed in [`data/extracts/index.json`](data/extracts/index.json).
- [`notes/`](notes/): public research notes citable from this release.
- [`docs/search-scope-statistics.md`](docs/search-scope-statistics.md): counting rules and search-breadth statistics.
- [`docs/llm-use.md`](docs/llm-use.md): model-use disclosure.
- [`docs/limitations-and-recovery-plan.md`](docs/limitations-and-recovery-plan.md): inspection and recovery agenda.
- [`docs/release-notes-v1.0.md`](docs/release-notes-v1.0.md): release notes for this first public package.
- [`scripts/`](scripts/) and [`tests/`](tests/): dependency-light validation and summary tooling.

## Release Checks

Before publication, run from a Git checkout:

```powershell
python scripts\release_check.py
```

Before the Zenodo DOI has been reserved, maintainers can run the structural gate:

```powershell
python scripts\release_check.py --structural
```

Reviewers working from a source archive without `.git` metadata can run:

```powershell
python scripts\release_check.py --archive
```

The gate validates register counts, schema drift, search and extract indexes, generated metadata freshness, JSON parseability, unit tests, DOI readiness, line endings, and Git hygiene where available. The manual checklist is in [`docs/release-checklist.md`](docs/release-checklist.md).

## Candidate Note

Konya Hacı Bektaş BY0000010729 is retained as an attribution-disputed candidate because it appears in a Bektaşi mecmua with an ambiguous Hakîkî attribution. Its current classification is probably non-Cihanşah by poetic context.

## Citation

If you use this dataset, cite the released Zenodo record:

> van der Heide, K. & Kazemipourleilabadi, N. (2026). *Jahanshah Qaraqoyunlu Manuscript Witness Census* (Version 1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20467142

`CITATION.cff` is included for citation managers and GitHub's citation widget.

## Status And Known Limits

This is a working research corpus, not a critical edition. Open work remains: interlibrary loan procurement, institutional image requests, direct inspection, and field correspondence. Material and decorative evidence is recorded only when source-supported. The corpus is a poetry-witness census with codicology as a secondary evidence layer.

The Iranian portion of the corpus remains the largest open area. Remote work left part of the Iranian manuscript-catalogue surface inaccessible or non-searchable, and no on-site research was performed. The Ilkhchi Kırklar Ocağı pirs' archive is reported to hold a complete unphotographed divan codex, but access depends on shrine-community consent and has not been granted to scholars outside the local pir tradition.

### Future Scope

Future work may extend the project to Cihanşah-related chancery documents, inscriptions, letters, and broader court-corpus evidence. Those documentary witnesses are outside this poetry-witness release but materially extend the historical picture of Cihanşah as a ruler and literary figure.

## Author Contributions

Following the [CRediT (Contributor Roles Taxonomy)](https://credit.niso.org/):

- Negar Kazemipourleilabadi: Conceptualization; Investigation; Writing, Review & Editing; Persian, Turkish, Ottoman Turkish, and Azerbaijani orthographic review; multilingual source-interpretation checks.
- Koen van der Heide: Conceptualization (joint); Methodology; Data Curation; Investigation; Software; Writing, Original Draft; Visualization.
