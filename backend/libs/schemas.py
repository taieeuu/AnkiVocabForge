from pydantic import BaseModel, Field


class VocabCard(BaseModel):
    word:      str = Field(description="The vocabulary word")
    pos:       str = Field(description="Part of speech in target language (e.g. n., v., adj.)")
    meaning:   str = Field(description="Meaning of the word in target language")
    synonyms:  str = Field(description="3-5 synonyms with target language translations, as a single string")
    ex1_ori:   str = Field(description="First example sentence in source language")
    ex1_trans: str = Field(description="Translation of first example sentence")
    ex2_ori:   str = Field(description="Second example sentence in source language")
    ex2_trans: str = Field(description="Translation of second example sentence")
    hint:      str = Field(description="Explanation without using the word itself, in source language")


class VocabResponse(BaseModel):
    vocab: list[VocabCard]


class GrammarCard(BaseModel):
    grammar:   str = Field(description="Grammar pattern or rule title")
    usage:     str = Field(description="When and conditions to use this grammar, in source language")
    meaning:   str = Field(description="Meaning or explanation in target language")
    contrast:  str = Field(description="Comparison with similar grammar, explaining when to choose each")
    ex1_ori:   str = Field(description="First example sentence in source language")
    ex1_trans: str = Field(description="Translation of first example sentence")
    ex2_ori:   str = Field(description="Second example sentence in source language")
    ex2_trans: str = Field(description="Translation of second example sentence")


class GrammarResponse(BaseModel):
    grammar: list[GrammarCard]
