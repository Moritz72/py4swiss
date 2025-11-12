from __future__ import annotations

from enum import Enum
from functools import total_ordering
from typing import TYPE_CHECKING

from pydantic import BaseModel

from py4swiss.engines.common import (
    ColorPreference,
    ColorPreferenceSide,
    ColorPreferenceStrength,
    Float,
)
from py4swiss.trf.results import ColorToken, ResultToken

if TYPE_CHECKING:
    from py4swiss.trf.parsed_trf import ParsedTrf
    from py4swiss.trf.sections import PlayerSection, XSection


class PlayerRole(int, Enum):
    """The role of a player in a bracket."""

    MDP = 2
    RESIDENT = 1
    LOWER = 0


@total_ordering
class Player(BaseModel):
    """
    A collection of all player related information relevant for pairing.

    Attributes:
        id (int): The starting number of the player acting as a unique identifier
        number (int): The starting number of the player for pairing purposes
        points (int): The current points of the player multiplied by ten
        points_with_acceleration (int): The current points of the player multiplied by ten (including acceleration)
        color_preference (ColorPreference): The color preference of the player
        color_difference (int): The number of played white games of the player minus the number of played black games
        color_double (bool): Whether the previous two played rounds of the player were played with the same color
        float_1 (Float): The float of the player from one round before
        float_2 (Float): The float of the player from two rounds before
        opponents (set[int]): The IDs of the players against which the player already has a played game against
        colors (list[bool): A list of whether the player had the white pieces or not in their played games
        bye_received (bool): Whether the player already had a bye or forfeit win
        top_scorer (bool): Whether the player is a topscorer
        role: (PlayerRole): The role of the player in the current bracket (bracket context only)
    """

    id: int
    number: int
    points: int
    points_with_acceleration: int
    color_preference: ColorPreference
    color_difference: int
    color_double: bool
    float_1: Float
    float_2: Float
    opponents: set[int]
    colors: list[bool]
    bye_received: bool
    top_scorer: bool

    role: PlayerRole = PlayerRole.RESIDENT

    def __lt__(self, other: Player) -> bool:
        """Check whether the latter player ranks higher than the former one."""
        # FIDE handbook: "A.2 Order"
        # For pairings purposes only, the players are ranked in order of, respectively
        # a. score
        # b. pairing numbers assigned to the players accordingly to the initial ranking list and subsequent
        #    modifications depending on possible late entries or rating adjustments
        return (self.points_with_acceleration, -self.number) < (other.points_with_acceleration, -other.number)

    def __le__(self, other: Player) -> bool:
        """Check whether the latter player is ranked higher or identical to the former one."""
        return self == other or self < other

    def __eq__(self, other: object) -> bool:
        """Check whether the given players have the same ID."""
        if not isinstance(other, Player):  # pragma: no cover
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Return the hash of the ID."""
        return hash(self.id)


def _get_points_list(section: PlayerSection, x_section: XSection) -> list[int]:
    """Return a list of points of the given player after each round (including acceleration)."""
    round_results = section.results
    accelerations = x_section.accelerations.get(section.starting_number, [])
    accelerations += (len(round_results) - len(accelerations) + 1) * [0]

    points_list = []
    current_points = 0

    for result, acceleration in zip(round_results, accelerations, strict=False):
        points_list.append(current_points + acceleration)
        current_points += x_section.scoring_point_system.get_points_times_ten(result)
    points_list.append(current_points + accelerations[len(round_results)])

    return points_list


def _get_color_preference(section: PlayerSection) -> tuple[ColorPreference, int, bool]:
    """Return the color preference and color difference of the given player."""
    colors = [round_result.color for round_result in section.results if round_result.result.is_played()]

    # FIDE handbook: "A.6 Colour differences and colour preferences"
    # The colour difference of a player is the number of games played with white minus the number of games played with
    # black by this player.
    # The colour preference is the colour that a player should ideally receive for the next game.
    # It can be determined for each player who has played at least one game.
    # a. An absolute colour preference occurs when a player’s colour difference is greater than +1 or less than -1, or
    #    when a player had the same colour in the two latest rounds he played. The preference is white when the colour
    #    difference is less than -1 or when the last two games were played with black. The preference is black when the
    #    colour difference is greater than +1, or when the last two games were played with white.
    # b. A strong colour preference occurs when a player‘s colour difference is +1 (preference for black) or -1
    #    (preference for white).
    # c. A mild colour preference occurs when a player’s colour difference is zero, the preference being to alternate
    #    the colour with respect to the previous game he played.
    # d. Players who did not play any games have no colour preference (the preference of their opponents is granted).

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


def _get_floats(section: PlayerSection, round_number: int, points_list_dict: dict[int, list[int]]) -> Float:
    """Return the float of the given player in the round with the given number."""
    if round_number < 0:
        return Float.NONE

    # FIDE handbook: "A.4 Floaters and floats"
    # a. A downfloater is a player who remains unpaired in a bracket, and is thus moved to the next bracket. In the
    #    destination bracket, such players are called "moved-down players" (MDPs for short).
    # b. After two players with different scores have played each other in a round, the higher ranked player receives a
    #    downfloat, the lower one an upfloat.
    #    A player who, for whatever reason, does not play in a round, also receives a downfloat.

    player_point_list = points_list_dict[section.starting_number]
    round_result = section.results[round_number]

    if not round_result.result.is_played():
        return Float.DOWN

    opponent_point_list = points_list_dict[round_result.id]
    player_points = player_point_list[round_number]
    opponent_points = opponent_point_list[round_number]

    if player_points > opponent_points:
        return Float.DOWN
    if player_points < opponent_points:
        return Float.UP
    return Float.NONE


def get_player_infos_from_trf(trf: ParsedTrf) -> list[Player]:
    """Return a list of all player related information relevant for pairing."""
    players = []
    sections = trf.player_sections
    points_list_dict = {section.starting_number: _get_points_list(section, trf.x_section) for section in sections}

    round_number = min(len(player.results) for player in sections)
    max_score = max(trf.x_section.scoring_point_system.score_dict.values()) * round_number
    last_round = round_number == trf.x_section.number_of_rounds - 1
    sections = [player for player in sections if len(player.results) == round_number]
    sections = [player for player in sections if player.starting_number not in trf.x_section.zeroed_ids]

    for i, section in enumerate(sections):
        number = i + 1 if trf.x_section.configuration.by_rank else section.starting_number

        color_preference, color_difference, color_double = _get_color_preference(section)
        float_1 = _get_floats(section, round_number - 1, points_list_dict)
        float_2 = _get_floats(section, round_number - 2, points_list_dict)

        white = ColorToken.WHITE
        opponents = {round_result.id for round_result in section.results if round_result.result.is_played()}
        colors = [round_result.color == white for round_result in section.results if round_result.result.is_played()]
        results = {round_result.result for round_result in section.results}

        pairing_allocated_bye = ResultToken.PAIRING_ALLOCATED_BYE in results
        forfeit_win = ResultToken.FORFEIT_WIN in results
        bye_received = pairing_allocated_bye or forfeit_win

        # FIDE handbook: "A.7 Topscorers"
        # Topscorers are players who have a score of over 50% of the maximum possible score when pairing the final round
        # of the tournament.
        top_scorer = last_round and (points_list_dict[section.starting_number][-1] > max_score / 2)

        player = Player(
            id=section.starting_number,
            number=number,
            points=section.points_times_ten,
            points_with_acceleration=points_list_dict[section.starting_number][-1],
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
