from abc import ABC, abstractmethod

from phrase_translator.types import Language, Translation


class DictionarySource(ABC):
    def get_translations(
        self,
        phrase: str,
        source_language: Language = None,
        target_language: Language = None,
    ) -> [Translation]:
        results = []

        for translation in self._provide_translations(phrase):
            if source_language and translation.get_source_lang() != source_language:
                continue

            if target_language and translation.get_target_lang() != target_language:
                continue

            results.append(translation)

        return results

    @abstractmethod
    def _provide_translations(self, phrase: str) -> [Translation]:
        pass


class PhraseTranslator:
    def __init__(
        self, source_language: Language = None, target_language: Language = None
    ) -> None:
        self.__dictionary_sources: [DictionarySource] = []

        self.__source_language = source_language
        self.__target_language = target_language

    def add_dictionary_source(self, dictionary_source: DictionarySource) -> None:
        self.__dictionary_sources.append(dictionary_source)

    def translate_phrase(self, phrase: str) -> [Translation]:
        results = []

        for dictionary_source in self.__dictionary_sources:
            results += dictionary_source.get_translations(
                phrase, self.__source_language, self.__target_language
            )

        return results

    def translate_phrases(self, phrases: [str]) -> [[Translation]]:
        results = [[]]

        for phrase in phrases:
            results.append(self.translate_phrase(phrase))

        return results
