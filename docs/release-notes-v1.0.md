# Release notes: v1.0.0

Release date in metadata: 2026-05-30.

This first public release packages the Jahanshah Qaraqoyunlu manuscript witness census and the LLM-assisted search workflow used to build it across inconsistent multilingual catalogues and other fragmented search routes.

## Release scope

v1.0.0 includes:

- 11 census entries: 7 verified witnesses, 2 witnesses verified with attribution caveats, 1 attribution-disputed candidate, and 1 lost-attested entry.
- 37 indexed search/action records in `data/searches/`.
- A 257-string search-key matrix spanning 14 language/script or orthographic traditions.
- 10 reference extracts across `data/tezkire_extracts/` and `data/research_log/`.
- 4 structured extract/concordance artifacts in `data/extracts/`.
- Public validation tooling in `scripts/` and `tests/`.

## Package boundary

The source package contains the dataset, evidence chain, release metadata, and validation tooling. It excludes article drafts, internal planning files, local source PDFs, local workflow guardrails, old repository history, and source scans.

## Validation

Run from a Git checkout:

```powershell
python scripts/release_check.py
```

Run from an extracted source archive:

```powershell
python scripts/release_check.py --archive
```

The release gate validates dataset consistency, generated metadata freshness, unit tests, JSON parseability, line endings, Git checkout hygiene where available, and DOI readiness for publication mode.

## Citation

Use `data/metadata.json` as the canonical publication metadata source. `.zenodo.json` and `CITATION.cff` are generated from it with:

```powershell
python scripts\render_metadata.py --write
```
