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

### Explorer navigation iteration (2026-10-12)
- Added project-file navigator alongside relationship map and function inspector.
- Module selection filters the graph to one Python file, with a resettable "All modules" selection.
- Fit-to-view adjusts initial zoom based on function count and viewport.
- Callers/callees in the function inspector navigate directly to the target function and module.
- Added regression test asserting navigation controls are served.
- JavaScript/browser interaction and GitHub CI remain to be verified in a live run.
- Future: actual dependency-aware layout, function/source grouping and better handling of large graphs.

### Hierarchical drill-down iteration (2026-10-12)
- Added application/module/function architecture-level selector.
- Application view aggregates direct function-call edges across source files.
- Module view includes module functions plus directly connected external-module functions.
- Function view focuses on one selected function and its immediate callers and callees.
- Module nodes drill into the selected module; function nodes drill into dependencies.
- Added interface regression checks; live browser and CI verification still required.
- Next: true directed graph layout, multi-hop depth controls, import-based dependency edges, GitHub source hyperlinks and a confidence model.

### Dependency-aware layout iteration (2026-10-12)
- Render caller-to-dependency layers instead of alphabetical row layout using a Kahn-style traversal.
- Application modules use labelled rectangular cards with counts; test modules use a separate visual style.
- Curved, directed connections and fit-to-view support; low-opacity unrelated edges when a function is selected.
- Fallback places cyclic/unlayered nodes into the initial layer; robust cycle condensation remains a future task.
- HTML regression assertion added; live browser/CI verification pending.
- Planned: include import-only dependencies, improve cycle handling, highlight selected paths, and add source hyperlinks.

### Dependency inspection iteration (2026-10-12)
- Added static internal Python module import edge extraction, retained separately from call edges.
- Application view overlays import-only links with dashed amber styling alongside solid call links.
- Selected module/function adjacency is highlighted, with unrelated graph edges dimmed.
- Function details link to GitHub source file and line for canonical GitHub URL inputs (currently defaults to main).
- Added regression tests for relative internal module imports and UI controls.
- Follow-up: include pinned scanned Git SHA in reports, resolve imported symbols more precisely, and expand highlighting to multi-hop paths.
- Avoid interpreting module imports as proof of runtime execution.

### Cycle detection and tracing iteration (2026-10-12)
- Added Tarjan-style strongly-connected component detection for resolved function calls and internal module imports.
- Exposed function_cycles and module_import_cycles in the JSON report and summary.
- Added multi-hop tracing selector (1/2/3/all) for function-level dependency exploration.
- Included detected cycles in Markdown documentation export.
- Added focused regression tests for simple call cycles, import cycles and UI selector presence.
- Limitations: cycles reflect *resolved* relationships only; false or missing call resolutions affect results. Multi-hop tracing follows edges in both directions for exploration, not execution sequencing.
- Next: graph cycle highlighting, runtime/browser interaction tests, analysis provenance (commit SHA), and scalable graph layout.

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

### Documentation Centre iteration (2026-10-12)
- Extracted module docstrings, function docstrings, parameters, and return annotations using AST; no analysed code execution.
- Added module dependency summaries and function counts to the API result.
- Expanded the searchable Documentation Centre and Markdown export with source-derived descriptions.
- Added regression tests for metadata extraction and interface content.
- Pending: CI/browser verification, scanned commit provenance, class/API catalogues, PDF export and documentation quality checks.

### Class and API documentation iteration (2026-10-12)
- Added class docstrings, base classes, source locations, and direct method inventories.
- Identified literal HTTP route decorators for GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS, including FastAPI/Flask-style decorators.
- Added searchable class catalogue and API route catalogue with handler navigation.
- Added these sections to Markdown documentation export.
- Limitations: dynamically generated routes, route prefixes, decorator aliases, nonliteral paths and runtime registration are not resolved.
- Next: repository/commit provenance and robust Markdown/PDF/HTML export.

### Source provenance and export iteration (2026-10-12)
- The analysis API now returns provenance: source type, canonical GitHub repository URL, and git HEAD SHA when available.
- GitHub function inspector hyperlinks use the scanned immutable commit instead of assuming the main branch.
- Markdown export includes source provenance and commit information.
- Added standalone HTML report export (escaped structured JSON for offline inspection); designed documentation layout is a later enhancement.
- Added web regression tests for provenance and HTML controls.
- Limitations: local uncommitted changes cannot be identified by git HEAD alone. Non-GitHub local scans intentionally have no remote-source link. ZIP upload, branch selector and HTML/PDF report styling remain outstanding.
- Verification: commits pushed; automated CI status and local browser tests still pending.

### Printable standalone architecture report iteration (2026-10-12)
- Replaced the raw-JSON HTML export with a structured self-contained HTML report.
- Includes analysis summary, source provenance, modules, classes, API routes, functions, call edges, import edges, cycles, parse errors and analysis limitations.
- Report escapes source-derived text and uses embedded CSS with print styling; no external CDN required.
- Added regression assertions for report sections and print CSS.
- Outstanding: visual dependency diagrams in export, automated browser validation, PDF-generation pipeline, class/route fidelity improvements and layout testing with large repositories.
