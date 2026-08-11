import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr("core.registry.discover_plugins", lambda: None)
    monkeypatch.setattr("desktop.api_server._proactive", None)
    import tempfile

    from core.automations import AutomationEngine

    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    fresh_engine = AutomationEngine(file_path=tmp.name)
    monkeypatch.setattr("core.automations.get_automation_engine", lambda: fresh_engine)
    sys.modules.pop("desktop.api_server", None)
    import importlib

    import desktop.api_server as api

    importlib.reload(api)
    api._API_SECRET = "test-secret"
    api._FRONTEND_ORIGIN = "http://localhost:5173"
    return api.app


@pytest.fixture
def headers():
    return {"X-API-Key": "test-secret"}


class TestHealth:
    async def test_health_ok(self, app):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/health")
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "ok"

    async def test_health_returns_sessions(self, app):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/health")
            data = await resp.get_json()
        assert "sessions" in data


class TestChat:
    async def test_chat_requires_message(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/chat", json={}, headers=headers)
        assert resp.status_code == 422

    async def test_chat_empty_message_rejected(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/chat", json={"message": ""}, headers=headers)
        assert resp.status_code == 422

    async def test_chat_long_message_rejected(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/chat", json={"message": "x" * 10001}, headers=headers)
        assert resp.status_code == 422

    async def test_chat_returns_event_stream(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/chat", json={"message": "hello"}, headers=headers)
        assert resp.status_code == 200
        assert resp.mimetype == "text/event-stream"


class TestSessions:
    async def test_list_sessions_empty(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/sessions", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["sessions"] == []

    async def test_create_session(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/sessions", json={"language": "english"}, headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 201
        assert "session_id" in data
        assert data["language"] == "english"

    async def test_create_session_invalid_language(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/sessions", json={"language": "french"}, headers=headers)
        assert resp.status_code == 422

    async def test_delete_session(self, app, headers):
        async with app.test_client() as client:
            create = await client.post("/api/v1/sessions", json={"language": "english"}, headers=headers)
            sid = (await create.get_json())["session_id"]
            resp = await client.delete(f"/api/v1/sessions/{sid}", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "deleted"

    async def test_delete_nonexistent_session(self, app, headers):
        async with app.test_client() as client:
            resp = await client.delete("/api/v1/sessions/nonexistent", headers=headers)
        assert resp.status_code == 404


class TestMetrics:
    async def test_metrics_endpoint(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/metrics", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "llm_calls" in data


class TestSystemInfo:
    async def test_system_info(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/system-info", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "hostname" in data
        assert "os" in data


class TestOutputDir:
    async def test_get_default_output_dir(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/output-dir?session_id=default", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "output_dir" in data

    async def test_set_output_dir(self, app, headers):
        async with app.test_client() as client:
            resp = await client.put(
                "/api/v1/output-dir", json={"session_id": "default", "path": "/tmp/friday_output"}, headers=headers
            )
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "ok"

    async def test_set_output_dir_traversal_rejected(self, app, headers):
        async with app.test_client() as client:
            resp = await client.put(
                "/api/v1/output-dir", json={"session_id": "default", "path": "../etc/passwd"}, headers=headers
            )
        assert resp.status_code == 422


class TestMemory:
    async def test_memory_list(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/memory", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "vector_memories" in data

    async def test_memory_search_empty(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/memory/search", json={"query": ""}, headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["count"] == 0

    async def test_memory_search(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/memory/search", json={"query": "test"}, headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "results" in data

    async def test_memory_clear(self, app, headers):
        async with app.test_client() as client:
            resp = await client.delete("/api/v1/memory", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True


class TestKnowledgeGraph:
    async def test_knowledge_list(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/knowledge", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "entities" in data

    async def test_knowledge_store_requires_text(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/knowledge", json={}, headers=headers)
        assert resp.status_code == 422

    async def test_knowledge_store_and_query(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/knowledge", json={"text": "the beta orb and Sarah"}, headers=headers)
            data = await resp.get_json()
            assert resp.status_code == 200
            assert data["count"] >= 0

            resp2 = await client.post("/api/v1/knowledge/query", json={"term": "sarah"}, headers=headers)
            data2 = await resp2.get_json()
        assert resp2.status_code == 200
        assert any(r["name"].lower() == "sarah" for r in data2["results"])

    async def test_knowledge_continuity(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/knowledge/continuity", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "continuity" in data


class TestComputerControl:
    async def test_computer_status(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/computer/status", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "platform" in data
        assert "mouse_keyboard" in data

    async def test_computer_windows(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/computer/windows", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "windows" in data

    async def test_computer_summary(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/computer/summary", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "available" in data
        assert "windows" in data


class TestPluginMarketplace:
    async def test_list_plugins(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/plugins", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "plugins" in data
        assert len(data["plugins"]) > 0

    async def test_install_missing_plugin(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/plugins/install", headers=headers, json={"name": "__nope__"})
        assert resp.status_code == 404

    async def test_install_requires_name(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/plugins/install", headers=headers, json={})
        assert resp.status_code == 422


class TestCustomTools:
    async def test_list_custom_tools(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/tools/custom", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "tools" in data

    async def test_create_requires_description(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/tools/custom", headers=headers, json={})
        assert resp.status_code == 422


class TestRag:
    async def test_search_requires_query(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/rag/search", headers=headers, json={})
        assert resp.status_code == 422

    async def test_ingest_requires_text(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/rag/ingest", headers=headers, json={"title": "x"})
        assert resp.status_code == 422


class TestPrivacy:
    async def test_privacy_status(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/privacy", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "enabled" in data
        assert "local_provider" in data

    async def test_privacy_toggle(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/privacy", headers=headers, json={"enabled": True})
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["enabled"] is True


class TestAutomations:
    async def test_list_automations_empty(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/automations", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["automations"] == []

    async def test_create_automation(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post(
                "/api/v1/automations",
                json={
                    "name": "Daily Briefing",
                    "trigger_type": "cron",
                    "trigger_config": {"cron": "0 8 * * *"},
                    "action": "briefing",
                },
                headers=headers,
            )
            data = await resp.get_json()
        assert resp.status_code == 201
        assert data["name"] == "Daily Briefing"
        assert data["trigger_type"] == "cron"

    async def test_create_automation_invalid(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post(
                "/api/v1/automations",
                json={
                    "name": "",
                    "trigger_type": "invalid",
                    "action": "",
                },
                headers=headers,
            )
        assert resp.status_code == 422

    async def test_get_automation(self, app, headers):
        async with app.test_client() as client:
            create = await client.post(
                "/api/v1/automations",
                json={
                    "name": "Test",
                    "trigger_type": "event",
                    "trigger_config": {},
                    "action": "notification",
                },
                headers=headers,
            )
            aid = (await create.get_json())["id"]
            resp = await client.get(f"/api/v1/automations/{aid}", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["name"] == "Test"

    async def test_get_automation_not_found(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/automations/nonexistent", headers=headers)
        assert resp.status_code == 404

    async def test_update_automation(self, app, headers):
        async with app.test_client() as client:
            create = await client.post(
                "/api/v1/automations",
                json={
                    "name": "Original",
                    "trigger_type": "cron",
                    "trigger_config": {"cron": "0 9 * * *"},
                    "action": "notification",
                },
                headers=headers,
            )
            aid = (await create.get_json())["id"]
            resp = await client.put(f"/api/v1/automations/{aid}", json={"name": "Updated"}, headers=headers)
            data = await resp.get_json()
        assert data["name"] == "Updated"

    async def test_delete_automation(self, app, headers):
        async with app.test_client() as client:
            create = await client.post(
                "/api/v1/automations",
                json={
                    "name": "ToDelete",
                    "trigger_type": "event",
                    "trigger_config": {},
                    "action": "notification",
                },
                headers=headers,
            )
            aid = (await create.get_json())["id"]
            resp = await client.delete(f"/api/v1/automations/{aid}", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "deleted"

    async def test_toggle_automation(self, app, headers):
        async with app.test_client() as client:
            create = await client.post(
                "/api/v1/automations",
                json={
                    "name": "ToggleMe",
                    "trigger_type": "cron",
                    "trigger_config": {"cron": "* * * * *"},
                    "action": "notification",
                },
                headers=headers,
            )
            aid = (await create.get_json())["id"]
            resp = await client.post(f"/api/v1/automations/{aid}/toggle", headers=headers)
            data = await resp.get_json()
        assert data["enabled"] is False

    async def test_trigger_automation(self, app, headers):
        async with app.test_client() as client:
            create = await client.post(
                "/api/v1/automations",
                json={
                    "name": "TriggerMe",
                    "trigger_type": "event",
                    "trigger_config": {},
                    "action": "notification",
                    "action_params": {"message": "hello"},
                },
                headers=headers,
            )
            aid = (await create.get_json())["id"]
            resp = await client.post(f"/api/v1/automations/{aid}/trigger", headers=headers)
            data = await resp.get_json()
        assert data["type"] == "notification"


class TestAlerts:
    async def test_alerts_list(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/alerts", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert "alerts" in data


class TestVision:
    async def test_vision_analyze_no_image(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/vision/analyze", json={}, headers=headers)
        assert resp.status_code == 422

    async def test_vision_screen(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/vision/screen", headers=headers)
        assert resp.status_code == 200


class TestApprovals:
    async def test_list_approvals_empty(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/approvals", headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["approvals"] == []

    async def test_resolve_unknown_approval_404(self, app, headers):
        async with app.test_client() as client:
            resp = await client.post("/api/v1/approvals/nope", json={"allowed": True}, headers=headers)
        assert resp.status_code == 404

    async def test_resolve_approval(self, app, headers):
        from core.security import get_approval_registry

        request_id = get_approval_registry().request("delete_file", {"path": "x"})
        async with app.test_client() as client:
            resp = await client.post(f"/api/v1/approvals/{request_id}", json={"allowed": True}, headers=headers)
            data = await resp.get_json()
        assert resp.status_code == 200
        assert data["allowed"] is True
        assert get_approval_registry().wait(request_id, timeout=0.1) is True


class TestAuth:
    async def test_unauthorized_without_key(self, app):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/metrics")
        assert resp.status_code == 401

    async def test_authorized_with_correct_key(self, app, headers):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/metrics", headers=headers)
        assert resp.status_code == 200

    async def test_health_does_not_require_auth(self, app):
        async with app.test_client() as client:
            resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
