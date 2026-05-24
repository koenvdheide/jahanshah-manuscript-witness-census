# LLM-Assisted Workflow Disclosure

This project uses large language model tools for first-pass manuscript witness discovery. The tools supported search planning and synthesis; they did not constitute evidence for witness classification.

## Tools Used

- Anthropic Claude Code: catalogue-probe planning and search-log synthesis in work sessions that produced `data/searches/*.json`.
- Google Gemini: cross-checks and broad-source comparison during selected search phases; no prompt/session replay is preserved.
- OpenAI Codex: repository editing, validation workflow, and release preparation; the preserved artifacts are validation scripts, tests, generated metadata, data files, and file history, not prompt/session replay.

Model-specific session replay is not preserved. The project preserves the evidence chain instead: search-session records, source extracts, register entries, and validation scripts.

## Tasks Delegated To LLM Tools

- multilingual and multiscript search-term expansion;
- catalogue-probe planning;
- bibliographic backchain tracing;
- false-positive grouping for homonymous Hakiki poets and adjective uses of `haqiqi`;
- access-gap summarization;
- consistency review of public counts and metadata.

## Tasks Reserved For Human Verification

- terminal witness classification;
- attribution judgments;
- colophon interpretation;
- manuscript-content interpretation;
- material or codicological judgment;
- final public prose and release decisions.

## Use-Case Caveats

The main LLM risks in this project were not invented manuscript witnesses. The observed risks were more specific to dispersed catalogue work:

- over-definitive coverage claims, such as describing a catalogue route as exhausted when only part of the search surface had been tested;
- wrong shelfmarks for real manuscripts;
- hallucinated bibliographic entries or unverifiable secondary references.

The project did not identify entirely invented manuscript witnesses among reviewed outputs, but that absence is not a general guarantee. LLM output is treated as route-generation, synthesis, and review assistance only.

Human review paired with cross-model LLM review helped catch overstatements, stale count language, and inconsistent search-surface claims before public claims were retained. Cross-model agreement is not evidence unless the claim resolves to a catalogue record, source extract, article, edition, image, or preserved search-session record.

## Error Controls

- model output may suggest search routes, bibliography, and source trails, but bibliography and witness evidence must resolve to recoverable source records before being used;
- coverage claims must distinguish tested search surfaces from untested or blocked portions of a catalogue route;
- every register claim must resolve to a catalogue, source extract, article, edition, direct image, or preserved search-session record;
- shelfmarks and bibliographic entries suggested by models must be checked against source records before entering the register, metadata, or public prose;
- false positives are recorded in search logs and structured evidence metadata where needed instead of silently deleted;
- generated metadata is rendered from `data/metadata.json`;
- `python scripts\release_check.py` validates register counts, schema drift checks, search/extract indexes, generated metadata freshness, JSON parseability, DOI state, tests, and Git checkout hygiene checks; `python scripts\release_check.py --archive` skips Git-only checks for source-archive review.

## Limits

This release does not claim prompt-level reproducibility, a human-only baseline comparison, or generalizable recall gains. It provides a source-linked evidence chain and a documented first-pass discovery workflow for this case.

## Maintenance Note

Keep this disclosure neutral and evidence-focused. Tool-use prose should remain about research planning, source synthesis, validation, and repository maintenance.
