from pydantic import BaseModel, Field


class VocabCard(BaseModel):
    word:      str = Field(description="目標單字")
    pos:       str = Field(description="母語的詞性（例如：n., v., adj., adv., prep., conj.）")
    meaning:   str = Field(description="單字在母語中的意思")
    synonyms:  str = Field(description="3-5 個同義詞及其母語翻譯，以單一字串呈現")
    ex1_ori:   str = Field(description="第一個例句（學習語言）")
    ex1_trans: str = Field(description="第一個例句的翻譯")
    ex2_ori:   str = Field(description="第二個例句（學習語言）")
    ex2_trans: str = Field(description="第二個例句的翻譯")
    hint:      str = Field(description="不使用該單字本身的說明，以學習語言撰寫")


class VocabResponse(BaseModel):
    vocab: list[VocabCard]


class GrammarCard(BaseModel):
    grammar:   str = Field(description="文法規則或句型的標題")
    usage:     str = Field(description="此文法的使用時機與條件，以學習語言撰寫")
    meaning:   str = Field(description="母語的意思或說明")
    contrast:  str = Field(description="與相似文法的比較，說明各自的使用時機")
    ex1_ori:   str = Field(description="第一個例句（學習語言）")
    ex1_trans: str = Field(description="第一個例句的翻譯")
    ex2_ori:   str = Field(description="第二個例句（學習語言）")
    ex2_trans: str = Field(description="第二個例句的翻譯")


class GrammarResponse(BaseModel):
    grammar: list[GrammarCard]
