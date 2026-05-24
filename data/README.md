# Data Layout

`witness_register.json` is the canonical register. It holds normalized witness fields, publication counts, and terminal verification/rejection status.

`metadata.json` is the canonical publication metadata source. Run `python scripts\render_metadata.py --write` after changing it, then run `python scripts\release_check.py`.

`spec.md` documents the register shape. If the register adds a top-level field or changes count semantics, update the spec in the same change.

`search_keys.json` is the query matrix and disambiguation helper. It is intentionally broader than the register and may contain overlapping query forms when a form belongs to more than one search axis.

`searches/` preserves historical search-session evidence. Use `searches/index.json` to resolve current versus superseded search artifacts.

`tezkire_extracts/` stores narrative source extracts. Use `tezkire_extracts/index.json` for machine-readable metadata instead of parsing the varied Markdown headers.

`research_log/` stores source-specific notes and methodological assessments that support register decisions but are not themselves register entries.

`extracts/` stores structured corpus probes, concordances, and candidate-route extracts outside the main witness register. Use `extracts/index.json` to resolve current extract artifacts instead of counting the directory by hand.
