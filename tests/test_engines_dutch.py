import random
from pathlib import Path

import pytest

from py4swiss.engines import DutchEngine
from py4swiss.engines.common import Pairing

from tests.helpers.bbp_pairings import generate_dutch_pairings
from tests.helpers.trf import add_random_result, get_trf


@pytest.mark.parametrize(
    "seed, number_of_players, number_of_rounds",
    [(0, 6, 3), (1, 25, 23), (2, 76, 73), (3, 99, 98)]
)
def test_vs_bbp_pairings(tmp_path: Path, seed: int, number_of_players: int, number_of_rounds: int) -> None:
    random.seed(seed)

    trf_file_path = tmp_path / "test_file.trf"
    bbp_pairings_file_path = tmp_path / "bbp_pairings_output.txt"
    dutch_engine_file_path = tmp_path / "dutch_engine_output.txt"

    trf = get_trf(number_of_players, number_of_rounds)

    for _ in range(number_of_rounds):
        trf.write_to_file(trf_file_path)
        generate_dutch_pairings(trf_file_path, bbp_pairings_file_path)
        DutchEngine.write_pairings_to_file(trf, dutch_engine_file_path)

        bbp_pairings_output = Pairing.from_file(bbp_pairings_file_path)
        dutch_engine_output = Pairing.from_file(dutch_engine_file_path)

        assert bbp_pairings_output == dutch_engine_output

        for pairing in dutch_engine_output:
            add_random_result(trf, pairing)
