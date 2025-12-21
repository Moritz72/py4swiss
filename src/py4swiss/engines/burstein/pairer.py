from py4swiss.engines.burstein.criteria import (
    ABSOLUTE_CRITERIA,
    COLOR_CRITERIA,
    QUALITY_CRITERIA,
)
from py4swiss.engines.burstein.player import Player, PlayerRole
from py4swiss.engines.burstein.state import State
from py4swiss.engines.matching import Matcher


class Pairer:
    """
    A class used to perform the pairing process for a bracket.

    This process is as follows:
        - Determine the pairings
        - Retrieve the chosen pairings after determining colors
    """

    def __init__(self, players: list[Player], state: State) -> None:
        """Initialize a new matcher along with the heterogeneous and homogeneous brackets."""
        self._players: list[Player] = players
        self._state: State = state

        self._matcher: Matcher[Player] = Matcher(
            self._players,
            self._state,
            (ABSOLUTE_CRITERIA[0], ABSOLUTE_CRITERIA[2]),
            QUALITY_CRITERIA,
            COLOR_CRITERIA,
            self._state.bracket_bits,
        )

        self._resident_list = [player for player in self._players if player.role == PlayerRole.RESIDENT]

    def determine_pairings(self) -> None:
        """Determine the first best round pairing."""
        # FIDE handbook: "3.2 Pairing Process for a Bracket"
        # 3.2.1 Preparation
        #     The pairing of a bracket is composed of pairs and outgoing floaters.
        #     Determine the maximum number of pairs that can be obtained in the current bracket while complying with
        #     criteria from [C1] to [C5] (see Articles 2.1.1 to 2.3.1).
        #     This automatically determines the number of outgoing floaters.
        # 3.2.2 Operations
        #     Choose the first pairing (as ordered according to Article 4) that complies best with all the pairing
        #     criteria ([C1] to [C8], see Articles 2.1 to 2.3).
        #     Consider that a pairing is better than another if it better satisfies a quality criterion ([C5]-[C8], see
        #     Article 2.3) of higher priority.

        # FIDE handbook: "4. Order of Pairings"
        # 4.1 All players in the bracket shall be tagged with consecutive in-bracket sequence-numbers (BSN for short)
        #     representing their respective ranking order (according to Article 1.8) in the bracket (i.e. 1, 2, 3, 4,
        #     ...).
        # 4.2 The bracket is then extended, adding a number of virtual players equal to the number of outgoing floaters
        #     (see [C5], Article 2.3.1). All those virtual players are assigned a BSN equal to zero, meaning that their
        #     opponent shall float.
        # 4.3 In order to sort all the possible pairings, apply the following rule: a pairing precedes another if its
        #     BSN #1's opponent has a larger BSN (i.e. lower ranking) than the other's. If BSN #1's opponents are the
        #     same, then compare BSN #2's opponents; and so on.

        for i, resident in enumerate(self._resident_list):
            # Incentivize the resident being paired with other residents in order. Pairing with the lowest ranked
            # available player is incentivized the most, while pairing with the highest is incentivized the least. This
            # ensures that the player is paired with the highest ranked player out of all possible choices.
            self._matcher.add_to_weights(resident, self._resident_list[i + 1 :], 0, increment=True)
            self._matcher.update_matching()

            match = self._matcher.matching[resident]

            # Finalize the pairing of the players so that it does not get overwritten in the future. This ensures that
            # players with lower BSN take precedence.
            self._matcher.finalize_match(resident, match)
            self._matcher.finalize_match(resident, match)

    def get_player_pairs(self) -> list[tuple[Player, Player]]:
        """
        Return the chosen pairings as a list of tuples.

        For each item the first player in each tuple is to receive the white pieces and the second player the black
        pieces in adherence to the color criteria. A possibly unpaired player is denoted by a tuple of that player with
        themselves.
        """
        player_pairs = []

        for player_1, player_2 in self._matcher.matching.items():
            # Ignore pairings with players from lower brackets.
            if not all(player.role == PlayerRole.RESIDENT for player in (player_1, player_2)):
                continue
            # Avoid counting each pair twice.
            if player_1 > player_2:
                player_pairs.append(self._matcher.get_player_pair(player_1, player_2))

        return player_pairs
