from config import get_system_prompt, MAX_ITERATIONS
from agent.llm import chat as llm_chat
from core.registry import get_tool_definitions, get_tool_map
from core.planner import Planner
from core.executor import Executor
from core.logger import info
from core.memory import get_memory_manager
from core.system1 import build_default_system1

_system1 = None


def _get_system1():
    global _system1
    if _system1 is None:
        _system1 = build_default_system1()
    return _system1


_TRANSIENT_ERRORS = ["timeout", "not found", "connection", "rate limit"]


class Agent:
    def __init__(self, language="english"):
        self.language = language
        self.messages = [{"role": "system", "content": get_system_prompt(language)}]
        self._tool_defs = get_tool_definitions()
        tool_map = get_tool_map()
        self._planner = Planner(llm_chat, tool_definitions=self._tool_defs)
        self._executor = Executor(llm_chat, tool_map)
        self._output_dir: str | None = None

    @property
    def output_dir(self) -> str | None:
        return self._output_dir

    def set_output_dir(self, path: str | None):
        self._output_dir = path
        self._executor.output_dir = path

    def set_language(self, lang):
        self.language = lang
        self.clear()

    def clear(self):
        self.messages = [{"role": "system", "content": get_system_prompt(self.language)}]

    def run(self, user_input: str):
        self._executor.output_dir = self._output_dir

        memory = get_memory_manager()
        context = memory.inject_context(user_input)
        if context:
            enhanced = get_system_prompt(self.language) + "\n\n" + context
            self.messages.append({"role": "system", "content": enhanced})
        self.messages.append({"role": "user", "content": user_input})

        fast = _get_system1().route(user_input)
        if fast:
            yield {"type": "fast", "reflex": fast["reflex"], "content": fast["content"]}
            yield {"type": "done", "content": fast["content"], "final": True}
            return

        plan = self._planner.create_plan(user_input, context=self.messages)
        info(f"Plan created: {len(plan)} tasks", tasks=[t.description for t in plan])

        yield {"type": "plan", "tasks": [t.to_dict() for t in plan]}

        for task in plan:
            yield {"type": "task_start", "task": task.to_dict()}
            info(f"Executing task: {task.id} - {task.description}")

            for event in self._executor.execute_task(
                task, self.messages, self._tool_defs, MAX_ITERATIONS
            ):
                yield event

            if task.status == "failed" and task.retries < task.max_retries:
                err = (task.error or "").lower()
                if any(x in err for x in _TRANSIENT_ERRORS):
                    info(f"Retrying task: {task.id} (attempt {task.retries}/{task.max_retries})")
                    for event in self._executor.retry_task(task, self.messages, self._tool_defs):
                        yield event

            yield {"type": "task_done", "task": task.to_dict()}

        last = self.messages[-1] if self.messages else {}
        final = last.get("content", "") if last.get("role") == "assistant" else ""

        if final:
            memory.store_conversation_memory(user_input, final)

        yield {"type": "done", "content": final or "Done.", "final": True}
