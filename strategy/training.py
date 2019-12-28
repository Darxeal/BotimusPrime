from maneuvers.strikes.dodge_shot import DodgeShot
from utils.game_info import GameInfo


def get_maneuver_by_name(name: str, info: GameInfo):
    if name == "DodgeShot":
        return DodgeShot(info.my_car, info, info.their_goal.center)