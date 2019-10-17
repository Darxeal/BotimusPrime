from maneuvers.kit import *
from maneuvers.strikes.dodge_strike import DodgeStrike


class Clear(DodgeStrike):

    def get_target_direction(self):
        facing_direction = ground_direction(self.car, self.intercept)
        team_sign = 1 if self.car.team == 1 else -1
        if sgn(facing_direction[1]) == team_sign:
            facing_direction = vec3(sgn(facing_direction[0]), 0, 0)
        return facing_direction

    def get_hit_direction(self):
        return self.get_target_direction()
        
