from maneuvers.driving.travel import Travel
from maneuvers.maneuver import Maneuver
from maneuvers.strikes.clears import DodgeClear
from rlutilities.linear_algebra import vec3, norm, dot
from rlutilities.simulation import Car
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.vector_math import distance, ground_distance, ground, ground_direction, angle_to, \
    nearest_point


class FakeChallenge(Maneuver):
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        self.travel = Travel(car)

    def step(self, dt: float):
        dribble_bot = min(self.info.get_opponents(), key=lambda car: distance(car, self.info.ball))
        if self.info.ball.position.z < 100:
            self.expire("Opponent dropped the ball.")
        if distance(dribble_bot, self.info.ball) > 300 or not dribble_bot.on_ground:
            self.expire("Opponent probably flicked?")

        dist_to_ball = ground_distance(self.car, self.info.ball)
        time_est = dist_to_ball / 2300
        ball_to_my_goal = ground_direction(self.info.ball, self.info.my_goal.center)
        target = ground(self.info.ball.position) + ball_to_my_goal * 1500 * max(time_est, 1.0)

        offset = vec3(norm(self.car.velocity), 0, 0)
        side_targets = [target - offset, target + offset]
        closest_side_target = nearest_point(self.car.position, side_targets)

        if ground_distance(self.car, closest_side_target) < 1500 and dot(self.car.velocity, ball_to_my_goal) < 0:
            self.travel.target = target
        else:
            self.travel.target = closest_side_target

        self.travel.step(dt)
        self.controls = self.travel.controls

        if distance(self.car, self.info.ball) < 1000 and angle_to(self.car, self.info.ball.position) < 1.0:
            self.expire("Got too close")
            self.push(DodgeClear(self.car, self.info))

        if ground_distance(self.info.ball, self.info.my_goal.center) < 3000:
            self.expire("Too close to my net")
            self.push(DodgeClear(self.car, self.info))

    def interruptible(self) -> bool:
        return False

    def render(self, draw: DrawingTool):
        self.travel.render(draw)
