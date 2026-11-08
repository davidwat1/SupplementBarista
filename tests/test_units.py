import pytest

from supplement_barista.core import SupplementStore
from supplement_barista.units import normalize_unit


@pytest.mark.parametrize(
    ("typed", "expected"),
    [
        ("cap", "capsule"), ("CAPS", "capsule"), ("pow", "powder"),
        ("tab", "tablet"), ("sg", "softgel"), ("ml", "mL"),
        ("MG", "mg"), ("mcg", "mcg"), ("iu", "IU"),
        ("custom unit", "custom unit"),
    ],
)
def test_normalize_unit(typed, expected):
    assert normalize_unit(typed) == expected


def test_empty_unit_rejected():
    with pytest.raises(ValueError):
        normalize_unit("   ")


def test_store_normalizes_added_and_updated_doses():
    store = SupplementStore()
    profile = store.add_profile("Person")
    supplement = store.add_supplement("NAC", "Capsule")
    dose = store.add_dose(profile, supplement, "08:00", 2, "cap")
    assert store.schedule(profile)[0]["unit"] == "capsule"
    store.update_dose(dose, "08:30", 1, "pow")
    assert store.schedule(profile)[0]["unit"] == "powder"
    store.close()


def test_supplement_form_normalizes_on_edit():
    store = SupplementStore()
    item = store.add_supplement("Vitamin C", "cap")
    assert store.supplements()[0]["form"] == "capsule"
    store.update_supplement(item, "Vitamin C", "pow")
    assert store.supplements()[0]["form"] == "powder"
    store.close()
