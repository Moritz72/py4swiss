from typing import ClassVar, Self

from pydantic import BaseModel

from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.results.result_token import ResultToken


class RoundResult(BaseModel):
    """
    A round result of a player.

    Attributes:
        id (int): The starting number of the player
        color (ColorToken): The color of the player for this round
        result (ResultToken): The result of the player for this round
    """

    CONTENT_LENGTH: ClassVar[int] = 8
    ID_LENGTH: ClassVar[int] = 4
    BUFFER_LENGTH: ClassVar[int] = 2
    ID_INDEX: ClassVar[int] = 0
    COLOR_INDEX: ClassVar[int] = 5
    RESULT_INDEX: ClassVar[int] = 7

    id: int
    color: ColorToken
    result: ResultToken

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Return an instance given a string from a TRF."""
        if len(string) < cls.CONTENT_LENGTH or any(string[i] != " " for i in (4, 6)):
            raise ValueError

        # Format for TRF (FIDE)
        # ---- | Startingrank-Number of the scheduled opponent (up to 4 digits)
        # 0000 | If the player had a bye (either half-point bye, full-point bye or odd-number bye) or was not paired
        #        (absent, retired, not nominated by team)
        #      | (four blanks) equivalent to 0000
        player_id = int(string[cls.ID_INDEX : cls.ID_INDEX + cls.ID_LENGTH].lstrip())

        # Format for TRF (FIDE)
        # w | Scheduled color against the scheduled opponent
        # b | Scheduled color against the scheduled opponent
        # - | (minus) If the player had a bye or was not paired
        #   | (blank) equivalent to -
        color_token = ColorToken(string[cls.COLOR_INDEX].replace(" ", "-"))

        # Format for TRF (FIDE)
        # The scheduled game was not played
        # - | forfeit loss
        # + | forfeit win
        # The scheduled game lasted less than one move
        # W | win  | Not rated
        # D | draw | Not rated
        # L | loss | Not rated
        # Regular game
        # 1 | win
        # = | draw
        # 0 | loss
        # Bye
        # H | half-point-bye          | Not rated
        # F | full-point-bye          | Not rated
        # U | pairing-allocated bye   | At most once for round - Not rated (U for player unpaired by the system)
        # Z | zero-point-bye          | Known absence from round - Not rated
        #   | (blank) equivalent to Z |
        result_token = ResultToken(string[cls.RESULT_INDEX].upper())

        # Played round results must have an opponent and a color. Similarly, a bye must have no color.
        if result_token.is_played() and not bool(player_id):
            raise ValueError
        if result_token.is_played() and color_token == ColorToken.BYE_OR_NOT_PAIRED:
            raise ValueError
        if result_token.is_bye() and color_token != ColorToken.BYE_OR_NOT_PAIRED:
            raise ValueError

        return cls(id=player_id, color=color_token, result=result_token)

    def to_string(self) -> str:
        """Return a TRF conform string representation of the given instance."""
        if self.id == 0:
            id_string = self.ID_LENGTH * "0"
        else:
            id_string = str(self.id).rjust(self.ID_LENGTH)
        return f"{id_string} {self.color.value} {self.result.value}"
