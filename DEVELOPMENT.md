# CodeAtlas Development Plan

## Status
**Milestone 1 — initial scaffold implemented (pending CI verification).**

### Implemented
- FastAPI minimal web UI and JSON endpoint
- Read-only static Python AST scanning
- Function catalogues and intra-project call edges
- Heuristic entry point reachability and orphan candidates
- Imports, unresolved call list and parse errors
- GitHub public HTTPS shallow-clone and local folder sources
- JSON CLI export, pytest baseline and GitHub Actions workflow

### Next: Milestone 2 — reliability and visualisation
- Correctly model imports, `self.method()`, `cls.method()` and scoped names
- Discover Flask/FastAPI routers, callbacks and background tasks
- Distinguish unknown reachability from confirmed disconnected components
- Integrate Cytoscape.js interactive graph; filtering/search/drill-down
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
