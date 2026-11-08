import sqlite3

import pytest

from supplement_barista.core import SupplementStore


def test_catalog_crud_and_cascading_deletion():
    store = SupplementStore()
    profile = store.add_profile("Person")
    item = store.add_supplement("Original", "Capsule")
    store.rename_profile(profile, "Updated")
    store.update_supplement(item, "Updated Item", "Powder", "Personal note")
    dose = store.add_dose(profile, item, "10:00", 1, "scoop")
    store.update_dose(dose, "10:30", 2, "scoops")
    assert store.profiles()[0]["name"] == "Updated"
    assert store.supplements()[0]["notes"] == "Personal note"
    assert store.schedule(profile)[0]["quantity"] == 2
    store.delete_supplement(item)
    assert store.schedule(profile) == []
    store.delete_profile(profile)
    assert store.profiles() == []
    store.close()


def test_backup_restores_data(tmp_path):
    original = SupplementStore(tmp_path / "source.sqlite3")
    original.add_profile("Persisted")
    backup = tmp_path / "backup.sqlite3"
    original.backup(backup)
    with pytest.raises(FileExistsError):
        original.backup(backup)
    original.close()
    restored = SupplementStore(backup)
    assert restored.profiles()[0]["name"] == "Persisted"
    assert restored.connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    restored.close()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), 0, -1])
def test_invalid_quantities_rejected(value):
    store = SupplementStore()
    profile = store.add_profile("Person")
    item = store.add_supplement("Item", "Tablet")
    with pytest.raises(ValueError):
        store.add_dose(profile, item, "08:00", value, "tablet")
    store.close()


def test_foreign_keys_enforced():
    store = SupplementStore()
    with pytest.raises(sqlite3.IntegrityError):
        store.add_dose(999, 999, "08:00", 1, "tablet")
    store.close()


def test_backup_can_replace_existing_file_when_explicit(tmp_path):
    store = SupplementStore(tmp_path / "live.sqlite3")
    store.add_profile("Before")
    destination = tmp_path / "saved.sqlite3"
    store.backup(destination)
    store.add_profile("After")
    store.backup(destination, overwrite=True)
    with sqlite3.connect(destination) as db:
        names = [row[0] for row in db.execute("SELECT name FROM profiles ORDER BY name")]
        assert names == ["After", "Before"]
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    store.close()


def test_backup_refuses_to_overwrite_active_database(tmp_path):
    path = tmp_path / "live.sqlite3"
    store = SupplementStore(path)
    with pytest.raises(ValueError, match="active database"):
        store.backup(path, overwrite=True)
    store.close()
