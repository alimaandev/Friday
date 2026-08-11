from main import _launch_ui


def test_launch_ui_builds_commands(monkeypatch):
    """--ui should spawn the API server and frontend dev server, then open the browser."""
    spawned: list[list[str]] = []
    opened: list[str] = []

    class FakeProc:
        def __init__(self, cmd):
            self._cmd = cmd
            self._polls = 0

        def poll(self):
            self._polls += 1
            return None if self._polls < 3 else 0

        def terminate(self):
            self._terminated = True

    def fake_popen(cmd, **kwargs):
        spawned.append(cmd)
        return FakeProc(cmd)

    def fake_sleep(_secs):
        pass

    def fake_open(url):
        opened.append(url)

    monkeypatch.setattr("main.subprocess.Popen", fake_popen)
    monkeypatch.setattr("main.time.sleep", fake_sleep)
    monkeypatch.setattr("main.webbrowser.open", fake_open)

    _launch_ui()

    assert len(spawned) == 2
    assert "api_server.py" in " ".join(spawned[0])
    assert any("dev" in str(c) for c in spawned[1])
    assert opened == ["http://localhost:5173"]
