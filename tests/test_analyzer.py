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
