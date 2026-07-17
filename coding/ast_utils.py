import ast
import os
from typing import Any


def parse_file(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
        return {
            "filepath": filepath,
            "source_length": len(source),
            "has_syntax_error": False,
            "imports": _get_imports(tree),
            "functions": _get_functions(tree),
            "classes": _get_classes(tree),
        }
    except SyntaxError as e:
        return {"filepath": filepath, "has_syntax_error": True, "error": str(e)}
    except Exception as e:
        return {"filepath": filepath, "error": str(e)}


def _get_imports(tree: ast.AST) -> list[dict]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"type": "import", "name": alias.name, "alias": alias.asname})
        elif isinstance(node, ast.ImportFrom):
            imports.append({
                "type": "from_import",
                "module": node.module or "",
                "names": [{"name": alias.name, "alias": alias.asname} for alias in node.names],
            })
    return imports


def _get_functions(tree: ast.AST) -> list[dict]:
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "args": [arg.arg for arg in node.args.args],
                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
            })
    return funcs


def _get_classes(tree: ast.AST) -> list[dict]:
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "methods": [
                    {"name": n.name, "lineno": n.lineno}
                    for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ],
            })
    return classes


def get_function_info(filepath: str, function_name: str) -> dict:
    info = parse_file(filepath)
    if info.get("has_syntax_error"):
        return info
    for fn in info.get("functions", []):
        if fn["name"] == function_name:
            return {"filepath": filepath, "function": fn, "found": True}
    for cls in info.get("classes", []):
        for m in cls.get("methods", []):
            if m["name"] == function_name:
                return {"filepath": filepath, "class": cls["name"], "method": m, "found": True}
    return {"filepath": filepath, "function_name": function_name, "found": False}


def find_references(filepath: str, symbol: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        refs = []
        for i, line in enumerate(lines, 1):
            if symbol in line:
                refs.append({
                    "line": i,
                    "column": line.index(symbol) + 1,
                    "text": line.strip()[:150],
                })
        return {"filepath": filepath, "symbol": symbol, "references": refs, "count": len(refs)}
    except Exception as e:
        return {"filepath": filepath, "symbol": symbol, "error": str(e)}


def rename_symbol(filepath: str, old_name: str, new_name: str, dry_run: bool = True) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = content.replace(old_name, new_name)
        changes = sum(1 for a, b in zip(content, new_content) if a != b)

        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

        return {
            "filepath": filepath,
            "old_name": old_name,
            "new_name": new_name,
            "changes": changes,
            "dry_run": dry_run,
            "success": True,
        }
    except Exception as e:
        return {"filepath": filepath, "old_name": old_name, "new_name": new_name, "error": str(e), "success": False}
