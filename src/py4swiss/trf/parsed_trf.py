from pathlib import Path

from pydantic import BaseModel, Field

from py4swiss.trf.exceptions import ConsistencyError
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
        player_sections (list[PlayerSection]): The sections containing player information
        tournament_section (TournamentSection): The section containing tournament information
        team_sections (list[TeamSection]): The sections containing team information
        x_section (XSection): The section containing javafo specific information

    """

    player_sections: list[PlayerSection] = Field(default_factory=list)
    tournament_section: TournamentSection = Field(default_factory=TournamentSection)
    team_sections: list[TeamSection] = Field(default_factory=list)
    x_section: XSection

    def _validate_round_number(self) -> None:
        """Validate that all information is consistent with the number of rounds."""
        for player_section in self.player_sections:
            if len(player_section.results) > self.x_section.number_of_rounds:
                error_message = f"Starting number '{player_section.starting_number}' has too many results"
                raise ConsistencyError(error_message)

    def _validate_starting_numbers(self) -> None:
        """Validate that the starting numbers of the players are consistent."""
        starting_numbers = {player_section.starting_number for player_section in self.player_sections}
        for i in range(len(self.player_sections)):
            if i + 1 not in starting_numbers:
                error_message = f"Starting number '{i + 1}' is missing"
                raise ConsistencyError(error_message)

    def _validate_points(self) -> None:
        """Validate that all player points are consistent with their respective results."""
        score_point_system = self.x_section.scoring_point_system

        for player_section in self.player_sections:
            number = player_section.starting_number
            calculated = sum(score_point_system.get_points_times_ten(result) for result in player_section.results)
            expected = player_section.points_times_ten

            if calculated != expected:
                calculated_integer, calculated_decimal = divmod(calculated, 10)
                expected_integer, expected_decimal = divmod(expected, 10)

                cal = f"{calculated_integer}.{calculated_decimal}"
                exp = f"{expected_integer}.{expected_decimal}"

                error_message = f"Calculated points for starting number '{number}' as {cal}, expected {exp}"
                raise ConsistencyError(error_message)

    def _validate_results(self) -> None:
        """Validate that all player results are consistent with one another."""
        results_dict = {section.starting_number: section.results for section in self.player_sections}

        for number, results in results_dict.items():
            for i, round_result in enumerate(results):
                if round_result.result.is_bye():
                    continue
                opponent_number = round_result.id
                suffix = f"for the game between starting numbers '{number}' and '{opponent_number}' in round {i + 1}"

                opponent_round_results = results_dict[opponent_number]
                if len(opponent_round_results) <= i:
                    error_message = f"Missing entry {suffix}"
                    raise ConsistencyError(error_message)

                opponent_round_result = opponent_round_results[i]
                if not round_result.result.is_compatible_with(opponent_round_result.result):
                    error_message = f"Incompatible result entries {suffix}"
                    raise ConsistencyError(error_message)
                if round_result.color == opponent_round_result.color:
                    error_message = f"Incompatible color entries {suffix}"
                    raise ConsistencyError(error_message)

    def validate_contents(self) -> None:
        """Validate all information contained in the TRF."""
        self._validate_round_number()
        self._validate_starting_numbers()
        self._validate_points()
        self._validate_results()

    def write_to_file(self, file_path: Path) -> None:
        """Write the TRF to a given file path."""
        lines = self.tournament_section.to_strings()
        lines += [player_section.to_string() for player_section in self.player_sections]
        lines += [team_section.to_string() for team_section in self.team_sections]
        lines += self.x_section.to_strings()

        file_path.parent.mkdir(exist_ok=True)
        with file_path.open("w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
            fh.write("\n")
