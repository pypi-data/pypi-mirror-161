import json
from copy import copy
from enum import Enum


class Language(Enum):
    ENGLISH = ("en",)
    GERMAN = ("ge",)
    UNKNOWN = "unknown"


class Translation:
    def __init__(
        self,
        source_phrase: str,
        target_phrase: str,
        source_lang: Language,
        target_lang: Language,
    ) -> None:
        self.__source_phrase = source_phrase
        self.__target_phrase = target_phrase
        self.__source_lang = source_lang
        self.__target_lang = target_lang

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.to_json_string()

    def get_source_lang(self) -> Language:
        return self.__source_lang

    def get_target_lang(self) -> Language:
        return self.__target_lang

    def to_json_string(self) -> str:
        pass
