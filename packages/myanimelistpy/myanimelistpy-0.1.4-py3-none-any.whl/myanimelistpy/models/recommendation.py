from .node import Node
from .picture import Picture

class Recommendation(Node):
    def __init__(
        self, 
        id: int, 
        title: str, 
        main_picture: Picture, 
        num_recommendations: int
    ) -> None:
        """ Constructor.

        Parameters
        -----------
        id: :class:`int`
            ID of the anime.
        title: :class:`str`
            Title of the anime.
        main_picture: :class:`Picture`
            Main picture of the anime.
        num_recommendations: :class:`RelationTypeEnum`
            Number of recommendations of the anime.
        """

        super().__init__(id, title, main_picture)

        self.__num_recommendations = num_recommendations

    def getNumRecommendations(self) -> int:
        """ Number of recommendations.

        Returns
        -----------
        :class:`int`
        """

        return self.__num_recommendations