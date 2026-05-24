# Search Artifact Status

This directory preserves historical search-session JSON files. Older files do not all share the same top-level schema: the 2026-05-02 scope sweeps often wrap details under `search_session`, while later probes usually use top-level `session_label`, `session_id`, `date`, and `summary` fields.

Use `index.json` for current-status questions. Each record declares whether the artifact is a current authority, whether it is superseded by another file, and whether it leaves a release blocker open. The historical files remain useful as evidence, but `index.json` is the routing layer for resolving apparent contradictions between intermediate probes and later syntheses.

Each JSON artifact also carries top-level `audit_metadata`. That object describes the artifact's method role, date, current/superseded status, source layers, access mode, disposition, and follow-up state. The field definitions and enum values are documented in `spec.md`.
