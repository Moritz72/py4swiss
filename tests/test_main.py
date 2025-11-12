import sys
from pathlib import Path

import pytest

from py4swiss.main import main

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_engine_dutch(tmp_path: Path) -> None:
    """Test running py4swiss using the Dutch engine."""
    trf_file = DATA_DIRECTORY / "javafo_example.trf"
    pairings_file = tmp_path / "pairings.txt"

    sys.argv = ["py4swiss", "-e", "dutch", "-t", str(trf_file), "-p", str(pairings_file)]
    main()


def test_engine_value_error(tmp_path: Path) -> None:
    """Test whether py4swiss throws value errors for invalid engines."""
    trf_file = DATA_DIRECTORY / "javafo_example.trf"
    pairings_file = tmp_path / "pairings.txt"

    with pytest.raises(ValueError):
        sys.argv = ["py4swiss", "-e", "knockout", "-t", str(trf_file), "-p", str(pairings_file)]
        main()
