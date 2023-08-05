from typing import List

from .node import Node
from ..enums.nsfwEnum import NsfwEnum
from .picture import Picture
from .alternativeTitles import AlternativeTitles
from .genre import Genre
from ..enums.mediaTypeEnum import MediaTypeEnum
from ..enums.airingStatusEnum import AiringStatusEnum
from .season import Season
from .broadcast import Broadcast
from ..enums.sourceEnum import SourceEnum
from ..enums.ratingEnum import RatingEnum
from .studio import Studio
from .relatedNode import RelatedNode
from .recommendation import Recommendation
from .statistics import Statistics
from ..enums.dayWeekEnum import DayWeekEnum
from ..enums.relationTypeEnum import RelationTypeEnum
from ..enums.seasonEnum import SeasonEnum
from .statisticsStatus import StatisticsStatus

class Anime(Node):
    def __init__(
        self,
        node: dict,
        fields: List[str]
    ) -> None:
        """ Constructor.

        Parameters
        -----------
        node: :class:`dict`
            The JSON object anime.
        fields: :class:`List[str]`
            The fields used for the request.
        """

        super().__init__(
            id           = node["id"], 
            title        = node["title"], 
            main_picture = node["main_picture"]
        )

        self.__alternative_titles       = None
        self.__start_date               = None
        self.__end_date                 = None
        self.__synopsis                 = None
        self.__mean                     = None
        self.__rank                     = None
        self.__popularity               = None
        self.__num_list_users           = None
        self.__num_scoring_users        = None
        self.__nsfw                     = None
        self.__genres                   = None
        self.__created_at               = None
        self.__updated_at               = None
        self.__media_type               = None
        self.__status                   = None
        self.__num_episodes             = None
        self.__start_season             = None
        self.__broadcast                = None
        self.__source                   = None
        self.__average_episode_duration = None
        self.__rating                   = None
        self.__studios                  = None
        self.__pictures                 = None # Cannot contain this field in a list.
        self.__background               = None # Cannot contain this field in a list.
        self.__related_anime            = None # Cannot contain this field in a list.
        self.__related_manga            = None # Cannot contain this field in a list.
        self.__recommendations          = None # Cannot contain this field in a list.
        self.__statistics               = None # Cannot contain this field in a list.

        self.__setFields(node=node, fields=fields)

    def __setFields(self, node: dict, fields: List[str]) -> None:
        """ Set the class attributes values using the fields.

        Parameters
        -----------
        node: :class:`dict`
            The JSON 'node' object sent by the MyAnimeList API.
        fields: :class:`List[str]`
            The fields used in the request.
        """

        for field in fields:
            match field:
                case "alternative_titles":
                    alternative_titles: dict = node["alternative_titles"]

                    synonyms: List[str] = alternative_titles["synonyms"]
                    english: str        = alternative_titles["en"]
                    japanese: str       = alternative_titles["ja"]

                    self.__alternative_titles = AlternativeTitles(
                        synonyms = synonyms,
                        english  = english,
                        japanese = japanese
                    )

                    pass
                case "start_date":
                    self.__start_date: str = node["start_date"]

                    pass
                case "end_date":
                    self.__end_date: str = node["end_date"]

                    pass
                case "synopsis":
                    self.__synopsis: str = node["synopsis"]

                    pass
                case "mean":
                    self.__mean: float = node["mean"]

                    pass
                case "rank":
                    self.__rank: int = node["rank"]

                    pass
                case "popularity":
                    self.__popularity: int = node["popularity"]

                    pass
                case "num_list_users":
                    self.__num_list_users: int = node["num_list_users"]

                    pass
                case "num_scoring_users":
                    self.__num_scoring_users: int = node["num_scoring_users"]

                    pass
                case "nsfw":
                    nsfw_type: str = node["nsfw"]

                    self.__nsfw: NsfwEnum = NsfwEnum[nsfw_type]

                    pass
                case "genres":
                    genres_json: List[dict] = node["genres"]
                    genres: List[Genre]     = []

                    for genre in genres_json:
                        genres.append(Genre(id=genre["id"], name=genre["name"]))

                    self.__genres: List[Genre] = genres

                    pass
                case "created_at":
                    self.__created_at: str = node["created_at"]

                    pass
                case "updated_at":
                    self.__updated_at: str = node["updated_at"]

                    pass
                case "media_type":
                    self.__media_type: MediaTypeEnum = node["media_type"]

                    pass
                case "status":
                    status_type: str = node["status"]

                    self.__status: AiringStatusEnum = AiringStatusEnum[status_type].value

                    pass
                case "num_episodes":
                    self.__num_episodes: int = node["num_episodes"]

                    pass
                case "start_season":
                    start_season: dict = node["start_season"]
                    season_type: str   = start_season["season"]

                    self.__start_season: Season = Season(
                        year   = start_season["year"],
                        season = SeasonEnum[season_type]
                    )

                    pass
                case "broadcast":
                    try:
                        broadcast: dict    = node["broadcast"]
                        day_week_type: str = broadcast["day_of_the_week"]
                    
                        self.__broadcast: Broadcast = Broadcast(
                            day_of_the_week = DayWeekEnum[day_week_type],
                            start_time      = broadcast["start_time"]
                        )
                    except:
                        self.__broadcast = None

                    pass
                case "source":
                    source_type: str = node["source"]

                    self.__source: SourceEnum = SourceEnum[source_type]

                    pass
                case "average_episode_duration":
                    self.__average_episode_duration: int = node[
                        "average_episode_duration"
                    ]

                    pass
                case "rating":
                    rating_type: str = "r_plus" if node["rating"] == "r+" else node["rating"]

                    self.__rating: RatingEnum = RatingEnum[rating_type]

                    pass
                case "studios":
                    studios_json: List[dict]   = node["studios"]
                    studios: List[Studio] = []

                    for studio in studios_json:
                        studios.append(
                            Studio(
                                id   = studio["id"], 
                                name = studio["name"]
                            )
                        )

                    self.__studios: List[Studio] = studios

                    pass
                case "pictures":
                    try:
                        pictures_json: List[dict] = node["pictures"]
                        pictures: List[Picture] = []

                        for picture in pictures_json:
                            pictures.append(
                                Picture(
                                    medium = picture["medium"],
                                    large  = picture["large"]
                                )
                            )

                        self.__pictures: List[Picture] = pictures
                    except:
                        self.__pictures = None

                    pass
                case "background":
                    try:
                        self.__background: str = node["background"]
                    except:
                        self.__background = None

                    pass
                case "related_anime":
                    try:
                        related_animes_json: List[dict]   = node["related_anime"]
                        related_animes: List[RelatedNode] = []

                        for node_related_anime in related_animes_json:
                            related_anime: dict = node_related_anime["node"]
                            main_picture: dict  = related_anime["main_picture"]
                            relation_type: str  = related_anime["relation_type"]
                            
                            related_animes.append(
                                RelatedNode(
                                    id           = related_anime["id"],
                                    title        = related_anime["title"],
                                    main_picture = Picture(
                                        medium = main_picture["medium"],
                                        large  = main_picture["large"]
                                    ),
                                    relation_type = RelationTypeEnum[
                                        relation_type
                                    ]
                                )
                            )
                        
                        self.__related_anime: List[RelatedNode] = related_animes
                    except:
                        self.__related_anime = None

                    pass
                case "related_manga":
                    try:
                        related_mangas_json: List[dict]   = node["related_manga"]
                        related_mangas: List[RelatedNode] = []

                        for node_related_manga in related_mangas_json:
                            related_manga: dict = node_related_manga["node"]
                            main_picture: dict  = related_manga["main_picture"]
                            relation_type: str  = related_manga["relation_type"]
                            
                            related_mangas.append(
                                RelatedNode(
                                    id           = related_manga["id"],
                                    title        = related_manga["title"],
                                    main_picture = Picture(
                                        medium = main_picture["medium"],
                                        large  = main_picture["large"]
                                    ),
                                    relation_type = RelationTypeEnum[
                                        relation_type
                                    ]
                                )
                            )

                        self.__related_manga: List[RelatedNode] = related_mangas
                    except:
                        self.__related_manga = None

                    pass
                case "recommendations":
                    try:
                        recommendations_json: List[dict] = node[
                            "recommendations"
                        ]
                        recommendations: List[Recommendation] = []

                        for node_recommendation in recommendations_json:
                            recommendation: Recommendation = node_recommendation["node"]
                            main_picture: Picture = recommendation["main_picture"]

                            recommendations.append(
                                Recommendation(
                                    id           = recommendation["id"],
                                    title        = recommendation["title"],
                                    main_picture = Picture(
                                        medium = main_picture["medium"],
                                        large  = main_picture["large"]
                                    ),
                                    num_recommendations = recommendation[
                                        "num_recommendations"
                                    ]
                                )
                            )
                    except:
                        self.__recommendations = None

                    pass
                case "statistics":
                    try:
                        statistics: dict = node["statistics"]
                        status: dict     = statistics["status"]

                        self.__statistics: Statistics = Statistics(
                            status = StatisticsStatus(
                                watching      = status["watching"],
                                completed     = status["completed"],
                                on_hold       = status["on_hold"],
                                dropped       = status["dropped"],
                                plan_to_watch = status["plan_to_watch"]
                            ),
                            num_list_users = statistics["num_list_users"]
                        )
                    except:
                        self.__statistics = None

                    pass

    def getAlternativeTitle(self) -> AlternativeTitles:
        """ The alternative title of the anime.

        Returns
        -----------
        :class:`AlternativeTitles`
        """

        return self.__alternative_titles

    def getStartDate(self) -> str:
        """ The anime start date. Format `YYYY-mm-dd`.

        Returns
        -----------
        :class:`str`
        """

        return self.__start_date

    def getEndDate(self) -> str:
        """ The anime end date. Format `YYYY-mm-dd`.

        Returns
        -----------
        :class:`str`
        """
        
        return self.__end_date

    def getSynopsis(self) -> str:
        """ Anime synopsis.

        Returns
        -----------
        :class:`str`
        """
        
        return self.__synopsis

    def getMean(self) -> float:
        """ Mean score.

        Returns
        -----------
        :class:`float`
        """
        
        return self.__mean

    def getRank(self) -> int:
        """ Anime rank.

        Returns
        -----------
        :class:`int`
        """
        
        return self.__rank

    def getPopularity(self) -> int:
        """ Anime popularity.

        Returns
        -----------
        :class:`int`
        """

        return self.__popularity

    def getNumUserList(self) -> int:
        """ The number of users who have the anime in their list.

        Returns
        -----------
        :class:`int`
        """

        return self.__num_list_users

    def getNumScoringUsers(self) -> int:
        """ The number of users who rated the anime.

        Returns
        -----------
        :class:`int`
        """
        
        return self.__num_scoring_users

    def getNsfwClassification(self) -> str:
        """ Anime NSFW classification.

        Returns
        -----------
        :class:`NsfwEnum`
        """

        return self.__nsfw.value

    def getGenres(self) -> List[Genre]:
        """ The list of anime genres.

        Returns
        -----------
        :class:`List[Genre]`
        """

        return self.__genres

    def getCreatedAt(self) -> str:
        """ Timestamp of anime creation in MyAnimeList database.

        Returns
        -----------
        :class:`str`
        """

        return self.__created_at

    def getUpdatedAt(self) -> str:
        """ Timestamp of anime update in MyAnimeList database.

        Returns
        -----------
        :class:`str`
        """

        return self.__updated_at

    def getMediaType(self) -> str:
        """ Anime media type.

        Returns
        -----------
        :class:`str`
        """

        return self.__media_type

    def getStatus(self) -> str:
        """ Airing status.

        Returns
        -----------
        :class:`str`
        """

        return self.__status

    def getNumEpisodes(self) -> int:
        """ The total number of episodes of this series. If unknown, it is 0.

        Returns
        -----------
        :class:`int`
        """

        return self.__num_episodes

    def getStartSeason(self) -> Season:
        """ Anime start season.

        Returns
        -----------
        :class:`Season`
        """

        return self.__start_season

    def getBroadcast(self) -> Broadcast | None:
        """ Broadcast day of the week and start time (JST).

        Returns
        -----------
        :class:`Broadcast | None`
        """

        return self.__broadcast

    def getSource(self) -> str:
        """ Original work.

        Returns
        -----------
        :class:`str`
        """

        return self.__source.value

    def getAvgEpisodeDurationInSeconds(self) -> int:
        """ Average length of episode in seconds.

        Returns
        -----------
        :class:`int`
        """

        return self.__average_episode_duration

    def getRating(self) -> str:
        """ Anime rating.

        Returns
        -----------
        :class:`str`
        """

        return self.__rating.value

    def getStudios(self) -> List[Studio]:
        """ List of studios that produced the anime.

        Returns
        -----------
        :class:`List[Studio]`
        """

        return self.__studios

    def getPictures(self) -> List[Picture] | None:
        """ List of anime pictures.

        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`List[Picture] | None`
        """

        return self.__pictures

    def getBackground(self) -> str | None:
        """ The API strips BBCode tags from the result.
        
        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`str | None`
        """

        return self.__background

    def getRelatedAnimes(self) -> List[RelatedNode] | None:
        """ List of related animes.
        
        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`List[RelatedNode] | None`
        """

        return self.__related_anime

    def getRelatedMangas(self) -> List[RelatedNode] | None:
        """ List of related mangas.
        
        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`List[RelatedNode] | None`
        """

        return self.__related_manga

    def getRecommendations(self) -> List[Recommendation] | None:
        """ Summary of recommended anime for those who like this anime.
        
        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`List[Recommendation] | None`
        """

        return self.__recommendations

    def getStatistics(self) -> Statistics | None:
        """ Anime statistics on MyAnimeList.
        
        You cannot contain this field in a list.
        
        Returns
        -----------
        :class:`Statistics | None`
        """

        return self.__statistics
