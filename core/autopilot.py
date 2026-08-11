"""Autopilot — autonomous, dependency-aware multi-task execution.

Orchestrates the Planner + Executor pair into a self-verifying loop with
workspace confinement. Every step is emitted both as its native executor
event and as an ``autopilot`` event so the UI can render a live "brain view".

Features:
- runtime scheduling that honors task ``dependencies`` (failures propagate
  to dependents as skips; cycles fail cleanly)
- confined workspace: path-based tools cannot escape the workspace root
- deterministic post-step verification (tool errors, written-file existence)
- optional tool allowlist for headless/scheduled runs
"""

import os
import re
from collections.abc import Generator
from typing import Any

from core.executor import Executor
from core.logger import info
from core.planner import Task

_WRITE_TOOLS = {"write_file", "create_file", "save_file"}
_PATH_ARG_KEYS = ("path", "filepath", "src", "destination", "directory", "cwd", "file")
_PATH_VALUE_RE = re.compile(r"(?:path|filepath|src|destination|directory|cwd|file)=([^,{}\[\]]+?)(?=,\s*\w+=|$)")

_BLOCKED_MARKERS = ("workspace", "blocked", "denied")


class Autopilot:
    """Runs a goal through plan -> scheduled steps -> verify, as a generator.

    Yields the executor's native events (``tokens``, ``tool_result``, ``done``)
    interleaved with ``autopilot`` events from the orchestration layer.
    """

    def __init__(
        self,
        planner,
        llm_provider,
        tool_map: dict[str, Any],
        tool_definitions: list[dict],
        workspace: str | None = None,
        verify: bool = True,
        tool_allowlist: list[str] | None = None,
        max_retries: int = 3,
        confirm_timeout: float = 120.0,
    ):
        self._planner = planner
        self.workspace_root = os.path.abspath(workspace) if workspace else None
        self.workspace_prefix = (self.workspace_root.rstrip("\\/") + os.sep) if self.workspace_root else None
        self.verify_enabled = verify
        self.tool_allowlist = list(tool_allowlist) if tool_allowlist else None
        self.max_retries = max_retries
        self._tool_defs = tool_definitions or []
        confined_map = {name: self._wrap(name, handler) for name, handler in tool_map.items()}
        self._executor = Executor(llm_provider, confined_map, confirm_timeout=confirm_timeout)

    # ─── Public API ────────────────────────────────────────────────

    def run(self, goal: str, context: list[dict] | None = None) -> Generator[dict, None, None]:
        self._executor.output_dir = self.workspace_root

        yield {"type": "autopilot", "event": "plan_started", "goal": goal}

        tasks = self._planner.create_plan(goal, context=context)
        yield {
            "type": "autopilot",
            "event": "plan",
            "goal": goal,
            "tasks": [t.to_dict() for t in tasks],
            "summary": f"Planned {len(tasks)} steps.",
        }

        stats = {"total": len(tasks), "completed": 0, "failed": 0, "skipped": 0}
        pending = list(tasks)
        finished: set[str] = set()
        failed: set[str] = set()
        messages = list(context or [])

        while pending:
            ready = [t for t in pending if all(dep in finished for dep in (t.dependencies or []))]
            if not ready:
                for t in pending:
                    if any(dep in failed for dep in (t.dependencies or [])):
                        t.status = "skipped"
                        stats["skipped"] += 1
                        yield {"type": "autopilot", "event": "step_skipped", "task": t.to_dict()}
                    else:
                        t.status = "failed"
                        t.error = "Unresolved dependencies (cycle) in plan"
                        stats["failed"] += 1
                pending.clear()
                break

            for task in ready:
                pending.remove(task)
                if any(dep in failed for dep in (task.dependencies or [])):
                    task.status = "skipped"
                    stats["skipped"] += 1
                    yield {"type": "autopilot", "event": "step_skipped", "task": task.to_dict()}
                    continue

                yield {"type": "autopilot", "event": "step_start", "task": task.to_dict()}
                outcomes: list[dict] = []

                for event in self._executor.execute_task(task, messages, self._tool_defs):
                    if event["type"] == "tool_result":
                        outcomes.extend(event["tools"])
                    yield event

                if task.status == "failed" and task.retries < task.max_retries:
                    info(f"Autopilot retrying task: {task.id} (attempt {task.retries}/{task.max_retries})")
                    for event in self._executor.retry_task(task, messages, self._tool_defs):
                        if event["type"] == "tool_result":
                            outcomes.extend(event["tools"])
                        yield event

                verification = self._verify_task(task, outcomes)
                if task.status != "failed" and not verification.get("verified"):
                    task.status = "failed"
                    task.error = (
                        f"Verification failed ({verification.get('mode')}): {str(verification.get('detail', ''))[:200]}"
                    )
                yield {
                    "type": "autopilot",
                    "event": "step_done",
                    "task": task.to_dict(),
                    "verification": verification,
                }

                if task.status == "failed":
                    failed.add(task.id)
                    stats["failed"] += 1
                else:
                    finished.add(task.id)
                    stats["completed"] += 1

                blocked_reason = self._blocked_reason(task, verification)
                if blocked_reason is not None:
                    yield {"type": "autopilot", "event": "aborted", "reason": blocked_reason, "goal": goal}
                    yield {"type": "done", "content": f"Autopilot stopped: {blocked_reason}", "final": True}
                    return

        summary = self._summarize(stats)
        yield {"type": "autopilot", "event": "done", "goal": goal, "stats": stats, "summary": summary}
        yield {"type": "done", "content": summary, "final": True}

    # ─── Helpers ───────────────────────────────────────────────────

    def _blocked_reason(self, task: Task, verification: dict) -> str | None:
        """Security-blocked steps are fatal: the run aborts instead of
        limping on after the sandbox fought the model."""
        if any(x in (task.error or "").lower() for x in _BLOCKED_MARKERS):
            return task.error
        if verification.get("mode") == "tool_error":
            detail = str(verification.get("detail", "")).lower()
            if any(x in detail for x in _BLOCKED_MARKERS):
                return str(verification.get("detail", ""))
        return None

    def _summarize(self, stats: dict) -> str:
        parts = [
            f"{stats['completed']} completed",
            f"{stats['failed']} failed",
            f"{stats['skipped']} skipped",
        ]
        return f"Autopilot finished: {', '.join(parts)}."

    # ─── Confinement ───────────────────────────────────────────────

    def _wrap(self, name: str, handler) -> callable:
        def wrapped(**kwargs) -> dict:
            if not self._is_tool_allowed(name):
                return {"error": f"Tool '{name}' blocked by autopilot allowlist"}
            if self.workspace_prefix:
                for key in _PATH_ARG_KEYS:
                    value = kwargs.get(key)
                    if not isinstance(value, str) or not value:
                        continue
                    expanded = os.path.abspath(os.path.expanduser(value))
                    if not (expanded == self.workspace_root or expanded.startswith(self.workspace_prefix)):
                        return {"error": f"Path '{value}' is outside the workspace ({self.workspace_root})"}
            return handler(**kwargs)

        return wrapped

    def _is_tool_allowed(self, name: str) -> bool:
        return self.tool_allowlist is None or name in self.tool_allowlist

    # ─── Verification ──────────────────────────────────────────────

    def _verify_task(self, task: Task, outcomes: list[dict]) -> dict:
        if not self.verify_enabled:
            return {"verified": True, "mode": "disabled"}
        for outcome in outcomes:
            if re.search(r'"error"', outcome.get("result", "")):
                return {"verified": False, "mode": "tool_error", "detail": outcome.get("result", "")[:300]}
        for outcome in outcomes:
            if outcome.get("name") in _WRITE_TOOLS:
                path = self._extract_path(outcome.get("args", ""))
                if path is not None and not os.path.exists(path):
                    return {"verified": False, "mode": "missing_file", "detail": path}
        return {"verified": True, "mode": "ok"}

    def _extract_path(self, args_str: str) -> str | None:
        match = _PATH_VALUE_RE.search(args_str)
        if not match:
            return None
        raw = match.group(1).strip().strip('"').strip("'")
        try:
            return os.path.abspath(raw)
        except Exception:
            return None
