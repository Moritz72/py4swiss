from pydantic import BaseModel

from py4swiss.trf.exceptions import ConsistencyException
from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.results.result_token import ResultToken
from py4swiss.trf.results.round_result import RoundResult
from py4swiss.trf.results.scoring_point_system_code import ScoringPointSystemCode as C


class ScoringPointSystem(BaseModel):
    score_dict: dict[tuple[ResultToken, ColorToken], int] = {
        (ResultToken.FORFEIT_LOSS, ColorToken.WHITE): 0,
        (ResultToken.FORFEIT_WIN, ColorToken.WHITE): 10,
        (ResultToken.WIN_NOT_RATED, ColorToken.WHITE): 10,
        (ResultToken.DRAW_NOT_RATED, ColorToken.WHITE): 5,
        (ResultToken.LOSS_NOT_RATED, ColorToken.WHITE): 0,
        (ResultToken.WIN, ColorToken.WHITE): 10,
        (ResultToken.DRAW, ColorToken.WHITE): 5,
        (ResultToken.LOSS, ColorToken.WHITE): 0,
        (ResultToken.FORFEIT_LOSS, ColorToken.BLACK): 0,
        (ResultToken.FORFEIT_WIN, ColorToken.BLACK): 10,
        (ResultToken.WIN_NOT_RATED, ColorToken.BLACK): 10,
        (ResultToken.DRAW_NOT_RATED, ColorToken.BLACK): 5,
        (ResultToken.LOSS_NOT_RATED, ColorToken.BLACK): 0,
        (ResultToken.WIN, ColorToken.BLACK): 10,
        (ResultToken.DRAW, ColorToken.BLACK): 5,
        (ResultToken.LOSS, ColorToken.BLACK): 0,
        (ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 5,
        (ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 10,
        (ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED): 10,
        (ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 0
    }

    def apply_code(self, code: C, points_times_ten: int) -> None:
        match code:
            case C.WIN_WITH_WHITE:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.WHITE)] = points_times_ten
            case C.WIN_WITH_BLACK:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.BLACK)] = points_times_ten
            case C.DRAW_WITH_WHITE:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.WHITE)] = points_times_ten
            case C.DRAW_WITH_BLACK:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.BLACK)] = points_times_ten
            case C.LOSS_WITH_WHITE:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.WHITE)] = points_times_ten
            case C.LOSS_WITH_BLACK:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.BLACK)] = points_times_ten
            case C.ZERO_POINT_BYE:
                self.score_dict[(ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.HALF_POINT_BYE:
                self.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.FULL_POINT_BYE:
                self.score_dict[(ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.PAIRING_ALLOCATED_BYE:
                self.score_dict[(ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.FORFEIT_WIN:
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BLACK)] = points_times_ten
            case C.FORFEIT_LOSS:
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BLACK)] = points_times_ten
            case C.WIN:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.DRAW:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case C.LOSS:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten

    def get_points_times_ten(self, round_result: RoundResult) -> int:
        color = round_result.color
        result = round_result.result
        try:
            return self.score_dict[(result, color)]
        except IndexError:
            raise ConsistencyException(f"Color '{color.value}' does not match result {result.value}")

    def get_max(self) -> int:
        return max(self.score_dict.values())

    def to_string(self) -> str:
        value_dict = {
            C.WIN_WITH_WHITE: self.score_dict[(ResultToken.WIN, ColorToken.WHITE)],
            C.WIN_WITH_BLACK: self.score_dict[(ResultToken.WIN, ColorToken.BLACK)],
            C.DRAW_WITH_WHITE: self.score_dict[(ResultToken.DRAW, ColorToken.WHITE)],
            C.DRAW_WITH_BLACK: self.score_dict[(ResultToken.DRAW, ColorToken.BLACK)],
            C.LOSS_WITH_WHITE: self.score_dict[(ResultToken.LOSS, ColorToken.WHITE)],
            C.LOSS_WITH_BLACK: self.score_dict[(ResultToken.LOSS, ColorToken.BLACK)],
            C.ZERO_POINT_BYE: self.score_dict[(ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)],
            C.HALF_POINT_BYE: self.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)],
            C.FULL_POINT_BYE: self.score_dict[(ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)],
            C.PAIRING_ALLOCATED_BYE: self.score_dict[(ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED)],
            C.FORFEIT_WIN: self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.WHITE)],
            C.FORFEIT_LOSS: self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.WHITE)]
        }
        parts = [f"{code.value}={round(points_times_ten / 10, 1)}" for code, points_times_ten in value_dict.items()]
        return " ".join(parts)
