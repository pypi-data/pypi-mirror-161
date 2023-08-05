from .statisticsStatus import StatisticsStatus

class Statistics:
    def __init__(self, num_list_users: int, status: StatisticsStatus) -> None:
        """ Constructor

        Parameters
        -----------
        num_list_users: :class:`int`
            Number of users who added the anime to their list.
        status: :class:`StatisticsStatus`
            Users list status.
        """

        self.__num_list_users = num_list_users
        self.__status = status
        
    def getNumUserList(self) -> int:
        """ The number of users who have the anime in their list.

        Returns
        -----------
        :class:`int`
        """

        return self.__num_list_users

    def getStatus(self) -> StatisticsStatus:
        """ Anime status in the users list.

        Returns
        -----------
        :class:`StatisticsStatus`
        """

        return self.__status