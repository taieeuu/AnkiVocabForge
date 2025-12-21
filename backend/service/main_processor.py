# /service/main_processor.py
from service.parser_service import ParserService
from service.anki_service import AnkiService
from libs.gpt import GPTClient
from libs.logger import LogLevel, get_logger

logger = get_logger()

class MainProcessor:
    def run_article_mode(self, pdf_path: str, text_path: str, deck_name: str, target: str, source_lang: str = 'English', target_lang: str = 'Chinese', selected_images: list[str] = None, card_type: str = 'Basic', session_dir: str = None, api_key: str = None, model: str = None) -> str:
        """
        執行文章模式
        
        Args:
            pdf_path: PDF 檔案路徑（如果已解析過，可以為空）
            text_path: 文字檔案路徑
            deck_name: Deck 名稱
            target: 目標
            source_lang: 來源語言
            target_lang: 目標語言
            selected_images: 選擇的圖片路徑列表（如果為 None，則使用所有圖片）
        """
        logger.log(LogLevel.INFO, "開始解析文章與單字...")
        # 如果 PDF 已在 UI 中解析過，selected_images 會包含選擇的圖片
        # 如果沒有 selected_images，則在 parse_passage 中解析 PDF
        transed_vocab_list = ParserService.parse_passage(
            pdf_path,
            text_path,
            target,
            source_lang=source_lang,
            target_lang=target_lang,
            selected_images=selected_images,
            deck_name=deck_name,
            session_dir=session_dir,
            api_key=api_key,
            model=model
        )
        logger.log(LogLevel.INFO, f"解析完成，共 {len(transed_vocab_list)} 個單字")
        
        logger.log(LogLevel.INFO, "開始生成語音檔...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        word_list = [word["word"] for word in transed_vocab_list]
        gpt.gen_vocabs_voice(word_list)
        logger.log(LogLevel.INFO, f"語音檔生成完成，共 {len(word_list)} 個檔案")
        
        logger.log(LogLevel.INFO, "開始匯入 Anki...")
        msg = self._import_to_anki(transed_vocab_list, deck_name, card_type, session_dir=session_dir)
        logger.log(LogLevel.INFO, "Anki 匯入完成")
        return f"文章模式完成 ✅｜{msg}"

    def run_vocab_mode(self, text_path: str, target: str, deck_name: str, source_lang: str = 'English', target_lang: str = 'Chinese', card_type: str = 'Basic', session_dir: str = None, api_key: str = None, model: str = None) -> str:
        logger.log(LogLevel.INFO, "開始解析單字列表...")
        vocab_list = ParserService.parse_vocab_txt(
            text_path,
            target,
            source_lang=source_lang,
            target_lang=target_lang,
            deck_name=deck_name,
            session_dir=session_dir,
            api_key=api_key,
            model=model
        )
        logger.log(LogLevel.INFO, f"解析完成，共 {len(vocab_list)} 個單字")

        logger.log(LogLevel.INFO, "開始生成語音檔...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        word_list = [word["word"] for word in vocab_list]
        gpt.gen_vocabs_voice(word_list)
        logger.log(LogLevel.INFO, f"語音檔生成完成，共 {len(word_list)} 個檔案")

        logger.log(LogLevel.INFO, "開始匯入 Anki...")
        msg = self._import_to_anki(vocab_list, deck_name, card_type, session_dir=session_dir)
        logger.log(LogLevel.INFO, "Anki 匯入完成")
        return f"單純單字模式完成 ✅｜{msg}"

    def run_excel_mode(self, excel_path: str) -> str:
        vocab_list = ParserService.parse_excel(excel_path)
        msg = AnkiService.import_passage(vocab_list)
        return f"Excel 模式完成 ✅｜{msg}"

    def run_word_mode(self, word_path: str) -> str:
        vocab_list = ParserService.parse_word(word_path)
        msg = AnkiService.import_passage(vocab_list)
        return f"Word 模式完成 ✅｜{msg}"

    def run_ai_generate_mode(self, target: str, count: int, deck_name: str, source_lang: str = 'English', target_lang: str = 'Chinese', card_type: str = 'Basic', session_dir: str = None, api_key: str = None, model: str = None) -> str:
        """
        執行 AI 生成模式
        
        Args:
            target: 學習目標（必填）
            count: 要生成的單字數量
            deck_name: Deck 名稱
            source_lang: 來源語言
            target_lang: 目標語言
            
        Returns:
            str: 執行結果訊息
        """
        if not target or not target.strip():
            raise ValueError("AI 生成模式必須提供學習目標（target）")
        
        try:
            count_int = int(count) if count else 10
        except ValueError:
            count_int = 10
            logger.log(LogLevel.WARNING, f"無法解析數量參數，使用預設值：{count_int}")
        
        logger.log(LogLevel.INFO, "開始使用 AI 生成單字列表...")
        vocab_list = ParserService.generate_vocab_ai(target, count_int, source_lang=source_lang, target_lang=target_lang, session_dir=session_dir, api_key=api_key, model=model)
        logger.log(LogLevel.INFO, f"生成完成，共 {len(vocab_list)} 個單字")
        
        logger.log(LogLevel.INFO, "開始生成語音檔...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        word_list = [word["word"] for word in vocab_list]
        gpt.gen_vocabs_voice(word_list)
        logger.log(LogLevel.INFO, f"語音檔生成完成，共 {len(word_list)} 個檔案")
        
        logger.log(LogLevel.INFO, "開始匯入 Anki...")
        msg = self._import_to_anki(vocab_list, deck_name, card_type, session_dir=session_dir)
        logger.log(LogLevel.INFO, "Anki 匯入完成")
        return f"AI 生成模式完成 ✅｜{msg}"

    def _import_to_anki(self, vocab_list: list[dict], deck_name: str, card_type: str, session_dir: str = None) -> str:
        """
        根據卡片類型匯入到 Anki
        
        Args:
            vocab_list: 單字列表
            deck_name: Deck 名稱
            card_type: 卡片類型 ("Basic", "Cloze", "Basic+Cloze")
            
        Returns:
            str: 處理結果訊息
        """
        # 使用 "orig" 作為檔案名稱後綴，表示原始生成的版本
        if card_type == "Basic":
            return AnkiService.import_basic_model_notes(vocab_list, deck_name, session_dir=session_dir, filename_suffix='orig')
        elif card_type == "Cloze":
            return AnkiService.import_cloze_model_notes(vocab_list, deck_name, session_dir=session_dir, filename_suffix='orig')
        elif card_type == "Basic+Cloze":
            return AnkiService.import_basic_and_cloze_notes(vocab_list, deck_name, session_dir=session_dir, filename_suffix='orig')
        else:
            # 預設使用 Basic
            logger.log(LogLevel.WARNING, f"未知的卡片類型：{card_type}，使用 Basic 模式")
            return AnkiService.import_basic_model_notes(vocab_list, deck_name, session_dir=session_dir, filename_suffix='orig')