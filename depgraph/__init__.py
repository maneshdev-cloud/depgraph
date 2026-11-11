"""DepGraph — dependency blast-radius analyzer."""

from .analyze import BlastRadius, blast_radius
from .graph import DepGraph
from .parsers import parse_critical_paths, parse_package_json, parse_requirements
from .report import html_report, text_report

__all__ = [
    "BlastRadius",
    "DepGraph",
    "blast_radius",
    "html_report",
    "parse_critical_paths",
    "parse_package_json",
    "parse_requirements",
    "text_report",
]

__version__ = "0.1.0"
