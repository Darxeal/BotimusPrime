from maneuvers.dribbling.dribble import Dribble
from maneuvers.air.aerial import Aerial
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from maneuvers.strikes.wall_strike import WallStrike
from maneuvers.strikes.strike import Strike
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.driving.travel import Travel
from maneuvers.chain_maneuver import ChainManeuver
from maneuvers.chainable.turn import Turn
from maneuvers.chainable.powerslide import Powerslide
from utils.game_info import GameInfo
from maneuvers.kit import *
from strategy.offense import Offense


def get_maneuver_by_name(name: str, info: GameInfo):
    car = info.my_car

    if name == "Offense":
        return Offense.get_best_strike(car, info.ball, info.their_goal.center)

    if name == "DodgeStrike":
        return DodgeStrike(car, info.ball, info.their_goal.center)

    if name == "GroundStrike":
        return GroundStrike(car, info.ball, info.their_goal.center)
        
    if name == "WallStrike":
        return WallStrike(car, info.ball, info.their_goal.center)
