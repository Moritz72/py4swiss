from enum import Enum


class ColorToken(str, Enum):
    WHITE = "w"
    BLACK = "b"
    BYE_OR_NOT_PAIRED = "-"

    def to_bool(self) -> bool | None:
        match self:
            case ColorToken.WHITE:
                return True
            case ColorToken.BLACK:
                return False
            case ColorToken.BYE_OR_NOT_PAIRED:
                return None
