from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dutch.bracket.bracket import Bracket
from py4swiss.engines.dutch.bracket.bracket_matcher import BracketMatcher
from py4swiss.engines.dutch.criteria import COLOR_CRITERIA
from py4swiss.engines.dutch.player import Player, PlayerRole
from py4swiss.engines.dutch.validity_matcher import ValidityMatcher


class BracketPairer:
    """
    A class used to perform the pairing process for a bracket.

    This process is as follows:
        - Determine the composition of S1 in the heterogeneous bracket and Limbo
        - Determine the order of S2 in the heterogeneous bracket
        - Determine the number of exchanges between S1 and S2 in the homogeneous bracket
        - Determine the exchanges from S1 to S2 in the homogeneous bracket
        - Determine the exchanges from S2 to S1 in the homogeneous bracket
        - Perform the exchanges between S1 and S2 in the homogeneous bracket
        - Determine the order of S2 in the homogeneous bracket
        - Check whether the chosen set of downfloaters allows for completion of the round pairing
        - If completion is possible, retrieve the chosen pairings after determining colors
    """

    def __init__(self, state: Bracket, validity_matcher: ValidityMatcher, initial_color: bool) -> None:
        """Initialize a new bracket matcher along with the heterogeneous and homogeneous brackets."""
        self._bracket: Bracket = state
        self._validity_matcher: ValidityMatcher = validity_matcher
        self._initial_color: bool = initial_color

        self._num: int = len(self._bracket.mdp_list + self._bracket.resident_list + self._bracket.lower_list)
        self._bracket_matcher: BracketMatcher = BracketMatcher(self._bracket, self._validity_matcher)

        self._heterogeneous_s1: list[Player] = []
        self._heterogeneous_s2: list[Player] = []
        self._homogeneous_s1: list[Player] = []
        self._homogeneous_s2: list[Player] = []
        self._exchanges: int = 0

    @staticmethod
    def _get_player_pair(player_1: Player, player_2: Player, initial_color: bool) -> tuple[Player, Player]:
        """
        Return a tuple of the given players.

        The first player in the tuple is to receive the white pieces and the second player the black pieces in adherence
        to the color criteria.
        """
        # Ignore unpaired players.
        if player_1 == player_2:
            return player_1, player_2

        i = 0
        player_1_color = ColorPreferenceSide.NONE

        # Evaluate the color criteria E.1 - E.5 in order until one is conclusive. Note that E.5 is always conclusive.
        while player_1_color == ColorPreferenceSide.NONE:
            player_1_color = COLOR_CRITERIA[i].evaluate(player_1, player_2)
            i += 1

        # The E.5 implementation assumes that the first seed gets the white pieces in the first round.
        if i == len(COLOR_CRITERIA) and not initial_color:
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

    def _in_s1(self, player: Player) -> bool:
        """Check whether the given player is currently considered to be in S1."""
        return player > self._bracket_matcher.matching[player] and self._get_match_role(player) == PlayerRole.RESIDENT

    def _in_s2(self, player: Player) -> bool:
        """Check whether the given player is currently considered to be in S2."""
        return player <= self._bracket_matcher.matching[player] or self._get_match_role(player) == PlayerRole.LOWER

    def determine_heterogeneous_s1(self) -> None:
        """Determine the composition of S1 in the heterogeneous bracket."""
        # Since the quality criteria are already taken into account by the bracket matcher, only the transpositions need
        # to be accounted for, specifically the exchanges from S1 to Limbo (D.3).

        # FIDE handbook: "D.3 Exchanges in heterogeneous brackets (original S1 ↔ original Limbo)"
        # An exchange in a heterogeneous bracket (also called a MDP-exchange) is a swap of two equally sized groups of
        # BSN(s) (all representing MDP(s)) between the original S1 and the original Limbo.
        # In order to sort all the possible MDP-exchanges, apply the following comparison rules between two
        # MDP-exchanges in the specified order (i.e. if a rule does not discriminate between two exchanges, move to the
        # next one) to the players that are in the new S1 after the exchange.
        # The priority goes to the exchange that yields a S1 having:
        # a. the highest different score among the players represented by their BSN (this comes automatically in
        #    complying with the C.6 criterion, which says to minimize the PSD of a bracket).
        # b. the lowest lexicographic value of the BSN(s) (sorted in ascending order).

        # As also mentioned in the rules document, D.3.a is already taken care of by C.6, thus only D.3.b needs to be
        # considered.
        for mdp in self._bracket.mdp_list:
            # If the MDP is currently unpaired, incentivize pairing it by adding 1 to each edge weight between it and
            # each resident. This will force the MDP to be paired in the new matching, if this is possible while still
            # satisfying all quality criteria as well as before this modification.
            if not self._has_resident_match(mdp):
                self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list, 1)
                self._bracket_matcher.update_matching()

            # If the MDP is paired after the optional modification, finalize the fact that it is in S1 by further
            # incentivizing its pairings such that later modifications will not overwrite this choice. Since the list of
            # MDPs is ordered by BSN, this ensures that D.3.b is adhered to.
            if self._has_resident_match(mdp):
                self._heterogeneous_s1.append(mdp)
                self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list, self._num)

    def determine_heterogeneous_s2(self) -> None:
        """Determine the order of S2 in the heterogeneous bracket."""
        # Since the quality criteria are already taken into account by the bracket matcher, only the transpositions need
        # to be accounted for, specifically D.1.

        # FIDE handbook: "D.1 Transpositions in S2"
        # A transposition is a change in the order of the BSNs (all representing resident players) in S2.
        # All the possible transpositions are sorted depending on the lexicographic value of their first N1 BSN(s),
        # where N1 is the number of BSN(s) in S1 (the remaining BSN(s) of S2 are ignored in this context, because they
        # represent players bound to constitute the remainder in case of a heterogeneous bracket; or bound to downfloat
        # in case of a homogeneous bracket - e.g. in a 11-player homogeneous bracket, it is 6-7-8-9-10, 6-7-8-9-11,
        # 6-7-8-10-11, ..., 6-11-10-9-8, 7-6-8-9-10, ..., 11-10-9-8-7 (720 transpositions); if the bracket is
        # heterogeneous with two MDPs, it is: 3-4, 3-5, 3-6, ..., 3-11, 4-3, 4-5, ..., 11-10 (72 transpositions)).
        for mdp in self._heterogeneous_s1:
            # Incentivize the MDP being paired with the resident players. Pairing with the highest ranked resident is
            # incentivized the most, while pairing with the lowest is incentivized the least. This ensures that the MDP
            # is paired with the resident that has the lowest BSN out of all possible choices.
            self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list[::-1], 0, increment=True)
            self._bracket_matcher.update_matching()

            match = self._bracket_matcher.matching[mdp]
            self._heterogeneous_s2.append(match)

            # Finalize the pairing of the MDP and the chosen resident so that it does not get overwritten in the future.
            # This ensures that MDPs with lower BSN take precedence such that D.1 is fully adhered to.
            self._bracket_matcher.finalize_match(mdp, match)
            self._validity_matcher.finalize_match(mdp, match)

    def determine_homogeneous_exchanges(self) -> None:
        """Determine the necessary number of exchanges in the homogeneous bracket."""
        # This step is technically not necessary. It is possible to determine the composition of S1 in one step.
        # However, this requires to recompute the optimal pairings per resident, similar to the heterogeneous case. In
        # contrast, determining the number of exchanges can be done at the cost of only one recomputation and improve
        # the efficient of later steps. The number of exchanges is determined by D.2, specifically D.2.a.

        # FIDE handbook: "D.2 Exchanges in homogeneous brackets or remainders (original S1 ↔ original S2)"
        # An exchange in a homogeneous brackets (also called a resident-exchange) is a swap of two equally sized groups
        # of BSN(s) (all representing resident players) between the original S1 and the original S2.
        # In order to sort all the possible resident-exchanges, apply the following comparison rules between two
        # resident-exchanges in the specified order (i.e. if a rule does not discriminate between two exchanges, move to
        # the next one).
        # The priority goes to the exchange having:
        # a. the smallest number of exchanged BSN(s) (e.g exchanging just one BSN is better than exchanging two of
        #    them).
        # b. the smallest difference between the sum of the BSN(s) moved from the original S2 to S1 and the sum of the
        #    BSN(s) moved from the original S1 to S2 (e.g. in a bracket containing eleven players, exchanging 6 with 4
        #    is better than exchanging 8 with 5; similarly exchanging 8+6 with 4+3 is better than exchanging 9+8 with
        #    5+4; and so on).
        # c. the highest different BSN among those moved from the original S1 to S2 (e.g. moving 5 from S1 to S2 is
        #    better than moving 4; similarly, 5-2 is better than 4-3; 5-4-1 is better than 5-3-2; and so on).
        # d. the lowest different BSN among those moved from the original S2 to S1 (e.g. moving 6 from S2 to S1 is
        #    better than moving 7; similarly, 6-9 is better than 7-8; 6-7-10 is better than 6-8-9; and so on).

        # Determine how many pairs can be formed after excluding the previously paired heterogeneous bracket.
        paired_residents = set(self._heterogeneous_s2)
        remainder = [player for player in self._bracket.resident_list if player not in paired_residents]
        pairs = sum(self._has_resident_match(resident) for resident in remainder) // 2

        # Compose the original S1 and S2 based on the number of pairs.
        self._homogeneous_s1 = remainder[:pairs]
        self._homogeneous_s2 = remainder[pairs:]

        # Incentivize pairings according to D.2.a and D.2.b. D.2.b is not strictly necessary for determining the number
        # of exchanges, but since it would need to be done later on anyway, it is taken care of in this step already.
        for i, resident in enumerate(remainder):
            # Incentivize pairs containing players in S1. This will in sum maximize the number of pairs between S1 and
            # S2 and thus, minimize the number of exchanges taking care of D.2.a. For D.2.b, a pairing is
            # disincentivized by a value equal to the minimum BSN of the pair. Thus, in sum, minimizing the difference
            # between the sum of BSNs moved from S1 to S2 and the sum of BSNs moved from S2 to S1, since, when pairing
            # is completed, a player is in S1, if and only if they are paired with a resident with a higher BSN and the
            # number of exchanges is already fixed by D.2.a. Note that the sum of the additions to the weights needed
            # for D.2.b is always smaller than the square of the number of residents. Thus, a shift of twice the number
            # of bracket bits is sufficient to avoid interference with the additions for D.2.a.
            value = ((int(i < pairs) << (2 * self._bracket.bracket_bits)) - i) << 1
            self._bracket_matcher.add_to_weights(resident, remainder[i + 1 :], value)

        self._bracket_matcher.update_matching()
        self._exchanges = sum(self._in_s2(resident) for resident in self._homogeneous_s1)

    def determine_moves_from_s1_to_s2(self) -> None:
        """Determine the players to move from S1 to S2 in the homogeneous bracket."""
        # Since D.2.a and D.2.b are already accounted for, it is only necessary to determine the highest different BSN
        # among those moved from the original S1 to S2 (D.2.c). This step is performed in a similar fashion as the
        # choice of S1 in the heterogeneous case.
        exchanges = self._exchanges

        for i in range(len(self._homogeneous_s1) - 1, -1, -1):
            # Stop immediately, if there are no more exchanges to be made.
            if exchanges == 0:
                return

            resident = self._homogeneous_s1[i]
            lower_residents = self._homogeneous_s1[i + 1 :] + self._homogeneous_s2
            was_exchanged = self._in_s2(resident)

            # If the resident is currently in S2, disincentivize pairings that would keep the resident in S2, i.e. ones
            # with lower ranked residents, by subtracting 1 to each edge weight between them. This will force the
            # resident to be in S1, if this is possible while still satisfying all quality criteria as well as before
            # this modification.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, lower_residents, -1)
                self._bracket_matcher.update_matching()

            # If the resident remains in S2 even after the optional modification, finalize the fact that it will be
            # exchanged by removing all edge weights with lower ranked residents. Since the current S1 is ordered by
            # BSN, this ensures that D.2.c is adhered to.
            if self._in_s2(resident):
                exchanges -= 1
                self._bracket_matcher.remove_weights(resident, lower_residents)

            # Remove the performed modification, as to not interfere with future iterations.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, lower_residents, 1)

    def determine_moves_from_s2_to_s1(self) -> None:
        """Determine the players to move from S2 to S1 in the homogeneous bracket."""
        # Since D.2.a and D.2.b are already accounted for, it is only necessary to determine the lowest different BSN
        # among those moved from the original S2 to S1 (D.2.d). This step is performed in the exact same way as the
        # moves from S1 to S2.
        exchanges = self._exchanges

        for i, resident in enumerate(self._homogeneous_s2):
            # Stop immediately, if there are no more exchanges to be made.
            if exchanges == 0:
                return

            higher_residents = self._homogeneous_s1 + self._homogeneous_s2[:i]
            was_exchanged = self._in_s1(resident)

            # If the resident is currently in S1, incentivize pairings that would move the resident into S2, i.e. ones
            # with lower ranked residents, by subtracting 1 to each edge weight between them. This will force the
            # resident to be in S2, if this is possible while still satisfying all quality criteria as well as before
            # this modification.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, higher_residents, -1)
                self._bracket_matcher.update_matching()

            # If the resident remains in S1 even after the optional modification, finalize the fact that it will be
            # exchanged by removing all edge weights with higher ranked residents. Since the current S2 is ordered by
            # BSN, this ensures that D.2.d is adhered to.
            if not self._in_s2(resident):
                exchanges -= 1
                self._bracket_matcher.remove_weights(resident, higher_residents + self._bracket.lower_list)

            # Remove the performed modification, as to not interfere with future iterations.
            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, higher_residents, 1)

    def perform_homogeneous_exchanges(self) -> None:
        """Move players to S1 and S2 in the homogeneous bracket as previously determined."""
        homogeneous_bracket = self._homogeneous_s1 + self._homogeneous_s2

        self._homogeneous_s1 = [resident for resident in homogeneous_bracket if self._in_s1(resident)]
        self._homogeneous_s2 = [resident for resident in homogeneous_bracket if self._in_s2(resident)]

        # Finalize S1 by removing all edge weights with higher ranked residents.
        for i, resident in enumerate(self._homogeneous_s1):
            self._bracket_matcher.remove_weights(resident, self._homogeneous_s1[i + 1 :])

        # Finalize S2 by removing all edge weights with lower ranked residents.
        for i, resident in enumerate(self._homogeneous_s2):
            self._bracket_matcher.remove_weights(resident, self._homogeneous_s2[i + 1 :])

    def transpose_homogeneous_s2(self) -> None:
        """Determine the order of S2 in the heterogeneous bracket."""
        for resident in self._homogeneous_s1:
            # Incentivize the player in S1 being paired with the players in S2 in order. Pairing with the highest ranked
            # player in S2 is incentivized the most, while pairing with the lowest is incentivized the least. This
            # ensures that the player in S1 is paired with the player in S2 that has the lowest BSN out of all possible
            # choices.
            self._bracket_matcher.add_to_weights(resident, self._homogeneous_s2[::-1], 0, increment=True)
            self._bracket_matcher.update_matching()

            match = self._bracket_matcher.matching[resident]

            # Finalize the pairing of the player in S1 and the chosen player in S2 so that it does not get overwritten
            # in the future. This ensures that players in S1 with lower BSN take precedence such that D.1 is fully
            # adhered to.
            self._bracket_matcher.finalize_match(resident, match)
            self._validity_matcher.finalize_match(resident, match)

    def check_completion_criterium(self) -> bool:
        """Check whether it is possible to complete the round pairing with the chosen set of downfloaters."""
        # If the current bracket is the PPB or LPB, completion is guaranteed.
        if self._bracket.penultimate_pairing_bracket or self._bracket.last_pairing_bracket:
            return True
        return self._validity_matcher.is_valid_matching()

    def get_player_pairs(self) -> list[tuple[Player, Player]]:
        """
        Return the chosen pairings as a list of tuples.

        For each item the first player in each tuple is to receive the white pieces and the second player the black
        pieces in adherence to the color criteria. A possibly unpaired player is denoted by a tuple of that player with
        themselves.
        """
        player_pairs = []

        for player_1, player_2 in self._bracket_matcher.matching.items():
            # Ignore pairings with players from lower brackets.
            if PlayerRole.LOWER in (player_1.role, player_2.role):
                continue
            # Avoid counting each pair twice.
            if player_1 > player_2:
                player_pairs.append(self._get_player_pair(player_1, player_2, self._initial_color))
            # If the current bracket is the LPB, there might be one unpaired player left in the bracket. This player
            # will consequently receive the pairing-allocated bye.
            if player_1.number == player_2.number and self._bracket.last_pairing_bracket:
                player_pairs.append(self._get_player_pair(player_1, player_2, self._initial_color))

        return player_pairs
