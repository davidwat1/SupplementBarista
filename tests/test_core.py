import pytest

from supplement_barista.core import SupplementStore


def test_profile_and_schedule():
    store = SupplementStore()
    profile = store.add_profile("Test")
    supplement = store.add_supplement("Example", "Capsule")
    store.add_dose(profile, supplement, "09:30", 1, "capsule")
    store.add_dose(profile, supplement, "08:00", 2, "capsules")
    assert [row["time"] for row in store.schedule(profile)] == ["08:00", "09:30"]
    store.close()


def test_rejects_invalid_schedule_time():
    store = SupplementStore()
    profile = store.add_profile("Test")
    supplement = store.add_supplement("Example", "Capsule")
    with pytest.raises(ValueError):
        store.add_dose(profile, supplement, "09:15", 1, "capsule")
    store.close()
