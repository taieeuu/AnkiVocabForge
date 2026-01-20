from docx import Document
from .gpt import GPTClient
import re
import fitz
import pandas as pd
from .config import PASSAGE_IMAGE_DIR
from .logger import LogLevel, get_logger

logger = get_logger()

class Parser:
    def __init__(self, ori_language: str = "en", trans_language: str = "zh", api_key: str = None, session_dir: str = None):
        # 延遲初始化 GPTClient，只有在需要時才創建
        self._api_key = api_key
        self._session_dir = session_dir
        self._gpt_client = None
        # 如果提供了 session_dir，將圖片儲存在 session_dir 中，否則使用預設目錄
        if session_dir:
            from pathlib import Path
            self.passage_image_path = str(Path(session_dir))
        else:
            self.passage_image_path = PASSAGE_IMAGE_DIR
        self.ori_language = ori_language
        self.trans_language = trans_language
    
    @property
    def gpt_client(self):
        """延遲初始化 GPTClient"""
        if self._gpt_client is None:
            self._gpt_client = GPTClient(api_key=self._api_key, session_dir=self._session_dir)
        return self._gpt_client
    
    def execute(self, *args, **kwargs):

        if kwargs.get("parser_type") == "passage":
            self.parse_pdf(kwargs.get("pdf_path"))
            vocab_list = self.gpt_client.passage_with_question(self.passage_image_path)
            logger.log(LogLevel.DEBUG, f"vocab_list: {vocab_list}")
            return vocab_list

        elif kwargs.get("parser_type") == "word":
            ...

        elif kwargs.get("parser_type") == "excel":
            ...
        

    def parse_word(self, path: str):
        doc = Document(path)

        current_word = None
        word_data = {}
        all_words = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            logger.log(LogLevel.DEBUG, f"\n =====> 原始段落: {text}")
            logger.log(LogLevel.DISPLAY, "-"*80)

            # 1️⃣ 檢查是否為新單字段落
            found_word = self._find_docx_word(text)
            if found_word:
                # 儲存前一個單字資料
                if current_word and word_data:
                    all_words.append(word_data)

                current_word = found_word
                word_data = {
                    "word": current_word,
                    "chinese": "",
                    "pos": "",
                    "examples": []
                }
                logger.log(LogLevel.INFO, f"找到新單字: {current_word}")


                chinese = self._find_docx_chinese(text)

                if chinese and word_data:
                    word_data["chinese"] = chinese
                    logger.log(LogLevel.INFO, f"中文解釋: {chinese}")


                pos = self._find_docx_pos(text)
                if pos and word_data:
                    word_data["pos"] = pos
                    logger.log(LogLevel.INFO, f"詞性: {pos}")


            # 4️⃣ Bullet 例句（中英對照）
            en, zh = self._find_docx_bulleted_list(para)
            if en and zh and word_data:
                word_data["examples"].append({"en": en, "zh": zh})
                logger.log(LogLevel.INFO, f"📍Bullet例句: EN='{en}' / ZH='{zh}'")
                continue

        # 最後一個單字加進來
        if current_word and word_data:
            all_words.append(word_data)

        logger.log(LogLevel.SUCCESS, f"\n 總共解析 {len(all_words)} 個單字")
        return all_words
    
    def _find_docx_bulleted_list(self, para):
        """判斷是否為 bullet list 並拆中英"""
        is_bullet = bool(para._element.xpath(".//w:numPr"))
        if is_bullet:
            lines = [line.strip() for line in para.text.splitlines() if line.strip()]
            if len(lines) == 2:
                en, zh = lines
                return en, zh
        return None, None

    def _find_docx_pos(self, text: str):
        pos_match = re.search(r'詞性：(.+)', text)
        return pos_match.group(1).strip() if pos_match else None

    def _find_docx_chinese(self, text: str):
        chinese_match = re.search(r'中文：(.+)', text)
        return chinese_match.group(1).strip() if chinese_match else None

    def _find_docx_word(self, text: str):
        word_match = re.match(r'^(\d+)\.\s+(\w+)', text)
        return word_match.group(2) if word_match else None

    def parse_pdf_text(self, path: str):
        """解析 pdf 的文字"""
        ...

    def parse_pdf(self, path: str):
        # 先嘗試文字；若無文字再抽圖
        text_found = False
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for p in pdf.pages:
                    if p.extract_text():
                        text_found = True
                        break
        except Exception:
            text_found = False

        if text_found:
            # TODO: 之後如需直接以文字進 LLM，可在此實作
            return
        self.parse_pdf_image(path)

    def parse_pdf_image(self, pdf_path: str):
        """解析 pdf 的圖片"""
        import os
        from pathlib import Path
        
        os.makedirs(self.passage_image_path, exist_ok=True)

        # 取得 PDF 檔案名稱（不含副檔名）
        pdf_name = Path(pdf_path).stem
        
        doc = fitz.open(pdf_path)
        image_counter = 1  # 圖片計數器，從 p1 開始
        
        for page_index in range(len(doc)):
            page = doc[page_index]
            images = page.get_images(full=True)
            logger.log(LogLevel.INFO, f"第 {page_index + 1} 頁包含 {len(images)} 張圖片")

            for image_index, img in enumerate(images):
                xref = img[0]  # 取出圖像的 XREF ID
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # 儲存圖片：PDF 名稱 + p1, p2, p3...
                from helpers.file_utils import slugify
                safe_pdf_name = slugify(pdf_name)
                image_filename = f"{safe_pdf_name}_p{image_counter}.{image_ext}"
                out_path = os.path.join(self.passage_image_path, image_filename)
                with open(out_path, "wb") as f:
                    f.write(image_bytes)

                logger.log(LogLevel.SUCCESS, f"儲存圖片：{image_filename}")
                image_counter += 1  # 遞增計數器

    def parse_excel(self, path: str):
        if not path:
            raise ValueError("請提供 Excel 檔案路徑。")

        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
        except Exception as e:
            raise ValueError(f"無法讀取 Excel：{e}") from e

        if df.empty:
            return []

        alias_map = {
            "word": ("word", "單字", "vocab", "詞彙"),
            "pos": ("pos", "詞性"),
            "meaning": ("meaning", "意思", "中文意思"),
            "synonyms": ("synonyms", "同義詞"),
            "ex1_ori": ("ex1_ori", "例句1", "例句1英文", "例句一英文"),
            "ex1_trans": ("ex1_trans", "例句1翻譯", "例句1中文", "例句一中文"),
            "ex2_ori": ("ex2_ori", "例句2", "例句2英文", "例句二英文"),
            "ex2_trans": ("ex2_trans", "例句2翻譯", "例句2中文", "例句二中文"),
            "audio": ("audio", "語音", "音檔"),
        }

        def normalize(name: str) -> str:
            return str(name).strip().lower()

        normalized_columns = {normalize(col): col for col in df.columns}

        column_mapping = {}
        for field, aliases in alias_map.items():
            for alias in aliases:
                normalized_alias = normalize(alias)
                if normalized_alias in normalized_columns:
                    column_mapping[field] = normalized_columns[normalized_alias]
                    break

        if "word" not in column_mapping:
            raise ValueError("Excel 檔案缺少必需欄位：word（或對應同義名稱）。")

        vocab_fields = [
            "word",
            "pos",
            "meaning",
            "synonyms",
            "ex1_ori",
            "ex1_trans",
            "ex2_ori",
            "ex2_trans",
            "audio",
        ]

        vocab_list = []
        for _, row in df.iterrows():
            word = row.get(column_mapping["word"], "")
            if pd.isna(word) or not str(word).strip():
                continue

            entry = {}
            for field in vocab_fields:
                source_col = column_mapping.get(field)
                value = row.get(source_col, "") if source_col else ""
                entry[field] = "" if pd.isna(value) else str(value).strip()
            vocab_list.append(entry)

        return vocab_list

    def parse_vocab_txt(self, vocab_path: str):
        """
        讀取詞彙清單檔案，並回傳詞彙清單
        """
        with open(vocab_path, "r", encoding="utf-8") as f:
            text = f.read()

        vocab_list = [word for word in text.splitlines()]
        return vocab_list

    def to_excel(self, data: list[dict]):
        ...


if __name__ == "__main__":
    parser = Parser()
    parser.execute(parser_type="passage", pdf_path="./sample/IELTS 19 Test 1 Reading Passage 1 題目-1.pdf")
