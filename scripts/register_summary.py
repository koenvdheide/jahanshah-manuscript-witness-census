#!/usr/bin/env python3
"""Shared derived counts for the witness register."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


VERIFICATION_BUCKETS = (
    "verified",
    "verified_with_attribution_caveat",
    "candidate_probably_non_cihansah",
    "candidate_probably_yusuf_hakiki_or_other_homonym",
    "lost_witness_attested_only",
    "rejected",
    "pending",
)
COUNTED_WITNESS_STATUSES = {"verified", "verified_with_attribution_caveat"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _counter_with_buckets(values, buckets: tuple[str, ...]) -> dict:
    counts = Counter(values)
    for bucket in buckets:
        counts.setdefault(bucket, 0)
    return dict(counts)


def _non_rejected_witnesses(register: dict) -> list[dict]:
    return [
        witness
        for witness in register["witnesses"]
        if witness.get("verification_status") != "rejected"
    ]


def _counted_witnesses(register: dict) -> list[dict]:
    return [
        witness
        for witness in register["witnesses"]
        if witness.get("verification_status") in COUNTED_WITNESS_STATUSES
    ]


def compute_stats(register: dict) -> dict:
    witnesses = register["witnesses"]
    non_rejected = _non_rejected_witnesses(register)
    verified_or_caveated = _counted_witnesses(register)

    return {
        "total_non_rejected_entries": len(non_rejected),
        "total_verified_or_caveated_witnesses": len(verified_or_caveated),
        "total_witnesses_active": len(non_rejected),
        "total_entries_including_rejected_and_lost": len(witnesses),
        "by_verification": _counter_with_buckets(
            (witness.get("verification_status") for witness in witnesses),
            VERIFICATION_BUCKETS,
        ),
        "by_completeness": dict(
            Counter(witness.get("completeness") for witness in non_rejected)
        ),
        "by_country": dict(Counter(witness.get("country") for witness in non_rejected)),
    }


def _is_ocak_witness(witness: dict) -> bool:
    collection = str(witness.get("collection") or "").casefold()
    return "ocağı" in collection or "ocagi" in collection or "ocak" in collection


def public_counts(register: dict) -> dict:
    stats = compute_stats(register)
    verification = stats["by_verification"]
    counted = _counted_witnesses(register)
    ocak_witnesses = [witness for witness in counted if _is_ocak_witness(witness)]
    institutional_fragments = [
        witness
        for witness in counted
        if witness.get("completeness") == "fragment" and not _is_ocak_witness(witness)
    ]

    return {
        "verified": verification.get("verified", 0),
        "caveated": verification.get("verified_with_attribution_caveat", 0),
        "candidate_probably_non_cihansah": verification.get(
            "candidate_probably_non_cihansah", 0
        ),
        "lost_witness_attested_only": verification.get(
            "lost_witness_attested_only", 0
        ),
        "rejected": verification.get("rejected", 0),
        "total_non_rejected_entries": stats["total_non_rejected_entries"],
        "total_verified_or_caveated_witnesses": stats[
            "total_verified_or_caveated_witnesses"
        ],
        "teis_yesevi_roster": len(register.get("teis_yesevi_roster", [])),
        "institutional_fragment": len(institutional_fragments),
        "alevi_shrine_witnesses": len(ocak_witnesses),
        "alevi_anatolian": sum(
            1 for witness in ocak_witnesses if witness.get("country") == "Turkey"
        ),
        "alevi_iranian_azerbaijani": sum(
            1 for witness in ocak_witnesses if witness.get("country") == "Iran"
        ),
    }
