import os
import time
from typing import Any

from core.logger import info

IGNORE_DIRS = {
    "__pycache__", ".git", ".svn", "node_modules", "venv", ".venv",
    ".env", "env", "dist", "build", ".idea", ".vscode",
}
IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".dylib",
    ".exe", ".bin", ".obj", ".class", ".jar", ".war",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt",
    ".scala", ".sql", ".sh", ".bash", ".zsh", ".ps1", ".bat",
    ".md", ".rst", ".txt", ".json", ".xml", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".env", ".gitignore",
    ".html", ".css", ".scss", ".less",
    ".vue", ".svelte", ".astro",
    ".pyi", ".pxd", ".pxi",
}


class ProjectIndex:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.files: list[dict[str, Any]] = []
        self.last_indexed: float = 0.0

    def index(self, force: bool = False) -> dict:
        if not force and self.last_indexed > time.time() - 5:
            return self.get_summary()
        self.files.clear()
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, self.root_dir).replace("\\", "/")
                entry = {
                    "path": rel,
                    "extension": ext,
                    "size": os.path.getsize(fpath),
                    "is_text": ext in TEXT_EXTENSIONS,
                }
                if rel.endswith("__init__.py"):
                    entry["type"] = "package"
                elif ext in (".py", ".js", ".ts", ".java", ".go", ".rs"):
                    entry["type"] = "source"
                elif ext in (".md", ".rst", ".txt"):
                    entry["type"] = "doc"
                elif ext in (".json", ".xml", ".yaml", ".yml", ".toml"):
                    entry["type"] = "config"
                else:
                    entry["type"] = "other"
                self.files.append(entry)
        self.files.sort(key=lambda f: f["path"])
        self.last_indexed = time.time()
        info(f"Indexed {len(self.files)} files in {self.root_dir}")
        return self.get_summary()

    def get_summary(self) -> dict:
        by_type: dict[str, int] = {}
        by_ext: dict[str, int] = {}
        for f in self.files:
            by_type[f["type"]] = by_type.get(f["type"], 0) + 1
            by_ext[f["extension"]] = by_ext.get(f["extension"], 0) + 1
        return {
            "root": self.root_dir,
            "total_files": len(self.files),
            "by_type": by_type,
            "by_extension": by_ext,
        }

    def search_files(self, query: str, file_type: str | None = None) -> list[dict]:
        results = []
        query_lower = query.lower()
        for f in self.files:
            if file_type and f["type"] != file_type:
                continue
            if query_lower in f["path"].lower():
                results.append(f)
        return results[:50]

    def get_source_files(self) -> list[str]:
        return [f["path"] for f in self.files if f["type"] == "source"]

    def get_structure(self, max_depth: int = 3) -> dict:
        root = {"name": os.path.basename(self.root_dir), "type": "directory", "children": {}}
        for f in self.files:
            parts = f["path"].split("/")
            if len(parts) > max_depth:
                continue
            current = root["children"]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = {"name": part, "type": "file", "ext": f["extension"]}
                else:
                    if part not in current:
                        current[part] = {"name": part, "type": "directory", "children": {}}
                    current = current[part]["children"]
        return root


_index: ProjectIndex | None = None


def get_project_index(root_dir: str | None = None) -> ProjectIndex:
    global _index
    if root_dir:
        _index = ProjectIndex(root_dir)
    elif _index is None:
        _index = ProjectIndex(os.getcwd())
    return _index
