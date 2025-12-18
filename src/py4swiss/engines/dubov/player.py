from __future__ import annotations

from enum import Enum
from functools import total_ordering
from typing import TYPE_CHECKING

from pydantic import BaseModel

from py4swiss.engines.common import (
    ColorPreference,
    ColorPreferenceSide,
    ColorPreferenceStrength,
)
from py4swiss.trf.results import ColorToken, ResultToken

if TYPE_CHECKING:
    from py4swiss.trf.parsed_trf import ParsedTrf
    from py4swiss.trf.sections import PlayerSection, XSection


class PlayerRole(int, Enum):
    """The role of a player in a bracket."""

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
        upfloat (int): The number of times the player has been upfloated
        previous_upfloat (bool): Whether the player was upfloated in the previous round
        is_maximum_upfloater (bool): Whether the player is a maximum upfloater
        aro (int): The average rating of the opponents of the player
        opponents (set[int]): The IDs of the players against which the player already has a played game against
        colors (list[bool): A list of whether the player had the white pieces or not in their played games
        bye_received (bool): Whether the player already had a bye or forfeit win
        role: (PlayerRole): The role of the player in the current bracket (bracket context only)

    """

    id: int
    number: int
    points: int
    points_with_acceleration: int
    color_preference: ColorPreference
    upfloats: int
    previous_upfloat: bool
    is_maximum_upfloater: bool
    aro: int
    opponents: set[int]
    colors: list[bool]
    bye_received: bool

    role: PlayerRole = PlayerRole.RESIDENT

    def __lt__(self, other: Player) -> bool:
        """Check whether the latter player ranks higher than the former one."""
        # FIDE handbook: "A.2 Order"
        # For pairings purposes only, the players are ranked in order of, respectively
        # a. score
        # b. pairing numbers assigned to the players accordingly to the initial ranking list and subsequent
        #    modifications depending on possible late entries or rating adjustments
        return (self.points_with_acceleration, -self.number) < (other.points_with_acceleration, -other.number)

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


def _get_color_preference(section: PlayerSection) -> ColorPreference:
    """Return the color preference of the given player."""
    colors = [round_result.color for round_result in section.results if round_result.result.is_played()]

    # FIDE handbook: "1.6 Colour differences and colour preferences"
    # The colour preference (also called: due colour) is the colour that a player should ideally receive for the next
    # game.
    # 1.6.1 An absolute colour preference occurs when a player's colour difference is greater than +1 or less than -1,
    #       or when a player had the same colour in the two latest rounds they played. The preference is for White when
    #       the colour difference is less than -1 or when the last two games were played with Black. The preference is
    #       for Black when the colour difference is greater than +1, or when the last two games were played with White.
    # 1.6.2 A strong colour preference occurs when a player's colour difference is +1 (preference for Black) or -1
    #       (preference for White).
    # 1.6.3 A mild colour preference occurs when a player's colour difference is zero, the preference being to alternate
    #       the colour with respect to the previous game they played.
    # 1.6.4 Players who did not play any games are considered to have a mild colour preference for Black.

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
        return ColorPreference(side=side, strength=ColorPreferenceStrength.ABSOLUTE)
    if abs(difference) == 1:
        return ColorPreference(side=side, strength=ColorPreferenceStrength.STRONG)
    if side != ColorPreferenceSide.NONE:
        return ColorPreference(side=side, strength=ColorPreferenceStrength.MILD)
    return ColorPreference(side=ColorPreferenceSide.BLACK, strength=ColorPreferenceStrength.MILD)


def _get_floats(section: PlayerSection, points_list_dict: dict[int, list[int]]) -> tuple[int, bool]:
    """Return the number of upfloats of the given player as well as whether they upfloated in the previous round."""
    upfloats = 0
    current_upfloat = False
    player_point_list = points_list_dict[section.starting_number]

    for i, round_result in enumerate(section.results):
        if not round_result.result.is_played():
            current_upfloat = False
            continue

        opponent_point_list = points_list_dict[round_result.id]
        player_points = player_point_list[i]
        opponent_points = opponent_point_list[i]

        current_upfloat = opponent_points > player_points
        upfloats += int(current_upfloat)

    return upfloats, current_upfloat


def _get_aro(sections: list[PlayerSection]) -> dict[int, int]:
    """Return a map from starting number to the average rating of opponents (ARO) of all players."""
    rating_dict = {section.starting_number: section.fide_rating or 0 for section in sections}
    aro_dict = {}

    # FIDE handbook: "1.7 Average Rating of Opponents (ARO)"
    # 1.7.1 ARO is defined for each player who has played at least one game. It is given by the sum of the ratings of
    #       the opponents the player met over-the-board (i.e. only played games are used to compute ARO), divided by the
    #       number of such opponents, and rounded to the nearest integer number (the higher, if the division ends for
    #       0.5).
    # 1.7.2 ARO is computed for each player after each round as a basis for the pairings of the next round.
    # 1.7.3 If a player has yet to play a game, their ARO is zero.
    for section in sections:
        ratings = [rating_dict[round_result.id] for round_result in section.results if round_result.result.is_played()]
        aro_dict[section.starting_number] = int(sum(ratings) / max(len(ratings), 1) + 0.5)

    return aro_dict


def get_player_infos_from_trf(trf: ParsedTrf) -> list[Player]:
    """Return a list of all player related information relevant for pairing."""
    players = []
    sections = trf.player_sections
    points_list_dict = {section.starting_number: _get_points_list(section, trf.x_section) for section in sections}
    aro_dict = _get_aro(sections)

    # FIDE handbook: "1.8 Maximum Upfloater"
    # 1.8.1 A player is said to be a maximum upfloater when they have already been upfloated a maximum number of
    #       times (MaxT).
    # 1.8.2 MaxT is a parameter whose value depends on the number of rounds in the tournament (Rnds), and is
    #       computed with the following formula:
    #           MaxT = 2 + [Rnds/5]
    #       where [Rnds/5] means Rnds divided by 5 and rounded downwards.
    max_t = 2 + trf.x_section.number_of_rounds // 5

    round_number = min(len(player.results) for player in sections)
    sections = [player for player in sections if len(player.results) == round_number]
    sections = [player for player in sections if player.starting_number not in trf.x_section.zeroed_ids]

    for i, section in enumerate(sections):
        number = i + 1 if trf.x_section.configuration.by_rank else section.starting_number

        color_preference = _get_color_preference(section)
        upfloats, previous_upfloat = _get_floats(section, points_list_dict)
        is_maximum_upfloater = upfloats >= max_t

        white = ColorToken.WHITE
        opponents = {round_result.id for round_result in section.results if round_result.result.is_played()}
        colors = [round_result.color == white for round_result in section.results if round_result.result.is_played()]
        results = {round_result.result for round_result in section.results}

        pairing_allocated_bye = ResultToken.PAIRING_ALLOCATED_BYE in results
        forfeit_win = ResultToken.FORFEIT_WIN in results
        bye_received = pairing_allocated_bye or forfeit_win

        player = Player(
            id=section.starting_number,
            number=number,
            points=section.points_times_ten,
            points_with_acceleration=points_list_dict[section.starting_number][-1],
            color_preference=color_preference,
            upfloats=upfloats,
            previous_upfloat=previous_upfloat,
            is_maximum_upfloater=is_maximum_upfloater,
            aro=aro_dict[section.starting_number],
            opponents=opponents,
            colors=colors,
            bye_received=bye_received,
        )
        players.append(player)

    return players
