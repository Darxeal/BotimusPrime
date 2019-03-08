from maneuvers.kit import *

#TODO: doesnt work, fix

class InversedHalfFlip(Maneuver):

    def __init__(self, car):
        super().__init__(car)

        duration = 0.12
        behind = car.pos + 1000.0 * car.forward()
        self.dodge = AirDodge(self.car, duration, behind)

        self.s = 0.95 * sgn(dot(self.car.omega, self.car.up()) + 0.01)

        self.timer = 0.0


    def step(self, dt):

        boost_delay = 0.4
        stall_start = 0.50
        stall_end = 0.70
        timeout = 2.0

        self.dodge.step(dt)
        self.controls = self.dodge.controls

        if stall_start < self.timer < stall_end:
            self.controls.roll  =  0.0
            self.controls.pitch = 1.0
            self.controls.yaw   =  0.0

        if self.timer > stall_end:
            self.controls.roll  =  -self.s
            self.controls.pitch = 1.0
            self.controls.yaw   =  -self.s

        self.controls.boost = 0

        self.timer += dt

        self.finished = (self.timer > timeout) or \
                        (self.car.on_ground and self.timer > 0.5)
