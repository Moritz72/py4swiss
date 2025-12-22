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
    from py4swiss.trf.results import ScoringPointSystem
    from py4swiss.trf.sections import PlayerSection


class PlayerRole(int, Enum):
    """The role of a player in a bracket."""

    RESIDENT = 2
    LOWER = 1
    NONE = 0


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
        buchholz (int): Sum of the scores of the opponents the player met
        sonneborn_berger (int): Sum of the scores of the opponents the player met times the points scored against them
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
    buchholz: int
    sonneborn_berger: int
    opponents: set[int]
    colors: list[bool]
    bye_received: bool

    role: PlayerRole = PlayerRole.RESIDENT

    def __lt__(self, other: Player) -> bool:
        """Check whether the latter player ranks higher than the former one."""
        # FIDE handbook: "1.8 Ranking Order"
        # After the seeding rounds (see Article 1.6), for pairings purposes only, the players in a bracket are ranked in
        # order of, respectively:
        # 1.8.1 (Opposition Evaluation) Index, which is a sequence of the methods seen in Article 1.7.1, to be applied
        #       in the following order (any subsequent method is used when preceding method(s) yield equal values):
        #           1. Buchholz (see Article 1.7.1.1)
        #           2. Sonneborn-Berger (see Article 1.7.1.2)
        # 1.8.2 TPN, in ascending order (see Article 1.1)
        own_score = (self.buchholz, self.sonneborn_berger, -self.number)
        other_score = (other.buchholz, other.sonneborn_berger, -other.number)

        return own_score < other_score

    def __eq__(self, other: object) -> bool:
        """Check whether the given players have the same ID."""
        if not isinstance(other, Player):  # pragma: no cover
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Return the hash of the ID."""
        return hash(self.id)


def _get_color_preference(section: PlayerSection) -> ColorPreference:
    """Return the color preference of the given player."""
    colors = [round_result.color for round_result in section.results if round_result.result.is_played()]

    # FIDE handbook: "1.5 Colour differences and colour preferences"
    # The colour preference (also called: due colour) is the colour that a player should ideally receive for the next
    # game. It can be determined for each player who has played at least one game.
    # 1.5.1 An absolute colour preference occurs when a player's colour difference is greater than +1 or less than -1,
    #       or when a player had the same colour in the two latest rounds they played. The preference is for White when
    #       the colour difference is less than -1 or when the last two games were played with Black. The preference is
    #       for Black when the colour difference is greater than +1, or when the last two games were played with White.
    # 1.5.2 A strong colour preference occurs when a player's colour difference is +1 (preference for Black) or -1
    #       (preference for White).
    # 1.5.3 A mild colour preference occurs when a player's colour difference is zero, the preference being to alternate
    #       the colour with respect to the previous game they played.
    # 1.5.4 Players who did not play any games have no colour preference (the preference of their opponents is granted).

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
    return ColorPreference(side=ColorPreferenceSide.NONE, strength=ColorPreferenceStrength.NONE)


def _get_buchholz_dict(sections: list[PlayerSection], score_point_system: ScoringPointSystem) -> dict[int, int]:
    """Return a map from starting number to the Buchholz of all players."""
    points_dict = {section.starting_number: section.points_times_ten for section in sections}
    buchholz_dict = {}

    # FIDE handbook: "1.7 Opposition Evaluation | 1.7.2 Common Rules | 3."
    # Exception: if a player has a series of consecutive zero-point-byes up to the current round, each of the ones
    # gathered in previous rounds, for the benefit of the player's actual over-the-board opponents, is considered as a
    # draw.

    draw_points = score_point_system.score_dict[(ResultToken.HALF_POINT_BYE, ColorToken.BYE_OR_NOT_PAIRED)]
    for section in sections:
        if all(round_result.result == ResultToken.ZERO_POINT_BYE for round_result in section.results):
            points_dict[section.starting_number] = draw_points * len(section.results)

    # FIDE handbook: "1.7 Opposition Evaluation | 1.7.1 Sorting Methods | 1. Buchholz"
    # It is the sum of the (current) scores of the opponents the player met.

    for section in sections:
        scores = [
            points_dict[round_result.id] if round_result.result.is_played() else section.points_times_ten
            for round_result in section.results
        ]
        buchholz_dict[section.starting_number] = sum(scores)

    return buchholz_dict


def _get_sonneborn_berger_dict(sections: list[PlayerSection], score_point_system: ScoringPointSystem) -> dict[int, int]:
    """Return a map from starting number to the Sonneborn Berger of all players."""
    points_dict = {section.starting_number: section.points_times_ten for section in sections}
    sonneborn_berger_dict = {}

    # FIDE handbook: "1.7 Opposition Evaluation | 1.7.1  Sorting Methods | 1. Sonneborn-Berger"
    # It is the sum of the products given by the points the player earned against each opponent times the (current)
    # scores of that opponent.

    for section in sections:
        scores = [
            points_dict[round_result.id] if round_result.result.is_played() else section.points_times_ten
            for round_result in section.results
        ]
        multiplied_scores = [
            score * score_point_system.get_points_times_ten(round_result)
            for score, round_result in zip(scores, section.results, strict=True)
        ]
        sonneborn_berger_dict[section.starting_number] = sum(multiplied_scores)

    return sonneborn_berger_dict


def get_player_infos_from_trf(trf: ParsedTrf) -> list[Player]:
    """Return a list of all player related information relevant for pairing."""
    players = []
    sections = trf.player_sections
    buchholz_dict = _get_buchholz_dict(sections, trf.x_section.scoring_point_system)
    sonneborn_berger_dict = _get_sonneborn_berger_dict(sections, trf.x_section.scoring_point_system)

    round_number = min(len(player.results) for player in sections)
    sections = [player for player in sections if len(player.results) == round_number]
    sections = [player for player in sections if player.starting_number not in trf.x_section.zeroed_ids]

    for i, section in enumerate(sections):
        number = i + 1 if trf.x_section.configuration.by_rank else section.starting_number
        accelerations = trf.x_section.accelerations.get(section.starting_number, (round_number + 1) * [0])

        color_preference = _get_color_preference(section)

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
            points_with_acceleration=section.points_times_ten + accelerations[round_number],
            color_preference=color_preference,
            buchholz=buchholz_dict[section.starting_number],
            sonneborn_berger=sonneborn_berger_dict[section.starting_number],
            opponents=opponents,
            colors=colors,
            bye_received=bye_received,
        )
        players.append(player)

    return players
