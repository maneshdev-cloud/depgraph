"""A tiny dependency graph with reachability queries.

Edges point from a package to the packages it depends on::

    express -> {body-parser, debug, qs}

"Dependents" queries walk the edges backwards (who depends on X?),
which is what you need when a vulnerability lands in X.
"""

from __future__ import annotations

from collections import deque


class DepGraph:
    def __init__(self) -> None:
        self.deps: dict[str, set[str]] = {}

    # -- construction ---------------------------------------------------
    def add_package(self, name: str, dependencies=()) -> None:
        self.deps.setdefault(name, set()).update(dependencies)
        for dep in dependencies:
            self.deps.setdefault(dep, set())

    @classmethod
    def from_registry(cls, registry: dict[str, list[str]]) -> "DepGraph":
        """Build a graph from ``{package: [its dependencies]}``."""
        graph = cls()
        for name, deps in registry.items():
            graph.add_package(name, deps)
        return graph

    # -- basics ---------------------------------------------------------
    @property
    def packages(self) -> set[str]:
        return set(self.deps)

    def dependencies_of(self, name: str) -> set[str]:
        return set(self.deps.get(name, set()))

    def direct_dependents(self, name: str) -> set[str]:
        return {pkg for pkg, ds in self.deps.items() if name in ds}

    # -- reachability ---------------------------------------------------
    def transitive_dependents(self, name: str) -> set[str]:
        """Every package that depends on ``name``, directly or transitively."""
        seen: set[str] = set()
        queue = deque(self.direct_dependents(name))
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(self.direct_dependents(current) - seen)
        return seen

    def reachable_from(self, entries) -> set[str]:
        """Every package reachable by following dependency edges from ``entries``."""
        seen: set[str] = set()
        queue = deque(e for e in entries if e in self.deps)
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(self.deps[current] - seen)
        return seen

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        """Shortest dependency path ``source -> ... -> target``, or None."""
        if source not in self.deps:
            return None
        parent: dict[str, str | None] = {source: None}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                node: str | None = current
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return list(reversed(path))
            for nxt in self.deps[current]:
                if nxt not in parent:
                    parent[nxt] = current
                    queue.append(nxt)
        return None
