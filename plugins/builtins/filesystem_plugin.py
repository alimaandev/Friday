import os

from plugins.base import ToolPlugin


class ReadFilePlugin(ToolPlugin):
    name = "read_file"
    description = "Read the contents of a file"
    category = "filesystem"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"},
            },
            "required": ["path"],
        }

    def execute(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "error": None}
        except Exception as e:
            return {"content": None, "error": str(e)}


class WriteFilePlugin(ToolPlugin):
    name = "write_file"
    description = "Write content to a file (overwrites existing)"
    category = "filesystem"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        }

    def execute(self, path: str, content: str) -> dict:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ListDirPlugin(ToolPlugin):
    name = "list_dir"
    description = "List all entries in a directory"
    category = "filesystem"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current dir)"},
            },
            "required": [],
        }

    def execute(self, path: str = ".") -> dict:
        try:
            entries = os.listdir(path)
            return {"entries": entries, "error": None}
        except Exception as e:
            return {"entries": None, "error": str(e)}
