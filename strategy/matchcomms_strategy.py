from typing import Optional

from rlbot.matchcomms.client import MatchcommsClient

from maneuvers.general_defense import GeneralDefense
from maneuvers.maneuver import Maneuver
from maneuvers.pickup_boostpad import PickupBoostPad
from maneuvers.strikes.aerial_strike import AerialStrike
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from rlutilities.simulation import Car
from strategy.boost_management import choose_boostpad_to_pickup
from tools.game_info import GameInfo

ACTIONS = {
    "dodge_strike": lambda car, info: DodgeStrike(car, info, info.their_goal.center),
    "ground_strike": lambda car, info: GroundStrike(car, info, info.their_goal.center),
    "aerial_strike": lambda car, info: AerialStrike(car, info, info.their_goal.center),
    "pickup_boost": lambda car, info: PickupBoostPad(car, choose_boostpad_to_pickup(info, car)),
    "defense": lambda car, info: GeneralDefense(car, info, info.ball.position, 5000),
}


def get_maneuver_from_comms(matchcomms: MatchcommsClient, car: Car, info: GameInfo) -> Optional[Maneuver]:
    if matchcomms.incoming_broadcast.empty():
        return

    message = matchcomms.incoming_broadcast.get_nowait()
    if isinstance(message, dict) and message.get("event", "") == "action_selected":
        action = message["action"]
        return ACTIONS[action](car, info)
