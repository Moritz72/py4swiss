from enum import Enum


class XCode(str, Enum):
    """Enum for javafo specific codes."""

    ROUNDS = "XXR"
    ZEROED_IDS = "XXZ"
    POINT_SYSTEM = "XXS"
    CONFIGURATIONS = "XXC"
    ACCELERATIONS = "XXA"
    FORBIDDEN_PAIRS = "XXP"
