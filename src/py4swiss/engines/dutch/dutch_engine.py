from py4swiss.engines.common import Pairing, PairingEngine, PairingError
from py4swiss.engines.dutch.bracket import BracketPairer, Brackets
from py4swiss.engines.dutch.player import Player, get_player_infos_from_trf
from py4swiss.engines.dutch.validity_matcher import ValidityMatcher
from py4swiss.trf import ParsedTrf


class DutchEngine(PairingEngine):
    """
    A pairing engine implementing the Dutch System according to the FIDE Handbook as of 2025, see "C.04.3 FIDE (Dutch)
    System (effective till 31 January 2026)".
    """

    @staticmethod
    def _get_player_pair_score(player_pair: tuple[Player, Player]) -> tuple[int, int, int]:
        """Return a score for a pair of players for purpose of sorting the round pairing."""
        player_1, player_2 = player_pair

        # FIDE handbook: "D. Pairing, colour and publishing rules" | 9.
        # After a pairing is complete, sort the pairs before publishing them.
        # The sorting criteria are (with descending priority)
        #
        # the score of the higher ranked player of the involved pair;
        # the sum of the scores of both players of the involved pair;
        # the rank according to the Initial Order (C.04.2.B) of the higher ranked player of the involved pair.

        # Note that for some reason, here, "score" and "ranked" uses the points without acceleration while in all other
        # cases, like the color criterion E.5, the points with acceleration are used. Or at least that is how
        # bbpPairings sees it.

        if player_1 == player_2:
            return -1, -1, -1
        if (player_2.points, -player_2.number) > (player_1.points, -player_1.number):
            player_1, player_2 = player_2, player_1

        return player_1.points, player_2.points, -player_1.number

    @staticmethod
    def _get_pairing(player_pair: tuple[Player, Player]) -> Pairing:
        """Return a pairing from a pair of players."""
        player_1, player_2 = player_pair

        # Players are denoted by their starting number, whilst the pairing-allocated bye is denoted by 0.
        if player_1 == player_2:
            return Pairing(white=player_1.id, black=0)
        return Pairing(white=player_1.id, black=player_2.id)

    @staticmethod
    def _get_bracket_pairs(bracket_pairer: BracketPairer) -> list[tuple[Player, Player]] | None:
        """Return the chosen players to be paired in the bracket."""
        bracket_pairer.determine_heterogeneous_s1()
        bracket_pairer.determine_heterogeneous_s2()

        bracket_pairer.determine_homogeneous_exchanges()
        bracket_pairer.determine_moves_from_s1_to_s2()
        bracket_pairer.determine_moves_from_s2_to_s1()
        bracket_pairer.perform_homogeneous_exchanges()
        bracket_pairer.transpose_homogeneous_s2()

        if not bracket_pairer.check_completion_criterium():
            return None
        return bracket_pairer.get_player_pairs()

    @classmethod
    def generate_pairings(cls, trf: ParsedTrf) -> list[Pairing]:
        """Return the round pairing of the next round for the given TRF."""
        player_pairs = []
        round_number = min(len(section.results) for section in trf.player_sections) + 1
        initial_color = trf.x_section.configuration.first_round_color

        players = get_player_infos_from_trf(trf)
        players.sort(reverse=True)

        validity_matcher = ValidityMatcher(players, trf.x_section.forbidden_pairs)
        brackets = Brackets(players, round_number)

        # Check whether pairing the next round is possible.
        if not validity_matcher.is_valid_matching():
            raise PairingError("Round can not be paired.")

        # Determine bracket pairings and save the results until there are none left.
        while not brackets.is_finished():
            bracket_state = brackets.get_current_bracket()
            bracket_pairer = BracketPairer(bracket_state, validity_matcher, initial_color)
            bracket_pairings = cls._get_bracket_pairs(bracket_pairer)

            if bracket_pairings is None:
                brackets.collapse()
            else:
                brackets.apply_bracket_pairings(bracket_pairings)
                player_pairs.extend(bracket_pairings)

        # Determine the round pairing from the bracket pairings with the correct order.
        player_pairs.sort(key=lambda player_pair: cls._get_player_pair_score(player_pair), reverse=True)
        pairings = [cls._get_pairing(player_pair) for player_pair in player_pairs]

        return pairings
