#!/usr/bin/env python3
"""Compute fill rate, unique count, duplicates, and run-to-run delta.

Input is a JSON array or JSONL file of objects. The script prints one JSON
object and does not judge whether the run is trusted.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def load_records(path: Path) -> list[dict]:
    text = path.read_text()
    if not text.strip():
        return []
    if text.lstrip().startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise SystemExit(f"{path} must be a JSON array or JSONL")
        records = data
    else:
        records = []
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: {exc}") from exc
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise SystemExit(f"{path}: record {index} is not an object")
    return records


def filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def field_names(records: list[dict], previous: list[dict] | None, requested: list[str] | None) -> list[str]:
    if requested:
        return requested
    names: list[str] = []
    seen: set[str] = set()
    groups = [records]
    if previous is not None:
        groups.append(previous)
    for group in groups:
        for record in group:
            for key in record:
                if key not in seen:
                    seen.add(key)
                    names.append(key)
    return names


def field_stats(records: list[dict], fields: list[str]) -> dict[str, dict]:
    total = len(records)
    stats: dict[str, dict] = {}
    for field in fields:
        values = [record.get(field) for record in records]
        present = [value for value in values if filled(value)]
        unique = len({canonical(value) for value in present})
        rate = (len(present) / total) if total else 0.0
        stats[field] = {
            "fill_rate": round(rate, 6),
            "filled": len(present),
            "unique": unique,
        }
    return stats


def duplicate_stats(records: list[dict], id_field: str | None) -> dict | None:
    if not id_field:
        return None
    keys = [canonical(record.get(id_field)) for record in records]
    counts = Counter(keys)
    extra = sum(count - 1 for count in counts.values() if count > 1)
    total = len(records)
    return {
        "id_field": id_field,
        "unique_keys": len(counts),
        "duplicate_extra": extra,
        "duplicate_rate": round((extra / total) if total else 0.0, 6),
    }


def build_delta(current: dict, previous: dict, fields: list[str]) -> dict:
    fill_rate = {}
    for field in fields:
        current_rate = current["fields"].get(field, {}).get("fill_rate", 0.0)
        previous_rate = previous["fields"].get(field, {}).get("fill_rate", 0.0)
        fill_rate[field] = round(current_rate - previous_rate, 6)
    current_dup = current["duplicates"]
    previous_dup = previous["duplicates"]
    duplicate_extra = None
    if current_dup is not None and previous_dup is not None:
        duplicate_extra = current_dup["duplicate_extra"] - previous_dup["duplicate_extra"]
    return {
        "records": current["records"] - previous["records"],
        "duplicate_extra": duplicate_extra,
        "fill_rate": fill_rate,
    }


def summarize(records: list[dict], fields: list[str], id_field: str | None) -> dict:
    return {
        "records": len(records),
        "fields": field_stats(records, fields),
        "duplicates": duplicate_stats(records, id_field),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--id-field")
    parser.add_argument(
        "--fields",
        help="Comma-separated required fields. Default is every key seen.",
    )
    args = parser.parse_args(argv)

    current_records = load_records(args.records)
    previous_records = load_records(args.previous) if args.previous else None
    requested = [part.strip() for part in args.fields.split(",") if part.strip()] if args.fields else None
    fields = field_names(current_records, previous_records, requested)
    current = summarize(current_records, fields, args.id_field)
    delta = None
    if previous_records is not None:
        previous = summarize(previous_records, fields, args.id_field)
        delta = build_delta(current, previous, fields)
    payload = {
        "records": current["records"],
        "fields": current["fields"],
        "duplicates": current["duplicates"],
        "delta": delta,
    }
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
