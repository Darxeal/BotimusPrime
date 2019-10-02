from maneuvers.kit import *

from RLUtilities.Maneuvers import Drive, AirDodge

class DiagonalKickoff(Maneuver):
    '''Dodge forward once to get there faster.'''
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        self.drive = Drive(car)
        self.drive.target_speed = 2300

        self.dodge = AirDodge(car, 0.1, info.ball.pos)

        self.phase = 0

    def step(self, dt):
        if self.phase == 0:
            self.controls.throttle = 1
            self.controls.boost = 1
            if ground_distance(self.car, self.info.ball) < 2950:
                print("entering phase 1")
                self.phase = 1
        
        if self.phase == 1:
            self.dodge.step(dt)
            self.controls = self.dodge.controls
            self.controls.yaw
            if self.dodge.finished and self.car.on_ground:
                print("entering phase 2")
                self.phase = 2
                self.dodge = AirDodge(self.car, 0.18, self.info.ball.pos)
        
        if self.phase == 2:
            self.drive.step(dt)
            self.controls = self.drive.controls
            if distance(self.car, self.info.ball) < 850:
                print("entering phase 3")
                self.phase = 3
                

        if self.phase == 3:
            self.dodge.step(dt)
            self.controls = self.dodge.controls

        self.finished = self.info.ball.pos[0] != 0 and self.dodge.finished

    def render(self, draw: DrawingTool):
        pass
