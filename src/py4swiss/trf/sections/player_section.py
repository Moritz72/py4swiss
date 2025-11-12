from enum import Enum
from typing import Self

from pydantic import Field

from py4swiss.trf.codes import PlayerCode
from py4swiss.trf.exceptions import LineError
from py4swiss.trf.results import RoundResult
from py4swiss.trf.sections.abstract_section import AbstractSection, Date


class Index(int, Enum):
    """Delimiter positions of a player section line of a TRF."""

    CODE = 0
    STARTING_NUMBER = 4
    SEX = 9
    TITLE = 10
    NAME = 14
    FIDE_RATING = 48
    FIDE_FEDERATION = 53
    FIDE_NUMBER = 57
    BIRTH_DATE = 69
    POINTS = 80
    RANK = 85
    RESULTS = 91


class Sex(str, Enum):
    """Sex of a player."""

    MALE = "m"
    FEMALE = "w"


class Title(str, Enum):
    """Title of a player."""

    GRANDMASTER = "gm"
    INTERNATIONAL_MASTER = "im"
    WOMEN_GRANDMASTER = "wgm"
    FIDE_MASTER = "fm"
    WOMEN_INTERNATIONAL_MASTER = "wim"
    CANDIDATE_MASTER = "cm"
    WOMEN_FIDE_MASTER = "wfm"
    WOMEN_CANDIDATE_MASTER = "wcm"


class PlayerSection(AbstractSection):
    """
    Representation of a parsed player section of a TRF.

    Attributes:
        code (PlayerCode): The player code of the section (any of xx1)
        starting_number (int): The starting number of the player in the tournament
        sex (Sex | None): The sex of the player if specified
        title (Title | None): The title of the player if present
        name (str | None): The name of the player if specified
        fide_rating (int | None): The FIDE rating of the player if present
        fide_federation (str | None): The FIDE federation of the player if present
        fide_number (int | None): The FIDE number of the player if present
        birth_date (Date | None): The date of birth of the player if specified
        points_times_ten (int): The current point total of the player in the tournament (not including acceleration)
        rank (int): The current rank of the player in the tournament
        results (list[RoundResult]): The current list of results of the player in the tournament
    """

    code: PlayerCode
    starting_number: int
    sex: Sex | None = None
    title: Title | None = None
    name: str | None = None
    fide_rating: int | None = None
    fide_federation: str | None = None
    fide_number: int | None = None
    birth_date: Date | None = None
    points_times_ten: int
    rank: int
    results: list[RoundResult] = Field(default_factory=list)

    @staticmethod
    def _get_result(string: str, index: int = 0) -> RoundResult:
        """Return a round result from the given string."""
        try:
            return RoundResult.from_string(string)
        except ValueError as e:
            raise LineError(f"Invalid round result '{string}'", column=index + 1) from e

    @staticmethod
    def _serialize_results(results: list[RoundResult]) -> str:
        """Return a TRF conform string representation of the round results."""
        return "".join([RoundResult.BUFFER_LENGTH * " " + result.to_string() for result in results])

    @staticmethod
    def _deserialize_results(string: str, index: int = 0) -> list[RoundResult]:
        """Convert the given string to a list of round results."""
        string = string.rstrip()

        step_size = RoundResult.CONTENT_LENGTH + RoundResult.BUFFER_LENGTH
        parts = [string[i : i + RoundResult.CONTENT_LENGTH] for i in range(0, len(string), step_size)]

        return [PlayerSection._get_result(part, index + i * step_size) for i, part in enumerate(parts)]

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Convert the given string to a player section."""
        if len(string) < Index.RESULTS - 2:
            raise LineError("Incomplete player section")

        code = cls._deserialize_enum(string[Index.CODE : Index.STARTING_NUMBER - 1], PlayerCode, Index.CODE)
        starting_number = cls._deserialize_integer(string[Index.STARTING_NUMBER : Index.SEX - 1], Index.STARTING_NUMBER)
        sex = cls._deserialize_enum(string[Index.SEX : Index.TITLE], Sex, Index.SEX + 1)
        title = cls._deserialize_enum(string[Index.TITLE : Index.NAME - 1].lower(), Title, Index.TITLE)
        name = cls._deserialize_string(string[Index.NAME : Index.FIDE_RATING - 1])
        fide_rating = cls._deserialize_integer(string[Index.FIDE_RATING : Index.FIDE_FEDERATION - 1], Index.FIDE_RATING)
        fide_federation = cls._deserialize_string(string[Index.FIDE_FEDERATION : Index.FIDE_NUMBER - 1])
        fide_number = cls._deserialize_integer(string[Index.FIDE_NUMBER : Index.BIRTH_DATE - 1], Index.FIDE_NUMBER)
        birth_date = cls._deserialize_date(string[Index.BIRTH_DATE : Index.POINTS - 1], Index.BIRTH_DATE)
        points_times_ten = cls._deserialize_decimal(string[Index.POINTS : Index.RANK - 1], Index.POINTS)
        rank = cls._deserialize_integer(string[Index.RANK : Index.RESULTS - 1], Index.RANK)
        results = cls._deserialize_results(string[Index.RESULTS :], Index.RESULTS)

        if code is None:
            raise LineError("No code provided", column=Index.CODE + 1)
        if starting_number is None:
            raise LineError("No starting number provided", column=Index.STARTING_NUMBER + 1)
        if points_times_ten is None:
            raise LineError("No points provided", column=Index.POINTS + 1)
        if rank is None:
            raise LineError("No rank provided", column=Index.RANK + 1)

        return cls(
            code=code,
            starting_number=starting_number,
            sex=sex,
            title=title,
            name=name,
            fide_rating=fide_rating,
            fide_federation=fide_federation,
            fide_number=fide_number,
            birth_date=birth_date,
            points_times_ten=points_times_ten,
            rank=rank,
            results=results,
        )

    def to_string(self) -> str:
        """Return a TRF conform string respresentation of the given player section."""
        parts = [
            self._serialize_enum(self.code).ljust(Index.STARTING_NUMBER - Index.CODE - 1),
            self._serialize_integer(self.starting_number).rjust(Index.SEX - Index.STARTING_NUMBER - 1),
            self._serialize_enum(self.sex).rjust(Index.TITLE - Index.SEX),
            self._serialize_enum(self.title).rjust(Index.NAME - Index.TITLE - 1),
            self._serialize_string(self.name).ljust(Index.FIDE_RATING - Index.NAME - 1),
            self._serialize_integer(self.fide_rating).rjust(Index.FIDE_FEDERATION - Index.FIDE_RATING - 1),
            self._serialize_string(self.fide_federation).ljust(Index.FIDE_NUMBER - Index.FIDE_FEDERATION - 1),
            self._serialize_integer(self.fide_number).rjust(Index.BIRTH_DATE - Index.FIDE_NUMBER - 1),
            self._serialize_date(self.birth_date).ljust(Index.POINTS - Index.BIRTH_DATE - 1),
            self._serialize_decimal(self.points_times_ten).rjust(Index.RANK - Index.POINTS - 1),
            self._serialize_integer(self.rank).rjust(Index.RESULTS - Index.RANK - 2),
            self._serialize_results(self.results)[1:],
        ]

        string = " ".join(parts)

        # There is no whitespace between sex and title.
        string = string[: Index.TITLE] + string[Index.TITLE + 1 :]

        return string
