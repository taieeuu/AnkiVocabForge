# Pydantic 遷移設計文件

**日期：** 2026-05-17  
**狀態：** 已確認  
**範圍：** 將 GPT 結構化輸出的 JSON schema dict 替換為 Pydantic 模型

---

## 問題描述

`backend/libs/gpt.py` 目前使用 `config.py` 中的 raw Python dict（`WORD_SCHEMA`、`GRAMMAR_SCHEMA`）定義 GPT 回應 schema，並透過 `json.loads()` + `.get("vocab", [])` 手動解析結果。這種做法有以下缺點：

- 欄位定義與欄位描述分散在不同地方
- 對 GPT 回應沒有型別驗證
- 下游程式碼依賴容易出錯的 dict 存取方式

---

## 目標

改用 Pydantic `BaseModel` 搭配 `client.beta.chat.completions.parse()`（OpenAI 結構化輸出），達到：

1. 欄位定義與 GPT prompt 描述集中在同一個地方
2. 從 GPT 取得有型別、經過驗證的回應物件
3. 移除手動建構 JSON schema 與 `json.loads()` 解析的程式碼

---

## 採用方案

**方案 A：Pydantic + `client.beta.chat.completions.parse()`**

使用 OpenAI structured outputs API，以 Pydantic 模型作為 `response_format`。SDK 會自動從 Pydantic 模型產生 JSON schema，並回傳完整解析、有型別的物件。

---

## 新增檔案：`backend/libs/schemas.py`

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

---

## 各檔案異動範圍

| 檔案 | 異動內容 |
|------|--------|
| `backend/libs/schemas.py` | **新增** — VocabCard、VocabResponse、GrammarCard、GrammarResponse Pydantic 模型 |
| `backend/libs/gpt.py` | **修改** — 5 個方法：將 `response_format` dict + `json.loads()` 替換為 `parse()` + Pydantic |
| `backend/service/parser_service.py` | **修改** — 5 個呼叫點：加上 `.model_dump()` 將 Pydantic 物件轉回 dict 供下游使用 |
| `backend/libs/config.py` | **修改** — 刪除 `WORD_SCHEMA` 與 `GRAMMAR_SCHEMA` 常數 |
| 其餘所有檔案 | 不需修改 |

---

## 資料流

**修改前：**
```
gpt.py 手動建構 dict schema → OpenAI API (json_schema 模式) → json.loads() → list[dict]
parser_service.py → item["word"] 等 dict 存取
```

**修改後：**
```
gpt.py 使用 Pydantic 模型 → OpenAI API (.parse()) → VocabResponse / GrammarResponse 物件
→ .model_dump() → list[dict]  （對下游介面保持不變）
parser_service.py → item["word"] 等 dict 存取  （不需改動）
```

---

## 關鍵限制

下游程式碼（`parser_service.py`、`main_processor.py`）以 dict 方式存取卡片（`item["word"]`、`word["meaning"]` 等）。在 `parser_service.py` 的 5 個呼叫點加上 `.model_dump()` 即可保持此介面，不需修改下游任何程式碼。

---

## 錯誤處理

`client.beta.chat.completions.parse()` 在回應被截斷時會拋出 `openai.LengthFinishReasonError`。`gpt.py` 中現有的 try/except 已能捕捉一般例外，無需額外的錯誤處理。

---

## 測試

- 手動觸發單字（vocab）generate 請求，確認卡片正確回傳
- 手動觸發文法（grammar）generate 請求，確認文法卡片正確回傳
- 確認前端卡片預覽在遷移後仍正常運作
