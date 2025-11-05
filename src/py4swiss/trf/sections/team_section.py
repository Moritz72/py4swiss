from pydantic import BaseModel, Field

from py4swiss.trf.codes import TeamCode
from py4swiss.trf.exceptions import LineException


class TeamSection(BaseModel):
    """
    Representation of a parsed team section of a TRF.
    """

    code: TeamCode | None = None
    team_name: str | None = None
    team_players: list[int] = Field(default_factory=list)

    @staticmethod
    def _parse_team_player(section: str) -> int | None:
        if not bool(section.strip()):
            return None
        return int(section.lstrip())

    def set_code(self, line: str) -> None:
        section = line[0:3]
        try:
            if bool(section.strip()):
                self.code = TeamCode(section)
        except ValueError as e:
            raise LineException(f"Invalid team code '{section}'", column=1) from e

    def set_team_name(self, line: str) -> None:
        section = line.rjust(36)[4:36]
        if bool(section.strip()):
            self.team_name = section.strip()

    def set_team_players(self, line: str) -> None:
        blank = False
        for i in range(36, len(line), 5):
            try:
                section = line[i : i + 5]
            except IndexError as e:
                if bool(line[i:].strip()):
                    raise LineException(f"Incomplete team player starting rank '{line[i:]}'", column=i + 1) from e
                return

            try:
                starting_rank = self._parse_team_player(section)
                if starting_rank is None:
                    blank = True
                elif blank:
                    raise LineException("Missing team player starting rank", column=i - 4)
                else:
                    self.team_players.append(starting_rank)
            except ValueError as e:
                raise LineException(f"Invalid team player starting rank '{section}'", column=i + 1) from e
