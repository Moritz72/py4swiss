from pathlib import Path

import pytest

from py4swiss.engines import BursteinEngine
from py4swiss.engines.common import PairingError
from py4swiss.trf import TrfParser

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_no_legal_pairing() -> None:
    """Test whether trying to generate pairings for TRF files with no legal pairings throws pairing errors."""
    input_file = DATA_DIRECTORY / "no_legal_pairings.trf"
    parsed_trf = TrfParser.parse(input_file)

    with pytest.raises(PairingError):
        BursteinEngine.generate_pairings(parsed_trf)

    input_file = DATA_DIRECTORY / "no_legal_pairings_odd.trf"
    parsed_trf = TrfParser.parse(input_file)

    with pytest.raises(PairingError):
        BursteinEngine.generate_pairings(parsed_trf)
