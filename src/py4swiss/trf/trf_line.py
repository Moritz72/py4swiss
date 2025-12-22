from py4swiss.trf.codes import (
    CODE_LENGTH,
    PLAYER_CODES,
    TEAM_CODES,
    TOURNAMENT_CODES,
    X_CODES,
    Code,
    PlayerCode,
    TeamCode,
    TournamentCode,
    XCode,
)
from py4swiss.trf.exceptions import ParsingError


class TrfLine:
    """A line of a TRF file."""

    def __init__(self, index: int, string: str) -> None:
        """Initialize a new line."""
        if len(string) < CODE_LENGTH:
            error_message = "Incomplete line"
            raise ParsingError(error_message, row=index + 1)

        self.row: int = index + 1
        self.code: str = string[:CODE_LENGTH]
        self.code_type: type[Code] = self._get_code_type(self.code, self.row)
        self.content: str = string[CODE_LENGTH + 1 :]

    def __str__(self) -> str:
        """Return a string representation of the given line."""
        return f"{self.code} {self.content}"

    @staticmethod
    def _get_code_type(code: str, row: int) -> type[Code]:
        """Return the code type to which the given code belongs to."""
        if code in PLAYER_CODES:
            return PlayerCode
        if code in TOURNAMENT_CODES:
            return TournamentCode
        if code in TEAM_CODES:
            return TeamCode
        if code in X_CODES:
            return XCode

        error_message = f"Invalid code '{code}'"
        raise ParsingError(error_message, row=row, column=1)
