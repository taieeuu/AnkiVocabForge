# 語言欄位重命名設計文件

**日期：** 2026-05-17  
**範圍：** 全 stack — frontend types、UI 標籤、backend 變數、常數、prompt 模板

---

## 背景

現行程式碼以翻譯領域的術語命名語言欄位（source/target language），但從語言學習者的視角來看，這些名稱並不直覺。此次重命名將改為以學習者為中心的命名：「學習語言」與「母語」。

此外，現有命名本身也有不一致之處（frontend type 中 `language` 而非 `targetLanguage`），本次一併修正。

---

## 命名對照表

| 語意 | 舊命名 | 新命名 |
|---|---|---|
| 正在學習的語言 | source language / `sourceLanguage` / `source_lang` / `SOURCE_LANG` | 學習語言 / `learningLanguage` / `learning_lang` / `LEARNING_LANG` |
| 母語（用於解釋/翻譯） | target language / `language` / `target_lang` / `TARGET_LANG` | 母語 / `nativeLanguage` / `native_lang` / `NATIVE_LANG` |

---

## 各層面改動

### Frontend — `frontend/src/types.ts`

```ts
// 前
sourceLanguage: string; // source language
language: string;       // target language

// 後
learningLanguage: string;
nativeLanguage: string;
```

### Frontend — `frontend/src/App.tsx`

- 初始值：`sourceLanguage: 'English'` → `learningLanguage: 'English'`
- 初始值：`language: 'Chinese'` → `nativeLanguage: 'Chinese'`
- API 請求 key：`sourceLang: settings.sourceLanguage` → `learningLang: settings.learningLanguage`
- API 請求 key：`language: settings.language` → `nativeLang: settings.nativeLanguage`

### Frontend — `frontend/src/components/SettingsModal.tsx`

- UI 標籤：`"Source Language"` → `"學習語言"`
- UI 標籤：`"Target Language"` → `"母語"`
- 綁定欄位：`sourceLanguage` → `learningLanguage`，`language` → `nativeLanguage`

### Backend — `backend/libs/config.py`

- 常數：`SOURCE_LANG` → `LEARNING_LANG`，`TARGET_LANG` → `NATIVE_LANG`
- Prompt 模板變數：`{source_language}` → `{learning_language}`，`{target_language}` → `{native_language}`

### Backend — `backend/routes/settings.py`

- import 常數更名
- API 回傳 key：`'sourceLang'` → `'learningLang'`

### Backend — `backend/routes/dependencies.py`

- `ValidatedSettings` 欄位：`source_lang` / `target_lang` → `learning_lang` / `native_lang`
- lookup keys（新）：`'learningLang'`, `'learningLanguage'`, `'learning_language'`
- lookup keys（新）：`'nativeLang'`, `'nativeLanguage'`, `'native_language'`
- 移除舊的 source/target lookup keys

### Backend — `backend/routes/generate_helpers.py`

- `get_language_settings()` 的 lookup keys 同 dependencies.py
- 回傳值命名更新

### Backend — `backend/libs/schemas.py`

- Field description 中「來源語言」→「學習語言」，「目標語言」→「母語」

### Backend — `backend/service/parser_service.py`

- 呼叫 `ValidatedSettings` 欄位時由 `source_lang`/`target_lang` → `learning_lang`/`native_lang`

---

## 不在本次範圍

- `.env` / `.env.example` 中的 `SOURCE_LANG` / `TARGET_LANG` 環境變數名稱（保持不變，config.py 讀取後對映到新常數名）
- API schema（HTTP request/response body 的 key 名稱）— 前後端透過 settings dict 傳遞，不是公開 API

---

## 驗證方式

1. `grep -r "source_lang\|target_lang\|sourceLanguage\|SOURCE_LANG\|TARGET_LANG" backend/ frontend/src/` 結果為空（除 `.env` 外）
2. SettingsModal 顯示「學習語言」/「母語」
3. 生成卡片流程正常（語言設定正確傳遞至 GPT prompt）
