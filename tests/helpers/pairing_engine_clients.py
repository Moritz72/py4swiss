import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from py4swiss.engines.common import Pairing
from py4swiss.main import main
from tests.helpers.ccp_dubov_system_adapter import CppDubovSystemAdapter


class PairingEngineClient(ABC):
    """Abstract client for generating pairings from a TRF."""

    @classmethod
    @abstractmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF."""
        pass


class BbpPairingsDutchClient(PairingEngineClient):
    """Client for generating pairings using the Dutch system implementation of bbpPairings."""

    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using bbpPairings (Dutch system)."""
        cmd = ["bbpPairings.exe", "--dutch", str(input_file_path), "-p", str(output_file_path)]
        subprocess.run(cmd, check=True)
        return Pairing.from_file(output_file_path)


class CppDubovSystemClient(PairingEngineClient):
    """Client for generating pairings from a TRF using CPPDubovSystem."""

    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using CPPDubovSystem."""
        CppDubovSystemAdapter.transform_trf(input_file_path)

        input_file_path = CppDubovSystemAdapter.get_suffixed_path(input_file_path)
        output_file_path = CppDubovSystemAdapter.get_suffixed_path(output_file_path)

        cmd = ["CPPDubovSystem", "--pairings", str(input_file_path), "--output", str(output_file_path)]
        subprocess.run(cmd, check=True)

        CppDubovSystemAdapter.transform_pairings(output_file_path, output_file_path)
        return Pairing.from_file(output_file_path)


class Py4SwissDutchClient(PairingEngineClient):
    """Client for generating pairings using the Dutch system implementation of py4swiss."""

    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using py4swiss (Dutch system)."""
        sys.argv = ["py4swiss", "-e", "dutch", "-t", str(input_file_path), "-p", str(output_file_path)]
        main()
        return Pairing.from_file(output_file_path)


class Py4SwissDubovClient(PairingEngineClient):
    """Client for generating pairings using the Dubov system implementation of py4swiss."""

    @classmethod
    def generate_pairings(cls, input_file_path: Path, output_file_path: Path) -> list[Pairing]:
        """Generate the pairing of the next round for the given TRF using py4swiss (Dubov system)."""
        sys.argv = ["py4swiss", "-e", "dubov", "-t", str(input_file_path), "-p", str(output_file_path)]
        main()
        return Pairing.from_file(output_file_path)
