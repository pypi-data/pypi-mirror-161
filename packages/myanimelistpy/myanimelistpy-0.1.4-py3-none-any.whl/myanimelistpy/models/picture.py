
class Picture:
    def __init__(self, large: str, medium: str) -> None:
        """ Constructor.

         Parameters
        -----------
        large: :class:`str`
            The URI of an anime's large picture.
        medium: :class:`str`
            The URI of an anime's medium picture.
        """

        self.__large  = large
        self.__medium = medium 

    def getLarge(self) -> str:
        """ Large size picture.

        Returns
        -----------
        :class:`str`
        """

        return self.__large

    def getMedium(self) -> str:
        """ Medium size picture.

        Returns
        -----------
        :class:`str`
        """

        return self.__medium