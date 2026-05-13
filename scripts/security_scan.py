#!/usr/bin/env python3
"""Lightweight local scanner for accidentally committed secrets.

The script scans text files in the current repository and reports only the file,
line number, and match type. It intentionally never prints the matched value.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024

ASSIGNMENT_KEYS = [
    ("password assignment", "pass" + "word"),
    ("secret assignment", "sec" + "ret"),
    ("token assignment", "tok" + "en"),
]

FEISHU_KEYS = [
    "feishu_app_" + "secret",
    "app_" + "secret",
    "app-" + "secret",
]

PLACEHOLDER_WORDS = (
    "example",
    "placeholder",
    "changeme",
    "change_me",
    "dummy",
    "fake",
    "test",
    "your_",
    "xxx",
)

WEBHOOK_RE = re.compile(r"https?://[^\s'\"]*(?:webhook|hooks?)[^\s'\"]*", re.IGNORECASE)
EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
PRIVATE_KEY_MARKER_RE = re.compile(
    re.escape("-" * 5 + "BEGIN ") + r"(?:[A-Z0-9 ]+ )?" + re.escape("PRIVATE KEY" + "-" * 5)
)


def iter_repo_files(repo_root: Path):
    """Yield non-skipped files under the repository root."""
    for root, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        root_path = Path(root)
        for filename in filenames:
            path = root_path / filename
            if path.is_symlink() or not path.is_file():
                continue
            yield path


def is_text_file(path: Path) -> bool:
    """Return True when a file looks small enough and text-like."""
    try:
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            return False
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in sample


def extract_assigned_value(line: str, key: str) -> str | None:
    """Extract a simple assigned value for a key without logging it."""
    pattern = re.compile(rf"(?<![A-Z0-9_\-]){re.escape(key)}(?![A-Z0-9_\-])", re.IGNORECASE)
    match = pattern.search(line)
    if not match:
        return None

    remainder = line[match.end() :].lstrip()
    if not remainder or remainder[0] not in "=:":
        return None

    value = remainder[1:].strip()
    if not value:
        return None

    if value[0] in {'"', "'"}:
        quote = value[0]
        value = value[1:].split(quote, 1)[0]
    else:
        value = re.split(r"[\s,#}]", value, maxsplit=1)[0]

    return value.strip()


def is_placeholder_or_code(value: str, key: str) -> bool:
    """Filter obvious examples, placeholders, and code references."""
    normalized = value.strip().strip('"\'').lower()
    normalized_key = key.lower().replace("-", "_")

    if not normalized:
        return True
    if normalized in {key.lower(), normalized_key, "none", "null", "true", "false"}:
        return True

    stripped_code_value = normalized.strip("()[]{}.,;->")
    if stripped_code_value in {"str", "int", "bool", "dict", "list", "float", "bytes"}:
        return True
    if normalized.startswith(("{", 'f"', "f'")):
        return True
    if re.match(r"^[a-z_][a-z0-9_]*\(", normalized):
        return True
    if "(" in normalized and normalized.endswith(")"):
        return True
    if any(word in normalized for word in PLACEHOLDER_WORDS):
        return True
    if any(marker in normalized for marker in ("os.getenv", "require_env", "getenv", "env[")):
        return True
    if normalized.startswith(("$", "${")):
        return True

    return False


def find_matches(line: str) -> list[str]:
    """Return risk types found on a line."""
    matches: list[str] = []

    for match_type, key in ASSIGNMENT_KEYS:
        value = extract_assigned_value(line, key)
        if value and not is_placeholder_or_code(value, key):
            matches.append(match_type)

    for key in FEISHU_KEYS:
        value = extract_assigned_value(line, key)
        if value and not is_placeholder_or_code(value, key):
            matches.append("Feishu app secret field")

    lowered = line.lower()
    if ("imap" in lowered or "smtp" in lowered) and any(
        word in lowered for word in ("user", "account", "email", "pass" + "word", "pass")
    ):
        for separator in ("=", ":"):
            if separator in line:
                candidate = line.split(separator, 1)[1].strip().strip('"\'')
                if EMAIL_RE.match(candidate) and not is_placeholder_or_code(candidate, "mail account"):
                    matches.append("IMAP/SMTP account configuration")
                if "pass" in lowered and candidate and not is_placeholder_or_code(candidate, "mail password"):
                    matches.append("IMAP/SMTP password configuration")
                break

    if WEBHOOK_RE.search(line):
        matches.append("webhook URL")

    if PRIVATE_KEY_MARKER_RE.search(line):
        matches.append("private key header")

    return matches


def scan_file(path: Path, repo_root: Path) -> list[tuple[str, int, str]]:
    """Scan one text file and return findings."""
    findings: list[tuple[str, int, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line_number, line in enumerate(handle, start=1):
                for match_type in find_matches(line):
                    findings.append((str(path.relative_to(repo_root)), line_number, match_type))
    except OSError:
        return findings
    return findings


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    findings: list[tuple[str, int, str]] = []

    for path in iter_repo_files(repo_root):
        if not is_text_file(path):
            continue
        findings.extend(scan_file(path, repo_root))

    if findings:
        print("Potential sensitive information found:")
        for file_path, line_number, match_type in findings:
            print(f"{file_path}:{line_number}: {match_type}")
        return 1

    print("No potential sensitive information found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
