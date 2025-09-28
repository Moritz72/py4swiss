from typing import Self

from pydantic import BaseModel

from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.results.result_token import ResultToken


class RoundResult(BaseModel):
    id: int
    color: ColorToken
    result: ResultToken

    @classmethod
    def from_section(cls, section: str) -> Self:
        if len(section) < 8 or any(section[i] != " " for i in {4, 6}):
            raise ValueError
        player_id = int(section[:4].lstrip())
        color_token = ColorToken(section[5].replace(" ", "-"))
        result_token = ResultToken(section[7].upper())
        return cls(id=player_id, color=color_token, result=result_token)

    def to_string(self) -> str:
        if self.id == 0:
            id_string = "0000"
        else:
            id_string = str(self.id)
        return f"{id_string:>6} {self.color.value} {self.result.value}"
