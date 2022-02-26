from typing import List

from maneuvers.strikes.aerial_strike import FastAerialStrike
from maneuvers.strikes.dodge_strike import DodgeStrike
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Ball, Car
from tools.arena import Arena

# make a bunch of points on the side of the arena
_one_side = [vec3(Arena.size[0], Arena.size[1] * i / 30, 0) for i in range(-30, 30)]
_other_side = [vec3(-p[0], p[1], 0) for p in _one_side]


# the clears simply pick the easiest point to aim at
# this is not a very elegant solution, so I'll just put a TODO: make this better
def get_target_points(car: Car, intercept: Ball) -> List[vec3]:
    if abs(intercept.position.x - car.position.x) < 1000:
        return _one_side if intercept.position.x > 0 else _other_side
    return _one_side + _other_side


class DodgeClear(DodgeStrike):
    def configure(self, intercept: Ball):
        self.target = self.pick_easiest_target(self.car, intercept, get_target_points(self.car, intercept))
        super().configure(intercept)


class FastAerialClear(FastAerialStrike):
    def configure(self, intercept: Ball):
        self.target = self.pick_easiest_target(self.car, intercept, get_target_points(self.car, intercept))
        super().configure(intercept)
