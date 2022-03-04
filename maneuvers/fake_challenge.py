from maneuvers.driving.travel import Travel
from maneuvers.maneuver import Maneuver
from maneuvers.strikes.clears import DodgeClear
from rlutilities.linear_algebra import vec3, norm, clip
from rlutilities.simulation import Car
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.intercept import estimate_time
from tools.vector_math import distance, ground_distance, ground, ground_direction, angle_to, \
    nearest_point


class FakeChallenge(Maneuver):
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        self.travel = Travel(car)

    def step(self, dt: float):
        time_est = estimate_time(self.car, self.info.ball)
        ball_to_my_goal = ground_direction(self.info.ball, self.info.my_goal.center)
        target = ground(self.info.ball.position) + ball_to_my_goal * 800 * clip(time_est, 0.5, 4.0)

        offset = vec3(norm(self.car.velocity), 0, 0)
        side_targets = [target - offset, target + offset]
        closest_side_target = nearest_point(self.car.position, side_targets)

        if ground_distance(self.car, closest_side_target) < 2000:  # and dot(self.car.velocity, ball_to_my_goal) < 0:
            self.travel.target = target
        else:
            self.travel.target = closest_side_target

        self.travel.step(dt)
        self.controls = self.travel.controls

        if distance(self.car, self.info.ball) < 200 and angle_to(self.car, self.info.ball.position) < 0.5:
            self.expire("Got too close")
            self.push(DodgeClear(self.car, self.info))

        if (
                ground_distance(self.info.ball, self.info.my_goal.center) < 3000
                or abs(self.info.my_goal.center.y - self.info.ball.position.y) < 1000
        ):
            self.expire("Too close to my net")
            self.push(DodgeClear(self.car, self.info))

        dribble_bot = min(self.info.get_opponents(), key=lambda car: distance(car, self.info.ball))
        if self.info.ball.position.z < 100:
            self.expire("Opponent dropped the ball.")
        if ground_distance(dribble_bot, self.info.ball) > 500 or not dribble_bot.on_ground:
            self.expire("Opponent probably flicked?")

    def interruptible(self) -> bool:
        return False

    def render(self, draw: DrawingTool):
        self.travel.render(draw)
