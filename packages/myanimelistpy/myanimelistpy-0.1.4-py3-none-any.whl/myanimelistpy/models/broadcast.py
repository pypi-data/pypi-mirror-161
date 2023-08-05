from ..enums.dayWeekEnum import DayWeekEnum

class Broadcast:
    def __init__(self, day_of_the_week: DayWeekEnum, start_time: str) -> None:
        """ Constructor

        Parameters
        -----------
        day_of_the_week: :class:`DayWeekEnum`
            Day of the week broadcast in Japan time.
        start_time: :class:`str`
            Time in hours format that is broadcasted.
        """
        
        self.__day_of_the_week = day_of_the_week
        self.__start_time = start_time

    def getDayOfTheWeek(self) -> str:
        """ Broadcast day of the week.

        Returns
        -----------
        :class:`str`
        """

        return self.__day_of_the_week.name

    def getStartTime(self) -> str:
        """ Anime start time in JST.

        Returns
        -----------
        :class:`str`
        """

        return self.__start_time