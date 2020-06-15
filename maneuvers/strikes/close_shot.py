from maneuvers.strikes.dodge_strike import DodgeStrike
from utils.intercept import Intercept
from utils.math import abs_clamp


class CloseShot(DodgeStrike):
    jump_time_multiplier = 1.1

    def configure(self, intercept: Intercept):
        self.target[0] = abs_clamp(self.intercept.ground_pos[0], 400)
        super().configure(intercept)
