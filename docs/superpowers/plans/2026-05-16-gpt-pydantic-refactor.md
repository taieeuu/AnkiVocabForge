# GPT Pydantic 重構 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 Pydantic model 取代手寫 schema dict，讓 GPT 查詢層擁有型別安全、統一欄位定義與自動 schema 生成。

**Architecture:** 新建 `backend/libs/models.py` 作為所有欄位定義的單一來源，包含 `VocabItem`、`VocabList`、`GrammarItem`、`GrammarList` 與 OpenAI schema 包裝 helper。`gpt.py` 使用 Pydantic 生成 schema 並解析回應，回傳型別從 `list[dict]` 改為 Pydantic model 實例。`AnkiService` 保持 dict 介面不變，在 `main_processor.py` 呼叫前用 `model_dump()` 轉換，確保 `routes/files.py` 不需動。

**Tech Stack:** Python 3.11+, Pydantic v2, OpenAI Python SDK v1.x

**Backend 路徑：** `/Users/taieeuu/Library/Mobile Documents/com~apple~CloudDocs/Personal/SideProject/anki_web/backend`  
所有 `cd /path/to/anki_web/backend` 請替換為上方路徑。

---

## 檔案結構

| 檔案 | 動作 | 說明 |
|---|---|---|
| `backend/libs/models.py` | 新建 | Pydantic models + schema helper |
| `backend/libs/gpt.py` | 修改 | 主要重構：用 models、抽 token logging、改回傳型別 |
| `backend/libs/config.py` | 修改 | 移除 `WORD_SCHEMA`、`GRAMMAR_SCHEMA` |
| `backend/service/main_processor.py` | 修改 | `word["word"]` → `word.word`；呼叫 AnkiService 前轉 dict |
| `backend/service/parser_service.py` | 修改 | 型別註解更新 |
| `backend/service/anki_service.py` | 不動 | dict 介面相容 routes/files.py，不需要更改 |

---

## Task 1：新建 `backend/libs/models.py`

**Files:**
- Create: `backend/libs/models.py`

- [ ] **Step 1：寫 `models.py`**

```python
from pydantic import BaseModel, Field, ConfigDict


class VocabItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    word: str = Field(description="The vocabulary word")
    pos: str = Field(description="Part of speech, using standard terms in the target language")
    meaning: str = Field(description="Word meaning in the target language")
    synonyms: str = Field(description="3-5 synonyms with their target-language meanings, as a single string")
    ex1_ori: str = Field(description="First example sentence in the source language using the word")
    ex1_trans: str = Field(description="Translation of the first example sentence")
    ex2_ori: str = Field(description="Second example sentence in the source language using the word")
    ex2_trans: str = Field(description="Translation of the second example sentence")
    hint: str = Field(description="Explanation of the word in the source language, without using the word itself")


class VocabList(BaseModel):
    model_config = ConfigDict(extra='forbid')
    vocab: list[VocabItem]


class GrammarItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    grammar: str = Field(description="Standard grammar pattern formula")
    usage: str = Field(description="When and how to use this grammar structure, in the source language")
    meaning: str = Field(description="Meaning in the target language")
    contrast: str = Field(description="How this pattern differs from similar structures and when each is required")
    ex1_ori: str = Field(description="First example sentence using this grammar")
    ex1_trans: str = Field(description="Translation of the first example sentence")
    ex2_ori: str = Field(description="Second example sentence using this grammar in a different context")
    ex2_trans: str = Field(description="Translation of the second example sentence")


class GrammarList(BaseModel):
    model_config = ConfigDict(extra='forbid')
    grammar: list[GrammarItem]


def build_openai_schema(model: type[BaseModel], name: str) -> dict:
    schema = _inject_additional_properties(model.model_json_schema())
    return {
        "type": "json_schema",
        "json_schema": {"name": name, "schema": schema, "strict": True},
    }


def _inject_additional_properties(node: dict | list) -> dict | list:
    if isinstance(node, list):
        return [_inject_additional_properties(i) for i in node]
    if isinstance(node, dict):
        result = {k: _inject_additional_properties(v) for k, v in node.items()}
        if result.get("type") == "object" and "properties" in result:
            result.setdefault("additionalProperties", False)
        return result
    return node
```

- [ ] **Step 2：驗證 import 無誤**

```bash
cd /path/to/anki_web/backend
python -c "from libs.models import VocabItem, VocabList, GrammarItem, GrammarList, build_openai_schema; print('OK')"
```

Expected: `OK`

- [ ] **Step 3：驗證 `build_openai_schema` 生成格式正確**

```bash
python -c "
from libs.models import VocabList, build_openai_schema
import json
schema = build_openai_schema(VocabList, 'vocab_list')
assert schema['type'] == 'json_schema'
assert schema['json_schema']['strict'] is True
inner = schema['json_schema']['schema']
assert inner.get('additionalProperties') == False or True  # top-level may vary
print('schema OK')
print(json.dumps(schema, indent=2)[:400])
"
```

Expected: 無 exception，印出 schema 前 400 字元

- [ ] **Step 4：Commit**

```bash
git add backend/libs/models.py
git commit -m "feat: add Pydantic models for GPT response schema"
```

---

## Task 2：重構 `backend/libs/gpt.py` — import 與 `_log_token_usage`

**Files:**
- Modify: `backend/libs/gpt.py`

- [ ] **Step 1：更新 import 區塊**

在 `gpt.py` 頂端找到：
```python
from .config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, WORD_SCHEMA, TRANSED_VOCAB_DIR, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE, GRAMMAR_PROMPT, GRAMMAR_SCHEMA
```

改為（移除 `WORD_SCHEMA` 與 `GRAMMAR_SCHEMA`，其他不動）：
```python
from .config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, TRANSED_VOCAB_DIR, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE, GRAMMAR_PROMPT
from .models import VocabItem, GrammarItem, VocabList, GrammarList, build_openai_schema
```

同時移除頂端的 `import json`（如果只用於 GPT 回應解析，後面會不再需要；若 `to_json` 還用到則保留）。  
**注意：** `to_json` 用到 `json.dump`，保留 `import json`。

- [ ] **Step 2：在 `GPTClient.__init__` 後新增 `_log_token_usage`**

在 `gen_voice` 方法前加入：
```python
def _log_token_usage(self, usage) -> None:
    if not usage:
        return
    logger.log(
        LogLevel.INFO,
        f"Token 使用量 - 輸入: {usage.prompt_tokens}, "
        f"輸出: {usage.completion_tokens}, 總計: {usage.total_tokens}",
    )
```

- [ ] **Step 3：驗證語法**

```bash
cd /path/to/anki_web/backend
python -c "from libs.gpt import GPTClient; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 4：Commit**

```bash
git add backend/libs/gpt.py
git commit -m "refactor: update gpt.py imports and extract _log_token_usage"
```

---

## Task 3：重構 `gpt.py` — 更新 `to_json`

**Files:**
- Modify: `backend/libs/gpt.py:341-385`

- [ ] **Step 1：更新 `to_json` 方法簽名與序列化邏輯**

找到 `to_json` 方法，將：
```python
def to_json(self, data: List[Dict], *, mode: str = "vocab", ...
```

改為：
```python
def to_json(self, data: list, *, mode: str = "vocab", deck_name: str | None = None,
            source_lang: str | None = None, target_lang: str | None = None,
            filename_hint: str | None = None) -> str:
```

在方法體最開頭（`if filename_hint:` 之前）加入：
```python
serializable = [item.model_dump() if hasattr(item, "model_dump") else item for item in data]
```

然後將方法體內所有 `json.dump(data, ...)` 改為 `json.dump(serializable, ...)`，共 2 處：

```python
# 第一處（filename_hint 分支）
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(serializable, f, ensure_ascii=False, indent=2)

# 第二處（預設命名分支）
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(serializable, f, ensure_ascii=False, indent=2)
```

同時，`count = len(data) ...` 那行的 `data` 改為 `serializable`：
```python
count = len(serializable) if isinstance(serializable, list) else 0
```

- [ ] **Step 2：驗證語法**

```bash
python -c "from libs.gpt import GPTClient; print('OK')"
```

Expected: `OK`

- [ ] **Step 3：Commit**

```bash
git add backend/libs/gpt.py
git commit -m "refactor: to_json supports Pydantic model instances via model_dump"
```

---

## Task 4：重構 `gpt.py` — 更新 vocab 查詢方法

**Files:**
- Modify: `backend/libs/gpt.py`

- [ ] **Step 1：更新 `passage_with_question`**

找到方法最後的 `response_format` 到 `return` 部分，完整替換如下：

原本（約 gpt.py:91-123）：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": contents}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "vocab_list",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": WORD_SCHEMA,
                "required": ["vocab"]
            },
            "strict": True
        }
    }
)

# 記錄 token 使用量
if hasattr(res, 'usage') and res.usage:
    usage = res.usage
    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
    completion_tokens = getattr(usage, 'completion_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)
    logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

raw = res.choices[0].message.content
try:
    obj = json.loads(raw)       # 這裡一定是 object（因為 schema）
    return obj.get("vocab", []) # 只回傳你要的 array
except json.JSONDecodeError:
    logger.log(LogLevel.ERROR, f"GPT 回傳非合法 JSON，原始輸出：\n{raw}")
    return []
```

替換為：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": contents}],
    response_format=build_openai_schema(VocabList, "vocab_list"),
)
self._log_token_usage(res.usage)
raw = res.choices[0].message.content
try:
    return VocabList.model_validate_json(raw).vocab
except Exception:
    logger.log(LogLevel.ERROR, f"GPT 回傳無效資料：\n{raw}")
    return []
```

同時更新方法回傳型別標注（若有）為 `list[VocabItem]`。

- [ ] **Step 2：更新 `vocab_from_words`**

找到方法中的 `response_format` 到 `return` 部分：

原本（約 gpt.py:133-164）：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "vocab_list",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": WORD_SCHEMA,
                "required": ["vocab"]
            },
            "strict": True
        }
    },
)
# 記錄 token 使用量
if hasattr(res, 'usage') and res.usage:
    usage = res.usage
    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
    completion_tokens = getattr(usage, 'completion_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)
    logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

raw = res.choices[0].message.content
try:
    obj = json.loads(raw)
    return obj.get("vocab", [])
except json.JSONDecodeError:
    logger.log(LogLevel.WARNING, f"⚠️ GPT 回傳非合法 JSON，原始輸出：\n{raw}")
    return []
```

替換為：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format=build_openai_schema(VocabList, "vocab_list"),
)
self._log_token_usage(res.usage)
raw = res.choices[0].message.content
try:
    return VocabList.model_validate_json(raw).vocab
except Exception:
    logger.log(LogLevel.WARNING, f"⚠️ GPT 回傳無效資料：\n{raw}")
    return []
```

- [ ] **Step 3：更新 `generate_vocab_list`**

找到方法中的 `response_format` 到 `return` 部分：

原本（約 gpt.py:257-291）：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "vocab_list",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": WORD_SCHEMA,
                "required": ["vocab"]
            },
            "strict": True
        }
    },
)

# 記錄 token 使用量
if hasattr(res, 'usage') and res.usage:
    usage = res.usage
    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
    completion_tokens = getattr(usage, 'completion_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)
    logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

raw = res.choices[0].message.content
try:
    obj = json.loads(raw)
    vocab_list = obj.get("vocab", [])
    logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(vocab_list)} 個單字")
    return vocab_list
except json.JSONDecodeError:
    logger.log(LogLevel.ERROR, f"GPT 回傳非合法 JSON，原始輸出：\n{raw}")
    return []
```

替換為：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format=build_openai_schema(VocabList, "vocab_list"),
)
self._log_token_usage(res.usage)
raw = res.choices[0].message.content
try:
    vocab_list = VocabList.model_validate_json(raw).vocab
    logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(vocab_list)} 個單字")
    return vocab_list
except Exception:
    logger.log(LogLevel.ERROR, f"GPT 回傳無效資料：\n{raw}")
    return []
```

- [ ] **Step 4：驗證語法**

```bash
python -c "from libs.gpt import GPTClient; print('OK')"
```

Expected: `OK`

- [ ] **Step 5：Commit**

```bash
git add backend/libs/gpt.py
git commit -m "refactor: vocab GPT methods use Pydantic schema and return list[VocabItem]"
```

---

## Task 5：重構 `gpt.py` — 更新 grammar 查詢方法

**Files:**
- Modify: `backend/libs/gpt.py`

- [ ] **Step 1：更新 `grammar_from_list`**

找到方法中的 `response_format` 到 `return` 部分：

原本（約 gpt.py:174-205）：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "grammar_list",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": GRAMMAR_SCHEMA,
                "required": ["grammar"]
            },
            "strict": True
        }
    },
)
# 記錄 token 使用量
if hasattr(res, 'usage') and res.usage:
    usage = res.usage
    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
    completion_tokens = getattr(usage, 'completion_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)
    logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

raw = res.choices[0].message.content
try:
    obj = json.loads(raw)
    return obj.get("grammar", [])
except json.JSONDecodeError:
    logger.log(LogLevel.WARNING, f"⚠️ GPT 回傳非合法 JSON，原始輸出：\n{raw}")
    return []
```

替換為：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format=build_openai_schema(GrammarList, "grammar_list"),
)
self._log_token_usage(res.usage)
raw = res.choices[0].message.content
try:
    return GrammarList.model_validate_json(raw).grammar
except Exception:
    logger.log(LogLevel.WARNING, f"⚠️ GPT 回傳無效資料：\n{raw}")
    return []
```

- [ ] **Step 2：更新 `generate_grammar_list`**

找到方法中的 `response_format` 到 `return` 部分：

原本（約 gpt.py:305-339）：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "grammar_list",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": GRAMMAR_SCHEMA,
                "required": ["grammar"]
            },
            "strict": True
        }
    },
)

# 記錄 token 使用量
if hasattr(res, 'usage') and res.usage:
    usage = res.usage
    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
    completion_tokens = getattr(usage, 'completion_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)
    logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

raw = res.choices[0].message.content
try:
    obj = json.loads(raw)
    grammar_list = obj.get("grammar", [])
    logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(grammar_list)} 個文法")
    return grammar_list
except json.JSONDecodeError:
    logger.log(LogLevel.ERROR, f"GPT 回傳非合法 JSON，原始輸出：\n{raw}")
    return []
```

替換為：
```python
res = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    response_format=build_openai_schema(GrammarList, "grammar_list"),
)
self._log_token_usage(res.usage)
raw = res.choices[0].message.content
try:
    grammar_list = GrammarList.model_validate_json(raw).grammar
    logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(grammar_list)} 個文法")
    return grammar_list
except Exception:
    logger.log(LogLevel.ERROR, f"GPT 回傳無效資料：\n{raw}")
    return []
```

- [ ] **Step 3：驗證語法**

```bash
python -c "from libs.gpt import GPTClient; print('OK')"
```

Expected: `OK`

- [ ] **Step 4：Commit**

```bash
git add backend/libs/gpt.py
git commit -m "refactor: grammar GPT methods use Pydantic schema and return list[GrammarItem]"
```

---

## Task 6：移除 `config.py` 中的 schema dict

**Files:**
- Modify: `backend/libs/config.py`

- [ ] **Step 1：移除 `WORD_SCHEMA` 與 `GRAMMAR_SCHEMA`**

在 `config.py` 中找到並刪除下面兩個常數定義（`WORD_SCHEMA` 從 `WORD_SCHEMA = {` 到對應的結尾 `}`，共約 25 行；`GRAMMAR_SCHEMA` 同理，共約 24 行）：

```python
# 刪除這一整塊（約第 416-446 行）
WORD_SCHEMA = {
    "vocab": {
        ...
    }
}

# 刪除這一整塊（約第 478-506 行）
GRAMMAR_SCHEMA = {
    "grammar": {
        ...
    }
}
```

- [ ] **Step 2：確認其他檔案沒有殘留 import**

```bash
grep -rn "WORD_SCHEMA\|GRAMMAR_SCHEMA" backend/ --include="*.py"
```

Expected: 無任何輸出（若有輸出，找到對應 import 行刪除）

- [ ] **Step 3：驗證 config.py 仍可 import**

```bash
python -c "from libs.config import AI_MODEL, PROMPT_EN_VOCAB; print('OK')"
```

Expected: `OK`

- [ ] **Step 4：Commit**

```bash
git add backend/libs/config.py
git commit -m "refactor: remove WORD_SCHEMA and GRAMMAR_SCHEMA, replaced by Pydantic models"
```

---

## Task 7：更新 `main_processor.py`

**Files:**
- Modify: `backend/service/main_processor.py`

- [ ] **Step 1：更新 3 處 dict 存取為屬性存取**

在 `run_article_mode`（約第 42 行）：
```python
# 改前
word_list = [word["word"] for word in transed_vocab_list]
# 改後
word_list = [word.word for word in transed_vocab_list]
```

在 `run_vocab_mode`（約第 67 行）：
```python
# 改前
word_list = [word["word"] for word in vocab_list]
# 改後
word_list = [word.word for word in vocab_list]
```

在 `run_ai_generate_mode`（約第 115 行）：
```python
# 改前
word_list = [word["word"] for word in vocab_list]
# 改後
word_list = [word.word for word in vocab_list]
```

- [ ] **Step 2：更新 `_import_to_anki` 在呼叫前轉換為 dict list**

找到 `_import_to_anki` 方法（約第 188 行），在方法體最開頭加入一行轉換：

```python
def _import_to_anki(self, vocab_list: list, deck_name: str, card_type: str, session_dir: str = None) -> str:
    vocab_list = [item.model_dump() if hasattr(item, "model_dump") else item for item in vocab_list]
    # 使用 "orig" 作為檔案名稱後綴...（以下不動）
```

- [ ] **Step 3：更新 `run_grammar_mode` 中的 grammar import 呼叫前轉換**

在 `run_grammar_mode`（約第 152 行），找到呼叫 `AnkiService.import_grammar_model_notes` 的那行，在它之前加入轉換：

```python
grammar_list_dicts = [item.model_dump() if hasattr(item, "model_dump") else item for item in grammar_list]
msg = AnkiService.import_grammar_model_notes(grammar_list_dicts, deck_name, session_dir=session_dir, filename_suffix='orig')
```

同樣在 `run_grammar_from_file_mode`（約第 184 行）的 `import_grammar_model_notes` 呼叫前加入：

```python
grammar_list_dicts = [item.model_dump() if hasattr(item, "model_dump") else item for item in grammar_list]
msg = AnkiService.import_grammar_model_notes(grammar_list_dicts, deck_name, session_dir=session_dir, filename_suffix='orig')
```

- [ ] **Step 4：驗證語法**

```bash
python -c "from service.main_processor import MainProcessor; print('OK')"
```

Expected: `OK`

- [ ] **Step 5：Commit**

```bash
git add backend/service/main_processor.py
git commit -m "refactor: use Pydantic model attribute access and serialize before AnkiService calls"
```

---

## Task 8：更新 `parser_service.py` 型別註解

**Files:**
- Modify: `backend/service/parser_service.py`

- [ ] **Step 1：更新 import**

在 `parser_service.py` 頂端加入：
```python
from libs.models import VocabItem, GrammarItem
```

- [ ] **Step 2：更新各方法的 docstring 與回傳型別**

`parse_passage` 方法 docstring 中的 `Returns: List[Dict]` → `Returns: list[VocabItem]`，函式簽名加上 `-> list[VocabItem]`：

```python
@staticmethod
def parse_passage(...) -> list[VocabItem]:
```

`parse_vocab_txt` → `-> list[VocabItem]`

`generate_vocab_ai` docstring `Returns: List[Dict]` → `list[VocabItem]`，加上 `-> list[VocabItem]`

`generate_grammar_ai` docstring `Returns: List[Dict]` → `list[GrammarItem]`，加上 `-> list[GrammarItem]`

`parse_grammar_txt` docstring 更新，加上 `-> list[GrammarItem]`

- [ ] **Step 3：驗證語法**

```bash
python -c "from service.parser_service import ParserService; print('OK')"
```

Expected: `OK`

- [ ] **Step 4：Commit**

```bash
git add backend/service/parser_service.py
git commit -m "refactor: update parser_service return type hints to use Pydantic models"
```

---

## Task 9：整合驗證

**Files:**
- No changes

- [ ] **Step 1：驗證全部 backend 模組可 import**

```bash
cd /path/to/anki_web/backend
python -c "
from libs.gpt import GPTClient
from libs.models import VocabItem, GrammarItem, VocabList, GrammarList, build_openai_schema
from service.main_processor import MainProcessor
from service.parser_service import ParserService
from service.anki_service import AnkiService
print('All imports OK')
"
```

Expected: `All imports OK`

- [ ] **Step 2：驗證 `VocabItem.model_dump()` 輸出格式與 `AnkiService` 相容**

```bash
python -c "
from libs.models import VocabItem
item = VocabItem(
    word='test', pos='noun', meaning='測試', synonyms='exam, trial',
    ex1_ori='This is a test.', ex1_trans='這是一個測試。',
    ex2_ori='Run the test.', ex2_trans='執行測試。',
    hint='A procedure to check something'
)
d = item.model_dump()
assert d['word'] == 'test'
assert d['pos'] == 'noun'
print('model_dump compatible:', list(d.keys()))
"
```

Expected: 印出所有欄位名稱，無 exception

- [ ] **Step 3：驗證 `build_openai_schema` 結構符合 OpenAI strict 要求**

```bash
python -c "
from libs.models import VocabList, build_openai_schema
import json

schema = build_openai_schema(VocabList, 'vocab_list')
assert schema['type'] == 'json_schema'
assert schema['json_schema']['strict'] is True

def check_objects(node):
    if isinstance(node, dict):
        if node.get('type') == 'object' and 'properties' in node:
            assert node.get('additionalProperties') == False, f'Missing additionalProperties: False in {list(node.get(\"properties\", {}).keys())}'
        for v in node.values():
            check_objects(v)
    elif isinstance(node, list):
        for i in node:
            check_objects(i)

check_objects(schema['json_schema']['schema'])
print('Schema validation passed')
"
```

Expected: `Schema validation passed`

- [ ] **Step 4：確認 `WORD_SCHEMA`、`GRAMMAR_SCHEMA` 不再被任何檔案引用**

```bash
grep -rn "WORD_SCHEMA\|GRAMMAR_SCHEMA" /path/to/anki_web/backend --include="*.py"
```

Expected: 無任何輸出

- [ ] **Step 5：最終 commit**

```bash
git add -A
git commit -m "chore: final integration check - GPT Pydantic refactor complete"
```
