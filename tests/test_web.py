"""Smoke tests for CodeAtlas visual interface and analysis API."""
from fastapi.testclient import TestClient

from codeatlas.web import app


def test_home_serves_interactive_explorer():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Function map" in response.text
    assert "Documentation centre" in response.text
    assert "Export documentation" in response.text
    assert "application/json" in response.text


def test_analyse_endpoint_supplies_graph_and_catalogue(tmp_path):
    (tmp_path / "example.py").write_text(
        "def main():\n    helper()\n\ndef helper():\n    return 3\n",
        encoding="utf-8",
    )
    response = TestClient(app).post("/api/analyse", json={"source": str(tmp_path)})
    assert response.status_code == 200
    report = response.json()
    assert len(report["functions"]) == 2
    assert {"source": "example.main", "target": "example.helper"} in report["calls"]


def test_rejects_non_github_network_source():
    response = TestClient(app).post(
        "/api/analyse", json={"source": "https://example.com/sample"}
    )
    assert response.status_code == 400


def test_explorer_module_navigation_and_linked_dependencies():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert 'id="project-tree"' in response.text
    assert "function renderTree()" in response.text
    assert "function fitGraph()" in response.text
    assert "class:'relation'" in response.text
    assert "activeModule=target.path" in response.text
