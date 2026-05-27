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
