import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from core.logger import info, warn


@dataclass
class PermissionRule:
    tool: str = ""
    command_prefix: str = ""
    allow: bool = True
    reason: str = ""


class Sandbox:
    def __init__(self, allowed_dirs: list[str] | None = None):
        self.allowed_dirs = [os.path.abspath(d) for d in (allowed_dirs or [])]

    def check_path(self, path: str) -> dict:
        if not self.allowed_dirs:
            return {"allowed": True}
        abs_path = os.path.abspath(path)
        for d in self.allowed_dirs:
            if abs_path.startswith(d):
                return {"allowed": True}
        return {
            "allowed": False,
            "reason": f"Path '{path}' is outside allowed directories: {self.allowed_dirs}",
        }


class RateLimiter:
    def __init__(self, max_calls: int = 30, window_sec: float = 60.0):
        self.max_calls = max_calls
        self.window_sec = window_sec
        self._calls: list[float] = []
        self._lock = threading.Lock()

    def check(self) -> dict:
        now = time.time()
        with self._lock:
            self._calls = [t for t in self._calls if now - t < self.window_sec]
            if len(self._calls) >= self.max_calls:
                oldest = self._calls[0] if self._calls else now
                wait = max(0, self.window_sec - (now - oldest))
                return {"allowed": False, "retry_after": round(wait, 1)}
            self._calls.append(now)
            return {"allowed": True, "calls_in_window": len(self._calls), "limit": self.max_calls}


class PermissionManager:
    def __init__(self):
        self._rules: list[PermissionRule] = []
        self._denied_tools: set[str] = set()
        self._allowed_tools: set[str] = set()
        self._command_blacklist: list[str] = [
            "rm -rf /", "rm -rf /*", ":(){ :|:& };:", "mkfs",
            "dd if=", "> /dev/sda", "chmod 777 /",
            "sudo rm", "wget http://", "curl http://",
        ]
        self._interactive_mode = True

    def set_interactive(self, enabled: bool):
        self._interactive_mode = enabled

    def allow_tool(self, name: str):
        self._allowed_tools.add(name)
        self._denied_tools.discard(name)

    def deny_tool(self, name: str):
        self._denied_tools.add(name)
        self._allowed_tools.discard(name)

    def check_tool(self, name: str, args: dict | None = None) -> dict:
        if name in self._denied_tools:
            return {"allowed": False, "reason": f"Tool '{name}' is denied"}
        if self._allowed_tools and name not in self._allowed_tools:
            return {"allowed": False, "reason": f"Tool '{name}' is not in the allowed list"}

        if name == "run_command" and args and "command" in args:
            return self._check_command(args["command"])

        return {"allowed": True}

    def _check_command(self, command: str) -> dict:
        cmd_lower = command.lower().strip()
        for blacklisted in self._command_blacklist:
            if blacklisted in cmd_lower:
                return {"allowed": False, "reason": f"Command contains blacklisted pattern: '{blacklisted}'"}
        if self._interactive_mode and any(cmd_lower.startswith(prefix) for prefix in ["rm ", "del ", "shutdown", "format"]):
            return {"allowed": True, "requires_confirmation": True}
        return {"allowed": True}

    def add_rule(self, rule: PermissionRule):
        self._rules.append(rule)

    def get_rules(self) -> list[dict]:
        return [
            {"tool": r.tool, "command_prefix": r.command_prefix, "allow": r.allow, "reason": r.reason}
            for r in self._rules
        ]


_sandbox = Sandbox()
_rate_limiter = RateLimiter()
_permissions = PermissionManager()


def get_sandbox() -> Sandbox:
    return _sandbox


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


def get_permission_manager() -> PermissionManager:
    return _permissions
