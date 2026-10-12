from codeatlas.analyzer import analyze


def test_calls_and_orphans(tmp_path):
    (tmp_path / "sample.py").write_text(
        "def main():\n    used()\n\ndef used():\n    pass\n\ndef forgotten():\n    pass\n",
        encoding="utf-8",
    )
    report = analyze(tmp_path)
    assert report["summary"]["functions"] == 3
    assert {"source": "sample.main", "target": "sample.used"} in report["calls"]
    functions = {f["name"]: f for f in report["functions"]}
    assert functions["used"]["reachable_from_known_entrypoint"]
    assert functions["forgotten"]["orphan_candidate"]
    assert not functions["main"]["orphan_candidate"]


def test_syntax_error_is_reported(tmp_path):
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    report = analyze(tmp_path)
    assert len(report["errors"]) == 1


def test_class_methods_constructor_and_pytest(tmp_path):
    (tmp_path / "sample.py").write_text(
        "class Worker:\n"
        "    def __init__(self):\n        self.ready = True\n"
        "    def work(self):\n        self.helper()\n"
        "    def helper(self):\n        return 1\n"
        "def main():\n    w = Worker()\n    w.work()\n",
        encoding="utf-8",
    )
    report = analyze(tmp_path)
    edges = {(e["source"], e["target"]) for e in report["calls"]}
    assert ("sample.main", "sample.Worker.__init__") in edges
    assert ("sample.Worker.work", "sample.Worker.helper") in edges
    assert not next(f for f in report["functions"] if f["id"] == "sample.Worker.__init__")["orphan_candidate"]


def test_framework_callbacks_and_external_calls(tmp_path):
    (tmp_path / "api.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/hello')\n"
        "def hello():\n    return sorted([3, 1])\n",
        encoding="utf-8",
    )
    report = analyze(tmp_path)
    function = next(f for f in report["functions"] if f["name"] == "hello")
    assert function["entrypoint_candidate"]
    assert not function["orphan_candidate"]
    assert any(call["expression"] == "sorted" for call in report["external_calls"])


def test_nodevisitor_methods_are_callbacks(tmp_path):
    (tmp_path / "visitor.py").write_text(
        "import ast\n"
        "class Visitor(ast.NodeVisitor):\n"
        "    def visit_Call(self, node):\n        return self.generic_visit(node)\n",
        encoding="utf-8",
    )
    report = analyze(tmp_path)
    function = next(f for f in report["functions"] if f["name"] == "visit_Call")
    assert function["entrypoint_candidate"]
    assert not function["orphan_candidate"]


def test_internal_import_edges(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "service.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    (pkg / "api.py").write_text(
        "from . import service\nfrom .service import run\n"
        "def main():\n    return run()\n", encoding="utf-8")
    report = analyze(tmp_path)
    assert {"source": "pkg/api.py", "target": "pkg/service.py", "type": "import"} in report["module_import_edges"]
    assert report["summary"]["internal_import_edges"] >= 1


def test_call_cycle_detected(tmp_path):
    (tmp_path / "cycles.py").write_text(
        "def main():\n    a()\n"
        "def a():\n    b()\n"
        "def b():\n    a()\n",
        encoding="utf-8",
    )
    report = analyze(tmp_path)
    assert ["cycles.a", "cycles.b"] in report["function_cycles"]
    assert report["summary"]["function_cycles"] == 1


def test_module_import_cycle_detected(tmp_path):
    (tmp_path / "a.py").write_text("import b\ndef run():\n    pass\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("import a\ndef run():\n    pass\n", encoding="utf-8")
    report = analyze(tmp_path)
    assert ["a.py", "b.py"] in report["module_import_cycles"]
    assert report["summary"]["module_import_cycles"] == 1
