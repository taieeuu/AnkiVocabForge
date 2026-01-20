# /service/parser_service.py
from libs.parser import Parser
from libs.gpt import GPTClient
from libs.config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE, GOAL_PROMPT, PASSAGE_IMAGE_DIR, GRAMMAR_PROMPT
from libs.logger import LogLevel, get_logger
from service.anki_service import AnkiService
import os

logger = get_logger()

class ParserService:
    @staticmethod
    def parse_passage(pdf_path: str, vocab_path: str, target: str, source_lang: str = 'English', target_lang: str = 'Chinese', selected_images: list[str] = None, deck_name: str | None = None, session_dir: str = None, api_key: str = None, model: str = None):
        """
        解析文章模式
        
        Args:
            pdf_path: PDF 檔案路徑（如果 selected_images 已提供，可以為空字串，不需要解析 PDF）
            vocab_path: 單字列表檔案路徑
            target: 目標
            source_lang: 來源語言
            target_lang: 目標語言
            selected_images: 選擇的圖片路徑列表（如果為 None，則需要 pdf_path 並解析 PDF 使用所有圖片）
        """
        logger.log(LogLevel.INFO, f"🚀 Start To Parsing Passage Mode ... ")
        
        parser = Parser(api_key=api_key, session_dir=session_dir)
        
        # 如果沒有提供選擇的圖片，則需要解析 PDF
        if selected_images is None:
            if not pdf_path:
                raise ValueError("❌ 請提供 PDF 檔案路徑或選擇的圖片列表")
            # 1) 解析 PDF 圖片 → 存到 outputs/passage_images/
            logger.log(LogLevel.INFO, "解析 PDF 檔案...")
            parser.parse_pdf(pdf_path)
            logger.log(LogLevel.INFO, "✅ PDF 解析完成")
        else:
            # 如果已提供選擇的圖片，使用該路徑的資料夾（用於後續處理，但實際上會直接使用 image_paths）
            parser.passage_image_path = os.path.dirname(selected_images[0]) if selected_images else PASSAGE_IMAGE_DIR
        
        logger.log(LogLevel.INFO, "解析單字列表...")
        parse_vocab_list = parser.parse_vocab_txt(vocab_path)
        logger.log(LogLevel.INFO, f"✅ 單字列表解析完成，共 {len(parse_vocab_list)} 個單字")

        # 所有單字都詢問 GPT（不過濾，因為需要考慮詞性差異）
        logger.log(LogLevel.INFO, f"呼叫 GPT 進行視覺理解與翻譯（共 {len(parse_vocab_list)} 個單字，包含可能重複的單字）...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        
        goal_prompt_section = ""
        if target:
            goal_prompt_section = GOAL_PROMPT.format(target=target)

        prompt = PROMPT_EN_PASSAGE_VOCAB_QUESTIONS.format(
            goal_prompt_section=goal_prompt_section,
            source_language=source_lang,
            target_language=target_lang,
            vocab_list="\n".join(parse_vocab_list)  # 使用所有單字，不過濾
        )
        logger.log(LogLevel.DEBUG, f"selected_images: {selected_images}")
        logger.log(LogLevel.DEBUG, f"prompt: {prompt}")
        # 如果有選擇的圖片，直接使用；否則從資料夾收集所有圖片
        transed_vocab_list = gpt.passage_with_question(
            passage_image_folder=parser.passage_image_path if not selected_images else None,
            question=prompt,
            image_paths=selected_images
        )
        logger.log(LogLevel.INFO, f"✅ GPT 處理完成，共 {len(transed_vocab_list)} 個單字")

        try:
            base = os.path.basename(vocab_path)
            stem, _ = os.path.splitext(base)
        except Exception:
            stem = None

        # 儲存 JSON 檔案
        logger.log(LogLevel.INFO, "儲存 JSON 檔案...")
        gpt.to_json(
            transed_vocab_list,
            mode="passage",
            source_lang=source_lang,
            target_lang=target_lang,
            filename_hint=stem,
        )
        logger.log(LogLevel.INFO, "✅ JSON 檔案儲存完成")
        
        return transed_vocab_list

    @staticmethod
    def parse_vocab_txt(vocab_path: str, target: str, source_lang: str = 'English', target_lang: str = 'Chinese', deck_name: str | None = None, session_dir: str = None, api_key: str = None, model: str = None):
        logger.log(LogLevel.INFO, "解析單字列表...")
        parser = Parser(api_key=api_key, session_dir=session_dir)
        vocab_list = parser.parse_vocab_txt(vocab_path)
        logger.log(LogLevel.INFO, f"✅ 單字列表解析完成，共 {len(vocab_list)} 個單字")

        # 所有單字都詢問 GPT（不過濾，因為需要考慮詞性差異）
        logger.log(LogLevel.INFO, f"呼叫 GPT 進行翻譯與擴充（共 {len(vocab_list)} 個單字，包含可能重複的單字）...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)

        goal_prompt_section = ""
        if target:
            goal_prompt_section = GOAL_PROMPT.format(target=target)

        prompt = PROMPT_EN_VOCAB.format(
            goal_prompt_section=goal_prompt_section,
            source_language=source_lang,
            target_language=target_lang,
            vocab_list="\n".join(vocab_list)  # 使用所有單字，不過濾
        )
        
        logger.log(LogLevel.DEBUG, f"prompt: {prompt}")
        transed_vocab_list = gpt.vocab_from_words(
            vocab_list,  # 使用所有單字，不過濾
            prompt=prompt
        )
        logger.log(LogLevel.INFO, f"✅ GPT 處理完成，共 {len(transed_vocab_list)} 個單字")

        try:
            base = os.path.basename(vocab_path)
            stem, _ = os.path.splitext(base)
        except Exception:
            stem = None

        logger.log(LogLevel.INFO, "儲存 JSON 檔案...")
        gpt.to_json(
            transed_vocab_list,
            mode="vocab",
            deck_name=deck_name,
            source_lang=source_lang,
            target_lang=target_lang,
            filename_hint=stem,
        )
        logger.log(LogLevel.INFO, "✅ JSON 檔案儲存完成")
        return transed_vocab_list

    @staticmethod
    def parse_word(word_path: str, api_key: str = None, session_dir: str = None):
        parser = Parser(api_key=api_key, session_dir=session_dir)
        parser.parse_word(word_path)
        return parser.word_list
    
    @staticmethod
    def parse_excel(excel_path: str, api_key: str = None, session_dir: str = None):
        """解析 Excel 文件（不需要 GPT Client，但為了保持一致性仍接受 api_key 參數）"""
        parser = Parser(api_key=api_key, session_dir=session_dir)
        return parser.parse_excel(excel_path)
    
    @staticmethod
    def generate_vocab_ai(target: str, count: int, source_lang: str = 'English', target_lang: str = 'Chinese', session_dir: str = None, api_key: str = None, model: str = None):
        """
        使用 AI 生成單字列表
        
        Args:
            target: 學習目標
            count: 要生成的單字數量
            source_lang: 來源語言
            target_lang: 目標語言
            
        Returns:
            List[Dict]: 生成的單字列表
        """
        logger.log(LogLevel.INFO, f"開始使用 AI 生成單字列表（目標：{target}，數量：{count}）...")
        
        # 格式化 prompt（與其他方法保持一致）
        goal_prompt_section = GOAL_PROMPT.format(target=target)
        prompt = PROMPT_AI_GENERATE.format(
            goal_prompt_section=goal_prompt_section,
            count=count,
            source_language=source_lang,
            target_language=target_lang
        )
        
        logger.log(LogLevel.DEBUG, f"prompt: {prompt}")
        
        # 呼叫 GPT 生成單字列表
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        vocab_list = gpt.generate_vocab_list(prompt=prompt)
        logger.log(LogLevel.INFO, f"✅ AI 生成完成，共 {len(vocab_list)} 個單字")
        
        
        # 儲存 JSON 檔案
        logger.log(LogLevel.INFO, "儲存 JSON 檔案...")
        gpt.to_json(
            vocab_list,
            mode="ai_generate",
            source_lang=source_lang,
            target_lang=target_lang,
            filename_hint=f"ai-generate-{target}-{count}w",
        )
        logger.log(LogLevel.INFO, "✅ JSON 檔案儲存完成")
        
        return vocab_list
    
    @staticmethod
    def generate_grammar_ai(target: str, count: int, source_lang: str = 'English', target_lang: str = 'Chinese', session_dir: str = None, api_key: str = None, model: str = None):
        """
        使用 AI 生成文法列表
        
        Args:
            target: 學習目標
            count: 要生成的文法數量
            source_lang: 來源語言
            target_lang: 目標語言
            
        Returns:
            List[Dict]: 生成的文法列表
        """
        logger.log(LogLevel.INFO, f"開始使用 AI 生成文法列表（目標：{target}，數量：{count}）...")
        
        # 格式化 prompt（與其他方法保持一致）
        goal_prompt_section = GOAL_PROMPT.format(target=target)
        prompt = GRAMMAR_PROMPT.format(
            goal_prompt_section=goal_prompt_section,
            count=count,
            source_language=source_lang,
            target_language=target_lang
        )
        
        logger.log(LogLevel.DEBUG, f"prompt: {prompt}")
        
        # 呼叫 GPT 生成文法列表
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)
        grammar_list = gpt.generate_grammar_list(prompt=prompt)
        logger.log(LogLevel.INFO, f"✅ AI 生成完成，共 {len(grammar_list)} 個文法")
        
        # 儲存 JSON 檔案
        logger.log(LogLevel.INFO, "儲存 JSON 檔案...")
        gpt.to_json(
            grammar_list,
            mode="grammar",
            source_lang=source_lang,
            target_lang=target_lang,
            filename_hint=f"grammar-{target}-{count}g",
        )
        logger.log(LogLevel.INFO, "✅ JSON 檔案儲存完成")
        
        return grammar_list
    
    @staticmethod
    def parse_grammar_txt(grammar_path: str, target: str, source_lang: str = 'English', target_lang: str = 'Chinese', deck_name: str | None = None, session_dir: str = None, api_key: str = None, model: str = None):
        """
        解析文法列表文件並生成文法卡片
        
        Args:
            grammar_path: 文法列表文件路徑
            target: 學習目標
            source_lang: 來源語言
            target_lang: 目標語言
            deck_name: Deck 名稱
            session_dir: 會話目錄
            api_key: API Key
            model: 模型名稱
            
        Returns:
            List[Dict]: 生成的文法列表
        """
        logger.log(LogLevel.INFO, "解析文法列表...")
        parser = Parser(api_key=api_key, session_dir=session_dir)
        grammar_list = parser.parse_vocab_txt(grammar_path)  # 重用現有的解析方法
        logger.log(LogLevel.INFO, f"✅ 文法列表解析完成，共 {len(grammar_list)} 個文法")

        # 所有文法都詢問 GPT
        logger.log(LogLevel.INFO, f"呼叫 GPT 進行文法擴充（共 {len(grammar_list)} 個文法）...")
        gpt = GPTClient(session_dir=session_dir, api_key=api_key, model=model)

        goal_prompt_section = ""
        if target:
            goal_prompt_section = GOAL_PROMPT.format(target=target)

        # 使用 GRAMMAR_PROMPT 但替換 {count} 為文法列表說明
        grammar_list_text = "\n".join(grammar_list)  # 使用所有文法，不過濾
        prompt_template = GRAMMAR_PROMPT.replace("{count}", str(len(grammar_list)))
        prompt = prompt_template.format(
            goal_prompt_section=goal_prompt_section,
            source_language=source_lang,
            target_language=target_lang
        )
        # 在 prompt 末尾添加文法列表
        prompt += f"\n\n我的文法如下：\n{grammar_list_text}"
        
        logger.log(LogLevel.DEBUG, f"prompt: {prompt}")
        transed_grammar_list = gpt.grammar_from_list(
            grammar_list,  # 使用所有文法，不過濾
            prompt=prompt
        )
        logger.log(LogLevel.INFO, f"✅ GPT 處理完成，共 {len(transed_grammar_list)} 個文法")

        try:
            base = os.path.basename(grammar_path)
            stem, _ = os.path.splitext(base)
        except Exception:
            stem = None

        logger.log(LogLevel.INFO, "儲存 JSON 檔案...")
        gpt.to_json(
            transed_grammar_list,
            mode="grammar",
            deck_name=deck_name,
            source_lang=source_lang,
            target_lang=target_lang,
            filename_hint=stem,
        )
        logger.log(LogLevel.INFO, "✅ JSON 檔案儲存完成")
        return transed_grammar_list
