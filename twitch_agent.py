from threading import Thread
from time import sleep
from typing import Optional, List

from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState
from rlbot_action_server.bot_action_broker import BotActionBroker, run_action_server, find_usable_port
from rlbot_action_server.bot_holder import set_bot_action_broker
from rlbot_action_server.models import BotAction, AvailableActions, ActionChoice, ApiResponse
from rlbot_twitch_broker_client import ActionServerRegistration, ApiClient, Configuration
from rlbot_twitch_broker_client.api.register_api import RegisterApi
from rlbot_twitch_broker_client.defaults import STANDARD_TWITCH_BROKER_PORT
from urllib3.exceptions import MaxRetryError

from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Input
from strategy.twitch_chat import TwitchChatStrategy
from tools.drawing import DrawingTool
from tools.game_info import GameInfo


class MyActionBroker(BotActionBroker):
    def __init__(self, bot):
        self.bot = bot
        self.current_action: BotAction = None

    def get_actions_currently_available(self) -> List[AvailableActions]:
        return self.bot.get_actions_currently_available()

    def set_action(self, choice: ActionChoice):
        self.current_action = choice.action
        return ApiResponse(200, f"Botimus shall {self.current_action.description}")


class BotwitchmusPrime(BaseAgent):
    RENDERING = True

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.info: GameInfo = None
        self.draw: DrawingTool = None
        self.strategy: TwitchChatStrategy = None

        self.tick_counter = 0
        self.last_latest_touch_time = 0

        self.maneuver: Optional[Maneuver] = None
        self.controls: SimpleControllerState = SimpleControllerState()

        self.action_broker = MyActionBroker(self)

    def initialize_agent(self):
        self.info = GameInfo(self.team)
        self.info.set_mode("soccar")
        self.draw = DrawingTool(self.renderer, self.team)
        self.strategy = TwitchChatStrategy(self.info)

        port = find_usable_port(8080)
        Thread(target=run_action_server, args=(port,), daemon=True).start()
        set_bot_action_broker(self.action_broker)  # This now works on initial load

        Thread(target=self.stay_connected_to_twitch_broker, args=(port,), daemon=True).start()

    def stay_connected_to_twitch_broker(self, port):
        register_api_config = Configuration()
        register_api_config.host = f"http://127.0.0.1:{STANDARD_TWITCH_BROKER_PORT}"
        twitch_broker_register = RegisterApi(ApiClient(configuration=register_api_config))
        while True:
            try:
                twitch_broker_register.register_action_server(
                    ActionServerRegistration(base_url=f"http://127.0.0.1:{port}"))
            except MaxRetryError:
                self.logger.warning('Failed to register with twitch broker, will try again...')
            sleep(10)

    def get_actions_currently_available(self) -> List[AvailableActions]:
        actions = AvailableActions(
            entity_name="Botwitchmus Prime",
            current_action=self.action_broker.current_action,
            available_actions=self.strategy.get_available_actions()
        )
        return [actions]

    def get_output(self, packet: GameTickPacket):
        # wait a few ticks after initialization, so we work correctly in rlbottraining
        if self.tick_counter < 20:
            self.tick_counter += 1
            return Input()

        self.info.read_packet(packet, self.get_field_info())

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
            if self.maneuver and self.maneuver.interruptible():
                self.maneuver = None

        # choose maneuver
        if self.maneuver is None:

            if self.RENDERING:
                self.draw.clear()

            self.info.predict_ball()
            action_name = self.action_broker.current_action.action_type if self.action_broker.current_action else "shoot"
            self.maneuver = self.strategy.choose_maneuver(self.info.cars[self.index], action_name)
            self.send_quick_chat(False, self.strategy.get_quick_chat(action_name))

        # execute maneuver
        if self.maneuver is not None:
            self.maneuver.step(self.info.time_delta)
            self.controls = self.maneuver.controls

            if self.RENDERING:
                self.draw.group("maneuver")
                self.draw.color(self.draw.yellow)
                self.draw.string(self.info.cars[self.index].position + vec3(0, 0, 50), type(self.maneuver).__name__)
                self.maneuver.render(self.draw)

            # cancel maneuver when finished
            if self.maneuver.finished:
                self.maneuver = None

        if self.RENDERING:
            self.draw.execute()

        return self.controls


