import pytest

from supplement_barista.core import SupplementStore
from supplement_barista.csv_io import export_schedule, import_schedule


def test_csv_roundtrip(tmp_path):
    store = SupplementStore()
    profile = store.add_profile("Test")
    supplement = store.add_supplement("Example", "Capsule")
    store.add_dose(profile, supplement, "08:30", 2, "capsules")
    path = tmp_path / "schedule.csv"
    assert export_schedule(store, profile, path) == 1
    with pytest.raises(FileExistsError):
        export_schedule(store, profile, path)
    second = store.add_profile("Other")
    assert import_schedule(store, second, path) == 1
    assert store.schedule(second)[0]["time"] == "08:30"
    store.close()


def test_csv_invalid_row_does_not_partially_import(tmp_path):
    store = SupplementStore()
    profile = store.add_profile("Test")
    path = tmp_path / "invalid.csv"
    path.write_text(
        "time,supplement,form,quantity,unit\n"
        "08:00,Valid,Capsule,1,capsule\n"
        "08:15,Invalid,Capsule,1,capsule\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        import_schedule(store, profile, path)
    assert store.schedule(profile) == []
    assert store.supplements() == []
    store.close()


def test_csv_conflicting_form_rolls_back(tmp_path):
    store = SupplementStore()
    profile = store.add_profile("Test")
    store.add_supplement("Existing", "Tablet")
    path = tmp_path / "conflict.csv"
    path.write_text(
        "time,supplement,form,quantity,unit\n"
        "08:00,New,Capsule,1,capsule\n"
        "08:30,Existing,Powder,1,scoop\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        import_schedule(store, profile, path)
    assert store.schedule(profile) == []
    assert [x["name"] for x in store.supplements()] == ["Existing"]
    store.close()
