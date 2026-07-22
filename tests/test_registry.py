import pytest
from core.registry import discover_plugins, get_tool_definitions, get_tool_map, run_health_checks


class TestRegistry:
    def test_discover_returns_tools(self):
        discover_plugins()
        defs = get_tool_definitions()
        tmap = get_tool_map()
        assert len(defs) > 0
        assert len(tmap) > 0

    def test_essential_tools_present(self):
        tmap = get_tool_map()
        for tool in ["run_command", "read_file", "write_file", "web_fetch",
                      "run_python", "remember", "recall",
                      "ask_user", "get_system_info"]:
            assert tool in tmap, f"{tool} missing"

    def test_health_checks_all_pass(self):
        checks = run_health_checks()
        for name, healthy in checks.items():
            assert healthy, f"Health check failed for {name}"

    def test_no_duplicate_tools(self):
        tmap = get_tool_map()
        assert len(tmap) == len(set(tmap.keys()))
