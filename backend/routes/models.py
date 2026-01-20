"""
生成 API 的 Pydantic 模型定義

每個 API 端點都有獨立的請求模型，提供更好的類型安全和驗證
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AudioSettings(BaseModel):
    """音頻設置"""
    enabled: bool = Field(default=False, description="是否啟用音頻生成")
    voice: str = Field(default="alloy", description="語音類型")


class GenerationSettings(BaseModel):
    """生成設置"""
    apiKey: Optional[str] = Field(default=None, description="OpenAI API Key")
    model: Optional[str] = Field(default=None, description="GPT 模型名稱")
    language: Optional[str] = Field(default=None, description="目標語言")
    sourceLang: Optional[str] = Field(default=None, description="源語言")
    audio: Optional[AudioSettings] = Field(default=None, description="音頻設置")


class ImageData(BaseModel):
    """圖片數據"""
    id: Optional[int] = Field(default=None, description="圖片 ID")
    src: Optional[str] = Field(default=None, description="圖片 URL")
    path: Optional[str] = Field(default=None, description="圖片路徑")
    selected: bool = Field(default=True, description="是否選中")


class BaseGenerationRequest(BaseModel):
    """基礎生成請求模型
    
    包含所有生成 API 共用的字段
    """
    deckName: str = Field(default="TestDeck", description="牌組名稱")
    noteName: str = Field(default="Basic", description="筆記類型名稱")
    userGoal: Optional[str] = Field(default="", description="使用者目標/指示")
    tags: Optional[str] = Field(default="", description="標籤（空格分隔）")
    sessionId: Optional[str] = Field(default=None, description="Session ID")
    settings: GenerationSettings = Field(..., description="生成設置")


class ArticleGenerationRequest(BaseGenerationRequest):
    """文章生成請求模型
    
    從上傳的文章（PDF/圖片）和單字列表生成 Anki 卡片
    """
    images: List[ImageData] = Field(default_factory=list, description="選中的圖片列表")
    vocabList: Optional[Any] = Field(default=None, description="單字列表（對象或字符串格式）")


class VocabGenerationRequest(BaseGenerationRequest):
    """單字生成請求模型
    
    從單字列表文件生成 Anki 卡片
    """
    vocabList: Optional[Any] = Field(default=None, description="單字列表（對象或字符串格式）")


class AIGenerationRequest(BaseGenerationRequest):
    """AI 生成請求模型
    
    使用 AI 根據主題生成單字或文法卡片
    """
    topic: str = Field(..., description="生成主題（必填）")
    count: int = Field(default=10, ge=1, le=100, description="生成數量")
    contentType: Optional[str] = Field(default="Word", description="內容類型：Word 或 Grammar")
    
    class Config:
        # 為 noteName 添加額外說明（僅用於 Word 類型）
        schema_extra = {
            "example": {
                "deckName": "TestDeck",
                "noteName": "Basic",
                "userGoal": "",
                "tags": "",
                "sessionId": None,
                "settings": {
                    "apiKey": "sk-...",
                    "model": "gpt-4o-mini",
                    "language": "Chinese",
                    "sourceLang": "English"
                },
                "topic": "Japanese N4 vocabulary",
                "count": 10,
                "contentType": "Word"
            }
        }


class GrammarGenerationRequest(BaseGenerationRequest):
    """文法生成請求模型
    
    從文法列表文件生成 Anki 卡片（僅支持文件輸入）
    """
    grammarFile: Optional[str] = Field(default=None, description="文法文件內容（字符串格式）")


class CardData(BaseModel):
    """卡片數據"""
    id: int = Field(..., description="卡片 ID")
    front: str = Field(default="", description="正面內容")
    back: str = Field(default="", description="背面內容")
    sentence: Optional[str] = Field(default=None, description="例句")
    word: Optional[str] = Field(default=None, description="單字")
    pos: Optional[str] = Field(default=None, description="詞性")
    meaning: Optional[str] = Field(default=None, description="意思")
    synonyms: Optional[str] = Field(default=None, description="同義詞")
    grammar: Optional[str] = Field(default=None, description="文法")
    pattern: Optional[str] = Field(default=None, description="句型")
    usage: Optional[str] = Field(default=None, description="用法")
    contrast: Optional[str] = Field(default=None, description="對比")
    ex1_ori: Optional[str] = Field(default=None, description="例句1原文")
    ex1_trans: Optional[str] = Field(default=None, description="例句1翻譯")
    ex2_ori: Optional[str] = Field(default=None, description="例句2原文")
    ex2_trans: Optional[str] = Field(default=None, description="例句2翻譯")
    hint: Optional[str] = Field(default=None, description="提示")


class GenerationResponse(BaseModel):
    """生成響應模型"""
    success: bool = Field(..., description="是否成功")
    cards: List[CardData] = Field(default_factory=list, description="生成的卡片列表")
    message: Optional[str] = Field(default=None, description="響應訊息")
    sessionId: Optional[str] = Field(default=None, description="Session ID")


class ErrorResponse(BaseModel):
    """錯誤響應模型"""
    success: bool = Field(default=False, description="是否成功")
    error: str = Field(..., description="錯誤類型")
    details: str = Field(..., description="錯誤詳情")

