"""CLI: analyze one package in a project directory.

Usage::

    python -m depgraph.cli fixtures/sample_project qs
    python -m depgraph.cli fixtures/sample_project ms --html out.html

The project directory is expected to contain:

* ``deps.json``         — registry: ``{package: [dependencies]}``
* ``critical_paths.txt``— one critical entry point per line
* ``package.json`` / ``requirements.txt`` (optional) — what the
  project declares directly; printed for context.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyze import blast_radius
from .graph import DepGraph
from .parsers import parse_critical_paths, parse_package_json, parse_requirements
from .report import html_report, text_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="depgraph", description=__doc__)
    parser.add_argument("project_dir", help="directory with deps.json + critical_paths.txt")
    parser.add_argument("package", help="package to analyze (e.g. the one with the CVE)")
    parser.add_argument("--html", default=None, help="HTML report path (default: <project_dir>/report.html)")
    args = parser.parse_args(argv)

    project = Path(args.project_dir)
    registry = json.loads((project / "deps.json").read_text(encoding="utf-8"))
    critical = parse_critical_paths(
        (project / "critical_paths.txt").read_text(encoding="utf-8")
    )
    graph = DepGraph.from_registry(registry)

    declared: list[tuple[str, str]] = []
    pkg_json = project / "package.json"
    if pkg_json.exists():
        declared += parse_package_json(pkg_json.read_text(encoding="utf-8"))
    reqs = project / "requirements.txt"
    if reqs.exists():
        declared += parse_requirements(reqs.read_text(encoding="utf-8"))
    if declared:
        print("Declared dependencies: " + ", ".join(n for n, _ in declared))
        print()

    result = blast_radius(graph, args.package, critical)
    print(text_report(result, critical))

    html_path = Path(args.html) if args.html else project / "report.html"
    html_path.write_text(html_report(graph, result, critical), encoding="utf-8")
    print(f"\nHTML report written to {html_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
