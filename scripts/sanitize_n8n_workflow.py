#!/usr/bin/env python3
"""Offline sanitizer for local n8n workflow JSON exports.

Public sanitized version. It reads a local JSON file, removes credential and
execution-data fields, redacts sensitive-looking keys and strings, and writes a
sanitized JSON file. It never prints matched secret values.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REDACTED = "REDACTED"

DROP_KEYS = {
    "credentials",
    "credential",
    "executionData",
    "execution_data",
    "pinData",
    "pin_data",
    "staticData",
    "static_data",
    "runtimeData",
    "runtime_data",
    "binaryData",
    "binary_data",
}

SENSITIVE_KEY_MARKERS = (
    "password", "passwd", "secret", "token", "apikey", "api_key",
    "authorization", "auth", "cookie", "webhook", "url", "host",
    "hostname", "email", "mail", "tableid", "table_id", "appid",
    "app_id", "apptoken", "app_token", "recordid", "record_id",
    "payload", "body", "headers", "query", "recipient", "contact",
    "customer", "client", "prospect",
)

CUSTOMER_LIKE_KEYS = {
    "company", "company_name", "contact_name", "name", "first_name",
    "last_name", "subject", "text", "html", "email_subject",
    "email_draft", "research_summary", "reply_summary",
}

STRING_REPLACEMENTS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("bearer token", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer REDACTED"),
    ("webhook URL", re.compile(r"(?i)https?://[^\s\"'<>]+/webhook(?:-test)?/[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]+"), "https://example.invalid/webhook/REDACTED"),
    ("webhook path", re.compile(r"(?i)(/webhook(?:-test)?/)[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]+"), r"\1REDACTED"),
    ("IPv4 address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "REDACTED_IP"),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "REDACTED_EMAIL"),
    ("table id", re.compile(r"\btbl[A-Za-z0-9]{8,}\b"), "REDACTED_TABLE_ID"),
    ("app id", re.compile(r"\bcli_[A-Za-z0-9]{8,}\b"), "REDACTED_APP_ID"),
    ("app key", re.compile(r"\bapp-[A-Za-z0-9]{12,}\b"), "REDACTED_APP_KEY"),
    ("long opaque id", re.compile(r"\b[A-Za-z0-9_-]{32,}\b"), "REDACTED_OPAQUE_ID"),
)


@dataclass
class SanitizeStats:
    dropped_keys: dict[str, int] = field(default_factory=dict)
    redacted_keys: dict[str, int] = field(default_factory=dict)
    string_replacements: dict[str, int] = field(default_factory=dict)

    def bump(self, bucket: dict[str, int], key: str, count: int = 1) -> None:
        bucket[key] = bucket.get(key, 0) + count


def normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def compact_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", key.lower())


def should_drop_key(key: str) -> bool:
    normalized = normalize_key(key)
    compact = compact_key(key)
    return normalized in DROP_KEYS or compact in {compact_key(item) for item in DROP_KEYS}


def should_redact_key(key: str) -> bool:
    normalized = normalize_key(key)
    compact = compact_key(key)
    if normalized in CUSTOMER_LIKE_KEYS or compact in {compact_key(item) for item in CUSTOMER_LIKE_KEYS}:
        return True
    return any(marker in compact for marker in SENSITIVE_KEY_MARKERS)


def sanitize_string(value: str, stats: SanitizeStats) -> str:
    sanitized = value
    for label, pattern, replacement in STRING_REPLACEMENTS:
        sanitized, count = pattern.subn(replacement, sanitized)
        if count:
            stats.bump(stats.string_replacements, label, count)
    return sanitized


def sanitize_value(value: Any, stats: SanitizeStats) -> Any:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if should_drop_key(key_text):
                stats.bump(stats.dropped_keys, key_text)
                continue
            if should_redact_key(key_text):
                stats.bump(stats.redacted_keys, key_text)
                output[key] = REDACTED
                continue
            output[key] = sanitize_value(child, stats)
        return output
    if isinstance(value, list):
        return [sanitize_value(item, stats) for item in value]
    if isinstance(value, str):
        return sanitize_string(value, stats)
    return copy.deepcopy(value)


def print_summary(stats: SanitizeStats) -> None:
    print("Sanitization summary:")
    if not (stats.dropped_keys or stats.redacted_keys or stats.string_replacements):
        print("- No sensitive markers detected by sanitizer rules.")
        return
    for label, values in (("Dropped keys", stats.dropped_keys), ("Redacted keys", stats.redacted_keys), ("String replacements", stats.string_replacements)):
        if values:
            print(f"- {label}:")
            for key, count in sorted(values.items()):
                print(f"  - {key}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize a local exported n8n workflow JSON file.")
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--check", action="store_true", help="Sanitize in memory and print summary only.")
    parser.add_argument("--fail-on-sensitive", action="store_true")
    args = parser.parse_args()

    if not args.stdout and not args.check and not args.output:
        print("Output path is required unless --stdout or --check is used.", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Input file is not valid JSON: {error}", file=sys.stderr)
        return 2

    stats = SanitizeStats()
    sanitized = sanitize_value(data, stats)
    output_text = json.dumps(sanitized, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    sensitive_count = sum(stats.dropped_keys.values()) + sum(stats.redacted_keys.values()) + sum(stats.string_replacements.values())

    if args.stdout:
        sys.stdout.write(output_text)
    elif args.check:
        print_summary(stats)
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
        print(f"Wrote sanitized workflow JSON: {output_path}")
        print_summary(stats)

    return 1 if args.fail_on_sensitive and sensitive_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
