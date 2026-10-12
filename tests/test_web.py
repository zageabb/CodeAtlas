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


def test_architecture_drilldown_controls():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    page = response.text
    assert 'id="level"' in page
    assert 'value="application"' in page
    assert 'value="module"' in page
    assert 'value="function"' in page
    assert "function displayModel()" in page
    assert "level==='application'" in page
    assert "level==='module'" in page
    assert "level==='function'" in page
    assert "activeModule=f.path" in page


def test_dependency_layout_and_module_cards():
    page = TestClient(app).get("/").text
    assert "function graphLayout(nodes,edges)" in page
    assert "Kahn-style layering" in page
    assert "f.kind==='module'" in page
    assert "f.path.startsWith('tests/')" in page
    assert "make('rect'" in page


def test_import_edges_and_github_source_links_available():
    page = TestClient(app).get("/").text
    assert "module_import_edges" in page
    assert "function sourceUrl(path,line)" in page
    assert "Open source on GitHub" in page
    assert "edge.type==='import'" in page


def test_multihop_tracing_and_cycle_documentation_ui():
    page = TestClient(app).get("/").text
    assert 'id="depth"' in page
    assert "selectedNeighborhood=new Set([selected])" in page
    assert "Module import cycles" in page
    assert "Function call cycles" in page


def test_documentation_centre_metadata_fields():
    page = TestClient(app).get('/').text
    assert 'id="modules"' in page
    assert 'No module docstring provided.' in page
    assert 'No docstring provided.' in page
    assert 'f.parameters' in page


def test_documentation_centre_class_and_route_sections():
    page = TestClient(app).get("/").text
    assert 'id="classes"' in page
    assert 'id="routes"' in page
    assert 'report.api_routes' in page
    assert 'report.classes' in page


def test_provenance_present_for_local_scan(tmp_path):
    (tmp_path / "example.py").write_text("def main():\n    return 1\n", encoding="utf-8")
    report = TestClient(app).post("/api/analyse", json={"source": str(tmp_path)}).json()
    assert report["provenance"]["repository_url"] is None
    assert report["provenance"]["immutable_source_links"] is False
    assert report["provenance"]["source"] == "local directory"


def test_html_export_and_pinned_source_links():
    page = TestClient(app).get("/").text
    assert 'id="html-export"' in page
    assert "provenance?.commit_sha" in page
    assert "codeatlas-documentation.html" in page


def test_exportable_architecture_report_sections():
    page = TestClient(app).get("/").text
    assert "function htmlReport(data)" in page
    assert "Application architecture report" in page
    assert "Module catalogue" in page
    assert "API endpoints" in page
    assert "Circular dependencies" in page
    assert "@media print" in page
