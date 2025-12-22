from typing import Protocol


class StateProtocol(Protocol):
    """Protocol representing a state containing necessary information for pairing purposes."""

    forbidden_pairs: set[tuple[int, int]]
