#!/usr/bin/env python3
"""Run the publication release gate for the witness census deposit."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
WATCHED_RELEASE_PATHS = {
    ".gitattributes",
    ".gitignore",
    ".zenodo.json",
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "docs/limitations-and-recovery-plan.md",
    "docs/llm-use.md",
    "docs/release-checklist.md",
    "docs/release-notes-v1.0.md",
    "docs/search-scope-statistics.md",
}
WATCHED_RELEASE_PREFIXES = ("data/", "scripts/", "tests/", "notes/")
TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
TEXT_BASENAMES = {"LICENSE"}
PENDING_DOI = "PENDING_" + "ZENODO_RESERVATION"
ZENODO_DOI_RE = re.compile(r"^10\.5281/zenodo\.[0-9]+$")
DOI_METADATA_SURFACES = ("data/metadata.json", ".zenodo.json", "CITATION.cff")


def run_command(command: list[str]) -> int:
    print(f"$ {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}: {' '.join(command)}")
    return result.returncode


def parse_all_json() -> int:
    print("$ parse all JSON files")
    failures: list[str] = []
    for path in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
    if failures:
        print("JSON parse failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("JSON parse ok")
    return 0


def _read_release_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _all_release_text_files() -> list[str]:
    files: list[str] = []
    if has_git_checkout():
        code, lines, _output = _git_lines(["git", "ls-files"])
        if code == 0:
            files.extend(path for path in lines if _is_text_file(path))
    if not files:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file():
                relative = path.relative_to(ROOT).as_posix()
                if _is_text_file(relative):
                    files.append(relative)
    return sorted(set(files))


def _pending_doi_hits() -> list[str]:
    hits: list[str] = []
    for relative in _all_release_text_files():
        if PENDING_DOI in _read_release_text(relative):
            hits.append(relative)
    return hits


def _metadata_doi() -> str:
    metadata = json.loads(_read_release_text("data/metadata.json") or "{}")
    return str(metadata.get("doi") or "")


def _citation_doi_values() -> list[str]:
    text = _read_release_text("CITATION.cff")
    pattern = r"value:\s*[\"']?(" + r"10\.5281/zenodo\.[0-9]+|" + re.escape(PENDING_DOI) + r")[\"']?"
    return re.findall(pattern, text)


def doi_validation_errors(structural: bool) -> list[str]:
    errors: list[str] = []
    doi = _metadata_doi()
    pending_hits = _pending_doi_hits()
    unexpected_pending_hits = [
        path for path in pending_hits if path not in DOI_METADATA_SURFACES
    ]

    if unexpected_pending_hits:
        errors.append(
            f"{PENDING_DOI} appears outside generated metadata surfaces: {unexpected_pending_hits}"
        )

    if structural:
        if doi != PENDING_DOI and not ZENODO_DOI_RE.fullmatch(doi):
            errors.append(
                f"data/metadata.json doi must be {PENDING_DOI} or a Zenodo DOI in structural mode"
            )
        return errors

    if doi == PENDING_DOI:
        errors.append(f"{PENDING_DOI} is not allowed in publication mode")
    elif not ZENODO_DOI_RE.fullmatch(doi):
        errors.append("data/metadata.json doi must match ^10\\.5281/zenodo\\.[0-9]+$")

    if pending_hits:
        errors.append(f"{PENDING_DOI} remains in publication tree: {pending_hits}")

    citation_values = _citation_doi_values()
    if doi and doi != PENDING_DOI and doi not in citation_values:
        errors.append("CITATION.cff DOI does not match data/metadata.json")

    return errors


def check_doi_state(structural: bool) -> int:
    mode = "structural" if structural else "publication"
    print(f"$ check DOI state ({mode} mode)")
    errors = doi_validation_errors(structural=structural)
    if errors:
        print("DOI validation failures:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DOI state ok.")
    return 0


def _normalize_git_path(path: str) -> str:
    return path.strip().replace("\\", "/")


def _is_release_relevant(path: str) -> bool:
    normalized = _normalize_git_path(path)
    return normalized in WATCHED_RELEASE_PATHS or normalized.startswith(
        WATCHED_RELEASE_PREFIXES
    )


def _git_lines(command: list[str]) -> tuple[int, list[str], str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout.strip()
    lines = [
        _normalize_git_path(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]
    return result.returncode, lines, output


def relevant_untracked_files() -> list[str]:
    code, lines, output = _git_lines(["git", "ls-files", "--others", "--exclude-standard"])
    if code != 0:
        return [f"<git ls-files failed: {output or 'no output'}>"]
    return sorted(path for path in lines if _is_release_relevant(path))


def check_untracked_files() -> int:
    print("$ check relevant untracked files")
    untracked = relevant_untracked_files()
    if not untracked:
        print("No relevant untracked files.")
        return 0
    print("Relevant untracked files must be staged or intentionally ignored:")
    for path in untracked:
        print(f"- {path}")
    return 1


def _is_text_file(path: str) -> bool:
    normalized = _normalize_git_path(path)
    return (
        Path(normalized).suffix.lower() in TEXT_SUFFIXES
        or Path(normalized).name in TEXT_BASENAMES
    )


def tracked_text_files() -> list[str]:
    code, lines, output = _git_lines(["git", "ls-files"])
    if code != 0:
        return [f"<git ls-files failed: {output or 'no output'}>"]
    return sorted(path for path in lines if _is_text_file(path))


def files_with_crlf(paths: list[str]) -> list[str]:
    offenders: list[str] = []
    for path in paths:
        if path.startswith("<git ls-files failed:"):
            offenders.append(path)
            continue
        full_path = ROOT / path
        if full_path.exists() and b"\r\n" in full_path.read_bytes():
            offenders.append(path)
    return offenders


def check_lf_line_endings() -> int:
    print("$ check LF line endings")
    offenders = files_with_crlf(tracked_text_files())
    if not offenders:
        print("LF line endings ok.")
        return 0
    print("CRLF line endings found in text files:")
    for path in offenders:
        print(f"- {path}")
    return 1


def has_git_checkout() -> bool:
    return (ROOT / ".git").exists()


def run_git_hygiene_checks(skip_git_checks: bool) -> int:
    if skip_git_checks:
        print("$ git hygiene checks")
        print(
            "Skipping git hygiene checks in archive mode. "
            "Run without --archive from a Git checkout before tagging."
        )
        return 0

    failures = 0
    failures += 1 if check_untracked_files() != 0 else 0
    failures += 1 if check_lf_line_endings() != 0 else 0
    failures += 1 if run_command(["git", "diff", "--check"]) != 0 else 0
    failures += 1 if run_command(["git", "diff", "--cached", "--check"]) != 0 else 0
    return failures


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        action="store_true",
        help="run archive-safe validation and skip Git checkout hygiene checks",
    )
    parser.add_argument(
        "--skip-git-checks",
        action="store_true",
        help="skip Git checkout hygiene checks; alias for --archive",
    )
    parser.add_argument(
        "--structural",
        action="store_true",
        help="allow the pre-reservation DOI marker while validating the staging tree",
    )
    return parser.parse_args([] if argv is None else argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    skip_git_checks = args.archive or args.skip_git_checks or not has_git_checkout()

    commands = [
        [sys.executable, "scripts/validate_dataset.py"],
        [sys.executable, "scripts/render_metadata.py", "--check"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    ]

    failures = 0
    for command in commands:
        failures += 1 if run_command(command) != 0 else 0
    failures += 1 if parse_all_json() != 0 else 0
    failures += 1 if check_doi_state(structural=args.structural) != 0 else 0
    failures += run_git_hygiene_checks(skip_git_checks)

    if failures:
        print(f"Release check failed: {failures} step(s) failed.")
        return 1

    print("Release check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
