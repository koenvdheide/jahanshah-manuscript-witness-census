#!/usr/bin/env python3
"""Validate high-level consistency for the witness census deposit."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from register_summary import compute_stats


ALLOWED_VERIFICATION_STATUSES = {
    "verified",
    "verified_with_attribution_caveat",
    "candidate_probably_non_cihansah",
    "candidate_probably_yusuf_hakiki_or_other_homonym",
    "lost_witness_attested_only",
    "rejected",
    "pending",
}
ALLOWED_COMPLETENESS = {"complete", "fragment", "fragment_or_excerpt", "unknown", None}
ALLOWED_EVIDENCE_LEVELS = {
    "direct_primary_inspection",
    "catalogue_or_scholarly_attestation",
    "reported_unexamined",
}
ALLOWED_ACCESS_LEVELS = {
    "digital_or_image_access",
    "catalogue_or_edition_only",
    "private_or_permissioned_access",
    "lost_or_unlocated",
}
ALLOWED_MATERIAL_DATA_LEVELS = {
    "substantive_material_evidence",
    "partial_material_evidence",
    "negative_or_qualitative_only",
    "unrecovered",
    "not_applicable_rejected",
}
ALLOWED_SEARCH_AUDIT_RECORD_TYPES = {
    "catalogue_probe",
    "literature_backchain",
    "source_apparatus_probe",
    "access_gap_disposition",
    "targeted_followup",
    "crosscheck",
    "extraction_or_concordance",
    "methodological_record",
}
ALLOWED_SEARCH_AUDIT_STATUSES = {"current", "superseded", "appendix"}
ALLOWED_SEARCH_AUDIT_SOURCE_LAYERS = {
    "catalogue_record",
    "scholarly_description",
    "edition_apparatus",
    "digital_surrogate",
    "community_report",
    "search_engine_index",
    "institutional_access_status",
    "project_classification",
}
ALLOWED_SEARCH_AUDIT_ACCESS_MODES = {
    "open_web",
    "login_required",
    "blocked_or_down",
    "on_site_only",
    "private_or_permissioned",
    "print_or_ill_only",
    "not_applicable",
}
ALLOWED_SEARCH_AUDIT_DISPOSITIONS = {
    "new_witness",
    "augmented_existing_witness",
    "no_new_witness",
    "rejected_false_positive",
    "access_gap_logged",
    "deferred_followup",
    "methodological_record",
}
ALLOWED_SEARCH_AUDIT_FOLLOW_UP_TYPES = {
    "institutional_query",
    "physical_inspection",
    "image_request",
    "source_acquisition",
    "community_consent_contact",
    "repeat_access_check",
    "none",
}
ALLOWED_CONFIDENCE = {"very_high", "high", "moderate", "low", "very_low", "unknown"}
REQUIRED_WITNESS_FIELDS = {
    "witness_id",
    "shelfmark",
    "collection",
    "city",
    "country",
    "date_ah",
    "date_ce",
    "scribe",
    "languages",
    "folios",
    "dimensions_cm",
    "lines_per_page",
    "contents",
    "completeness",
    "fragment_type",
    "digital_surrogate",
    "decoration",
    "scholarly_attestation",
    "discovery_source",
    "evidence_level",
    "access_level",
    "material_data_level",
    "verification_status",
    "notes",
}
REQUIRED_DECORATION_FIELDS = {
    "paper_description",
    "illumination",
    "binding",
    "data_source",
    "notes",
    "confidence",
}
REQUIRED_ATTESTATION_FIELDS = {"author", "year", "ref"}
REQUIRED_REJECTION_FIELDS = {"rejection_type", "rejection_reason"}
REQUIRED_SEARCH_AUDIT_FIELDS = {
    "record_type",
    "record_date",
    "artifact_status",
    "source_layers",
    "access_mode",
    "disposition",
    "follow_up_required",
    "follow_up_type",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path):
    return json.loads(read_text(path))


def path_exists(path: Path) -> bool:
    return path.exists()


def normalized_text(path: Path) -> str:
    text = " ".join(read_text(path).lower().split())
    return re.sub(r"-\s+", "-", text)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _witness_label(witness: dict) -> str:
    return str(witness.get("witness_id", "<missing witness_id>"))


def _validate_attestation_shape(errors: list[str], witness: dict) -> None:
    witness_id = _witness_label(witness)
    attestations = witness.get("scholarly_attestation")
    if not isinstance(attestations, list):
        fail(errors, f"{witness_id} scholarly_attestation must be an array")
        return

    for index, attestation in enumerate(attestations):
        if not isinstance(attestation, dict):
            fail(errors, f"{witness_id} scholarly_attestation[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_ATTESTATION_FIELDS - attestation.keys())
        if missing:
            fail(
                errors,
                f"{witness_id} scholarly_attestation[{index}] missing fields: {missing}",
            )
        if not isinstance(attestation.get("author"), str):
            fail(errors, f"{witness_id} scholarly_attestation[{index}].author must be a string")
        if "ref" in attestation and not isinstance(attestation.get("ref"), str):
            fail(errors, f"{witness_id} scholarly_attestation[{index}].ref must be a string")
        year = attestation.get("year")
        if year is not None and not isinstance(year, (int, str)):
            fail(errors, f"{witness_id} scholarly_attestation[{index}].year has invalid type")
        if attestation.get("year") == "n.d.":
            fail(errors, f"{witness_id} uses year='n.d.'; use null for unknown year")
        if attestation.get("saw_firsthand", "__missing__") is None:
            fail(errors, f"{witness_id} uses saw_firsthand=null; omit it when unknown")
        saw_firsthand = attestation.get("saw_firsthand", "__missing__")
        if saw_firsthand != "__missing__" and saw_firsthand not in {True, False, "likely"}:
            fail(
                errors,
                f"{witness_id} scholarly_attestation[{index}].saw_firsthand has invalid value",
            )


def _has_firsthand_attestation(witness: dict) -> bool:
    return any(
        attestation.get("saw_firsthand") in {True, "likely"}
        for attestation in witness.get("scholarly_attestation", [])
        if isinstance(attestation, dict)
    )


def _validate_witness_schema(errors: list[str], witness: dict) -> None:
    witness_id = _witness_label(witness)
    missing = sorted(REQUIRED_WITNESS_FIELDS - witness.keys())
    if missing:
        fail(errors, f"{witness_id} missing core fields: {missing}")

    status = witness.get("verification_status")
    if status not in ALLOWED_VERIFICATION_STATUSES:
        fail(errors, f"{witness_id} has unknown verification_status: {status!r}")
    if status == "rejected":
        missing_rejection = sorted(REQUIRED_REJECTION_FIELDS - witness.keys())
        if missing_rejection:
            fail(errors, f"{witness_id} rejected entry missing fields: {missing_rejection}")

    completeness = witness.get("completeness")
    if completeness not in ALLOWED_COMPLETENESS:
        fail(errors, f"{witness_id} has unknown completeness: {completeness!r}")

    evidence_level = witness.get("evidence_level")
    if evidence_level is None:
        fail(errors, f"{witness_id} missing evidence_level")
    elif evidence_level not in ALLOWED_EVIDENCE_LEVELS:
        fail(errors, f"{witness_id} has unknown evidence_level: {evidence_level!r}")

    access_level = witness.get("access_level")
    if access_level is None:
        fail(errors, f"{witness_id} missing access_level")
    elif access_level not in ALLOWED_ACCESS_LEVELS:
        fail(errors, f"{witness_id} has unknown access_level: {access_level!r}")

    material_data_level = witness.get("material_data_level")
    if material_data_level is None:
        fail(errors, f"{witness_id} missing material_data_level")
    elif material_data_level not in ALLOWED_MATERIAL_DATA_LEVELS:
        fail(
            errors,
            f"{witness_id} has unknown material_data_level: {material_data_level!r}",
        )

    if status == "rejected" and material_data_level != "not_applicable_rejected":
        fail(
            errors,
            f"{witness_id} rejected entry must use material_data_level=not_applicable_rejected",
        )
    if status != "rejected" and material_data_level == "not_applicable_rejected":
        fail(
            errors,
            f"{witness_id} non-rejected entry cannot use material_data_level=not_applicable_rejected",
        )

    decoration = witness.get("decoration")
    if not isinstance(decoration, dict):
        fail(errors, f"{witness_id} decoration must be an object")
    else:
        missing_decoration = sorted(REQUIRED_DECORATION_FIELDS - decoration.keys())
        if missing_decoration:
            fail(errors, f"{witness_id} decoration missing fields: {missing_decoration}")
        for key, value in decoration.items():
            if key == "confidence" or key.endswith("_confidence"):
                if value not in ALLOWED_CONFIDENCE:
                    fail(errors, f"{witness_id} decoration.{key} has invalid value: {value!r}")

    _validate_attestation_shape(errors, witness)

    if (
        witness.get("digital_surrogate") is None
        and isinstance(witness.get("colophon"), dict)
        and witness["colophon"].get("iiif_manifest")
        and not witness.get("surrogate_access_note")
    ):
        fail(
            errors,
            f"{witness_id} has colophon.iiif_manifest but no digital_surrogate or surrogate_access_note",
        )

    caveat = str(witness.get("verification_caveat") or "").lower()
    if "primary text" in caveat and not _has_firsthand_attestation(witness):
        fail(
            errors,
            f"{witness_id} claims primary text verification without firsthand evidence",
        )

    contents = str(witness.get("contents") or "")
    if witness_id == "bl_or_9493":
        stale_bl_counts = all(
            token in contents
            for token in ("105 Persian", "87 Turkish", "32 Turkish")
        )
        corrected_counts_visible = all(
            token in contents
            for token in ("Macit corrected", "113", "92", "33")
        )
        if stale_bl_counts and not corrected_counts_visible:
            fail(
                errors,
                "bl_or_9493 contents must surface Macit corrected counts when retaining Minorsky counts",
            )

    if witness.get("contents_discrepancy_flag") and "disputed" not in contents.lower():
        fail(
            errors,
            f"{witness_id} contents_discrepancy_flag requires caveated contents",
        )

    if witness_id == "tehran_university_8198" and "Persian" not in (
        witness.get("languages") or []
    ):
        fail(errors, "tehran_university_8198 languages must include Persian")

    for specific_field, base_field in (
        ("date_ah_specific", "date_ah"),
        ("date_ce_specific", "date_ce"),
    ):
        if specific_field in witness and witness.get(specific_field) == witness.get(base_field):
            fail(errors, f"{witness_id} {specific_field} duplicates {base_field}")

    if witness_id == "nuruosmaniye_04281":
        rejection_text = " ".join(
            str(witness.get(field) or "")
            for field in ("verification_caveat", "rejection_reason", "notes")
        ).lower()
        if any(
            pattern in rejection_text
            for pattern in ("cannot accommodate", "exactly the demographic", "not the demographic")
        ):
            fail(
                errors,
                "nuruosmaniye_04281 rejection wording overstates evidence",
            )


def validate_json_parse(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        try:
            load_json(path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            fail(errors, f"{rel(path)} is invalid JSON: {exc}")


def validate_register(errors: list[str]) -> None:
    register_path = ROOT / "data" / "witness_register.json"
    register = load_json(register_path)
    witnesses = register["witnesses"]
    stats = register["stats"]

    for witness in witnesses:
        _validate_witness_schema(errors, witness)

    witness_ids = [witness.get("witness_id") for witness in witnesses]
    duplicates = sorted(
        witness_id
        for witness_id, count in Counter(witness_ids).items()
        if witness_id and count > 1
    )
    if duplicates:
        fail(errors, f"duplicate witness_id values: {duplicates}")

    expected_stats = compute_stats(register)
    if expected_stats["by_verification"].get("pending", 0) != 0:
        fail(errors, "verification_status pending is not allowed in publication data")
    expected_messages = {
        "total_non_rejected_entries": "stats.total_non_rejected_entries must equal non-rejected witness count",
        "total_verified_or_caveated_witnesses": "stats.total_verified_or_caveated_witnesses must equal verified plus caveated witnesses",
        "total_witnesses_active": "stats.total_witnesses_active must equal non-rejected witness count",
        "total_entries_including_rejected_and_lost": "stats.total_entries_including_rejected_and_lost must equal total witness entry count",
        "by_verification": "stats.by_verification must match computed register counts",
        "by_completeness": "stats.by_completeness must match computed non-rejected completeness counts",
        "by_country": "stats.by_country must match computed non-rejected country counts",
    }
    for key, message in expected_messages.items():
        if stats.get(key) != expected_stats.get(key):
            fail(errors, message)


def validate_spec(errors: list[str]) -> None:
    spec = read_text(ROOT / "data" / "spec.md")
    register = load_json(ROOT / "data" / "witness_register.json")
    generated = register["generated"]
    if f"Generated {generated}" not in spec:
        fail(errors, "data/spec.md generated date does not match witness_register.json")
    if '"candidate_inclusion_criterion"' not in spec:
        fail(errors, "data/spec.md top-level example omits candidate_inclusion_criterion")
    if "total_non_rejected_entries" not in spec:
        fail(errors, "data/spec.md does not document total_non_rejected_entries")


def validate_stale_text(errors: list[str]) -> None:
    stale_patterns = {
        "data/research_log/nuruosmaniye_04281_decoration_extract.md": [
            "Final register status: `candidate_probably_yusuf_hakiki_or_other_homonym`",
            "YEK shows `has_digitized_images: false`, so direct images are not available",
        ],
        "README.md": [
            "All nine Iranian portals were inaccessible",
            "nine remaining gaps that require on-site or in-person work",
            "Negative evidence with confidence:",
            "Partial (seal only):",
            "Qualitative description only:",
            "Unrecovered: 8 of 11",
            "Substantive decoration data is captured for only one non-rejected entry",
            "remaining 8 non-rejected entries have no decoration data",
        ],
        "data/searches/gap_disposition_2026-05-11.json": [
            "Gap disposition for 7 tool-shaped gaps",
            "All 10 tool-shaped gaps",
        ],
        "data/searches/probe_2026-05-11_avenues_rollup_summary.json": [
            "candidate_probably_yusuf_hakiki_or_other_homonym=1, rejected=2",
            "rejected=2 [total=14]",
            "verified=8, verified_with_attribution_caveat=1",
        ],
        "data/witness_register.json": [
            "All Iranian portals BLOCKED to UK/US IPs",
        ],
        "data/spec.md": [
            "alemdari_findings",
        ],
    }
    for relative, patterns in stale_patterns.items():
        text = read_text(ROOT / relative)
        for pattern in patterns:
            if pattern in text:
                fail(errors, f"{relative} contains stale text: {pattern}")

    readme = read_text(ROOT / "README.md").lower()
    ambiguous_readme_patterns = [
        "active entry",
        "active entries",
        "active witness",
        "active witnesses",
    ]
    for pattern in ambiguous_readme_patterns:
        if pattern in readme:
            fail(errors, f"README.md uses ambiguous README terminology: {pattern}")

    if any(
        pattern in readme
        for pattern in (
            "100% institutional",
            "never having entered the market",
            "confirms that the corpus is held",
        )
    ):
        fail(errors, "README.md overstates auction evidence")

    if "cannot accommodate" in readme:
        fail(errors, "README.md overstates Nuruosmaniye size evidence")
    if "exactly the demographic" in readme or "not the demographic" in readme:
        fail(errors, "README.md overstates Nuruosmaniye demographic evidence")


PUBLIC_BOUNDARY_SCAN_SUFFIXES = {".cff", ".json", ".md"}
PUBLIC_BOUNDARY_SCAN_ROOTS = ("data", "docs", "notes")
PUBLIC_BOUNDARY_SCAN_FILES = ("README.md", "CITATION.cff", ".zenodo.json")
PUBLIC_BOUNDARY_RESIDUE_TEXT = {
    ".env": "private environment-file reference",
    "dedup_registry.json": "private registry reference",
    "decorated manuscripts project": "private sibling-project reference",
    "project memory": "agent memory reference",
    "older project memory": "agent memory reference",
    "subagent": "agent-process reference",
    "maincontext": "agent-process reference",
    "main-context": "agent-process reference",
    "api overload": "agent/tool failure reference",
    "api error: overloaded": "agent/tool failure reference",
    "bash-append": "agent checkpoint implementation detail",
    "model-role failure": "agent/tool failure reference",
    "tool-level restriction": "agent/tool restriction reference",
    "credentials included": "browser credential-state reference",
    "bvid": "browser session-token reference",
    "challenge-passed": "browser challenge/session residue",
    "bot challenge": "browser challenge/session residue",
    "parallel research project": "private parallel-project reference",
    "local working pdf": "local working-file reference",
}
PUBLIC_BOUNDARY_RESIDUE_REGEXES = (
    (re.compile(r"[A-Za-z]:\\+"), "local Windows path reference"),
    (re.compile(r"\bprk\b", re.IGNORECASE), "browser session-token reference"),
)


def _iter_public_boundary_scan_paths():
    for relative in PUBLIC_BOUNDARY_SCAN_FILES:
        path = ROOT / relative
        if path.exists():
            yield path
    for root_name in PUBLIC_BOUNDARY_SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in PUBLIC_BOUNDARY_SCAN_SUFFIXES:
                yield path


def validate_public_boundary_residue(errors: list[str]) -> None:
    for path in _iter_public_boundary_scan_paths():
        relative = rel(path)
        text = read_text(path)
        scan_text = f"{relative}\n{text}"
        lower_scan_text = scan_text.lower()
        for pattern, description in PUBLIC_BOUNDARY_RESIDUE_TEXT.items():
            if pattern in lower_scan_text:
                fail(errors, f"{relative} contains {description}: {pattern}")
        for regex, description in PUBLIC_BOUNDARY_RESIDUE_REGEXES:
            if regex.search(scan_text):
                fail(errors, f"{relative} contains {description}")


def validate_search_count_prose(errors: list[str]) -> None:
    stale_patterns = (
        "Final register: 14 audited entries / 12 non-rejected",
        "+ 2 candidates + 1 lost + 2 rejected",
    )
    for path in sorted((ROOT / "data" / "searches").glob("*.json")):
        text = read_text(path)
        for pattern in stale_patterns:
            if pattern in text:
                fail(errors, f"{rel(path)} contains stale register-count prose: {pattern}")


def validate_public_methodology_framing(errors: list[str]) -> None:
    readme_text = read_text(ROOT / "README.md")
    if "?" in readme_text:
        fail(errors, "README.md contains literal '?' characters; check for lost diacritics")

    readme_lower = " ".join(readme_text.lower().split())
    readme_lower = re.sub(r"-\s+", "-", readme_lower)
    forbidden_headline = "a codicological inventory of manuscript witnesses"
    if forbidden_headline in readme_lower:
        fail(errors, "README.md uses old codicological inventory headline")

    required_readme_phrases = [
        "llm-assisted search workflow",
        "inconsistent multilingual catalogues",
        "manuscript witness census",
        "method outputs",
        "llm-assisted workflow",
        "evidence chain",
        "over-definitive coverage claims",
    ]
    for phrase in required_readme_phrases:
        if phrase not in readme_lower:
            fail(errors, f"README.md missing methodology framing phrase: {phrase}")

    for relative_path in (
        "docs/llm-use.md",
        "docs/limitations-and-recovery-plan.md",
    ):
        if not path_exists(ROOT / relative_path):
            fail(errors, f"{relative_path} is missing")

    llm_use_path = ROOT / "docs" / "llm-use.md"
    if path_exists(llm_use_path):
        llm_use_lower = normalized_text(llm_use_path)
        required_llm_use_phrases = [
            "over-definitive coverage claims",
            "wrong shelfmarks",
            "hallucinated bibliographic entries",
            "cross-model llm review",
        ]
        for phrase in required_llm_use_phrases:
            if phrase not in llm_use_lower:
                fail(errors, f"docs/llm-use.md missing LLM caveat phrase: {phrase}")

    metadata = load_json(ROOT / "data" / "metadata.json")
    version = str(metadata.get("version") or "")
    if not version:
        fail(errors, "data/metadata.json missing version")

    version_markers = {
        "data/metadata.json": f'"version": "{version}"',
        ".zenodo.json": f'"version": "{version}"',
        "CITATION.cff": f'version: "{version}"',
    }
    for relative_path in ("data/metadata.json", ".zenodo.json", "CITATION.cff"):
        text = normalized_text(ROOT / relative_path)
        if "llm-assisted search workflow" not in text:
            fail(errors, f"{relative_path} missing LLM-assisted search-workflow framing")
        if "inconsistent multilingual catalogues" not in text:
            fail(errors, f"{relative_path} missing inconsistent-catalogue framing")
        if "over-definitive coverage claims" not in text:
            fail(errors, f"{relative_path} missing LLM caveat framing")
        if version and version_markers[relative_path] not in text:
            fail(errors, f"{relative_path} missing metadata version {version}")
    if version and f"(version {version})" not in readme_lower:
        fail(errors, f"README.md citation block missing Version {version}")


def validate_gap_disposition(errors: list[str]) -> None:
    path = ROOT / "data" / "searches" / "gap_disposition_2026-05-11.json"
    data = load_json(path)
    gap_count = len(data["gaps"])
    summary_count = data["summary"]["total_gaps_addressed"]
    if summary_count != gap_count:
        fail(
            errors,
            f"{rel(path)} summary.total_gaps_addressed={summary_count}, expected {gap_count}",
        )
    if "companion_playwright_gaps_probed" not in data["summary"]:
        fail(errors, f"{rel(path)} summary must state companion Playwright gap count")

    groups = Counter(gap.get("disposition_group") for gap in data["gaps"])
    if None in groups:
        fail(errors, f"{rel(path)} summary.dispositions must match disposition_group counts")
    elif dict(groups) != data["summary"].get("dispositions", {}):
        fail(errors, f"{rel(path)} summary.dispositions must match disposition_group counts")


def validate_search_index(errors: list[str]) -> None:
    searches_dir = ROOT / "data" / "searches"
    index_path = searches_dir / "index.json"
    if not index_path.exists():
        fail(errors, "data/searches/index.json is missing")
        return

    index = load_json(index_path)
    indexed = {record["file"] for record in index.get("records", [])}
    actual = {
        path.name
        for path in searches_dir.glob("*.json")
        if path.name != "index.json"
    }
    missing = sorted(actual - indexed)
    extra = sorted(indexed - actual)
    if missing:
        fail(errors, f"data/searches/index.json missing records: {missing}")
    if extra:
        fail(errors, f"data/searches/index.json references missing files: {extra}")

    for record in index.get("records", []):
        if "current" not in record or "superseded_by" not in record:
            fail(errors, f"search index record lacks current/superseded_by: {record}")
            continue
        superseded_by = record["superseded_by"]
        if not isinstance(superseded_by, list):
            fail(errors, f"search index record superseded_by must be a list: {record}")
            continue
        for target in superseded_by:
            if not isinstance(target, str):
                fail(errors, f"search index superseded_by target must be a string: {record}")
                continue
            target_path = (searches_dir / target).resolve()
            try:
                target_path.relative_to(ROOT)
            except ValueError:
                fail(errors, f"search index superseded_by target escapes repo: {target}")
                continue
            if not target_path.exists():
                fail(errors, f"search index superseded_by target missing: {target}")


def validate_search_audit_metadata(errors: list[str]) -> None:
    searches_dir = ROOT / "data" / "searches"
    spec_path = searches_dir / "spec.md"
    if not spec_path.exists():
        fail(errors, "data/searches/spec.md is missing")

    index_path = searches_dir / "index.json"
    if not index_path.exists():
        fail(errors, "data/searches/index.json is missing")
        return
    index = load_json(index_path)
    current_by_file = {
        record.get("file"): record.get("current")
        for record in index.get("records", [])
    }

    for path in sorted(searches_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        data = load_json(path)
        metadata = data.get("audit_metadata")
        if not isinstance(metadata, dict):
            fail(errors, f"{rel(path)} missing audit_metadata object")
            continue

        missing = sorted(REQUIRED_SEARCH_AUDIT_FIELDS - metadata.keys())
        if missing:
            fail(errors, f"{rel(path)} audit_metadata missing fields: {missing}")
            continue

        record_type = metadata.get("record_type")
        if record_type not in ALLOWED_SEARCH_AUDIT_RECORD_TYPES:
            fail(errors, f"{rel(path)} audit_metadata.record_type invalid: {record_type!r}")

        record_date = metadata.get("record_date")
        if record_date is not None and not (
            isinstance(record_date, str)
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", record_date)
        ):
            fail(errors, f"{rel(path)} audit_metadata.record_date must be YYYY-MM-DD or null")

        artifact_status = metadata.get("artifact_status")
        if artifact_status not in ALLOWED_SEARCH_AUDIT_STATUSES:
            fail(errors, f"{rel(path)} audit_metadata.artifact_status invalid: {artifact_status!r}")
        indexed_current = current_by_file.get(path.name)
        if indexed_current is True and artifact_status != "current":
            fail(errors, f"{rel(path)} audit_metadata.artifact_status must be current")
        if indexed_current is False and artifact_status == "current":
            fail(errors, f"{rel(path)} superseded index record cannot have current artifact_status")

        source_layers = metadata.get("source_layers")
        if not isinstance(source_layers, list) or not source_layers:
            fail(errors, f"{rel(path)} audit_metadata.source_layers must be a non-empty array")
        else:
            invalid_layers = sorted(set(source_layers) - ALLOWED_SEARCH_AUDIT_SOURCE_LAYERS)
            if invalid_layers:
                fail(errors, f"{rel(path)} audit_metadata.source_layers invalid: {invalid_layers}")

        access_mode = metadata.get("access_mode")
        if access_mode not in ALLOWED_SEARCH_AUDIT_ACCESS_MODES:
            fail(errors, f"{rel(path)} audit_metadata.access_mode invalid: {access_mode!r}")

        disposition = metadata.get("disposition")
        if disposition not in ALLOWED_SEARCH_AUDIT_DISPOSITIONS:
            fail(errors, f"{rel(path)} audit_metadata.disposition invalid: {disposition!r}")

        follow_up_required = metadata.get("follow_up_required")
        follow_up_type = metadata.get("follow_up_type")
        if not isinstance(follow_up_required, bool):
            fail(errors, f"{rel(path)} audit_metadata.follow_up_required must be boolean")
        if follow_up_type not in ALLOWED_SEARCH_AUDIT_FOLLOW_UP_TYPES:
            fail(errors, f"{rel(path)} audit_metadata.follow_up_type invalid: {follow_up_type!r}")
        elif follow_up_required is False and follow_up_type != "none":
            fail(errors, f"{rel(path)} audit_metadata.follow_up_type must be none without follow-up")
        elif follow_up_required is True and follow_up_type == "none":
            fail(errors, f"{rel(path)} audit_metadata.follow_up_type must name required follow-up")


def _search_index_counts() -> dict[str, int]:
    index = load_json(ROOT / "data" / "searches" / "index.json")
    records = index.get("records", [])
    return {
        "total": len(records),
        "current": sum(1 for record in records if record.get("current") is True),
        "superseded": sum(1 for record in records if record.get("current") is False),
    }


def _count_string_values(value) -> int:
    if isinstance(value, str):
        return 1
    if isinstance(value, list):
        return sum(_count_string_values(item) for item in value)
    if isinstance(value, dict):
        return sum(
            _count_string_values(nested)
            for key, nested in value.items()
            if not key.startswith("_")
        )
    return 0


def _search_key_matrix_count() -> int:
    keys = load_json(ROOT / "data" / "search_keys.json")
    base_blocks = (
        "author_forms",
        "title_forms",
        "catalogue_context_keys",
        "scribe_and_colophon_keys",
        "nesimi_adjacency_keys",
    )
    base_count = sum(_count_string_values(keys[block]) for block in base_blocks)
    script_count = sum(
        _count_string_values(value)
        for family in keys["script_families"].values()
        if isinstance(family, dict)
        for key, value in family.items()
        if key.endswith("_variants")
    )
    south_asian_queries = keys["south_asian_haqiqi_homonym_treatment"][
        "query_families"
    ]
    south_asian_count = _count_string_values(
        south_asian_queries["latin"]
    ) + _count_string_values(south_asian_queries["persian_urdu"])
    return (
        base_count
        + script_count
        + _count_string_values(keys["alevi_community_route_terms"])
        + south_asian_count
    )


DIRECT_QUERY_FIELD_NAMES = {"query", "search_term", "term", "q"}


def _direct_query_values(value) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in DIRECT_QUERY_FIELD_NAMES:
                values.extend(_string_query_values(nested))
            values.extend(_direct_query_values(nested))
    elif isinstance(value, list):
        for item in value:
            values.extend(_direct_query_values(item))
    return values


def _string_query_values(value) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            values.extend(_string_query_values(item))
        return values
    return []


def _direct_query_field_counts() -> dict[str, int]:
    values: list[str] = []
    for path in sorted((ROOT / "data" / "searches").glob("*.json")):
        values.extend(_direct_query_values(load_json(path)))
    return {
        "occurrences": len(values),
        "unique": len(set(values)),
    }


def _validate_regex_counts(
    errors: list[str],
    relative_path: str,
    patterns: list[str],
    expected: int,
    label: str,
) -> None:
    text = read_text(ROOT / relative_path)
    for pattern in patterns:
        matches = [int(match) for match in re.findall(pattern, text, flags=re.IGNORECASE)]
        if not matches:
            fail(errors, f"{relative_path} missing {label} count pattern: {pattern}")
            continue
        stale = [value for value in matches if value != expected]
        if stale:
            fail(
                errors,
                f"{relative_path} has stale {label} count(s) {stale}; expected {expected}",
            )


def validate_public_search_counts(errors: list[str]) -> None:
    counts = _search_index_counts()
    _validate_regex_counts(
        errors,
        "docs/search-scope-statistics.md",
        [
            r"\|\s*Indexed search/action artifacts\s*\|\s*(\d+)\s*\|",
            r"documented by\s+(\d+)\s+indexed search/action records",
        ],
        counts["total"],
        "indexed search/action artifact",
    )
    _validate_regex_counts(
        errors,
        "docs/search-scope-statistics.md",
        [r"\|\s*Current search/action artifacts\s*\|\s*(\d+)\s*\|"],
        counts["current"],
        "current search/action artifact",
    )
    _validate_regex_counts(
        errors,
        "docs/search-scope-statistics.md",
        [
            r"\|\s*(?:Superseded provenance artifacts|Non-current search/action artifacts)\s*\|\s*(\d+)\s*\|"
        ],
        counts["superseded"],
        "non-current search/action artifact",
    )

    _validate_regex_counts(
        errors,
        "README.md",
        [
            r"holds\s+(\d+)\s+search-session and action records",
            r"\[`data/searches/`\]\(data/searches/\):\s+(\d+)\s+search-session and action records",
            r"(\d+)\s+indexed search-session and action records",
        ],
        counts["total"],
        "indexed search/action artifact",
    )
    for relative_path in (
        "data/metadata.json",
        ".zenodo.json",
        "CITATION.cff",
    ):
        _validate_regex_counts(
            errors,
            relative_path,
            [r"(\d+)\s+indexed search(?:/action|-session and action) records"],
            counts["total"],
            "indexed search/action artifact",
        )

    search_key_count = _search_key_matrix_count()
    for relative_path in (
        "README.md",
        "docs/search-scope-statistics.md",
        "data/metadata.json",
        ".zenodo.json",
        "CITATION.cff",
    ):
        _validate_regex_counts(
            errors,
            relative_path,
            [
                r"(\d+)(?:-string(?: multilingual)? search-key matrix|\s+reusable search-key/query strings)"
            ],
            search_key_count,
            "search-key matrix",
        )

    direct_query_counts = _direct_query_field_counts()
    _validate_regex_counts(
        errors,
        "docs/search-scope-statistics.md",
        [r"\|\s*Direct query-field occurrences in logs\s*\|\s*(\d+)\s*\|"],
        direct_query_counts["occurrences"],
        "direct query-field occurrence",
    )
    _validate_regex_counts(
        errors,
        "docs/search-scope-statistics.md",
        [r"\|\s*Unique direct query-field values in logs\s*\|\s*(\d+)\s*\|"],
        direct_query_counts["unique"],
        "unique direct query-field value",
    )


def validate_extract_index(errors: list[str]) -> None:
    directory = ROOT / "data" / "extracts"
    index_path = directory / "index.json"
    if not index_path.exists():
        fail(errors, "data/extracts/index.json is missing")
        return

    index = load_json(index_path)
    indexed = {record["file"] for record in index.get("records", [])}
    actual = {path.name for path in directory.glob("*.json") if path.name != "index.json"}
    missing = sorted(actual - indexed)
    extra = sorted(indexed - actual)
    if missing:
        fail(errors, f"data/extracts/index.json missing records: {missing}")
    if extra:
        fail(errors, f"data/extracts/index.json references missing files: {extra}")

    required = {"file", "artifact_type", "current", "release_blocker", "note"}
    for record in index.get("records", []):
        missing_fields = sorted(required - record.keys())
        if missing_fields:
            fail(
                errors,
                f"extract index record for {record.get('file', '<unknown>')} missing {missing_fields}",
            )
        if "current" in record and not isinstance(record["current"], bool):
            fail(errors, f"extract index current must be boolean: {record}")
        if "release_blocker" in record and not isinstance(record["release_blocker"], bool):
            fail(errors, f"extract index release_blocker must be boolean: {record}")


def validate_teece_extract(errors: list[str]) -> None:
    path = ROOT / "data" / "extracts" / "teece_2016_pir_budaq_corpus.json"
    data = load_json(path)
    entries = data["appendix_b_pir_budaq_manuscripts"]["entries"]
    keys: dict[tuple[object, ...], list[int]] = defaultdict(list)
    for index, entry in enumerate(entries):
        key = (
            entry.get("shelfmark"),
            entry.get("current_location"),
            entry.get("text"),
            entry.get("date_ah"),
            entry.get("date_ce"),
        )
        keys[key].append(index)
    duplicates = {key: idxs for key, idxs in keys.items() if len(idxs) > 1}
    if duplicates:
        fail(errors, f"{rel(path)} has duplicate Appendix B compound keys: {duplicates}")


def _iter_string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _iter_string_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_string_values(nested)


def _validate_source_witness_ids(errors: list[str], path: Path, data: dict) -> None:
    register = load_json(ROOT / "data" / "witness_register.json")
    witness_ids = {witness["witness_id"] for witness in register["witnesses"]}

    def walk(value, object_path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                nested_path = object_path + (key,)
                if key.endswith("witness_id") and isinstance(nested, str):
                    if nested not in witness_ids:
                        fail(
                            errors,
                            f"{rel(path)} {'/'.join(nested_path)} unknown source_witness_id: {nested}",
                        )
                walk(nested, nested_path)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, object_path + (str(index),))

    walk(data)


def _validate_no_untracked_temp_references(errors: list[str], path: Path, data: dict) -> None:
    for value in _iter_string_values(data):
        normalized = value.replace("\\", "/")
        if "tmp/" in normalized:
            fail(errors, f"{rel(path)} contains untracked temp reference: {value}")


def _validate_dogan_kaya_extract(errors: list[str], path: Path, data: dict) -> None:
    placeholder_values = {"boyutundadır.", "boyutlarındadır."}
    non_holder_fragments = (
        "boyutundadır",
        "boyutlarındadır",
        "Cönkte yer alan",
        "Cönkte;",
        "Cönkün tamamında",
        "Şiirlerin",
        "Üç tane",
        "Sonunda Latin harfleriyle",
    )
    malformed_owner_fragments = {"Cönkün aslı Yrd.", "Cönkün aslı, Yrd."}
    for entry in data.get("entries", []):
        holder = str(entry.get("holder_or_owner_raw") or "").strip()
        if holder in placeholder_values:
            fail(
                errors,
                f"{rel(path)} conk {entry.get('conk_no')} has placeholder holder_or_owner_raw",
            )
        elif any(fragment in holder for fragment in non_holder_fragments):
            fail(
                errors,
                f"{rel(path)} conk {entry.get('conk_no')} has non-holder holder_or_owner_raw",
            )
        elif (
            holder in malformed_owner_fragments
            or re.search(r"\d+(?:[,.]\d+)?\s*x\s*\d+(?:[,.]\d+)?\s*cm\b", holder)
            or re.match(r"^\d{3,4}\)\s+yıl", holder)
        ):
            fail(
                errors,
                f"{rel(path)} conk {entry.get('conk_no')} has malformed holder_or_owner_raw",
            )


def validate_extracts(errors: list[str]) -> None:
    for path in sorted((ROOT / "data" / "extracts").glob("*.json")):
        if path.name == "index.json":
            continue
        data = load_json(path)
        _validate_source_witness_ids(errors, path, data)
        _validate_no_untracked_temp_references(errors, path, data)
        if path.name == "dogan_kaya_2011_conk_corpus.json":
            _validate_dogan_kaya_extract(errors, path, data)

    for path in sorted((ROOT / "data" / "searches").glob("*.json")):
        data = load_json(path)
        _validate_no_untracked_temp_references(errors, path, data)


def validate_tezkire_index(errors: list[str]) -> None:
    directory = ROOT / "data" / "tezkire_extracts"
    index_path = directory / "index.json"
    if not index_path.exists():
        fail(errors, "data/tezkire_extracts/index.json is missing")
        return

    index = load_json(index_path)
    indexed = {record["file"] for record in index.get("records", [])}
    actual = {path.name for path in directory.glob("*.md")}
    missing = sorted(actual - indexed)
    extra = sorted(indexed - actual)
    if missing:
        fail(errors, f"data/tezkire_extracts/index.json missing records: {missing}")
    if extra:
        fail(errors, f"data/tezkire_extracts/index.json references missing files: {extra}")

    required = {"file", "source_type", "source_citation", "access", "extraction_date"}
    for record in index.get("records", []):
        missing_fields = sorted(required - record.keys())
        if missing_fields:
            fail(
                errors,
                f"tezkire index record for {record.get('file', '<unknown>')} missing {missing_fields}",
            )


def validate_metadata_surface(errors: list[str]) -> None:
    metadata_path = ROOT / "data" / "metadata.json"
    if not metadata_path.exists():
        fail(errors, "data/metadata.json is missing")
        return

    metadata = load_json(metadata_path)
    required = {
        "title",
        "version",
        "doi",
        "license",
        "release_date",
        "authors",
        "keywords",
        "subjects",
        "related_identifiers",
        "intro",
        "search_key_summary",
        "alevi_summary",
        "methodology_summary",
    }
    missing = sorted(required - metadata.keys())
    if missing:
        fail(errors, f"data/metadata.json missing fields: {missing}")

    if len(metadata.get("authors", [])) < 1:
        fail(errors, "data/metadata.json must define at least one author")

    alevi_summary = str(metadata.get("alevi_summary") or "").lower()
    if (
        "complete unphotographed divan codex" in alevi_summary
        and "reports" not in alevi_summary
    ):
        fail(
            errors,
            "data/metadata.json alevi_summary must describe the reported complete, unphotographed divan codex",
        )

    renderer = ROOT / "scripts" / "render_metadata.py"
    if not renderer.exists():
        fail(errors, "scripts/render_metadata.py is missing")
        return

    result = subprocess.run(
        [sys.executable, str(renderer), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        fail(errors, f"render_metadata.py --check failed:\n{result.stdout.strip()}")


def validate_release_assets(errors: list[str]) -> None:
    required = [
        ROOT / "scripts" / "release_check.py",
        ROOT / "docs" / "release-checklist.md",
        ROOT / "docs" / "release-notes-v1.0.md",
    ]
    for path in required:
        if not path.exists():
            fail(errors, f"{rel(path)} is missing")

    release_notes_path = ROOT / "docs" / "release-notes-v1.0.md"
    if release_notes_path.exists():
        release_notes = read_text(release_notes_path)
        if release_notes.count("```") % 2 != 0:
            fail(errors, "docs/release-notes-v1.0.md has an unclosed fenced code block")
        if "python scripts\\render_metadata.py --write" not in release_notes:
            fail(
                errors,
                "docs/release-notes-v1.0.md must include the metadata render command",
            )


def main() -> int:
    errors: list[str] = []
    validate_json_parse(errors)
    validate_register(errors)
    validate_spec(errors)
    validate_stale_text(errors)
    validate_public_boundary_residue(errors)
    validate_public_methodology_framing(errors)
    validate_gap_disposition(errors)
    validate_search_index(errors)
    validate_search_audit_metadata(errors)
    validate_public_search_counts(errors)
    validate_search_count_prose(errors)
    validate_extract_index(errors)
    validate_teece_extract(errors)
    validate_extracts(errors)
    validate_tezkire_index(errors)
    validate_metadata_surface(errors)
    validate_release_assets(errors)

    if errors:
        print("Dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Dataset validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
