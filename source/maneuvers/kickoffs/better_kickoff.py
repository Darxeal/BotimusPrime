
from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive

class BetterKickoff(Maneuver):

    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)

        self.info = info

        self.arrive = Arrive(car, vec3(0,0,0), 0, direction(info.ball, info.their_goal.center))
        self.arrive.lerp_t = 0.65

        self.first_dodge = AirDodge(car, 0.05, info.ball.pos)
        self.second_dodge = AirDodge(car, 0.05, info.ball.pos)

        self.state = 0
        self.action = self.arrive

    def step(self, dt):
        if self.state == 0 and norm(self.car.vel) > 600:
            self.state = 1
            self.action = self.first_dodge

        if self.state == 1 and self.first_dodge.finished and self.car.on_ground:
            self.state = 2
            self.action = self.arrive
        
        if self.state == 2 and distance(self.car, self.info.ball) < 1000:
            self.state = 3
            self.action = self.second_dodge

        self.action.step(dt)
        self.controls = self.action.controls
        self.finished = self.second_dodge.finished

    # def render(self, draw: DrawingTool):
    #     self.arrive.render(draw)
