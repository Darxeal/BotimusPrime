from maneuvers.kit import *
from maneuvers.driving.travel import Travel


class Fallback(Maneuver):

    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info: GameInfo = info
        self.travel = Travel(car)

    def step(self, dt):
        self.travel.target = vec3(sgn(self.info.ball.position[0]) * 2000, self.info.my_goal.center[1] * 0.9, 0)
        self.travel.step(dt)
        self.controls = self.travel.controls
        if ground_distance(self.travel.target, self.car.position) < 2000:
            self.finished = True

    def render(self, draw):
        self.travel.render(draw)
