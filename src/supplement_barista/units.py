"""Normalize common dose-unit abbreviations without guessing ambiguous units."""

UNIT_ALIASES = {
    "cap": "capsule",
    "caps": "capsule",
    "capsule": "capsule",
    "capsules": "capsule",
    "pow": "powder",
    "pwdr": "powder",
    "powder": "powder",
    "tab": "tablet",
    "tabs": "tablet",
    "tablet": "tablet",
    "tablets": "tablet",
    "softgel": "softgel",
    "softgels": "softgel",
    "sg": "softgel",
    "drop": "drop",
    "drops": "drop",
    "scoop": "scoop",
    "scoops": "scoop",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "tbsp": "tbsp",
    "tablespoon": "tbsp",
    "milligram": "mg",
    "milligrams": "mg",
    "mg": "mg",
    "gram": "g",
    "grams": "g",
    "g": "g",
    "milliliter": "mL",
    "milliliters": "mL",
    "ml": "mL",
    "microgram": "mcg",
    "micrograms": "mcg",
    "mcg": "mcg",
    "µg": "mcg",
    "iu": "IU",
}


def normalize_unit(value: str) -> str:
    """Return a consistent label for known aliases; retain unknown custom units."""
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise ValueError("Dose unit is required")
    return UNIT_ALIASES.get(cleaned.casefold(), cleaned)
