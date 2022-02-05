from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec2, look_at, vec3
from rlutilities.mechanics import Reorient, Dodge
from tools.vector_math import ground_direction


class JumpOffTheWallDash(Maneuver):
    def __init__(self, car, target: vec3):
        super().__init__(car)
        self.target = target

        self.reorient = Reorient(car)
        self.dodge = Dodge(car)
        self.dodge.jump_duration = 0
        self.dodge.delay = 0

        self.__start_time = car.time

    def step(self, dt: float):
        if self.car.time - self.__start_time < 0.1:
            self.controls.jump = True
            self.explain("Jumping off wall.")
            return

        if self.car.on_ground:
            self.expire()

        to_target = ground_direction(self.car, self.target)

        if self.car.position.z + self.car.velocity.z * 0.1 < 0:
            self.dodge.direction = vec2(to_target)
            self.dodge.step(dt)
            self.controls = self.dodge.controls
            self.explain("Almost landing, attempting wavedash.", slowmo=True)
        else:
            self.reorient.target_orientation = look_at(to_target + vec3(z=0.3), vec3(z=1))
            self.reorient.step(dt)
            self.controls = self.reorient.controls
