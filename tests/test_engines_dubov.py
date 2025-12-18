from pathlib import Path

import pytest

from py4swiss.engines import DubovEngine
from py4swiss.engines.common import PairingError
from py4swiss.trf import TrfParser
from py4swiss.trf.sections import XSection
from py4swiss.trf.sections.x_section import XSectionConfiguration
from tests.helpers.pairing_engine_clients import (
    CppDubovSystemClient,
    Py4SwissDubovClient,
)
from tests.helpers.pairing_engine_comparers import RandomResultsComparer

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_simple(tmp_path: Path) -> None:
    """Compare to CPPDubovSystem for tournaments with simple conditions."""
    comparer = RandomResultsComparer(Py4SwissDubovClient, CppDubovSystemClient, tmp_path, strict=False)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=5, configuration=configuration)
    comparer("small_1", 7, x_section, 3463)
    comparer("small_2", 8, x_section, 8556)
    comparer("small_3", 9, x_section, 1244)

    x_section = XSection(number_of_rounds=7, configuration=configuration)
    comparer("medium_1", 33, x_section, 7434)
    comparer("medium_2", 34, x_section, 9862)
    comparer("medium_3", 35, x_section, 4912)

    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large_1", 78, x_section, 5235)
    comparer("large_2", 79, x_section, 9421)
    comparer("large_3", 80, x_section, 3466)


def test_configuration(tmp_path: Path) -> None:
    """Compare to CPPDubovSystem for tournaments with various configurations."""
    comparer = RandomResultsComparer(Py4SwissDubovClient, CppDubovSystemClient, tmp_path, strict=False)

    configuration = XSectionConfiguration(first_round_color=False)
    x_section = XSection(number_of_rounds=4, configuration=configuration)
    comparer("small", 7, x_section, 5325)

    configuration = XSectionConfiguration(first_round_color=True)
    x_section = XSection(number_of_rounds=6, configuration=configuration)
    comparer("medium", 28, x_section, 5952)

    configuration = XSectionConfiguration(first_round_color=False)
    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large", 75, x_section, 9389)


def test_rare_situations(tmp_path: Path) -> None:
    """Test rare situations that might not come up in regular testing."""
    input_file = DATA_DIRECTORY / "dubov_bye_for_high_tpn.trf"
    output_file = tmp_path / "dubov_bye_for_high_tpn_pairings.txt"

    Py4SwissDubovClient.generate_pairings(input_file, output_file)


def test_no_legal_pairing() -> None:
    """Test whether trying to generate pairings for TRF files with no legal pairings throws pairing errors."""
    input_file = DATA_DIRECTORY / "no_legal_pairings.trf"
    parsed_trf = TrfParser.parse(input_file)

    with pytest.raises(PairingError):
        DubovEngine.generate_pairings(parsed_trf)

    input_file = DATA_DIRECTORY / "no_legal_pairings_odd.trf"
    parsed_trf = TrfParser.parse(input_file)

    with pytest.raises(PairingError):
        DubovEngine.generate_pairings(parsed_trf)
