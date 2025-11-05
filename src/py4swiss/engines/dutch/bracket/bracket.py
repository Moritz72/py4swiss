from typing import Self

from pydantic import BaseModel

from py4swiss.engines.dutch.player import Player


class Bracket(BaseModel):
    """
    Represents the state of a pairing bracket.

    This includes not only the players (MDPs and residents) within the bracket themselves but also
    the players of the next score group as well as various properties of the bracket.

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
    def _get_score_difference_bits(mdp_list: list[Player], resident_list: list[Player]) -> tuple[int, dict[int, int]]:
        """
        Returns the number of bits necessary to represent all occurrences of all score differences
        as well as a dictionary containing the number of bits necessary to represent all
        occurrences of the given score difference for the given MDPs and residents.
        """
        # Count potential downfloats
        # "For each downfloater, the SD is defined as the difference between the score of the
        # downfloater, and an artificial value that is one point less than the score of the lowest
        # ranked player of the current bracket (even when this yields a negative value)."
        point_differences = [player.points - resident_list[-1].points + 10 for player in mdp_list + resident_list]

        # Count the possible score difference between MDPs and residents. Note that MDPs can never
        # be paired with one another, since they would already have been paired in the previous
        # bracket, if that was the case.
        for mdp in mdp_list:
            point_differences.extend({mdp.points - resident.points for resident in resident_list})

        # Count the possible score differences between residents. Note that here a non-zero score
        # is only possible if the bracket is the CLB.
        for i, resident in enumerate(resident_list):
            point_differences.extend({resident.points - other.points for other in resident_list[i + 1 :]})

        bits = {key: point_differences.count(key).bit_length() for key in point_differences}
        cumulative_bits = {}
        running_total = 0

        # Add the sum of all score difference bits lower than the current one to itself. By doing
        # this, a binary string of length equal to the score difference bit total can be subdivided
        # into parts at the resulting bit numbers in order to easily separate occurrences of
        # different score differences in order of importance from highest to lowest.
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
        collapsed: bool,
    ) -> Self:
        """Returns an instance given the minimal necessary information."""
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
            score_difference_bit_dict=score_difference_bit_dict,
        )
