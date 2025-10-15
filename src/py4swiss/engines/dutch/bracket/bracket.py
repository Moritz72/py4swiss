from typing import Self

from pydantic import BaseModel

from py4swiss.engines.dutch.player import Player


class Bracket(BaseModel):
    """
    Represents the state of a pairing bracket.

    Attributes:
        one_round_played (bool): Whether at least one round has been played
        two_rounds_played (bool): Whether at least two rounds have been played
        penultimate_pairing_bracket (bool): Whether this is the penultimate pairing bracket
        last_pairing_bracket (bool): Whether this is the last pairing bracket
        min_bracket_score (int): The lowest score of residents in the bracket
        bracket_bits (int): The number of bits to represent all residents
        low_bracket_bits (int): The number of bits to represent all players in the lower bracket
        score_difference_total_bits (int): The number of bits to represent all score differences
        score_difference_bit_dict (dict[int, int]): The number of bits for each difference
    """
    mdp_list: list[Player]
    resident_list: list[Player]
    lower_list: list[Player]
    one_round_played: bool
    two_rounds_played: bool
    penultimate_pairing_bracket: bool
    last_pairing_bracket: bool
    min_bracket_score: int
    bracket_bits: int
    low_bracket_bits: int
    score_difference_total_bits: int
    score_difference_bit_dict: dict[int, int]

    @staticmethod
    def _get_score_difference_bits(
            mdp_list: list[Player],
            resident_list: list[Player]
    ) -> tuple[int, dict[int, int]]:
        point_differences = [player.points - resident_list[-1].points + 10 for player in mdp_list + resident_list]

        for mdp in mdp_list:
            point_differences.extend({mdp.points - resident.points for resident in resident_list})

        for i, resident in enumerate(resident_list):
            point_differences.extend({resident.points - other.points for other in resident_list[i + 1:]})

        bits = {key: point_differences.count(key).bit_length() for key in point_differences}
        cumulative_bits = {}
        running_total = 0

        for key in sorted(bits):
            cumulative_bits[key] = running_total
            running_total += bits[key]

        return running_total, cumulative_bits

    @classmethod
    def from_data(
            cls,
            mdp_list: list[Player],
            resident_list: list[Player],
            lower_list: list[Player],
            round_number: int,
            collapsed: bool
    ) -> Self:
        score_difference_total_bits, score_difference_bit_dict = cls._get_score_difference_bits(mdp_list, resident_list)
        return cls(
            mdp_list=mdp_list,
            resident_list=resident_list,
            lower_list=lower_list,
            one_round_played=round_number > 1,
            two_rounds_played=round_number > 2,
            penultimate_pairing_bracket=collapsed,
            last_pairing_bracket=not bool(lower_list),
            min_bracket_score=resident_list[-1].points,
            bracket_bits=len(resident_list).bit_length(),
            low_bracket_bits=len(lower_list).bit_length(),
            score_difference_total_bits=score_difference_total_bits,
            score_difference_bit_dict=score_difference_bit_dict
        )
