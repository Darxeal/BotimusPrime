from typing import Optional

from rlbot.matchcomms.client import MatchcommsClient

from maneuvers.challenge import Challenge
from maneuvers.general_defense import GeneralDefense
from maneuvers.maneuver import Maneuver
from maneuvers.pickup_boostpad import PickupBoostPad
from maneuvers.recovery import Recovery
from maneuvers.squishy_save import SquishySave
from maneuvers.strikes.approach import Approach
from maneuvers.strikes.clears import DodgeClear
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from rlutilities.simulation import Car, BoostPad
from strategy.boost_management import best_pad_on_the_way_to_ball, best_pad_on_the_way_to_my_goal
from tools.game_info import GameInfo
from tools.intercept import intercept_estimate
from tools.vector_math import ground_direction


def approach_shot(car: Car, info: GameInfo) -> Approach:
    info.predict_ball(7.0)
    intercept = intercept_estimate(car, info.ball_predictions)
    shot_direction = ground_direction(intercept, info.their_goal.center)
    return Approach(car, shot_direction, intercept.position)


def handle_pad_none(car: Car, pad: Optional[BoostPad]) -> Maneuver:
    if pad:
        return PickupBoostPad(car, pad)
    else:
        return Recovery(car)  # should expire immediately


ACTIONS = {
    "dodge_strike": lambda car, info: DodgeStrike(car, info, info.their_goal.center),
    "ground_strike": lambda car, info: GroundStrike(car, info, info.their_goal.center),
    "defense": lambda car, info: GeneralDefense(car, info, info.ball.position, 5000),
    "clear": lambda car, info: DodgeClear(car, info),
    "boost_to_ball": lambda car, info: handle_pad_none(car, best_pad_on_the_way_to_ball(car, info)),
    "boost_to_goal": lambda car, info: handle_pad_none(car, best_pad_on_the_way_to_my_goal(car, info)),
    "squishy_save": lambda car, info: SquishySave(car, info),
    "challenge": lambda car, info: Challenge(car, info),
}


def get_maneuver_from_comms(matchcomms: MatchcommsClient, car: Car, info: GameInfo) -> Optional[Maneuver]:
    if matchcomms.incoming_broadcast.empty():
        return

    message = matchcomms.incoming_broadcast.get_nowait()
    if isinstance(message, dict) and message.get("event", "") == "action_selected":
        action = message["action"]
        return ACTIONS[action](car, info)
