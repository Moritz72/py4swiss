from pathlib import Path
from typing import Self

from pydantic import BaseModel


class Pairing(BaseModel):
    white: int
    black: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pairing):
            return False
        return self.white == other.white and self.black == other.black

    def __hash__(self) -> int:
        return hash((self.white, self.black))

    @classmethod
    def from_file(cls, file_path: Path) -> list[Self]:
        with file_path.open("r", encoding="utf-8") as fh:
            lines = [line.rstrip() for line in fh]
        pair_list = [[int(item) for item in line.split(" ")] for line in lines[1:]]

        if not all(0 < len(pair) < 3 for pair in pair_list):
            raise ValueError("Invalid pair")

        for pair in pair_list:
            if len(pair) == 1:
                pair.append(0)
            if pair[0] == pair[1]:
                raise ValueError("Invalid pair")

        return [cls(white=pair[0], black=pair[1]) for pair in pair_list]

    def to_string(self) -> str:
        return f"{self.white} {self.black}"
