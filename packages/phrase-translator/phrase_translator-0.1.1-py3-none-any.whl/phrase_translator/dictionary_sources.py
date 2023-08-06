from collections import defaultdict

from phrase_translator.phrase_translator import DictionarySource
from phrase_translator.types import Language, Translation


class FileDictionarySource(DictionarySource):

    SEPARATOR: str = " -> "
    COMMENT: str = "#"
    LANGUAGE_INDICATOR = "lang: "

    def __init__(self, dictionary_files: [str]) -> None:
        self.__dictionary_files: [str] = dictionary_files
        self.__translations: {str: [Translation]} = defaultdict(list)

        self.__load_files()

    def __raise_syntax_error(self, index: int, line: str):
        raise SyntaxError("Malformed Translation on line " + str(index) + ": " + line)

    def __load_files(self) -> None:
        for dictionary_path in self.__dictionary_files:
            with open(dictionary_path, "r") as dictionary_file:
                source_language = Language.UNKNOWN
                target_language = Language.UNKNOWN

                for index, line in enumerate(dictionary_file):
                    if line.startswith(self.COMMENT):
                        continue

                    if line.startswith(self.LANGUAGE_INDICATOR):
                        lang_splits = line[len(self.LANGUAGE_INDICATOR) :].split(
                            self.SEPARATOR
                        )

                        if len(lang_splits) != 2:
                            self.__raise_syntax_error(index, line)

                        source_language = Language(lang_splits[0])
                        target_language = Language(lang_splits[1])

                    line = line.replace("\n", "")
                    splits = line.split(self.SEPARATOR)

                    if len(splits) != 2:
                        self.__raise_syntax_error(index, line)

                    self.__translations[splits[0]].append(
                        Translation(
                            splits[0], splits[1], source_language, target_language
                        )
                    )

    def _provide_translations(self, phrase: str) -> [Translation]:
        return self.__translations[phrase]
