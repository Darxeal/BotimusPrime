from maneuvers.dribbling.dribble import Dribble
from maneuvers.air.aerial import Aerial
from maneuvers.strikes.dodge_shot import DodgeShot
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.strike import Strike
from maneuvers.strikes.ground_shot import GroundShot
from maneuvers.strikes.mirror_shot import MirrorShot
from maneuvers.strikes.close_shot import CloseShot
from maneuvers.strikes.aerial_shot import AerialShot
from maneuvers.strikes.wall_shot import WallShot
from maneuvers.strikes.wall_dodge_shot import WallDodgeShot
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.driving.travel import Travel
from maneuvers.chain_maneuver import ChainManeuver
from maneuvers.chainable.turn import Turn
from maneuvers.chainable.powerslide import Powerslide
from utils.game_info import GameInfo
from maneuvers.kit import *

def get_maneuver_by_name(name: str, info: GameInfo):
    car = info.my_car
    if name == "DodgeShot":
        return DodgeShot(car, info, info.their_goal.center)
    if name == "DodgeStrike":
        return DodgeStrike(car, info, info.their_goal.center)
    if name == "TurnAndTravel":
        travel = Travel(car)
        travel.target = info.ball.position
        return ChainManeuver(car, [Turn(car, travel.target)], travel)
    if name == "SlideAndTravel":
        travel = Travel(car)
        travel.target = info.ball.position
        return ChainManeuver(car, [Powerslide(car, travel.target)], travel)
