from datetime import datetime
import json
import os
from pathlib import Path

from libs.anki_logic import AnkiLogic
from libs.config import VOICE_DIR
from libs.logger import LogLevel, get_logger
from helpers.file_utils import safe_voice_filename


logger = get_logger()


class AnkiService:
    # ---------------- Import helpers ----------------
    @staticmethod
    def import_basic_model_notes(vocab_list: list[dict], deck_name: str = "MyTestDeck", session_dir: str = None, voice_dir: str = None, filename_suffix: str = None) -> str:
        """
        匯入基本模型的 notes 到 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            session_dir: 輸出目錄
            voice_dir: 語音檔案目錄（如果提供則優先使用，否則從 session_dir 或預設目錄查找）
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)

        # 確定 audio 路徑
        if voice_dir:
            # 如果明確指定了 voice_dir，使用它
            voice_dir = voice_dir
        elif session_dir:
            # 如果提供了 session_dir，先嘗試在 session_dir/voice 查找
            session_voice_dir = os.path.join(session_dir, "voice")
            if os.path.exists(session_voice_dir):
                voice_dir = session_voice_dir
            else:
                # 如果 session_dir/voice 不存在，嘗試在上一層的 orig/voice 查找
                parent_dir = os.path.dirname(session_dir)
                orig_voice_dir = os.path.join(parent_dir, "orig", "voice")
                if os.path.exists(orig_voice_dir):
                    voice_dir = orig_voice_dir
                else:
                    voice_dir = VOICE_DIR
        else:
            voice_dir = VOICE_DIR

        # 建立 model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki model 與 notes...")
        model = logic.get_or_create_basic_model()

        for v in vocab_list:
            word = v.get("word", "")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(voice_dir, audio_filename) if audio_filename else ""
            note = logic.create_anki_note(
                model=model,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=v.get("ex1_ori", ""),
                ex1_trans=v.get("ex1_trans", ""),
                ex2_ori=v.get("ex2_ori", ""),
                ex2_trans=v.get("ex2_trans", ""),
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 notes")
            
        # 產生 .apkg 檔案
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack(output_dir=session_dir)
        logger.log(LogLevel.INFO, f"✅ 打包完成：{logic.deck_name}.apkg")
        return f"打包完成，請在 Anki 中匯入 {logic.deck_name}.apkg"
        
    @staticmethod
    def confirm_and_pack_basic_model(vocab_list: list[dict], deck_name: str = "MyTestDeck") -> str:
        """
        確認重複單字後，打包 Basic 模型的 notes 到 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)

        # 建立 model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki model 與 notes...")
        model = logic.get_or_create_basic_model()

        for v in vocab_list:
            word = v.get("word", "")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(VOICE_DIR, audio_filename) if audio_filename else ""
            note = logic.create_anki_note(
                model=model,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=v.get("ex1_ori", ""),
                ex1_trans=v.get("ex1_trans", ""),
                ex2_ori=v.get("ex2_ori", ""),
                ex2_trans=v.get("ex2_trans", ""),
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 notes")
            
        # 產生 .apkg 檔案
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack()
        logger.log(LogLevel.INFO, f"✅ 打包完成：{logic.deck_name}.apkg")
        return f"打包完成，請在 Anki 中匯入 {logic.deck_name}.apkg"

    @staticmethod
    def confirm_and_pack_cloze_model(vocab_list: list[dict], deck_name: str = "MyTestDeck") -> str:
        """
        確認重複單字後，打包 Cloze 模型的 notes 到 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)
        
        # 建立 Cloze model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Cloze model 與 notes...")
        model = logic.get_or_create_cloze_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            ex1_ori = v.get("ex1_ori", "")
            ex1_trans = v.get("ex1_trans", "")
            ex2_ori = v.get("ex2_ori", "")
            ex2_trans = v.get("ex2_trans", "")
            
            # 將兩個例句中的單字轉換為 Cloze 格式
            import re
            
            # 處理第一個例句
            cloze_ex1 = ex1_ori
            if word and ex1_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex1 = pattern.sub(f"{{{{c1::{word}}}}}", ex1_ori, count=1)
            
            # 處理第二個例句
            cloze_ex2 = ex2_ori
            if word and ex2_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex2 = pattern.sub(f"{{{{c1::{word}}}}}", ex2_ori, count=1)
            
            # 將兩個例句和翻譯組合成一個 Text 欄位
            cloze_text = f"{cloze_ex1}\n{ex1_trans}\n\n{cloze_ex2}\n{ex2_trans}" if cloze_ex2 else f"{cloze_ex1}\n{ex1_trans}"
            
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(VOICE_DIR, audio_filename) if audio_filename else ""
            note = logic.create_cloze_note(
                model=model,
                text=cloze_text,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=ex1_ori,
                ex1_trans=ex1_trans,
                ex2_ori=ex2_ori,
                ex2_trans=ex2_trans,
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Cloze notes")
        
        # 產生 .apkg 檔案
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack()
        logger.log(LogLevel.INFO, f"✅ 打包完成：{logic.deck_name}.apkg")
        return f"打包完成，請在 Anki 中匯入 {logic.deck_name}.apkg"

    @staticmethod
    def confirm_and_pack_basic_and_cloze(vocab_list: list[dict], deck_name: str = "MyTestDeck") -> str:
        """
        確認重複單字後，同時打包 Basic 和 Cloze 模型的 notes 到同一個 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)
        
        # 建立 Basic model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Basic model 與 notes...")
        basic_model = logic.get_or_create_basic_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(VOICE_DIR, audio_filename) if audio_filename else ""
            note = logic.create_anki_note(
                model=basic_model,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=v.get("ex1_ori", ""),
                ex1_trans=v.get("ex1_trans", ""),
                ex2_ori=v.get("ex2_ori", ""),
                ex2_trans=v.get("ex2_trans", ""),
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Basic notes")
        
        # 建立 Cloze model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Cloze model 與 notes...")
        cloze_model = logic.get_or_create_cloze_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            ex1_ori = v.get("ex1_ori", "")
            ex1_trans = v.get("ex1_trans", "")
            ex2_ori = v.get("ex2_ori", "")
            ex2_trans = v.get("ex2_trans", "")
            
            # 將兩個例句中的單字轉換為 Cloze 格式
            import re
            
            # 處理第一個例句
            cloze_ex1 = ex1_ori
            if word and ex1_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex1 = pattern.sub(f"{{{{c1::{word}}}}}", ex1_ori, count=1)
            
            # 處理第二個例句
            cloze_ex2 = ex2_ori
            if word and ex2_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex2 = pattern.sub(f"{{{{c1::{word}}}}}", ex2_ori, count=1)
            
            # 將兩個例句和翻譯組合成一個 Text 欄位
            cloze_text = f"{cloze_ex1}\n{ex1_trans}\n\n{cloze_ex2}\n{ex2_trans}" if cloze_ex2 else f"{cloze_ex1}\n{ex1_trans}"
            logger.log(LogLevel.DEBUG, f"cloze_text: {cloze_text}")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(VOICE_DIR, audio_filename) if audio_filename else ""
            note = logic.create_cloze_note(
                model=cloze_model,
                text=cloze_text,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=ex1_ori,
                ex1_trans=ex1_trans,
                ex2_ori=ex2_ori,
                ex2_trans=ex2_trans,
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Cloze notes")
        
        # 產生 .apkg 檔案（包含兩種卡片）
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack()
        logger.log(LogLevel.INFO, f"✅ 打包完成：{logic.deck_name}.apkg")
        return f"打包完成，請在 Anki 中匯入 {logic.deck_name}.apkg（包含 Basic 和 Cloze 卡片）"

    @staticmethod
    def import_cloze_model_notes(vocab_list: list[dict], deck_name: str = "MyTestDeck", session_dir: str = None, voice_dir: str = None, filename_suffix: str = None) -> str:
        """
        匯入 Cloze 模型的 notes 到 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            session_dir: 輸出目錄
            voice_dir: 語音檔案目錄（如果提供則優先使用，否則從 session_dir 或預設目錄查找）
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)
        
        # 確定 audio 路徑
        if voice_dir:
            # 如果明確指定了 voice_dir，使用它
            voice_dir = voice_dir
        elif session_dir:
            # 如果提供了 session_dir，先嘗試在 session_dir/voice 查找
            session_voice_dir = os.path.join(session_dir, "voice")
            if os.path.exists(session_voice_dir):
                voice_dir = session_voice_dir
            else:
                # 如果 session_dir/voice 不存在，嘗試在上一層的 orig/voice 查找
                parent_dir = os.path.dirname(session_dir)
                orig_voice_dir = os.path.join(parent_dir, "orig", "voice")
                if os.path.exists(orig_voice_dir):
                    voice_dir = orig_voice_dir
                else:
                    voice_dir = VOICE_DIR
        else:
            voice_dir = VOICE_DIR
        
        # 建立 Cloze model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Cloze model 與 notes...")
        model = logic.get_or_create_cloze_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            ex1_ori = v.get("ex1_ori", "")
            ex1_trans = v.get("ex1_trans", "")
            ex2_ori = v.get("ex2_ori", "")
            ex2_trans = v.get("ex2_trans", "")
            
            # 將兩個例句中的單字轉換為 Cloze 格式
            import re
            
            # 處理第一個例句
            cloze_ex1 = ex1_ori
            if word and ex1_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex1 = pattern.sub(f"{{{{c1::{word}}}}}", ex1_ori, count=1)
            
            # 處理第二個例句
            cloze_ex2 = ex2_ori
            if word and ex2_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex2 = pattern.sub(f"{{{{c1::{word}}}}}", ex2_ori, count=1)
            
            # 將兩個例句和翻譯組合成一個 Text 欄位
            cloze_text = f"{cloze_ex1}\n{ex1_trans}\n\n{cloze_ex2}\n{ex2_trans}" if cloze_ex2 else f"{cloze_ex1}\n{ex1_trans}"
            
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(voice_dir, audio_filename) if audio_filename else ""
            note = logic.create_cloze_note(
                model=model,
                text=cloze_text,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=ex1_ori,
                ex1_trans=ex1_trans,
                ex2_ori=ex2_ori,
                ex2_trans=ex2_trans,
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Cloze notes")
        
        # 產生 .apkg 檔案
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack(output_dir=session_dir)
        logger.log(LogLevel.INFO, f"✅ 打包完成：{logic.deck_name}.apkg")
        return f"打包完成，請在 Anki 中匯入 {logic.deck_name}.apkg"
    
    @staticmethod
    def import_basic_and_cloze_notes(vocab_list: list[dict], deck_name: str = "MyTestDeck", session_dir: str = None, voice_dir: str = None, filename_suffix: str = None) -> str:
        """
        同時匯入 Basic 和 Cloze 模型的 notes 到同一個 Anki deck
        
        Args:
            vocab_list: 單字列表，每個元素為包含單字資訊的字典
            deck_name: deck 名稱
            session_dir: 輸出目錄
            voice_dir: 語音檔案目錄（如果提供則優先使用，否則從 session_dir 或預設目錄查找）
            
        Returns:
            str: 處理結果訊息
        """
        logic = AnkiLogic(deck_name)
        
        # 確定 audio 路徑
        if voice_dir:
            # 如果明確指定了 voice_dir，使用它
            voice_dir = voice_dir
        elif session_dir:
            # 如果提供了 session_dir，先嘗試在 session_dir/voice 查找
            session_voice_dir = os.path.join(session_dir, "voice")
            if os.path.exists(session_voice_dir):
                voice_dir = session_voice_dir
            else:
                # 如果 session_dir/voice 不存在，嘗試在上一層的 orig/voice 查找
                parent_dir = os.path.dirname(session_dir)
                orig_voice_dir = os.path.join(parent_dir, "orig", "voice")
                if os.path.exists(orig_voice_dir):
                    voice_dir = orig_voice_dir
                else:
                    voice_dir = VOICE_DIR
        else:
            voice_dir = VOICE_DIR
        
        # 建立 Basic model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Basic model 與 notes...")
        basic_model = logic.get_or_create_basic_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(voice_dir, audio_filename) if audio_filename else ""
            note = logic.create_anki_note(
                model=basic_model,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=v.get("ex1_ori", ""),
                ex1_trans=v.get("ex1_trans", ""),
                ex2_ori=v.get("ex2_ori", ""),
                ex2_trans=v.get("ex2_trans", ""),
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Basic notes")
        
        # 建立 Cloze model 並產生 notes
        logger.log(LogLevel.INFO, "建立 Anki Cloze model 與 notes...")
        cloze_model = logic.get_or_create_cloze_model()
        
        for v in vocab_list:
            word = v.get("word", "")
            ex1_ori = v.get("ex1_ori", "")
            ex1_trans = v.get("ex1_trans", "")
            ex2_ori = v.get("ex2_ori", "")
            ex2_trans = v.get("ex2_trans", "")
            
            # 將兩個例句中的單字轉換為 Cloze 格式
            import re
            
            # 處理第一個例句
            cloze_ex1 = ex1_ori
            if word and ex1_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex1 = pattern.sub(f"{{{{c1::{word}}}}}", ex1_ori, count=1)
            
            # 處理第二個例句
            cloze_ex2 = ex2_ori
            if word and ex2_ori:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cloze_ex2 = pattern.sub(f"{{{{c1::{word}}}}}", ex2_ori, count=1)
            
            # 將兩個例句和翻譯組合成一個 Text 欄位
            cloze_text = f"{cloze_ex1}\n{ex1_trans}\n\n{cloze_ex2}\n{ex2_trans}" if cloze_ex2 else f"{cloze_ex1}\n{ex1_trans}"
            logger.log(LogLevel.DEBUG, f"cloze_text: {cloze_text}")
            # 使用 safe_voice_filename 確保文件名與生成時一致
            audio_filename = f'{safe_voice_filename(word)}.mp3' if word else ""
            audio_path = os.path.join(voice_dir, audio_filename) if audio_filename else ""
            note = logic.create_cloze_note(
                model=cloze_model,
                text=cloze_text,
                word=word,
                pos=v.get("pos", ""),
                meaning=v.get("meaning", ""),
                synonyms=v.get("synonyms", ""),
                ex1_ori=ex1_ori,
                ex1_trans=ex1_trans,
                ex2_ori=ex2_ori,
                ex2_trans=ex2_trans,
                audio=audio_path,
                hint=v.get("hint", ""),
            )
            logic.create_anki_card(note)
        logger.log(LogLevel.INFO, f"✅ 已建立 {len(vocab_list)} 個 Cloze notes")
        
        # 產生 .apkg 檔案（包含兩種卡片）
        from helpers.file_utils import slugify
        logger.log(LogLevel.INFO, "打包 .apkg 檔案...")
        logic.to_pack(output_dir=session_dir, filename_suffix=filename_suffix)
        safe_deck_name = slugify(logic.deck_name)
        if filename_suffix:
            safe_suffix = slugify(filename_suffix)
            apkg_filename = f'{safe_deck_name}_{safe_suffix}.apkg'
        else:
            apkg_filename = f'{safe_deck_name}.apkg'
        logger.log(LogLevel.INFO, f"✅ 打包完成：{apkg_filename}")
        return f"打包完成，請在 Anki 中匯入 {apkg_filename}（包含 Basic 和 Cloze 卡片）"
    
    def read_vocab_json(self, json_path: str):
        """讀取單字 JSON 檔案"""
        logic = AnkiLogic()
        vocab_dict = logic.read_vocab_json(json_path)
        return vocab_dict

