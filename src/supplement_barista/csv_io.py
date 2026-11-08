"""Portable CSV import/export for supplement catalogs and profile schedules."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from supplement_barista.core import SupplementStore


def export_schedule(store: SupplementStore, profile_id: int, destination: str | Path) -> int:
    """Export one profile schedule; does not overwrite an existing file."""
    target = Path(destination)
    if target.exists():
        raise FileExistsError(f"File already exists: {target}")
    rows = store.schedule(profile_id)
    with target.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["time", "supplement", "form", "quantity", "unit"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in writer.fieldnames})
    return len(rows)


def import_schedule(store: SupplementStore, profile_id: int, source: str | Path) -> int:
    """Validate the entire CSV before writing; import new supplements as needed.

    Existing schedule rows are retained. Reimporting the same file adds doses again.
    """
    with Path(source).open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"time", "supplement", "form", "quantity", "unit"}
        if reader.fieldnames is None or set(reader.fieldnames) != required:
            raise ValueError("CSV must have exactly: time, supplement, form, quantity, unit")
        entries = list(reader)
    if not store.connection.execute(
        "SELECT 1 FROM profiles WHERE id = ?", (profile_id,)
    ).fetchone():
        raise ValueError("Profile not found")
    validated = []
    for number, row in enumerate(entries, start=2):
        if any(value is None for value in row.values()):
            raise ValueError(f"Invalid CSV row {number}")
        name = row["supplement"].strip()
        form = row["form"].strip()
        unit = row["unit"].strip()
        time = row["time"].strip()
        if not name or not form or not unit:
            raise ValueError(f"Missing required value on row {number}")
        try:
            quantity = float(row["quantity"])
        except ValueError as exc:
            raise ValueError(f"Invalid quantity on row {number}") from exc
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError(f"Invalid quantity on row {number}")
        from datetime import time as clock_time

        try:
            parsed = clock_time.fromisoformat(time)
        except ValueError as exc:
            raise ValueError(f"Invalid time on row {number}") from exc
        if parsed.strftime("%H:%M") != time or parsed.minute % 30:
            raise ValueError(f"Invalid 30-minute time on row {number}")
        validated.append((time, name, form, quantity, unit))

    # Use a savepoint so both catalog and dose writes roll back on any failure.
    connection = store.connection
    connection.execute("SAVEPOINT csv_import")
    try:
        for time, name, form, quantity, unit in validated:
            existing = connection.execute(
                "SELECT id, form FROM supplements WHERE name = ?", (name,)
            ).fetchone()
            if existing:
                if existing["form"] != form:
                    raise ValueError(f"Conflicting form for supplement: {name}")
                supplement_id = existing["id"]
            else:
                supplement_id = connection.execute(
                    "INSERT INTO supplements(name, form) VALUES (?, ?)", (name, form)
                ).lastrowid
            connection.execute(
                "INSERT INTO doses(profile_id, supplement_id, time, quantity, unit) "
                "VALUES (?, ?, ?, ?, ?)",
                (profile_id, supplement_id, time, quantity, unit),
            )
        connection.execute("RELEASE SAVEPOINT csv_import")
    except Exception:
        connection.execute("ROLLBACK TO SAVEPOINT csv_import")
        connection.execute("RELEASE SAVEPOINT csv_import")
        raise
    return len(validated)
