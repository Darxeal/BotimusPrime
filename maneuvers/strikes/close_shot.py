from maneuvers.strikes.dodge_strike import DodgeStrike
from rlutilities.simulation import Car, Ball
from tools.intercept import Intercept
from tools.math import abs_clamp


class CloseShot(DodgeStrike):
    jump_time_multiplier = 1.1

    def intercept_predicate(self, car: Car, ball: Ball):
        return ball.position[2] < 250

    def configure(self, intercept: Intercept):
        self.target[0] = abs_clamp(self.intercept.ground_pos[0], 400)
        super().configure(intercept)
