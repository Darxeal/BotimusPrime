from maneuvers.kit import *
from strategy.offense import Offense
from maneuvers.refuel import Refuel
from maneuvers.fallback import Fallback
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.air.fast_recovery import FastRecovery
from maneuvers.drive_down_wall import DriveDownWall
from maneuvers.jump_off_wall import JumpOffWall
from maneuvers.strikes.clear import Clear
from maneuvers.strikes.challenge import Challenge
from maneuvers.telepathy import Telepathy
from maneuvers.shadow_defense import ShadowDefense
from maneuvers.dribbling.dribble import Dribble


class SoccarStrategy:

    def __init__(self, info: GameInfo, draw: DrawingTool):
        self.info = info
        self.draw = draw
    
    def choose_maneuver(self) -> Maneuver:
        self.draw.group("strategy")
        info = self.info
        car = info.my_car
        ball = info.ball

        # just in case there are some showmatches in Lightfall
        opponents_sorted_by_distance_to_ball = sorted(
            info.opponents, key=lambda opponent: ground_distance(ball, opponent)
        )
        opponent = opponents_sorted_by_distance_to_ball[0]
        self.draw.line(car, opponent)



        # air recovery
        if not car.on_ground:
            return FastRecovery(car)

        # get down to floor
        if car.position[2] > 200:
            if norm(xy(car.velocity)) > 500 and car.position[2] < 1000: 
                return JumpOffWall(car)
            else:
                return DriveDownWall(car)

        # kickoff
        if ball.position[0] == 0 and ball.position[1] == 0:
            return Kickoff(car, info)

        if abs(ball.velocity[2]) > 50:
            if ground_distance(car, ball) < 600:
                if ground_distance(opponent, ball) > 1000:
                    return Dribble(car, info, info.their_goal.center)

        if (
            abs(car.position[1] - info.my_goal.center[1]) >
            abs(ball.position[1] - info.my_goal.center[1])
            and abs(ball.position[0]) < 2000
            and ground_distance(ball, info.my_goal.center) < 5000
        ):
            return Clear(car, ball)


        if ground_distance(ball, info.my_goal.center) < 4000:
            return Challenge(car, info)


        if car.boost < 10 and abs(ball.position[0]) > 3000:
            return Refuel(car, info, info.my_goal.center)


        my_strike = Offense.get_best_strike(car, ball, info.their_goal)
        their_strike = Offense.get_best_strike(opponent, ball, info.my_goal)

        if my_strike and their_strike:
            diff = my_strike.intercept.time - their_strike.intercept.time
            if abs(diff) < 1.0 and ground_distance(my_strike.intercept, info.my_goal.center) < 4000:
                return Challenge(car, info)
            if diff < 0:
                return Telepathy(car, info, their_strike)

        if their_strike and not my_strike:
            return Telepathy(car, info, their_strike)

        if my_strike:
            if ground_distance(my_strike.intercept, info.my_goal.center) < ground_distance(my_strike.intercept, info.their_goal.center):
                my_align = -align(car.position, my_strike.intercept, info.my_goal.center)
            else:
                my_align = align(car.position, my_strike.intercept, info.their_goal.center)

            if my_align > -0.3:
                return my_strike
            else:
                return ShadowDefense(car, info, my_strike.intercept.position, 6000)
        
        if car.boost < 50:
            return Refuel(car, info, info.my_goal.center)

        return Fallback(car, info)

        # if distance(their_best_hit.ground_pos, their_goal) < distance(their_best_hit.ground_pos, my_goal):
        #     opponents_align = -align(opponent.pos, their_best_hit.ball, their_goal)
        # else:
        #     opponents_align = align(opponent.pos, their_best_hit.ball, my_goal)