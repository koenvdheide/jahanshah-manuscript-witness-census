# Release Checklist

Run this checklist before publishing the dataset or making a release-style commit.

1. Update `data/witness_register.json` first. Keep terminal witness status in the register, not in README prose.
2. Update `data/spec.md` when register top-level fields or stat semantics change.
3. Add or update index entries for new evidence artifacts:
   - `data/searches/index.json` for search-session JSON files.
   - `data/extracts/index.json` for structured extract JSON files.
   - `data/tezkire_extracts/index.json` for tezkire Markdown extracts.
4. Mark superseded artifacts with `current_status_note` or `superseded_by` instead of deleting historical evidence.
5. Update `data/metadata.json` for publication metadata changes, then run `python scripts\render_metadata.py --write`.
6. Update release notes when the release scope, method layer, package contents, or validation evidence changes.
7. Run `python scripts\release_check.py --structural` before DOI reservation when the pre-reservation DOI marker is still present.
8. After the Zenodo DOI is reserved and inserted, run `python scripts\release_check.py` from a Git checkout.
9. For reviewer validation from a source archive, run `python scripts\release_check.py --archive`.
10. Read the staged diff before commit. Exclude local PDFs, source scans, caches, and unrelated workspace files.

## Methodology Framing Checks

- README opening frames the project as a manuscript witness census plus llm-assisted first-pass manuscript discovery workflow.
- README links to `docs/llm-use.md` and `docs/limitations-and-recovery-plan.md`.
- Every witness entry has `evidence_level`, `access_level`, and `material_data_level`.
- `data/metadata.json`, `.zenodo.json`, and `CITATION.cff` use the hybrid methodology framing.
- The release gate passes in the appropriate DOI mode.

The release gate is local and dependency-light. It validates JSON parseability, register statistics, stale status phrases, search/extract indexes, publication metadata rendering, unit tests, DOI state, line endings, and Git hygiene when `.git` metadata is available. Archive mode skips Git checkout hygiene checks.
