from maneuvers.jumps.aim_dodge import AimDodge
from maneuvers.strikes.strike import Strike
from rlutilities.linear_algebra import norm, dot, normalize, xy
from rlutilities.simulation import Ball
from tools.intercept import estimate_time
from tools.math import clamp
from tools.vector_math import ground_direction


class DodgeStrike(Strike):
    """
    Strike the ball by dodging into it.
    """

    jump_time_multiplier = 1.0

    def intercept_predicate(self, ball: Ball):
        time_left = ball.time - self.car.time
        jump_duration = self.get_jump_duration(ball.position[2])

        if jump_duration >= time_left: return False

        time = estimate_time(self.car, ball, max_accelerate_time=time_left - jump_duration)
        if time > time_left: return False

        return ball.position[2] < 300

    def __init__(self, car, info, target=None):
        self.dodge = AimDodge(car, 0.1, info.ball.position)
        self.dodging = False

        super().__init__(car, info, target)

    def get_jump_duration(self, ball_height: float) -> float:
        return 0.05 + clamp((ball_height - 92) / 500, 0, 1.5) * self.jump_time_multiplier

    def configure(self, intercept: Ball):
        target_direction = ground_direction(intercept, self.target)
        hit_dir = ground_direction(intercept.velocity, target_direction * (norm(intercept.velocity) * 3 + 500))

        self.arrive.target = xy(intercept.position) - hit_dir * 165
        self.arrive.target_direction = hit_dir
        self.arrive.arrival_time = intercept.time

        self.dodge.jump.duration = self.get_jump_duration(intercept.position[2])
        self.dodge.target = intercept.position
        self.arrive.additional_shift = self.get_jump_duration(intercept.position[2]) * 500

    def interruptible(self) -> bool:
        if self.info.ball.position.z > 400 and self.dodging:
            self.announce("Opponent hit the ball at a decent height, interrupting")
            return True
        return not self.dodging and super().interruptible()

    def step(self, dt):
        if self.dodging:
            self.dodge.step(dt)
            self.controls = self.dodge.controls
        else:
            super().step(dt)

            if self.arrive.arrival_time - self.car.time < self.dodge.jump.duration + 0.13:
                if self.explainable_and([
                    ("speed diff", abs(self.arrive.drive.target_speed - norm(self.car.velocity)) < 1000),
                    ("velocity dir", dot(normalize(self.car.velocity), ground_direction(self.car, self.intercept)) > 0.8
                                     or norm(self.car.velocity) < 1000),
                ], slowmo=True):
                    self.dodging = True

        if self.dodge.finished:
            self.expire("Dodge finished.")
