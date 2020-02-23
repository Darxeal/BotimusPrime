from rlbot.agents.base_agent import GameTickPacket

from utils.game_info import GameInfo
from rlutilities.linear_algebra import *
from rlutilities.simulation import Car, Ball

from utils.vector_math import *
from utils.math import *
from utils.misc import *
from utils.intercept import Intercept
from utils.arena import Arena


from maneuvers.kit import Maneuver
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.kickoffs.diagonal import DiagonalKickoff
from maneuvers.driving.stop import Stop
from maneuvers.air.recovery import Recovery
from maneuvers.strikes.dodge_shot import DodgeShot
from maneuvers.strikes.strike import Strike
from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_shot import GroundShot
from maneuvers.strikes.aerial_strike import AerialStrike
from maneuvers.refuel import Refuel
from maneuvers.shadow_defense import ShadowDefense

from strategy.offense import Offense


#This file is a Wintertide-deadline mess and definitely not something you should learn from..

class SoccarStrategy:
    def __init__(self, info: GameInfo):
        self.info = info
        self.offense = Offense(info)
        self.aggresivity = 0
        self.packet: GameTickPacket = None

    def get_team_scores(self):
        our_score = 0
        their_score = 0
        
        for team in self.packet.teams:
            if team.team_index == self.info.my_car.team:
                our_score = team.score
            else:
                their_score = team.score

        return our_score, their_score

    def best_intercept(self, cars, max_height=9999) -> Intercept:
        best_intercept = None
        best_car = None

        for car in cars:
            intercept = Intercept(car, self.info.ball_predictions, lambda car, ball: ball.position[2] < max_height)
            if best_intercept is None or intercept.time <= best_intercept.time:
                best_intercept = intercept
                best_car = car

        if best_intercept is None:
            best_car = Car()
            best_intercept = Intercept(best_car, [])

        return best_intercept, best_car

    def when_airborne(self) -> Maneuver:
        double_tap = self.offense.double_tap(self.info.my_car, self.info.their_goal.center)
        if double_tap is not None:
            return double_tap
        return Recovery(self.info.my_car)

    def clear_into_corner(self, my_hit: Intercept) -> DodgeShot:
        car = self.info.my_car
        my_goal = self.info.my_goal.center
        corners = [my_goal + vec3(Arena.size[0], 0, 0), my_goal - vec3(Arena.size[0], 0, 0)]
        corner = Strike.pick_easiest_target(car, my_hit.ball, corners)
        corner[1] *= 0.8
        if abs(corner[1]) > abs(car.position[1]):
            corner[1] = car.position[1]

        return DodgeShot(car, self.info, corner)

    def choose_maneuver(self):
        info = self.info
        offense = self.offense

        ball = info.ball
        car = info.my_car

        my_score, their_score = self.get_team_scores()

        their_goal = ground(info.their_goal.center)
        my_goal = ground(info.my_goal.center)

        my_hit = Intercept(car, info.ball_predictions, lambda car, ball: ball.position[2] < 300)
        their_best_hit, opponent = self.best_intercept(info.opponents)

        my_attack_align = align(car.position, my_hit.ball, their_goal)

        opponents_align = 0
        my_align = 0
        if distance(their_best_hit.ground_pos, their_goal) < distance(their_best_hit.ground_pos, my_goal):
            opponents_align = -align(opponent.position, their_best_hit.ball, their_goal)
        else:
            opponents_align = align(opponent.position, their_best_hit.ball, my_goal)
        if distance(my_hit.ground_pos, my_goal) < distance(my_hit.ground_pos, their_goal):
            my_align = -align(car.position, my_hit.ball, my_goal)
        else:
            my_align = align(car.position, my_hit.ball, their_goal)

        print(my_align, my_attack_align, opponents_align)

        if their_score > my_score and not self.packet.game_info.is_unlimited_time:
            if self.packet.game_info.game_time_remaining < 30:
                self.aggresivity = 99999

        # if len(info.opponents) == 1 and self.packet.game_cars[opponent.id].name == "Self-driving car":
        #     self.aggresivity = 100

        should_commit = True
        if info.teammates:
            best_team_intercept, _ = self.best_intercept(info.teammates, 500)
            if best_team_intercept.time < my_hit.time - 0.05:
                should_commit = False


        if not car.on_ground:
            print("Recovery")
            return self.when_airborne()

        # kickoff
        if should_commit and ball.position[0] == 0 and ball.position[1] == 0:
            print("Kickoff")
            if abs(car.position[0]) > 1000:
                return DiagonalKickoff(car, info)
            return Kickoff(car, info)

        # dont save our own shots
        if info.about_to_score:
            if info.time_of_goal < their_best_hit.time - 2:
                print("Stopping in order to not screw up my own shot")
                return Stop(car)

        # save
        if info.about_to_be_scored_on:

            if my_align > -0.2:

                any_shot = offense.any_shot(car, their_goal, my_hit)

                # if (not isinstance(any_shot, Strike) or their_best_hit.time < any_shot.intercept.time + 0.5) \
                # and my_attack_align < 0.6:
                
                #     print("Panic save")
                #     return DodgeStrike(car, info, their_goal)

                print("Saving and trying to shoot")
                return any_shot

            print("Saving into corner")
            return self.clear_into_corner(my_hit)


        # fallback
        if align(car.position, my_hit.ball, my_goal) > 0.2:
            if (
                should_commit
                and ground_distance(car, my_hit) < 5000
                and their_best_hit.time < my_hit.time + 4
                # and abs(car.position[1]) < abs(my_hit.position[1])
                and abs(my_hit.position[0]) < Arena.size[0] - 2000
            ):
                print("fallback, clearing into corner")
                return self.clear_into_corner(my_hit)

            print("fallback")
            return ShadowDefense(car, info, my_hit.ground_pos, 6000)

        # clear
        if (
            should_commit
            and ground_distance(my_hit, my_goal) < 3500
            and abs(my_hit.position[0]) < 2500
            and ground_distance(car, my_goal) < 2500
        ):

            if my_attack_align > -0.2:

                any_shot = offense.any_shot(car, their_goal, my_hit)

                if (not isinstance(any_shot, Strike) or their_best_hit.time < any_shot.intercept.time + 0.5) \
                and my_align < 0.6:
                
                    print("panic clear")
                    return DodgeStrike(car, info, their_goal)

                print("clear shot")
                return any_shot

            print("Clearing into corner")
            return self.clear_into_corner(my_hit)


        # double tap 
        if should_commit and car.position[2] > 1000:
            double_tap = offense.double_tap(car, their_goal)
            if double_tap is not None:
                print("weeeee")
                return double_tap

        # 1v1
        if not info.teammates:

            their_time_left = their_best_hit.time - info.time

            # should I go for the ball?
            if should_commit:
                strike = offense.any_shot(car, their_goal, my_hit)

                if not isinstance(strike, Strike):
                    print("dribble")
                    return strike

                my_time_left = strike.intercept.time - info.time

                if (
                    my_time_left < their_time_left - opponents_align * 2 + my_attack_align
                    and (not info.about_to_score or strike.intercept.time < info.time_of_goal - 1)
                ):

                    if (
                        my_time_left > 4                                                # if the shot is far away
                        and car.boost < 30                                              # i dont have boost
                        and distance(strike.intercept.ground_pos, their_goal) > 3000    # and far from their goal
                        and distance(their_best_hit.ground_pos, my_goal) > 5000         # and far from my net
                    ):
                        print("boost, because it's not dangerous")
                        return Refuel(car, info, my_hit.ground_pos)

                    # go for boost if ball is near the sidewall
                    if (
                        abs(strike.intercept.ground_pos[0]) > Arena.size[0] - 1000
                        and abs(strike.intercept.ground_pos[1]) < 4000
                        and car.boost < 30
                        and their_time_left > 4
                    ):
                        print("boost, near sidewall")
                        return Refuel(car, info, my_hit.ground_pos)

                    if distance(opponent, their_goal) > 2000: # if opponent is not sitting in their net
                        if (
                            abs(strike.intercept.ball.position[1] - their_goal[1]) > 1000     # ball is not near their back wall
                            or abs(strike.intercept.ball.position[0]) < 900     # ball is near their goal
                        ):
                            print("going for ball!")
                            return strike

            if (
                distance(their_best_hit.ball, my_goal) > 7000 
                and (
                    their_time_left > 4
                    or align(opponent.position, their_best_hit.ball, my_goal) < 0
                )
                and car.boost < 30
            ):
                print("boost, because it's safe")
                return Refuel(car, info, my_hit.ground_pos)

            if car.boost < 35 and their_time_left > 4:
                refuel = Refuel(car, info, my_hit.ground_pos)
                if estimate_time(car, refuel.pad.position, 1400) < 1.5:
                    print("boost, because it's near")
                    return refuel

        # teamplay
        else:
            if should_commit:
                return offense.any_shot(car, their_goal, my_hit)

            if car.boost < 50:
                return Refuel(car, info, my_goal)

        shadow_distance = 6500
        # shadow_distance = 3000 + opponents_align * 2500
        # shadow_distance = max(shadow_distance, 1000)
        return ShadowDefense(car, info, their_best_hit.ground_pos, shadow_distance)
