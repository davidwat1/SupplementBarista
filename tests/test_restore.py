import sqlite3

import pytest

from supplement_barista.core import SupplementStore


def test_restore_with_recovery_copy(tmp_path):
    live = SupplementStore(tmp_path / "live.sqlite3")
    live.add_profile("Before")
    incoming = SupplementStore(tmp_path / "incoming.sqlite3")
    incoming.add_profile("After")
    incoming.close()
    recovery_path = tmp_path / "recovery.sqlite3"
    live.restore(tmp_path / "incoming.sqlite3", recovery_path)
    assert [x["name"] for x in live.profiles()] == ["After"]
    recovery = SupplementStore(recovery_path)
    assert [x["name"] for x in recovery.profiles()] == ["Before"]
    recovery.close()
    live.close()


def test_invalid_restore_keeps_current_data(tmp_path):
    live = SupplementStore(tmp_path / "live.sqlite3")
    live.add_profile("Safe")
    invalid = tmp_path / "invalid.sqlite3"
    invalid.write_text("not a database", encoding="utf-8")
    with pytest.raises(sqlite3.DatabaseError):
        live.restore(invalid, tmp_path / "recovery.sqlite3")
    assert [x["name"] for x in live.profiles()] == ["Safe"]
    assert not (tmp_path / "recovery.sqlite3").exists()
    live.close()


def test_restore_rejects_active_database(tmp_path):
    path = tmp_path / "live.sqlite3"
    live = SupplementStore(path)
    with pytest.raises(ValueError, match="active database"):
        live.restore(path, tmp_path / "recovery.sqlite3")
    live.close()


def test_restore_rejects_unsupported_schema(tmp_path):
    live = SupplementStore(tmp_path / "live.sqlite3")
    live.add_profile("Safe")
    source = tmp_path / "future.sqlite3"
    with sqlite3.connect(source) as connection:
        connection.execute("PRAGMA user_version = 99")
    with pytest.raises(ValueError, match="schema version"):
        live.restore(source, tmp_path / "recovery.sqlite3")
    assert [x["name"] for x in live.profiles()] == ["Safe"]
    live.close()
