from .node import Node
from .picture import Picture
from ..enums.relationTypeEnum import RelationTypeEnum

class RelatedNode(Node):
    def __init__(
        self, 
        id: int,
        title: str,
        main_picture: Picture,
        relation_type: RelationTypeEnum
    ) -> None:
        """ Constructor.

        Parameters
        -----------
        id: :class:`int`
            ID of the anime or manga.
        title: :class:`str`
            Title of the anime or manga.
        main_picture: :class:`Picture`
            Main picture of the anime or manga.
        relation_type: :class:`RelationTypeEnum`
            Relation type of the anime or manga.
        """

        super().__init__(id, title, main_picture)
        
        self.__relation_type = relation_type

    def getRelationType(self) -> str:
        """ Anime or manga relation type.

        Returns
        -----------
        :class:`str`
        """

        return self.__relation_type.value