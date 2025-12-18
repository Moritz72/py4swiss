from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dubov.bracket.bracket import Bracket
from py4swiss.engines.dubov.bracket.bracket_matcher import BracketMatcher
from py4swiss.engines.dubov.criteria import COLOR_CRITERIA
from py4swiss.engines.dubov.player import Player, PlayerRole


class BracketPairer:
    """
    A class used to perform the pairing process for a bracket.

    This process is as follows:
        - Determine the initial G1 and G2
        - Shift players from G1 to G2 and from G2 to G1 (first from smaller to larger, then from larger to smaller)
        - Choose T2 i.e. transpose G2
        - Retrieve the chosen pairings after determining colors
    """

    def __init__(self, bracket: Bracket, forbidden_pairs: set[tuple[int, int]], initial_color: bool) -> None:
        """Initialize a new bracket matcher along with the heterogeneous and homogeneous brackets."""
        self._bracket: Bracket = bracket
        self._initial_color: bool = initial_color

        self._bracket_matcher: BracketMatcher = BracketMatcher(self._bracket, forbidden_pairs)

        self._g1: list[Player] = []
        self._g2: list[Player] = []

    @staticmethod
    def _get_player_pair(player_1: Player, player_2: Player, initial_color: bool) -> tuple[Player, Player]:
        """
        Return a tuple of the given players.

        The first player in the tuple is to receive the white pieces and the second player the black pieces in adherence
        to the color criteria.
        """
        i = 0
        player_1_color = ColorPreferenceSide.NONE

        # Evaluate the color criteria E.1 - E.5 in order until one is conclusive. Note that E.5 is always conclusive.
        while player_1_color == ColorPreferenceSide.NONE:
            player_1_color = COLOR_CRITERIA[i].evaluate(player_1, player_2)
            i += 1

        # The E.1 implementation assumes that the first seed gets the white pieces in the first round.
        if i == 1 and not initial_color:
            player_1_color = player_1_color.get_opposite()

        match player_1_color:
            case ColorPreferenceSide.WHITE:
                return player_1, player_2
            case ColorPreferenceSide.BLACK:
                return player_2, player_1
            case _:  # pragma: no cover
                error_message = "Unreachable code reached"
                raise AssertionError(error_message)

    def _get_match_role(self, player: Player) -> PlayerRole:
        """Return the role of the player with which the given player is currently matched."""
        return self._bracket_matcher.matching[player].role

    def _has_resident_match(self, player: Player) -> bool:
        """Check whether the given player is currently matched to a resident."""
        return self._get_match_role(player) == PlayerRole.RESIDENT

    def _has_g1_match(self, player: Player) -> bool:
        """Check whether the given player is currently matched to a player in G1."""
        return self._bracket_matcher.matching[player] in self._g1

    def _has_g2_match(self, player: Player) -> bool:
        """Check whether the given player is currently matched to a player in G2."""
        return self._bracket_matcher.matching[player] in self._g2

    def _shift_from_g1_to_g2(self) -> None:
        """Shift players from G1 to G2."""
        # The number of exchanges is already determined by the quality criteria.
        exchanges = sum(self._bracket_matcher.matching[player] in self._g1 for player in self._g1)

        # FIDE handbook: "4.3 Sorting the Shifters | 4.3.3"
        # With the list sorted as in 4.3.2, assign the sequence numbers, starting with the player in the (remaining)
        # middle of the list or, when two players are in the (remaining) middle, to the one with a higher position in
        # the list.

        length = len(self._g1)
        middle = (length - 1) / 2
        permutation = sorted(range(length), key=lambda i: (abs(i - middle), -i if i <= middle else i))
        numbered_g1 = [self._g1[i] for i in permutation]

        for player in numbered_g1:
            # Stop immediately, if there are no more exchanges to be made.
            if exchanges == 0:
                return

            was_exchanged = self._has_g1_match(player)

            # If the player is not currently matched to a player in G1, incentivize pairings with players in G1, by
            # adding 1 to each edge weight between them. This will force pairing with a player in G1, if this is
            # possible while still satisfying all quality criteria as well as before this modification.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(player, self._g1, 1)
                self._bracket_matcher.update_matching()

                # Remove the performed modification, as to not interfere with future iterations.
                self._bracket_matcher.add_to_weights(player, self._g1, -1)

            # If the player is now matched to a player in G1, finalize the fact that it will be matched to a player in
            # G1 by removing all edge weights with players in G2.
            if self._has_g1_match(player):
                exchanges -= 1
                self._bracket_matcher.remove_weights(player, self._g2)
                self._g1.remove(player)
                self._g2.append(player)

    def _shift_from_g2_to_g1(self) -> None:
        """Shift players from G2 to G1."""
        # The number of exchanges is already determined by the quality criteria.
        exchanges = sum(self._bracket_matcher.matching[player] in self._g2 for player in self._g2)

        # FIDE handbook: "4.3 Sorting the Shifters | 4.3.3"
        # With the list sorted as in 4.3.2, assign the sequence numbers, starting with the player in the (remaining)
        # middle of the list or, when two players are in the (remaining) middle, to the one with a higher position in
        # the list.

        length = len(self._g2)
        middle = (length - 1) / 2
        permutation = sorted(range(length), key=lambda i: (abs(i - middle), -i if i <= middle else i))
        numbered_g2 = [self._g2[i] for i in permutation]

        for player in numbered_g2:
            # Stop immediately, if there are no more exchanges to be made.
            if exchanges == 0:
                return

            was_exchanged = self._has_g2_match(player)

            # If the player is not currently matched to a player in G2, incentivize pairings with players in G2, by
            # adding 1 to each edge weight between them. This will force pairing with a player in G2, if this is
            # possible while still satisfying all quality criteria as well as before this modification.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(player, self._g2, 1)
                self._bracket_matcher.update_matching()

                # Remove the performed modification again, as to not interfere with future iterations.
                self._bracket_matcher.add_to_weights(player, self._g2, -1)

            # If the player is now matched to a player in G2, finalize the fact that it will be matched to a player in
            # G2 by removing all edge weights with players in G1.
            if self._has_g2_match(player):
                exchanges -= 1
                self._bracket_matcher.remove_weights(player, self._g1)
                self._g2.remove(player)
                self._g1.append(player)

    def determine_initial_g1_and_g2(self) -> None:
        """Determine the initial compositions of G1 and G2."""
        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.1"
        # Determine the minimum number of upfloaters needed to obtain a legal pairing of all the (remaining) resident
        # players of the scoregroup.
        # Note: A pairing is legal when the criteria [C1], [C3] and [C4] (see Articles 2.1.1, 2.1.3 and 2.2.1
        # respectively) are complied with.

        # The number of upfloaters is already determined by the quality criteria.
        upfloaters = sum(self._has_resident_match(player) for player in self._bracket.lower_list)

        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.2"
        # Choose the first set of upfloaters (first in the order given by Article 4.2) that, together with the
        # (remaining) resident players of this scoregroup, produces a pairing that complies at best with all the pairing
        # criteria ([C1] to [C10], see Articles 2.1 to 2.3).
        # Note: To choose the best set of upfloaters, consider that the ensuing bracket (residents + upfloaters) is
        # paired better than another one if it better satisfies a quality criterion ([C5] to [C10], see Article 2.3) of
        # higher priority.

        # FIDE handbook: "4.2 Sorting the Upfloaters | 4.2.2"
        # Each possible upfloater receives a sequence number, according to their descending score and, when scores are
        # equal, to their ascending TPN.

        potential_upfloaters = sorted(self._bracket.lower_list, key=lambda p: (-p.points, p.number))

        for player in potential_upfloaters:
            # Stop immediately, if there are no more exchanges to be made.
            if upfloaters == 0:
                break

            was_upfloater = self._has_resident_match(player)

            # If the player is not currently matched to a resident, incentivize pairings with residents, by adding 1 to
            # each edge weight between them. This will force pairing with residents, if this is possible while still
            # satisfying all quality criteria as well as before this modification.
            if not was_upfloater:
                self._bracket_matcher.add_to_weights(player, self._bracket.resident_list, 1)
                self._bracket_matcher.update_matching()

                # Remove the performed modification, as to not interfere with future iterations.
                self._bracket_matcher.add_to_weights(player, self._bracket.resident_list, -1)

            # If the player is now matched to a resident, finalize the fact that it will be to a resdient by removing
            # all edge weights with non-residents.
            if self._has_resident_match(player):
                upfloaters -= 1
                self._bracket_matcher.remove_weights(player, potential_upfloaters)

        # Finalize the players to be paired in this bracket.
        player_list = self._bracket.resident_list
        player_list += [player for player in self._bracket.lower_list if self._has_resident_match(player)]

        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.3"
        # The players of the bracket are divided in two subgroups:
        # 1. G1: This subgroup initially contains the players who have a colour preference for White, unless all the
        #        players in the bracket have yet to play a game (like, for instance, in the first round). In the latter
        #        case, this subgroup contains the first half of the players of the bracket (according to their TPN).
        # 2. G2: This subgroup initially contains the remaining players of the bracket.

        if self._bracket.is_first_round:
            self._g1 = player_list[: len(player_list) // 2]
        else:
            self._g1 = [player for player in player_list if player.color_preference.side == ColorPreferenceSide.WHITE]
        self._g2 = [player for player in player_list if player not in self._g1]

    def perform_g1_g2_recomposition(self) -> None:
        """Perform the recomposition of G1 and G2."""
        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.4 G1/G2 re-composition"
        # 1. If players from the smaller subgroup (or from G1, if their sizes are equal) must unavoidably be paired
        #    together, a number of players equal to the number of such pairs must be shifted from that subgroup into the
        #    other one. Find the best set of such players and proceed with the shift.
        # 2. Now, if the number of players in (the possibly new) G1 is different from the number of players in (the
        #    possibly new) G2, in order to equalise the size of the two subgroups, extract the best set of players from
        #    the larger subgroup, and shift those players into the smaller subgroup.
        # Note: Best, in both instances, means the first set of players (first in the order given by Article 4.3) that
        # can yield a legal pairing that complies at best with [C7] (see Article 2.3.3).

        original_g1 = self._g1.copy()
        original_g2 = self._g2.copy()

        # Incentivize pairings between G1 and G2
        for player in original_g1:
            self._bracket_matcher.add_to_weights(player, original_g2, 2)
        self._bracket_matcher.update_matching()

        # FIDE handbook: "4.3 Sorting the Shifters | 4.3.2"
        # White seekers are sorted in order of ascending ARO or, when AROs are equal, ascending TPN. Black seekers are
        # sorted according to their ascending TPN.

        self._g1.sort(key=lambda p: (p.aro, p.number))
        self._g2.sort(key=lambda p: p.number)

        # Shift from the smaller subgroup to the larger subgroup.
        if len(self._g1) <= len(self._g2):
            self._shift_from_g1_to_g2()
        else:
            self._shift_from_g2_to_g1()

        self._g1.sort(key=lambda p: (p.aro, p.number))
        self._g2.sort(key=lambda p: p.number)

        # Shift from the larger subgroup to the smaller subgroup.
        if len(self._g1) <= len(self._g2):
            self._shift_from_g2_to_g1()
        else:
            self._shift_from_g1_to_g2()

        # Remove the earlier given incentive again
        for player in original_g1:
            self._bracket_matcher.add_to_weights(player, original_g2, -2)

    def transpose_g2(self) -> None:
        """Choose T2 i.e. determine the order of G2."""
        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.5"
        # Sort the players in (the possibly new) G1 in order of ascending ARO or, when AROs are equal, according to
        # their ascending TPN. S1 is the subgroup resulting from such sorting.
        # Note: The sorting of G2 players is described in Article 4.3.

        # FIDE handbook: "4.4 Sorting G2 Players (Transpositions) | 4.4.2"
        # The players in the G2 pool are assigned sequence numbers according to their ascending TPN. The sorted sets of
        # G2 players are also called Transpositions.
        # Note: If, for instance, players A, B, C (listed according to their ascending TPN) are in G2, the different
        # Transpositions are {A, B, C} {A, C, B} {B, A, C} {B, C, A} {C, A, B} and {C, B, A}, in that exact order.

        self._g1.sort(key=lambda p: (p.aro, p.number))
        self._g2.sort(key=lambda p: p.number)

        # FIDE handbook: "3.2 Pairing Process for a Bracket | 3.2.5"
        # Choose T2, which is the first such transposition of G2 players (transpositions are sorted by Article 4.4) that
        # can yield a legal pairing, according to the following generation rule: the first player of S1 is paired with
        # the first player of T2, the second player of S1 with the second player of T2, and so on.

        for player in self._g1:
            # Incentivize the player in G1 being paired with the players in G2 in order. Pairing with the first player
            # in G2 is incentivized the most, while pairing with the last is incentivized the least. This ensures that
            # the player in G1 is paired with the player in G2 that has the highest position in the list out of all
            # possible choices.
            self._bracket_matcher.add_to_weights(player, self._g2[::-1], 0, increment=True)
            self._bracket_matcher.update_matching()

            match = self._bracket_matcher.matching[player]

            # Finalize the pairing of the player in G1 and the chosen player in G2 so that it does not get overwritten
            # in the future. This ensures that players in G1 with lower index take precedence.
            self._bracket_matcher.finalize_match(player, match)

    def get_player_pairs(self) -> list[tuple[Player, Player]]:
        """
        Return the chosen pairings as a list of tuples.

        For each item the first player in each tuple is to receive the white pieces and the second player the black
        pieces in adherence to the color criteria. A possibly unpaired player is denoted by a tuple of that player with
        themselves.
        """
        player_pairs = []

        for player_1, player_2 in self._bracket_matcher.matching.items():
            # Ignore pairings with no residents.
            if player_1.role == PlayerRole.LOWER and player_2.role == PlayerRole.LOWER:
                continue
            # Avoid counting each pair twice.
            if player_1 > player_2:
                player_pairs.append(self._get_player_pair(player_1, player_2, self._initial_color))

        return player_pairs
