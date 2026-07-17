import subprocess


def _find_command(cmds: list[str]) -> str | None:
    for cmd in cmds:
        parts = cmd.split()
        try:
            subprocess.run(parts + ["--version"], capture_output=True, text=True, timeout=5)
            return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def run_tests(path: str = ".", timeout: int = 60, verbose: bool = False) -> dict:
    try:
        import pytest
        pytest_cmd = "pytest"
    except ImportError:
        pytest_target = _find_command(["pytest", "python -m pytest", "python3 -m pytest"])
        if not pytest_target:
            return {"error": "pytest not found", "exit_code": -1}
        pytest_cmd = pytest_target

    cmd = [pytest_cmd, path] if pytest_cmd == "pytest" else pytest_cmd.split() + [path]
    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "stdout": result.stdout.strip()[:2000],
            "stderr": result.stderr.strip()[:1000],
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Tests timed out after {timeout}s", "exit_code": -1}
    except Exception as e:
        return {"error": str(e), "exit_code": -1}


def run_lint(path: str = ".") -> dict:
    try:
        import ruff  # noqa: F401
        cmd = ["python", "-m", "ruff", "check", path]
    except ImportError:
        return {"error": "ruff not found. Install with: pip install ruff", "exit_code": -1}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = [l for l in result.stdout.split("\n") if l.strip()][:30]
        return {
            "issues": lines,
            "count": len(lines),
            "exit_code": result.returncode,
            "clean": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Lint timed out", "exit_code": -1}
    except Exception as e:
        return {"error": str(e), "exit_code": -1}


def run_format(path: str = ".", check: bool = True) -> dict:
    try:
        import ruff  # noqa: F401
        cmd = ["python", "-m", "ruff", "format"]
        if check:
            cmd.append("--check")
        cmd.append(path)
    except ImportError:
        return {"error": "ruff not found", "exit_code": -1}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout.strip()[:1000],
            "stderr": result.stderr.strip()[:500],
            "exit_code": result.returncode,
            "would_format": result.returncode != 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Format check timed out", "exit_code": -1}
    except Exception as e:
        return {"error": str(e), "exit_code": -1}
