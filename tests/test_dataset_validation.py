from __future__ import annotations

import copy
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_dataset.py"
RELEASE_CHECK_PATH = ROOT / "scripts" / "release_check.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_dataset", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load scripts/validate_dataset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_release_check():
    spec = importlib.util.spec_from_file_location("release_check", RELEASE_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load scripts/release_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def witness_by_id(register: dict, witness_id: str) -> dict:
    return next(w for w in register["witnesses"] if w["witness_id"] == witness_id)


class DatasetValidationTests(unittest.TestCase):
    def test_spec_example_does_not_use_nd_year(self) -> None:
        spec = (ROOT / "data" / "spec.md").read_text(encoding="utf-8")

        self.assertNotIn('"year": "n.d."', spec)

    def test_validate_register_rejects_stale_total_active_alias(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["stats"]["total_witnesses_active"] += 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("stats.total_witnesses_active" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_stale_total_entries(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["stats"]["total_entries_including_rejected_and_lost"] += 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any(
                "stats.total_entries_including_rejected_and_lost" in error
                for error in errors
            ),
            errors,
        )

    def test_validate_register_rejects_stale_completeness_counts(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["stats"]["by_completeness"]["complete"] += 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("stats.by_completeness" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_stale_country_counts(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["stats"]["by_country"]["Turkey"] += 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("stats.by_country" in error for error in errors), errors)

    def test_validate_register_rejects_unknown_status_even_when_stats_match(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = broken["witnesses"][0]
        witness["verification_status"] = "verfied"
        broken["stats"]["by_verification"]["verified"] -= 1
        broken["stats"]["by_verification"]["verfied"] = 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("unknown verification_status" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_publication_pending_status(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["witnesses"][0]["verification_status"] = "pending"
        broken["stats"] = validator.compute_stats(broken)

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("pending" in error for error in errors), errors)

    def test_validate_register_rejects_duplicate_witness_id(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["witnesses"][1]["witness_id"] = broken["witnesses"][0]["witness_id"]

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("duplicate witness_id" in error for error in errors), errors)

    def test_validate_register_requires_rejection_metadata(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "baku_doerfer_unspecified")
        witness.pop("rejection_reason")
        witness.pop("rejection_type")

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("rejected entry missing" in error for error in errors), errors)

    def test_validate_register_requires_evidence_axes(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["witnesses"][0].pop("evidence_level", None)

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("missing evidence_level" in error for error in errors), errors)

    def test_validate_register_rejects_unknown_evidence_axis_value(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["witnesses"][0]["access_level"] = "maybe_online"

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("unknown access_level" in error for error in errors), errors)

    def test_validate_register_rejects_rejected_entry_without_rejected_material_level(
        self,
    ) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        rejected = witness_by_id(broken, "nuruosmaniye_04281")
        rejected["material_data_level"] = "substantive_material_evidence"

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("rejected entry must use material_data_level" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_unknown_completeness_even_when_stats_match(
        self,
    ) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = broken["witnesses"][0]
        witness["completeness"] = "complet"
        broken["stats"]["by_completeness"]["complete"] -= 1
        broken["stats"]["by_completeness"]["complet"] = 1

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("unknown completeness" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_missing_core_fields(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        del broken["witnesses"][0]["shelfmark"]

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("missing core fields" in error for error in errors), errors)

    def test_validate_register_rejects_invalid_decoration_confidence(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        broken["witnesses"][0]["decoration"]["confidence"] = "confident"

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("decoration.confidence" in error for error in errors), errors)

    def test_validate_register_requires_surrogate_note_for_nested_manifest(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "nuruosmaniye_04281")
        witness.pop("surrogate_access_note", None)

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(any("surrogate_access_note" in error for error in errors), errors)

    def test_validate_register_rejects_primary_text_caveat_without_firsthand_evidence(
        self,
    ) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "ilkhchi_kirklar_ocagi_full_divan")
        witness["verification_caveat"] = "Existence verified via primary text."

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any(
                "claims primary text verification without firsthand evidence" in error
                for error in errors
            ),
            errors,
        )

    def test_validate_register_rejects_uncaveated_bl_contents_counts(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "bl_or_9493")
        witness["contents"] = (
            "105 Persian ghazals + 1 mustazad; 87 Turkish ghazals; "
            "32 Turkish quatrains"
        )

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("bl_or_9493 contents must surface Macit corrected counts" in error for error in errors),
            errors,
        )

    def test_validate_register_requires_disputed_contents_caveat(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "matenadaran_965")
        witness["contents_discrepancy_flag"] = "counts diverge"
        witness["contents"] = "32 Persian mesnevis; 114 Persian ghazals"

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("contents_discrepancy_flag requires caveated contents" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_nuruosmaniye_overstatement(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "nuruosmaniye_04281")
        witness["rejection_reason"] = (
            "326 folios cannot accommodate Cihanshah; exactly the demographic "
            "that preserved Yusuf Hakiki."
        )

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("nuruosmaniye_04281 rejection wording overstates evidence" in error for error in errors),
            errors,
        )

    def test_validate_register_requires_tehran_persian_language(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "tehran_university_8198")
        witness["languages"] = ["Turkish"]

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("tehran_university_8198 languages must include Persian" in error for error in errors),
            errors,
        )

    def test_validate_register_rejects_duplicate_specific_date_fields(self) -> None:
        validator = load_validator()
        register = validator.load_json(ROOT / "data" / "witness_register.json")
        broken = copy.deepcopy(register)
        witness = witness_by_id(broken, "matenadaran_965")
        witness["date_ah_specific"] = witness["date_ah"]
        witness["date_ce_specific"] = witness["date_ce"]

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_register(errors)

        self.assertTrue(
            any("date_ah_specific duplicates date_ah" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("date_ce_specific duplicates date_ce" in error for error in errors),
            errors,
        )

    def test_validate_metadata_surface_rejects_unexamined_divan_overclaim(self) -> None:
        validator = load_validator()
        metadata = validator.load_json(ROOT / "data" / "metadata.json")
        broken = copy.deepcopy(metadata)
        broken["alevi_summary"] = (
            "The Alevi shrine corpus preserves eleven ghazals plus a complete "
            "unphotographed divan codex."
        )

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_metadata_surface(errors)

        self.assertTrue(
            any("reported complete, unphotographed divan codex" in error for error in errors),
            errors,
        )

    def test_validate_stale_text_rejects_active_terminology_in_readme(self) -> None:
        validator = load_validator()
        text_by_path = {
            "README.md": "11 active entries",
            "data/witness_register.json": "",
            "data/spec.md": "",
            "data/research_log/nuruosmaniye_04281_decoration_extract.md": "",
            "data/searches/gap_disposition_2026-05-11.json": "",
            "data/searches/probe_2026-05-11_avenues_rollup_summary.json": "",
        }

        with mock.patch.object(
            validator,
            "read_text",
            side_effect=lambda path: text_by_path[validator.rel(path)],
        ):
            errors: list[str] = []
            validator.validate_stale_text(errors)

        self.assertTrue(any("ambiguous README terminology" in error for error in errors), errors)

    def test_validate_stale_text_rejects_public_overclaims(self) -> None:
        validator = load_validator()
        text_by_path = {
            "README.md": (
                "auction archives confirm never having entered the market; "
                "326-folio codex cannot accommodate; exactly the demographic"
            ),
            "data/witness_register.json": "",
            "data/spec.md": "",
            "data/research_log/nuruosmaniye_04281_decoration_extract.md": "",
            "data/searches/gap_disposition_2026-05-11.json": "",
            "data/searches/probe_2026-05-11_avenues_rollup_summary.json": "",
        }

        with mock.patch.object(
            validator,
            "read_text",
            side_effect=lambda path: text_by_path[validator.rel(path)],
        ):
            errors: list[str] = []
            validator.validate_stale_text(errors)

        self.assertTrue(any("overstates auction evidence" in error for error in errors), errors)
        self.assertTrue(any("overstates Nuruosmaniye size evidence" in error for error in errors), errors)
        self.assertTrue(any("overstates Nuruosmaniye demographic evidence" in error for error in errors), errors)

    def test_validate_stale_text_rejects_stale_register_and_rollup_phrases(self) -> None:
        validator = load_validator()
        text_by_path = {
            "README.md": "",
            "data/witness_register.json": "All Iranian portals BLOCKED to UK/US IPs",
            "data/spec.md": "alemdari_findings",
            "data/research_log/nuruosmaniye_04281_decoration_extract.md": "",
            "data/searches/gap_disposition_2026-05-11.json": "",
            "data/searches/probe_2026-05-11_avenues_rollup_summary.json": (
                "verified=8, verified_with_attribution_caveat=1"
            ),
        }

        with mock.patch.object(
            validator,
            "read_text",
            side_effect=lambda path: text_by_path[validator.rel(path)],
        ):
            errors: list[str] = []
            validator.validate_stale_text(errors)

        self.assertTrue(any("All Iranian portals BLOCKED" in error for error in errors), errors)
        self.assertTrue(any("alemdari_findings" in error for error in errors), errors)
        self.assertTrue(any("verified=8" in error for error in errors), errors)


    def test_validate_public_boundary_residue_rejects_private_workflow_terms(self) -> None:
        validator = load_validator()
        path = ROOT / "data" / "searches" / "private_residue.json"

        with mock.patch.object(
            validator,
            "_iter_public_boundary_scan_paths",
            return_value=[path],
        ), mock.patch.object(
            validator,
            "read_text",
            return_value="Used .env auth from Z:\\redacted-local-tool and bvid token state.",
        ):
            errors: list[str] = []
            validator.validate_public_boundary_residue(errors)

        self.assertTrue(any("private environment-file reference" in error for error in errors), errors)
        self.assertTrue(any("local Windows path reference" in error for error in errors), errors)
        self.assertTrue(any("browser session-token reference" in error for error in errors), errors)

    def test_validate_search_count_prose_rejects_stale_final_register_counts(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            searches = root / "data" / "searches"
            searches.mkdir(parents=True)
            (searches / "search.json").write_text(
                '"Final register: 14 audited entries / 12 non-rejected / '
                '9 verified-or-with-caveat witnesses + 2 candidates + 1 lost + 2 rejected"',
                encoding="utf-8",
            )
            original_root = validator.ROOT
            validator.ROOT = root
            try:
                errors: list[str] = []
                validator.validate_search_count_prose(errors)
            finally:
                validator.ROOT = original_root

        self.assertTrue(any("stale register-count prose" in error for error in errors), errors)

    def test_validate_gap_disposition_requires_summary_groups(self) -> None:
        validator = load_validator()
        data = validator.load_json(ROOT / "data" / "searches" / "gap_disposition_2026-05-11.json")
        broken = copy.deepcopy(data)
        for gap in broken["gaps"]:
            gap.pop("disposition_group", None)

        with mock.patch.object(validator, "load_json", return_value=broken):
            errors: list[str] = []
            validator.validate_gap_disposition(errors)

        self.assertTrue(
            any("summary.dispositions must match disposition_group counts" in error for error in errors),
            errors,
        )

    def test_validate_search_index_rejects_missing_superseded_by_target(self) -> None:
        validator = load_validator()
        data_by_path = {
            "index.json": {
                "records": [
                    {
                        "file": "search_2026-05-02_auctions.json",
                        "current": False,
                        "superseded_by": ["missing_target.json"],
                    }
                ]
            }
        }

        def fake_load_json(path: Path) -> dict:
            return data_by_path[path.name]

        with (
            mock.patch.object(validator, "load_json", side_effect=fake_load_json),
            mock.patch.object(
                validator.Path,
                "glob",
                return_value=[
                    ROOT / "data" / "searches" / "search_2026-05-02_auctions.json",
                ],
            ),
        ):
            errors: list[str] = []
            validator.validate_search_index(errors)

        self.assertTrue(
            any("superseded_by target missing" in error for error in errors),
            errors,
        )

    def test_validate_search_audit_metadata_rejects_missing_object(self) -> None:
        validator = load_validator()
        data_by_path = {
            "index.json": {
                "records": [
                    {
                        "file": "search_2026-05-02_auctions.json",
                        "current": True,
                    }
                ]
            },
            "search_2026-05-02_auctions.json": {},
        }

        def fake_load_json(path: Path) -> dict:
            return data_by_path[path.name]

        with (
            mock.patch.object(validator, "load_json", side_effect=fake_load_json),
            mock.patch.object(validator.Path, "exists", return_value=True),
            mock.patch.object(
                validator.Path,
                "glob",
                return_value=[
                    ROOT / "data" / "searches" / "search_2026-05-02_auctions.json",
                ],
            ),
        ):
            errors: list[str] = []
            validator.validate_search_audit_metadata(errors)

        self.assertTrue(any("missing audit_metadata object" in error for error in errors), errors)

    def test_validate_search_audit_metadata_rejects_followup_inconsistency(self) -> None:
        validator = load_validator()
        data_by_path = {
            "index.json": {
                "records": [
                    {
                        "file": "search_2026-05-02_auctions.json",
                        "current": True,
                    }
                ]
            },
            "search_2026-05-02_auctions.json": {
                "audit_metadata": {
                    "record_type": "catalogue_probe",
                    "record_date": "2026-05-02",
                    "artifact_status": "current",
                    "source_layers": ["catalogue_record"],
                    "access_mode": "open_web",
                    "disposition": "no_new_witness",
                    "follow_up_required": True,
                    "follow_up_type": "none",
                }
            },
        }

        def fake_load_json(path: Path) -> dict:
            return data_by_path[path.name]

        with (
            mock.patch.object(validator, "load_json", side_effect=fake_load_json),
            mock.patch.object(validator.Path, "exists", return_value=True),
            mock.patch.object(
                validator.Path,
                "glob",
                return_value=[
                    ROOT / "data" / "searches" / "search_2026-05-02_auctions.json",
                ],
            ),
        ):
            errors: list[str] = []
            validator.validate_search_audit_metadata(errors)

        self.assertTrue(
            any("follow_up_type must name required follow-up" in error for error in errors),
            errors,
        )

    def test_validate_public_search_counts_matches_search_index(self) -> None:
        validator = load_validator()

        errors: list[str] = []
        validator.validate_public_search_counts(errors)

        self.assertEqual(errors, [])

    def test_validate_public_search_counts_rejects_stale_direct_query_counts(
        self,
    ) -> None:
        validator = load_validator()
        original_read_text = validator.read_text

        def fake_read_text(path: Path) -> str:
            text = original_read_text(path)
            if validator.rel(path) != "docs/search-scope-statistics.md":
                return text
            text = re.sub(
                r"(\|\s*Direct query-field occurrences in logs\s*\|\s*)\d+",
                r"\g<1>1",
                text,
            )
            return re.sub(
                r"(\|\s*Unique direct query-field values in logs\s*\|\s*)\d+",
                r"\g<1>1",
                text,
            )

        with mock.patch.object(validator, "read_text", side_effect=fake_read_text):
            errors: list[str] = []
            validator.validate_public_search_counts(errors)

        self.assertTrue(
            any("direct query-field occurrence" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("unique direct query-field value" in error for error in errors),
            errors,
        )

    def test_validate_public_framing_rejects_codicological_inventory_headline(
        self,
    ) -> None:
        validator = load_validator()
        text_by_path = {
            "README.md": "A codicological inventory of manuscript witnesses",
            "data/metadata.json": "{}",
            ".zenodo.json": "{}",
            "CITATION.cff": "",
            "docs/llm-use.md": "over-definitive coverage claims wrong shelfmarks hallucinated bibliographic entries cross-model llm review",
        }

        with mock.patch.object(
            validator,
            "read_text",
            side_effect=lambda path: text_by_path[validator.rel(path)],
        ):
            errors: list[str] = []
            validator.validate_public_methodology_framing(errors)

        self.assertTrue(
            any("codicological inventory headline" in error for error in errors),
            errors,
        )

    def test_validate_public_framing_requires_llm_methodology_docs(self) -> None:
        validator = load_validator()
        valid_readme = (
            "manuscript witness census; "
            "llm-assisted search workflow; inconsistent multilingual catalogues; "
            "method outputs; llm-assisted workflow; evidence chain; over-definitive coverage claims; "
            "(Version 1.0.0)"
        )
        valid_generated = "llm-assisted search workflow inconsistent multilingual catalogues over-definitive coverage claims 1.0.0"
        text_by_path = {
            "README.md": valid_readme,
            "data/metadata.json": (
                '{"version": "1.0.0", '
                '"intro": "llm-assisted search workflow inconsistent multilingual catalogues over-definitive coverage claims"}'
            ),
            ".zenodo.json": valid_generated,
            "CITATION.cff": valid_generated,
            "docs/llm-use.md": "over-definitive coverage claims wrong shelfmarks hallucinated bibliographic entries cross-model llm review",
            "docs/limitations-and-recovery-plan.md": "limits",
        }

        with (
            mock.patch.object(
                validator,
                "read_text",
                side_effect=lambda path: text_by_path[validator.rel(path)],
            ),
            mock.patch.object(validator, "load_json", return_value={"version": "1.0.0"}),
            mock.patch.object(validator, "path_exists", return_value=False),
        ):
            errors: list[str] = []
            validator.validate_public_methodology_framing(errors)

        self.assertTrue(any("docs/llm-use.md is missing" in error for error in errors), errors)
        self.assertTrue(
            any("docs/limitations-and-recovery-plan.md is missing" in error for error in errors),
            errors,
        )

    def test_validate_public_framing_rejects_readme_question_mark_mojibake(self) -> None:
        validator = load_validator()
        valid_generated = "llm-assisted search workflow inconsistent multilingual catalogues over-definitive coverage claims 1.0.0"
        text_by_path = {
            "README.md": (
                "manuscript witness census; "
                "llm-assisted search workflow; inconsistent multilingual catalogues; "
                "method outputs; llm-assisted workflow; evidence chain; over-definitive coverage claims; "
                "Hak?k? (Version 1.0.0)"
            ),
            "data/metadata.json": (
                '{"version": "1.0.0", '
                '"intro": "llm-assisted search workflow inconsistent multilingual catalogues over-definitive coverage claims"}'
            ),
            ".zenodo.json": valid_generated,
            "CITATION.cff": valid_generated,
            "docs/llm-use.md": "over-definitive coverage claims wrong shelfmarks hallucinated bibliographic entries cross-model llm review",
            "docs/limitations-and-recovery-plan.md": "limits",
        }

        with (
            mock.patch.object(
                validator,
                "read_text",
                side_effect=lambda path: text_by_path[validator.rel(path)],
            ),
            mock.patch.object(validator, "load_json", return_value={"version": "1.0.0"}),
            mock.patch.object(validator, "path_exists", return_value=True),
        ):
            errors: list[str] = []
            validator.validate_public_methodology_framing(errors)

        self.assertTrue(any("lost diacritics" in error for error in errors), errors)

    def test_validate_release_assets_rejects_truncated_release_notes(self) -> None:
        validator = load_validator()

        with mock.patch.object(
            validator,
            "read_text",
            return_value="Use `data/metadata.json`; generated from it with:",
        ):
            errors: list[str] = []
            validator.validate_release_assets(errors)

        self.assertTrue(any("metadata render command" in error for error in errors), errors)

    def test_validate_extract_index_requires_all_extract_json_files(self) -> None:
        validator = load_validator()
        broken_index = {
            "records": [
                {
                    "file": "teece_2016_pir_budaq_corpus.json",
                    "current": True,
                    "release_blocker": False,
                    "note": "Only one record, so other extract files are missing.",
                }
            ]
        }

        def fake_load_json(path: Path) -> dict:
            if path.name == "index.json":
                return broken_index
            return validator.load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extract_index(errors)

        self.assertTrue(
            any("data/extracts/index.json missing records" in error for error in errors),
            errors,
        )

    def test_validate_extracts_rejects_unknown_source_witness_ids(self) -> None:
        validator = load_validator()
        original_load_json = validator.load_json
        broken_extract = copy.deepcopy(
            original_load_json(
                ROOT / "data" / "extracts" / "alevi_hakiki_incipit_concordance.json"
            )
        )
        broken_extract["entries"][0]["source_witness_id"] = "missing_witness"

        def fake_load_json(path: Path) -> dict:
            if path.name == "alevi_hakiki_incipit_concordance.json":
                return broken_extract
            return original_load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extracts(errors)

        self.assertTrue(any("unknown source_witness_id" in error for error in errors), errors)

    def test_validate_extracts_rejects_untracked_temp_references(self) -> None:
        validator = load_validator()
        original_load_json = validator.load_json
        broken_extract = copy.deepcopy(
            original_load_json(
                ROOT / "data" / "extracts" / "albanian_hurufi_bektashi_ali_emiri_003094.json"
            )
        )
        broken_extract["source"]["evidence_note"] = "tmp/missing-source.txt:10-12"

        def fake_load_json(path: Path) -> dict:
            if path.name == "albanian_hurufi_bektashi_ali_emiri_003094.json":
                return broken_extract
            return original_load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extracts(errors)

        self.assertTrue(any("untracked temp reference" in error for error in errors), errors)

    def test_validate_extracts_rejects_dogan_kaya_placeholder_owner_fields(self) -> None:
        validator = load_validator()
        original_load_json = validator.load_json
        broken_extract = copy.deepcopy(
            original_load_json(ROOT / "data" / "extracts" / "dogan_kaya_2011_conk_corpus.json")
        )
        broken_extract["entries"][0]["holder_or_owner_raw"] = "boyutundadır."

        def fake_load_json(path: Path) -> dict:
            if path.name == "dogan_kaya_2011_conk_corpus.json":
                return broken_extract
            return original_load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extracts(errors)

        self.assertTrue(any("placeholder holder_or_owner_raw" in error for error in errors), errors)

    def test_validate_extracts_rejects_dogan_kaya_non_holder_owner_fragments(self) -> None:
        validator = load_validator()
        original_load_json = validator.load_json
        broken_extract = copy.deepcopy(
            original_load_json(ROOT / "data" / "extracts" / "dogan_kaya_2011_conk_corpus.json")
        )
        broken_extract["entries"][0]["holder_or_owner_raw"] = (
            "Sonunda Latin harfleriyle notes and dimensions, not an owner."
        )

        def fake_load_json(path: Path) -> dict:
            if path.name == "dogan_kaya_2011_conk_corpus.json":
                return broken_extract
            return original_load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extracts(errors)

        self.assertTrue(any("non-holder holder_or_owner_raw" in error for error in errors), errors)

    def test_validate_extracts_rejects_dogan_kaya_malformed_owner_fragments(self) -> None:
        validator = load_validator()
        original_load_json = validator.load_json
        broken_extract = copy.deepcopy(
            original_load_json(ROOT / "data" / "extracts" / "dogan_kaya_2011_conk_corpus.json")
        )
        broken_extract["entries"][0]["holder_or_owner_raw"] = "Cönkün aslı Yrd."
        broken_extract["entries"][1]["holder_or_owner_raw"] = (
            "Aslı Sivas-Yıldızeli-Yukarı Çakmak köyünden Mehmet Korkmaz’da olan cönk, 11x23 cm."
        )

        def fake_load_json(path: Path) -> dict:
            if path.name == "dogan_kaya_2011_conk_corpus.json":
                return broken_extract
            return original_load_json(path)

        with mock.patch.object(validator, "load_json", side_effect=fake_load_json):
            errors: list[str] = []
            validator.validate_extracts(errors)

        self.assertTrue(any("malformed holder_or_owner_raw" in error for error in errors), errors)

    def test_validate_extracts_accepts_current_extract_files(self) -> None:
        validator = load_validator()

        errors: list[str] = []
        validator.validate_extracts(errors)

        self.assertEqual(errors, [])


class ReleaseCheckDoiModeTests(unittest.TestCase):
    def _write_metadata_surfaces(self, root: Path, doi: str) -> None:
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "data" / "metadata.json").write_text(
            json.dumps({"doi": doi}, indent=2) + "\n",
            encoding="utf-8",
        )
        (root / ".zenodo.json").write_text(
            json.dumps({"description": f"DOI marker: {doi}"}, indent=2) + "\n",
            encoding="utf-8",
        )
        (root / "CITATION.cff").write_text(
            f"identifiers:\n  - type: doi\n    value: \"{doi}\"\n",
            encoding="utf-8",
        )

    def test_release_check_structural_mode_allows_pending_doi_marker(self) -> None:
        release_check = load_release_check()
        with tempfile.TemporaryDirectory() as tmp:
            original_root = release_check.ROOT
            release_check.ROOT = Path(tmp)
            try:
                self._write_metadata_surfaces(
                    release_check.ROOT,
                    release_check.PENDING_DOI,
                )

                errors = release_check.doi_validation_errors(structural=True)
            finally:
                release_check.ROOT = original_root

        self.assertEqual(errors, [])

    def test_release_check_publication_mode_rejects_pending_doi_marker(self) -> None:
        release_check = load_release_check()
        with tempfile.TemporaryDirectory() as tmp:
            original_root = release_check.ROOT
            release_check.ROOT = Path(tmp)
            try:
                self._write_metadata_surfaces(
                    release_check.ROOT,
                    release_check.PENDING_DOI,
                )

                errors = release_check.doi_validation_errors(structural=False)
            finally:
                release_check.ROOT = original_root

        self.assertTrue(any(release_check.PENDING_DOI in error for error in errors), errors)

    def test_release_check_publication_mode_accepts_zenodo_doi(self) -> None:
        release_check = load_release_check()
        with tempfile.TemporaryDirectory() as tmp:
            original_root = release_check.ROOT
            release_check.ROOT = Path(tmp)
            try:
                self._write_metadata_surfaces(
                    release_check.ROOT,
                    "10.5281/zenodo.1234567",
                )

                errors = release_check.doi_validation_errors(structural=False)
            finally:
                release_check.ROOT = original_root

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
