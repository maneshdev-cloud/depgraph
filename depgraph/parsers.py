"""Parsers for dependency declarations and analyzer inputs."""

from __future__ import annotations

import json
import re

_REQ_LINE_RE = re.compile(r"^([A-Za-z0-9_.\-]+)(?:\[([^\]]+)\])?\s*(.*)$")


def _normalize_pip_name(name: str) -> str:
    """PEP 503 normalisation: lowercase, runs of -_. collapse to -."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements(text: str) -> list[tuple[str, str]]:
    """Parse a ``requirements.txt`` body into ``(name, version_spec)`` pairs.

    Handles comments, blank lines, extras (``flask[async]``) and
    version specifiers. Option lines (``-r``, ``-e`` ...) are skipped.
    """
    out: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.split(" #", 1)[0].strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = _REQ_LINE_RE.match(line)
        if m:
            out.append((_normalize_pip_name(m.group(1)), m.group(3).strip()))
    return out


def parse_package_json(text: str) -> list[tuple[str, str]]:
    """Parse a ``package.json`` body, merging dependencies + devDependencies."""
    data = json.loads(text)
    out: list[tuple[str, str]] = []
    for section in ("dependencies", "devDependencies"):
        for name, spec in sorted(data.get(section, {}).items()):
            out.append((name, spec))
    return out


def parse_critical_paths(text: str) -> list[str]:
    """Parse a critical-paths file: one entry point per line, ``#`` comments."""
    out = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out
