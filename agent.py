from typing import Optional

from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState

from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.kit import Maneuver
from rlutilities.simulation import Input
from strategy.soccar_strategy import SoccarStrategy
from utils.drawing import DrawingTool
from utils.game_info import GameInfo


class BotimusPrime(BaseAgent):
    
    RENDERING = True

    PREDICTION_RATE = 120
    PREDICTION_DURATION = 8

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info: GameInfo = None
        self.draw: DrawingTool = None
        self.strategy: SoccarStrategy = None

        self.tick_counter = 0
        self.last_latest_touch_time = 0

        self.maneuver: Optional[Maneuver] = None
        self.controls: SimpleControllerState = SimpleControllerState()

    def initialize_agent(self):
        self.info = GameInfo(self.index, self.team)
        self.info.set_mode("soccar")
        self.draw = DrawingTool(self.renderer)
        self.strategy = SoccarStrategy(self.info, self.draw)

    def get_output(self, packet: GameTickPacket):
        # wait a few ticks after initialization, so we work correctly in rlbottraining
        self.tick_counter += 1
        if self.tick_counter < 10:
            return Input()

        self.info.read_packet(packet, self.get_field_info())
        self.strategy.packet = packet

        # cancel maneuver if a kickoff is happening and current maneuver isn't a kickoff maneuver
        if packet.game_info.is_kickoff_pause and not isinstance(self.maneuver, Kickoff):
            self.maneuver = None

        # reset maneuver when another car hits the ball
        touch = packet.game_ball.latest_touch
        if (
            touch.time_seconds > self.last_latest_touch_time
            and touch.player_name != packet.game_cars[self.index].name
        ):
            self.last_latest_touch_time = touch.time_seconds

            # don't reset when we're dodging, wavedashing or recovering
            if self.info.my_car.on_ground and not self.controls.jump:
                self.maneuver = None

        # choose maneuver
        if self.maneuver is None:

            if self.RENDERING:
                self.draw.clear()
            
            self.info.predict_ball(self.PREDICTION_RATE * self.PREDICTION_DURATION, 1 / self.PREDICTION_RATE)
            self.maneuver = self.strategy.choose_maneuver()
        
        # execute maneuver
        if self.maneuver is not None:
            self.maneuver.step(self.info.time_delta)
            self.controls = self.maneuver.controls

            if self.RENDERING:
                self.draw.group("maneuver")
                self.maneuver.render(self.draw)

            # cancel maneuver when finished
            if self.maneuver.finished:
                self.maneuver = None

        if self.RENDERING:
            self.draw.execute()

        return self.controls


