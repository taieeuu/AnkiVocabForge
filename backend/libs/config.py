from __future__ import annotations

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

CONTENT_TYPES = [
    "Word",
    "Grammar"
]

INPUT_MODES = [
    "Article",
    "Vocab",
    "AI Generate"
]

ANKI_CARD_TYPES = [
    "Basic",
    "Cloze",
    "Basic+Cloze"
]

AI_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-5-nano",
]


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
SOURCE_LANG: str = _get("SOURCE_LANG", "English")
TARGET_LANG: str = _get("TARGET_LANG", "Chinese")

# Deck 設定
DEFAULT_DECK_NAME: str = _get("DEFAULT_DECK_NAME", "TestDeck")

# AI 模型設定
AI_MODEL: str = _get("AI_MODEL", "gpt-5-nano")

# 輸出資料夾
VOICE_DIR: str = str(_get("VOICE_DIR", str(OUTPUTS_DIR / "voice")))
PASSAGE_IMAGE_DIR: str = str(_get("PASSAGE_IMAGE_DIR", str(OUTPUTS_DIR / "passage_images")))
TRANSED_VOCAB_DIR: str = str(_get("TRANSED_VOCAB_DIR", str(OUTPUTS_DIR / "transed_vocab")))
CONFIG_DIR: str = str(_get("CONFIG_DIR", str(ROOT_DIR / "config")))

# Anki 資料庫路徑
_DEFAULT_ANKI_DB = "/Users/taieeuu/Library/Application Support/Anki2/使用者 1/collection.anki2"
ANKI_DB_PATH: str = _get("ANKI_DB_PATH", _DEFAULT_ANKI_DB)

# OpenAI API Key
OPENAI_API_KEY: str = _get("OPENAI_API_KEY", "")


# =========================
# Anki Settings
# =========================

BASIC_FIELDS = [
    {'name': 'Word'}, 
    {'name': 'Pos'},
    {'name': 'Meaning'}, 
    {'name': 'Synonyms'},
    {'name': 'Ex1_ori'},
    {'name': 'Ex1_trans'},
    {'name': 'Ex2_ori'},
    {'name': 'Ex2_trans'},
    {'name': 'Audio'},
    {'name': 'Hint'},
]

BASIC_TEMPLATES = [
    {
        'name': 'Card 1',
        'qfmt': '''
                <div>
                    <div>{{Word}} <span style="color:gray;">({{Pos}})</span></div>
                    <br>
                    <div>{{Hint}}</div>
                    <div>{{Audio}}</div>
                </div>
                ''',
        'afmt': '''
                <div>
                    <div>{{Word}} <span style="color:gray;">({{Pos}})</span></div>
                    <br>
                    <div>{{Hint}}</div>
                    <div>{{Audio}}</div>
                    <hr id=answer>
                    <div><b>{{Meaning}}</b></div>
                    <br>
                    <div>
                        <span style="color:gray;">{{Synonyms}}</span>
                    </div>
                    <br>
                    <div>
                        {{Ex1_ori}}<br><span style="color:gray;">{{Ex1_trans}}</span>
                    </div>
                    <br>
                    <div>
                        {{Ex2_ori}}<br><span style="color:gray;">{{Ex2_trans}}</span>
                    </div>
                </div>
                ''',
    },
    {
        'name': 'Card 2 (Reverse)',
        'qfmt': '''
                <div>
                    <div>{{Meaning}} <span style="color:gray;">({{Pos}})</span></div>
                    <br>
                    <div>{{Hint}}</div>
                </div>
                ''',
        'afmt': '''
                <div>
                    <div>{{Meaning}} <span style="color:gray;">({{Pos}})</span></div>
                    <br>
                    <div>{{Hint}}</div>
                    <hr id=answer>
                    <div>
                        <b>{{Word}}</b>
                    </div>
                    <br>
                    <div>
                        <span style="color:gray;">{{Synonyms}}</span>
                    </div>
                    <br>
                    <div>
                        {{Ex1_ori}}<br><span style="color:gray;">{{Ex1_trans}}</span>
                    </div>
                    <br>
                    <div>
                        {{Ex2_ori}}<br><span style="color:gray;">{{Ex2_trans}}</span>
                    </div>
                    <br>
                    <div>
                        {{Audio}}
                    </div>
                </div>
                ''',
    }
]

BASIC_CSS = """
    .card { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif; font-size: 22px; }
    .hint { color: #888; margin-top: .5em; }
    .extra { margin-top: 1em; font-size: 18px; line-height: 1.5; }
    .src { margin-top: .5em; font-size: 14px; color: #666; }
"""

CLOZE_FIELDS = [
    {'name': 'Text'},       # Cloze 格式的文本（包含兩個例句和翻譯）
    {'name': 'Word'},     
    {'name': 'Pos'},      
    {'name': 'Meaning'},  
    {'name': 'Synonyms'}, 
    {'name': 'Ex1_ori'},  
    {'name': 'Ex1_trans'},
    {'name': 'Ex2_ori'},  
    {'name': 'Ex2_trans'},
    {'name': 'Audio'},    
    {'name': 'Hint'},     
]

CLOZE_TEMPLATES = [
    {
        'name': 'Cloze',
        'qfmt': '''
                <div>
                    <div>{{type:cloze:Text}}</div>
                    <span style="color:gray; font-weight: normal;">{{Pos}}</span>
                    <div style="white-space: pre-line;">{{cloze:Text}}</div>
                </div>
                ''',
        'afmt': '''
                <div>
                    <span style="color:gray; font-weight: normal;">{{Pos}}</span>
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 1em;">{{Meaning}}</div>
                </div>
                <hr id=answer>
                <div>
                    <div>{{type:cloze:Text}}</div>
                    <div style="white-space: pre-line;">{{cloze:Text}}</div>
                </div>
                '''
    }
]

# =========================
# GPT Settings
# =========================

GOAL_PROMPT = """
🎯 學習目標：本次生成內容請符合 {target} 的內容。
請依此學習目標調整整體語言難度、詞彙深度與語氣，確保產出內容與該等級相符。

"""

PROMPT_EN_PASSAGE_VOCAB_QUESTIONS = """
{goal_prompt_section}

請根據以下設定，為我在這篇 {source_language} 文章中不熟悉的單字逐一產生對應資訊。  
輸出格式請嚴格遵照下列欄位結構：

- word: 單字
- pos: 單字的詞性 (請使用 {source_language} 常見且標準的詞性名稱，並使用 {target_language} 回答)
- meaning: {target_language} 意思
- synonyms: 同義詞（若有的話給 3-5 個並附上 {target_language} 意思，全部以字串形式呈現）
- ex1_ori: 第一句 {source_language} 例句（使用該單字，且不要創造超出文章內容的額外背景）
- ex1_trans: 第一句例句的 {target_language} 翻譯
- ex2_ori: 第二句 {source_language} 例句（使用該單字，且不要創造超出文章內容的額外背景）
- ex2_trans: 第二句例句的 {target_language} 翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（使用 {source_language} 回答）

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
- pos: 單字的詞性 (請使用 {source_language} 常見且標準的詞性名稱，並使用 {target_language} 回答)
- meaning: 單字在 {target_language} 的意義
- synonyms: 同義詞（若有的話給 3-5 個，並附上 {target_language} 意思，全部以字串形式呈現）
- ex1_ori: 第一句 {source_language} 例句（使用該單字，且盡量貼近目標相關內容）
- ex1_trans: 第一句例句的 {target_language} 翻譯
- ex2_ori: 第二句 {source_language} 例句（使用該單字，且盡量貼近目標相關內容）
- ex2_trans: 第二句例句的 {target_language} 翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（請使用 {source_language} 回答）

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

請根據學習目標生成 {count} 個適合的 {source_language} 單字，並為每個單字產生以下欄位：

- word: 單字
- pos: 單字的詞性 (請使用 {source_language} 常見且標準的詞性名稱，並使用 {target_language} 回答)
- meaning: 單字在 {target_language} 的意義
- synonyms: 同義詞（若有的話給 3-5 個，並附上它們在 {target_language} 的意思；全部以字串形式呈現）
- ex1_ori: 第一句 {source_language} 例句（使用該單字，難度與學習目標一致，不得添加無關背景）
- ex1_trans: 第一句例句在 {target_language} 的翻譯
- ex2_ori: 第二句 {source_language} 例句（使用該單字，難度與學習目標一致，不得添加無關背景）
- ex2_trans: 第二句例句在 {target_language} 的翻譯
- hint: 對這個單字的說明，解釋時不要包含單字本身（使用 {source_language} 回答）

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

WORD_SCHEMA = {
    "vocab": {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "word": {"type": "string"},
                "pos": {"type": "string"},
                "meaning": {"type": "string"},
                "synonyms": {"type": "string"},
                "ex1_ori": {"type": "string"},
                "ex1_trans": {"type": "string"},
                "ex2_ori": {"type": "string"},
                "ex2_trans": {"type": "string"},
                "hint": {"type": "string"},
            },
            "required": ["word", "pos", "meaning", "synonyms", "ex1_ori", "ex1_trans", "ex2_ori", "ex2_trans", "hint"]
        }
    }
}

