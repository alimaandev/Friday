import platform
import os
from datetime import datetime, timezone

from plugins.base import ToolPlugin


class SystemInfoPlugin(ToolPlugin):
    name = "get_system_info"
    description = "Get system information: OS, CPU, memory, disk, Python version"
    category = "system"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "current_directory": os.getcwd(),
        }
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count(logical=True)
            info["cpu_usage_percent"] = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            info["memory_total_gb"] = round(mem.total / (1024 ** 3), 1)
            info["memory_available_gb"] = round(mem.available / (1024 ** 3), 1)
            disk = psutil.disk_usage(os.getcwd())
            info["disk_total_gb"] = round(disk.total / (1024 ** 3), 1)
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 1)
        except ImportError:
            info["note"] = "Install psutil for detailed system info (pip install psutil)"
        return info


class GetCurrentDateTimePlugin(ToolPlugin):
    name = "get_current_datetime"
    description = "Get the current date, time, and timezone. Use this for any question about current date, time, day, or year."
    category = "system"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict:
        now = datetime.now(timezone.utc).astimezone()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": str(now.tzinfo),
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "weekday": now.strftime("%A"),
        }
