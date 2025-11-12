from pathlib import Path
from typing import Self

from pydantic import BaseModel


class Pairing(BaseModel):
    """
    Pairing between two players represented by their IDs.

    Attributes:
        white (int): The ID of the player with the white pieces (0 in case of the pairing-allocated bye)
        black (int): The ID of the player with the black pieces (0 in case of the pairing-allocated bye)
    """

    white: int
    black: int

    def __eq__(self, other: object) -> bool:
        """Check whether given pairings are identical."""
        if not isinstance(other, Pairing):  # pragma: no cover
            return NotImplemented
        return self.white == other.white and self.black == other.black

    def __hash__(self) -> int:
        """Return the hash of the player IDs."""
        return hash((self.white, self.black))

    @classmethod
    def from_file(cls, file_path: Path) -> list[Self]:
        """Convert the contents of the given file to a list of pairings."""
        with file_path.open("r", encoding="utf-8") as fh:
            lines = [line.rstrip() for line in fh]
        pair_list = [[int(item) for item in line.split(" ")] for line in lines[1:]]

        # Pairs need to consist of exactly two items separated by whitespace.
        if not all(len(pair) == 1 + 1 for pair in pair_list):
            raise ValueError("Invalid pair")

        # A pair must consist of two distinct IDs.
        for pair in pair_list:
            if pair[0] == pair[1]:
                raise ValueError("Invalid pair")

        return [cls(white=pair[0], black=pair[1]) for pair in pair_list]

    def to_string(self) -> str:
        """Return a string of the player IDs separated by whitespace."""
        return f"{self.white} {self.black}"
