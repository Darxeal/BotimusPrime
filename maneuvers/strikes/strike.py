from typing import List, Optional

from maneuvers.driving.arrive import Arrive
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3, dot, xy
from rlutilities.simulation import Car, Ball
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.intercept import find_intercept, estimate_time
from tools.vector_math import ground_direction


class Strike(Maneuver):
    update_interval = 0.2
    stop_updating = 0.1
    max_additional_time = 0.4

    def __init__(self, car: Car, info: GameInfo, target: vec3 = None):
        super().__init__(car)

        self.info: GameInfo = info
        self.target: Optional[vec3] = target

        self.arrive = Arrive(car)
        self.intercept: Ball = None

        self._start_time = car.time
        self._has_drawn_prediction = False
        self._last_update_time = car.time
        self.update_intercept()
        self._initial_intercept_time = self.intercept.time

    def intercept_predicate(self, ball: Ball):
        return estimate_time(self.car, ball.position) < ball.time - self.car.time

    def configure(self, intercept: Ball):
        self.arrive.target = xy(intercept.position)
        self.arrive.arrival_time = intercept.time

    def update_intercept(self):
        self.intercept = find_intercept(self.info.ball_predictions, self.intercept_predicate)
        self.configure(self.intercept)
        self._last_update_time = self.car.time

    def interruptible(self) -> bool:
        return self.arrive.interruptible()

    def step(self, dt):
        if (
                self._last_update_time + self.update_interval < self.car.time < self.intercept.time - self.stop_updating
                and self.car.on_ground and not self.controls.jump
        ):
            self.info.predict_ball(duration=self.intercept.time - self.car.time + 1)
            self._has_drawn_prediction = False
            self.update_intercept()

            if self.intercept.time > self._initial_intercept_time + self.max_additional_time:
                self.expire("This strike has delayed the intercept too much.")

        self.arrive.step(dt)
        self.controls = self.arrive.controls

        # if self.arrive.drive.target_speed < 300:
        #     self.controls.throttle = 0
        #     self.explain("Target speed low, stopping instead.")

        if self.intercept.time - self.car.time > 2.0 and self.car.time > self._start_time + 1.0:
            self.expire("Plenty of time left, see if there's something better to do.")

        if self.arrive.finished:
            self.expire("Arrive finished.")

    def render(self, draw: DrawingTool):
        self.arrive.render(draw)
        draw.color(draw.lime)
        draw.circle(xy(self.intercept.position), Ball.radius)
        draw.point(self.intercept.position)

        if self.target:
            strike_direction = ground_direction(self.intercept, self.target)
            draw.color(draw.cyan)
            draw.triangle(xy(self.intercept.position) + strike_direction * 150, strike_direction, length=100)

        if not self._has_drawn_prediction:
            self._has_drawn_prediction = True
            draw.ball_prediction(self.info.ball_predictions, self.intercept.time)

    def pick_easiest_target(self, car: Car, ball: Ball, targets: List[vec3]) -> vec3:
        to_goal = ground_direction(ball, self.info.their_goal.center)
        return max(targets,
                   key=lambda target: dot(ground_direction(car, ball) + to_goal * 0.5, ground_direction(ball, target)))
