import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from py4swiss.engines.common import Pairing
from py4swiss.main import main


class PairingEngineClient(ABC):
    """Abstract client for generating pairing from a TRF."""

    @classmethod
    @abstractmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF."""
        pass


class BbpPairingsDutchClient(PairingEngineClient):
    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using bbpPairings (Dutch system)."""
        cmd = ["bbpPairings.exe", "--dutch", str(input_file_path), "-p", str(output_file_path)]
        subprocess.run(cmd, check=True)
        return Pairing.from_file(output_file_path)


class Py4SwissDutchClient(PairingEngineClient):
    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using py4swiss (Dutch system)."""
        sys.argv = ["py4swiss", "-e", "dutch", "-t", str(input_file_path), "-p", str(output_file_path)]
        main()
        return Pairing.from_file(output_file_path)
