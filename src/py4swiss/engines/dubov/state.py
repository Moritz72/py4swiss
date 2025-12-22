from typing import Self

from pydantic import BaseModel

from py4swiss.engines.dubov.player import Player, PlayerRole


class State(BaseModel):
    """
    Represents the state of a pairing bracket.

    Attributes:
        forbidden_pairs (set[tuple[int, int]]): The pairs of players that are not allowed to be paired with each other
        initial_color (bool): Whether the initial color for the first seed is white
        is_first_round (bool): Whether it is currently the first round
        is_last_round (bool): Whether it is currently the last round
        bracket_bits (int): The number of bits to represent all residents
        score_difference_total_bits (int): The number of bits to represent all score differences
        score_difference_bit_dict (dict[int, int]): The number of bits for each difference
        upfloat_total_bits (int): The number of bits to represent all numbers of upfloats
        upfloat_bit_dict (dict[int, int]): The number of bits for each number upfloats

    """

    forbidden_pairs: set[tuple[int, int]]
    initial_color: bool
    is_first_round: bool
    is_last_round: bool
    bracket_bits: int
    score_difference_total_bits: int
    score_difference_bit_dict: dict[int, int]
    upfloat_total_bits: int
    upfloat_bit_dict: dict[int, int]

    @staticmethod
    def _get_score_difference_bits(players: list[Player]) -> tuple[int, dict[int, int]]:
        """
        Return the number of bits necessary to represent score differences as well as a dictionary.

        This refers to all occurrences of all score differences between the given players. The returned dictionary
        contains the number of bits necessary to represent all occurrences of the given score difference for the given
        players.
        """
        max_points = max(player.points_with_acceleration for player in players)
        point_differences = [max_points - player.points_with_acceleration for player in players]
        point_differences = [difference for difference in point_differences if difference != 0]

        bits = {key: point_differences.count(key).bit_length() for key in point_differences}
        cumulative_bits = {}
        running_total = 0

        # Add the sum of all score difference bits higher than the current one to itself. By doing this, a binary string
        # of length equal to the score difference bit total can be subdivided into parts at the resulting bit numbers in
        # order to easily separate occurrences of different score differences in order of importance from lowest to
        # highest.
        for key in sorted(bits, reverse=True):
            cumulative_bits[key] = running_total
            running_total += bits[key]

        return running_total, cumulative_bits

    @staticmethod
    def _get_upfloat_bits(players: list[Player]) -> tuple[int, dict[int, int]]:
        """
        Return the number of bits necessary to represent numbers of upfloats as well as a dictionary.

        This refers to all occurrences of all numbers of upfloats between the given players. The returned dictionary
        contains the number of bits necessary to represent all occurrences of the given number of upfloats for the given
        players.
        """
        upfloats = [
            player.upfloats for player in players if player.role == PlayerRole.LOWER and player.is_maximum_upfloater
        ]

        bits = {key: upfloats.count(key).bit_length() for key in upfloats}
        cumulative_bits = {}
        running_total = 0

        # Add the sum of all upfloat bits higher than the current one to itself. By doing this, a binary string of
        # length equal to the upfloat bit total can be subdivided into parts at the resulting bit numbers in order to
        # easily separate occurrences of different numbers of upfloats in order of importance from lowest to highest.
        for key in sorted(bits):
            cumulative_bits[key] = running_total
            running_total += bits[key]

        return running_total, cumulative_bits

    @classmethod
    def from_data(
        cls,
        players: list[Player],
        round_number: int,
        number_of_rounds: int,
        forbidden_pairs: set[tuple[int, int]],
        initial_color: bool,
    ) -> Self:
        """Return a bracket given the minimal necessary information."""
        score_difference_total_bits, score_difference_bit_dict = cls._get_score_difference_bits(players)
        upfloat_total_bits, upfloat_bit_dict = cls._get_upfloat_bits(players)
        return cls(
            forbidden_pairs=forbidden_pairs,
            initial_color=initial_color,
            is_first_round=round_number == 1,
            is_last_round=round_number == number_of_rounds,
            bracket_bits=sum(player.role == PlayerRole.RESIDENT for player in players).bit_length(),
            score_difference_total_bits=score_difference_total_bits,
            score_difference_bit_dict=score_difference_bit_dict,
            upfloat_total_bits=upfloat_total_bits,
            upfloat_bit_dict=upfloat_bit_dict,
        )
