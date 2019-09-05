from tools.twitch_chat_bot import TwitchChatBot
from typing import List, Optional

from maneuvers.kit import Maneuver
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.driving.stop import Stop
from maneuvers.air.fast_recovery import FastRecovery
from maneuvers.strikes.dodge_shot import DodgeShot
from maneuvers.strikes.strike import Strike
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_shot import GroundShot
from maneuvers.strikes.aerial_strike import AerialStrike
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.dribbling.dribble import Dribble
from maneuvers.air.aerial import Aerial
from maneuvers.strikes.dodge_shot import DodgeShot
from maneuvers.strikes.strike import Strike
from maneuvers.strikes.ground_shot import GroundShot
from maneuvers.strikes.mirror_shot import MirrorShot
from maneuvers.strikes.close_shot import CloseShot
from maneuvers.strikes.aerial_shot import AerialShot
from maneuvers.strikes.wall_shot import WallShot
from maneuvers.strikes.wall_dodge_shot import WallDodgeShot

from RLUtilities.GameInfo import GameInfo
from RLUtilities.LinearAlgebra import *
from RLUtilities.Simulation import Car, Ball

from utils.vector_math import *
from utils.math import *
from utils.misc import *
from utils.intercept import Intercept
from utils.arena import Arena

from strategy.offense import Offense

from tools.drawing import DrawingTool
from tools.maneuver_history import *

class Command:
    def __init__(self, author: str, command: str):
        self.author: str = author
        self.command: str = command

class TwitchChatStrategy(TwitchChatBot):
    def __init__(self, info: GameInfo, drawing_tool: DrawingTool, history: ManeuverHistory):
        super().__init__("darxeal", "oauth:1l8n2ogyscw5k1o36vn3ln4v97mkst", "#darxeal")

        self.scanned_commands: List[Command] = []
        self.info = info
        self.offense = Offense(info)
        self.draw = drawing_tool
        self.history = history

    def on_message(self, sender, message):
        if message[0] == "!":
            self.scanned_commands.append(Command(sender, message[1:]))

    def clear_into_corner(self, my_hit: Intercept) -> DodgeShot:
        car = self.info.my_car
        my_goal = self.info.my_goal.center
        corners = [my_goal + vec3(Arena.size[0], 0, 0), my_goal - vec3(Arena.size[0], 0, 0)]
        corner = Strike.pick_easiest_target(car, my_hit.ball, corners)
        corner[1] *= 0.8
        return self.offense.any_shot(car, corner, my_hit)

    def get_maneuver(self):

        info = self.info
        car = info.my_car
        their_goal = info.their_goal.center
        my_goal = info.my_goal.center
        my_hit = Intercept(car, info.ball_predictions)
        their_hit = Intercept(info.opponents[0], info.ball_predictions)
            
        self.scan()

        action: Optional[Maneuver] = None
        selected_command: Command = None

        for command in reversed(self.scanned_commands):
            if command.command == "defend":
                action = ShadowDefense(car, info, their_hit.ground_pos, 5000)
            elif command.command == "attack":
                action = self.offense.any_shot(car, their_goal, my_hit)
            elif command.command == "carry":
                action = Dribble(car, info, their_goal)
            elif command.command == "recovery":
                action = FastRecovery(car)
            elif command.command == "shoot":
                action = DodgeShot(car, info, their_goal)
            elif command.command == "aerial":
                action = AerialShot(car, info, their_goal)
            elif command.command == "chipshot":
                action = GroundShot(car, info, their_goal)
            elif command.command == "boost":
                action = Refuel(car, info, their_hit.ground_pos)
            elif command.command == "hit":
                action = DodgeStrike(car, info)
            elif command.command == "clearintocorner":
                action = self.clear_into_corner(my_hit)
            else:
                print("Invalid command")
                self.history.add(selected_command.command, selected_command.author, "Invalid command")
                continue

            action.step(1/120)
            if action.finished:
                continue

            selected_command = command
            break

        if selected_command is not None:
            self.history.add(selected_command.command, selected_command.author, "In progress")

        self.scanned_commands.clear()
        return action
