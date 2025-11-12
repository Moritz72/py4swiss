from collections import defaultdict
from typing import Self

from pydantic import BaseModel, Field

from py4swiss.trf.codes import CODE_LENGTH, XCode
from py4swiss.trf.exceptions import LineError, ParsingError
from py4swiss.trf.results import (
    SCORING_POINT_SYSTEM_IDENTIFIER_DICT,
    ScoringPointSystem,
    ScoringPointSystemCode,
)
from py4swiss.trf.sections.abstract_section import AbstractSection
from py4swiss.trf.trf_line import TrfLine

PLAYER_ID_LENGTH = 4
SCORE_LENGTH = 4
FORBIDDEN_PAIR_LENGTH = 2


class XSectionConfiguration(BaseModel):
    """
    Configuration settings of a TRF(x).

    Attributes:
        first_round_color (bool): Whether the initial piece color of the top seed is white (default: True)
        by_rank (bool): Whether to pair by starting number or position (rank) in the TRF (default: False)
    """

    first_round_color: bool = True
    by_rank: bool = False

    def apply_string(self, string: str) -> None:
        """Apply configurations from the given string."""
        for part in string.split(" "):
            match part:
                case "rank":
                    self.by_rank = True
                case "white1":
                    self.first_round_color = True
                case "black1":
                    self.first_round_color = False
                case _:
                    raise ValueError(f"Invalid configuration '{part}'")

    def to_string(self) -> str:
        """Return a TRF conform string representation of the given configuration."""
        items = []

        if self.by_rank:
            items.append("rank")

        if self.first_round_color is not None:
            if self.first_round_color:
                items.append("white1")
            else:
                items.append("black1")

        return " ".join(items)


class XSection(AbstractSection):
    """
    Representation of a parsed 'X-section' of a TRF(x).

    Attributes:
        number_of_rounds (int): The number of rounds of the tournament
        zeroed_ids (set[int]): The number of players not participating in the current round of the tournament
        scoring_point_system (ScoringPointSystem): The scoring point system of the tournament
        configuration (XSectionConfiguration): The configuration of the tournament
        accelerations (dict[int, list[int]]): The acceleration points for all player and rounds of the tournament
        forbidden_pairs (set[tuple[int, int]]): The pairs of players that are not allowed to be paired with each other
    """

    number_of_rounds: int
    zeroed_ids: set[int] = Field(default_factory=set)
    scoring_point_system: ScoringPointSystem = Field(default_factory=ScoringPointSystem)
    configuration: XSectionConfiguration = Field(default_factory=XSectionConfiguration)
    accelerations: dict[int, list[int]] = Field(default_factory=dict)
    forbidden_pairs: set[tuple[int, int]] = Field(default_factory=set)

    @staticmethod
    def _get_score_points(string: str, index: int = 0) -> tuple[ScoringPointSystemCode, int]:
        """Return a scoring point system code and point value from the given string."""
        try:
            code_string, points_string = string.split("=", 1)
        except ValueError as e:
            raise LineError(f"Invalid score points '{string}'", column=index + 1) from e

        try:
            code = ScoringPointSystemCode(code_string)
        except ValueError as e:
            raise LineError(f"Invalid score point system code '{code_string}'", column=index + 1) from e

        points_times_ten = XSection._deserialize_decimal(points_string, index=index + len(code_string) + 1)
        if points_times_ten is None:
            raise LineError(f"Invalid score points '{points_string}'", column=index + len(code_string) + 1)

        return code, points_times_ten

    @staticmethod
    def _serialize_player_accelerations(player_id: int, player_accelerations: list[int]) -> str:
        """Return a TRF conform string representation of the given starting number and accelerations."""
        player_string = XSection._serialize_integer(player_id, PLAYER_ID_LENGTH)
        accelerations_string = XSection._serialize_decimals(player_accelerations, SCORE_LENGTH)
        return f"{player_string} {accelerations_string}"

    @staticmethod
    def _serialize_scoring_points_dict(scoring_points_dict: dict[ScoringPointSystemCode, int]) -> str:
        """Return a TRF conform string representation of the given scoring points dictionary."""
        parts = [
            f"{code.value}={XSection._serialize_decimal(points_times_ten)}"
            for code, points_times_ten in scoring_points_dict.items()
        ]
        return " ".join(parts)

    @staticmethod
    def _deserialize_player_accelerations(string: str, index: int = 0) -> tuple[int, list[int]]:
        """Convert the givne string to a starting number and list of accelerations."""
        if len(string) < PLAYER_ID_LENGTH:
            raise LineError(f"No player id provided '{string}'", column=index + 1)

        id_string = string[:PLAYER_ID_LENGTH]
        accelerations_string = string[PLAYER_ID_LENGTH + 1 :]

        player_id = XSection._deserialize_integer(id_string, index)
        if player_id is None:
            raise LineError(f"No player id provided '{string}'", column=index + 1)

        return player_id, XSection._deserialize_decimals(accelerations_string, index + PLAYER_ID_LENGTH + 1)

    @staticmethod
    def _deserialize_scoring_points_dict(string: str, index: int = 0) -> dict[ScoringPointSystemCode, int]:
        """Convert the given string to a scoring points dictionary."""
        scoring_points_dict = {}

        for part in string.split(" "):
            code, points_times_ten = XSection._get_score_points(part, index)
            scoring_points_dict[code] = points_times_ten

            index += len(part) + 1

        return scoring_points_dict

    @classmethod
    def from_lines(cls, lines: list[TrfLine]) -> Self:
        """Convert the given lines to a 'X-section' section."""
        code_line_dict: defaultdict[XCode, list[TrfLine]] = defaultdict(list)

        for line in lines:
            code = XCode(line.code)
            code_line_dict[code].append(line)

        round_lines = code_line_dict[XCode.ROUNDS]
        if len(round_lines) == 0:
            raise ParsingError("No number of rounds provided")
        if len(round_lines) > 1:
            raise ParsingError(f"Code '{XCode.ROUNDS}' is declared twice", row=round_lines[1].row)

        round_line = round_lines[0]
        try:
            number_of_rounds = cls._deserialize_integer(round_line.content, CODE_LENGTH + 1)
        except LineError as e:
            raise ParsingError(e.message, row=round_line.row, column=e.column) from e
        if number_of_rounds is None:
            raise ParsingError("Invalid number of rounds")

        configuration_lines = code_line_dict[XCode.CONFIGURATIONS]
        if len(configuration_lines) > 1:
            raise ParsingError(f"Code '{XCode.CONFIGURATIONS}' is declared twice", row=configuration_lines[1].row)

        configuration = XSectionConfiguration()
        if len(configuration_lines) > 0:
            configuration_line = configuration_lines[0]
            try:
                configuration.apply_string(configuration_line.content)
            except ValueError as e:
                raise ParsingError(str(e), row=configuration_line.row, column=1) from e

        zeroed_ids = set()
        for ids_line in code_line_dict[XCode.ZEROED_IDS]:
            try:
                zeroed_ids |= set(cls._deserialize_integers(ids_line.content, CODE_LENGTH + 1))
            except LineError as e:
                raise ParsingError(e.message, row=ids_line.row, column=e.column) from e

        scoring_point_system = ScoringPointSystem()
        for scoring_points_line in code_line_dict[XCode.POINT_SYSTEM]:
            try:
                scoring_points_dict = cls._deserialize_scoring_points_dict(scoring_points_line.content, CODE_LENGTH + 1)
                for scoring_point_system_code, score_points in scoring_points_dict.items():
                    scoring_point_system.apply_code(scoring_point_system_code, score_points)
            except LineError as e:
                raise ParsingError(e.message, row=scoring_points_line.row, column=e.column) from e

        accelerations = {}
        for accelerations_line in code_line_dict[XCode.ACCELERATIONS]:
            try:
                player_id, player_accelerations = cls._deserialize_player_accelerations(
                    accelerations_line.content, CODE_LENGTH + 1
                )
                if player_id in accelerations:
                    raise LineError(f"Acceleration for the player with id '{player_id}' is declared twice")
                accelerations[player_id] = player_accelerations
            except LineError as e:
                raise ParsingError(e.message, row=accelerations_line.row, column=e.column) from e

        forbidden_pairs = set()
        for forbidden_pairs_line in code_line_dict[XCode.FORBIDDEN_PAIRS]:
            try:
                ids = tuple(cls._deserialize_integers(forbidden_pairs_line.content, CODE_LENGTH + 1))
                if len(ids) != 1 + 1:
                    raise LineError(f"Invalid forbidden pair '{forbidden_pairs_line.content}'", column=CODE_LENGTH + 1)
                forbidden_pairs.add((ids[0], ids[1]))
            except LineError as e:
                raise ParsingError(e.message, row=forbidden_pairs_line.row, column=e.column) from e

        return cls(
            number_of_rounds=number_of_rounds,
            zeroed_ids=zeroed_ids,
            scoring_point_system=scoring_point_system,
            configuration=configuration,
            accelerations=accelerations,
            forbidden_pairs=forbidden_pairs,
        )

    def to_strings(self) -> list[str]:
        """Return a list of TRF conform string respresentation of the given tournament section."""
        scoring_points_dict = {
            code: self.scoring_point_system.score_dict[value]
            for code, value in SCORING_POINT_SYSTEM_IDENTIFIER_DICT.items()
        }
        configuration_string = self.configuration.to_string()

        code_value_pairs = [
            (XCode.ROUNDS, self._serialize_integer(self.number_of_rounds)),
            (XCode.POINT_SYSTEM, self._serialize_scoring_points_dict(scoring_points_dict)),
        ]

        if bool(configuration_string):
            code_value_pairs.append((XCode.CONFIGURATIONS, configuration_string))

        if bool(self.zeroed_ids):
            code_value_pairs.append((XCode.ZEROED_IDS, self._serialize_integers(sorted(self.zeroed_ids))))

        code_value_pairs.extend(
            (XCode.ACCELERATIONS, self._serialize_player_accelerations(player_id, player_accelerations))
            for player_id, player_accelerations in self.accelerations.items()
        )

        code_value_pairs.extend(
            (XCode.FORBIDDEN_PAIRS, self._serialize_integers(sorted(pair))) for pair in sorted(self.forbidden_pairs)
        )

        return [f"{code.value} {value}" for code, value in code_value_pairs if value is not None]
