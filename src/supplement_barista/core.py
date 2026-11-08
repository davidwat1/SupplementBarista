"""SQLite-backed supplement catalog and daily schedule foundation."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class SupplementStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS supplements (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                form TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS doses (
                id INTEGER PRIMARY KEY,
                profile_id INTEGER NOT NULL REFERENCES profiles(id),
                supplement_id INTEGER NOT NULL REFERENCES supplements(id),
                time TEXT NOT NULL,
                quantity REAL NOT NULL CHECK(quantity > 0),
                unit TEXT NOT NULL,
                CHECK(length(time) = 5 AND time GLOB '[0-2][0-9]:[0-5][0-9]')
            );
        """)
        self.connection.commit()

    def add_profile(self, name: str) -> int:
        if not name.strip():
            raise ValueError("Profile name is required")
        with self.connection:
            cursor = self.connection.execute("INSERT INTO profiles(name) VALUES (?)", (name.strip(),))
        return int(cursor.lastrowid)

    def add_supplement(self, name: str, form: str, notes: str = "") -> int:
        if not name.strip() or not form.strip():
            raise ValueError("Supplement name and form are required")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO supplements(name, form, notes) VALUES (?, ?, ?)",
                (name.strip(), form.strip(), notes),
            )
        return int(cursor.lastrowid)

    def add_dose(
        self, profile_id: int, supplement_id: int, time: str, quantity: float, unit: str
    ) -> int:
        from datetime import time as clock_time

        try:
            parsed = clock_time.fromisoformat(time)
        except ValueError as exc:
            raise ValueError("Time must be HH:MM") from exc
        if parsed.strftime("%H:%M") != time or parsed.minute % 30 != 0:
            raise ValueError("Time must be HH:MM on a 30-minute increment")
        if quantity <= 0 or not unit.strip():
            raise ValueError("Positive quantity and unit are required")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO doses(profile_id, supplement_id, time, quantity, unit) "
                "VALUES (?, ?, ?, ?, ?)",
                (profile_id, supplement_id, time, quantity, unit.strip()),
            )
        return int(cursor.lastrowid)

    def schedule(self, profile_id: int) -> list[dict]:
        rows = self.connection.execute(
            "SELECT d.id, d.time, s.name AS supplement, s.form, d.quantity, d.unit "
            "FROM doses d JOIN supplements s ON s.id = d.supplement_id "
            "WHERE d.profile_id = ? ORDER BY d.time, s.name, d.id",
            (profile_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.connection.close()
