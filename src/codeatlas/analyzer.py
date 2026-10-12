"""Read-only, best-effort Python AST analysis.

This scanner deliberately does not import or execute analysed application code.
"""
from __future__ import annotations

import ast
from collections import defaultdict, deque
from pathlib import Path

SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
ENTRYPOINT_NAMES = {"main", "run", "create_app", "app_factory"}


class _Scanner(ast.NodeVisitor):
    def __init__(self, module: str, relative_path: str):
        self.module = module
        self.path = relative_path
        self.stack: list[str] = []
        self.functions: list[dict] = []
        self.calls: list[tuple[str, str]] = []
        self.imports: list[str] = []
        self.decorators: dict[str, list[str]] = {}
        self.classes: dict[str, list[str]] = {}

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.extend(alias.name for alias in node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append("." * node.level + node.module)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes[".".join([self.module, *self.stack, node.name])] = [ast.unparse(base) for base in node.bases]
        self.stack.append(node.name)
        for statement in node.body:
            self.visit(statement)
        self.stack.pop()

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualified = ".".join([self.module, *self.stack, node.name])
        decorators = [ast.unparse(dec) for dec in node.decorator_list]
        self.functions.append({
            "id": qualified, "name": node.name, "path": self.path,
            "line": node.lineno, "async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": decorators,
        })
        self.decorators[qualified] = decorators
        self.stack.append(node.name)
        for statement in node.body:
            self.visit(statement)
        self.stack.pop()

    visit_FunctionDef = _function
    visit_AsyncFunctionDef = _function

    def visit_Call(self, node: ast.Call) -> None:
        if self.stack:
            try:
                callee = ast.unparse(node.func)
                caller = ".".join([self.module, *self.stack])
                self.calls.append((caller, callee))
            except (TypeError, ValueError):
                pass
        self.generic_visit(node)


def _module_name(relative: Path) -> str:
    pieces = list(relative.with_suffix("").parts)
    if pieces[-1] == "__init__":
        pieces.pop()
    return ".".join(pieces) or "__init__"


def analyze(root: str | Path) -> dict:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Source must be a directory")
    functions: list[dict] = []
    raw_calls: list[tuple[str, str]] = []
    imports: list[dict] = []
    classes: dict[str, list[str]] = {}
    errors: list[dict] = []
    files = 0

    for source in sorted(root.rglob("*.py")):
        if any(part in SKIP or part.startswith(".") for part in source.relative_to(root).parts):
            continue
        relative = source.relative_to(root)
        files += 1
        try:
            tree = ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(relative))
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append({"path": str(relative), "error": str(exc)})
            continue
        visitor = _Scanner(_module_name(relative), relative.as_posix())
        visitor.visit(tree)
        classes.update(visitor.classes)
        functions.extend(visitor.functions)
        raw_calls.extend(visitor.calls)
        imports.append({"path": relative.as_posix(), "modules": sorted(set(visitor.imports))})

    by_id = {f["id"]: f for f in functions}
    by_short: dict[str, list[str]] = defaultdict(list)
    for item in functions:
        by_short[item["name"]].append(item["id"])
    edges: set[tuple[str, str]] = set()
    unresolved: list[dict] = []
    external: list[dict] = []
    module_names = {_module_name(Path(f["path"])) for f in functions}

    for caller, expression in raw_calls:
        if caller not in by_id:
            continue
        module = _module_name(Path(by_id[caller]["path"]))
        scopes = caller.split(".")
        class_scope = caller.rsplit(".", 1)[0]
        candidates: list[str] = []
        if expression.startswith(("self.", "cls.")):
            method = expression.split(".", 1)[1]
            candidates.append(class_scope + "." + method)
            for base in classes.get(class_scope, []):
                candidates.append(module + "." + base + "." + method)
        elif "." not in expression:
            # Nested/local function then module-level function, then constructor.
            candidates.extend([
                class_scope + "." + expression,
                module + "." + expression,
                module + "." + expression + ".__init__",
            ])
            # An inherited visitor method can be invoked by AST dispatch.
            if expression in by_short and len(by_short[expression]) == 1:
                candidates.extend(by_short[expression])
        else:
            candidates.append(module + "." + expression)
        target = next((name for name in candidates if name in by_id), None)
        if target:
            edges.add((caller, target))
        elif expression.startswith(("self.", "cls.")) or expression.split(".", 1)[0] in {
            name.rsplit(".", 1)[-1] for name in classes
        }:
            unresolved.append({"caller": caller, "expression": expression, "category": "dynamic_or_attribute"})
        else:
            external.append({"caller": caller, "expression": expression, "category": "external_or_builtin"})

    # Constructors and AST NodeVisitor dispatch are indirectly invoked.
    for item in functions:
        if item["name"] == "__init__":
            owner = item["id"].rsplit(".", 1)[0]
            constructor = owner.rsplit(".", 1)[-1]
            for caller, expression in raw_calls:
                if expression == constructor and caller in by_id:
                    edges.add((caller, item["id"]))
        if item["name"].startswith("visit_"):
            owner = item["id"].rsplit(".", 1)[0]
            if any("NodeVisitor" in base for base in classes.get(owner, [])):
                # Framework-dispatched callback; deliberately an entry point candidate.
                item["framework_callback"] = True

    incoming: dict[str, int] = defaultdict(int)
    outgoing: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        incoming[dst] += 1
        outgoing[src].append(dst)

    # Framework-decorated functions and common entry point names are roots,
    # but this heuristic does not guarantee runtime reachability.
    roots = sorted(f["id"] for f in functions if
                   f["name"] in ENTRYPOINT_NAMES or
                   (f["path"].startswith("tests/") and f["name"].startswith("test_")) or
                   f.get("framework_callback", False) or
                   any(d.startswith(("app.get(", "app.post(", "app.put(", "app.delete(", "router.", "pytest.")) for d in f["decorators"]))
    reachable = set(roots)
    queue = deque(roots)
    while queue:
        for target in outgoing[queue.popleft()]:
            if target not in reachable:
                reachable.add(target)
                queue.append(target)

    for item in functions:
        item["incoming_calls"] = incoming[item["id"]]
        item["entrypoint_candidate"] = item["id"] in roots
        item["reachable_from_known_entrypoint"] = item["id"] in reachable
        item["orphan_candidate"] = (incoming[item["id"]] == 0 and item["id"] not in roots
                                   and item["name"] not in {"__init__", "_function"} )

    return {
        "root": str(root),
        "summary": {
            "python_files": files, "functions": len(functions),
            "resolved_calls": len(edges), "unresolved_calls": len(unresolved),
            "external_or_builtin_calls": len(external),
            "orphan_candidates": sum(f["orphan_candidate"] for f in functions),
            "reachable_from_known_entrypoints": len(reachable),
        },
        "functions": sorted(functions, key=lambda f: f["id"]),
        "calls": [{"source": a, "target": b} for a, b in sorted(edges)],
        "unresolved_calls": unresolved, "external_calls": external,
        "imports": imports, "errors": errors,
        "limitations": [
            "Best-effort static Python analysis; no target code executed",
            "Dynamic calls, instance method dispatch and cross-module aliases may be unresolved",
            "Orphan candidates are not confirmed unused code",
        ],
    }
