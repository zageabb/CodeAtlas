# CodeAtlas

CodeAtlas maps Python application structure, traces function calls, finds potential orphan functions, and produces machine-readable documentation.

## First milestone

- Read-only analysis of a local folder, cloned Git repository, or GitHub URL
- Python AST function/class discovery, imports and call edges
- Reachability analysis from recognised entry points
- JSON analysis report and basic web UI
- No execution of target application code

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn codeatlas.web:app --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080. Enter a local project path or a public GitHub HTTPS URL. GitHub analysis clones into a temporary directory and needs `git` installed.

CLI:

```bash
codeatlas ./src --output report.json
codeatlas https://github.com/owner/repo --output report.json
pytest
```

## Security

Do not expose the analysis service publicly without authentication and access controls. The initial web interface permits scanning server-readable local paths and public HTTPS GitHub repositories, so bind to loopback only. The tool never runs scanned Python code, but fetching an untrusted repository still requires resource/time limits in a hardened production deployment.

## Analysis caveats

Static call resolution is approximate. Decorators, dependency injection, reflection, routes, callbacks, external consumers and dynamically dispatched methods can produce false positives. An orphan candidate is not proof of dead code. Only direct, statically resolved calls contribute to reachability.
