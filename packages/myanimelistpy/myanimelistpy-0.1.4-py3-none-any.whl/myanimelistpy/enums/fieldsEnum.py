from enum import Enum

class FieldsEnum(Enum):
    id                       = 0
    title                    = 1
    main_picture             = 2
    alternative_titles       = 3
    start_date               = 4
    end_date                 = 5
    synopsis                 = 6
    mean                     = 7
    rank                     = 8
    popularity               = 9
    num_list_users           = 10
    num_scoring_users        = 11
    nsfw                     = 12
    genres                   = 13
    created_at               = 14
    updated_at               = 15
    media_type               = 16
    status                   = 17
    num_episodes             = 18
    start_season             = 19
    broadcast                = 20
    source                   = 21
    average_episode_duration = 22
    rating                   = 23
    studios                  = 24
    pictures                 = 25 # Cannot contain this field in a list.
    background               = 26 # Cannot contain this field in a list.
    related_anime            = 27 # Cannot contain this field in a list.
    related_manga            = 28 # Cannot contain this field in a list.
    recommendations          = 29 # Cannot contain this field in a list.
    statistics               = 30 # Cannot contain this field in a list.