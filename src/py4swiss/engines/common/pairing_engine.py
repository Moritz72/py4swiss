from abc import ABC, abstractmethod
from pathlib import Path

from py4swiss.engines.common.pairing import Pairing
from py4swiss.trf import ParsedTrf


class PairingEngine(ABC):
    """Abstract base class for pairing engines."""

    @staticmethod
    def write_pairings_to_file(pairings: list[Pairing], file_path: Path) -> None:
        """Write the round pairing of the next round for the given TRF to a given file."""
        file_path.parent.mkdir(exist_ok=True)

        lines = [pairing.to_string() for pairing in pairings]

        with file_path.open("w", encoding="utf-8") as fh:
            fh.write(f"{len(lines)}\n")
            fh.write("\n".join(lines))
            fh.write("\n")

    @classmethod
    @abstractmethod
    def generate_pairings(cls, trf: ParsedTrf) -> list[Pairing]:
        """Return the round pairing of the next round for the given TRF."""
        pass  # pragma: no cover
