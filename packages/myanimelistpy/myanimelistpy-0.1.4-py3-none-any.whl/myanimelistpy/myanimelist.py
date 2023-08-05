import requests
from typing import List
from json import dumps

from .services.validateFields import validateFields
from .models.anime import Anime

# ------------------------------ Constants ----------------------------------- #
BASE_URL            = "https://api.myanimelist.net/v2"
ANIME_LIST_ENDPOINT = "anime"
AUTH_HEADER         = "X-MAL-CLIENT-ID"
# ---------------------------------------------------------------------------- #

class MyAnimeList:
    def __init__(self, client_id: str) -> None:
        """ Constructor.

        Parameters
        -----------
        client_id: :class:`str`
            MyAnimeList Client ID.
        """
        
        self.client_id = client_id
        self.base_url  =  BASE_URL

    def getAnimeListInDict(
        self, 
        anime_name: str, 
        limit: int = 100, 
        offset: int = 0,
        fields: List[str] = []
    ) -> dict:
        """ Returns a list of dictionaries containing the anime by name.

        Parameters
        -----------
        anime_name: :class:`str`
            Name of the anime/series.
        limit: :class:`int`
            The maximum size of the list. `The default value is 100`.
        offset: :class:`int`
            The list offset. `The default value is 0`.
        fields: :class:`List[str]`
            List of fields used to show more information about the anime. If is 
            empty, the default fields are `id`, `title` and `main_picture`.

        Returns
        -----------
        animes: :class:`dict`
        """

        validateFields(fields=fields)

        url = f"{BASE_URL}/{ANIME_LIST_ENDPOINT}?q={anime_name}&limit={limit}&offset={offset}"

        if(len(fields) > 0):
            url += f"&fields={fields}"

        response = requests.get(
            url     = url,
            headers = {AUTH_HEADER: self.client_id}
        )

        temp: List[dict] = response.json()["data"]

        return temp
    
    def getAnimeList(
        self, 
        anime_name: str, 
        limit: int = 100, 
        offset: int = 0,
        fields: List[str] = []
    ) -> List[Anime]:
        """ Returns a list of anime by name.

        Parameters
        -----------
        anime_name: :class:`str`
            Name of the anime/series.
        limit: :class:`int`
            The maximum size of the list. `The default value is 100`.
        offset: :class:`int`
            The list offset. `The default value is 0`.
        fields: :class:`List[str]`
            List of fields used to show more information about the anime. If is 
            empty, the default fields are `id`, `title` and `main_picture`.

        Returns
        -----------
        animes: :class:`List[Anime]`
        """

        responseJson: dict = self.getAnimeListInDict(
            anime_name = anime_name,
            limit      = limit,
            offset     = offset,
            fields     = fields,
        )

        animes: List[Anime] = []

        for index in range(len(responseJson)):
            animes.append(
                Anime(node=responseJson[index]["node"], fields=fields)
            )

        return animes

    def getAnimeListInJSON(
        self, 
        anime_name: str, 
        limit: int = 100, 
        offset: int = 0,
        fields: List[str] = []
    ) -> str:
        """ Returns a JSON stringified containing the list of anime by name.

        Parameters
        -----------
        anime_name: :class:`str`
            Name of the anime/series.
        limit: :class:`int`
            The maximum size of the list. `The default value is 100`.
        offset: :class:`int`
            The list offset. `The default value is 0`.
        fields: :class:`List[str]`
            List of fields used to show more information about the anime. If is 
            empty, the default fields are `id`, `title` and `main_picture`.

        Returns
        -----------
        animes: :class:`str`
        """

        responseJson: dict = self.getAnimeListInDict(
            anime_name = anime_name,
            limit      = limit,
            offset     = offset,
            fields     = fields,
        )

        return '{"data":' + dumps(responseJson) + '}'