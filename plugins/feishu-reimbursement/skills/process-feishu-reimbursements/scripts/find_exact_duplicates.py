#!/usr/bin/env python3
"""Find byte-identical files without modifying any input path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


def iter_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file() and not any(part.startswith(".") for part in child.parts):
                yield child


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find exact SHA-256 duplicates for files in a candidate path."
    )
    parser.add_argument("candidate", type=Path, help="Candidate file or directory")
    parser.add_argument(
        "--against",
        action="append",
        required=True,
        type=Path,
        help="Reference file or directory; repeat as needed",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--fail-on-duplicate",
        action="store_true",
        help="Exit with status 1 when at least one exact duplicate is found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = list(iter_files(args.candidate.expanduser()))
    references = [
        file
        for root in args.against
        for file in iter_files(root.expanduser())
    ]

    if not candidates:
        raise SystemExit(f"No candidate files found: {args.candidate}")
    if not references:
        raise SystemExit("No reference files found")

    by_hash: dict[str, list[Path]] = {}
    for reference in references:
        by_hash.setdefault(sha256(reference), []).append(reference)

    results = []
    for candidate in candidates:
        digest = sha256(candidate)
        matches = [str(path) for path in by_hash.get(digest, []) if path != candidate]
        results.append(
            {
                "candidate": str(candidate),
                "sha256": digest,
                "exact_matches": matches,
                "is_duplicate": bool(matches),
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "DUPLICATE" if result["is_duplicate"] else "UNMATCHED"
            print(f"{status}\t{result['candidate']}")
            for match in result["exact_matches"]:
                print(f"  = {match}")

    has_duplicates = any(item["is_duplicate"] for item in results)
    return 1 if args.fail_on_duplicate and has_duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())
