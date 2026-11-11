"""Text and standalone-HTML reports for a blast-radius analysis.

The HTML report is a single self-contained file: the dependency graph
is drawn as inline SVG (no JavaScript, no external assets) with the
analysed package in red and critical entry points ringed in green.
"""

from __future__ import annotations

import html
import math

from .analyze import BlastRadius
from .graph import DepGraph


def text_report(result: BlastRadius, critical_entries: list[str]) -> str:
    lines = [
        f"Blast radius for '{result.package}'",
        "=" * (22 + len(result.package)),
        f"Blast radius score : {result.score}/100",
        f"Reachable from critical paths: "
        + (", ".join(result.reachable_from) if result.reachable_from else "NO"),
    ]
    if result.shortest_path:
        lines.append(
            "Shortest critical path: " + " -> ".join(result.shortest_path)
        )
    lines += [
        f"Direct dependents ({len(result.direct_dependents)}): "
        + (", ".join(result.direct_dependents) or "none"),
        f"Transitive dependents ({len(result.transitive_dependents)}): "
        + (", ".join(result.transitive_dependents) or "none"),
        f"Graph size: {result.total_packages} packages; "
        f"critical entries: {', '.join(critical_entries)}",
    ]
    return "\n".join(lines)


def html_report(
    graph: DepGraph, result: BlastRadius, critical_entries: list[str]
) -> str:
    names = sorted(graph.packages)
    cx, cy, radius = 420, 300, 220
    positions: dict[str, tuple[float, float]] = {}
    for i, name in enumerate(names):
        angle = 2 * math.pi * i / max(1, len(names)) - math.pi / 2
        positions[name] = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))

    edges = []
    for pkg, deps in sorted(graph.deps.items()):
        for dep in deps:
            x1, y1 = positions[pkg]
            x2, y2 = positions[dep]
            hot = dep == result.package or pkg == result.package
            edges.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{"#e5484d" if hot else "#c3ccd6"}" '
                f'stroke-width="{2 if hot else 1}" marker-end="url(#arrow)"/>'
            )

    nodes = []
    for name in names:
        x, y = positions[name]
        if name == result.package:
            fill, stroke, width = "#e5484d", "#7a1f22", 2
            label_fill = "#ffffff"
        elif name in critical_entries:
            fill, stroke, width = "#e6f4ea", "#30a46c", 3
            label_fill = "#17351f"
        else:
            fill, stroke, width = "#eef1f4", "#8b9bab", 1
            label_fill = "#22303c"
        nodes.append(
            f'<g><circle cx="{x:.0f}" cy="{y:.0f}" r="26" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>'
            f'<text x="{x:.0f}" y="{y + 4:.0f}" text-anchor="middle" '
            f'font-size="10" fill="{label_fill}">{html.escape(name)}</text></g>'
        )

    path_text = (
        " -&gt; ".join(html.escape(p) for p in result.shortest_path)
        if result.shortest_path
        else "not reachable from any critical entry"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8">
<title>DepGraph — blast radius: {html.escape(result.package)}</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;color:#22303c}}
.score{{font-size:2rem;font-weight:700}}</style></head>
<body>
<h1>Blast radius: {html.escape(result.package)}</h1>
<p class="score">{result.score}/100</p>
<p><strong>Shortest critical path:</strong> {path_text}</p>
<p><strong>Direct dependents:</strong> {html.escape(", ".join(result.direct_dependents) or "none")}<br>
<strong>Transitive dependents:</strong> {html.escape(", ".join(result.transitive_dependents) or "none")}</p>
<svg width="840" height="600" viewBox="0 0 840 600" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3"
orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#8b9bab"/></marker></defs>
{''.join(edges)}
{''.join(nodes)}
</svg>
<p>Red node = analysed package. Green ring = critical entry point.</p>
</body></html>
"""
