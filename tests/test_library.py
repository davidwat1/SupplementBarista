from supplement_barista.library import STARTER_SUPPLEMENTS, search_supplements


def test_starter_library_is_substantial_and_unique():
    assert len(STARTER_SUPPLEMENTS) >= 40
    names = [name.casefold() for name, _form in STARTER_SUPPLEMENTS]
    assert len(names) == len(set(names))
    assert all(name.strip() and form.strip() for name, form in STARTER_SUPPLEMENTS)


def test_search_matches_case_insensitively():
    assert ("N-Acetylcysteine (NAC)", "Powder") in search_supplements("nac")
    assert ("Magnesium Glycinate", "Capsule") in search_supplements("MAGNESIUM")
    assert search_supplements("no-match-12345") == []
