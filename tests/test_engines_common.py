from pathlib import Path

import pytest

from py4swiss.engines.common import ColorPreferenceSide, Pairing, PairingEngine

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_pairings(tmp_path: Path) -> None:
    """Test reading pairings from and writing pairíngs to files."""
    pairings_file = DATA_DIRECTORY / "pairings_example.txt"
    tmp_file = tmp_path / "pairings.txt"

    pairings = Pairing.from_file(pairings_file)
    PairingEngine.write_pairings_to_file(pairings, tmp_file)

    assert set(tmp_file.read_text().splitlines()) == set(tmp_file.read_text().splitlines())

    pairings_copy = Pairing.from_file(tmp_file)

    assert pairings == pairings_copy
    assert hash(tuple(pairings)) == hash(tuple(pairings_copy))


def test_pairing_error() -> None:
    """Test whether reading invalid pairing files throws pairing errors."""
    pairings_file = DATA_DIRECTORY / "malformed_pairings.txt"

    with pytest.raises(ValueError):
        Pairing.from_file(pairings_file)

    pairings_file = DATA_DIRECTORY / "non_distinct_pairings.txt"

    with pytest.raises(ValueError):
        Pairing.from_file(pairings_file)


def test_color_preference() -> None:
    """Test the color preference logic."""
    assert ColorPreferenceSide.WHITE.get_opposite() == ColorPreferenceSide.BLACK
    assert ColorPreferenceSide.BLACK.get_opposite() == ColorPreferenceSide.WHITE
    assert ColorPreferenceSide.NONE.get_opposite() == ColorPreferenceSide.NONE

    assert ColorPreferenceSide.WHITE.conflicts(ColorPreferenceSide.WHITE)
    assert not ColorPreferenceSide.WHITE.conflicts(ColorPreferenceSide.BLACK)
    assert not ColorPreferenceSide.WHITE.conflicts(ColorPreferenceSide.NONE)

    assert not ColorPreferenceSide.BLACK.conflicts(ColorPreferenceSide.WHITE)
    assert ColorPreferenceSide.BLACK.conflicts(ColorPreferenceSide.BLACK)
    assert not ColorPreferenceSide.BLACK.conflicts(ColorPreferenceSide.NONE)

    assert not ColorPreferenceSide.NONE.conflicts(ColorPreferenceSide.WHITE)
    assert not ColorPreferenceSide.NONE.conflicts(ColorPreferenceSide.BLACK)
    assert not ColorPreferenceSide.NONE.conflicts(ColorPreferenceSide.NONE)
