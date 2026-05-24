# Search Scope Statistics and Counting Rules

Updated: 2026-05-30.

This note defines the search-breadth statistics used in the README, publication
metadata, Zenodo description, and related paper prose. It exists because
"collections searched" is too imprecise for this project: the evidence base
mixes union catalogues, individual institutional catalogues, printed catalogues,
OCR corpora, auction archives, modern printed editions, shop/acquisition pages,
blocked endpoints, and private-archive leads.

Use **search surfaces** as the denominator. Do not state that the
project searched a fixed number of "collections" unless the sentence is limited
to a specific union catalogue or institution.

## Headline Counts

| Metric | Count | Counting rule |
| --- | ---: | --- |
| Indexed search/action artifacts | 37 | Records in `data/searches/index.json`. |
| Current search/action artifacts | 29 | `current: true` records in `data/searches/index.json`. |
| Non-current search/action artifacts | 8 | `current: false` records in `data/searches/index.json`; these are split by artifact audit metadata into superseded records and appendix records. |
| Release-blocking search artifacts | 0 | `release_blocker: true` records in `data/searches/index.json`. |
| Raw portal/search labels | 88 | Unique string values under `portal` keys in `data/searches/*.json`. |
| Normalized distinct search surfaces | 62 | Raw portal labels after alias/endpoint deduplication; excludes the obsolete `yazmaeserler.gov.tr` endpoint. |
| Component-expanded named surfaces | 68 | Normalized surfaces plus explicit expansion of compound labels that bundle separately named catalogues or institutions. |
| Obsolete endpoint explicitly tested | 1 | `yazmaeserler.gov.tr`, documented as non-resolving/dead. |
| Digital Orientalist 2023 resources inventoried | 28 | Resources enumerated in `crosscheck_2026-05-11_digital_orientalist_2023_resources.json`. |
| Explicit tool/access gaps handled | 13 | 4 Playwright probes plus 9 formal dispositions in `gap_disposition_2026-05-11.json`. |
| Reusable search-key/query strings | 257 | Search-key matrix count from `data/search_keys.json`; see breakdown below. |
| Direct query-field occurrences in logs | 272 | String-valued occurrences under direct query fields such as `query`, `search_term`, `term`, and `q`; this is a lower-bound log count, not every query-like list item or structured query metadata block. |
| Unique direct query-field values in logs | 189 | Deduplicated string values from the same direct query fields. |
| Modern edition/study backchain targets | 19 | Entries in `data/search_keys.json` under `modern_editions_and_studies_for_backchain.editions_and_studies`. |
| Printed catalogue OCR files in the backchain pass | 15 | `catalogues_OCR_searched` in `search_2026-05-02_catalogue_scribe_edition_backchain.json`. |
| Recorded OCR characters in that pass | 19,240,860 | Sum of strict `ocr_chars` values; one multi-scan catalogue stores its count under `ocr_chars_combined` and is not included in this field-name-specific sum. |
| South Asian / global IA/OCR catalogue files consulted | 24 | `files_consulted_via_ia_ocr` in `search_2026-05-02_south_asian_global.json`; the sweep includes South Asian catalogue files plus a small number of global comparator catalogues. |
| Tezkire / tezkire-adjacent extract files | 5 | Markdown files in `data/tezkire_extracts/`, excluding `index.json`. |
| Research-log extract files | 5 | Markdown files in `data/research_log/`. |
| Structured extract files | 4 | JSON files in `data/extracts/`, excluding `index.json`. |
| Witness-register entries audited | 14 | Entries in `data/witness_register.json`, including rejected audit entries. |

These counts support both the census and methodology layers of the deposit. They
document the first-pass discovery surface area and access-gap handling; they are
not claims that every internal collection of every union catalogue was
exhaustively searched.

## Search-Key Matrix

The 257 reusable search-key/query strings are not 257 searches run against every
surface. They are the maintained query matrix used to adapt searches to the
language, script, catalogue field, and false-positive profile of each surface.
The separate direct query-field count above is intentionally narrower: it counts
only string values under direct query field names in `data/searches/*.json`.
Structured objects named `query` are not counted merely because the container
is named `query`, though any nested string-valued direct query fields inside
those objects are still counted.

| Search-key block | Count |
| --- | ---: |
| Author-name forms | 49 |
| Title forms | 17 |
| Catalogue-context terms | 15 |
| Scribe and colophon keys | 11 |
| Nesimi / Hurufi adjacency queries | 7 |
| Base search-key total | 99 |
| Additional script-family variants | 106 |
| South Asian Haqiqi homonym queries | 12 |
| Alevi community route/contact terms | 40 |
| Total maintained search-key/query strings | 257 |

## Language, Script, and Orthographic Coverage

Use this wording: **14 language/script or orthographic traditions**. Do not call
these simply "14 languages," because some entries are scripts or transliteration
traditions rather than separate languages.

The count consists of five base traditions plus nine additional script-family
extensions:

1. Modern academic Latin transliteration.
2. Modern Turkish / Ottoman Turkish forms.
3. Nineteenth-century French Orientalist forms.
4. Nineteenth-century German Orientalist forms.
5. Persian / Arabic-script forms, including Unicode and dotted/dotless-ya variants.
6. Modern Russian Cyrillic.
7. Modern Azerbaijani Latin.
8. Soviet-era Azerbaijani Cyrillic.
9. Georgian Mkhedruli.
10. Modern Uzbek Latin.
11. Soviet-legacy Uzbek Cyrillic.
12. Modern Tajik Cyrillic.
13. Devanagari.
14. Urdu nastaliq.

## Search-Surface Normalization

The raw JSON labels preserve what was actually written during each search pass,
including aliases, endpoint-specific labels, and repeated portals. The normalized
count deduplicates obvious aliases. Examples:

| Raw-label family | Normalized surface |
| --- | --- |
| `Qalamos`, `Qalamos (qalamos.net)`, `Qalamos (German union catalog)` | Qalamos |
| `DLME`, `DLME (dlmenetwork.org)`, `Digital Library of the Middle East (DLME) Blacklight-faceted Solr index` | DLME |
| `WorldCat`, `WorldCat search`, `WorldCat (search.worldcat.org)` | WorldCat |
| `HathiTrust`, `HathiTrust Persian-manuscripts subset`, HathiTrust catalogue labels | HathiTrust |
| `Namami Kritisampada`, `National Mission for Manuscripts NAMAMI / Kriti Sampada` | NAMAMI / Kriti Sampada |
| `YEK`, `yazmalar.gov.tr (direct)` | YEK / yazmalar.gov.tr |
| `christies`, `christies.com search/results endpoints` | Christie's |
| `sothebys`, `sothebys.com /results endpoint` | Sotheby's |
| `AMEA Manuscripts Institute, Baku`, `manuscript.az AMEA Institute of Manuscripts` | AMEA Institute of Manuscripts / manuscript.az |

The component-expanded count adds six named components that are collapsed inside
three raw labels:

| Compound raw label | Component expansion |
| --- | ---: |
| `Aligarh Muslim University (Zaidi catalogue) + India Office Library (Ethe) + Tonk + Bombay Mulla Firuz + Hyderabad` | +4 beyond the one normalized label |
| `British Library Digitised Manuscripts + Asian and African studies blog` | +1 beyond the one normalized label |
| `Dushanbe Beruni Institute / Almaty` | +1 beyond the one normalized label |

## Evidence-Strength Categories

Do not collapse all search surfaces into one evidentiary class. The logs use
several different methods, each with different negative-evidence strength:

| Category | Evidentiary strength |
| --- | --- |
| Direct catalogue or authenticated portal search | Strongest remote negative evidence when query execution and result counts are visible. |
| Direct record inspection or IIIF/detail-page inspection | Strong for the inspected manuscript or record; not necessarily exhaustive for the whole collection. |
| Printed catalogue OCR / full-text backchain | Strong where OCR quality is good and scripts are searchable; weaker for Arabic/Persian-script OCR or damaged scans. |
| Google `site:` search and public web-cache recovery | Useful fallback for blocked portals, but not equivalent to direct catalogue execution. |
| Wayback, endpoint discovery, and source-code inspection | Useful for access diagnosis; negative evidence depends on whether records are actually indexed. |
| Shop, publisher, Telegram, and acquisition pages | Bibliographic or acquisition evidence only; not manuscript-witness evidence unless they expose codex-level source apparatus or images. |
| Blocked, geo-restricted, on-site-only, or non-searchable surfaces | Counted as explicitly handled gaps, not as fully searched collections. |

## Recommended Wording

For Zenodo:

> The audit is documented by 37 indexed search/action records and a
> 257-string multilingual search-key matrix spanning 14 language/script or
> orthographic traditions. The search logs contain 88 raw portal/search labels,
> conservatively normalized to 62 distinct search surfaces or 68
> component-expanded named surfaces; these are search surfaces, not a claim that
> every internal collection of every union catalogue was exhaustively searched.
> Coverage included 28 Digital Orientalist Persian-manuscript resources, 19
> modern edition/study backchain targets, 15 OCR-searched printed catalogues
> comprising 19.24 million recorded OCR characters, 24 South Asian/global
> OCR/catalogue files, 10 tezkire or research-log source extracts, and 4
> structured extract/concordance artifacts.

For a paper methods note:

> I count search breadth at the level of documented search surfaces rather than
> manuscript collections, because several targets are union catalogues or
> blocked institutional portals. The JSON logs preserve 88 raw portal/search
> labels; after deduplicating aliases and alternate endpoints, these represent
> 62 distinct search surfaces, or 68 named surfaces when compound labels are
> expanded into their named institutional/catalogue components. Blocked,
> geo-restricted, and on-site-only routes are treated as handled access gaps,
> not as fully completed catalogue searches.

## Reviewer Caveats to Preserve

- "Search surface" is not identical to "collection."
- Union-catalogue coverage should not be converted into a precise count of
  sub-collections unless a separate portal-specific denominator is available.
- The 257 search keys were not all run against every surface.
- Direct catalogue search, OCR search, Google site-restricted search, and
  acquisition-page tracing have different evidentiary strength.
- OCR character counts are impressive scope evidence but not proof of perfect
  recall, especially for non-Latin scripts.
- The LLM-assisted workflow is reproducible at the evidence-chain level, not at
  the prompt/session-replay level.
- Methodology claims are descriptive for this case study; no human-only baseline
  recall comparison is claimed.
