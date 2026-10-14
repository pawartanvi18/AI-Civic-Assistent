from app.domain.matching import count_hits, has_complaint_signal
from app.messages import MESSAGES


def test_ascii_matches_word_start_only():
    assert count_hits(["tap"], "capital of France") == 0
    assert count_hits(["drain"], "the drains are blocked") == 1


def test_devanagari_substring_match():
    assert count_hits(["जन्म"], "जन्म प्रमाणपत्र कुठे मिळेल") == 1


def test_complaint_signal():
    assert has_complaint_signal("There is a big pothole near my house")
    assert not has_complaint_signal("Where can I get a birth certificate?")


def test_all_languages_have_same_keys_and_placeholders():
    from string import Formatter

    def fields(s):
        return {f for _, f, _, _ in Formatter().parse(s) if f}

    en = MESSAGES["en"]
    for lang in ("mr", "hi"):
        assert set(MESSAGES[lang]) == set(en), lang
        for key in en:
            assert fields(MESSAGES[lang][key]) == fields(en[key]), (lang, key)