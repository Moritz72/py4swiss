import random

from py4swiss.engines.common import Pairing
from py4swiss.trf import ParsedTrf
from py4swiss.trf.codes import PlayerCode
from py4swiss.trf.results import ColorToken, ResultToken, RoundResult
from py4swiss.trf.sections import PlayerSection, XSection
from py4swiss.trf.sections.x_section import XSectionConfiguration


def get_trf(number_of_players: int, number_of_rounds: int) -> ParsedTrf:
    player_sections = [
        PlayerSection(code=PlayerCode.PLAYER, starting_number=i, name=f"Player {i}", points_times_ten=0, rank=i)
        for i in range(1, number_of_players + 1)
    ]
    x_section = XSection(number_of_rounds=number_of_rounds, configuration=XSectionConfiguration(first_round_color=True))
    return ParsedTrf(player_sections=player_sections, x_section=x_section)


def add_random_result(trf: ParsedTrf, pairing: Pairing) -> None:
    players = trf.player_sections
    score_system = trf.x_section.score_point_system
    player_white = players[pairing.white - 1]
    player_black = players[max(0, pairing.black - 1)]

    assert player_white.points_times_ten is not None
    assert player_black.points_times_ten is not None

    if pairing.black == 0:
        result = RoundResult(id=0, color=ColorToken.BYE_OR_NOT_PAIRED, result=ResultToken.PAIRING_ALLOCATED_BYE)
        player_white.results.append(result)
        player_white.points_times_ten += score_system.get_points_times_ten(result)

    else:
        match random.randint(0, 2):
            case 0:
                result_white = RoundResult(id=pairing.black, color=ColorToken.WHITE, result=ResultToken.WIN)
                result_black = RoundResult(id=pairing.white, color=ColorToken.BLACK, result=ResultToken.LOSS)
            case 1:
                result_white = RoundResult(id=pairing.black, color=ColorToken.WHITE, result=ResultToken.DRAW)
                result_black = RoundResult(id=pairing.white, color=ColorToken.BLACK, result=ResultToken.DRAW)
            case _:
                result_white = RoundResult(id=pairing.black, color=ColorToken.WHITE, result=ResultToken.LOSS)
                result_black = RoundResult(id=pairing.white, color=ColorToken.BLACK, result=ResultToken.WIN)

        player_white.results.append(result_white)
        player_black.results.append(result_black)
        player_white.points_times_ten += score_system.get_points_times_ten(result_white)
        player_black.points_times_ten += score_system.get_points_times_ten(result_black)

    sorted_players = sorted(players, key=lambda p: p.points_times_ten or 0, reverse=True)
    for player in players:
        player.rank = sorted_players.index(player) + 1
