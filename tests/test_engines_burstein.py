import random
from pathlib import Path

import pytest

from py4swiss.engines import BursteinEngine
from py4swiss.engines.common import PairingError
from py4swiss.trf import TrfParser
from py4swiss.trf.sections import XSection
from py4swiss.trf.sections.x_section import XSectionConfiguration
from tests.helpers.pairing_engine_clients import Py4SwissBursteinClient
from tests.helpers.pairing_engine_comparers import RandomResultsComparer

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_simple(tmp_path: Path) -> None:
    """Test for tournaments with simple conditions."""
    comparer = RandomResultsComparer(Py4SwissBursteinClient, Py4SwissBursteinClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=5, configuration=configuration)
    comparer("small_1", 7, x_section, 5321)
    comparer("small_2", 8, x_section, 7351)
    comparer("small_3", 9, x_section, 6712)

    x_section = XSection(number_of_rounds=7, configuration=configuration)
    comparer("medium_1", 33, x_section, 1324)
    comparer("medium_2", 34, x_section, 6743)
    comparer("medium_3", 35, x_section, 6235)

    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large_1", 78, x_section, 2352)
    comparer("large_2", 79, x_section, 7453)
    comparer("large_3", 80, x_section, 7754)


def test_forbidden_pairs(tmp_path: Path) -> None:
    """Test for tournaments with forbidden pairs."""
    comparer = RandomResultsComparer(Py4SwissBursteinClient, Py4SwissBursteinClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    forbidden_pairs = {(1, 2), (1, 5), (2, 4), (6, 3)}
    x_section = XSection(number_of_rounds=4, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("small", 9, x_section, 7523)

    forbidden_pairs = {(1, 5), (4, 20), (27, 10), (21, 13), (5, 6), (7, 4), (5, 18), (9, 5), (14, 6), (25, 2)}
    x_section = XSection(number_of_rounds=5, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("medium", 27, x_section, 6734)

    random.seed(0)
    forbidden_pairs = {(random.randint(1, 81), random.randint(1, 81)) for _ in range(200)}
    forbidden_pairs = {pair for pair in forbidden_pairs if len(set(pair)) > 1}
    x_section = XSection(number_of_rounds=10, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("large", 81, x_section, 7362)


def test_rare_situations(tmp_path: Path) -> None:
    """Test rare situations that might not come up in regular testing."""
    input_file = DATA_DIRECTORY / "burstein_late_entries.trf"
    output_file = tmp_path / "burstein_late_entries_pairings.txt"

    Py4SwissBursteinClient.generate_pairings(input_file, output_file)

    input_file = DATA_DIRECTORY / "burstein_late_entries_black.trf"
    output_file = tmp_path / "burstein_late_entries_black_pairings.txt"

    Py4SwissBursteinClient.generate_pairings(input_file, output_file)


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
