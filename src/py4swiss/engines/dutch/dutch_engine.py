from itertools import groupby

from py4swiss.engines.common import Pairing, PairingEngine, PairingException
from py4swiss.engines.dutch.bracket_matcher import BracketMatcher
from py4swiss.engines.dutch.player_info import PlayerInfo, PlayerRole, get_player_infos_from_trf
from py4swiss.engines.dutch.validity_matcher import ValidityMatcher
from py4swiss.trf import ParsedTrf


class DutchEngine(PairingEngine):
    @classmethod
    def _get_bracket_pairing(
            cls,
            mdp_list: list[PlayerInfo],
            resident_list: list[PlayerInfo],
            low_resident_list: list[PlayerInfo],
            round_number: int,
            is_penultimate_pairing_bracket: bool,
            is_last_pairing_bracket: bool,
            validity_matcher: ValidityMatcher
    ) -> list[Pairing] | None:
        bracket_matcher = BracketMatcher(
            mdp_list,
            resident_list,
            low_resident_list,
            round_number,
            is_penultimate_pairing_bracket,
            is_last_pairing_bracket,
            validity_matcher
        )
        bracket_matcher.calculate_base_matching()
        bracket_matcher.finalize_mdp_matches()
        bracket_matcher.finalize_resident_matches()
        if not bracket_matcher.check_completion_criterium():
            return None
        return bracket_matcher.get_pairings()

    @classmethod
    def generate_pairings(cls, trf: ParsedTrf) -> list[Pairing]:
        pairings = []
        round_number = min(len(section.results) for section in trf.player_sections) + 1

        players = get_player_infos_from_trf(trf)
        players.sort(reverse=True)

        validity_matcher = ValidityMatcher(players)
        if not validity_matcher.is_valid_matching():
            raise PairingException("Round can not be paired.")

        score_brackets = [list(group) for score, group in groupby(players, key=lambda p: p.points)]
        mdp_list: list[PlayerInfo] = []
        is_penultimate_pairing_bracket = False

        i = 0
        while i < len(score_brackets):
            resident_list = score_brackets[i]
            if i + 1 < len(score_brackets):
                lower_resident_list = score_brackets[i + 1]
            else:
                lower_resident_list = []

            for mdp in mdp_list:
                mdp.role = PlayerRole.MDP
            for resident in resident_list:
                resident.role = PlayerRole.RESIDENT
            for lower in lower_resident_list:
                lower.role = PlayerRole.LOWER

            bracket_pairings = cls._get_bracket_pairing(
                mdp_list,
                resident_list,
                lower_resident_list,
                round_number,
                is_penultimate_pairing_bracket,
                i == len(score_brackets) - 1,
                validity_matcher
            )

            if bracket_pairings is None:
                is_penultimate_pairing_bracket = True
                collapsed_last_bracket = [player for bracket in score_brackets[i + 1:] for player in bracket]
                score_brackets = score_brackets[:i + 1] + [collapsed_last_bracket]
                continue

            paired = {pairing.white for pairing in bracket_pairings} | {pairing.black for pairing in bracket_pairings}
            mdp_list = [player for player in mdp_list + resident_list if player.number not in paired]

            pairings.extend(bracket_pairings)
            i += 1

        player_dict = {player.number: player for player in players}
        pairings.sort(
            key=lambda p: (
                max(player_dict[p.white].points, player_dict[p.black].points),
                min(player_dict[p.white].points, player_dict[p.black].points)
            ) if p.white != 0 and p.black != 0 else (0, 0),
            reverse=True
        )

        return pairings
