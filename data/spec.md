# Witness Register Schema (v1)

This document describes the structure of `witness_register.json`, the primary artifact of this deposit. It is organised as a **core schema** (the v1 design fields, present in every witness entry) plus **observed extension fields** (per-witness fields added during execution to record codex-specific evidence). The register is hand-curated, not generated, so a future witness may carry additional extension fields not documented here.

## Schema version

`schema_version: 1`. Generated 2026-05-11.

## Top-level structure

```json
{
  "schema_version": 1,
  "generated": "2026-05-11",
  "purpose": "...",
  "rejection_inclusion_criterion": "...",
  "candidate_inclusion_criterion": "...",
  "witnesses": [ ... ],
  "stats": { ... },
  "teis_yesevi_roster": [ ... ]
}
```

The `teis_yesevi_roster` block lists the five witnesses on the TEIS Yesevi roster (a subset of the entries in `witnesses[]`).

## Witness entry: core fields

Every witness entry carries the listed core fields with `null` for unknown values. Beyond the core, observed extension fields (e.g. `verification_caveat`, `dimensions_mm`, `script`, `columns`) appear only in entries where they are relevant and are omitted entirely otherwise.

### Identity fields

| Field | Type | Description |
|---|---|---|
| `witness_id` | string | Stable internal identifier. Lowercase snake_case. Usually `<collection-slug>_<shelfmark-slug>`. |
| `shelfmark` | string | Catalogue shelfmark in its native form. |
| `collection` | string | Holding institution and sub-collection. |
| `city`, `country` | string | Location of holding institution. |

### Codicology fields (all optional)

| Field | Type | Description |
|---|---|---|
| `date_ah`, `date_ce` | string \| null | Hijri and CE year of copying, or range. |
| `scribe` | string \| null | Scribe name as transcribed from the colophon. |
| `languages` | array of string \| null | Languages present in the codex. |
| `folios` | integer \| null | Total folio count. |
| `dimensions_cm` | string \| null | Dimensions in centimeters, e.g. `"23 × 16"`. Field is present in all entries but typically null (codicology data is sparse across the corpus); Nuruosmaniye uses `dimensions_mm` instead. |
| `dimensions_mm` | string \| null | Optional alternate dimensions in millimeters when the source quotes mm-precision values. |
| `lines_per_page` | string or integer \| null | Line count per page. May be a range. |
| `contents` | string \| null | Free-text contents description. |

### Status (3 fields)

| Field | Type | Description |
|---|---|---|
| `completeness` | string \| null | One of: `complete`, `fragment`, `fragment_or_excerpt`, `unknown`. May be `null` for rejected non-witness entries that were never substantively evaluated. |
| `fragment_type` | string \| null | If `completeness` is `fragment` or `fragment_or_excerpt`, kind of fragment. |
| `digital_surrogate` | string \| null | URL to digital surrogate, if extant. |

### Decoration object

The `decoration` object records paper, illumination, and binding observations. Core fields are present in every entry; extension fields appear when relevant evidence was recovered.

```json
{
  "paper_description": "string or null",
  "illumination": "string or null",
  "binding": "string or null",
  "data_source": "string or null",
  "notes": "string or null",
  "confidence": "very_high | high | moderate | low | very_low | unknown"
}
```

`data_source` records who described the decoration (firsthand examiner, catalogue entry, photograph, IIIF surrogate). `confidence` follows the project-wide qualitative scale and is present in all entries.

**Observed extension fields inside `decoration`** (added when a single confidence value would conflate distinct sub-judgments):

- `seals_marks` (string): waqf seals, ownership marks, library stamps. Recorded when seals are codicologically diagnostic.
- `decoration_data_confidence` (qualitative): confidence in the decoration evidence itself, separate from the next field.
- `cihansah_attribution_confidence` (qualitative): confidence that the codex is a Cihānşāh witness (relevant when an Ottoman-period homonym ambiguity exists).

### Provenance and verification (5 fields)

| Field | Type | Description |
|---|---|---|
| `scholarly_attestation` | array of object | Each object has `author`, `year`, `ref`, and optionally `saw_firsthand` (boolean or string `"likely"`; omitted for attestation objects where firsthand status is not assessed, e.g. authoritative encyclopedia entries). `year` may be an integer, string, or `null` when undated. May carry an optional `remark` field for verbatim cross-collation evidence. |
| `discovery_source` | string | URL or printed-catalogue reference that originally surfaced the witness. |
| `verification_status` | string | See enum below. |
| `verification_caveat` | string | Optional free-text qualification of verified, candidate, or audit-rejected status. For rejected entries, use only when the caveat preserves the reclassification path and keep the terminal rationale in `rejection_reason`. |
| `notes` | string \| null | Free-text notes on dating, scribal hand, or context. |

### Evidence axes

`verification_status` is the terminal classification. It answers whether the entry is a verified witness, caveated witness, candidate, lost-attested witness, or audit-preserved rejection. It does not by itself describe how direct the evidence is.

Every witness therefore also carries three reviewer-facing evidence axes:

| Field | Values | Meaning |
| --- | --- | --- |
| `evidence_level` | `direct_primary_inspection`, `catalogue_or_scholarly_attestation`, `reported_unexamined` | How directly the project/deposit currently establishes or audits the entry. Candidate status is carried by `verification_status`, not by this field. |
| `access_level` | `digital_or_image_access`, `catalogue_or_edition_only`, `private_or_permissioned_access`, `lost_or_unlocated` | What kind of access the project currently has or still needs for verification. |
| `material_data_level` | `substantive_material_evidence`, `partial_material_evidence`, `negative_or_qualitative_only`, `unrecovered`, `not_applicable_rejected` | How much material or codicological evidence has been recovered for the Cihanşah witness; rejected entries use `not_applicable_rejected` because their material data is not corpus evidence. |

For `material_data_level`, basic dimensions or writing-area dimensions count as `partial_material_evidence`; folio count, folio range, language, contents, or script alone remain `unrecovered` unless paired with a material datum such as dimensions, seal, binding, paper, illumination, or image-based negative evidence.

For `access_level`, use the best project-held access to the witness evidence while preserving the remaining physical-access route. Published plates or IIIF images count as `digital_or_image_access`; catalogue, edition, or article text without images counts as `catalogue_or_edition_only`; a privately held or community-controlled codex with only text-level publication evidence should remain `private_or_permissioned_access` when direct physical verification is still the recovery path.

For structured dimension fields, use the multiplication sign `×` rather than ASCII `x` so newly lifted dimensions match existing register convention.

## Witness entry: observed extension fields

Beyond the core schema, individual entries carry codex-specific evidence fields. The most common:

- `candidate_provenance`: origin of a candidate witness traced from a tezkire or printed-catalogue lead.
- `columns`: page columnation, when relevant.
- `script`: script style (e.g. *nastaʿlīq*, *nasta'liq*, *taʿlīq*).
- `rejection_reason`: explicit reasoning for `rejected` entries (audit-preserved).
- `rejection_type`: sub-classification of rejected entries. Values: `derivative_surrogate` (the entry is a copy/microfilm of an existing witness and would double-count it if included), `non_manuscript_misidentification` (the entry was never an independent manuscript, e.g. a printed edition once treated as if it were an MS witness), and `scribal_homonym_misidentification` (the entry was attributed to Cihānşāh but colophon evidence identifies a scribe with a homonymous given name; the manuscript is the work of a different person of the same first name).

Single-occurrence extension fields document evidence specific to one witness (e.g. `alemdari_edition_findings`, `disambiguation_caveat`, `recovery_method`, `decoration_data_value_for_or_9493_question`). These are not part of the v1 schema; they are research notes that future versions may either lift to first-class fields or move into `notes`.

## verification_status enum

The publication terminal-state enum has six values:

| Value | Meaning |
|---|---|
| `verified` | Primary-source-attested or independently confirmed witness. |
| `verified_with_attribution_caveat` | Witness existence and primary attribution are confirmed, but a caveat remains (institutional/holding attribution disagreement OR unresolved attribution to Cihānşāh). |
| `candidate_probably_non_cihansah` | Manuscript confirmed to exist; attribution to Cihānşāh weakly supported. |
| `candidate_probably_yusuf_hakiki_or_other_homonym` | Manuscript confirmed to exist; attribution probably points to a homonym (Yusuf Hakîkî or another *Hakîkî* poet). |
| `lost_witness_attested_only` | Witness attested in scholarly literature but no longer extant or no longer locatable. |
| `rejected` | Investigated and dismissed; audit-preserved with explicit `rejection_reason` plus a `rejection_type` sub-classification (`derivative_surrogate`, `non_manuscript_misidentification`, or `scribal_homonym_misidentification`; see extension fields above). **Inclusion criterion**: only candidates cited in published scholarship or acquired as Cihānşāh witnesses by a major institution appear here. Routine search false-positives live in per-session JSONs under `data/searches/`. |

Per-status counts live in `witness_register.json` `stats.by_verification`.

`pending` is a transient execution state allowed during in-progress work, not a publication terminal value. At publication, no entry may carry `pending`, and `stats.by_verification.pending` must remain `0`.

The rejected-entry subclasses are also part of the methodology layer: they preserve false-positive disposition patterns so future researchers do not rediscover the same Baku publication witness, AMEA surrogate, or Nuruosmaniye scribal-homonym claim as unresolved leads.

The evidence axes are project-current access descriptors. They are intentionally orthogonal to `verification_status`: a catalogue-attested candidate and a catalogue-attested verified witness can share the same `evidence_level`, while their terminal classification remains different.

## Stats block

The `stats` object aggregates counts (`by_completeness` and `by_country` count non-rejected entries; `by_verification` includes all entries):

```json
{
  "total_non_rejected_entries": <int>,
  "total_verified_or_caveated_witnesses": <int>,
  "total_witnesses_active": <int>,
  "total_entries_including_rejected_and_lost": <int>,
  "by_verification": { "<status>": <count>, ... },
  "by_completeness": { "<value>": <count>, ... },
  "by_country": { "<ISO-or-name>": <count>, ... }
}
```

The preferred top-line count is `total_non_rejected_entries`: it excludes entries with `verification_status: rejected` and includes verified/caveated witnesses, candidates, and lost-attested entries. `total_verified_or_caveated_witnesses` counts only `verified` plus `verified_with_attribution_caveat`. `total_witnesses_active` is retained as a compatibility alias for `total_non_rejected_entries`, but README prose should avoid the ambiguous word "active" when precision matters. `total_entries_including_rejected_and_lost` is the audit-preserved total of all entries. `by_verification` may retain zero-count transient buckets such as `pending` for release-to-release diff stability.

## Verification rule

Every entry in `witness_register.json` carries an evidence trail that resolves independently. Resolvable references typically appear in `discovery_source`; where a witness was first surfaced through means other than a single URL/printed reference, the resolvable evidence may live in `scholarly_attestation`, `rejection_reason`, or `decoration.data_source` instead. Candidate bibliography is treated as candidate, not attested, until verified by an independently resolvable source URL or printed-catalogue reference. The `rejected` entries are kept in the register, not silently deleted, to preserve the audit trail of which proposed witnesses were investigated and dismissed. Inclusion in the register requires that the candidate has been cited in published scholarship or acquired by a major institution as a Cihānşāh witness; routine search false-positives are documented in the per-session JSONs under `data/searches/` and not promoted to the register. Three current rejected entries: two address Baku-related claims (the Doerfer 1976 hypothesis and the AMEA Manuscripts Institute 2021 acquisition announcement), both concluding Baku does not hold an independent Cihānşāh codex; the third (Nuruosmaniye 04281) addresses a scribal homonym misidentification where colophon evidence identifies the scribe as Jahānshāh b. Bābā Gejelū (Muḥarram 1088 AH / 1677 CE), not Cihānşāh Qaraqoyunlu.

## Example entry: bl_or_9493 (abridged)

```json
{
  "witness_id": "bl_or_9493",
  "shelfmark": "Or 9493",
  "collection": "British Library, Oriental Manuscripts",
  "city": "London",
  "country": "UK",
  "date_ah": "Shawwāl 893",
  "date_ce": "September 1488",
  "scribe": "Qanbar-ʿAlī b. Khusraw al-Iṣfahānī",
  "languages": ["Persian", "Turkish"],
  "folios": 85,
  "dimensions_cm": "23 × 16",
  "writing_surface_cm": "16 × 11",
  "lines_per_page": "10-11",
  "contents": "Contents counts differ by source: Minorsky 1954 reported 105 Persian ghazals + 1 mustazad, 87 Turkish ghazals, and 32 Turkish quatrains; Macit corrected the count after collation to 113 Persian ghazals, 92 Turkish ghazals, and 33 tuyug. Two added poems by 'Farrukh' appear on f. 85b (one Persian, one Turkish).",
  "completeness": "complete",
  "fragment_type": null,
  "digital_surrogate": null,
  "decoration": {
    "paper_description": null,
    "illumination": null,
    "binding": null,
    "data_source": null,
    "confidence": "unknown",
    "notes": "Minorsky 1954 reports state of preservation 'perfect' and calls it a 'handsome little manuscript'. No further decoration data in any open-access scholarly source."
  },
  "scholarly_attestation": [
    {"author": "Minorsky", "year": 1954, "ref": "BSOAS 16/2: 271-297", "saw_firsthand": true},
    {"author": "Macit", "year": 2000, "ref": "Bilig 13: 9-17", "saw_firsthand": true},
    {"author": "Düzgün, D.", "year": null, "ref": "academia.edu/43146022 (self-deposited preprint)", "saw_firsthand": false},
    {"author": "Alemdârî", "year": "2001 / 1379 SH", "ref": "...", "saw_firsthand": true}
  ],
  "discovery_source": "https://www.fihrist.org.uk/catalog/manuscript_6481",
  "verification_status": "verified",
  "fihrist_decoration_facet": "Decoration: No, per sweep 2026-05-02. Caveat: Fihrist's coarse boolean tag does not distinguish illumination from decorated paper.",
  "notes": "Posthumous copy: 21 years after Jahānshāh's death."
}
```

The `writing_surface_cm` and `fihrist_decoration_facet` fields illustrate single-occurrence extension fields that future schema versions may lift to first-class.
