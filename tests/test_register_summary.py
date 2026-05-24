from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "scripts" / "register_summary.py"


def load_summary():
    spec = importlib.util.spec_from_file_location("register_summary", SUMMARY_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load scripts/register_summary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegisterSummaryTests(unittest.TestCase):
    def test_compute_stats_matches_canonical_register_stats(self) -> None:
        summary = load_summary()
        register = summary.load_json(ROOT / "data" / "witness_register.json")

        self.assertEqual(summary.compute_stats(register), register["stats"])

    def test_public_counts_derives_metadata_subcounts_from_register(self) -> None:
        summary = load_summary()
        register = summary.load_json(ROOT / "data" / "witness_register.json")

        counts = summary.public_counts(register)

        self.assertEqual(counts["verified"], 7)
        self.assertEqual(counts["caveated"], 2)
        self.assertEqual(counts["candidate_probably_non_cihansah"], 1)
        self.assertEqual(counts["lost_witness_attested_only"], 1)
        self.assertEqual(counts["rejected"], 3)
        self.assertEqual(counts["teis_yesevi_roster"], 5)
        self.assertEqual(counts["institutional_fragment"], 1)
        self.assertEqual(counts["alevi_shrine_witnesses"], 3)
        self.assertEqual(counts["alevi_anatolian"], 1)
        self.assertEqual(counts["alevi_iranian_azerbaijani"], 2)


if __name__ == "__main__":
    unittest.main()
