import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "health",
    str(Path(__file__).parent.parent / "app" / "api" / "health.py"),
)
health_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_mod)


def test_health():
    assert health_mod.health() == {"status": "ok"}
