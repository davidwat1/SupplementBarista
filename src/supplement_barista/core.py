"""SQLite-backed supplement catalog and daily schedule foundation."""

from __future__ import annotations

import math
import sqlite3
import os
import tempfile
from contextlib import closing
from pathlib import Path

from supplement_barista.units import normalize_unit


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
        self.connection.execute("PRAGMA user_version = 1")
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
                (name.strip(), normalize_unit(form), notes),
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
        if not math.isfinite(quantity) or quantity <= 0 or not unit.strip():
            raise ValueError("Positive quantity and unit are required")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO doses(profile_id, supplement_id, time, quantity, unit) "
                "VALUES (?, ?, ?, ?, ?)",
                (profile_id, supplement_id, time, quantity, normalize_unit(unit)),
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

    def profiles(self) -> list[dict]:
        return [dict(row) for row in self.connection.execute(
            "SELECT id, name FROM profiles ORDER BY name, id"
        )]

    def supplements(self) -> list[dict]:
        return [dict(row) for row in self.connection.execute(
            "SELECT id, name, form, notes FROM supplements ORDER BY name, id"
        )]

    def rename_profile(self, profile_id: int, name: str) -> None:
        if not name.strip():
            raise ValueError("Profile name is required")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE profiles SET name = ? WHERE id = ?", (name.strip(), profile_id)
            )
        if cursor.rowcount == 0:
            raise LookupError("Profile not found")

    def update_supplement(
        self, supplement_id: int, name: str, form: str, notes: str = ""
    ) -> None:
        if not name.strip() or not form.strip():
            raise ValueError("Supplement name and form are required")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE supplements SET name = ?, form = ?, notes = ? WHERE id = ?",
                (name.strip(), normalize_unit(form), notes, supplement_id),
            )
        if cursor.rowcount == 0:
            raise LookupError("Supplement not found")

    def update_dose(self, dose_id: int, time: str, quantity: float, unit: str) -> None:
        from datetime import time as clock_time

        try:
            parsed = clock_time.fromisoformat(time)
        except ValueError as exc:
            raise ValueError("Time must be HH:MM") from exc
        if parsed.strftime("%H:%M") != time or parsed.minute % 30 != 0:
            raise ValueError("Time must be HH:MM on a 30-minute increment")
        if not math.isfinite(quantity) or quantity <= 0 or not unit.strip():
            raise ValueError("Positive finite quantity and unit are required")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE doses SET time = ?, quantity = ?, unit = ? WHERE id = ?",
                (time, quantity, normalize_unit(unit), dose_id),
            )
        if cursor.rowcount == 0:
            raise LookupError("Dose not found")

    def delete_dose(self, dose_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM doses WHERE id = ?", (dose_id,))

    def delete_profile(self, profile_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM doses WHERE profile_id = ?", (profile_id,))
            self.connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))

    def delete_supplement(self, supplement_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM doses WHERE supplement_id = ?", (supplement_id,)
            )
            self.connection.execute(
                "DELETE FROM supplements WHERE id = ?", (supplement_id,)
            )

    def backup(self, destination: str | Path, *, overwrite: bool = False) -> None:
        target = Path(destination)
        if str(target) == ":memory:":
            raise ValueError("Backup destination must be a file")
        target = target.resolve()
        active_path = self.connection.execute("PRAGMA database_list").fetchone()[2]
        if active_path and target == Path(active_path).resolve():
            raise ValueError("Backup destination cannot be the active database")
        if target.exists() and not overwrite:
            raise FileExistsError("Refusing to overwrite existing backup")
        if target.exists() and not target.is_file():
            raise ValueError("Backup destination must be a file")
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".supplement-barista-", suffix=".sqlite3",
                dir=target.parent, delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)
            with closing(sqlite3.connect(str(temp_path))) as backup_connection:
                self.connection.backup(backup_connection)
                if backup_connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("New backup failed SQLite integrity check")
            if target.exists() and not overwrite:
                raise FileExistsError("Refusing to overwrite existing backup")
            os.replace(temp_path, target)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def restore(self, source: str | Path, recovery_backup: str | Path) -> None:
        """Restore a validated SQLite backup after saving the current database.

        Recovery backup must be a new file, never an existing database.
        """
        source_path = Path(source).resolve(strict=True)
        recovery_path = Path(recovery_backup).resolve()
        active_path = self.connection.execute("PRAGMA database_list").fetchone()[2]
        if active_path and source_path == Path(active_path).resolve():
            raise ValueError("Restore source cannot be the active database")
        if active_path and recovery_path == Path(active_path).resolve():
            raise ValueError("Recovery backup cannot overwrite the active database")
        if source_path == recovery_path:
            raise ValueError("Recovery backup must differ from restore source")
        if recovery_path.exists():
            raise FileExistsError("Recovery backup already exists")
        if source_path.stat().st_size == 0:
            raise ValueError("Restore source is empty")

        with sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True) as incoming:
            integrity = incoming.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise ValueError("Restore source failed SQLite integrity check")
            version = incoming.execute("PRAGMA user_version").fetchone()[0]
            if version != 1:
                raise ValueError(f"Unsupported database schema version: {version}")
            required = {"profiles", "supplements", "doses"}
            tables = {
                row[0] for row in incoming.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            if not required.issubset(tables):
                raise ValueError("Restore source is not a Supplement Barista database")
            for table in required:
                incoming.execute(f"SELECT * FROM {table} LIMIT 1").fetchall()
            # Save the current database before replacing it.
            self.backup(recovery_path)
            try:
                incoming.backup(self.connection)
                self.connection.execute("PRAGMA foreign_keys = ON")
                integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    raise ValueError("Restored database failed integrity check")
            except Exception:
                with sqlite3.connect(str(recovery_path)) as recovery:
                    recovery.backup(self.connection)
                raise

    def close(self) -> None:
        self.connection.close()
