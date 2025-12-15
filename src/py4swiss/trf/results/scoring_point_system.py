from pydantic import BaseModel

from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.results.result_token import ResultToken
from py4swiss.trf.results.round_result import RoundResult
from py4swiss.trf.results.scoring_point_system_code import ScoringPointSystemCode

ScoreDict = dict[tuple[ResultToken, ColorToken], int]

# A mapping of codes to tuples of result tokens necessary to construct a concised representation of the scoring system.
SCORING_POINT_SYSTEM_IDENTIFIER_DICT = {
    ScoringPointSystemCode.WIN_WITH_WHITE: (ResultToken.WIN, ColorToken.WHITE),
    ScoringPointSystemCode.WIN_WITH_BLACK: (ResultToken.WIN, ColorToken.BLACK),
    ScoringPointSystemCode.DRAW_WITH_WHITE: (ResultToken.DRAW, ColorToken.WHITE),
    ScoringPointSystemCode.DRAW_WITH_BLACK: (ResultToken.DRAW, ColorToken.BLACK),
    ScoringPointSystemCode.LOSS_WITH_WHITE: (ResultToken.LOSS, ColorToken.WHITE),
    ScoringPointSystemCode.LOSS_WITH_BLACK: (ResultToken.LOSS, ColorToken.BLACK),
    ScoringPointSystemCode.ZERO_POINT_BYE: (ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED),
    ScoringPointSystemCode.HALF_POINT_BYE: (ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED),
    ScoringPointSystemCode.FULL_POINT_BYE: (ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED),
    ScoringPointSystemCode.PAIRING_ALLOCATED_BYE: (ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED),
    ScoringPointSystemCode.FORFEIT_WIN: (ResultToken.FORFEIT_WIN, ColorToken.WHITE),
    ScoringPointSystemCode.FORFEIT_LOSS: (ResultToken.FORFEIT_LOSS, ColorToken.WHITE),
}


class ScoringPointSystem(BaseModel):
    """
    A scoring system for a tournament supporting all codes defined by javafo.

    Attributes:
        score_dict (ScoreDict): The number of points times ten awarded for pairs of result and color token

    """

    score_dict: ScoreDict = {
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
        (ResultToken.FORFEIT_LOSS, ColorToken.BYE_OR_NOT_PAIRED): 0,
        (ResultToken.FORFEIT_WIN, ColorToken.BYE_OR_NOT_PAIRED): 10,
        (ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 5,
        (ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 10,
        (ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED): 10,
        (ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED): 0,
    }

    def apply_code(self, code: ScoringPointSystemCode, points_times_ten: int) -> None:
        """Update the score dictionary entry for all pairs covered by the given code to the given number of points."""
        # javafo Advanced User Manual
        # WW  | 1.0 | points for win with White
        # BW  | 1.0 | points for win with Black
        # WD  | 0.5 | points for draw with White
        # BD  | 0.5 | points for draw with Black
        # WL  | 0.0 | points for loss with White
        # BL  | 0.0 | points for loss with Black
        # ZPB | 0.0 | points for zero-point-bye
        # HPB | 0.5 | points for half-point-bye
        # FPB | 1.0 | points for full-point-bye
        # PAB | 1.0 | points for pairing-allocated-bye
        # FW  | 1.0 | points for forfeit win
        # FL  | 0.0 | points for forfeit loss
        # W   | 1.0 | encompasses all the codes WW, BW, FW, FPB
        # D   | 0.5 | encompasses all the codes WD, BD, HPB
        # L   | 0.0 | encompasses all the codes WL, BL, ZPB, FL (not supported by javafo)
        match code:
            case ScoringPointSystemCode.WIN_WITH_WHITE:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.WHITE)] = points_times_ten
            case ScoringPointSystemCode.WIN_WITH_BLACK:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.BLACK)] = points_times_ten
            case ScoringPointSystemCode.DRAW_WITH_WHITE:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.WHITE)] = points_times_ten
            case ScoringPointSystemCode.DRAW_WITH_BLACK:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.BLACK)] = points_times_ten
            case ScoringPointSystemCode.LOSS_WITH_WHITE:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.WHITE)] = points_times_ten
            case ScoringPointSystemCode.LOSS_WITH_BLACK:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.BLACK)] = points_times_ten
            case ScoringPointSystemCode.ZERO_POINT_BYE:
                self.score_dict[(ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.HALF_POINT_BYE:
                self.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.FULL_POINT_BYE:
                self.score_dict[(ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.PAIRING_ALLOCATED_BYE:
                self.score_dict[(ResultToken.PAIRING_ALLOCATED_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.FORFEIT_WIN:
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.FORFEIT_LOSS:
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.WIN:
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.WIN_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.WIN, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_WIN, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
                self.score_dict[(ResultToken.FULL_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.DRAW:
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.DRAW_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.DRAW, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
            case ScoringPointSystemCode.LOSS:
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.LOSS_NOT_RATED, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.LOSS, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.WHITE)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BLACK)] = points_times_ten
                self.score_dict[(ResultToken.FORFEIT_LOSS, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten
                self.score_dict[(ResultToken.ZERO_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)] = points_times_ten

    def get_points_times_ten(self, round_result: RoundResult) -> int:
        """Return the number of points times ten awarded for a round result of a player."""
        return self.score_dict[(round_result.result, round_result.color)]
