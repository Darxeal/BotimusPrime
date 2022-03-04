from maneuvers.jumps.double_jump import DoubleJump
from maneuvers.strikes.strike import Strike
from rlutilities.linear_algebra import norm, xy
from rlutilities.simulation import Ball
from tools.drawing import DrawingTool
from tools.intercept import estimate_time
from tools.vector_math import ground_direction, ground_distance


class DoubleJumpStrike(Strike):
    vel_align_radius_threshold = 50

    def intercept_predicate(self, ball: Ball):
        time_left = ball.time - self.car.time
        jump_duration = self.get_jump_duration(ball.position.z)

        if jump_duration >= time_left: return False

        time = estimate_time(self.car, ball, max_accelerate_time=time_left - jump_duration)
        if time > time_left: return False

        return 450 < ball.position.z < 650

    def __init__(self, car, info, target=None):
        self.jump = DoubleJump(car, info.ball.position)
        self.jumping = False
        super().__init__(car, info, target)

    def configure(self, intercept: Ball):
        target_direction = ground_direction(intercept, self.target)
        hit_dir = ground_direction(intercept.velocity, target_direction * (norm(intercept.velocity) * 3 + 500))

        self.arrive.target = xy(intercept.position) - hit_dir * 100
        self.arrive.target_direction = hit_dir
        self.arrive.arrival_time = intercept.time

        self.jump.aim_target = intercept.position
        self.arrive.additional_shift = self.get_jump_duration(intercept.position.z) * 300

    def interruptible(self) -> bool:
        if self.info.ball.position.z > 400 and self.jumping:
            self.announce("Opponent hit the ball at a decent height, interrupting")
            return True
        return not self.jumping and super().interruptible()

    def step(self, dt):
        if self.jumping:
            self.jump.step(dt)
            self.controls = self.jump.controls
        else:
            super().step(dt)

            dj_time = self.get_jump_duration(self.intercept.position.z)
            if self.arrive.arrival_time - self.car.time < dj_time:
                pos_after_dj = xy(self.car.position) + xy(self.car.velocity) * dj_time
                if ground_distance(pos_after_dj, self.arrive.target) < self.vel_align_radius_threshold:
                    self.jumping = True
                else:
                    self.explain("Not matching required velocity.", slowmo=True)
                    if ground_distance(self.car.position, pos_after_dj) > ground_distance(
                            self.car.position, self.arrive.target) + self.vel_align_radius_threshold:
                        self.controls.boost = False
                        self.controls.throttle = -1
                        self.explain("Approaching too fast, slowing down!")

        if self.jump.finished:
            self.expire("Dodge finished.")

    def render(self, draw: DrawingTool):
        super().render(draw)

        if not self.jumping:
            dj_time = self.get_jump_duration(self.intercept.position.z)
            pos_after_dj = xy(self.car.position) + xy(self.car.velocity) * dj_time
            draw.color(draw.red)
            draw.line(xy(self.car.position), pos_after_dj)
            draw.circle(self.arrive.target, self.vel_align_radius_threshold)

    @staticmethod
    def get_jump_duration(height):
        """Return the time needed for the double jump to reach a given height"""
        # polynomial approximation
        height = height - 90
        a = 1.872348977E-8 * height * height * height
        b = -1.126747937E-5 * height * height
        c = 3.560647225E-3 * height
        d = -7.446058499E-3
        return a + b + c + d
