import os

from coding.ast_utils import parse_file, get_function_info, find_references, rename_symbol
from coding.indexer import get_project_index, ProjectIndex
from coding.test_runner import run_tests, run_lint, run_format
from plugins.base import ToolPlugin


class ParseFilePlugin(ToolPlugin):
    name = "parse_file"
    description = "Parse a source file and return its AST structure: imports, functions, classes, and line numbers."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the source file"},
            },
            "required": ["filepath"],
        }

    def execute(self, filepath: str) -> dict:
        return parse_file(filepath)


class FunctionInfoPlugin(ToolPlugin):
    name = "function_info"
    description = "Get detailed information about a specific function or method in a source file."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the source file"},
                "function_name": {"type": "string", "description": "Name of the function or method"},
            },
            "required": ["filepath", "function_name"],
        }

    def execute(self, filepath: str, function_name: str) -> dict:
        return get_function_info(filepath, function_name)


class FindReferencesPlugin(ToolPlugin):
    name = "find_references"
    description = "Find all references to a symbol (variable, function, class) in a file with line numbers."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the file"},
                "symbol": {"type": "string", "description": "The symbol name to search for"},
            },
            "required": ["filepath", "symbol"],
        }

    def execute(self, filepath: str, symbol: str) -> dict:
        return find_references(filepath, symbol)


class RenameSymbolPlugin(ToolPlugin):
    name = "rename_symbol"
    description = "Rename a symbol across a file. Supports dry-run mode to preview changes first."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to the file"},
                "old_name": {"type": "string", "description": "Current symbol name"},
                "new_name": {"type": "string", "description": "New symbol name"},
                "dry_run": {"type": "boolean", "description": "Preview changes without applying (default: true)"},
            },
            "required": ["filepath", "old_name", "new_name"],
        }

    def execute(self, filepath: str, old_name: str, new_name: str, dry_run: bool = True) -> dict:
        return rename_symbol(filepath, old_name, new_name, dry_run)


class ProjectIndexPlugin(ToolPlugin):
    name = "project_index"
    description = "Index a project directory and get a summary of files by type and extension."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory to index (default: current directory)"},
                "force": {"type": "boolean", "description": "Force re-indexing (default: false)"},
            },
            "required": [],
        }

    def execute(self, path: str = "", force: bool = False) -> dict:
        root = os.path.abspath(path) if path else os.getcwd()
        idx = get_project_index(root)
        return idx.index(force=force)


class ProjectSearchPlugin(ToolPlugin):
    name = "project_search"
    description = "Search the project index for files matching a path pattern, optionally filtered by type."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "File path pattern to search for"},
                "file_type": {
                    "type": "string",
                    "description": "Filter by type: source, doc, config, package (optional)",
                },
            },
            "required": ["query"],
        }

    def execute(self, query: str, file_type: str = "") -> dict:
        idx = get_project_index()
        results = idx.search_files(query, file_type if file_type else None)
        return {"query": query, "results": results, "count": len(results)}


class ProjectStructurePlugin(ToolPlugin):
    name = "project_structure"
    description = "Get the project directory tree structure up to a given depth."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "max_depth": {"type": "integer", "description": "Maximum directory depth (default: 3)"},
            },
            "required": [],
        }

    def execute(self, max_depth: int = 3) -> dict:
        idx = get_project_index()
        return idx.get_structure(max_depth=max_depth)


class RunTestsPlugin(ToolPlugin):
    name = "run_tests"
    description = "Run tests using pytest. Optionally specify a path and verbose output."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Test path or file (default: current dir)"},
                "verbose": {"type": "boolean", "description": "Verbose output (default: false)"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)"},
            },
            "required": [],
        }

    def execute(self, path: str = ".", verbose: bool = False, timeout: int = 60) -> dict:
        return run_tests(path, timeout, verbose)


class RunLintPlugin(ToolPlugin):
    name = "run_lint"
    description = "Lint source files using ruff. Returns a list of issues found."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or directory to lint (default: current dir)"},
            },
            "required": [],
        }

    def execute(self, path: str = ".") -> dict:
        return run_lint(path)


class RunFormatPlugin(ToolPlugin):
    name = "run_format"
    description = "Check or apply code formatting using ruff. Default is check-only mode."
    category = "code"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or directory to format (default: current dir)"},
                "apply": {"type": "boolean", "description": "Apply formatting instead of just checking (default: false)"},
            },
            "required": [],
        }

    def execute(self, path: str = ".", apply: bool = False) -> dict:
        return run_format(path, check=not apply)
