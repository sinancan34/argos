import json
from pathlib import Path

import pytest

from scenario import ScenarioError, Step, load_steps

pytestmark = pytest.mark.unit


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_steps_returns_steps_in_order(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        json.dumps(
            [
                {"action": "start_browser", "params": {}},
                {"action": "navigate", "params": {"url": "https://example.com"}},
            ]
        ),
    )

    assert load_steps(path) == [
        Step(action="start_browser", params={}),
        Step(action="navigate", params={"url": "https://example.com"}),
    ]


def test_load_steps_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(tmp_path / "missing.json")


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[]",
        '{"action": "navigate", "params": {}}',
        '[{"params": {}}]',
        '[{"action": "navigate"}]',
        '[{"action": "", "params": {}}]',
        '[{"action": "navigate", "params": "url"}]',
        '[{"action": "navigate", "params": {}, "intent": "extra field"}]',
    ],
)
def test_load_steps_rejects_invalid_content(tmp_path: Path, content: str) -> None:
    with pytest.raises(ScenarioError, match="invalid scenario"):
        load_steps(_write(tmp_path, content))


def test_load_steps_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "scenario.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(path)
