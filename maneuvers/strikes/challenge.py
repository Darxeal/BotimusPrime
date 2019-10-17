from maneuvers.kit import *
from maneuvers.strikes.dodge_strike import DodgeStrike


class Challenge(DodgeStrike):

    def __init__(self, car, info: GameInfo):
        super().__init__(car, info.ball)
        self.info = info
        self.arrive.arena_clamp = 300

    def get_target_direction(self):
        return ground_direction(self.info.my_goal.center, self.intercept.position)

    def get_hit_direction(self):
        return self.get_target_direction()
        
