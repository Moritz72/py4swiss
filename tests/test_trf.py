from pathlib import Path

import pytest

from py4swiss.trf import TrfLine, TrfParser
from py4swiss.trf.exceptions import ConsistencyError, LineError, ParsingError
from py4swiss.trf.sections import (
    PlayerSection,
    TeamSection,
    TournamentSection,
    XSection,
)

DATA_DIRECTORY = Path(__file__).parent / "data"


def test_player_section() -> None:
    """Test whether the player section parsing is correct for different scenarios."""
    lines = [
        "001    1      Player 1                                                           0.0    1 ",
        "001    1 w    Player 2                                                           0.0    3 ",
        "001    1 m gm Player 3                                                           0.0    5 ",
        "001    1 wwgm Player 4                          1234                             0.0    7 ",
        "001    1 m im Player 5                          5678 ABC                         0.0   11 ",
        "001    1 wwim Player 6                          9012 DEF    12345678             0.0   13 ",
        "001    1 m fm Player 7                          3456 GHI    90123456 1970/01/01  0.0   17 ",
        "001    2 wwfm Player 8                          7890 JKL    78901234 2025/12/31  1.0   19    42 w 1",
        "001    2 m cm Player 9                          1234 MNO    56789012 2012/12/21  1.5   23    54 b =  0000 - Z",
    ]

    for line in lines:
        parsed_section = PlayerSection.from_string(line)
        assert parsed_section.to_string() == line


def test_player_section_line_error() -> None:
    """Test whether the player section throws line errors for wrongly formatted lines."""
    lines = [
        "001    1 m gm Player 1",
        "       1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "101    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001      m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    a m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    1 x gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    1 m ab Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          abcd ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    abcdefgh 1970/01/01  2.0    1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 abcd/ef/gh  2.0    1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01         1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  a.b    1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2      1     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0          2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    a     2 w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     a w 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 x 1  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w c  0000 - Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - X",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 --X",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 - 1",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1  0000 w Z",
        "001    1 m gm Player 1                          1234 ABC    12345678 1970/01/01  2.0    1     2 w 1     3 - 1",
    ]

    for line in lines:
        with pytest.raises(LineError):
            PlayerSection.from_string(line)


def test_tournament_section() -> None:
    """Test whether the tournament section parsing is correct for all tournament codes."""
    parsed_section = TournamentSection.from_lines([])

    assert parsed_section.to_strings() == []

    lines = [
        "012 Swiss Tournament",
        "022 Berlin",
        "032 GER",
        "042 1970/01/01",
        "052 1970/01/05",
        "062 25",
        "072 25",
        "082 0",
        "092 Swiss",
        "102 Alice",
        "112 Bob",
        "122 40/90, 30",
        "132                                                                                        25/01/01 25/01/02",
    ]

    trf_lines = [TrfLine(i, line) for i, line in enumerate(lines)]
    parsed_section = TournamentSection.from_lines(trf_lines)

    assert parsed_section.to_strings() == [str(trf_line) for trf_line in trf_lines]


def test_tournament_section_parsing_error() -> None:
    """Test whether the tournament section throws parsing errors for wrongly formatted lines."""
    lines = ["012 Swiss Tournament", "012 Round Robin Tournament"]

    with pytest.raises(ParsingError):
        trf_lines = [TrfLine(0, line) for line in lines]
        TournamentSection.from_lines(trf_lines)

    lines = ["132 "]

    with pytest.raises(ParsingError):
        trf_lines = [TrfLine(i, line) for i, line in enumerate(lines)]
        TournamentSection.from_lines(trf_lines)


def test_team_section() -> None:
    """Test whether the team section parsing is correct for different scenarios."""
    lines = [
        "013 Team                            ",
        "013 Team                               1",
        "013 Team                               1    2",
    ]

    for line in lines:
        parsed_section = TeamSection.from_string(line)
        assert parsed_section.to_string() == line


def test_team_section_line_error() -> None:
    """Test whether the team section throws line errors for wrongly formatted lines."""
    lines = [
        "013 Team",
        "    Team                               1    2",
        "103 Team                               1    2",
        "013                                    1    2",
        "013 Team                               a    b",
    ]

    for line in lines:
        with pytest.raises(LineError):
            TeamSection.from_string(line)


def test_x_section() -> None:
    """Test whether the 'x-section' parsing is correct for all javafo codes."""
    default_configuration = "XXC white1"
    default_scoring = "XXS WW=1.0 BW=1.0 WD=0.5 BD=0.5 WL=0.0 BL=0.0 ZPB=0.0 HPB=0.5 FPB=1.0 PAB=1.0 FW=1.0 FL=0.0"

    rounds_string = "XXR 5"
    parsed_section = XSection.from_lines([TrfLine(0, rounds_string)])

    assert set(parsed_section.to_strings()) == {rounds_string, default_configuration, default_scoring}

    lines = [
        "XXR 5",
        "XXC rank white1",
        "XXS WW=1.0 BW=1.0 WD=0.5 BD=0.5 WL=0.0 BL=0.0 ZPB=0.0 HPB=0.5 FPB=1.0 PAB=1.0 FW=1.0 FL=0.0",
    ]

    trf_lines = [TrfLine(i, line) for i, line in enumerate(lines)]
    parsed_section = XSection.from_lines(trf_lines)

    assert set(parsed_section.to_strings()) == {str(trf_line) for trf_line in trf_lines}

    lines = [
        "XXR 5",
        "XXC rank black1",
        "XXZ 1 2 3 4",
        "XXA    1  1.0  1.0  0.0  0.0  0.0",
        "XXA    2  0.0  0.0  0.0  0.0  0.0",
        "XXP 1 2",
        "XXP 3 4",
        "XXS W=1.0 D=0.5 L=0.0",
    ]

    trf_lines = [TrfLine(i, line) for i, line in enumerate(lines)]
    parsed_section = XSection.from_lines(trf_lines)

    assert set(parsed_section.to_strings()) == {str(trf_line) for trf_line in trf_lines[:-1]} | {default_scoring}


def test_x_section_parsing_error() -> None:
    """Test whether the 'x-section' throws parsing errors for wrongly formatted lines."""
    rounds_line = "XXR 5"

    with pytest.raises(ParsingError):
        XSection.from_lines([])

    with pytest.raises(ParsingError):
        XSection.from_lines([TrfLine(0, "XXR ")])

    with pytest.raises(ParsingError):
        XSection.from_lines([TrfLine(0, "XXR a")])

    individual_lines = [
        "XXR 6",
        "XXC random1",
        "XXS 1.0",
        "XXS W=",
        "XXS W=a.b",
        "XXS XX=1.0",
        "XXZ a b",
        "XXA ",
        "XXA     ",
        "XXA    a  1.0  1.0  0.0  0.0  0.0",
        "XXA    1  a.b  1.0  0.0  0.0  0.0",
        "XXP 1",
        "XXP 1 b",
    ]

    for line in individual_lines:
        with pytest.raises(ParsingError):
            trf_lines = [TrfLine(0, rounds_line), TrfLine(1, line)]
            XSection.from_lines(trf_lines)

    lines = ["XXA    1  1.0  1.0  0.0  0.0  0.0", "XXA    1  2.0  2.0  1.0  0.0  0.0"]

    with pytest.raises(ParsingError):
        trf_lines = [TrfLine(0, rounds_line)] + [TrfLine(i + 1, line) for i, line in enumerate(lines)]
        XSection.from_lines(trf_lines)

    lines = ["XXC white1", "XXC rank"]

    with pytest.raises(ParsingError):
        trf_lines = [TrfLine(0, rounds_line)] + [TrfLine(i + 1, line) for i, line in enumerate(lines)]
        XSection.from_lines(trf_lines)


def test_trf_parser(tmp_path: Path) -> None:
    """Test whether the TRF parsing is correct."""
    trf_file = DATA_DIRECTORY / "javafo_example.trf"
    tmp_file = tmp_path / "parsed.trf"

    parsed_trf = TrfParser.parse(trf_file)
    parsed_trf.write_to_file(tmp_file)

    assert set(trf_file.read_text().splitlines()) == set(tmp_file.read_text().splitlines())


def test_trf_parser_consistency_error() -> None:
    """Test whether the TRF parser throws consistency errors for TRFs with inconsistent contents."""
    trf_files = [
        DATA_DIRECTORY / "too_many_results.trf",
        DATA_DIRECTORY / "missing_starting_number.trf",
        DATA_DIRECTORY / "incorrect_points.trf",
        DATA_DIRECTORY / "missing_result.trf",
        DATA_DIRECTORY / "incompatible_result.trf",
        DATA_DIRECTORY / "incompatible_color.trf",
    ]

    for trf_file in trf_files:
        with pytest.raises(ConsistencyError):
            TrfParser.parse(trf_file)


def test_trf_line_parsing_error(tmp_path: Path) -> None:
    """Test whether a TRF line throws parsing errors for wrongly formatted lines."""
    with pytest.raises(ParsingError):
        TrfLine(0, "")

    with pytest.raises(ParsingError):
        TrfLine(0, "101").get_code_type()
