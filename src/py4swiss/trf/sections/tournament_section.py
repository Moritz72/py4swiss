from typing import Self

from py4swiss.trf.codes import CODE_LENGTH, TournamentCode
from py4swiss.trf.exceptions import LineError, ParsingError
from py4swiss.trf.sections.abstract_section import AbstractSection, Date
from py4swiss.trf.trf_line import TrfLine

DATES_START_INDEX = 91


class TournamentSection(AbstractSection):
    """
    Representation of a parsed tournament section of a TRF.

    Attributes:
        tournament_name (str | None): The name of the tournament if specified
        city (str | None): The city in which the tournament is taking place if specified
        federation (str | None): The federation in which the tournament is taking place if specified
        date_of_start (str | None): The start date of the tournament if specified
        date_of_end (str | None): The end date of the tournament if specified
        number_of_players (str | None): The number of players taking part in the tournament if specified
        number_of_rated_players (str | None): The number of rated players taking part in the tournament if specified
        number_of_teams (str | None): The number of teams taking part in the tournament if specified
        type_of_tournament (str | None): The type of the tournament if specified
        chief_arbiter (str | None): The chief arbiter of the tournament if present
        deputy_chief_arbiter (str | None): The deputy chief arbiter of the tournament if present
        alloted_time_per_moves_game (str | None): The alloted time per move or game in the tournament if specified
        dates_of_the_round (list[Date] | None): The dates for the individual rounds of the tournament if specified

    """

    tournament_name: str | None = None
    city: str | None = None
    federation: str | None = None
    date_of_start: str | None = None
    date_of_end: str | None = None
    number_of_players: str | None = None
    number_of_rated_players: str | None = None
    number_of_teams: str | None = None
    type_of_tournament: str | None = None
    chief_arbiter: str | None = None
    deputy_chief_arbiter: str | None = None
    alloted_time_per_moves_game: str | None = None
    dates_of_the_round: list[Date] | None = None

    @staticmethod
    def _get_date(string: str, index: int = 0) -> Date:
        """Return a date from the given string."""
        return TournamentSection._deserialize_date(string, index, short=True) or Date(year=0, month=0, day=0)

    @staticmethod
    def _serialize_dates_of_the_round(dates_of_the_round: list[Date] | None) -> str | None:
        """Return a TRF conform string representation of the given list of dates."""
        if dates_of_the_round is None:
            return None

        parts = [TournamentSection._serialize_date(date, short=True) for date in dates_of_the_round]
        return (DATES_START_INDEX - CODE_LENGTH - 1) * " " + " ".join(parts)

    @staticmethod
    def _deserialize_dates_of_the_round(string: str, index: int = 0) -> list[Date]:
        """Convert the given string to a list of dates."""
        start_index = DATES_START_INDEX - index
        if len(string) < start_index:
            error_message = "Incomplete dates of rounds"
            raise LineError(error_message)
        string = string[start_index:].rstrip()

        step_size = Date.LENGTH_SHORT + 1
        parts = [string[i : i + Date.LENGTH_SHORT] for i in range(0, len(string), step_size)]

        return [TournamentSection._get_date(part, start_index + i * step_size) for i, part in enumerate(parts)]

    @classmethod
    def from_lines(cls, lines: list[TrfLine]) -> Self:
        """Convert the given lines to a tournament section."""
        code_line_dict = {}

        for line in lines:
            code = TournamentCode(line.code)

            if code in code_line_dict:
                error_message = f"Code '{code}' is declared twice"
                raise ParsingError(error_message, row=line.row)

            code_line_dict[code] = line

        if TournamentCode.DATES_OF_THE_ROUND in code_line_dict:
            line = code_line_dict[TournamentCode.DATES_OF_THE_ROUND]
            try:
                dates_of_the_round = cls._deserialize_dates_of_the_round(line.content, CODE_LENGTH + 1)
            except LineError as e:
                raise ParsingError(e.message, row=line.row, column=e.column) from e
        else:
            dates_of_the_round = None

        def get_code_string(code_: TournamentCode) -> str | None:
            """Return the line contents of the given code if the code was declared."""
            line_ = code_line_dict.get(code_)
            if line_ is None:
                return None
            return line_.content

        return cls(
            tournament_name=get_code_string(TournamentCode.TOURNAMENT_NAME),
            city=get_code_string(TournamentCode.CITY),
            federation=get_code_string(TournamentCode.FEDERATION),
            date_of_start=get_code_string(TournamentCode.DATE_OF_START),
            date_of_end=get_code_string(TournamentCode.DATE_OF_END),
            number_of_players=get_code_string(TournamentCode.NUMBER_OF_PLAYERS),
            number_of_rated_players=get_code_string(TournamentCode.NUMBER_OF_RATED_PLAYERS),
            number_of_teams=get_code_string(TournamentCode.NUMBER_OF_TEAMS),
            type_of_tournament=get_code_string(TournamentCode.TYPE_OF_TOURNAMENT),
            chief_arbiter=get_code_string(TournamentCode.CHIEF_ARBITER),
            deputy_chief_arbiter=get_code_string(TournamentCode.DEPUTY_CHIEF_ARBITER),
            alloted_time_per_moves_game=get_code_string(TournamentCode.ALLOTTED_TIMES_PER_GAME_MOVE),
            dates_of_the_round=dates_of_the_round,
        )

    def to_strings(self) -> list[str]:
        """Return a list of TRF conform string respresentation of the given tournament section."""
        code_value_pairs = [
            (TournamentCode.TOURNAMENT_NAME, self.tournament_name),
            (TournamentCode.CITY, self.city),
            (TournamentCode.FEDERATION, self.federation),
            (TournamentCode.DATE_OF_START, self.date_of_start),
            (TournamentCode.DATE_OF_END, self.date_of_end),
            (TournamentCode.NUMBER_OF_PLAYERS, self.number_of_players),
            (TournamentCode.NUMBER_OF_RATED_PLAYERS, self.number_of_rated_players),
            (TournamentCode.NUMBER_OF_TEAMS, self.number_of_teams),
            (TournamentCode.TYPE_OF_TOURNAMENT, self.type_of_tournament),
            (TournamentCode.CHIEF_ARBITER, self.chief_arbiter),
            (TournamentCode.DEPUTY_CHIEF_ARBITER, self.deputy_chief_arbiter),
            (TournamentCode.ALLOTTED_TIMES_PER_GAME_MOVE, self.alloted_time_per_moves_game),
            (TournamentCode.DATES_OF_THE_ROUND, self._serialize_dates_of_the_round(self.dates_of_the_round)),
        ]

        return [f"{code.value} {value}" for code, value in code_value_pairs if value is not None]
