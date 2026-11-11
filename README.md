# DepGraph

**Dependency blast-radius analyzer: when a package gets a CVE, find
out whether it actually matters to *your* critical paths — and how
much of your tree it drags with it.**

## Problem

Vulnerability scanners answer one question: "is package X somewhere
in your dependency tree?" The answer is almost always *yes*, which
makes it nearly useless for triage. A vulnerable package that only
exists under a dev tool is background noise; the same package sitting
underneath your checkout route is a fire.

DepGraph answers the sharper questions:

1. **Is it reachable from a critical entry point?** You declare the
   packages whose subtrees carry production traffic; DepGraph checks
   whether the vulnerable package lives under any of them, and shows
   the shortest path.
2. **How many packages depend on it?** Directly and transitively —
   that count is the real size of the upgrade job.
3. **What's the blast radius?** A 0–100 score combining critical
   reachability (50), share of the tree that depends on it (30), and
   depth below a critical entry (20).

## Features

- Parses `requirements.txt` (comments, extras, version specifiers)
  and `package.json` (dependencies + devDependencies).
- Builds a dependency graph from a registry description
  (`{package: [dependencies]}` JSON) and runs BFS reachability,
  transitive-dependent and shortest-path queries.
- Emits a plain-text report and a **standalone HTML report** with the
  graph drawn as inline SVG — vulnerable package in red, critical
  entry points ringed in green, zero JavaScript or external assets.
- Zero dependencies: Python 3.10+ standard library only.
- Ships with a fake sample project (`fixtures/sample_project`, a
  storefront mixing npm and pip packages) so you can run it instantly.

## How to run

```bash
# Analyze the sample project's `qs` package
python -m depgraph.cli fixtures/sample_project qs

# Deep transitive package under express
python -m depgraph.cli fixtures/sample_project ms --html ms-report.html

# Tests
pip install pytest
python -m pytest
```

Example output (abridged):

```
Blast radius for 'qs'
======================
Blast radius score : 75/100
Reachable from critical paths: express
Shortest critical path: express -> qs
Direct dependents (2): body-parser, express
Transitive dependents (2): body-parser, express
```

To analyze your own project, write a `deps.json` describing your
tree (`{package: [its dependencies]}`) and a `critical_paths.txt`
listing your entry points, one per line.

## Project structure

```
depgraph/
    __init__.py   public API re-exports
    parsers.py    requirements.txt / package.json / critical-paths parsing
    graph.py      DepGraph: reachability, dependents, shortest path (BFS)
    analyze.py    blast-radius computation and scoring
    report.py     text report + standalone HTML/SVG report
    cli.py        python -m depgraph.cli <project_dir> <package>
fixtures/
    sample_project/   fake storefront: package.json, requirements.txt,
                      deps.json, critical_paths.txt
tests/
    test_parsers.py   parsing edge cases
    test_graph.py     reachability on the sample graph
    test_analyze.py   scoring + report rendering
```

## Tech

Python 3.10+ (standard library only), pytest for tests.

## License

MIT — see `LICENSE`.
