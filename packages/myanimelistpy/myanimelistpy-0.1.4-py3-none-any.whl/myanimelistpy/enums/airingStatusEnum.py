from enum import Enum

class AiringStatusEnum(Enum):
    finished_airing  = "Finished airing"
    currently_airing = "Currently airing"
    not_yet_aired    = "Not yet aired"