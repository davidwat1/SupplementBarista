"""Curated starter library of supplement names; no dosing recommendations."""

from __future__ import annotations

# Names are options, not a record of current use or medical recommendations.
STARTER_SUPPLEMENTS: tuple[tuple[str, str], ...] = (
    ("Activated BroccoRaphanin", "Capsule"),
    ("Alpha-Lipoic Acid (ALA)", "Capsule"),
    ("Ashwagandha", "Capsule"),
    ("Benfotiamine (B1)", "Capsule"),
    ("Berberine", "Capsule"),
    ("Betaine (TMG)", "Powder"),
    ("Beet Root", "Powder"),
    ("Bromelain", "Capsule"),
    ("Calcium", "Tablet"),
    ("Celeryforce", "Capsule"),
    ("Chlorella", "Tablet"),
    ("Coenzyme Q10 (CoQ10)", "Capsule"),
    ("Collagen Peptides", "Powder"),
    ("Comprehensive Minerals", "Capsule"),
    ("Creatine Monohydrate", "Powder"),
    ("Curcumin / Turmeric", "Capsule"),
    ("DHEA", "Capsule"),
    ("Electrolytes", "Powder"),
    ("Fish Oil (Omega-3)", "Softgel"),
    ("Ginger", "Powder"),
    ("Glutathione (GSH)", "Capsule"),
    ("Gotu Kola", "Capsule"),
    ("Hesperidin", "Capsule"),
    ("L-Arginine", "Powder"),
    ("L-Citrulline", "Powder"),
    ("Lactoferrin", "Capsule"),
    ("L-Theanine", "Capsule"),
    ("Magnesium Glycinate", "Capsule"),
    ("Magnesium L-Threonate", "Capsule"),
    ("Melatonin", "Capsule"),
    ("MSM", "Capsule"),
    ("N-Acetylcysteine (NAC)", "Powder"),
    ("Ornithine", "Capsule"),
    ("P5P (Vitamin B6)", "Capsule"),
    ("Probiotic", "Capsule"),
    ("Quercetin", "Capsule"),
    ("RelaxMax", "Powder"),
    ("Resveratrol", "Capsule"),
    ("Riboflavin (Vitamin B2)", "Capsule"),
    ("Selenium", "Capsule"),
    ("Slippery Elm", "Powder"),
    ("Taurine", "Powder"),
    ("Thiamine (Vitamin B1)", "Capsule"),
    ("Tribulus Terrestris", "Powder"),
    ("Vitamin B12", "Liquid"),
    ("Vitamin C", "Powder"),
    ("Vitamin D3", "Capsule"),
    ("Vitamin K2", "Capsule"),
    ("Zinc", "Capsule"),
)


def search_supplements(query: str = "") -> list[tuple[str, str]]:
    """Case-insensitive substring search; returns names and suggested default forms."""
    term = query.strip().casefold()
    return [
        (name, form)
        for name, form in STARTER_SUPPLEMENTS
        if term in name.casefold()
    ]
