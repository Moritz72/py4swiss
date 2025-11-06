from typing import Self

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

    id: int
    color: ColorToken
    result: ResultToken

    @classmethod
    def from_section(cls, section: str) -> Self:
        """Return an instance given a part of a line in a TRF file defining a player section."""
        if len(section) < 8 or any(section[i] != " " for i in (4, 6)):
            raise ValueError

        # Format for TRF (FIDE)
        # ---- | Startingrank-Number of the scheduled opponent (up to 4 digits)
        # 0000 | If the player had a bye (either half-point bye, full-point bye or odd-number bye) or was not paired
        #        (absent, retired, not nominated by team)
        #      | (four blanks) equivalent to 0000
        player_id = int(section[:4].lstrip())

        # Format for TRF (FIDE)
        # w | Scheduled color against the scheduled opponent
        # b | Scheduled color against the scheduled opponent
        # - | (minus) If the player had a bye or was not paired
        #   | (blank) equivalent to -
        color_token = ColorToken(section[5].replace(" ", "-"))

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
        result_token = ResultToken(section[7].upper())

        return cls(id=player_id, color=color_token, result=result_token)

    def to_string(self) -> str:
        """Return a TRF conform string representation of the instance."""
        if self.id == 0:
            id_string = "0000"
        else:
            id_string = str(self.id)
        return f"{id_string:>6} {self.color.value} {self.result.value}"
