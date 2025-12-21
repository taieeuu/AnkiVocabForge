from openai import OpenAI
import base64
from typing import List, Dict
import json
import os
import glob
from .config import PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, WORD_SCHEMA, TRANSED_VOCAB_DIR, PROMPT_EN_VOCAB, PROMPT_AI_GENERATE
from datetime import datetime
from .config import VOICE_DIR, AI_MODEL, OPENAI_API_KEY
from helpers.file_utils import slugify
from .logger import LogLevel, get_logger

logger = get_logger()


class GPTClient:
    def __init__(self, model: str = None, session_dir: str = None, api_key: str = None):
        """
        初始化 GPT 客戶端。
        :param model: 預設使用 AI_MODEL，可視需要改成其他模型。
        :param session_dir: 會話目錄路徑，如果提供則將文件保存到此目錄
        :param api_key: OpenAI API Key（優先使用此參數，如果未提供則從環境變數讀取）
        """
        # 優先順序：參數 -> 環境變數
        if api_key:
            final_api_key = api_key
        else:
            final_api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        
        if not final_api_key:
            raise RuntimeError("未設定 OPENAI_API_KEY，請在參數或環境變數中配置。")
        
        self.client = OpenAI(api_key=final_api_key)
        # 優先使用環境變數中的模型，否則使用參數或預設值
        self.model = model

        # 如果提供了 session_dir，使用它作為輸出目錄；否則使用默認目錄
        if session_dir:
            self.voice_output_path = os.path.join(session_dir, "voice")
            self.transed_vocab_path = session_dir
        else:
            self.voice_output_path = VOICE_DIR
            self.transed_vocab_path = TRANSED_VOCAB_DIR

        for p in (self.voice_output_path, self.transed_vocab_path):
            os.makedirs(p, exist_ok=True)
        
    def _encode_image(self, image_path: str) -> str:
        """
        將圖片轉成 Base64
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def passage_with_question(self, passage_image_folder: str = None, question: str = PROMPT_EN_PASSAGE_VOCAB_QUESTIONS, image_paths: list[str] = None):
        """
        收集圖片，並生成問題，最後呼叫 GPT 生成詞彙清單並回傳
        
        Args:
            passage_image_folder: 圖片資料夾路徑（如果未提供 image_paths）
            question: 問題提示
            image_paths: 指定的圖片路徑列表（優先使用）
        """
        # 如果提供了指定的圖片列表，直接使用
        if image_paths:
            if not image_paths:
                raise ValueError("❌ 未選擇任何圖片")
        else:
            # 否則從資料夾收集所有圖片
            if not passage_image_folder:
                raise ValueError("❌ 請提供圖片資料夾路徑或圖片列表")
            image_paths = sorted(
                glob.glob(os.path.join(passage_image_folder, "*.jpg")) +
                glob.glob(os.path.join(passage_image_folder, "*.jpeg")) +
                glob.glob(os.path.join(passage_image_folder, "*.png"))
            )
            if not image_paths:
                raise ValueError(f"❌ 資料夾 {passage_image_folder} 裡沒有圖片")

        contents = [{"type": "text", "text": "請閱讀以下的英文文章圖片內容。"}]
        for img in image_paths:
            contents.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(img)}"}
            })
        
        contents.append({"type": "text", "text": question})

        logger.log(LogLevel.INFO, "生成中...")

        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": contents}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "vocab_list",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": WORD_SCHEMA,
                        "required": ["vocab"]
                    },
                    "strict": True
                }
            }
        )

        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")
        
        raw = res.choices[0].message.content
        try:
            obj = json.loads(raw)       # 這裡一定是 object（因為 schema）
            return obj.get("vocab", []) # 只回傳你要的 array
        except json.JSONDecodeError:
            logger.log(LogLevel.ERROR, f"GPT 回傳非合法 JSON，原始輸出：\n{raw}")
            return []

    def vocab_from_words(self, words: List[str], prompt: str = PROMPT_EN_VOCAB):
        """
        給定單字清單，請 GPT 依 WORD_SCHEMA 產生完整詞彙資料（pos/meaning/例句）。
        """
        words = [w.strip() for w in words if isinstance(w, str) and w.strip()]
        if not words:
            return []

        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "vocab_list",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": WORD_SCHEMA,
                        "required": ["vocab"]
                    },
                    "strict": True
                }
            },
        )
        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")
        
        raw = res.choices[0].message.content
        try:
            obj = json.loads(raw)
            return obj.get("vocab", [])
        except json.JSONDecodeError:
            logger.log(LogLevel.WARNING, f"⚠️ GPT 回傳非合法 JSON，原始輸出：\n{raw}")
            return []

    def gen_voice(self, text: str):
        """
        生成語音檔案
        """
        from helpers.file_utils import safe_voice_filename
        
        os.makedirs(self.voice_output_path, exist_ok=True)
        # 清理文件名，只替換路徑分隔符，保留其他字符
        safe_filename = safe_voice_filename(text)
        file_path = os.path.join(self.voice_output_path, f"{safe_filename}.mp3")
        
        # 檢查檔案是否已存在
        if os.path.exists(file_path):
            logger.log(LogLevel.INFO, f"⏭️  語音檔已存在，跳過生成: {file_path}")
            return
        
        res = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",  # 可換: 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer', 'coral', 'verse', 'ballad', 'ash', 'sage', 'marin', and 'cedar'
            input=text
        )
        with open(file_path, "wb") as f:
            f.write(res.read())

        logger.log(LogLevel.SUCCESS, f"✅ 已生成語音檔: {file_path}")
        
    def gen_vocabs_voice(self, vocab_list: List[str]):
        """
        將詞彙清單轉成語音檔案
        """
        os.makedirs(self.voice_output_path, exist_ok=True)
        count = 0
        for vocab in vocab_list:
            if vocab:
                self.gen_voice(vocab)
                count += 1
        logger.log(LogLevel.SUCCESS, f"已生成 {count} 個語音檔")
    
    def generate_vocab_list(self, prompt: str = PROMPT_AI_GENERATE):
        """
        根據提供的 prompt 生成單字列表
        
        Args:
            prompt: 已格式化好的提示文字
            
        Returns:
            List[Dict]: 生成的單字列表
        """
        logger.log(LogLevel.INFO, "正在生成單字...")
        
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "vocab_list",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": WORD_SCHEMA,
                        "required": ["vocab"]
                    },
                    "strict": True
                }
            },
        )
        
        # 記錄 token 使用量
        if hasattr(res, 'usage') and res.usage:
            usage = res.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            logger.log(LogLevel.INFO, f"Token 使用量 - 輸入: {prompt_tokens}, 輸出: {completion_tokens}, 總計: {total_tokens}")
        
        raw = res.choices[0].message.content
        try:
            obj = json.loads(raw)
            vocab_list = obj.get("vocab", [])
            logger.log(LogLevel.SUCCESS, f"✅ 成功生成 {len(vocab_list)} 個單字")
            return vocab_list
        except json.JSONDecodeError:
            logger.log(LogLevel.ERROR, f"GPT 回傳非合法 JSON，原始輸出：\n{raw}")
            return []
    
    def to_json(self, data: List[Dict], *, mode: str = "vocab", deck_name: str | None = None,
                source_lang: str | None = None, target_lang: str | None = None,
                filename_hint: str | None = None) -> str:
        """
        將詞彙清單存成 JSON 檔案。

        - 當提供 filename_hint 時：
          檔名為 `{filename_hint}-{%Y%m%d_%H%M%S}.json`
        - 若未提供 filename_hint，則使用具辨識度命名（模式/字數/語言/時間）。

        :return: 檔名（含副檔名，不含路徑）
        """
        # 優先使用 filename_hint 命名
        if filename_hint:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            base = f"{slugify(filename_hint)}-{ts}.json"
            out_path = os.path.join(self.transed_vocab_path, base)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.log(LogLevel.SUCCESS, f"已輸出 JSON：{out_path}")
            return base

        # 預設：具辨識度的命名（舊規則）
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        count = len(data) if isinstance(data, list) else 0
        mode_part = slugify(mode or "vocab")
        deck_part = slugify(deck_name) if deck_name else None
        lang_part = None
        if source_lang or target_lang:
            lang_part = f"{slugify(source_lang or '')}-{slugify(target_lang or '')}".strip('-')
        parts = [mode_part]
        if deck_part:
            parts.append(deck_part)
        if count:
            parts.append(f"{count}w")
        if lang_part:
            parts.append(lang_part)
        parts.append(ts)

        filename = "-".join([p for p in parts if p]) + ".json"
        out_path = os.path.join(self.transed_vocab_path, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.log(LogLevel.SUCCESS, f"已輸出 JSON：{out_path}")
        return filename

if __name__ == "__main__":
    gpt = GPTClient(model="gpt-4o-mini")

    text_path = "./sample_vocab.txt"
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()
    vocab_list = [word for word in text.splitlines()]
    logger.log(LogLevel.DEBUG, str(vocab_list))
    gpt.gen_vocabs_voice(vocab_list)
