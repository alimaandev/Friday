import json
from dataclasses import dataclass, field, asdict
from typing import Any

def _format_tool_list(defs: list[dict]) -> str:
    lines = []
    for d in defs:
        fn = d.get("function", {})
        name = fn.get("name", "?")
        desc = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        args_str = ", ".join(params.keys()) if params else "(no args)"
        lines.append(f"  - {name}({args_str}): {desc}")
    return "\n".join(lines)


PLANNER_SYSTEM_PROMPT = '''You are a planning agent for a computer assistant. Decompose the user goal into concrete executable tasks.

AVAILABLE TOOLS:
{tools}

RULES:
1. Each task is ONE tool call. If the user asks multiple things, create MULTIPLE tasks.
2. Tasks must be ordered by dependency (prerequisites first).
3. Include the exact arguments needed when you know them.
4. Max 10 tasks per plan.

Example 1: "open notepad and write hello world to a file"
[
  {{"id": "task_1", "description": "Write hello world to a file", "tool": "write_file", "args": {{"path": "C:/hello.txt", "content": "Hello World!"}}, "dependencies": []}},
  {{"id": "task_2", "description": "Open the file in Notepad", "tool": "run_command", "args": {{"command": "notepad C:/hello.txt"}}, "dependencies": ["task_1"]}}
]

Example 2: "what year is it?"
[
  {{"id": "task_1", "description": "Get current datetime", "tool": "get_current_datetime", "args": {{}}, "dependencies": []}}
]

Example 3: "hello how are you"
[
  {{"id": "task_1", "description": "Respond to greeting", "tool": "none", "args": {{}}, "dependencies": []}}
]

Respond with ONLY the JSON array, no other text.'''



@dataclass
class Task:
    id: str
    description: str
    tool: str | None = None
    args: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None
    error: str | None = None
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_tasks(text: str) -> list[Task]:
    import re
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return [Task(id="task_1", description=text.strip()[:200], tool="none")]
    try:
        data = json.loads(match.group())
        tasks = []
        for item in data:
            tasks.append(Task(
                id=item.get("id", f"task_{len(tasks)+1}"),
                description=item.get("description", ""),
                tool=item.get("tool"),
                args=item.get("args", {}),
                dependencies=item.get("dependencies", []),
            ))
        return tasks if tasks else [Task(id="task_1", description=text.strip()[:200], tool="none")]
    except json.JSONDecodeError:
        return [Task(id="task_1", description=text.strip()[:200], tool="none")]


class Planner:
    def __init__(self, llm_provider, tool_definitions: list[dict] | None = None):
        self._llm = llm_provider
        self._tool_defs = tool_definitions or []

    def create_plan(self, goal: str, context: list[dict] | None = None) -> list[Task]:
        tool_list = _format_tool_list(self._tool_defs) if self._tool_defs else "(no tools available)"
        prompt = PLANNER_SYSTEM_PROMPT.format(tools=tool_list)

        messages = [{"role": "system", "content": prompt}]
        if context:
            last = context[-3:]
            messages.append({
                "role": "user",
                "content": f"Conversation context:\n{json.dumps(last, indent=2)}\n\nNew goal: {goal}",
            })
        else:
            messages.append({"role": "user", "content": goal})

        content = ""
        tool_calls = None
        for event in self._llm(messages, tools=self._tool_defs or None):
            if event["type"] == "tokens":
                content += event["content"]
            elif event["type"] == "done":
                content = event["content"]
                tool_calls = event.get("tool_calls")

        if tool_calls:
            return _toolcalls_to_tasks(tool_calls)
        return _parse_tasks(content)


def _toolcalls_to_tasks(tool_calls: list) -> list[Task]:
    tasks = []
    for i, tc in enumerate(tool_calls):
        fn = tc.get("function", tc.function if hasattr(tc, "function") else {})
        name = fn.get("name", fn.name if hasattr(fn, "name") else "?")
        args = fn.get("arguments", fn.arguments if hasattr(fn, "arguments") else {})
        tasks.append(Task(
            id=f"task_{i+1}",
            description=f"Execute {name}",
            tool=name,
            args=args if isinstance(args, dict) else {},
        ))
    return tasks if tasks else [Task(id="task_1", description="No tasks generated", tool="none")]

    def revise_plan(self, tasks: list[Task], failed: Task, feedback: str) -> list[Task]:
        context = {
            "original_tasks": [t.to_dict() for t in tasks],
            "failed_task": failed.to_dict(),
            "feedback": feedback,
        }
        prompt = f"The following task failed. Revise the remaining plan.\n\n{json.dumps(context, indent=2)}"
        return self.create_plan(prompt)
