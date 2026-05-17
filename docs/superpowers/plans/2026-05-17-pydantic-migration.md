# Pydantic Migration 實作計畫

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 將 `gpt.py` 中 5 個方法的 GPT 回應解析，從手動 JSON schema dict + `json.loads()` 改為 Pydantic BaseModel + `client.beta.chat.completions.parse()`。

**Architecture:** 新增 `backend/libs/schemas.py` 定義 Pydantic 模型，`gpt.py` 改用 `.parse()` API 並在方法內部做 `.model_dump()` 轉換，維持對下游 `parser_service.py` 的 `list[dict]` 介面不變。刪除 `config.py` 中的 `WORD_SCHEMA` 與 `GRAMMAR_SCHEMA`。

**Tech Stack:** Python 3.10+, Pydantic v2, `openai` SDK (`client.beta.chat.completions.parse`)

---

## 異動檔案總覽

| 檔案 | 異動類型 | 說明 |
|------|---------|------|
| `backend/libs/schemas.py` | 新增 | VocabCard、VocabResponse、GrammarCard、GrammarResponse |
| `backend/libs/gpt.py` | 修改 | import 調整 + 5 個方法改用 `.parse()` |
| `backend/libs/config.py` | 修改 | 刪除 WORD_SCHEMA（第 478–508 行）與 GRAMMAR_SCHEMA（第 540–568 行） |
| `backend/service/parser_service.py` | 不需改動 | gpt.py 方法仍回傳 `list[dict]`，介面不變 |

---

## Task 1：新增 `backend/libs/schemas.py`

**Files:**
- Create: `backend/libs/schemas.py`

- [ ] **Step 1：建立 schemas.py**

```python
from pydantic import BaseModel, Field


class VocabCard(BaseModel):
    word:      str = Field(description="The vocabulary word")
    pos:       str = Field(description="Part of speech in target language (e.g. n., v., adj.)")
    meaning:   str = Field(description="Meaning of the word in target language")
    synonyms:  str = Field(description="3-5 synonyms with target language translations, as a single string")
    ex1_ori:   str = Field(description="First example sentence in source language")
    ex1_trans: str = Field(description="Translation of first example sentence")
    ex2_ori:   str = Field(description="Second example sentence in source language")
    ex2_trans: str = Field(description="Translation of second example sentence")
    hint:      str = Field(description="Explanation without using the word itself, in source language")


class VocabResponse(BaseModel):
    vocab: list[VocabCard]


class GrammarCard(BaseModel):
    grammar:   str = Field(description="Grammar pattern or rule title")
    usage:     str = Field(description="When and conditions to use this grammar, in source language")
    meaning:   str = Field(description="Meaning or explanation in target language")
    contrast:  str = Field(description="Comparison with similar grammar, explaining when to choose each")
    ex1_ori:   str = Field(description="First example sentence in source language")
    ex1_trans: str = Field(description="Translation of first example sentence")
    ex2_ori:   str = Field(description="Second example sentence in source language")
    ex2_trans: str = Field(description="Translation of second example sentence")


class GrammarResponse(BaseModel):
    grammar: list[GrammarCard]
```

- [ ] **Step 2：確認檔案存在**

```bash
ls backend/libs/schemas.py
```
Expected: 顯示檔案路徑，無錯誤。

- [ ] **Step 3：確認 import 正常**

```bash
cd backend && python -c "from libs.schemas import VocabResponse, GrammarResponse; print('OK')"
```
Expected: `OK`

- [ ] **Step 4：Commit**

```bash
git add backend/libs/schemas.py
git commit -m "feat: add Pydantic schemas for GPT structured output"
```

---

## Task 2：更新 `backend/libs/gpt.py` — 新增 schemas import

**Files:**
- Modify: `backend/libs/gpt.py:7`

目前第 7 行：
```python
from .config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, WORD_SCHEMA, TRANSED_VOCAB_DIR, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE, GRAMMAR_PROMPT, GRAMMAR_SCHEMA
```

- [ ] **Step 1：在第 7 行下方新增 schemas import（此步驟只新增，不移除舊 import）**

在第 7 行下方新增一行：
```python
from .schemas import VocabResponse, GrammarResponse
```

注意：`WORD_SCHEMA` 與 `GRAMMAR_SCHEMA` 的 import 在 Task 8 才移除，避免在方法尚未更新時出現 NameError。

- [ ] **Step 2：確認 import 正常**

```bash
cd backend && python -c "from libs.gpt import GPTClient; print('OK')"
```
Expected: `OK`

---

## Task 3：更新 `passage_with_question` 方法（`gpt.py:91–123`）

**Files:**
- Modify: `backend/libs/gpt.py:91-123`

- [ ] **Step 1：將 response_format dict + json.loads 替換為 .parse()**

將方法中的 API 呼叫與解析區塊（目前第 91–123 行）替換為：

```python
        res = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": contents}],
            response_format=VocabResponse,
        )

        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

        parsed = res.choices[0].message.parsed
        if parsed is None:
            logger.log(LogLevel.ERROR, "GPT 回傳解析失敗")
            return []
        return [card.model_dump() for card in parsed.vocab]
```

---

## Task 4：更新 `vocab_from_words` 方法（`gpt.py:133–164`）

**Files:**
- Modify: `backend/libs/gpt.py:133-164`

- [ ] **Step 1：替換 API 呼叫與解析**

將方法中的 API 呼叫與解析區塊替換為：

```python
        res = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format=VocabResponse,
        )
        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

        parsed = res.choices[0].message.parsed
        if parsed is None:
            logger.log(LogLevel.WARNING, "⚠️ GPT 回傳解析失敗")
            return []
        return [card.model_dump() for card in parsed.vocab]
```

---

## Task 5：更新 `grammar_from_list` 方法（`gpt.py:174–205`）

**Files:**
- Modify: `backend/libs/gpt.py:174-205`

- [ ] **Step 1：替換 API 呼叫與解析（改用 GrammarResponse）**

將方法中的 API 呼叫與解析區塊替換為：

```python
        res = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format=GrammarResponse,
        )
        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

        parsed = res.choices[0].message.parsed
        if parsed is None:
            logger.log(LogLevel.WARNING, "⚠️ GPT 回傳解析失敗")
            return []
        return [card.model_dump() for card in parsed.grammar]
```

---

## Task 6：更新 `generate_vocab_list` 方法（`gpt.py:257–291`）

**Files:**
- Modify: `backend/libs/gpt.py:257-291`

- [ ] **Step 1：替換 API 呼叫與解析**

將方法中的 API 呼叫與解析區塊替換為：

```python
        res = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format=VocabResponse,
        )

        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

        parsed = res.choices[0].message.parsed
        if parsed is None:
            logger.log(LogLevel.ERROR, "GPT 回傳解析失敗")
            return []
        vocab_list = [card.model_dump() for card in parsed.vocab]
        logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(vocab_list)} 個單字")
        return vocab_list
```

---

## Task 7：更新 `generate_grammar_list` 方法（`gpt.py:305–339`）

**Files:**
- Modify: `backend/libs/gpt.py:305-339`

- [ ] **Step 1：替換 API 呼叫與解析（改用 GrammarResponse）**

將方法中的 API 呼叫與解析區塊替換為：

```python
        res = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format=GrammarResponse,
        )

        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")

        parsed = res.choices[0].message.parsed
        if parsed is None:
            logger.log(LogLevel.ERROR, "GPT 回傳解析失敗")
            return []
        grammar_list = [card.model_dump() for card in parsed.grammar]
        logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(grammar_list)} 個文法")
        return grammar_list
```

- [ ] **Step 2：確認 gpt.py import 與語法正常**

```bash
cd backend && python -c "from libs.gpt import GPTClient; print('OK')"
```
Expected: `OK`

- [ ] **Step 3：Commit Tasks 2–7**

```bash
git add backend/libs/gpt.py
git commit -m "refactor: migrate gpt.py to Pydantic structured output parsing"
```

---

## Task 8：清理舊 schema 常數

**Files:**
- Modify: `backend/libs/gpt.py:7`
- Modify: `backend/libs/config.py:478-568`

此時 5 個方法已全部更新完畢，可以安全移除 WORD_SCHEMA / GRAMMAR_SCHEMA。

- [ ] **Step 1：從 gpt.py 的 config import 移除 WORD_SCHEMA 與 GRAMMAR_SCHEMA**

將 `gpt.py` 第 7 行改為：
```python
from .config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, TRANSED_VOCAB_DIR, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE, GRAMMAR_PROMPT
```

- [ ] **Step 2：刪除 config.py 中的 WORD_SCHEMA 與 GRAMMAR_SCHEMA**

刪除 `config.py` 第 478–508 行（`WORD_SCHEMA = { ... }` 整段）與第 540–568 行（`GRAMMAR_SCHEMA = { ... }` 整段）。

- [ ] **Step 3：確認無殘留引用**

```bash
cd backend && grep -rn "WORD_SCHEMA\|GRAMMAR_SCHEMA" .
```
Expected: 無輸出（零個引用）

- [ ] **Step 4：確認整體 import 正常**

```bash
cd backend && python -c "from libs.config import GRAMMAR_PROMPT; from libs.gpt import GPTClient; print('OK')"
```
Expected: `OK`

- [ ] **Step 5：Commit**

```bash
git add backend/libs/gpt.py backend/libs/config.py
git commit -m "chore: remove WORD_SCHEMA and GRAMMAR_SCHEMA from config"
```

---

## Task 9：手動驗證

- [ ] **Step 1：啟動後端**

```bash
cd backend && uvicorn main:app --reload
```

- [ ] **Step 2：觸發一次單字生成請求**

在前端點選「AI 生成」並選擇 Word 模式，觸發 generate 請求。
確認：後端 log 出現 `✅ 成功生成 N 個單字`，前端卡片預覽正常顯示。

- [ ] **Step 3：觸發一次文法生成請求**

在前端選擇 Grammar 模式觸發 generate 請求。
確認：後端 log 出現 `✅ 成功生成 N 個文法`，前端卡片預覽正常顯示。
