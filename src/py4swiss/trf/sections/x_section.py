from pydantic import BaseModel, Field

from py4swiss.trf.codes import XCode
from py4swiss.trf.exceptions import LineException
from py4swiss.trf.results import ScoringPointSystem, ScoringPointSystemCode


class XSectionConfiguration(BaseModel):
    by_rank: bool = False
    first_round_color: bool | None = None

    def to_string(self) -> str:
        items = []

        if self.by_rank:
            items.append("rank")

        if self.first_round_color is not None:
            if self.first_round_color:
                items.append("white1")
            else:
                items.append("black1")

        return " ".join(items)


class XSection(BaseModel):
    number_of_rounds: int | None = None
    zeroed_ids: set[int] = Field(default_factory=set)
    score_point_system: ScoringPointSystem = Field(default_factory=ScoringPointSystem)
    configuration: XSectionConfiguration = Field(default_factory=XSectionConfiguration)
    accelerations: dict[int, list[int]] = Field(default_factory=dict)
    forbidden_pairs: list[tuple[int, int]] = Field(default_factory=list)

    def set_number_of_rounds(self, line: str) -> None:
        sections = line.split()
        if len(sections) != 2:
            raise LineException(f"Invalid number_of_rounds line '{line}'")
        try:
            number_of_rounds = int(sections[1])
            self.number_of_rounds = number_of_rounds
        except ValueError as e:
            raise LineException(f"Invalid number of rounds '{sections[1]}'") from e

    def add_zeroed_id(self, section: str) -> None:
        try:
            zeroed_id = int(section.lstrip())
            self.zeroed_ids.add(zeroed_id)
        except ValueError as e:
            raise LineException(f"Invalid player id '{section}'") from e

    def adjust_score_point_system(self, section: str) -> None:
        if "=" not in section or section.count("=") != 1:
            raise ValueError
        code_string, point_string = section.split("=")

        try:
            code = ScoringPointSystemCode(code_string)
        except ValueError as e:
            raise LineException(f"Invalid score point system code '{code_string}'") from e

        try:
            if "." in point_string:
                integer_string, decimal_string = point_string.split(".")
            else:
                integer_string = point_string
                decimal_string = ""
            if len(decimal_string) > 1:
                raise ValueError
            points_times_ten = int(integer_string) * 10 + int(decimal_string)
        except ValueError as e:
            raise LineException(f"Invalid score point system points '{point_string}'") from e

        self.score_point_system.apply_code(code, points_times_ten)

    def adjust_configuration(self, section: str) -> None:
        match section.strip():
            case "rank":
                self.configuration.by_rank = True
            case "white1":
                self.configuration.first_round_color = True
            case "black1":
                self.configuration.first_round_color = False
            case _:
                raise LineException(f"Invalid configuration code '{section}'")

    def add_acceleration(self, line: str) -> None:
        sections = line.split()
        if len(sections) < 2:
            raise LineException(f"Incomplete acceleration code line '{line}'")

        try:
            player_id = int(sections[1].lstrip())
            points_times_ten_list = []
        except ValueError as e:
            raise LineException(f"Invalid acceleration player id '{sections[1]}'") from e

        for section in sections[2:]:
            try:
                integer_string, decimal_string = section.split(".")
                points_times_ten = int(integer_string) * 10 + int(decimal_string)
                points_times_ten_list.append(points_times_ten)
            except ValueError as e:
                raise LineException(f"Invalid acceleration points '{section}'") from e

        self.accelerations[player_id] = points_times_ten_list

    def add_forbidden_pair(self, line: str) -> None:
        sections = line.split()
        if len(sections) != 3:
            raise LineException(f"Invalid forbidden pairs line '{line}'")

        try:
            player_id_1 = int(sections[1])
        except ValueError as e:
            raise LineException(f"Invalid forbidden pair id '{sections[1]}'") from e

        try:
            player_id_2 = int(sections[2])
        except ValueError as e:
            raise LineException(f"Invalid forbidden pair id '{sections[2]}'") from e

        self.forbidden_pairs.append((player_id_1, player_id_2))

    def to_lines(self) -> list[str]:
        zeroed_ids_string = " ".join(str(player_id) for player_id in self.zeroed_ids)

        acceleration_strings = []
        for player_id, points_times_ten_list in self.accelerations.items():
            string = f"{player_id:>4}"
            for points_times_ten in points_times_ten_list:
                string += f"{round(points_times_ten / 10, 1):5}"
            acceleration_strings.append(string)

        lines = []
        if self.number_of_rounds is not None:
            lines += [f"{XCode.ROUNDS.value} {self.number_of_rounds}"]
        if bool(zeroed_ids_string):
            lines += [f"{XCode.ZEROED_IDS.value} {zeroed_ids_string}"]
        lines += [f"{XCode.POINT_SYSTEM.value} {self.score_point_system.to_string()}"]
        lines += [f"{XCode.CONFIGURATIONS.value} {self.configuration.to_string()}"]
        for acceleration_string in acceleration_strings:
            lines += [f"{XCode.ACCELERATIONS.value} {acceleration_string}"]
        for id_1, id_2 in self.forbidden_pairs:
            lines += [f"{XCode.FORBIDDEN_PAIRS.value} {id_1} {id_2}"]

        return lines
