# CodeAtlas contributor guidance

- Maintain a read-only source analysis model. Never execute code from a scanned repository.
- Keep `src/codeatlas/analyzer.py` deterministic and return evidence for every finding.
- Label possible unused code as a *candidate*, not a proven defect.
- Keep acquisition (`source.py`), analysis (`analyzer.py`), and presentation (`web.py`) separate.
- Add regression tests for every change to detection or call resolution.
- Never commit credentials; use least-privilege access for private repositories.
- Public deployment requires authentication, scan limits, source restrictions, and job isolation.
- Update DEVELOPMENT.md for milestone completion, limitations and next actions.
