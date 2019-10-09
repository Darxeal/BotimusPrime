from maneuvers.kit import *

from maneuvers.strikes.strike import Strike
from maneuvers.jumps.aim_dodge import AimDodge

class DodgeStrike(Strike):

    allow_backwards = True

    def intercept_predicate(self, car, ball):
        return ball.position[2] < 280

    def __init__(self, car, info, target=None):
        self.dodge = AimDodge(car)
        self.dodging = False

        super().__init__(car, info, target)

    def configure(self, intercept: Intercept):
        super().configure(intercept)

        if self.target is None:
            self.arrive.target = intercept.ground_pos + ground_direction(intercept, self.car) * 100
        else:
            self.arrive.target = intercept.ground_pos - ground_direction(intercept.ground_pos, self.target) * 150

        additional_jump = clamp((intercept.ball.position[2]-92) / 600, 0, 1.5)
        self.dodge.duration = 0.05 + additional_jump
        self.dodge.direction = vec2(ground_direction(self.arrive.target, intercept))
        self.arrive.additional_shift = additional_jump * 500


    def step(self, dt):
        if self.dodging:
            self.dodge.step(dt)
            self.controls = self.dodge.controls
        else:
            super().step(dt)
            if self.arrive.time - self.car.time < self.dodge.duration + 0.3:
                self.dodging = True
        self.finished = self.finished or self.dodge.finished
