from dataclasses import dataclass
from typing import List, Callable, Dict

from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot_action_server.models import BotAction

from maneuvers.dribbling.carry_and_flick import CarryAndFlick
from maneuvers.general_defense import GeneralDefense
from maneuvers.maneuver import Maneuver
from maneuvers.recovery import Recovery
from maneuvers.refuel import Refuel
from rlutilities.simulation import Car
from strategy.defense import Defense
from strategy.kickoffs import KickoffStrategy
from strategy.offense import Offense
from tools.game_info import GameInfo
from tools.vector_math import distance


@dataclass
class TwitchAction:
    description: str
    get: Callable[[Car, GameInfo], Maneuver]
    chat: QuickChatSelection


class TwitchChatStrategy:
    def __init__(self, game_info: GameInfo):
        self.info = game_info
        self.offense = Offense(game_info)
        self.defense = Defense(game_info)
        self.offense.allow_dribbles = True

        self.actions: Dict[str, TwitchAction] = {
            "shoot": TwitchAction(
                description="Take the shot!",
                get=lambda car, info: self.offense.direct_shot(car, info.their_goal.center),
                chat=QuickChatSelection.Information_IGotIt
            ),
            "clear": TwitchAction(
                description="Save / clear",
                get=lambda car, info: self.defense.any_clear(car),
                chat=QuickChatSelection.Information_Defending
            ),
            "dribble": TwitchAction(
                description="Attempt to dribble",
                get=lambda car, info: CarryAndFlick(car, info, info.their_goal.center),
                chat=QuickChatSelection.Information_Incoming
            ),
            "refuel": TwitchAction(
                description="Get some boost",
                get=lambda car, info: Refuel(car, info, info.ball.position),
                chat=QuickChatSelection.Information_NeedBoost
            ),
            "fallback": TwitchAction(
                description="Go back and wait",
                get=lambda car, info: GeneralDefense(car, info, info.ball.position, 7000),
                chat=QuickChatSelection.Information_InPosition
            ),
        }

    def get_available_actions(self) -> List[BotAction]:
        return [BotAction(description=self.actions[key].description, action_type=key, data={})
                for key in self.actions]

    def get_quick_chat(self, action_name: str) -> QuickChatSelection:
        return self.actions[action_name].chat

    def choose_maneuver(self, car: Car, action_name: str) -> Maneuver:
        info = self.info
        ball = info.ball

        teammates = info.get_teammates(car)

        # recovery
        if not car.on_ground:
            return Recovery(car)

        # kickoff
        should_go = all(distance(mate, ball) > distance(car, ball) for mate in teammates)
        if should_go and ball.position[0] == 0 and ball.position[1] == 0:
            return KickoffStrategy.choose_kickoff(info, car)

        # twitch chat chosen actions
        return self.actions[action_name].get(car, info)
