from pathlib import Path

from pydantic import BaseModel, Field

from py4swiss.trf.exceptions import ConsistencyException
from py4swiss.trf.sections import (
    PlayerSection,
    TeamSection,
    TournamentSection,
    XSection,
)


class ParsedTrf(BaseModel):
    """
    Representation of a parsed TRF(x) as defined by FIDE and javafo.

    Attributes:
        player_sections (list[PlayerSection]): Sections containing player information
        tournament_section (TournamentSection): Section containing tournament information
        team_sections (list[TeamSection]): Sections containing team information
        x_section (XSection): Sections containing javafo specific information
    """

    player_sections: list[PlayerSection] = Field(default_factory=list)
    tournament_section: TournamentSection = Field(default_factory=TournamentSection)
    team_sections: list[TeamSection] = Field(default_factory=list)
    x_section: XSection = Field(default_factory=XSection)

    def _validate_round_number(self) -> None:
        """Validate that all information is consistent with the number of rounds."""
        number_of_rounds = self.x_section.number_of_rounds
        if number_of_rounds is None:
            raise ConsistencyException("No number of rounds provided")

        results_lengths = {len(player_section.results) for player_section in self.player_sections}
        if max(results_lengths) > number_of_rounds:
            raise ConsistencyException("Some players have more results than there are rounds")

    def _validate_starting_numbers(self) -> None:
        """Validate that the starting numbers of the players are consistent."""
        starting_numbers = {player_section.starting_number for player_section in self.player_sections}
        for i in range(len(self.player_sections)):
            if i + 1 not in starting_numbers:
                raise ConsistencyException(f"Starting number '{i + 1}' is missing")

    def _validate_points(self) -> None:
        """Validate that all player points are consistent with their results."""
        score_point_system = self.x_section.score_point_system

        for player_section in self.player_sections:
            name = player_section.name
            calculated = sum(score_point_system.get_points_times_ten(result) for result in player_section.results)
            expected = player_section.points_times_ten or 0

            if calculated != expected:
                points_c = round(calculated / 10, 1)
                points_e = round(expected / 10, 1)
                raise ConsistencyException(f"Calculated points for {name} as {points_c:.1f}, expected {points_e:.1f}")

    def validate_contents(self) -> None:
        """Validate all information contained in the TRF."""
        self._validate_round_number()
        self._validate_starting_numbers()
        self._validate_points()

    def write_to_file(self, file_path: Path) -> None:
        """Write the TRF to a given file."""
        lines = [player_section.to_string() for player_section in self.player_sections]
        lines += self.x_section.to_lines()

        file_path.parent.mkdir(exist_ok=True)
        with file_path.open("w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
            fh.write("\n")
