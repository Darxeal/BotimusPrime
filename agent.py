from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState

from rlutilities.simulation import Input
from rlutilities.linear_algebra import norm

from tools.drawing import DrawingTool
from tools.quick_chats import QuickChatTool
from rlbot.matchcomms.common_uses.set_attributes_message import handle_set_attributes_message
from rlbot.matchcomms.common_uses.reply import reply_to

from maneuvers.kit import Maneuver
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.kickoffs.diagonal import DiagonalKickoff
from maneuvers.shadow_defense import ShadowDefense

from strategy.soccar_strategy import SoccarStrategy
from strategy.training import get_maneuver_by_name

from utils.vector_math import distance
from utils.game_info import GameInfo

import time

class BotimusPrime(BaseAgent):
    
    RENDERING = True

    PREDICTION_RATE = 120
    PREDITION_DURATION = 8

    # def is_hot_reload_enabled(self):
    #     return False

    def initialize_agent(self):
        self.info: GameInfo = GameInfo(self.index, self.team)
        self.controls: SimpleControllerState = SimpleControllerState()
        self.maneuver: Maneuver = None

        self.info.set_mode("soccar")

        self.last_touch_time = 0
        self.reset_time = 0
        self.ticks = 0

        self.draw: DrawingTool = DrawingTool(self.renderer)

        self.strategy = SoccarStrategy(self.info, self.draw)

        # variables related to quick chats
        self.chat = QuickChatTool(self)
        self.last_ball_vel = 0
        self.said_gg = False
        self.last_time_said_all_yours = 0
        self.num_of_our_goals_reacted_to = 0
        self.num_of_their_goals_reacted_to = 0

        self.training = False
        self.matchcomms_message = ""

    def handle_training_matchcomms(self) -> bool:
        try:
            msg = self.matchcomms.incoming_broadcast.get_nowait()
            if handle_set_attributes_message(msg, self, allowed_keys=['matchcomms_message']):
                reply_to(self.matchcomms, msg)
                self.training = True
                return True
        except:
            return False
        return False

    def get_output(self, packet: GameTickPacket):
        self.info.read_packet(packet, self.get_field_info())
        self.ticks += 1
        self.strategy.packet = packet

        # check if we should go for kickoff
        if packet.game_info.is_kickoff_pause and not isinstance(self.maneuver, Kickoff):
            self.maneuver = None

        # reset maneuver when another car hits the ball
        touch = packet.game_ball.latest_touch
        if ((
            self.info.my_car.on_ground
            and not self.controls.jump
            and touch.time_seconds > self.last_touch_time
            and touch.player_name != packet.game_cars[self.index].name
        )):
            self.last_touch_time = touch.time_seconds
            self.maneuver = None

        # check if an excercise wants us to set a certain maneuver
        if self.handle_training_matchcomms():
            self.info.predict_ball(self.PREDICTION_RATE * self.PREDITION_DURATION, 1 / self.PREDICTION_RATE)
            self.maneuver = get_maneuver_by_name(self.matchcomms_message, self.info)
            print("Training: Setting " + self.matchcomms_message)


        # choose maneuver
        if self.maneuver is None and self.ticks > 10:

            if self.RENDERING:
                self.draw.clear()

            self.info.predict_ball(self.PREDICTION_RATE * self.PREDITION_DURATION, 1 / self.PREDICTION_RATE)
            
            if self.training and self.info.my_car.on_ground:
                self.maneuver = get_maneuver_by_name(self.matchcomms_message, self.info)            
            else:
                self.maneuver = self.strategy.choose_maneuver()
            
            name = str(type(self.maneuver).__name__)
            print(name)

            self.last_ball_vel = norm(self.info.ball.velocity)

        
        # execute maneuver
        if self.maneuver is not None:
            self.maneuver.step(self.info.time_delta)
            self.controls = self.maneuver.controls

            if self.RENDERING:
                self.draw.group("maneuver")
                self.maneuver.render(self.draw)

            if self.maneuver.finished:
                self.maneuver = None

        if self.RENDERING:
            self.draw.execute()

        self.chat.step(packet)

        return self.controls
