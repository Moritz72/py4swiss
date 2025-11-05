from pydantic import BaseModel

from py4swiss.trf.exceptions import LineException


class TournamentSection(BaseModel):
    """
    Representation of a parsed tournament section of a TRF.

    Attributes:
        tournament_name (str | None)
        city (str | None)
        federation (str | None)
        date_of_start (str | None)
        date_of_end (str | None)
        number_of_players (str | None)
        number_of_rated_players (str | None)
        number_of_teams (str | None)
        type_of_tournament (str | None)
        chief_arbiter (str | None)
        deputy_chief_arbiter (str | None)
        alloted_time_per_moves_game (str | None)
        dates_of_the_round (list[tuple[int, int, int]] | None)
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
    dates_of_the_round: list[tuple[int, int, int]] | None = None

    def set_dates_of_the_round(self, line: str) -> None:
        self.dates_of_the_round = []

        for i in range(91, len(line), 8):
            try:
                section = line[i : i + 8]
            except IndexError as e:
                raise LineException(f"Incomplete dates of the round line '{line}'") from e

            try:
                if bool(section.strip()):
                    year = int(section[:4].strip() or 0)
                    month = int(section[5:7].strip() or 0)
                    day = int(section[8:10].strip() or 0)
                    self.dates_of_the_round.append((year, month, day))
            except ValueError as e:
                raise LineException(f"Invalid round date '{section}'", column=i) from e
