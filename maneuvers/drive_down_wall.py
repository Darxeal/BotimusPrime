from maneuvers.kit import *
from maneuvers.driving.drive import Drive


class DriveDownWall(Maneuver):

    def __init__(self, car: Car):
        super().__init__(car)
        self.drive = Drive(car)

    def step(self, dt):
        self.drive.target_pos = ground(self.car.position) + self.car.up() * 10
        self.drive.step(dt)
        self.controls = self.drive.controls
        if self.car.position[2] < 200 or not self.car.on_ground:
            self.finished = True
