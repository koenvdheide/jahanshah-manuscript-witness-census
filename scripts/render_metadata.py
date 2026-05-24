#!/usr/bin/env python3
"""Render publication metadata from canonical repo data."""

from __future__ import annotations

import argparse
import html
import json
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from register_summary import public_counts


METADATA_PATH = ROOT / "data" / "metadata.json"
REGISTER_PATH = ROOT / "data" / "witness_register.json"
ZENODO_PATH = ROOT / ".zenodo.json"
CITATION_PATH = ROOT / "CITATION.cff"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def census_paragraph(metadata: dict, register: dict) -> str:
    counts = public_counts(register)
    text = (
        f"The census records {counts['verified']} verified and "
        f"{counts['caveated']} caveated Jahanshah witnesses: "
        f"{counts['teis_yesevi_roster']} on the TEIS Yesevi roster, "
        f"{counts['institutional_fragment']} institutional fragment, and "
        f"{counts['alevi_shrine_witnesses']} Alevi shrine witnesses in the Ocak tradition: "
        f"{counts['alevi_anatolian']} Anatolian (Diyarbakır Ulutürk) and "
        f"{counts['alevi_iranian_azerbaijani']} Iranian Azerbaijani (Ilkhchi Kırklar Ocağı). "
        f"It also records {counts['candidate_probably_non_cihansah']} attribution-disputed candidate "
        f"and {counts['lost_witness_attested_only']} lost-attested entry (Diyarbakır YE per Cunbur 1999). "
        "Routine search false positives are kept in the per-session search JSONs "
        "under data/searches/, outside the witness table. "
        f"{metadata['search_key_summary']}"
    )
    return text


def description_paragraphs(metadata: dict, register: dict) -> list[str]:
    return [
        metadata["intro"],
        census_paragraph(metadata, register),
        metadata["alevi_summary"],
        metadata["methodology_summary"],
    ]


def html_description(metadata: dict, register: dict) -> str:
    paragraphs = description_paragraphs(metadata, register)
    return "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)


def render_zenodo(metadata: dict, register: dict) -> str:
    data = {
        "title": metadata["title"],
        "version": metadata["version"],
        "upload_type": metadata["upload_type"],
        "access_right": metadata["access_right"],
        "license": metadata["license"]["zenodo"],
        "language": metadata["language"],
        "creators": [
            {
                "name": author["name"],
                "orcid": author["orcid"],
                "affiliation": author["affiliation"],
            }
            for author in metadata["authors"]
        ],
        "description": html_description(metadata, register),
        "keywords": metadata["keywords"],
        "subjects": metadata["subjects"],
        "communities": [],
    }
    if metadata.get("related_identifiers"):
        data["related_identifiers"] = metadata["related_identifiers"]
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def wrap_abstract(paragraphs: list[str]) -> list[str]:
    lines: list[str] = []
    for paragraph in paragraphs:
        wrapped = textwrap.wrap(paragraph, width=78, break_long_words=False)
        if not wrapped:
            lines.append("  ")
        else:
            lines.extend(f"  {line}" for line in wrapped)
    return lines


def render_citation(metadata: dict, register: dict) -> str:
    lines: list[str] = [
        "cff-version: 1.2.0",
        f"title: {yaml_quote(metadata['title'])}",
        'message: "If you use this dataset, please cite it as below."',
        "type: dataset",
        "authors:",
    ]
    for author in metadata["authors"]:
        lines.extend(
            [
                f"  - family-names: {yaml_quote(author['family_names'])}",
                f"    given-names: {yaml_quote(author['given_names'])}",
                f"    orcid: {yaml_quote('https://orcid.org/' + author['orcid'])}",
                f"    affiliation: {yaml_quote(author['affiliation'])}",
            ]
        )

    lines.extend(
        [
            f"date-released: {yaml_quote(metadata['release_date'])}",
            f"version: {yaml_quote(metadata['version'])}",
            f"license: {yaml_quote(metadata['license']['cff'])}",
            "identifiers:",
            "  - type: doi",
            f"    value: {yaml_quote(metadata['doi'])}",
            "abstract: >",
        ]
    )
    lines.extend(wrap_abstract(description_paragraphs(metadata, register)))
    lines.append("keywords:")
    lines.extend(f"  - {yaml_quote(keyword)}" for keyword in metadata["keywords"])
    return "\n".join(lines) + "\n"


def render_all() -> dict[Path, str]:
    metadata = load_json(METADATA_PATH)
    register = load_json(REGISTER_PATH)
    return {
        ZENODO_PATH: render_zenodo(metadata, register),
        CITATION_PATH: render_citation(metadata, register),
    }


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    stale: list[str] = []
    for path, rendered in outputs.items():
        current = path.read_bytes() if path.exists() else b""
        if current != rendered.encode("utf-8"):
            stale.append(path.relative_to(ROOT).as_posix())
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="fail if rendered metadata is stale")
    group.add_argument("--write", action="store_true", help="write rendered metadata files")
    args = parser.parse_args()

    outputs = render_all()
    if args.write:
        for path, rendered in outputs.items():
            path.write_bytes(rendered.encode("utf-8"))
        print("Rendered publication metadata.")
        return 0

    stale = check_outputs(outputs)
    if stale:
        print("Publication metadata is stale:")
        for path in stale:
            print(f"- {path}")
        print("Run: python scripts\\render_metadata.py --write")
        return 1

    print("Publication metadata is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
