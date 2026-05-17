import os
from pathlib import Path
from dotenv import load_dotenv

# =========================
# 路徑設定
# =========================

ROOT_DIR: Path = Path(__file__).resolve().parents[1]
OUTPUTS_DIR: Path = ROOT_DIR / "outputs"

# 載入 .env 文件（從 backend 目錄和項目根目錄）
# 優先順序：backend/.env -> 項目根目錄/.env
env_file_backend = ROOT_DIR / ".env"
env_file_root = ROOT_DIR.parent / ".env"

# 先載入 backend/.env（如果存在）
if env_file_backend.exists():
    load_dotenv(env_file_backend, override=False)
# 再載入項目根目錄/.env（如果存在，不會覆蓋已載入的變數）
if env_file_root.exists():
    load_dotenv(env_file_root, override=False)
# 最後嘗試從當前工作目錄載入（用於開發環境）
load_dotenv(override=False)


# =========================
# 常數
# =========================

CONTENT_TYPES = ["Word", "Grammar"]

INPUT_MODES = ["Article", "Vocab", "AI Generate"]

ANKI_CARD_TYPES = ["Basic", "Cloze", "Basic+Cloze"]

AI_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-5-nano",
]

BATCH_SIZE = 5

# =========================
# Function
# =========================


def _get(key: str, default: str) -> str:
    """從環境變數讀取配置，如果不存在則使用預設值"""
    env_val = os.getenv(key)
    if isinstance(env_val, str) and env_val:
        return env_val
    return default


# =========================
# Gobal Settings
# =========================

# 語言設定
LEARNING_LANG: str = _get("SOURCE_LANG", "English")
NATIVE_LANG: str = _get("TARGET_LANG", "Chinese")

# Deck 設定
DEFAULT_DECK_NAME: str = _get("DEFAULT_DECK_NAME", "TestDeck")

# AI 模型設定
AI_MODEL: str = _get("AI_MODEL", "gpt-5-nano")

# 輸出資料夾
VOICE_DIR: str = str(_get("VOICE_DIR", str(OUTPUTS_DIR / "voice")))
PASSAGE_IMAGE_DIR: str = str(
    _get("PASSAGE_IMAGE_DIR", str(OUTPUTS_DIR / "passage_images"))
)
TRANSED_VOCAB_DIR: str = str(
    _get("TRANSED_VOCAB_DIR", str(OUTPUTS_DIR / "transed_vocab"))
)
CONFIG_DIR: str = str(_get("CONFIG_DIR", str(ROOT_DIR / "config")))

# Anki 資料庫路徑
_DEFAULT_ANKI_DB = (
    "/Users/taieeuu/Library/Application Support/Anki2/使用者 1/collection.anki2"
)
ANKI_DB_PATH: str = _get("ANKI_DB_PATH", _DEFAULT_ANKI_DB)

# OpenAI API Key
OPENAI_API_KEY: str = _get("OPENAI_API_KEY", "")


# =========================
# Anki Settings
# =========================

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
]

BASIC_TEMPLATES = [
    {
        "name": "Card 1",
        "qfmt": """
<div class="heading">{{Word}}<span class="pos-badge">{{Pos}}</span></div>
{{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}
{{#Audio}}<div class="section">{{Audio}}</div>{{/Audio}}
""",
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
""",
    },
    {
        "name": "Card 2 (Reverse)",
        "qfmt": """
<div class="heading">{{Meaning}}<span class="pos-badge">{{Pos}}</span></div>
{{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}
""",
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
""",
    },
]

BASIC_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif;
    font-size: 20px;
    color: #1e293b;
    background: #ffffff;
    padding: 32px;
    line-height: 1.6;
}

.heading {
    font-size: 30px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 4px;
}

.pos-badge {
    display: inline-block;
    background: #f1f5f9;
    color: #64748b;
    font-size: 14px;
    font-weight: normal;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 8px;
    vertical-align: middle;
}

.hint {
    color: #64748b;
    font-size: 18px;
    margin-top: 4px;
}

.meaning {
    font-size: 24px;
    font-weight: 700;
    color: #2563eb;
    margin-top: 4px;
    margin-bottom: 4px;
}

.synonyms {
    color: #64748b;
    font-size: 16px;
    margin-top: 4px;
}

.section {
    margin-top: 12px;
}

.example-block {
    border-left: 2px solid #e2e8f0;
    padding-left: 12px;
    margin-top: 12px;
}

.example-ori {
    color: #334155;
    font-size: 16px;
}

.example-trans {
    color: #64748b;
    font-size: 14px;
    margin-top: 4px;
}

.info-block {
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 12px;
}

.info-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}

.info-content {
    font-size: 15px;
    font-weight: normal;
    color: #334155;
}

.info-block-usage {
    background: #fffbeb;
    border: 1px solid #fde68a;
}

.info-block-usage .info-label { color: #d97706; }

.info-block-contrast {
    background: #faf5ff;
    border: 1px solid #e9d5ff;
}

.info-block-contrast .info-label { color: #9333ea; }

/* Night mode */
.card.night_mode {
    color: #e2e8f0;
    background: #1e293b;
}

.card.night_mode .heading   { color: #f1f5f9; }
.card.night_mode .pos-badge { background: #334155; color: #94a3b8; }
.card.night_mode .hint      { color: #94a3b8; }
.card.night_mode .meaning   { color: #60a5fa; }
.card.night_mode .synonyms  { color: #94a3b8; }

.card.night_mode .example-block           { border-left-color: #334155; }
.card.night_mode .example-ori             { color: #e2e8f0; }
.card.night_mode .example-trans           { color: #94a3b8; }
.card.night_mode .info-content            { color: #cbd5e1; }

.card.night_mode .info-block-usage        { background: rgba(120,53,15,0.2);  border-color: rgba(146,64,14,0.3); }
.card.night_mode .info-block-usage .info-label    { color: #fbbf24; }
.card.night_mode .info-block-contrast     { background: rgba(88,28,135,0.2);  border-color: rgba(107,33,168,0.3); }
.card.night_mode .info-block-contrast .info-label { color: #c084fc; }
"""

CLOZE_FIELDS = [
    {"name": "Text"},  # Cloze 格式的文本（包含兩個例句和翻譯）
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
]

CLOZE_TEMPLATES = [
    {
        "name": "Cloze",
        "qfmt": """
{{#Pos}}<span class="pos-badge" style="margin-left:0;">{{Pos}}</span>{{/Pos}}
<div class="section" style="white-space: pre-line; line-height: 1.8;">{{cloze:Text}}</div>
""",
        "afmt": """
{{#Pos}}<span class="pos-badge" style="margin-left:0;">{{Pos}}</span>{{/Pos}}
<div class="meaning">{{Meaning}}</div>
<hr id=answer>
<div class="section" style="white-space: pre-line; line-height: 1.8;">{{cloze:Text}}</div>
""",
    }
]

GRAMMAR_FIELDS = [
    {"name": "Grammar"},
    {"name": "Usage"},
    {"name": "Meaning"},
    {"name": "Contrast"},
    {"name": "Ex1_ori"},
    {"name": "Ex1_trans"},
    {"name": "Ex2_ori"},
    {"name": "Ex2_trans"},
]

BASIC_GRAMMAR_TEMPLATES = [
    {
        "name": "Grammar Card 1",
        "qfmt": """
<div class="heading">{{Grammar}}</div>
""",
        "afmt": """
<div class="heading">{{Grammar}}</div>
<hr id=answer>
<div class="meaning">{{Meaning}}</div>
{{#Usage}}
<div class="info-block info-block-usage">
    <div class="info-label">Usage</div>
    <div class="info-content">{{Usage}}</div>
</div>
{{/Usage}}
{{#Contrast}}
<div class="info-block info-block-contrast">
    <div class="info-label">Contrast</div>
    <div class="info-content">{{Contrast}}</div>
</div>
{{/Contrast}}
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
""",
    },
]

# =========================
# GPT Settings
# =========================
SYSTEM_PROMPT = """

"""

GOAL_PROMPT = """
🎯 學習目標：本次生成內容請符合 {target} 的內容。
請依此學習目標調整整體語言難度、詞彙深度與語氣，確保產出內容與該等級相符。

"""

PROMPT_EN_PASSAGE_VOCAB_QUESTIONS = """
{goal_prompt_section}

請根據以下設定，為我在這篇 {learning_language} 文章中不熟悉的單字逐一產生對應資訊。  
輸出格式請嚴格遵照下列欄位結構：

- word: 單字
- pos: 單字的詞性 (請使用 {learning_language} 常見且標準的詞性名稱，並使用 {native_language} 回答)
- meaning: {native_language} 意思
- synonyms: 單字的同義詞（若有的話給 3-5 個並附上 {native_language} 意思，全部以字串形式呈現）
- ex1_ori: 第一句 {learning_language} 例句（使用該單字，且不要創造超出文章內容的額外背景）
- ex1_trans: 第一句例句的 {native_language} 翻譯
- ex2_ori: 第二句 {learning_language} 例句（使用該單字，且不要創造超出文章內容的額外背景）
- ex2_trans: 第二句例句的 {native_language} 翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（使用 {learning_language} 回答）

⚠️ 注意事項：
1. 僅針對我提供的單字生成內容，不要新增額外單字。
2. 幫我檢查單字意思是否有錯誤，如果有錯誤請修正。
3. 所有輸出請保持清晰且結構一致，以利程式後續解析。
4. 請只返回純 JSON 格式，不要包含任何額外的文字、編號、註解或格式符號。
5. 確保每個欄位都要生成，不可漏掉。
6. 所有內容請使用標準 UTF-8 字元，不要加入 emoji、特殊符號（如 smart quotes、破折號）。
7. 不要推測或延伸任何未提供的單字或內容。
8. 若 vocab_list 中有重複單字，每個單字仍需獨立輸出。
9. 每個欄位的值都必須是字串（string），不可使用陣列、物件或數字。
10. 最終輸出請以 JSON 陣列格式呈現，每個單字為一個獨立的 JSON 物件。

以下為單字清單：
{vocab_list}
"""


PROMPT_EN_VOCAB = """
{goal_prompt_section}

以下是我不會的單字清單，請依序針對這些單字產生以下欄位：

- word: 單字
- pos: 單字的詞性 (請使用 {learning_language} 常見且標準的詞性名稱，並使用 {native_language} 回答)
- meaning: 單字在 {native_language} 的意義
- synonyms: 單字的同義詞（若有的話給 3-5 個，並附上 {native_language} 意思，全部以字串形式呈現）
- ex1_ori: 第一句 {learning_language} 例句（使用該單字，且盡量貼近目標相關內容）
- ex1_trans: 第一句例句的 {native_language} 翻譯
- ex2_ori: 第二句 {learning_language} 例句（使用該單字，且盡量貼近目標相關內容）
- ex2_trans: 第二句例句的 {native_language} 翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（請使用 {learning_language} 回答）

⚠️ 注意事項：
1. 僅針對我提供的單字生成內容，不要新增額外單字。
2. 幫我檢查單字意思是否有錯誤，如果有錯誤請修正。
3. 所有輸出請保持清晰且結構一致，以利程式後續解析。
4. 請只返回純 JSON 格式，不要包含任何額外的文字、編號、註解或格式符號。
5. 確保每個欄位都要生成，不可漏掉。
6. 所有內容請使用標準 UTF-8 字元，不要加入 emoji、特殊符號（如 smart quotes、破折號）。
7. 不要推測或延伸任何未提供的單字或內容。
8. 若 vocab_list 中有重複單字，每個單字仍需獨立輸出。
9. 每個欄位的值都必須是字串（string），不可使用陣列、物件或數字。
10. 最終輸出請以 JSON 陣列格式呈現，每個單字為一個獨立的 JSON 物件。

我的單字如下：
{vocab_list}
"""

PROMPT_AI_GENERATE = """
{goal_prompt_section}

請根據學習目標生成 {count} 個適合的 {learning_language} 單字，並為每個單字產生以下欄位：

- word: 單字
- pos: 單字的詞性 (請使用 {learning_language} 常見且標準的詞性名稱，並使用 {native_language} 回答)
- meaning: 單字在 {native_language} 的意義
- synonyms: 單字的同義詞（若有的話給 3-5 個，並附上它們在 {native_language} 的意思；全部以字串形式呈現）
- ex1_ori: 第一句 {learning_language} 例句（使用該單字，難度與學習目標一致，不得添加無關背景）
- ex1_trans: 第一句例句在 {native_language} 的翻譯
- ex2_ori: 第二句 {learning_language} 例句（使用該單字，難度與學習目標一致，不得添加無關背景）
- ex2_trans: 第二句例句在 {native_language} 的翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（使用 {learning_language} 回答）

⚠️ 注意事項：
1. 生成的單字必須完全符合學習目標的主題與難度。
2. 單字之間需具有主題或語意上的邏輯關聯，形成一個有一致性的學習單元。
3. 所有輸出必須保持清晰且結構一致，以利後續程式解析。
4. **請僅輸出純 JSON，不可包含任何額外文字、註解或符號，否則將無法解析。**
5. 所有欄位皆必須生成，不可缺漏。
6. 生成的單字總數必須嚴格等於 {count}。
7. 所有欄位的值必須是字串（string），不得使用陣列、物件或數字。
8. 例句需自然簡潔，不可加入與學習目標無關的複雜背景情節。
9. 請勿加入 emoji 或特殊 Unicode 字元（如 smart quotes 或破折號）。
10. **最終輸出請以 JSON 陣列格式呈現，每個單字為獨立 JSON 物件。**
"""

GRAMMAR_PROMPT = """
{goal_prompt_section}

以下是我尚未熟悉的文法清單。請將每一條輸入視為一個獨立且不可拆分的文法項目，並依照輸入順序逐一生成對應資料。

請針對每一個文法項目，嚴格依照下列欄位定義產生內容，並遵守所有規則。

每一個文法項目必須包含以下欄位：

- grammar：該文法的標準句型結構公式；請勿省略文法句型的變化。
- usage：此文法的實際使用時機與適用條件，需具體描述何時選用此結構，避免抽象或模糊表述（使用 {learning_language}）。
- meaning：此文法的意思（使用 {native_language}）。
- contrast：contrast 必須明確指出「相似文法」與「本結構」的選擇判斷依據，並說明在何種語境或條件下只能使用其中一者，而非僅描述表面差異。
- ex1_ori：第一句 {learning_language} 例句，必須正確且自然地使用該文法，語句簡潔，難度符合學習目標。
- ex1_trans：第一句例句的 {native_language} 專業且自然的翻譯。
- ex2_ori：第二句 {learning_language} 例句，必須使用相同文法，但呈現不同且合理的使用情境。
- ex2_trans：第二句例句的 {native_language} 專業且自然的翻譯。

嚴格規則（請務必遵守）：
1. 所有生成的文法項目必須完全符合學習目標所定義的主題、語域與難度。
2. 所有欄位必須嚴格遵守欄位定義。
3. 請僅生成與文法本身直接相關的內容，不得加入背景敘事、對話情境或多餘說明。
4. 所有輸出內容必須結構穩定、欄位完整、順序一致，以利後續程式解析。
5. 請僅輸出純 JSON，不得包含任何說明文字、註解、Markdown、前後綴文字或多餘符號。
6. 最終輸出必須為一個 JSON array，每一個文法項目為一個獨立的 object。
7. 所有欄位的值一律使用字串（string），不得使用陣列、物件、數字、布林值或 null。
8. 請勿使用 emoji、smart quotes、破折號或任何非 ASCII 的特殊字元。
9. 請勿遺漏任何欄位，所有欄位皆必須出現在每一個 JSON 物件中，且欄位名稱需完全一致。
"""


