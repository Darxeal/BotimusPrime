from maneuvers.kit import *
from strategy.offense import Offense
from maneuvers.refuel import Refuel
from maneuvers.fallback import Fallback
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.air.fast_recovery import FastRecovery
from maneuvers.drive_down_wall import DriveDownWall
from maneuvers.jump_off_wall import JumpOffWall
from maneuvers.strikes.clear import Clear
from maneuvers.telepathy import Telepathy

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


        my_strike = Offense.get_best_strike(car, ball, info.their_goal)
        their_strike = Offense.get_best_strike(opponent, ball, info.my_goal)

        if my_strike and their_strike:
            if my_strike.intercept.time < their_strike.intercept.time:
                return my_strike

        if car.boost < 10:
            return Refuel(car, info, info.my_goal.center)

        if their_strike:
            return Telepathy(car, info, their_strike)

        if my_strike:
            return my_strike

        return Fallback(car, info)