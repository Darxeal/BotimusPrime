from typing import Optional

from rlbot.matchcomms.client import MatchcommsClient

from maneuvers.general_defense import GeneralDefense
from maneuvers.maneuver import Maneuver
from maneuvers.pickup_boostpad import PickupBoostPad
from rlutilities.simulation import Car
from strategy import offense
from strategy.boost_management import choose_boostpad_to_pickup
from tools.game_info import GameInfo

ACTIONS = {
    "direct_shot": lambda car, info: offense.direct_shot(info, car, info.their_goal.center),
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
