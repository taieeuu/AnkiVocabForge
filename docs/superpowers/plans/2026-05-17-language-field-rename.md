# Language Field Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename all `source`/`target` language identifiers to `learning`/`native` across the full stack so that UI labels, frontend types, backend models, constants, and GPT prompt templates all use learner-centric terminology.

**Architecture:** The rename touches 9 files in a layered order — backend constants first (since prompt templates depend on them), then the route/service layer, then frontend types and components. No new files are created; all changes are in-place renames.

**Tech Stack:** Python/FastAPI (backend), React/TypeScript (frontend), Pydantic models, GPT prompt string templates.

---

## File Map

| File | What changes |
|---|---|
| `backend/libs/config.py` | `SOURCE_LANG` → `LEARNING_LANG`, `TARGET_LANG` → `NATIVE_LANG`; prompt template variables `{source_language}` → `{learning_language}`, `{target_language}` → `{native_language}` |
| `backend/libs/schemas.py` | Field description strings: 「來源語言」→「學習語言」, 「目標語言」→「母語」 |
| `backend/routes/dependencies.py` | `ValidatedSettings` fields `source_lang`/`target_lang` → `learning_lang`/`native_lang`; lookup key lists updated |
| `backend/routes/generate_helpers.py` | Import `LEARNING_LANG`/`NATIVE_LANG`; `get_language_settings()` lookup keys + return values |
| `backend/routes/settings.py` | Import `LEARNING_LANG`/`NATIVE_LANG`; response key `'sourceLang'` → `'learningLang'` |
| `backend/routes/generate.py` | `validated_settings.source_lang` → `validated_settings.learning_lang`, same for `target_lang` |
| `backend/service/main_processor.py` | Parameter names `source_lang`/`target_lang` → `learning_lang`/`native_lang` throughout |
| `backend/service/parser_service.py` | Parameter names + `.format()` keyword args updated |
| `frontend/src/types.ts` | `Settings` interface: `sourceLanguage` → `learningLanguage`, `language` → `nativeLanguage` |
| `frontend/src/components/SettingsModal.tsx` | UI labels + field bindings |
| `frontend/src/App.tsx` | Initial state keys + API request body keys |

---

## Task 1: Backend — Rename constants and prompt template variables in `config.py`

**Files:**
- Modify: `backend/libs/config.py`

- [ ] **Step 1: Rename the two language constants**

Find lines 63–64 in `backend/libs/config.py`:
```python
# 語言設定
SOURCE_LANG: str = _get("SOURCE_LANG", "English")
TARGET_LANG: str = _get("TARGET_LANG", "Chinese")
```
Replace with:
```python
# 語言設定
LEARNING_LANG: str = _get("SOURCE_LANG", "English")
NATIVE_LANG: str = _get("TARGET_LANG", "Chinese")
```
Note: The env var key strings (`"SOURCE_LANG"`, `"TARGET_LANG"`) stay unchanged so existing `.env` files keep working.

- [ ] **Step 2: Replace all `{source_language}` placeholders in prompt templates**

In `backend/libs/config.py`, do a global replace:
- `{source_language}` → `{learning_language}` (appears ~10 times across the three prompt template strings)
- `{target_language}` → `{native_language}` (appears ~10 times)

After the replace, every prompt format call will expect keyword args `learning_language=` and `native_language=` instead of `source_language=` and `target_language=`.

- [ ] **Step 3: Verify no old names remain in config.py**

```bash
grep -n "SOURCE_LANG\|TARGET_LANG\|source_language\|target_language" backend/libs/config.py
```
Expected: zero matches (the env var strings `"SOURCE_LANG"` and `"TARGET_LANG"` inside `_get(...)` are fine to remain — they are string literals passed as dict keys, not identifiers).

- [ ] **Step 4: Commit**

```bash
git add backend/libs/config.py
git commit -m "refactor: rename SOURCE/TARGET_LANG constants and prompt vars to LEARNING/NATIVE_LANG"
```

---

## Task 2: Backend — Update field descriptions in `schemas.py`

**Files:**
- Modify: `backend/libs/schemas.py`

- [ ] **Step 1: Update VocabCard descriptions**

Current (lines 9, 11, 13):
```python
ex1_ori:   str = Field(description="第一個例句（來源語言）")
ex2_ori:   str = Field(description="第二個例句（來源語言）")
hint:      str = Field(description="不使用該單字本身的說明，以來源語言撰寫")
```
Replace with:
```python
ex1_ori:   str = Field(description="第一個例句（學習語言）")
ex2_ori:   str = Field(description="第二個例句（學習語言）")
hint:      str = Field(description="不使用該單字本身的說明，以學習語言撰寫")
```

Also update lines 6–8 (meaning and synonyms use target):
```python
pos:       str = Field(description="目標語言的詞性（例如：n., v., adj., adv., prep., conj.）")
meaning:   str = Field(description="單字在目標語言中的意思")
synonyms:  str = Field(description="3-5 個同義詞及其目標語言翻譯，以單一字串呈現")
```
Replace with:
```python
pos:       str = Field(description="母語的詞性（例如：n., v., adj., adv., prep., conj.）")
meaning:   str = Field(description="單字在母語中的意思")
synonyms:  str = Field(description="3-5 個同義詞及其母語翻譯，以單一字串呈現")
```

- [ ] **Step 2: Update GrammarCard descriptions**

Current (lines 22–25):
```python
usage:     str = Field(description="此文法的使用時機與條件，以來源語言撰寫")
meaning:   str = Field(description="目標語言的意思或說明")
ex1_ori:   str = Field(description="第一個例句（來源語言）")
ex2_ori:   str = Field(description="第二個例句（來源語言）")
```
Replace with:
```python
usage:     str = Field(description="此文法的使用時機與條件，以學習語言撰寫")
meaning:   str = Field(description="母語的意思或說明")
ex1_ori:   str = Field(description="第一個例句（學習語言）")
ex2_ori:   str = Field(description="第二個例句（學習語言）")
```

- [ ] **Step 3: Commit**

```bash
git add backend/libs/schemas.py
git commit -m "refactor: update schema field descriptions to use 學習語言/母語 terminology"
```

---

## Task 3: Backend — Update `ValidatedSettings` and lookup keys in `dependencies.py`

**Files:**
- Modify: `backend/routes/dependencies.py`

- [ ] **Step 1: Rename ValidatedSettings fields**

Current (lines 16–17):
```python
class ValidatedSettings(BaseModel):
    """驗證後的設置"""
    api_key: str
    model: str
    source_lang: str
    target_lang: str
```
Replace with:
```python
class ValidatedSettings(BaseModel):
    """驗證後的設置"""
    api_key: str
    model: str
    learning_lang: str
    native_lang: str
```

- [ ] **Step 2: Update the lookup key lists and constructor call**

Current (lines 52–72):
```python
    source_lang = _get_setting_value(
        settings,
        'sourceLang',
        'sourceLanguage',
        'source_language',
        default='English'
    )
    target_lang = _get_setting_value(
        settings,
        'language',
        'targetLang',
        'targetLanguage',
        'target_language',
        default='Chinese'
    )
    
    return ValidatedSettings(
        api_key=api_key,
        model=model,
        source_lang=source_lang,
        target_lang=target_lang
    )
```
Replace with:
```python
    learning_lang = _get_setting_value(
        settings,
        'learningLang',
        'learningLanguage',
        'learning_language',
        default='English'
    )
    native_lang = _get_setting_value(
        settings,
        'nativeLang',
        'nativeLanguage',
        'native_language',
        default='Chinese'
    )
    
    return ValidatedSettings(
        api_key=api_key,
        model=model,
        learning_lang=learning_lang,
        native_lang=native_lang
    )
```

- [ ] **Step 3: Verify no old identifiers remain**

```bash
grep -n "source_lang\|target_lang\|sourceLanguage\|source_language\|targetLanguage\|target_language" backend/routes/dependencies.py
```
Expected: zero matches.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/dependencies.py
git commit -m "refactor: rename ValidatedSettings source_lang/target_lang to learning_lang/native_lang"
```

---

## Task 4: Backend — Update `generate_helpers.py` and `settings.py`

**Files:**
- Modify: `backend/routes/generate_helpers.py`
- Modify: `backend/routes/settings.py`

- [ ] **Step 1: Update import in `generate_helpers.py`**

Current (line 11):
```python
from libs.config import OUTPUTS_DIR, PASSAGE_IMAGE_DIR, SOURCE_LANG, TARGET_LANG, AI_MODEL
```
Replace with:
```python
from libs.config import OUTPUTS_DIR, PASSAGE_IMAGE_DIR, LEARNING_LANG, NATIVE_LANG, AI_MODEL
```

- [ ] **Step 2: Update `get_language_settings()` in `generate_helpers.py`**

Current (lines 193–208):
```python
    source_lang = _get_setting_value(
        settings,
        'sourceLang',
        'sourceLanguage',
        'source_language',
        default=SOURCE_LANG
    )
    target_lang = _get_setting_value(
        settings,
        'language',
        'targetLang',
        'targetLanguage',
        'target_language',
        default=TARGET_LANG
    )
    return source_lang, target_lang
```
Replace with:
```python
    learning_lang = _get_setting_value(
        settings,
        'learningLang',
        'learningLanguage',
        'learning_language',
        default=LEARNING_LANG
    )
    native_lang = _get_setting_value(
        settings,
        'nativeLang',
        'nativeLanguage',
        'native_language',
        default=NATIVE_LANG
    )
    return learning_lang, native_lang
```

- [ ] **Step 3: Update import in `settings.py`**

Current (line 6):
```python
from libs.config import OPENAI_API_KEY, AI_MODEL, TARGET_LANG, SOURCE_LANG
```
Replace with:
```python
from libs.config import OPENAI_API_KEY, AI_MODEL, NATIVE_LANG, LEARNING_LANG
```

- [ ] **Step 4: Update `get_settings()` response in `settings.py`**

Current (lines 16–21):
```python
    return {
        'apiKey': OPENAI_API_KEY[:10] + '***' if OPENAI_API_KEY else '',
        'model': AI_MODEL,
        'language': TARGET_LANG,
        'sourceLang': SOURCE_LANG
    }
```
Replace with:
```python
    return {
        'apiKey': OPENAI_API_KEY[:10] + '***' if OPENAI_API_KEY else '',
        'model': AI_MODEL,
        'nativeLang': NATIVE_LANG,
        'learningLang': LEARNING_LANG
    }
```

- [ ] **Step 5: Verify no old names remain in both files**

```bash
grep -n "SOURCE_LANG\|TARGET_LANG\|source_lang\|target_lang\|sourceLang\|targetLang\|source_language\|target_language" backend/routes/generate_helpers.py backend/routes/settings.py
```
Expected: zero matches.

- [ ] **Step 6: Commit**

```bash
git add backend/routes/generate_helpers.py backend/routes/settings.py
git commit -m "refactor: update generate_helpers and settings routes to use learning/native lang constants"
```

---

## Task 5: Backend — Update `generate.py` callers of `ValidatedSettings`

**Files:**
- Modify: `backend/routes/generate.py`

- [ ] **Step 1: Replace all `validated_settings.source_lang` and `validated_settings.target_lang`**

There are 4 places in `generate.py` that pass language to processor methods (lines ~143–144, ~257–258, ~342–343, ~363–364, ~463–464). In each one:

```python
# Before (example)
source_lang=validated_settings.source_lang,
target_lang=validated_settings.target_lang,
```
Change to:
```python
# After
source_lang=validated_settings.learning_lang,
target_lang=validated_settings.native_lang,
```
Note: The keyword argument name (`source_lang=`) matches the parameter name in `main_processor.py` methods — do NOT rename these keyword argument names yet; that happens in Task 6.

- [ ] **Step 2: Verify**

```bash
grep -n "\.source_lang\|\.target_lang" backend/routes/generate.py
```
Expected: zero matches.

- [ ] **Step 3: Commit**

```bash
git add backend/routes/generate.py
git commit -m "refactor: update generate.py to access learning_lang/native_lang from ValidatedSettings"
```

---

## Task 6: Backend — Rename parameters in `main_processor.py` and `parser_service.py`

**Files:**
- Modify: `backend/service/main_processor.py`
- Modify: `backend/service/parser_service.py`

- [ ] **Step 1: Rename parameters in all `main_processor.py` methods**

Each of the 5 public methods (`run_article_mode`, `run_vocab_mode`, `run_ai_generate_mode`, `run_grammar_mode`, `run_grammar_from_file_mode`) has `source_lang: str = 'English'` and `target_lang: str = 'Chinese'` parameters. Rename all of them:

```python
# Before
def run_article_mode(self, ..., source_lang: str = 'English', target_lang: str = 'Chinese', ...):
    ...
    result = ParserService.parse_passage_with_vocab(..., source_lang=source_lang, target_lang=target_lang, ...)
```
```python
# After
def run_article_mode(self, ..., learning_lang: str = 'English', native_lang: str = 'Chinese', ...):
    ...
    result = ParserService.parse_passage_with_vocab(..., source_lang=learning_lang, target_lang=native_lang, ...)
```
Do the same rename for all 5 methods. At this stage, keep the **keyword argument names** to `parser_service.py` as `source_lang=` and `target_lang=` — those will be fixed in the next step.

- [ ] **Step 2: Update `generate.py` keyword arg names to match new `main_processor.py` params**

In `generate.py`, the 4–5 processor call sites currently use `source_lang=validated_settings.learning_lang`. Now that `main_processor.py` parameters are renamed to `learning_lang`, update the call sites:

```python
# Before
source_lang=validated_settings.learning_lang,
target_lang=validated_settings.native_lang,
```
```python
# After
learning_lang=validated_settings.learning_lang,
native_lang=validated_settings.native_lang,
```

- [ ] **Step 3: Rename parameters in `parser_service.py` static methods**

All 5 static methods (`parse_passage_with_vocab`, `parse_vocab_txt`, `generate_vocab_ai`, `generate_grammar_ai`, `parse_grammar_txt`) have `source_lang`/`target_lang` parameters. Rename them and update internal usage.

Also update the `.format()` keyword argument names to match the new template placeholders (changed in Task 1):

```python
# Before
prompt = PROMPT_EN_PASSAGE_VOCAB_QUESTIONS.format(
    ...,
    source_language=source_lang,
    target_language=target_lang,
    ...
)
```
```python
# After
prompt = PROMPT_EN_PASSAGE_VOCAB_QUESTIONS.format(
    ...,
    learning_language=learning_lang,
    native_language=native_lang,
    ...
)
```
Apply the same `.format()` keyword arg change in all 5 places across `parser_service.py` (each static method that calls `.format()` on a prompt template).

Also update `gpt.to_json(...)` calls' keyword args:
```python
# Before
gpt.to_json(..., source_lang=source_lang, target_lang=target_lang, ...)
```
```python
# After
gpt.to_json(..., source_lang=learning_lang, target_lang=native_lang, ...)
```
(The `gpt.to_json` parameter names stay as-is unless they're renamed inside `gpt.py` — check first with `grep -n "source_lang\|target_lang" backend/libs/gpt.py`. If `gpt.py` uses those names as local params only and doesn't reference `config.py` constants, leave its parameter names unchanged and just pass the right values.)

Also update `main_processor.py` calls to `ParserService.*` to use new keyword names:
```python
# Before
ParserService.parse_passage_with_vocab(..., source_lang=learning_lang, target_lang=native_lang, ...)
```
```python
# After  
ParserService.parse_passage_with_vocab(..., learning_lang=learning_lang, native_lang=native_lang, ...)
```

- [ ] **Step 4: Verify no old identifiers remain in service layer**

```bash
grep -n "source_lang\|target_lang" backend/service/main_processor.py backend/service/parser_service.py
```
Expected: zero matches (only string literals in docstrings are acceptable if any remain).

- [ ] **Step 5: Commit**

```bash
git add backend/service/main_processor.py backend/service/parser_service.py backend/routes/generate.py
git commit -m "refactor: rename source_lang/target_lang to learning_lang/native_lang in service layer"
```

---

## Task 7: Frontend — Update types, App state, and SettingsModal

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/SettingsModal.tsx`

- [ ] **Step 1: Rename fields in `types.ts` Settings interface**

Current (lines 13–18):
```ts
export interface Settings {
  apiKey: string;
  model: string;
  language: string; // target language
  sourceLanguage: string; // source language
  audio: {
    enabled: boolean;
    voice: string;
  };
}
```
Replace with:
```ts
export interface Settings {
  apiKey: string;
  model: string;
  nativeLanguage: string;
  learningLanguage: string;
  audio: {
    enabled: boolean;
    voice: string;
  };
}
```

- [ ] **Step 2: Update initial state in `App.tsx`**

Current (lines 71–77):
```tsx
const [settings, setSettings] = useState<SettingsType>({
  apiKey: '',
  model: 'gpt-4o-mini',
  language: 'Chinese',
  sourceLanguage: 'English',
  audio: { enabled: false, voice: 'alloy' }
});
```
Replace with:
```tsx
const [settings, setSettings] = useState<SettingsType>({
  apiKey: '',
  model: 'gpt-4o-mini',
  nativeLanguage: 'Chinese',
  learningLanguage: 'English',
  audio: { enabled: false, voice: 'alloy' }
});
```

- [ ] **Step 3: Update the analyze API call in `App.tsx`**

Current (line 223):
```tsx
language: settings.language
```
Replace with:
```tsx
nativeLang: settings.nativeLanguage
```

- [ ] **Step 4: Update the generate API call body in `App.tsx`**

Current (lines 318–321):
```tsx
settings: {
  apiKey: settings.apiKey && !settings.apiKey.includes('***') ? settings.apiKey : '',
  model: settings.model,
  language: settings.language,
  sourceLang: settings.sourceLanguage,
  audio: settings.audio
}
```
Replace with:
```tsx
settings: {
  apiKey: settings.apiKey && !settings.apiKey.includes('***') ? settings.apiKey : '',
  model: settings.model,
  nativeLang: settings.nativeLanguage,
  learningLang: settings.learningLanguage,
  audio: settings.audio
}
```

- [ ] **Step 5: Update `SettingsModal.tsx` UI labels and bindings**

Current (lines 53–84):
```tsx
<div>
  <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">Source Language</div>
  <select 
    value={settings.sourceLanguage}
    onChange={(e) => setSettings({...settings, sourceLanguage: e.target.value})}
    ...
  >
    ...
  </select>
</div>
<div>
  <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">Target Language</div>
  <select 
    value={settings.language}
    onChange={(e) => setSettings({...settings, language: e.target.value})}
    ...
  >
    ...
  </select>
</div>
```
Replace with:
```tsx
<div>
  <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">學習語言</div>
  <select 
    value={settings.learningLanguage}
    onChange={(e) => setSettings({...settings, learningLanguage: e.target.value})}
    ...
  >
    ...
  </select>
</div>
<div>
  <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">母語</div>
  <select 
    value={settings.nativeLanguage}
    onChange={(e) => setSettings({...settings, nativeLanguage: e.target.value})}
    ...
  >
    ...
  </select>
</div>
```

- [ ] **Step 6: Verify no old field names remain in frontend**

```bash
grep -rn "sourceLanguage\|\.language\b\|'language'" frontend/src/
```
Expected: zero matches for `sourceLanguage`. The `settings.language` references should all be gone. (Unrelated uses of the word "language" in strings or comments are fine.)

- [ ] **Step 7: Commit**

```bash
git add frontend/src/types.ts frontend/src/App.tsx frontend/src/components/SettingsModal.tsx
git commit -m "refactor: rename language fields to learningLanguage/nativeLanguage in frontend"
```

---

## Task 8: Final Verification

- [ ] **Step 1: Run the full old-name grep across the whole codebase**

```bash
grep -rn \
  "source_lang\|target_lang\|sourceLanguage\|SOURCE_LANG\|TARGET_LANG\|source_language\|target_language" \
  backend/ frontend/src/ \
  --include="*.py" --include="*.ts" --include="*.tsx"
```
Expected: zero matches.

- [ ] **Step 2: Start the backend and check for import errors**

```bash
cd backend && python -c "from routes.dependencies import ValidatedSettings; from libs.config import LEARNING_LANG, NATIVE_LANG; print('OK')"
```
Expected output: `OK`

- [ ] **Step 3: Start the frontend TypeScript check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: zero type errors.

- [ ] **Step 4: Commit final verification note**

```bash
git commit --allow-empty -m "chore: verify language field rename complete — all old identifiers removed"
```
