from enum import Enum
from typing import Self

from pydantic import Field

from py4swiss.trf.codes import TeamCode
from py4swiss.trf.exceptions import LineError
from py4swiss.trf.sections.abstract_section import AbstractSection

STARTING_NUMBER_SIZE = 4


class Index(int, Enum):
    """Delimiter positions of a team section line of a TRF."""

    CODE = 0
    TEAM_NAME = 4
    PLAYERS = 36


class TeamSection(AbstractSection):
    """
    Representation of a parsed team section of a TRF.

    Attributes:
        code (TeamCode): The team code of the section (any of xx2)
        team_name (str): The name of the team
        players (list[int]): The list of starting numbers of all players in the team
    """

    code: TeamCode
    team_name: str
    players: list[int] = Field(default_factory=list)

    @staticmethod
    def _get_player(string: str, index: int = 0) -> int:
        """Return a starting number from the given string."""
        try:
            return int(string)
        except ValueError as e:
            raise LineError(f"Invalid starting number '{string}'", column=index + 1) from e

    @staticmethod
    def _serialize_players(players: list[int]) -> str:
        """Return a TRF conform string representation of the given list of starting numbers."""
        return " ".join([str(player).rjust(STARTING_NUMBER_SIZE) for player in players])

    @staticmethod
    def _deserialize_players(string: str, index: int = 0) -> list[int]:
        """Convert the given string to a list of starting numbers."""
        string = string.rstrip()

        step_size = STARTING_NUMBER_SIZE + 1
        parts = [string[i : i + STARTING_NUMBER_SIZE] for i in range(0, len(string), step_size)]

        return [TeamSection._get_player(part, index + i * step_size) for i, part in enumerate(parts)]

    @classmethod
    def from_string(cls, line: str) -> Self:
        """Convert the given string to a team section."""
        if len(line) < Index.PLAYERS:
            raise LineError("Incomplete team section")

        code = cls._deserialize_enum(line[Index.CODE : Index.TEAM_NAME - 1], TeamCode, Index.CODE)
        team_name = cls._deserialize_string(line[Index.TEAM_NAME : Index.PLAYERS - 1])
        players = cls._deserialize_players(line[Index.PLAYERS :], Index.PLAYERS)

        if code is None:
            raise LineError("No code provided", column=Index.CODE + 1)
        if team_name is None:
            raise LineError("No name provided", column=Index.TEAM_NAME + 1)

        return cls(code=code, team_name=team_name, players=players)

    def to_string(self) -> str:
        """Return a TRF conform string respresentation of the given team section."""
        parts = [
            self._serialize_enum(self.code).ljust(Index.TEAM_NAME - Index.CODE - 1),
            self._serialize_string(self.team_name).ljust(Index.PLAYERS - Index.TEAM_NAME - 1),
            self._serialize_players(self.players),
        ]

        return " ".join(parts)
