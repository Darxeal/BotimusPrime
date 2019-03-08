from rlbot.agents.base_agent import BaseAgent, GameTickPacket

from RLUtilities.GameInfo import GameInfo
from RLUtilities.Simulation import Input
from RLUtilities.LinearAlgebra import norm

from tools.drawing import DrawingTool
from tools.maneuver_history import ManeuverHistory
from tools.quick_chats import QuickChats, QuickChatTool

from maneuvers.kit import Maneuver
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.shadow_defense import ShadowDefense

from strategy.soccar_strategy import SoccarStrategy

from utils.vector_math import distance

# TODO:
# last second save,
# challenge on clears,
# add air roll shots
# doublejump saves
# beat SDC 20-0

class BotimusPrime(BaseAgent):
    
    rendering = False

    def initialize_agent(self):
        self.info: GameInfo = GameInfo(self.index, self.team)
        self.controls: Input = Input()
        self.maneuver: Maneuver = None

        self.time = 0
        self.prev_time = 0
        self.last_touch_time = 0
        self.reset_time = 0
        self.ticks = 0

        self.draw: DrawingTool = DrawingTool(self.renderer)
        self.history: ManeuverHistory = ManeuverHistory()

        self.strategy = SoccarStrategy(self.info)

        # variables related to quick chats
        self.chat = QuickChatTool(self)
        self.last_ball_vel = 0
        self.said_gg = False
        self.last_time_said_all_yours = 0
        self.playing_against_sdc = False
        self.num_of_our_goals_reacted_to = 0
        self.num_of_their_goals_reacted_to = 0


    def get_output(self, packet: GameTickPacket):
        self.time = packet.game_info.seconds_elapsed
        dt = self.time - self.prev_time
        if packet.game_info.is_kickoff_pause and not isinstance(self.maneuver, Kickoff):
            if self.history.history:
                self.history.history.clear()
            self.maneuver = None

        self.prev_time = self.time
        if self.ticks < 1000:
            self.ticks += 1
        self.info.read_packet(packet)
        self.strategy.packet = packet
        

        #reset maneuver when an opponent hits the ball
        touch = packet.game_ball.latest_touch
        if touch.time_seconds > self.last_touch_time:
            self.last_touch_time = touch.time_seconds
            if touch.player_name != packet.game_cars[self.index].name and self.info.my_car.on_ground \
            and (not isinstance(self.maneuver, ShadowDefense) or self.maneuver.travel._driving):
                self.maneuver = None
                self.reset_time = self.time


        # choose maneuver
        if self.maneuver is None and self.time > self.reset_time + 0.01 and self.ticks > 5:

            if self.rendering:
                self.draw.clear()

            self.info.predict_ball(60*8, 1/120)

            self.maneuver, reason = self.strategy.get_maneuver_with_reason()
            
            name = str(type(self.maneuver).__name__)
            print("chosen maneuver: " + name)
            self.history.add(name, reason)

            self.last_ball_vel = norm(self.info.ball.vel)

        
        # execute maneuver
        if self.maneuver is not None:
            self.maneuver.step(dt)
            self.controls = self.maneuver.controls

            if self.rendering:
                self.maneuver.render(self.draw)

            if self.maneuver.finished:
                self.maneuver = None


        if self.rendering:
            self.history.render(self.draw)
            self.draw.execute()

        self.maybe_chat(packet)
        self.chat.step(packet)

        return self.controls

    def maybe_chat(self, packet: GameTickPacket):

        # start of the game
        if self.ticks == 100:

            # react to playing against SDC
            for car in packet.game_cars:
                if car.name == "Self-driving car":
                    for i in range(5):
                        self.chat.send_random([
                            QuickChats.Reactions_OMG,
                            QuickChats.PostGame_Gg,
                            QuickChats.Reactions_HolyCow,
                            QuickChats.Reactions_NoWay
                        ])
                        self.playing_against_sdc = True
                    break

        for team in packet.teams:
            if team.team_index == self.team:
                our_score = team.score
            else:
                their_score = team.score

        # last second goal
        if their_score > self.num_of_their_goals_reacted_to or our_score > self.num_of_our_goals_reacted_to:
            if abs(their_score - our_score) < 2 and packet.game_info.game_time_remaining < 5:
                for i in range(6):
                    self.chat.send_random([
                        QuickChats.Reactions_OMG,
                        QuickChats.PostGame_Gg,
                        QuickChats.Reactions_HolyCow,
                        QuickChats.Reactions_NoWay,
                        QuickChats.Reactions_Wow,
                        QuickChats.Reactions_OMG
                    ])

        # they scored
        if their_score > self.num_of_their_goals_reacted_to:
            self.num_of_their_goals_reacted_to = their_score
            for i in range(2):
                if self.last_ball_vel > 2000:
                    self.chat.send_random([
                        QuickChats.Compliments_NiceShot,
                        QuickChats.Compliments_NiceOne,
                        QuickChats.Reactions_Wow,
                        QuickChats.Reactions_OMG,
                        QuickChats.Reactions_Noooo
                    ])
                else:
                    self.chat.send_random([
                        QuickChats.Reactions_Whew,
                        QuickChats.Apologies_Whoops,
                        QuickChats.Apologies_Oops,
                        QuickChats.Apologies_Cursing
                    ])

        # we scored
        if our_score > self.num_of_our_goals_reacted_to:
            self.num_of_our_goals_reacted_to = our_score

            if self.last_ball_vel > 3000:
                self.chat.send(QuickChats.Reactions_Siiiick)

            if self.last_ball_vel < 300:
                self.chat.send(QuickChats.Compliments_WhatASave)

        # game is over
        if packet.game_info.is_match_ended and not self.said_gg:
            self.said_gg = True

            # celebrate winning against SDC :D
            if self.playing_against_sdc and our_score > their_score:
                for i in range(7):
                    self.chat.send_random([
                        QuickChats.Reactions_NoWay,
                        QuickChats.Reactions_Wow,
                        QuickChats.Reactions_OMG,
                        QuickChats.Reactions_Siiiick,
                        QuickChats.PostGame_WhatAGame,
                        QuickChats.PostGame_ThatWasFun,
                        QuickChats.Custom_Compliments_TinyChances
                    ])

            self.chat.send(QuickChats.PostGame_Gg)
            self.chat.send(QuickChats.PostGame_WellPlayed)
            if our_score < their_score:
                self.chat.send(QuickChats.PostGame_OneMoreGame)

        # all yours :D
        if self.time > self.last_time_said_all_yours + 30:
            if isinstance(self.maneuver, ShadowDefense) and distance(self.info.my_car, self.info.ball) > 5000:
                self.last_time_said_all_yours = self.time
                self.chat.send(QuickChats.Information_AllYours)


