from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "scripts" / "render_metadata.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_metadata", RENDERER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load scripts/render_metadata.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MetadataRenderingTests(unittest.TestCase):
    def test_census_paragraph_reports_verified_and_caveated_subcounts(self) -> None:
        renderer = load_renderer()
        metadata = renderer.load_json(ROOT / "data" / "metadata.json")
        register = renderer.load_json(ROOT / "data" / "witness_register.json")

        paragraph = renderer.census_paragraph(metadata, register)

        self.assertIn("7 verified and 2 caveated", paragraph)
        self.assertNotIn("9 verified or caveated", paragraph)

    def test_check_outputs_detects_crlf_byte_drift(self) -> None:
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as tmp:
            original_root = renderer.ROOT
            renderer.ROOT = Path(tmp)
            try:
                path = renderer.ROOT / ".zenodo.json"
                path.write_bytes(b"{\r\n}\r\n")

                stale = renderer.check_outputs({path: "{\n}\n"})
            finally:
                renderer.ROOT = original_root

        self.assertEqual(stale, [".zenodo.json"])


if __name__ == "__main__":
    unittest.main()
