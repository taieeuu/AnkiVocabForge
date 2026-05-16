# GPT 查詢層 Pydantic 重構設計

**日期：** 2026-05-16  
**範圍：** `backend/libs/gpt.py` 及下游呼叫端  
**目標：** 用 Pydantic model 取代手寫 schema dict，統一欄位定義、型別驗證與 GPT 回應解析

---

## 背景與問題

目前 `gpt.py` 的四個 GPT 查詢方法（`vocab_from_words`、`passage_with_question`、`generate_vocab_list`、`generate_grammar_list`）存在以下問題：

1. **欄位定義分散：** `WORD_SCHEMA`/`GRAMMAR_SCHEMA` dict 在 `config.py` 定義型別，欄位語意描述散落在各 prompt 字串中，沒有單一來源。
2. **無型別安全：** GPT 回應以 `json.loads()` 解析為 `dict`，回傳 `List[Dict]`，欄位存取無任何型別保護。
3. **重複邏輯：** Token logging（約 6 行）在四個方法中完全重複。
4. **Schema 維護困難：** OpenAI `response_format` 的 schema 需要手動與 `config.py` 的 dict 保持同步。

---

## 設計決策

- **Pydantic 範疇：** 同時用於生成 OpenAI JSON Schema（取代 schema dict）與解析 GPT 回應
- **模型位置：** 新建 `backend/libs/models.py`，集中管理所有 Pydantic model
- **回傳型別：** GPT 方法改為回傳 `list[VocabItem]` / `list[GrammarItem]`，下游一並更新
- **欄位說明：** 使用 `Field(description=...)` 讓 model 成為欄位的單一來源（型別 + 語意）

---

## 新增：`backend/libs/models.py`

定義四個 Pydantic model 與一個 schema helper：

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
    return {"type": "json_schema", "json_schema": {"name": name, "schema": schema, "strict": True}}

def _inject_additional_properties(node):
    if isinstance(node, list):
        return [_inject_additional_properties(i) for i in node]
    if isinstance(node, dict):
        result = {k: _inject_additional_properties(v) for k, v in node.items()}
        if result.get("type") == "object" and "properties" in result:
            result.setdefault("additionalProperties", False)
        return result
    return node
```

**設計說明：**
- `extra='forbid'` 確保 Pydantic model 不接受未定義欄位，行為等同於原本的 `additionalProperties: False`
- `_inject_additional_properties` 遞迴補齊 OpenAI strict 模式要求的 `additionalProperties: False`（Pydantic `model_json_schema()` 可能在巢狀 `$defs` 裡漏補）
- `build_openai_schema` 是統一的 schema 包裝 helper，取代每個方法裡手寫的 `response_format` dict

---

## 修改：`backend/libs/gpt.py`

### 1. Import 更新

```python
# 新增
from .models import VocabItem, GrammarItem, VocabList, GrammarList, build_openai_schema
# 移除
# from .config import WORD_SCHEMA, GRAMMAR_SCHEMA（從 import 列表移除）
```

### 2. 新增 `_log_token_usage` private method

抽取四個方法的重複 token logging：

```python
def _log_token_usage(self, usage) -> None:
    if not usage:
        return
    logger.log(LogLevel.INFO,
        f"Token 使用量 - 輸入: {usage.prompt_tokens}, "
        f"輸出: {usage.completion_tokens}, 總計: {usage.total_tokens}")
```

### 3. 各方法的改動模式

**改前：**
```python
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
# ... token logging 6 行 ...
raw = res.choices[0].message.content
obj = json.loads(raw)
return obj.get("vocab", [])
```

**改後：**
```python
response_format=build_openai_schema(VocabList, "vocab_list")
# ... self._log_token_usage(res.usage) ...
raw = res.choices[0].message.content
return VocabList.model_validate_json(raw).vocab
```

Grammar 方法同理，使用 `build_openai_schema(GrammarList, "grammar_list")` 與 `GrammarList.model_validate_json(raw).grammar`。

**錯誤處理：** 原本 catch `json.JSONDecodeError` 並回傳 `[]`。改為 catch `pydantic.ValidationError`（含 JSON 解析失敗），同樣記 log 並回傳 `[]`，行為與原本一致。

### 4. 回傳型別變更

| 方法 | 改前 | 改後 |
|---|---|---|
| `passage_with_question` | `list[dict]` | `list[VocabItem]` |
| `vocab_from_words` | `list[dict]` | `list[VocabItem]` |
| `generate_vocab_list` | `list[dict]` | `list[VocabItem]` |
| `grammar_from_list` | `list[dict]` | `list[GrammarItem]` |
| `generate_grammar_list` | `list[dict]` | `list[GrammarItem]` |

### 5. `to_json()` 支援 Pydantic model

```python
def to_json(self, data: list[VocabItem | GrammarItem | dict], ...) -> str:
    serializable = [
        item.model_dump() if hasattr(item, "model_dump") else item
        for item in data
    ]
    json.dump(serializable, f, ...)
```

---

## 修改：`backend/libs/config.py`

移除以下常數（完全由 `models.py` 取代）：
- `WORD_SCHEMA`
- `GRAMMAR_SCHEMA`

---

## 修改：`backend/service/main_processor.py`

3 處 dict 存取改為屬性存取：

```python
# 改前
word_list = [word["word"] for word in transed_vocab_list]

# 改後
word_list = [word.word for word in transed_vocab_list]
```

---

## 修改：`backend/service/anki_service.py`

所有 `v.get("field")` 改為屬性存取，型別簽名更新：

```python
# 改前
def import_basic_model_notes(vocab_list: list[dict], ...) -> str:
    word = v.get("word") or ""
    pos = v.get("pos") or ""
    ...

# 改後
def import_basic_model_notes(vocab_list: list[VocabItem], ...) -> str:
    word = v.word
    pos = v.pos
    ...
```

涉及方法：
- `import_basic_model_notes`（VocabItem）
- `import_cloze_model_notes`（VocabItem）
- `import_basic_and_cloze_notes`（VocabItem）
- `confirm_and_pack_basic_model`（VocabItem）
- `confirm_and_pack_cloze_model`（VocabItem）
- `confirm_and_pack_basic_and_cloze`（VocabItem）
- `import_grammar_model_notes`（GrammarItem）

---

## 修改：`backend/service/parser_service.py`

型別註解更新（`list[dict]` → `list[VocabItem]` / `list[GrammarItem]`）。邏輯無需改動。

---

## 變更摘要

| 檔案 | 類型 |
|---|---|
| `backend/libs/models.py` | 新增 |
| `backend/libs/gpt.py` | 修改（主要）|
| `backend/libs/config.py` | 修改（移除 2 個常數）|
| `backend/service/main_processor.py` | 修改（3 處）|
| `backend/service/anki_service.py` | 修改（7 個方法）|
| `backend/service/parser_service.py` | 修改（型別註解）|
