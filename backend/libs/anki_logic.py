import genanki
from .config import *
from typing import List, Optional
import random
import json
import os
from .logger import LogLevel, get_logger

logger = get_logger()


class AnkiLogic:
    def __init__(self, deck_name: str = "MyTestDeck"):
        self.deck_name = deck_name
        
        # 不再连接本地 Anki 数据库，直接生成随机 deck_id
        deck_id = random.randint(10**9, 10**10)   # genanki 需要 9~10 digit random int
        logger.log(LogLevel.INFO, f"Creating new deck '{deck_name}' with id: {deck_id}")

        self.deck_id = deck_id
        logger.log(LogLevel.SUCCESS, f"✅ Using Deck '{deck_name}' with id: {self.deck_id}")

        # ---- genanki Deck 用同 id ----
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.media_files = []
    
    def execute(self, *args, **kwargs):
        if kwargs.get("execute_type") == "import_vocab":
            self.import_vocab(kwargs.get("vocab_json"))
        else:
            raise ValueError(f"Invalid execute type: {kwargs.get('execute_type')}")
    
    # ---------------- Deck & Note functions ----------------

    def create_anki_note(
        self, 
        model,
        word: str,
        pos: str,
        meaning: str,
        synonyms: str,
        ex1_ori: str,
        ex1_trans: str,
        ex2_ori: str,
        ex2_trans: str,
        audio: str = "",
        hint: str = "",
    ):
        """建立 Anki note"""
        audio_filename = os.path.basename(audio) if audio else ""

        fields = [
            word,
            pos,
            meaning,
            synonyms,
            ex1_ori,
            ex1_trans,
            ex2_ori,
            ex2_trans,
            f"[sound:{audio_filename}]" if audio else "",
            hint,
        ]

        note = genanki.Note(
            model=model,
            fields=fields
        )

        # 如果提供了 audio，加入 media_files（只添加存在的文件，使用绝对路径）
        if audio:
            audio_path = os.path.abspath(audio) if not os.path.isabs(audio) else audio
            if os.path.exists(audio_path):
                self.media_files.append(audio_path)
            else:
                logger.log(LogLevel.WARNING, f"Audio file not found, skipping: {audio_path}")

        return note
        
    def create_anki_card(self, note: genanki.Note):
        """將 note 加入到 deck 中"""
        self.deck.add_note(note)
        logger.log(LogLevel.SUCCESS, f"✅ Added note: {note.fields[0]}")

    # ---------------- Anki Collection utils (已移除本地数据库连接) ----------------
    
    def find_decks_id(self, deck_name: str):
        """尋找指定名稱的 deck ID（已移除本地数据库连接，返回 None）"""
        logger.log(LogLevel.WARNING, "本地 Anki 数据库连接已移除，此方法不再可用")
        return None
    
    def get_decks(self):
        """取得所有 decks（已移除本地数据库连接，返回空列表）"""
        logger.log(LogLevel.WARNING, "本地 Anki 数据库连接已移除，此方法不再可用")
        return []
    
    def find_notes(self, deck_name: str):
        """尋找指定 deck 的所有 notes（已移除本地数据库连接，返回空列表）"""
        logger.log(LogLevel.WARNING, "本地 Anki 数据库连接已移除，此方法不再可用")
        return []

    # ---------------- Models ----------------
    
    def create_basic_model(self, id: int):
        """建立 basic model"""
        return genanki.Model(
            id,
            f"{self.deck_name}_basic",
            fields=BASIC_FIELDS,
            templates=BASIC_TEMPLATES,
            css=BASIC_CSS
        )

    def create_cloze_model(self, id: int):
        """建立 cloze model"""
        return genanki.Model(
            id,
            f"{self.deck_name}_cloze",
            fields=CLOZE_FIELDS,
            templates=CLOZE_TEMPLATES,
            css=BASIC_CSS,
            model_type=genanki.Model.CLOZE  # 標記為 Cloze 類型
        )
    
    def create_cloze_note(
        self,
        model,
        text: str = "",  # Cloze 格式的文本（包含兩個例句和翻譯）
        word: str = "",
        pos: str = "",
        meaning: str = "",
        synonyms: str = "",
        ex1_ori: str = "",
        ex1_trans: str = "",
        ex2_ori: str = "",
        ex2_trans: str = "",
        audio: str = "",
        hint: str = "",
    ):
        """
        建立 Cloze 類型的 Anki note（可輸入單字版本）
        
        Args:
            model: Anki model
            text: Cloze 格式的文本（包含兩個例句和翻譯）
            word: 單字（用於輸入驗證和答案顯示）
            pos: 詞性
            meaning: 單字意思
            synonyms: 同義詞
            ex1_ori: 第一句例句（來源語言）
            ex1_trans: 第一句例句翻譯（目標語言）
            ex2_ori: 第二句例句（來源語言）
            ex2_trans: 第二句例句翻譯（目標語言）
            audio: 語音檔案路徑
            hint: 提示
        """
        audio_filename = os.path.basename(audio) if audio else ""
        
        fields = [
            text,  # Cloze 格式的文本（包含兩個例句和翻譯）
            word,  # 單字
            pos,   # 詞性
            meaning,
            synonyms,
            ex1_ori,
            ex1_trans,
            ex2_ori,
            ex2_trans,
            f"[sound:{audio_filename}]" if audio else "",  # Audio
            hint,
        ]
        
        note = genanki.Note(
            model=model,
            fields=fields
        )
        
        # 如果提供了 audio，加入 media_files（只添加存在的文件，使用绝对路径）
        if audio:
            audio_path = os.path.abspath(audio) if not os.path.isabs(audio) else audio
            if os.path.exists(audio_path):
                self.media_files.append(audio_path)
            else:
                logger.log(LogLevel.WARNING, f"Audio file not found, skipping: {audio_path}")
        
        return note
    
    def to_pack(self, output_dir: str = None, filename_suffix: str = None):
        """將 deck 打包成 .apkg 檔案"""
        import os
        from helpers.file_utils import slugify
        # 構建檔案名稱（使用 slugify 確保安全）
        safe_deck_name = slugify(self.deck_name)
        if filename_suffix:
            safe_suffix = slugify(filename_suffix)
            apkg_filename = f'{safe_deck_name}_{safe_suffix}.apkg'
        else:
            apkg_filename = f'{safe_deck_name}.apkg'
        
        # 如果提供了 output_dir，使用它；否則使用默認的 APKG_DIR
        if output_dir:
            output_path = os.path.join(output_dir, apkg_filename)
            os.makedirs(output_dir, exist_ok=True)
        else:
            # 確保 APKG_DIR 目錄存在
            from .config import OUTPUTS_DIR
            APKG_DIR = str(OUTPUTS_DIR / "apkg")
            os.makedirs(APKG_DIR, exist_ok=True)
            output_path = os.path.join(APKG_DIR, apkg_filename)
        
        # 過濾並轉換 media_files 為絕對路徑，只保留存在的文件
        valid_media_files = []
        for media_file in self.media_files:
            # 轉換為絕對路徑
            abs_path = os.path.abspath(media_file) if not os.path.isabs(media_file) else media_file
            if os.path.exists(abs_path):
                valid_media_files.append(abs_path)
            else:
                logger.log(LogLevel.WARNING, f"Media file not found, skipping: {abs_path}")
        
        pkg = genanki.Package(self.deck)
        pkg.media_files = valid_media_files
        pkg.write_to_file(output_path)
        logger.log(LogLevel.SUCCESS, f"Exported: {output_path}")

    def random_model_id(self):
        """產生隨機的 model ID"""
        return random.randint(10**9, 10**10)

    def read_vocab_json(self, json_path: str):
        """讀取單字 JSON 檔案"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.log(LogLevel.ERROR, f"Error reading vocab JSON: {e}")
            return []

    def has_model(self, model_name: str) -> bool:
        """
        檢查 Anki Collection 是否已有指定名稱的 Model（已移除本地数据库连接，总是返回 False）。
        """
        logger.log(LogLevel.INFO, f"本地 Anki 数据库连接已移除，总是创建新 model: {model_name}")
        return False

    def get_model_id(self, model_name: str) -> Optional[int]:
        """
        回傳 Model 的 ID（已移除本地数据库连接，总是返回 None）。
        """
        return None

    def get_model(self, model_name: str) -> Optional[dict]:
        """
        回傳 Model 的完整資訊（已移除本地数据库连接，总是返回 None）。
        """
        return None

    def _compare_model_fields(self, existing_model: dict, expected_fields: list[dict]) -> bool:
        """
        比較既有 model 的欄位是否與預期欄位一致
        
        Args:
            existing_model: 既有 model 的完整資訊
            expected_fields: 預期的欄位列表（例如 CLOZE_FIELDS）
            
        Returns:
            bool: 如果欄位一致則回傳 True，否則回傳 False
        """
        try:
            # 獲取既有 model 的欄位
            existing_fields = existing_model.get("flds", [])
            
            # 轉換為欄位名稱列表（忽略順序）
            existing_field_names = {field.get("name", "") for field in existing_fields}
            expected_field_names = {field.get("name", "") for field in expected_fields}
            
            # 比較欄位名稱是否一致
            if existing_field_names != expected_field_names:
                logger.log(LogLevel.WARNING, 
                    f"Model 欄位不一致：既有欄位 {sorted(existing_field_names)}，預期欄位 {sorted(expected_field_names)}")
                return False
            
            # 檢查欄位順序是否一致（可選，但建議保持一致）
            existing_field_order = [field.get("name", "") for field in existing_fields]
            expected_field_order = [field.get("name", "") for field in expected_fields]
            
            if existing_field_order != expected_field_order:
                logger.log(LogLevel.WARNING, 
                    f"Model 欄位順序不一致：既有順序 {existing_field_order}，預期順序 {expected_field_order}")
                # 順序不一致不影響功能，但記錄警告
                return True  # 欄位名稱一致即可，順序可以不同
            
            return True
        except Exception as e:
            logger.log(LogLevel.WARNING, f"比較 model 欄位時發生錯誤：{e}")
            return False

    def get_or_create_basic_model(self):
        """
        建立新的 basic model（已移除本地数据库连接，总是创建新 model）。
        """
        model_name = f"{self.deck_name}_basic"
        model_id = self.random_model_id()
        logger.log(LogLevel.INFO, f"創建新的 Basic model '{model_name}' (ID: {model_id})")
        return self.create_basic_model(model_id)

    def get_or_create_cloze_model(self):
        """
        建立新的 cloze model（已移除本地数据库连接，总是创建新 model）。
        """
        model_name = f"{self.deck_name}_cloze"
        model_id = self.random_model_id()
        logger.log(LogLevel.INFO, f"創建新的 Cloze model '{model_name}' (ID: {model_id})")
        return self.create_cloze_model(model_id)

    # ---------------- Duplicate Check Functions ----------------
    
    def get_existing_words_from_deck(self, deck_name: Optional[str] = None) -> set:
        """
        從 Anki 資料庫中取得指定 deck 的所有單字（已移除本地数据库连接，返回空集合）。
        """
        logger.log(LogLevel.INFO, "本地 Anki 数据库连接已移除，返回空集合")
        return set()

    def check_duplicate_with_anki_db(self, vocab_list: list[dict], deck_name: Optional[str] = None) -> dict:
        """
        檢查即將產生的單字列表是否與 Anki 資料庫中已有的單字重複
        
        Args:
            vocab_list: 即將產生的單字列表
            deck_name: 要檢查的 deck 名稱，如果為 None 則使用 self.deck_name
            
        Returns:
            dict: 包含重複資訊的字典，包含以下欄位：
                - has_duplicates: bool
                - duplicate_words: set
                - duplicate_details: dict
                - new_words_count: int
                - unique_new_words: int
                - existing_words_count: int
                - duplicate_count: int
        """
        # 取得即將產生的單字列表
        new_words = [v.get("word", "").strip() for v in vocab_list if v.get("word", "").strip()]
        new_words_set = set(new_words)
        
        # 取得 Anki 資料庫中已有的單字
        existing_words = self.get_existing_words_from_deck(deck_name)
        
        # 找出重複的單字
        duplicate_words = new_words_set.intersection(existing_words)
        
        # 建立重複單字的詳細資訊
        duplicate_details = {}
        for word in duplicate_words:
            # 找出這個單字在 vocab_list 中的位置
            indices = [i for i, v in enumerate(vocab_list) if v.get("word", "").strip() == word]
            duplicate_details[word] = {
                "indices": indices,
                "count_in_new": len(indices),
                "exists_in_anki": True
            }
        
        return {
            "has_duplicates": len(duplicate_words) > 0,
            "duplicate_words": duplicate_words,
            "duplicate_details": duplicate_details,
            "new_words_count": len(new_words),
            "unique_new_words": len(new_words_set),
            "existing_words_count": len(existing_words),
            "duplicate_count": len(duplicate_words)
        }

    def check_duplicate_notes(self) -> dict:
        """
        檢查當前 deck 中是否有重複的 notes（根據單字欄位）
        
        Returns:
            dict: 包含重複資訊的字典，包含以下欄位：
                - has_duplicates: bool
                - duplicates: dict (word -> list of indices)
                - total_notes: int
                - unique_words: int
                - duplicate_count: int
        """
        if not hasattr(self.deck, 'notes') or len(self.deck.notes) == 0:
            return {
                "has_duplicates": False,
                "duplicates": {},
                "total_notes": 0,
                "unique_words": 0,
                "duplicate_count": 0
            }
        
        # 建立單字到 note 索引的對應關係
        word_to_indices = {}
        for idx, note in enumerate(self.deck.notes):
            word = note.fields[0] if len(note.fields) > 0 else ""
            if word and word.strip():
                word = word.strip()
                if word not in word_to_indices:
                    word_to_indices[word] = []
                word_to_indices[word].append(idx)
        
        # 找出重複的單字
        duplicates = {
            word: indices 
            for word, indices in word_to_indices.items() 
            if len(indices) > 1
        }
        
        return {
            "has_duplicates": len(duplicates) > 0,
            "duplicates": duplicates,
            "total_notes": len(self.deck.notes),
            "unique_words": len(word_to_indices),
            "duplicate_count": len(duplicates)
        }

    def export_deck_notes(self, deck_name: Optional[str] = None) -> dict:
        """
        匯出指定 deck 的 note 詳細資訊（已移除本地数据库连接，返回空结果）。
        """
        target_deck = deck_name if deck_name else self.deck_name
        logger.log(LogLevel.WARNING, f"本地 Anki 数据库连接已移除，无法导出 deck：{target_deck}")
        return {
            "deck_name": target_deck,
            "deck_id": None,
            "note_count": 0,
            "notes": []
        }


# ---------------- DEMO ----------------
if __name__ == "__main__":
    logic = AnkiLogic("MyTestDeck")
    model = logic.create_basic_model(1234567890)

    note = logic.create_anki_note(
        model,
        word="apple",
        pos="n.",
        meaning="一種水果",
        synonyms="",
        ex1_ori="I eat an apple every morning.",
        ex1_trans="我每天早上都吃一顆蘋果。",
        ex2_ori="Apples are rich in vitamins.",
        ex2_trans="蘋果富含維生素。",
        audio="apple.mp3",
        hint="This is a fruit."
    )

    logic.create_anki_card(note)
    logic.to_pack()
