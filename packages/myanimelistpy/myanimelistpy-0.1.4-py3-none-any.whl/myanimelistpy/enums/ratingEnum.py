from enum import Enum

class RatingEnum(Enum):
    g      = "All Ages"
    pg     = "Children"
    pg_13  = "Teens 13 and Older"
    r      = "17+ (violence & profanity)"
    r_plus = "Profanity & Mild Nudity" # r+
    rx     = "Hentai"