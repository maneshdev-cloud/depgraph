from depgraph.parsers import (
    parse_critical_paths,
    parse_package_json,
    parse_requirements,
)


def test_requirements_parsing():
    text = """
# a comment
requests==2.31.0
urllib3>=1.26.0,<3.0
flask[async]==3.0.0  # inline comment
-e git+https://example.com/repo.git#egg=devonly
"""
    parsed = dict(parse_requirements(text))
    assert parsed["requests"] == "==2.31.0"
    assert parsed["urllib3"] == ">=1.26.0,<3.0"
    assert parsed["flask"] == "==3.0.0"  # extras stripped from the name
    assert "devonly" not in parsed  # option lines skipped


def test_package_json_merges_dependencies_and_dev():
    text = (
        '{"dependencies": {"express": "^4.18.2"},'
        ' "devDependencies": {"jest": "^29.7.0"}}'
    )
    parsed = dict(parse_package_json(text))
    assert parsed == {"express": "^4.18.2", "jest": "^29.7.0"}


def test_critical_paths_parsing():
    assert parse_critical_paths("# note\nexpress\n\nreact # web\n") == [
        "express",
        "react",
    ]
