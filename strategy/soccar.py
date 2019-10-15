from maneuvers.kit import *
from strategy.offense import Offense
from maneuvers.refuel import Refuel
from maneuvers.fallback import Fallback
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.air.fast_recovery import FastRecovery
from maneuvers.drive_down_wall import DriveDownWall
from maneuvers.jump_off_wall import JumpOffWall


class SoccarStrategy:

    def __init__(self, info: GameInfo, draw: DrawingTool):
        self.info = info
        self.draw = draw
    
    def choose_maneuver(self) -> Maneuver:
        info = self.info
        car = info.my_car
        ball = info.ball

        if not car.on_ground:
            return FastRecovery(car)

        if car.position[2] > 200:
            if norm(xy(car.velocity)) > 500 and car.position[2] < 1000: 
                return JumpOffWall(car)
            else:
                return DriveDownWall(car)

        if ball.position[0] == 0 and ball.position[1] == 0:
            return Kickoff(car, info)

        if car.boost < 5:
            return Refuel(car, info, info.my_goal.center)

        strike = Offense.get_best_strike(car, ball, info.their_goal)
        if strike:
            return strike

        if car.boost < 50:
            return Refuel(car, info, info.my_goal.center)

        return Fallback(car, info)