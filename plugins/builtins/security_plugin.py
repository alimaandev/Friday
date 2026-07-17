from core.security import get_sandbox, get_permission_manager
from plugins.base import ToolPlugin


class SandboxCheckPlugin(ToolPlugin):
    name = "sandbox_check"
    description = "Check if a file path is within the allowed workspace directories."
    category = "security"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to check"},
            },
            "required": ["path"],
        }

    def execute(self, path: str) -> dict:
        return get_sandbox().check_path(path)


class PermissionListPlugin(ToolPlugin):
    name = "permission_list"
    description = "List all security permission rules currently active."
    category = "security"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        rules = get_permission_manager().get_rules()
        return {"rules": rules, "count": len(rules)}


class PermissionDenyPlugin(ToolPlugin):
    name = "permission_deny"
    description = "Deny a specific tool from being used."
    category = "security"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool name to deny"},
            },
            "required": ["tool"],
        }

    def execute(self, tool: str) -> dict:
        get_permission_manager().deny_tool(tool)
        return {"success": True, "tool": tool, "status": "denied"}


class PermissionAllowPlugin(ToolPlugin):
    name = "permission_allow"
    description = "Allow a previously denied tool."
    category = "security"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool name to allow"},
            },
            "required": ["tool"],
        }

    def execute(self, tool: str) -> dict:
        get_permission_manager().allow_tool(tool)
        return {"success": True, "tool": tool, "status": "allowed"}
