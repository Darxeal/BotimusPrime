from typing import Optional, List

from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState

from maneuvers.maneuver import Maneuver, PushToStackException
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Input
from strategy import solo_strategy, teamplay_strategy
from strategy.kickoffs import choose_kickoff
from strategy.matchcomms_strategy import get_maneuver_from_comms
from tools.announcer import Announcer
from tools.drawing import DrawingTool
from tools.game_info import GameInfo


class BotimusPrime(BaseAgent):
    RENDERING = True

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info = GameInfo(self.team)
        self.draw: DrawingTool = None

        self.tick_counter = 0
        self.last_latest_touch_time = 0

        self.stack: List[Maneuver] = []
        self.controls: SimpleControllerState = SimpleControllerState()

    def initialize_agent(self):
        self.info.set_mode("soccar")
        self.info.read_field_info(self.get_field_info())
        self.draw = DrawingTool(self.renderer, self.team)

    def is_hot_reload_enabled(self):
        return False

    @property
    def maneuver(self) -> Optional[Maneuver]:
        return self.stack[-1] if self.stack else None

    @maneuver.setter
    def maneuver(self, value: Maneuver):
        self.stack = [value]

    def get_output(self, packet: GameTickPacket):
        # wait a few ticks after initialization, so we work correctly in rlbottraining
        if self.tick_counter < 20:
            self.tick_counter += 1
            return Input()

        self.info.read_packet(packet)
        my_car = self.info.cars[self.index]

        # cancel maneuver if a kickoff is happening and current maneuver isn't a kickoff maneuver
        if self.info.ball.position.x == self.info.ball.position.y == 0 and not hasattr(self.maneuver, "is_kickoff"):
            self.maneuver = choose_kickoff(self.info, my_car)

        # reset maneuver when another car hits the ball
        touch = packet.game_ball.latest_touch
        if (
                touch.time_seconds > self.last_latest_touch_time
                and touch.player_name != packet.game_cars[self.index].name
        ):
            self.last_latest_touch_time = touch.time_seconds

            # don't reset when we're dodging, wavedashing or recovering
            if self.maneuver and self.maneuver.interruptible():
                self.maneuver = None
                # Announcer.announce("Someone touched the ball, aborting maneuver.")

        advised_maneuver = get_maneuver_from_comms(self.matchcomms, my_car, self.info)
        if advised_maneuver:
            self.maneuver = advised_maneuver

        # choose maneuver
        if self.maneuver is None and self.info.is_ball_present:

            if self.RENDERING:
                self.draw.clear()

            # self.matchcomms.outgoing_broadcast.put_nowait({
            #     "event": "checkpoint",
            #     "actions": list(matchcomms_strategy.ACTIONS.keys())
            # })

            if self.info.get_teammates(my_car):
                self.maneuver = teamplay_strategy.choose_maneuver(self.info, my_car)
            else:
                self.maneuver = solo_strategy.choose_maneuver(self.info, my_car)
            Announcer.announce(type(self.maneuver).__name__)

        # execute maneuver
        if self.maneuver is not None:
            try:
                self.maneuver.step(self.info.time_delta)
                self.controls = self.maneuver.controls
            except PushToStackException as push:
                self.stack.extend(push.pushed_maneuvers)

            if self.RENDERING:
                self.draw.group("maneuver")
                self.draw.color(self.draw.yellow)
                stack_str = "\n".join(type(maneuver).__name__ for maneuver in self.stack)
                self.draw.string(my_car.position + vec3(0, 0, 50), stack_str)
                self.maneuver.render(self.draw)

            # cancel maneuver when finished
            if self.maneuver.finished:
                self.stack.pop()

        # if self.teleport_detector.teleport_happened(self.info):
        #     self.maneuver = None

        if self.RENDERING:
            Announcer.step(self.set_game_state, self.renderer)
            self.draw.execute()

        return self.controls
