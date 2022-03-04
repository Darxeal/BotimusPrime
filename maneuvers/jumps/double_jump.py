from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3, look_at
from rlutilities.mechanics import Reorient
from rlutilities.simulation import Car


class DoubleJump(Maneuver):
    def __init__(self, car: Car, aim_target: vec3):
        super().__init__(car)
        self.aim_target = aim_target

        self.timer = 0
        self.counter = 0

        self.reorient = Reorient(car)

    def interruptible(self) -> bool:
        return False

    def step(self, dt):
        # first jump
        if self.timer <= 0.2:
            self.controls.jump = True

        elif self.counter < 3:
            self.controls.jump = False
            self.counter += 1

        # second jump
        elif self.timer < 0.3:
            self.controls.jump = True

        else:
            self.reorient.target_orientation = look_at(self.aim_target - self.car.position)
            self.reorient.step(dt)
            self.controls = self.reorient.controls

        self.timer += dt

        if self.car.velocity.z < -100 or self.timer > 0.5 and self.car.on_ground:
            self.finished = True
