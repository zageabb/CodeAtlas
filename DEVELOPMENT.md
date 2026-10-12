# CodeAtlas Development Plan

## Status
**Milestone 2 — interactive graph and Markdown documentation interface implemented; CI/runtime verification pending.**

### Implemented
- FastAPI minimal web UI and JSON endpoint
- Read-only static Python AST scanning
- Function catalogues and intra-project call edges
- Heuristic entry point reachability and orphan candidates
- Imports, unresolved call list and parse errors
- GitHub public HTTPS shallow-clone and local folder sources
- JSON CLI export, pytest baseline and GitHub Actions workflow

### Milestone 2 progress (2026-10-12)
- Improved handling for local class methods, self/cls calls, constructors and NodeVisitor callbacks.
- Added classification of external/builtin calls separately from ambiguous attribute calls.
- Recognised pytest test functions and AST method aliases as externally referenced.
- Added targeted regression tests for these cases.
- Self-scan should be repeated and compared with baseline (6 files, 14 functions, 7 resolved calls, 97 unresolved calls, 8 orphan candidates).
- CI is not yet verified; local clone of GitHub repo was unavailable in the execution environment.

### Milestone 2 visualisation progress (2026-10-12)
- Introduced standalone interactive SVG function graph (no CDN dependency), including search, scope filters, pan/zoom and caller/callee details.
- Added Documentation Centre function catalogue with source location and call metadata.
- Added downloadable Markdown function catalogue and Mermaid call graph, alongside JSON export.
- Packaged frontend HTML inside the Python distribution, with the FastAPI root serving this asset.
- Added route/UI regression tests. Production hardening and CI verification remain pending.

### Remaining: Milestone 2 — reliability and visualisation
- Correctly model imports, `self.method()`, `cls.method()` and scoped names
- Discover Flask/FastAPI routers, callbacks and background tasks
- Distinguish unknown reachability from confirmed disconnected components
- Improve graph layout for large projects; evaluate Cytoscape.js once core layout usability is validated
- Add scanned commit SHA, branch selection, caching, pagination and size/time limits
- Formal threat model for symlinks, local-path access, clone isolation and credentials
- Restrict/disable arbitrary local path scans for deployed web instances

### Milestone 3 — Documentation Centre
- Function, class, module and feature catalogues with source links
- Mermaid diagrams, Markdown/HTML/PDF export
- Architectural summaries with clear evidence versus inference labels

### Milestone 4 — multi-language and CI
- JavaScript/TypeScript relationships, templates, HTTP route links, SQL dependencies
- Diff between commits, architecture regression reports, GitHub PR annotations

### Release rule
CI green and manual localhost smoke test before declaring milestone complete.
