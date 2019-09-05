from rlbot.agents.base_agent import BaseAgent, GameTickPacket, SimpleControllerState
from rlbot.utils.game_state_util import GameState

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Input
from RLUtilities.LinearAlgebra import norm

from tools.drawing import DrawingTool
from tools.quick_chats import QuickChatTool

from maneuvers.kit import Maneuver
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.shadow_defense import ShadowDefense

from strategy.twitch_chat import TwitchChatStrategy

from utils.vector_math import distance

from utils.intercept import Intercept
from maneuvers.air.fast_recovery import FastRecovery

from tools.maneuver_history import *
from time import time

class BotimusPrime(BaseAgent):
    
    RENDERING = True

    PREDICTION_RATE = 120
    PREDITION_DURATION = 8

    def initialize_agent(self):
        self.info: GameInfo = GameInfo(self.index, self.team)
        self.controls: SimpleControllerState = SimpleControllerState()
        self.maneuver: Maneuver = None

        self.time = 0
        self.prev_time = 0
        self.last_touch_time = 0
        self.reset_time = 0
        self.ticks = 0

        self.draw: DrawingTool = DrawingTool(self.renderer)
        self.history = ManeuverHistory()

        self.strategy = TwitchChatStrategy(self.info, self.draw, self.history)
        self.paused = False
        self.pause_target = False
        self.last_time_paused = -99


    def get_output(self, packet: GameTickPacket):
        self.time = packet.game_info.seconds_elapsed
        dt = self.time - self.prev_time
        if packet.game_info.is_kickoff_pause and not isinstance(self.maneuver, Kickoff):
            self.maneuver = None

        self.prev_time = self.time
        if self.ticks < 6:
            self.ticks += 1

        self.info.read_packet(packet)
        self.strategy.packet = packet
        

        #reset maneuver when another car hits the ball
        touch = packet.game_ball.latest_touch
        if ((
            touch.time_seconds > self.last_touch_time
            and touch.player_name != packet.game_cars[self.index].name
        ) or (
            touch.player_name == '' and # if latest touch info is missing
            any([distance(self.info.ball, car) < 300 for car in self.info.opponents + self.info.teammates])
        )):
            self.last_touch_time = touch.time_seconds
            if (
                self.info.my_car.on_ground
                and (not isinstance(self.maneuver, ShadowDefense) or self.maneuver.travel._driving)
            ):
                pass
                # self.maneuver = None
                #self.reset_time = self.time


        # choose maneuver
        if self.maneuver is None and self.time > self.reset_time + 0.01 and self.ticks > 5 and packet.game_info.is_round_active:

            info = self.info
            car = info.my_car
            their_goal = info.their_goal.center
            my_goal = info.my_goal.center
            my_hit = Intercept(car, info.ball_predictions)
            their_hit = Intercept(info.opponents[0], info.ball_predictions)

            if not car.on_ground:
                self.maneuver = FastRecovery(car)
                self.history.add("Recovery", "AUTOMATIC", "In progress")

            elif info.ball.pos[0] == 0 and info.ball.pos[1] == 0:
                self.maneuver = Kickoff(car, info)
                self.history.add("Kickoff", "AUTOMATIC", "In progress")
            
            else:
                self.info.predict_ball(self.PREDICTION_RATE * self.PREDITION_DURATION, 1 / self.PREDICTION_RATE)
                self.draw.string2D(500, 300, "Waiting for new commands...", 3)
                self.draw.ball_prediction(self.info)

                if not self.paused:
                    self.set_game_state(GameState(console_commands=["Pause"]))
                    self.paused = True
                    self.pause_target = True

                self.paused = True
                print("getting command")
                self.maneuver = self.strategy.get_maneuver()

            if self.maneuver is None:
                self.pause_target = True

            else:
                self.pause_target = False
                print("chosen " + str(type(self.maneuver).__name__))
        
        # execute maneuver
        if self.maneuver is not None:
            self.maneuver.step(dt)

            self.controls = self.maneuver.controls

            if self.RENDERING:
                self.maneuver.render(self.draw)


            if self.maneuver.finished:
                print(str(type(self.maneuver).__name__) + " finished")
                self.maneuver = None
                self.history.history[len(self.history.history) - 1].status = "Finished"

                if self.RENDERING:
                    self.draw.clear()

        if self.RENDERING:
            self.history.render(self.draw)
            self.draw.execute()

        if time() > self.last_time_paused + 0.1:
            if self.paused != self.pause_target:
                self.set_game_state(GameState(console_commands=["Pause"]))
                self.paused = self.pause_target
            self.last_time_paused = time()

        return self.controls