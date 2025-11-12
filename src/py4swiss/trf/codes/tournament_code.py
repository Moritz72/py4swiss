from enum import Enum


class TournamentCode(str, Enum):
    """TRF tournament codes."""

    TOURNAMENT_NAME = "012"
    CITY = "022"
    FEDERATION = "032"
    DATE_OF_START = "042"
    DATE_OF_END = "052"
    NUMBER_OF_PLAYERS = "062"
    NUMBER_OF_RATED_PLAYERS = "072"
    NUMBER_OF_TEAMS = "082"
    TYPE_OF_TOURNAMENT = "092"
    CHIEF_ARBITER = "102"
    DEPUTY_CHIEF_ARBITER = "112"
    ALLOTTED_TIMES_PER_GAME_MOVE = "122"
    DATES_OF_THE_ROUND = "132"
