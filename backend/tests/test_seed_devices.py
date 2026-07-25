"""Tests for scripts/seed_devices.py — Chrome DevTools preset seeding.

Domain rules asserted here are derived from the script and its bundled data file
(`scripts/chrome_devices.json`), which mirrors Chromium's `EmulatedDevices.ts`
device-toolbar presets:

* Seeding is idempotent and matched by ``name`` — existing rows are never touched.
* ``meta`` is free-form; a preset without ``meta`` seeds an empty dict.
* ``status`` defaults to ``True`` when the preset omits it.
"""

import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models import Device
from scripts import seed_devices as seed_module
from scripts.seed_devices import DATA_FILE, load_seed_data, main, seed_devices

TURKISH_NAME = "Türk Telefonu Ğğ İıŞş"
EMOJI_NAME = "Nest Hub 📱"


def _write_seed_file(tmp_path: Path, payload: object) -> Path:
    """Write `payload` as the script's data file and return its path."""
    path = tmp_path / "chrome_devices.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _stored_devices(session_factory) -> list[Device]:
    """Read every persisted device through a fresh session."""
    with session_factory() as session:
        return list(session.execute(select(Device)).scalars().all())


@pytest.mark.unit
class TestLoadSeedData:
    def test_bundled_file_loads_as_list_of_dicts(self) -> None:
        # Act
        data = load_seed_data()

        # Assert
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(entry, dict) for entry in data)

    def test_bundled_presets_have_required_shape(self) -> None:
        # Act
        data = load_seed_data()

        # Assert
        for entry in data:
            assert isinstance(entry["name"], str)
            assert entry["name"] != ""
            assert isinstance(entry.get("status", True), bool)
            assert isinstance(entry.get("meta", {}), dict)

    def test_bundled_preset_names_are_unique(self) -> None:
        # Act
        names = [entry["name"] for entry in load_seed_data()]

        # Assert — duplicates would silently seed only the first occurrence
        assert len(names) == len(set(names))

    def test_bundled_viewports_are_positive_integers(self) -> None:
        # Act
        data = load_seed_data()

        # Assert
        viewports = [
            entry["meta"]["viewport"]
            for entry in data
            if "viewport" in entry.get("meta", {})
        ]
        assert viewports, "expected at least one preset to declare a viewport"
        for viewport in viewports:
            assert isinstance(viewport["width"], int)
            assert isinstance(viewport["height"], int)
            assert viewport["width"] > 0
            assert viewport["height"] > 0

    def test_data_file_points_next_to_the_script(self) -> None:
        # Assert
        assert DATA_FILE.name == "chrome_devices.json"
        assert DATA_FILE.exists()

    def test_reads_unicode_names_verbatim(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [{"name": TURKISH_NAME, "meta": {}}])

        # Act
        with patch.object(seed_module, "DATA_FILE", path):
            data = load_seed_data()

        # Assert
        assert data[0]["name"] == TURKISH_NAME

    def test_empty_list_is_valid(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [])

        # Act
        with patch.object(seed_module, "DATA_FILE", path):
            data = load_seed_data()

        # Assert
        assert data == []

    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        # Arrange
        missing = tmp_path / "absent.json"

        # Act / Assert
        with patch.object(seed_module, "DATA_FILE", missing):
            with pytest.raises(FileNotFoundError):
                load_seed_data()

    def test_malformed_json_raises_decode_error(self, tmp_path: Path) -> None:
        # Arrange
        path = tmp_path / "chrome_devices.json"
        path.write_text("{not json", encoding="utf-8")

        # Act / Assert
        with patch.object(seed_module, "DATA_FILE", path):
            with pytest.raises(json.JSONDecodeError):
                load_seed_data()


@pytest.mark.integration
class TestSeedDevices:
    def test_seeds_every_bundled_preset_on_empty_database(
        self, session_factory
    ) -> None:
        # Arrange
        expected = len(load_seed_data())

        # Act
        with patch.object(seed_module, "SessionLocal", session_factory):
            created, skipped = seed_devices()

        # Assert
        assert created == expected
        assert skipped == 0
        assert len(_stored_devices(session_factory)) == expected

    def test_second_run_is_idempotent(self, session_factory) -> None:
        # Arrange
        expected = len(load_seed_data())

        # Act
        with patch.object(seed_module, "SessionLocal", session_factory):
            seed_devices()
            created, skipped = seed_devices()

        # Assert
        assert created == 0
        assert skipped == expected
        assert len(_stored_devices(session_factory)) == expected

    def test_existing_row_is_left_untouched(self, session_factory) -> None:
        # Arrange — a device whose name collides with a bundled preset
        preset_name = load_seed_data()[0]["name"]
        with session_factory() as session:
            session.add(
                Device(name=preset_name, meta={"hand": "edited"}, status=False)
            )
            session.commit()

        # Act
        with patch.object(seed_module, "SessionLocal", session_factory):
            created, skipped = seed_devices()

        # Assert — the pre-existing row keeps its own meta and status
        assert skipped == 1
        assert created == len(load_seed_data()) - 1
        stored = {d.name: d for d in _stored_devices(session_factory)}
        assert stored[preset_name].meta == {"hand": "edited"}
        assert stored[preset_name].status is False

    @pytest.mark.parametrize(
        ("entry", "expected_meta", "expected_status"),
        [
            ({"name": "No Meta"}, {}, True),
            ({"name": "Empty Meta", "meta": {}}, {}, True),
            ({"name": "Explicit Off", "status": False}, {}, False),
            (
                {"name": "Full", "meta": {"type": "phone"}, "status": True},
                {"type": "phone"},
                True,
            ),
            ({"name": TURKISH_NAME, "meta": {"platform": "Android"}}, {"platform": "Android"}, True),
            ({"name": EMOJI_NAME}, {}, True),
        ],
    )
    def test_entry_defaults(
        self,
        session_factory,
        tmp_path: Path,
        entry: dict,
        expected_meta: dict,
        expected_status: bool,
    ) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [entry])

        # Act
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            created, skipped = seed_devices()

        # Assert
        assert (created, skipped) == (1, 0)
        stored = _stored_devices(session_factory)
        assert stored[0].name == entry["name"]
        assert stored[0].meta == expected_meta
        assert stored[0].status is expected_status

    def test_generates_a_uuid_and_timestamps_per_row(
        self, session_factory, tmp_path: Path
    ) -> None:
        # Arrange
        path = _write_seed_file(
            tmp_path, [{"name": "A"}, {"name": "B"}]
        )

        # Act
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            seed_devices()

        # Assert
        stored = _stored_devices(session_factory)
        ids = {d.id for d in stored}
        assert len(ids) == 2
        assert all(len(d.id) == 36 for d in stored)
        assert all(d.created_at.endswith("+00:00") for d in stored)
        assert all(d.updated_at >= d.created_at for d in stored)

    def test_duplicate_names_within_one_file_seed_once(
        self, session_factory, tmp_path: Path
    ) -> None:
        # Arrange
        path = _write_seed_file(
            tmp_path,
            [
                {"name": "Twin", "meta": {"first": True}},
                {"name": "Twin", "meta": {"second": True}},
            ],
        )

        # Act
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            created, skipped = seed_devices()

        # Assert — the in-loop `existing_names.add` guards intra-file duplicates
        assert (created, skipped) == (1, 1)
        stored = _stored_devices(session_factory)
        assert len(stored) == 1
        assert stored[0].meta == {"first": True}

    def test_empty_seed_file_creates_nothing(
        self, session_factory, tmp_path: Path
    ) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [])

        # Act
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            created, skipped = seed_devices()

        # Assert
        assert (created, skipped) == (0, 0)
        assert _stored_devices(session_factory) == []

    def test_entry_without_name_raises_key_error(
        self, session_factory, tmp_path: Path
    ) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [{"meta": {"type": "phone"}}])

        # Act / Assert
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            with pytest.raises(KeyError, match="name"):
                seed_devices()

    def test_rows_survive_the_seeding_session(
        self, session_factory, tmp_path: Path
    ) -> None:
        # Arrange
        path = _write_seed_file(tmp_path, [{"name": "Persisted"}])

        # Act — the script commits inside its own `with SessionLocal()` block
        with patch.object(seed_module, "DATA_FILE", path), patch.object(
            seed_module, "SessionLocal", session_factory
        ):
            seed_devices()

        # Assert — a brand new session still sees the row
        with session_factory() as session:
            names = session.execute(select(Device.name)).scalars().all()
        assert list(names) == ["Persisted"]


@pytest.mark.unit
class TestMain:
    def test_prints_created_and_skipped_counts(self, capsys) -> None:
        # Arrange
        with patch.object(seed_module, "seed_devices", return_value=(7, 3)):
            # Act
            main()

        # Assert
        out = capsys.readouterr().out
        assert "7 created" in out
        assert "3 skipped" in out

    @pytest.mark.filterwarnings(
        "ignore:.*found in sys.modules after import of package.*:RuntimeWarning"
    )
    def test_running_the_module_as_a_script_seeds(
        self, session_factory, capsys
    ) -> None:
        # Arrange — patch the source `SessionLocal` so the fresh module
        # namespace created by runpy imports the in-memory factory
        expected = len(load_seed_data())

        # Act — exercises the `if __name__ == "__main__"` entry point
        with patch("app.database.SessionLocal", session_factory):
            runpy.run_module("scripts.seed_devices", run_name="__main__")

        # Assert
        assert f"{expected} created" in capsys.readouterr().out
        assert len(_stored_devices(session_factory)) == expected

    def test_propagates_seeding_errors(self) -> None:
        # Arrange
        with patch.object(
            seed_module, "seed_devices", side_effect=RuntimeError("db gone")
        ):
            # Act / Assert
            with pytest.raises(RuntimeError, match=r"db gone"):
                main()
