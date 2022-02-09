from maneuvers.strikes.strike import Strike
from rlutilities.linear_algebra import vec3, norm, normalize, look_at, dot, vec2, axis_to_rotation
from rlutilities.mechanics import Aerial, Dodge
from rlutilities.simulation import Car, Ball
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.intercept import estimate_time
from tools.math import range_map
from tools.vector_math import ground_direction, angle_to, ground_distance, direction


class AerialStrike(Strike):
    MAX_DISTANCE_ERROR = 50
    MINIMAL_HEIGHT = None
    MAXIMAL_HEIGHT = None
    MINIMAL_HEIGHT_TIME = None
    MAXIMAL_HEIGHT_TIME = None
    DOUBLE_JUMP = False
    FREESTYLE = False

    def __init__(self, car: Car, info: GameInfo, target: vec3 = None):
        self.aerial = Aerial(car)
        self.aerial.angle_threshold = 0.8
        self.aerial.double_jump = self.DOUBLE_JUMP

        super().__init__(car, info, target)
        self.arrive.allow_dodges_and_wavedashes = False

        self.aerialing = False

    def required_aerial_time(self, height: float = None) -> float:
        if height is None:
            height = self.intercept.position[2]

        return range_map(height, self.MINIMAL_HEIGHT, self.MAXIMAL_HEIGHT,
                         self.MINIMAL_HEIGHT_TIME, self.MAXIMAL_HEIGHT_TIME)

    def boost_required(self):
        return self.required_aerial_time() * 33 * 0.8

    def intercept_predicate(self, ball: Ball):
        aerial_duration = self.required_aerial_time(ball.position[2])
        time_left = ball.time - self.car.time
        if aerial_duration > time_left:
            return False

        if estimate_time(self.car, ball.position, max_accelerate_time=time_left - aerial_duration) > time_left:
            return False

        return self.MINIMAL_HEIGHT < ball.position[2] < self.MAXIMAL_HEIGHT and time_left > aerial_duration

    additional_z_intercept_offset = 0

    def configure(self, intercept: Ball):
        target_pos = intercept.position - direction(intercept, self.target) * 100
        target_pos.z += self.additional_z_intercept_offset

        self.aerial.target_position = target_pos
        self.aerial.arrival_time = intercept.time

        self.arrive.target = target_pos
        self.arrive.arrival_time = intercept.time + intercept.position[2] / 1000 * 0.2 + 0.1

    def interruptible(self) -> bool:
        return self.aerialing or super().interruptible()

    def step(self, dt):
        time_left = self.aerial.arrival_time - self.car.time

        if self.aerialing:
            to_ball = direction(self.car, self.info.ball)

            # freestyling
            if self.FREESTYLE and self.car.position[2] > 200:
                if time_left > 0.5:
                    rotation = axis_to_rotation(self.car.forward() * 0.5)
                    self.aerial.up = dot(rotation, self.car.up())
                else:
                    self.aerial.up = vec3(0, 0, -3) + to_ball
                self.aerial.target_orientation = look_at(to_ball, vec3(0, 0, -3) + to_ball)

            self.aerial.step(dt)

            self.controls = self.aerial.controls
            self.finished = self.aerial.finished and time_left < -0.3

        else:
            super().step(dt)

            if time_left < self.required_aerial_time() + 0.1:
                speed_towards_target = dot(self.car.velocity, ground_direction(self.car, self.aerial.target_position))
                too_fast_towards_target = speed_towards_target > ground_distance(self.car, self.intercept) / time_left

                if self.explainable_and([
                    ("facing target", angle_to(self.car, self.aerial.target_position) < 0.1),
                    ("angvel low", norm(self.car.angular_velocity) < 0.5),
                    ("low speed towards target", not too_fast_towards_target),
                ], slowmo=True):
                    self.aerialing = True
                elif too_fast_towards_target:
                    self.controls.throttle = -1
                    self.controls.boost = False
                    self.explain("Slowing down.")

    def render(self, draw: DrawingTool):
        super().render(draw)


class FastAerialStrike(AerialStrike):
    MINIMAL_HEIGHT = 800
    MAXIMAL_HEIGHT = 1800
    MINIMAL_HEIGHT_TIME = 1.2
    MAXIMAL_HEIGHT_TIME = 2.2
    DOUBLE_JUMP = True
    FREESTYLE = True


class AirRollStrike(AerialStrike):
    MINIMAL_HEIGHT = 300
    MAXIMAL_HEIGHT = 800
    MINIMAL_HEIGHT_TIME = 0.8
    MAXIMAL_HEIGHT_TIME = 1.8

    additional_z_intercept_offset = 0

    def __init__(self, car: Car, info: GameInfo, target: vec3 = None):
        super().__init__(car, info, target)
        self.dodge = Dodge(car)
        self.dodge.jump_duration = 0.0
        self.dodge.delay = 0.0

    def boost_required(self):
        return self.required_aerial_time() * 33

    def step(self, dt):
        super().step(dt)

        if self.aerialing:
            self.aerial.up = normalize(direction(self.intercept, self.car) + vec3(0, 0, 1))

            time_left = self.aerial.arrival_time - self.car.time
            if time_left < 0.15:
                self.dodge.direction = vec2(direction(self.car.position, self.info.ball.position))
                self.dodge.step(dt)
                self.controls = self.dodge.controls
