import random
from pathlib import Path

import pytest

from py4swiss.engines import DutchEngine
from py4swiss.engines.common import PairingError
from py4swiss.trf import TrfParser
from py4swiss.trf.sections import XSection
from py4swiss.trf.sections.x_section import XSectionConfiguration
from tests.helpers.pairing_engine_clients import (
    BbpPairingsDutchClient,
    Py4SwissDutchClient,
)
from tests.helpers.pairing_engine_comparers import (
    RandomResultsComparer,
    RandomResultsComparerWithByes,
    RandomResultsComparerWithForfeits,
    RandomResultsComparerWithShuffle,
)

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_simple(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with simple conditions."""
    comparer = RandomResultsComparer(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=5, configuration=configuration)
    comparer("small_1", 7, x_section, 3245)
    comparer("small_2", 8, x_section, 4234)
    comparer("small_3", 9, x_section, 2948)

    x_section = XSection(number_of_rounds=7, configuration=configuration)
    comparer("medium_1", 33, x_section, 2346)
    comparer("medium_2", 34, x_section, 8568)
    comparer("medium_3", 35, x_section, 4212)

    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large_1", 78, x_section, 3124)
    comparer("large_2", 79, x_section, 6346)
    comparer("large_3", 80, x_section, 8563)


def test_forfeits(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with forfeits."""
    comparer = RandomResultsComparerWithForfeits(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path, 0.2)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=5, configuration=configuration)
    comparer("small", 8, x_section, 3543)

    x_section = XSection(number_of_rounds=6, configuration=configuration)
    comparer("medium", 26, x_section, 5645)

    x_section = XSection(number_of_rounds=7, configuration=configuration)
    comparer("large", 85, x_section, 3244)


def test_byes(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with byes."""
    comparer = RandomResultsComparerWithByes(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path, 0.2)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=4, configuration=configuration)
    comparer("small", 10, x_section, 7682)

    x_section = XSection(number_of_rounds=7, configuration=configuration)
    comparer("medium", 27, x_section, 4674)

    x_section = XSection(number_of_rounds=8, configuration=configuration)
    comparer("large", 89, x_section, 2435)


def test_configuration(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with various configurations."""
    comparer = RandomResultsComparerWithShuffle(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path)

    configuration = XSectionConfiguration(first_round_color=False)
    x_section = XSection(number_of_rounds=4, configuration=configuration)
    comparer("small", 7, x_section, 6354)

    configuration = XSectionConfiguration(first_round_color=True, by_rank=True)
    x_section = XSection(number_of_rounds=6, configuration=configuration)
    comparer("medium", 28, x_section, 8632)

    configuration = XSectionConfiguration(first_round_color=False, by_rank=True)
    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large", 75, x_section, 9123)


def test_acceleration(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with accelerated rounds."""
    comparer = RandomResultsComparer(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    accelerations = {i + 1: [10, 0, 0] for i in range(3)}
    x_section = XSection(number_of_rounds=3, configuration=configuration, accelerations=accelerations)
    comparer("small", 6, x_section, 7582)

    accelerations = {i + 1: [10, 10, 5, 0, 0] for i in range(26)}
    x_section = XSection(number_of_rounds=5, configuration=configuration, accelerations=accelerations)
    comparer("medium", 26, x_section, 3294)

    random.seed(0)
    accelerations = {i + 1: [random.randint(0, 30) for _ in range(9)] for i in range(73)}
    x_section = XSection(number_of_rounds=9, configuration=configuration, accelerations=accelerations)
    comparer("large", 73, x_section, 1245)


def test_forbidden_pairs(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with forbidden pairs."""
    comparer = RandomResultsComparer(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    forbidden_pairs = {(1, 2), (1, 5), (2, 4), (6, 3)}
    x_section = XSection(number_of_rounds=4, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("small", 9, x_section, 2389)

    forbidden_pairs = {(1, 5), (4, 20), (27, 10), (21, 13), (5, 6), (7, 4), (5, 18), (9, 5), (14, 6), (25, 2)}
    x_section = XSection(number_of_rounds=5, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("medium", 27, x_section, 4125)

    random.seed(0)
    forbidden_pairs = {(random.randint(1, 81), random.randint(1, 81)) for _ in range(200)}
    forbidden_pairs = {pair for pair in forbidden_pairs if len(set(pair)) > 1}
    x_section = XSection(number_of_rounds=10, configuration=configuration, forbidden_pairs=forbidden_pairs)
    comparer("large", 81, x_section, 5723)


def test_many_rounds(tmp_path: Path) -> None:
    """Compare to bbpPairngs for tournaments with a lot of rounds in relation to the number of participants."""
    comparer = RandomResultsComparer(Py4SwissDutchClient, BbpPairingsDutchClient, tmp_path)
    configuration = XSectionConfiguration(first_round_color=True)

    x_section = XSection(number_of_rounds=4, configuration=configuration)
    comparer("small", 6, x_section, 4376)

    x_section = XSection(number_of_rounds=29, configuration=configuration)
    comparer("medium", 31, x_section, 9323)

    x_section = XSection(number_of_rounds=97, configuration=configuration)
    comparer("large", 99, x_section, 5345)


def test_rare_situations(tmp_path: Path) -> None:
    """Compare to bbpPairngs for rare situations that might not come up in regular testing."""
    input_file = DATA_DIRECTORY / "dutch_d2_criterion_d.trf"
    output_file_1 = tmp_path / "dutch_d2_criterion_d_pairings_1.txt"
    output_file_2 = tmp_path / "dutch_d2_criterion_d_pairings_2.txt"

    pairings_1 = Py4SwissDutchClient.generate_pairings(input_file, output_file_1)
    pairings_2 = BbpPairingsDutchClient.generate_pairings(input_file, output_file_2)

    assert pairings_1 == pairings_2

    input_file = DATA_DIRECTORY / "dutch_e2_both_absolute_higher_favored.trf"
    output_file_1 = tmp_path / "dutch_e2_both_absolute_higher_favored_pairings_1.txt"
    output_file_2 = tmp_path / "dutch_e2_both_absolute_higher_favored_pairings_2.txt"

    pairings_1 = Py4SwissDutchClient.generate_pairings(input_file, output_file_1)
    pairings_2 = BbpPairingsDutchClient.generate_pairings(input_file, output_file_2)

    assert pairings_1 == pairings_2

    input_file = DATA_DIRECTORY / "dutch_e2_both_absolute_lower_favored.trf"
    output_file_1 = tmp_path / "dutch_e2_both_absolute_lower_favored_pairings_1.txt"
    output_file_2 = tmp_path / "dutch_e2_both_absolute_lower_favored_pairings_2.txt"

    pairings_1 = Py4SwissDutchClient.generate_pairings(input_file, output_file_1)
    pairings_2 = BbpPairingsDutchClient.generate_pairings(input_file, output_file_2)

    assert pairings_1 == pairings_2


def test_no_legal_pairing() -> None:
    """Test whether trying to generate pairings for TRF files with no legal pairings throws pairing errors."""
    input_file = DATA_DIRECTORY / "no_legal_pairings.trf"
    parsed_trf = TrfParser.parse(input_file)

    with pytest.raises(PairingError):
        DutchEngine.generate_pairings(parsed_trf)
