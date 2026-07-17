import json, os
import time
from typing import Any, Generator

from core.planner import Task
from core.logger import info, warn, error, Timer


class Executor:
    def __init__(self, llm_provider, tool_map: dict[str, Any]):
        self._llm = llm_provider
        self._tool_map = tool_map
        self.output_dir: str | None = None

    def execute_task(
        self,
        task: Task,
        messages: list[dict],
        tool_definitions: list[dict],
        max_iterations: int = 10,
    ) -> Generator[dict, None, None]:
        task.status = "running"
        yield from self._react_loop(messages, tool_definitions, max_iterations, task)

    def _react_loop(
        self,
        messages: list[dict],
        tool_definitions: list[dict],
        max_iterations: int,
        task: Task,
    ) -> Generator[dict, None, None]:
        try:
            yield from self._react_loop_impl(messages, tool_definitions, max_iterations, task)
        except Exception as e:
            error(f"Unhandled exception in _react_loop: {e}", exc_info=True)
            task.status = "failed"
            task.error = str(e)
            yield {"type": "done", "content": f"Error: {e}"}

    def _react_loop_impl(
        self,
        messages: list[dict],
        tool_definitions: list[dict],
        max_iterations: int,
        task: Task,
    ) -> Generator[dict, None, None]:
        for iteration in range(max_iterations):
            collected = ""
            tool_calls = None

            for event in self._llm(messages, tools=tool_definitions):
                if event["type"] == "tokens":
                    collected += event["content"]
                    yield event
                elif event["type"] == "done":
                    collected = event["content"]
                    tool_calls = event["tool_calls"]

            if tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": collected,
                    "tool_calls": tool_calls,
                })

                tool_summary = []
                for tc in tool_calls:
                    func_name = tc["function"]["name"]
                    tc_id = tc.get("id", "")
                    raw_args = tc["function"]["arguments"]
                    try:
                        if isinstance(raw_args, str):
                            args = json.loads(raw_args)
                        else:
                            args = raw_args
                    except json.JSONDecodeError as e:
                        warn(f"Failed to parse args for {func_name}: {e}")
                        result = {"error": f"Invalid tool arguments: {e}"}
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc_id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })
                        continue

                    if self.output_dir and func_name == 'write_file' and 'path' in args:
                        p = args['path']
                        if not os.path.isabs(p):
                            args['path'] = os.path.join(self.output_dir, p)

                    handler = self._tool_map.get(func_name)
                    if handler:
                        try:
                            with Timer(f"tool:{func_name}"):
                                result = handler(**args)
                        except Exception as e:
                            result = {"error": str(e)}
                    else:
                        result = {"error": f"Unknown tool: {func_name}"}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

                    args_str = ", ".join(f"{k}={v}" for k, v in args.items())
                    tool_summary.append({
                        "name": func_name,
                        "args": args_str,
                        "result": json.dumps(result, ensure_ascii=False)[:300],
                    })

                    if result.get("error"):
                        task.error = str(result["error"])
                        task.retries += 1

                yield {"type": "tool_result", "tools": tool_summary}
            else:
                messages.append({"role": "assistant", "content": collected})
                task.status = "completed"
                task.result = collected
                yield {"type": "done", "content": collected}
                return

        task.status = "failed"
        task.error = "Max iterations reached"
        yield {"type": "done", "content": "Max iterations reached."}

    def retry_task(
        self,
        task: Task,
        messages: list[dict],
        tool_definitions: list[dict],
    ) -> Generator[dict, None, None]:
        if task.retries >= task.max_retries:
            yield {"type": "tool_result", "tools": [{
                "name": "retry",
                "args": f"task={task.id}",
                "result": f"Max retries ({task.max_retries}) exceeded",
            }]}
            return

        task.retries += 1
        task.status = "running"
        task.error = None

        messages.append({
            "role": "user",
            "content": f"The previous attempt failed: {task.error}\n\nPlease try again with a different approach.",
        })
        yield from self._react_loop(messages, tool_definitions, 10, task)
