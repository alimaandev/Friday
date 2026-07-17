from core.logger import get_metrics, get_timeline, reset_metrics
from plugins.base import ToolPlugin


class GetMetricsPlugin(ToolPlugin):
    name = "get_metrics"
    description = "Get performance metrics: LLM calls, tokens used, tool usage, failures, retries, uptime."
    category = "system"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        return get_metrics()


class GetTimelinePlugin(ToolPlugin):
    name = "get_timeline"
    description = "Get the recent event timeline (last N events). Useful for debugging and understanding what happened."
    category = "system"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of recent events (default: 20)"},
            },
            "required": [],
        }

    def execute(self, limit: int = 20) -> dict:
        events = get_timeline(limit=limit)
        return {"events": events, "count": len(events)}


class ResetMetricsPlugin(ToolPlugin):
    name = "reset_metrics"
    description = "Reset all performance counters to zero."
    category = "system"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        reset_metrics()
        return {"success": True, "message": "Metrics reset"}
