# Search Artifact Audit Schema

This directory preserves heterogeneous search and action records. `index.json`
remains the current-status routing layer. Each individual JSON artifact carries
an inline `audit_metadata` object that describes the artifact's method role,
access condition, evidence layer, and outcome.

The audit layer is intentionally separate from the witness-register schema. It
describes how a search/action artifact should be read; it does not classify a
manuscript witness.

## Placement

`audit_metadata` lives at the top level of every JSON artifact in
`data/searches/`, excluding `index.json`. It is not duplicated in `index.json`.
The index answers "which artifact is current?"; `audit_metadata` answers "what
kind of artifact is this, what evidence layer did it touch, and what did it
produce?"

## Required Object

```json
{
  "audit_metadata": {
    "record_type": "catalogue_probe",
    "record_date": "2026-05-11",
    "artifact_status": "current",
    "source_layers": ["catalogue_record", "project_classification"],
    "access_mode": "open_web",
    "disposition": "no_new_witness",
    "follow_up_required": false,
    "follow_up_type": "none"
  }
}
```

## Field Definitions

| Field | Type | Values | Fallback rule |
| --- | --- | --- | --- |
| `record_type` | string | `catalogue_probe`, `literature_backchain`, `source_apparatus_probe`, `access_gap_disposition`, `targeted_followup`, `crosscheck`, `extraction_or_concordance`, `methodological_record` | Required. Use `methodological_record` only when no narrower intent fits. |
| `record_date` | string or null | ISO `YYYY-MM-DD` | Use the artifact filename date or top-level date. Use `null` only if no reliable date appears in either place. |
| `artifact_status` | string | `current`, `superseded`, `appendix` | Mirrors `index.json` routing where possible. Use `appendix` for non-current evidence retained as supporting detail rather than as an obsolete route. |
| `source_layers` | array of strings | `catalogue_record`, `scholarly_description`, `edition_apparatus`, `digital_surrogate`, `community_report`, `search_engine_index`, `institutional_access_status`, `project_classification` | Required non-empty array. Use all layers materially touched by the artifact; include `project_classification` when the artifact assigns a disposition. |
| `access_mode` | string | `open_web`, `login_required`, `blocked_or_down`, `on_site_only`, `private_or_permissioned`, `print_or_ill_only`, `not_applicable` | Use the main access condition governing the artifact's evidence. Mixed-access records should use the limiting condition and explain nuance in the artifact body. |
| `disposition` | string | `new_witness`, `augmented_existing_witness`, `no_new_witness`, `rejected_false_positive`, `access_gap_logged`, `deferred_followup`, `methodological_record` | Required. Use `methodological_record` for accounting, synthesis, or intake artifacts that do not resolve witness status. |
| `follow_up_required` | boolean | `true`, `false` | Required. Use `true` only when the artifact leaves a concrete next action. |
| `follow_up_type` | string | `institutional_query`, `physical_inspection`, `image_request`, `source_acquisition`, `community_consent_contact`, `repeat_access_check`, `none` | Must be `none` when `follow_up_required` is `false`. Must be a non-`none` value when `follow_up_required` is `true`. |

## Intent Versus Outcome

`record_type` describes the artifact's intent: what kind of search or action it
was created to perform. `disposition` describes the artifact's outcome: what the
search or action produced. For example, a record can have
`record_type: access_gap_disposition` and `disposition: access_gap_logged`, or
`record_type: catalogue_probe` and `disposition: rejected_false_positive`.

## Scope Wording

Historical search logs may use terms such as "exhaustive" or "exhausted" for a
specific route, source surface, query family, or follow-up pass. Those terms are
local to the named artifact and do not assert corpus-wide recall, full
collection coverage, or physical inspection of every possible manuscript.

## Retrofit Rule

Retrofitted records use only information already present in the artifact,
filename, or `index.json`. Do not infer a manuscript result that the artifact
does not state. When a field proves routinely unrecoverable across historical
records, make that field optional or use a documented fallback before tightening
validation.
