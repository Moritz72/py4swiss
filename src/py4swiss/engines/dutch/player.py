from __future__ import annotations

from enum import Enum
from functools import total_ordering

from pydantic import BaseModel

from py4swiss.engines.common import (
    ColorPreference,
    ColorPreferenceSide,
    ColorPreferenceStrength,
    Float,
)
from py4swiss.trf.parsed_trf import ParsedTrf
from py4swiss.trf.results.color_token import ColorToken
from py4swiss.trf.sections import PlayerSection, XSection


class PlayerRole(int, Enum):
    """The role of a player in a bracket."""

    MDP = 2
    RESIDENT = 1
    LOWER = 0


@total_ordering
class Player(BaseModel):
    """
    A collection of any player related information relevant for pairing.

    Attributes:
        number (int): Starting number
        points (int): Points multiplied by 10 (including acceleration)
        color_preference (ColorPreference): Color preference according to A.6
        color_difference (int): Number of white games minus number of black games
        color_double (bool): Whether the previous two rounds were player with the same color
        float_1 (Float): Float from one round before
        float_2 (Float): Float from two rounds before
        opponents (set[int]): Starting numbers of already encountered players
        colors (list[bool | None): Colors from all rounds (None for unplayed rounds)
        bye_received (bool): Whether there was already a bye or forfeit win
        top_scorer (bool): Whether this is a topscorer
        role: (PlayerRole): Role in the current bracket (bracket context only)
    """

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
        # "For pairings purposes only, the players are ranked in order of, respectively
        # a. score
        # b. pairing numbers assigned to the players accordingly to the initial ranking list and
        #    subsequent modifications depending on possible late entries or rating adjustments"
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
    """Get a list of points of the given player after each round (including acceleration)."""
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
    """Get the color preference and color difference of the given player."""
    colors = [result.color for result in player_section.results if result.color != ColorToken.BYE_OR_NOT_PAIRED]

    # "The colour difference of a player is the number of games played with white minus the number
    # of games played with black by this player.
    # The colour preference is the colour that a player should ideally receive for the next game.
    # It can be determined for each player who has played at least one game.
    # a. An absolute colour preference occurs when a player’s colour difference is greater than +1
    #    or less than -1, or when a player had the same colour in the two latest rounds he played.
    #    The preference is white when the colour difference is less than -1 or when the last two
    #    games were played with black. The preference is black when the colour difference is
    #    greater than +1, or when the last two games were played with white.
    # b. A strong colour preference occurs when a player‘s colour difference is +1 (preference for
    #    black) or -1 (preference for white).
    # c. A mild colour preference occurs when a player’s colour difference is zero, the preference
    #    being to alternate the colour with respect to the previous game he played.
    # d. Players who did not play any games have no colour preference (the preference of their
    #    opponents is granted)."

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
    """Get the float from one and two rounds before for the given player."""
    if round_number < 0:
        return Float.NONE

    assert player_section.starting_number is not None
    player = player_section.starting_number

    # FIDE handbook: "A.4 Floaters and floats"
    # a. A downfloater is a player who remains unpaired in a bracket, and is thus moved to the next
    #    bracket. In the destination bracket, such players are called "moved-down players" (MDPs
    #    for short).
    # b. After two players with different scores have played each other in a round, the higher
    #    ranked player receives a downfloat, the lower one an upfloat.
    #    A player who, for whatever reason, does not play in a round, also receives a downfloat.

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
    """Get all information relevant for pairing of all players."""
    players = []
    sections = trf.player_sections
    points_list_dict = {
        player.starting_number: _get_points_list(player, trf.x_section)
        for player in sections
        if player.starting_number is not None
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

        # FIDE handbook: "A.7 Topscorers"
        # Topscorers are players who have a score of over 50% of the maximum possible score when
        # pairing the final round of the tournament.
        top_scorer = last_round and (points_list_dict[player_section.starting_number][-1] > max_score / 2)

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
            top_scorer=top_scorer,
        )
        players.append(player)

    return players
