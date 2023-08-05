from enum import Enum

class NsfwEnum(Enum):
    white = "This work is safe for work"
    gray  = "This work may be not safe for work"
    black = "This work is not safe for work"