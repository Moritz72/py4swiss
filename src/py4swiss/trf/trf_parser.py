from collections import defaultdict
from pathlib import Path

from py4swiss.trf.codes import PlayerCode, TeamCode, TournamentCode, XCode
from py4swiss.trf.parsed_trf import ParsedTrf
from py4swiss.trf.sections import (
    PlayerSection,
    TeamSection,
    TournamentSection,
    XSection,
)
from py4swiss.trf.trf_line import TrfLine


class TrfParser:
    """Parser for TRF(x) files as defined by FIDE and javafo."""

    @classmethod
    def parse(cls, file_path: Path) -> ParsedTrf:
        """Return a parsed representation of the given TRF(x) file."""
        code_lines_dict = defaultdict(list)

        with file_path.open("r", encoding="utf-8") as fh:
            lines = [TrfLine(i, line.strip()) for i, line in enumerate(fh)]

        for line in lines:
            code_lines_dict[line.get_code_type()].append(line)

        player_sections = [PlayerSection.from_string(str(player_line)) for player_line in code_lines_dict[PlayerCode]]
        team_sections = [TeamSection.from_string(str(team_line)) for team_line in code_lines_dict[TeamCode]]
        tournament_section = TournamentSection.from_lines(code_lines_dict[TournamentCode])
        x_section = XSection.from_lines(code_lines_dict[XCode])

        trf = ParsedTrf(
            player_sections=player_sections,
            team_sections=team_sections,
            tournament_section=tournament_section,
            x_section=x_section,
        )

        trf.validate_contents()
        return trf
