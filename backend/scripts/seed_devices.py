"""Seed the devices table with Chrome DevTools device-toolbar presets.

Data source: the devices shown by default in Chrome DevTools' device toolbar
(``show-by-default: true`` in Chromium's ``EmulatedDevices.ts``). Each row stores
the emulation properties (viewport, DPR, user agent, capabilities) in the
free-form ``meta`` column.

Idempotent: devices are matched by ``name``; existing rows are left untouched.

Run from ``backend/`` with the virtualenv active::

    python -m scripts.seed_devices
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Device

DATA_FILE = Path(__file__).parent / "chrome_devices.json"


def load_seed_data() -> list[dict]:
    """Read the Chrome device presets bundled next to this script."""
    with DATA_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def seed_devices() -> tuple[int, int]:
    """Insert any missing preset devices. Returns (created, skipped)."""
    devices = load_seed_data()
    created = 0
    skipped = 0

    with SessionLocal() as db:
        existing_names = set(db.execute(select(Device.name)).scalars().all())

        for entry in devices:
            name = entry["name"]
            if name in existing_names:
                skipped += 1
                continue

            db.add(
                Device(
                    name=name,
                    meta=entry.get("meta", {}),
                    status=entry.get("status", True),
                )
            )
            existing_names.add(name)
            created += 1

        db.commit()

    return created, skipped


def main() -> None:
    created, skipped = seed_devices()
    print(f"Seed complete: {created} created, {skipped} skipped (already present).")


if __name__ == "__main__":
    main()
