import json
from pathlib import Path

from depgraph.analyze import blast_radius
from depgraph.graph import DepGraph
from depgraph.parsers import parse_critical_paths
from depgraph.report import html_report, text_report

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "sample_project"


def setup():
    registry = json.loads((FIXTURE / "deps.json").read_text(encoding="utf-8"))
    graph = DepGraph.from_registry(registry)
    critical = parse_critical_paths(
        (FIXTURE / "critical_paths.txt").read_text(encoding="utf-8")
    )
    return graph, critical


def test_critical_transitive_package_scores_high():
    graph, critical = setup()
    result = blast_radius(graph, "qs", critical)
    assert result.reachable_from == ["express"]
    assert result.direct_dependents == ["body-parser", "express"]
    assert result.shortest_path == ["express", "qs"]
    assert result.score >= 70


def test_uncritical_leaf_scores_zero():
    graph, critical = setup()
    result = blast_radius(graph, "lodash", critical)
    assert result.reachable_from == []
    assert result.shortest_path is None
    assert result.score == 0


def test_reports_render():
    graph, critical = setup()
    result = blast_radius(graph, "qs", critical)
    text = text_report(result, critical)
    assert "qs" in text and "/100" in text
    page = html_report(graph, result, critical)
    assert "<svg" in page and "qs" in page
