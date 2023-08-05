from .picture import Picture

class Node:
    def __init__(self, 
        id: int,
        title: str, 
        main_picture: dict, 
    ) -> None:
        """ Constructor

        Parameters
        -----------
        id: :class:`int`
            ID of the anime or manga.
        title: :class:`str`
            Title of the anime or manga.
        main_picture: :class:`dict`
            Main picture of the anime or manga.
        """

        self.__id           = id
        self.__title        = title
        self.__main_picture = Picture(
            large  = main_picture["large"], 
            medium = main_picture["medium"]
        )

    def getId(self) -> int:
        """ Anime or manga ID.

        Returns
        -----------
        :class:`int`
        """
        
        return self.__id

    def getTitle(self) -> str:
        """ Anime or manga ID.

        Returns
        -----------
        :class:`int`
        """
        
        return self.__title

    def getMainPicture(self) -> Picture:
        """ Anime or manga main picture.

        Returns
        -----------
        :class:`int`
        """
        
        return self.__main_picture