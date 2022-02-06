from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec2, dot, sgn
from rlutilities.mechanics import Dodge
from rlutilities.simulation import Car


# Most of this class is from the old RLUtilities, made by chip


class HalfFlip(Maneuver):
    def __init__(self, car: Car, use_boost=False):
        super().__init__(car)
        self.use_boost = use_boost

        self.dodge = Dodge(car)
        self.dodge.jump_duration = 0.12
        self.dodge.direction = vec2(car.forward() * (-1))

        self.s = 0.95 * sgn(dot(self.car.angular_velocity, self.car.up()) + 0.01)

        self.timer = 0.0

    def interruptible(self) -> bool:
        return False

    def step(self, dt):

        boost_delay = 0.4
        stall_start = 0.50
        stall_end = 0.70
        timeout = 2.0

        self.dodge.step(dt)
        self.controls = self.dodge.controls

        if stall_start < self.timer < stall_end:
            self.controls.roll = 0.0
            self.controls.pitch = -1.0
            self.controls.yaw = 0.0

        if self.timer > stall_end:
            self.controls.roll = self.s
            self.controls.pitch = -1.0
            self.controls.yaw = self.s

        if self.use_boost and self.timer > boost_delay:
            self.controls.boost = 1
        else:
            self.controls.boost = 0

        self.timer += dt

        self.finished = (self.timer > timeout) or (self.car.on_ground and self.timer > 0.5)
