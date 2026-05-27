import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from libs.config import BASIC_FIELDS, CLOZE_FIELDS, BASIC_TEMPLATES, BASIC_CSS


def test_basic_fields_include_notes_and_mnemonic():
    field_names = [f["name"] for f in BASIC_FIELDS]
    assert "Notes" in field_names
    assert "Mnemonic" in field_names


def test_cloze_fields_include_notes_and_mnemonic():
    field_names = [f["name"] for f in CLOZE_FIELDS]
    assert "Notes" in field_names
    assert "Mnemonic" in field_names


def test_basic_templates_afmt_contain_notes_block():
    for tpl in BASIC_TEMPLATES:
        assert "{{#Notes}}" in tpl["afmt"], f"Template '{tpl['name']}' missing Notes block"
        assert "{{#Mnemonic}}" in tpl["afmt"], f"Template '{tpl['name']}' missing Mnemonic block"


def test_css_contains_notes_and_mnemonic_classes():
    assert "info-block-notes" in BASIC_CSS
    assert "info-block-mnemonic" in BASIC_CSS


from libs.anki_logic import AnkiLogic


def test_create_anki_note_includes_notes_and_mnemonic():
    logic = AnkiLogic("TestDeck")
    model = logic.create_basic_model(123456789)
    note = logic.create_anki_note(
        model=model,
        word="beefy",
        pos="adj.",
        meaning="壯碩的",
        synonyms="",
        ex1_ori="He's a beefy guy.",
        ex1_trans="他是個壯碩的人。",
        ex2_ori="",
        ex2_trans="",
        notes="vs muscular: beefy 強調體型厚重，不一定有線條",
        mnemonic="beef = 牛肉 → 想像一塊厚實牛排",
    )
    # Field order: Word(0), Pos(1), Meaning(2), Synonyms(3), Ex1_ori(4), Ex1_trans(5),
    #              Ex2_ori(6), Ex2_trans(7), Audio(8), Hint(9), Notes(10), Mnemonic(11)
    assert note.fields[10] == "vs muscular: beefy 強調體型厚重，不一定有線條"
    assert note.fields[11] == "beef = 牛肉 → 想像一塊厚實牛排"


def test_create_anki_note_defaults_to_empty_strings():
    logic = AnkiLogic("TestDeck")
    model = logic.create_basic_model(123456789)
    note = logic.create_anki_note(
        model=model,
        word="apple",
        pos="n.",
        meaning="蘋果",
        synonyms="",
        ex1_ori="I eat an apple.",
        ex1_trans="我吃一顆蘋果。",
        ex2_ori="",
        ex2_trans="",
    )
    assert note.fields[10] == ""   # Notes
    assert note.fields[11] == ""   # Mnemonic


def test_create_cloze_note_includes_notes_and_mnemonic():
    logic = AnkiLogic("TestDeck")
    model = logic.create_cloze_model(987654321)
    note = logic.create_cloze_note(
        model=model,
        text="He's a {{c1::beefy}} guy.",
        word="beefy",
        pos="adj.",
        meaning="壯碩的",
        synonyms="",
        ex1_ori="He's a beefy guy.",
        ex1_trans="他是個壯碩的人。",
        ex2_ori="",
        ex2_trans="",
        notes="vs muscular",
        mnemonic="beef → 牛排",
    )
    # Field order for Cloze: Text(0), Word(1), Pos(2), Meaning(3), Synonyms(4),
    #   Ex1_ori(5), Ex1_trans(6), Ex2_ori(7), Ex2_trans(8), Audio(9), Hint(10), Notes(11), Mnemonic(12)
    assert note.fields[11] == "vs muscular"
    assert note.fields[12] == "beef → 牛排"
