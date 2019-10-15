from maneuvers.kit import *
from maneuvers.air.fast_recovery import FastRecovery
from maneuvers.driving.drive import Drive

class JumpOffWall(Maneuver):

    def __init__(self, car: Car):
        super().__init__(car)
        self.recovery = FastRecovery(car)
        self.drive = Drive(car)
        self.jumped = False

    def step(self, dt):
        if not self.jumped:
            self.drive.target_pos = ground(self.car.position)
            self.drive.step(dt)
            self.controls = self.drive.controls

            if self.car.velocity[2] < -500:
                self.controls.jump = True
                self.jumped = True
        else:
            self.recovery.step(dt)
            self.controls = self.recovery.controls
            self.finished = self.recovery.finished
