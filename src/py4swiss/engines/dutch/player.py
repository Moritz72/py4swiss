from __future__ import annotations

from enum import Enum
from functools import total_ordering

from pydantic import BaseModel

from py4swiss.engines.common import ColorPreference, ColorPreferenceSide, ColorPreferenceStrength, Float
from py4swiss.trf.parsed_trf import ParsedTrf
from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.sections import PlayerSection, XSection


class PlayerRole(int, Enum):
    MDP = 2
    RESIDENT = 1
    LOWER = 0


@total_ordering
class Player(BaseModel):
    number: int
    points: int
    color_preference: ColorPreference
    color_difference: int
    color_double: bool
    float_1: Float
    float_2: Float
    opponents: set[int]
    colors: list[bool | None]
    bye_received: bool
    top_scorer: bool

    role: PlayerRole = PlayerRole.RESIDENT

    def __lt__(self, other: Player) -> bool:
        return (self.points, -self.number) < (other.points, -other.number)

    def __le__(self, other: Player) -> bool:
        return (self.points, -self.number) <= (other.points, -other.number)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return (self.points, -self.number) == (other.points, -other.number)

    def __hash__(self) -> int:
        return self.number


def _get_points_list(player_section: PlayerSection, x_section: XSection) -> list[int]:
    assert player_section.starting_number is not None

    results = player_section.results
    accelerations = x_section.accelerations.get(player_section.starting_number, [])
    accelerations += (len(results) - len(accelerations) + 1) * [0]

    points_list = []
    current_points = 0

    for result, acceleration in zip(results, accelerations[:-1]):
        points_list.append(current_points + acceleration)
        current_points += x_section.score_point_system.get_points_times_ten(result)
    points_list.append(current_points + accelerations[-1])

    return points_list


def _get_color_preference(player_section: PlayerSection) -> tuple[ColorPreference, int, bool]:
    colors = [result.color for result in player_section.results if result.color != ColorToken.BYE_OR_NOT_PAIRED]

    whites = colors.count(ColorToken.WHITE)
    blacks = colors.count(ColorToken.BLACK)
    difference = whites - blacks
    double = len(colors) > 1 and len(set(colors[-2:])) == 1

    if difference > 0:
        side = ColorPreferenceSide.BLACK
    elif difference < 0:
        side = ColorPreferenceSide.WHITE
    elif bool(colors):
        side = ColorPreferenceSide.WHITE if colors[-1] == ColorToken.BLACK else ColorPreferenceSide.BLACK
    else:
        side = ColorPreferenceSide.NONE

    if abs(difference) > 1 or double:
        return ColorPreference(side=side, strength=ColorPreferenceStrength.ABSOLUTE), difference, double
    if abs(difference) == 1:
        return ColorPreference(side=side, strength=ColorPreferenceStrength.STRONG), difference, double
    if side != ColorPreferenceSide.NONE:
        return ColorPreference(side=side, strength=ColorPreferenceStrength.MILD), difference, double
    return ColorPreference(side=side, strength=ColorPreferenceStrength.NONE), difference, double


def _get_floats(player_section: PlayerSection, round_number: int, points_list_dict: dict[int, list[int]]) -> Float:
    if round_number < 0:
        return Float.NONE

    assert player_section.starting_number is not None
    player = player_section.starting_number

    player_point_list = points_list_dict[player]
    if len(player_point_list) < round_number:
        return Float.NONE

    opponent = player_section.results[round_number].id
    if opponent == 0:
        return Float.DOWN

    opponent_point_list = points_list_dict[opponent]
    player_points = player_point_list[round_number]
    opponent_points = opponent_point_list[round_number]

    if player_points > opponent_points:
        return Float.DOWN
    if player_points < opponent_points:
        return Float.UP
    return Float.NONE


def get_player_infos_from_trf(trf: ParsedTrf) -> list[Player]:
    players = []
    sections = trf.player_sections
    points_list_dict = {
        player.starting_number: _get_points_list(player, trf.x_section)
        for player in sections if player.starting_number is not None
    }

    round_number = min(len(player.results) for player in sections)
    max_score = trf.x_section.score_point_system.get_max() * round_number
    last_round = round_number == (trf.x_section.number_of_rounds or 0) - 1
    sections = [player for player in sections if len(player.results) == round_number]
    sections = [player for player in sections if player.starting_number not in trf.x_section.zeroed_ids]

    for player_section in sections:
        assert player_section.starting_number is not None

        color_preference, color_difference, color_double = _get_color_preference(player_section)
        float_1 = _get_floats(player_section, round_number - 1, points_list_dict)
        float_2 = _get_floats(player_section, round_number - 2, points_list_dict)

        opponents = {result.id for result in player_section.results}
        colors = [result.color.to_bool() for result in player_section.results]
        bye_received = 0 in opponents
        opponents.discard(0)

        player = Player(
            number=player_section.starting_number,
            points=points_list_dict[player_section.starting_number][-1],
            color_preference=color_preference,
            color_difference=color_difference,
            color_double=color_double,
            float_1=float_1,
            float_2=float_2,
            opponents=opponents,
            colors=colors,
            bye_received=bye_received,
            top_scorer=last_round and (points_list_dict[player_section.starting_number][-1] > max_score / 2)
        )
        players.append(player)

    return players
