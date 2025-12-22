from typing import Protocol


class PlayerProtocol(Protocol):
    """Protocol representing a player to be paired."""

    id: int

    def __hash__(self) -> int:
        """Return a hash."""
