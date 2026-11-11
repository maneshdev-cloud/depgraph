"""Blast-radius analysis: how much of a project does one package touch?

When a CVE drops for a package, the raw question "is it in my tree?"
is almost useless — nearly everything is in the tree.  The useful
questions are:

1. **Is it reachable from a critical entry point?** A vulnerable
   package that only shows up in a dev tool is a very different fire
   from one sitting under your payment route.
2. **How many packages depend on it?** That is the size of the
   upgrade/pin/migration job.
3. **How deep is it?** Deep transitive packages are the ones nobody
   remembers installing.

The score combines the three into a 0–100 blast radius.
"""

from __future__ import annotations

from dataclasses import dataclass

from .graph import DepGraph


@dataclass
class BlastRadius:
    package: str
    total_packages: int
    direct_dependents: list[str]
    transitive_dependents: list[str]
    reachable_from: list[str]  # critical entries that can reach the package
    shortest_path: list[str] | None  # from the closest critical entry
    score: int


def blast_radius(
    graph: DepGraph, package: str, critical_entries: list[str]
) -> BlastRadius:
    direct = sorted(graph.direct_dependents(package))
    transitive = sorted(graph.transitive_dependents(package))

    reachable_entries: list[str] = []
    best_path: list[str] | None = None
    for entry in critical_entries:
        path = graph.shortest_path(entry, package)
        if path is not None:
            reachable_entries.append(entry)
            if best_path is None or len(path) < len(best_path):
                best_path = path

    total = len(graph.packages)
    score = 0.0
    if reachable_entries:
        score += 50  # on a critical path: half the scale immediately
    if total > 1:
        score += 30 * (len(transitive) / (total - 1))
    if best_path is not None:
        edges = len(best_path) - 1
        score += 20 if edges <= 2 else 10 if edges <= 4 else 5

    return BlastRadius(
        package=package,
        total_packages=total,
        direct_dependents=direct,
        transitive_dependents=transitive,
        reachable_from=reachable_entries,
        shortest_path=best_path,
        score=int(round(min(100, score))),
    )
