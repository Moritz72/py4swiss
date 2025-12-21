from typing import Self

from pydantic import BaseModel

from py4swiss.engines.burstein.player import Player, PlayerRole


class State(BaseModel):
    """
    Represents the state of a pairing bracket.

    Attributes:
        forbidden_pairs (set[tuple[int, int]]): The pairs of players that are not allowed to be paired with each other
        initial_color (bool): Whether the initial color for the first seed is white
        bracket_bits (int): The number of bits to represent all residents
        lower_bits (int): The number of bits to represent all residents in the lower bracket
        resident_score_total_bits (int): The number of bits to represent all scores of residents
        resident_score_bit_dict (dict[int, int]): The number of bits for each score of residents

    """

    forbidden_pairs: set[tuple[int, int]]
    initial_color: bool
    bracket_bits: int
    lower_bits: int
    resident_score_total_bits: int
    resident_score_bit_dict: dict[int, int]

    @staticmethod
    def _get_score_bits(players: list[Player]) -> tuple[int, dict[int, int]]:
        """
        Return the number of bits necessary to represent scores as well as a dictionary.

        This refers to all occurrences of all scores between the given players. The returned dictionary contains the
        number of bits necessary to represent all occurrences of the given score for the given players.
        """
        scores = [player.points_with_acceleration for player in players]

        bits = {key: scores.count(key).bit_length() for key in set(scores)}
        cumulative_bits = {}
        running_total = 0

        # Add the sum of all score  bits higher than the current one to itself. By doing this, a binary string of length
        # equal to the score bit total can be subdivided into parts at the resulting bit numbers in order to easily
        # separate occurrences of different scores in order of importance from lowest to highest.
        for key in sorted(bits, reverse=True):
            cumulative_bits[key] = running_total
            running_total += bits[key]

        return running_total, cumulative_bits

    @classmethod
    def from_data(cls, players: list[Player], forbidden_pairs: set[tuple[int, int]], initial_color: bool) -> Self:
        """Return a bracket given the minimal necessary information."""
        resident_list = [player for player in players if player.role == PlayerRole.RESIDENT]
        lower_list = [player for player in players if player.role == PlayerRole.LOWER]
        resident_score_total_bits, resident_score_bit_dict = cls._get_score_bits(resident_list)
        return cls(
            forbidden_pairs=forbidden_pairs,
            initial_color=initial_color,
            bracket_bits=len(resident_list).bit_length(),
            lower_bits=len(lower_list).bit_length(),
            resident_score_total_bits=resident_score_total_bits,
            resident_score_bit_dict=resident_score_bit_dict,
        )
