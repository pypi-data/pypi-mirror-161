from typing import List


class AlternativeTitles:
    def __init__(self, synonyms: List[str], english: str, japanese: str) -> None:
        """ Constructor.

        Parameters
        -----------
        synonyms: :class:`List[str]`
            A list of title synonyms.
        english: :class:`str`
            English version of the title.
        japanese: :class:`str`
            Japanese version of the title.
        """

        self.__synonyms = synonyms
        self.__english  = english
        self.__japanese = japanese
        
    def getSynonyms(self) -> List[str]:
        """ List of synonyms.

        Returns
        -----------
        :class:`List[str]`
        """

        return self.__synonyms

    def getEnglish(self) -> str:
        """ English version.
        
        Returns
        -----------
        :class:`str`
        """

        return self.__english

    def getJapanese(self) -> str:
        """ Japanese version.
        
        Returns
        -----------
        :class:`str`
        """

        return self.__japanese