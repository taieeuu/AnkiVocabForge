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
請為以下 {learning_language} 文章中不熟悉的單字逐一產生卡片資訊。

- pos / meaning / synonyms 使用 {native_language} 回答
- ex1_ori / ex2_ori / hint 使用 {learning_language} 撰寫
- synonyms：若有則給 3-5 個，附上 {native_language} 意思；無則留空字串
- hint：說明時不可包含單字本身
- 例句只能使用文章已有的語境，不要創造超出文章範圍的背景
- 若清單中有重複單字，每個仍需獨立輸出
- 若單字意思有誤請修正；不要使用 emoji 或特殊符號

單字清單：
{vocab_list}
"""


PROMPT_EN_VOCAB = """
{goal_prompt_section}
以下是我不會的單字清單，請逐一產生卡片資訊。

- pos / meaning / synonyms 使用 {native_language} 回答
- ex1_ori / ex2_ori / hint 使用 {learning_language} 撰寫
- synonyms：若有則給 3-5 個，附上 {native_language} 意思；無則留空字串
- hint：說明時不可包含單字本身
- 例句盡量貼近目標相關內容
- 若清單中有重複單字，每個仍需獨立輸出
- 若單字意思有誤請修正；不要使用 emoji 或特殊符號

單字清單：
{vocab_list}
"""

PROMPT_AI_GENERATE = """
{goal_prompt_section}
請根據學習目標生成 {count} 個 {learning_language} 單字，並逐一產生卡片資訊。

- pos / meaning / synonyms 使用 {native_language} 回答
- ex1_ori / ex2_ori / hint 使用 {learning_language} 撰寫
- synonyms：若有則給 3-5 個，附上 {native_language} 意思；無則留空字串
- hint：說明時不可包含單字本身
- 單字需符合學習目標的主題與難度，且彼此具有語意關聯
- 例句難度與學習目標一致，不要添加無關背景
- 生成數量必須嚴格等於 {count}；不要使用 emoji 或特殊符號
"""

GRAMMAR_PROMPT = """
{goal_prompt_section}
以下是我尚未熟悉的文法清單，請逐一產生卡片資訊。

- grammar：標準句型結構公式，不可省略句型的變化形式
- usage：使用 {learning_language}，具體描述何時選用此結構，避免抽象模糊表述
- meaning：使用 {native_language}
- contrast：明確說明此文法與相似文法的選擇判斷依據，指出何種語境下只能用其中一者，而非僅描述表面差異
- ex1_ori / ex2_ori：使用 {learning_language}，兩句需呈現不同的合理使用情境
- ex1_trans / ex2_trans：使用 {native_language}，翻譯需專業且自然

- 內容符合學習目標的主題、語域與難度
- 不要添加背景敘事或對話情境
- 不要使用 emoji 或特殊符號
"""


