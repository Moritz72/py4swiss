from enum import Enum

from pydantic import BaseModel, Field

from py4swiss.trf.codes import PlayerCode
from py4swiss.trf.exceptions import LineException
from py4swiss.trf.results import RoundResult


class Sex(str, Enum):
    """Enum for the sex of a player."""

    MALE = "m"
    FEMALE = "w"


class Title(str, Enum):
    """Enum for the title of a player."""

    GRANDMASTER = "GM"
    INTERNATIONAL_MASTER = "IM"
    WOMEN_GRANDMASTER = "WGM"
    FIDE_MASTER = "FM"
    WOMEN_INTERNATIONAL_MASTER = "WIM"
    CANDIDATE_MASTER = "CM"
    WOMEN_FIDE_MASTER = "WFM"
    WOMEN_CANDIDATE_MASTER = "WCM"


class PlayerSection(BaseModel):
    """
    Representation of a parsed player section of a TRF.

    Attributes:
        code (PlayerCode | None):
        starting_number (int | None)
        sex (Sex | None)
        title (Title | None)
        name (str | None)
        fide_rating (int | None)
        fide_federation (str | None)
        fide_number (int | None)
        birth_date (tuple[int, int, int] | None)
        points_times_ten (int | None)
        rank (int | None)
        results (list[RoundResult])
    """

    code: PlayerCode | None = None
    starting_number: int | None = None
    sex: Sex | None = None
    title: Title | None = None
    name: str | None = None
    fide_rating: int | None = None
    fide_federation: str | None = None
    fide_number: int | None = None
    birth_date: tuple[int, int, int] | None = None
    points_times_ten: int | None = None
    rank: int | None = None
    results: list[RoundResult] = Field(default_factory=list)

    @staticmethod
    def _get_birth_date_string(birth_date: tuple[int, int, int]) -> str:
        string = ""
        if birth_date[0] == 0:
            return string
        string += str(birth_date[0]).zfill(4)
        if birth_date[1] == 0:
            return string
        string += "/"
        string += str(birth_date[1]).zfill(2)
        if birth_date[2] == 0:
            return string
        string += "/"
        string += str(birth_date[2]).zfill(2)
        return string

    @staticmethod
    def _get_points_string(points_times_ten: int) -> str:
        return f"{points_times_ten // 10}.{points_times_ten % 10}"

    def set_code(self, line: str) -> None:
        section = line[0:3]
        try:
            if bool(section.strip()):
                self.code = PlayerCode(section)
        except ValueError as e:
            raise LineException(f"Invalid player code '{section}'", column=1) from e

    def set_starting_number(self, line: str) -> None:
        section = line[4:8]
        try:
            if bool(section.strip()):
                self.starting_number = int(section.lstrip())
        except ValueError as e:
            raise LineException(f"Invalid starting rank '{section}'", column=5) from e

    def set_sex(self, line: str) -> None:
        section = line[9]
        try:
            if bool(section.strip()):
                self.sex = Sex(section)
        except ValueError as e:
            raise LineException(f"Invalid sex '{section}'", column=10) from e

    def set_title(self, line: str) -> None:
        section = line[10:13]
        try:
            if bool(section.strip()):
                self.title = Title(section.strip().upper())
        except ValueError as e:
            raise LineException(f"Invalid title '{section}'", column=11) from e

    def set_name(self, line: str) -> None:
        section = line[14:47]
        if bool(section.strip()):
            self.name = section.strip()

    def set_fide_rating(self, line: str) -> None:
        section = line[48:52]
        try:
            if bool(section.strip()):
                self.fide_rating = int(section.lstrip())
        except ValueError as e:
            raise LineException(f"Invalid fide rating '{section}'", column=53) from e

    def set_fide_federation(self, line: str) -> None:
        section = line[53:56]
        if bool(section.strip()):
            self.fide_federation = section.strip()

    def set_fide_number(self, line: str) -> None:
        section = line[57:68]
        try:
            if bool(section[:3].strip()):
                raise ValueError
            if bool(section.strip()):
                self.fide_number = int(section.lstrip())
        except ValueError as e:
            raise LineException(f"Invalid fide number '{section}'", column=58) from e

    def set_birth_date(self, line: str) -> None:
        section = line[69:79]
        try:
            if bool(section.strip()):
                year = int(section[:4].strip() or 0)
                month = int(section[5:7].strip() or 0)
                day = int(section[8:10].strip() or 0)
                self.birth_date = (year, month, day)
        except ValueError as e:
            raise LineException(f"Invalid birth date '{section}'", column=70) from e

    def set_points_times_ten(self, line: str) -> None:
        section = line[80:84]
        try:
            if bool(section.strip()):
                if section[-2] != ".":
                    raise ValueError
                self.points_times_ten = int(section[:-2].lstrip()) * 10 + int(section[-1])
        except ValueError as e:
            raise LineException(f"Invalid points '{section}'", column=81) from e

    def set_rank(self, line: str) -> None:
        section = line[85:90]
        try:
            if bool(section.strip()):
                self.rank = int(section.lstrip())
        except ValueError as e:
            raise LineException(f"Invalid rank '{section}'", column=86) from e

    def set_results(self, line: str) -> None:
        for i in range(89, len(line), 10):
            try:
                section = line[i : i + 10]
            except IndexError as e:
                if bool(line[i:].strip()):
                    raise LineException(f"Incomplete round result '{line[i:]}'", column=i + 1) from e
                return

            try:
                if any(section[i] != " " for i in (0, 1)):
                    raise ValueError
                self.results.append(RoundResult.from_section(section[2:]))
            except ValueError as e:
                raise LineException(f"Invalid round result '{section}'", column=i + 1) from e

    def to_string(self) -> str:
        code_string = self.code.value if self.code else ""
        starting_number_string = str(self.starting_number) if self.starting_number else ""
        sex_string = self.sex.value if self.sex else ""
        tite_string = self.title.value if self.title else ""
        name_string = self.name or ""
        fide_rating_string = str(self.fide_rating) if self.fide_rating else ""
        fide_federation_string = self.fide_federation or ""
        fide_number_string = str(self.fide_number) if self.fide_number else ""
        birth_date_string = self._get_birth_date_string(self.birth_date) if self.birth_date else ""
        points_string = self._get_points_string(self.points_times_ten) if self.points_times_ten else "0.0"
        rank_string = str(self.rank) if self.rank else ""

        line = ""
        line += f"{code_string:>3} {starting_number_string:>4} {sex_string:>1}{tite_string:>3} {name_string:<33} "
        line += f"{fide_rating_string:>4} {fide_federation_string:>3} {fide_number_string:>11} {birth_date_string:<10} "
        line += f"{points_string:>4} {rank_string:>4}"
        for result in self.results:
            line += result.to_string().ljust(10)

        return line
