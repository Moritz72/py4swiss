from py4swiss.trf.codes.player_code import PlayerCode
from py4swiss.trf.codes.team_code import TeamCode
from py4swiss.trf.codes.tournament_code import TournamentCode
from py4swiss.trf.codes.x_code import XCode

Code = PlayerCode | TeamCode | TournamentCode | XCode

CODE_LENGTH = 3
PLAYER_CODES = set(PlayerCode)
TEAM_CODES = set(TeamCode)
TOURNAMENT_CODES = set(TournamentCode)
X_CODES = set(XCode)

__all__ = [
    "CODE_LENGTH",
    "PLAYER_CODES",
    "TEAM_CODES",
    "TOURNAMENT_CODES",
    "X_CODES",
    "Code",
    "PlayerCode",
    "TeamCode",
    "TournamentCode",
    "XCode",
]
