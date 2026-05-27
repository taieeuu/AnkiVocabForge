# Notes & Mnemonic Fields Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two optional user-filled fields (`notes`, `mnemonic`) to Vocab Anki cards (Basic and Cloze), displayed on the answer side with info-block styling.

**Architecture:** Pure data-layer addition — new fields flow from the frontend `Card` type → backend Anki model fields → Anki note `fields` list → exported `.apkg`. No AI generation, no schema changes, no grammar card changes.

**Tech Stack:** TypeScript (frontend types), Python + genanki (backend Anki export), Anki HTML/CSS templates

---

## File Map

| File | Change |
|------|--------|
| `frontend/src/types.ts` | Add `notes?` and `mnemonic?` to `Card` interface |
| `backend/libs/config.py` | Add fields to `BASIC_FIELDS` / `CLOZE_FIELDS`; update `BASIC_TEMPLATES` afmt; add CSS classes |
| `backend/libs/anki_logic.py` | Add `notes` / `mnemonic` params to `create_anki_note` and `create_cloze_note` |
| `backend/service/anki_service.py` | Pass `notes` / `mnemonic` at all 6 call sites |
| `backend/tests/test_anki_notes_fields.py` | New — unit tests for the new fields |

---

### Task 1: Frontend — extend Card type

**Files:**
- Modify: `frontend/src/types.ts:31-53`

- [ ] **Step 1: Add fields to Card interface**

Open `frontend/src/types.ts`. The `Card` interface currently ends with `hint: string;`. Add two optional fields after it:

```ts
export interface Card {
  id: number;
  front?: string;
  back?: string;
  sentence?: string;
  // Vocab card fields
  word?: string;
  pos?: string;
  synonyms?: string;
  audio?: string;
  // Grammar card fields
  grammar?: string;
  pattern?: string;
  usage?: string;
  contrast?: string;
  // Common fields
  meaning: string;
  ex1_ori: string;
  ex1_trans: string;
  ex2_ori: string;
  ex2_trans: string;
  hint: string;
  notes?: string;
  mnemonic?: string;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat: add notes and mnemonic fields to Card interface"
```

---

### Task 2: Backend config — Anki fields, templates, CSS

**Files:**
- Modify: `backend/libs/config.py`

- [ ] **Step 1: Write failing test first**

Create `backend/tests/test_anki_notes_fields.py`:

```python
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
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd backend && python -m pytest tests/test_anki_notes_fields.py -v
```

Expected: 4 FAILED (fields and classes not yet defined).

- [ ] **Step 3: Add Notes and Mnemonic to BASIC_FIELDS**

In `backend/libs/config.py`, find `BASIC_FIELDS` (currently ends with `{"name": "Hint"}`). Append:

```python
BASIC_FIELDS = [
    {"name": "Word"},
    {"name": "Pos"},
    {"name": "Meaning"},
    {"name": "Synonyms"},
    {"name": "Ex1_ori"},
    {"name": "Ex1_trans"},
    {"name": "Ex2_ori"},
    {"name": "Ex2_trans"},
    {"name": "Audio"},
    {"name": "Hint"},
    {"name": "Notes"},
    {"name": "Mnemonic"},
]
```

- [ ] **Step 4: Add Notes and Mnemonic to CLOZE_FIELDS**

Find `CLOZE_FIELDS` (currently ends with `{"name": "Hint"}`). Append:

```python
CLOZE_FIELDS = [
    {"name": "Text"},
    {"name": "Word"},
    {"name": "Pos"},
    {"name": "Meaning"},
    {"name": "Synonyms"},
    {"name": "Ex1_ori"},
    {"name": "Ex1_trans"},
    {"name": "Ex2_ori"},
    {"name": "Ex2_trans"},
    {"name": "Audio"},
    {"name": "Hint"},
    {"name": "Notes"},
    {"name": "Mnemonic"},
]
```

- [ ] **Step 5: Update BASIC_TEMPLATES — Card 1 afmt**

In `BASIC_TEMPLATES`, find the `"Card 1"` template. Replace its `afmt` value so that Notes and Mnemonic blocks appear after the example blocks:

```python
        "afmt": """
<div class="heading">{{Word}}<span class="pos-badge">{{Pos}}</span></div>
{{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}
{{#Audio}}<div class="section">{{Audio}}</div>{{/Audio}}
<hr id=answer>
<div class="meaning">{{Meaning}}</div>
{{#Synonyms}}<div class="synonyms">{{Synonyms}}</div>{{/Synonyms}}
{{#Ex1_ori}}
<div class="example-block">
    <div class="example-ori">{{Ex1_ori}}</div>
    <div class="example-trans">{{Ex1_trans}}</div>
</div>
{{/Ex1_ori}}
{{#Ex2_ori}}
<div class="example-block">
    <div class="example-ori">{{Ex2_ori}}</div>
    <div class="example-trans">{{Ex2_trans}}</div>
</div>
{{/Ex2_ori}}
{{#Notes}}
<div class="info-block info-block-notes">
    <div class="info-label">Notes</div>
    <div class="info-content">{{Notes}}</div>
</div>
{{/Notes}}
{{#Mnemonic}}
<div class="info-block info-block-mnemonic">
    <div class="info-label">Mnemonic</div>
    <div class="info-content">{{Mnemonic}}</div>
</div>
{{/Mnemonic}}
""",
```

- [ ] **Step 6: Update BASIC_TEMPLATES — Card 2 (Reverse) afmt**

Find the `"Card 2 (Reverse)"` template. Replace its `afmt` similarly:

```python
        "afmt": """
<div class="heading">{{Meaning}}<span class="pos-badge">{{Pos}}</span></div>
{{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}
<hr id=answer>
<div class="meaning">{{Word}}</div>
{{#Synonyms}}<div class="synonyms">{{Synonyms}}</div>{{/Synonyms}}
{{#Ex1_ori}}
<div class="example-block">
    <div class="example-ori">{{Ex1_ori}}</div>
    <div class="example-trans">{{Ex1_trans}}</div>
</div>
{{/Ex1_ori}}
{{#Ex2_ori}}
<div class="example-block">
    <div class="example-ori">{{Ex2_ori}}</div>
    <div class="example-trans">{{Ex2_trans}}</div>
</div>
{{/Ex2_ori}}
{{#Audio}}<div class="section">{{Audio}}</div>{{/Audio}}
{{#Notes}}
<div class="info-block info-block-notes">
    <div class="info-label">Notes</div>
    <div class="info-content">{{Notes}}</div>
</div>
{{/Notes}}
{{#Mnemonic}}
<div class="info-block info-block-mnemonic">
    <div class="info-label">Mnemonic</div>
    <div class="info-content">{{Mnemonic}}</div>
</div>
{{/Mnemonic}}
""",
```

- [ ] **Step 7: Add CSS classes to BASIC_CSS**

In `BASIC_CSS`, append these rules before the closing `"""`. Add them after the existing `info-block-contrast` night mode lines:

```css
.info-block-notes {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
}
.info-block-notes .info-label { color: #2563eb; }

.info-block-mnemonic {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
}
.info-block-mnemonic .info-label { color: #16a34a; }

.card.night_mode .info-block-notes        { background: rgba(37,99,235,0.15);  border-color: rgba(37,99,235,0.3); }
.card.night_mode .info-block-notes .info-label    { color: #93c5fd; }
.card.night_mode .info-block-mnemonic     { background: rgba(22,163,74,0.15);  border-color: rgba(22,163,74,0.3); }
.card.night_mode .info-block-mnemonic .info-label { color: #86efac; }
```

- [ ] **Step 8: Run tests to confirm they pass**

```bash
cd backend && python -m pytest tests/test_anki_notes_fields.py -v
```

Expected: 4 PASSED.

- [ ] **Step 9: Commit**

```bash
git add backend/libs/config.py backend/tests/test_anki_notes_fields.py
git commit -m "feat: add Notes and Mnemonic to Anki Basic/Cloze fields and templates"
```

---

### Task 3: anki_logic.py — note creation functions

**Files:**
- Modify: `backend/libs/anki_logic.py:35-79` (create_anki_note), `backend/libs/anki_logic.py:136-198` (create_cloze_note)

- [ ] **Step 1: Write failing tests**

Add to `backend/tests/test_anki_notes_fields.py`:

```python
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
    # Field order: Word, Pos, Meaning, Synonyms, Ex1_ori, Ex1_trans,
    #              Ex2_ori, Ex2_trans, Audio, Hint, Notes, Mnemonic
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
    # Field order for Cloze: Text, Word, Pos, Meaning, Synonyms, Ex1_ori, Ex1_trans,
    #                        Ex2_ori, Ex2_trans, Audio, Hint, Notes, Mnemonic
    assert note.fields[11] == "vs muscular"
    assert note.fields[12] == "beef → 牛排"
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd backend && python -m pytest tests/test_anki_notes_fields.py -v
```

Expected: 3 new tests FAILED (unexpected keyword argument `notes`).

- [ ] **Step 3: Update create_anki_note signature and fields**

In `backend/libs/anki_logic.py`, replace the `create_anki_note` method:

```python
def create_anki_note(
    self,
    model,
    word: str,
    pos: str,
    meaning: str,
    synonyms: str,
    ex1_ori: str,
    ex1_trans: str,
    ex2_ori: str,
    ex2_trans: str,
    audio: str = "",
    hint: str = "",
    notes: str = "",
    mnemonic: str = "",
):
    """建立 Anki note"""
    audio_filename = os.path.basename(audio) if audio else ""

    fields = [
        str(word) if word is not None else "",
        str(pos) if pos is not None else "",
        str(meaning) if meaning is not None else "",
        str(synonyms) if synonyms is not None else "",
        str(ex1_ori) if ex1_ori is not None else "",
        str(ex1_trans) if ex1_trans is not None else "",
        str(ex2_ori) if ex2_ori is not None else "",
        str(ex2_trans) if ex2_trans is not None else "",
        f"[sound:{audio_filename}]" if audio else "",
        str(hint) if hint is not None else "",
        str(notes) if notes is not None else "",
        str(mnemonic) if mnemonic is not None else "",
    ]

    note = genanki.Note(model=model, fields=fields)

    if audio:
        audio_path = os.path.abspath(audio) if not os.path.isabs(audio) else audio
        if os.path.exists(audio_path):
            self.media_files.append(audio_path)
        else:
            logger.log(LogLevel.WARNING, f"Audio file not found, skipping: {audio_path}")

    return note
```

- [ ] **Step 4: Update create_cloze_note signature and fields**

In the same file, replace the `create_cloze_note` method:

```python
def create_cloze_note(
    self,
    model,
    text: str = "",
    word: str = "",
    pos: str = "",
    meaning: str = "",
    synonyms: str = "",
    ex1_ori: str = "",
    ex1_trans: str = "",
    ex2_ori: str = "",
    ex2_trans: str = "",
    audio: str = "",
    hint: str = "",
    notes: str = "",
    mnemonic: str = "",
):
    """建立 Cloze 類型的 Anki note"""
    audio_filename = os.path.basename(audio) if audio else ""

    fields = [
        str(text) if text is not None else "",
        str(word) if word is not None else "",
        str(pos) if pos is not None else "",
        str(meaning) if meaning is not None else "",
        str(synonyms) if synonyms is not None else "",
        str(ex1_ori) if ex1_ori is not None else "",
        str(ex1_trans) if ex1_trans is not None else "",
        str(ex2_ori) if ex2_ori is not None else "",
        str(ex2_trans) if ex2_trans is not None else "",
        f"[sound:{audio_filename}]" if audio else "",
        str(hint) if hint is not None else "",
        str(notes) if notes is not None else "",
        str(mnemonic) if mnemonic is not None else "",
    ]

    note = genanki.Note(model=model, fields=fields)

    if audio:
        audio_path = os.path.abspath(audio) if not os.path.isabs(audio) else audio
        if os.path.exists(audio_path):
            self.media_files.append(audio_path)
        else:
            logger.log(LogLevel.WARNING, f"Audio file not found, skipping: {audio_path}")

    return note
```

- [ ] **Step 5: Run all tests**

```bash
cd backend && python -m pytest tests/test_anki_notes_fields.py -v
```

Expected: all 7 tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add backend/libs/anki_logic.py backend/tests/test_anki_notes_fields.py
git commit -m "feat: add notes and mnemonic params to create_anki_note and create_cloze_note"
```

---

### Task 4: anki_service.py — pass fields at all call sites

**Files:**
- Modify: `backend/service/anki_service.py`

There are 8 call sites across 6 methods. Add `notes=v.get("notes") or ""` and `mnemonic=v.get("mnemonic") or ""` to each.

- [ ] **Step 1: Update import_basic_model_notes (line ~62)**

Find the `logic.create_anki_note(...)` call inside `import_basic_model_notes`. Add the two new kwargs:

```python
note = logic.create_anki_note(
    model=model,
    word=word,
    pos=v.get("pos") or "",
    meaning=v.get("meaning") or "",
    synonyms=v.get("synonyms") or "",
    ex1_ori=v.get("ex1_ori") or "",
    ex1_trans=v.get("ex1_trans") or "",
    ex2_ori=v.get("ex2_ori") or "",
    ex2_trans=v.get("ex2_trans") or "",
    audio=audio_path,
    hint=v.get("hint") or "",
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 2: Update confirm_and_pack_basic_model (line ~107)**

Same change — find `logic.create_anki_note(...)` inside `confirm_and_pack_basic_model`:

```python
note = logic.create_anki_note(
    model=model,
    word=word,
    pos=v.get("pos") or "",
    meaning=v.get("meaning") or "",
    synonyms=v.get("synonyms") or "",
    ex1_ori=v.get("ex1_ori") or "",
    ex1_trans=v.get("ex1_trans") or "",
    ex2_ori=v.get("ex2_ori") or "",
    ex2_trans=v.get("ex2_trans") or "",
    audio=audio_path,
    hint=v.get("hint") or "",
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 3: Update confirm_and_pack_cloze_model — cloze call site (line ~175)**

Find `logic.create_cloze_note(...)` inside `confirm_and_pack_cloze_model`:

```python
note = logic.create_cloze_note(
    model=model,
    text=cloze_text,
    word=word,
    pos=v.get("pos", ""),
    meaning=v.get("meaning", ""),
    synonyms=v.get("synonyms", ""),
    ex1_ori=ex1_ori,
    ex1_trans=ex1_trans,
    ex2_ori=ex2_ori,
    ex2_trans=ex2_trans,
    audio=audio_path,
    hint=v.get("hint", ""),
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 4: Update confirm_and_pack_basic_and_cloze — basic call site (line ~221)**

Find the Basic `logic.create_anki_note(...)` call inside `confirm_and_pack_basic_and_cloze`:

```python
note = logic.create_anki_note(
    model=basic_model,
    word=word,
    pos=v.get("pos") or "",
    meaning=v.get("meaning") or "",
    synonyms=v.get("synonyms") or "",
    ex1_ori=v.get("ex1_ori") or "",
    ex1_trans=v.get("ex1_trans") or "",
    ex2_ori=v.get("ex2_ori") or "",
    ex2_trans=v.get("ex2_trans") or "",
    audio=audio_path,
    hint=v.get("hint") or "",
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 5: Update confirm_and_pack_basic_and_cloze — cloze call site (line ~269)**

Find the Cloze `logic.create_cloze_note(...)` call inside the same method:

```python
note = logic.create_cloze_note(
    model=cloze_model,
    text=cloze_text,
    word=word,
    pos=v.get("pos", ""),
    meaning=v.get("meaning", ""),
    synonyms=v.get("synonyms", ""),
    ex1_ori=ex1_ori,
    ex1_trans=ex1_trans,
    ex2_ori=ex2_ori,
    ex2_trans=ex2_trans,
    audio=audio_path,
    hint=v.get("hint", ""),
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 6: Update import_basic_and_cloze_notes — basic call site (line ~428)**

Find `logic.create_anki_note(...)` inside `import_basic_and_cloze_notes`:

```python
note = logic.create_anki_note(
    model=basic_model,
    word=word,
    pos=v.get("pos") or "",
    meaning=v.get("meaning") or "",
    synonyms=v.get("synonyms") or "",
    ex1_ori=v.get("ex1_ori") or "",
    ex1_trans=v.get("ex1_trans") or "",
    ex2_ori=v.get("ex2_ori") or "",
    ex2_trans=v.get("ex2_trans") or "",
    audio=audio_path,
    hint=v.get("hint") or "",
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 7: Update import_cloze_model_notes (line ~360)**

Find `logic.create_cloze_note(...)` inside `import_cloze_model_notes`:

```python
note = logic.create_cloze_note(
    model=model,
    text=cloze_text,
    word=word,
    pos=v.get("pos", ""),
    meaning=v.get("meaning", ""),
    synonyms=v.get("synonyms", ""),
    ex1_ori=ex1_ori,
    ex1_trans=ex1_trans,
    ex2_ori=ex2_ori,
    ex2_trans=ex2_trans,
    audio=audio_path,
    hint=v.get("hint", ""),
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 8: Update import_basic_and_cloze_notes — cloze call site (line ~476)**

Find `logic.create_cloze_note(...)` inside the same method:

```python
note = logic.create_cloze_note(
    model=cloze_model,
    text=cloze_text,
    word=word,
    pos=v.get("pos", ""),
    meaning=v.get("meaning", ""),
    synonyms=v.get("synonyms", ""),
    ex1_ori=ex1_ori,
    ex1_trans=ex1_trans,
    ex2_ori=ex2_ori,
    ex2_trans=ex2_trans,
    audio=audio_path,
    hint=v.get("hint", ""),
    notes=v.get("notes") or "",
    mnemonic=v.get("mnemonic") or "",
)
```

- [ ] **Step 9: Run all tests**

```bash
cd backend && python -m pytest tests/test_anki_notes_fields.py -v
```

Expected: all 7 PASSED.

- [ ] **Step 10: Commit**

```bash
git add backend/service/anki_service.py
git commit -m "feat: pass notes and mnemonic through all anki_service call sites"
```

---

### Task 5: Final verification

- [ ] **Step 1: Start the backend**

```bash
cd backend && python main.py
```

Expected: server starts without errors.

- [ ] **Step 2: Start the frontend**

```bash
cd frontend && npm run dev
```

Expected: dev server starts, no TypeScript errors in console.

- [ ] **Step 3: Generate a vocab card and check JSON**

In the UI, generate any vocab card. Open the JSON editor. Verify that `notes` and `mnemonic` keys appear as empty strings in each card object:

```json
{
  "word": "beefy",
  ...
  "notes": "",
  "mnemonic": ""
}
```

- [ ] **Step 4: Fill in notes and mnemonic, export, verify .apkg**

In the JSON editor, manually add values:
```json
"notes": "vs muscular: beefy 強調體型厚重",
"mnemonic": "beef = 牛肉 → 想像一塊厚實牛排"
```

Export the deck. Import the `.apkg` into Anki and confirm:
- Notes block (blue) appears at the bottom of the answer side
- Mnemonic block (green) appears below Notes
- Both are absent on cards where the fields are empty

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "feat: notes and mnemonic fields complete"
```
