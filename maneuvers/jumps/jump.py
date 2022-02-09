from maneuvers.maneuver import Maneuver
from rlutilities.simulation import Car


# Most of this class is from the old RLUtilities, made by chip


class Jump(Maneuver):
    def __init__(self, car: Car, duration: float):
        super().__init__(car)
        self.duration = duration

        self.timer = 0
        self.counter = 0

    def interruptible(self) -> bool:
        return False

    def step(self, dt):

        self.controls.jump = 1 if self.timer < self.duration else 0

        if self.controls.jump == 0:
            self.counter += 1

        self.timer += dt

        if self.counter >= 2:
            self.finished = True

        return self.finished
