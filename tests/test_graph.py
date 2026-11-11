import json
from pathlib import Path

from depgraph.graph import DepGraph
from depgraph.parsers import parse_critical_paths

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "sample_project"


def load_graph() -> DepGraph:
    registry = json.loads((FIXTURE / "deps.json").read_text(encoding="utf-8"))
    return DepGraph.from_registry(registry)


def load_critical() -> list[str]:
    return parse_critical_paths(
        (FIXTURE / "critical_paths.txt").read_text(encoding="utf-8")
    )


def test_transitive_dependents():
    graph = load_graph()
    assert graph.transitive_dependents("qs") == {"body-parser", "express"}
    assert graph.transitive_dependents("ms") == {"debug", "body-parser", "express"}
    assert graph.transitive_dependents("express") == set()


def test_reachability_from_critical_entries():
    graph = load_graph()
    reachable = graph.reachable_from(load_critical())
    assert {"express", "qs", "ms", "react", "scheduler", "certifi"} <= reachable
    # axios and lodash are in the tree but under no critical entry point.
    assert "lodash" not in reachable
    assert "axios" not in reachable


def test_shortest_path():
    graph = load_graph()
    assert graph.shortest_path("express", "ms") == ["express", "debug", "ms"]
    assert graph.shortest_path("react", "qs") is None
