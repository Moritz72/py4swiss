from pathlib import Path

from py4swiss.trf.sections import XSection
from py4swiss.trf.sections.x_section import XSectionConfiguration
from tests.helpers.pairing_engine_clients import CppDubovSystemClient, Py4SwissDubovClient
from tests.helpers.pairing_engine_comparers import RandomResultsComparer


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
    comparer("medium_3", 35, x_section, 7257)

    x_section = XSection(number_of_rounds=9, configuration=configuration)
    comparer("large_1", 78, x_section, 4634)
    comparer("large_2", 79, x_section, 7473)
    comparer("large_3", 80, x_section, 3466)
