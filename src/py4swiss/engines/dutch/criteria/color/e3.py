from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E3(ColorCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        colors_1 = [color for color in player_1.colors if color is not None]
        colors_2 = [color for color in player_2.colors if color is not None]

        for color_1, color_2 in zip(colors_1[::-1], colors_2[::-1]):
            if color_1 != color_2:
                return not color_1

        return None
