# Notes & Mnemonic Fields — Design Spec

Date: 2026-05-27

## Summary

Add two optional, user-filled fields to Vocab cards (Basic and Cloze models). Neither field is AI-generated. Both initialize as empty strings and are only visible in the Anki card when the user has entered content.

Grammar cards are out of scope.

---

## Fields

| Field | Key | Purpose |
|-------|-----|---------|
| 備注 | `notes` | Record distinctions between confusable words (e.g., great vs greet, fantastic vs wonderful) |
| 記憶法 | `mnemonic` | Record a personal mnemonic when the user keeps forgetting a word |

---

## Anki Card Display

Both fields appear on the **answer side (afmt)** at the bottom of the card, after the example sentences.

```
答案面
───────────────────────────────
Meaning
Synonyms
Ex1_ori / Ex1_trans
Ex2_ori / Ex2_trans
───────────────────────────────
Notes      ← 藍色 info-block（有內容才顯示）
Mnemonic   ← 綠色 info-block（有內容才顯示）
```

Styling uses the existing `.info-block` CSS pattern (already defined in `BASIC_CSS`). Text size follows `.info-content` at 15px — smaller than the 20px card body, visually de-emphasizing them as supplementary annotations.

Two new CSS classes are added:
- `.info-block-notes` — blue palette
- `.info-block-mnemonic` — green palette

Both use `{{#Notes}}...{{/Notes}}` / `{{#Mnemonic}}...{{/Mnemonic}}` conditional wrapping so empty fields render nothing.

---

## Files to Modify

### `frontend/src/types.ts`
Add two optional fields to the `Card` interface:
```ts
notes?: string;
mnemonic?: string;
```

### `backend/libs/config.py`
1. Add `{"name": "Notes"}` and `{"name": "Mnemonic"}` to `BASIC_FIELDS` and `CLOZE_FIELDS`.
2. Add conditional display blocks to the `afmt` of both `BASIC_TEMPLATES` (Card 1 and Card 2 Reverse).
3. Add `.info-block-notes` and `.info-block-mnemonic` CSS to `BASIC_CSS` (and night mode variants).

### `backend/libs/anki_logic.py`
Add `notes: str = ""` and `mnemonic: str = ""` parameters to:
- `create_anki_note()`
- `create_cloze_note()`

Append both to their respective `fields` lists.

### `backend/service/anki_service.py`
In every call site of `create_anki_note()` and `create_cloze_note()`, add:
```python
notes=v.get("notes") or "",
mnemonic=v.get("mnemonic") or "",
```

Affected methods: `import_basic_model_notes`, `confirm_and_pack_basic_model`, `confirm_and_pack_cloze_model`, `confirm_and_pack_basic_and_cloze`, `import_cloze_model_notes`, `import_basic_and_cloze_notes`.

---

## Out of Scope

- AI generation of either field
- Grammar card changes
- Any changes to existing prompts or schemas (`schemas.py` untouched)
