from enum import Enum


class ColorToken(str, Enum):
    """Enum for the color in a round result of a player."""

    WHITE = "w"
    BLACK = "b"
    BYE_OR_NOT_PAIRED = "-"

    def to_bool(self) -> bool | None:
        """
        Return a boolean or None of the instance:
            - True, in case of white
            - False, in case of black
            - None, in case of bye or not paired
        """
        match self:
            case ColorToken.WHITE:
                return True
            case ColorToken.BLACK:
                return False
            case ColorToken.BYE_OR_NOT_PAIRED:
                return None
