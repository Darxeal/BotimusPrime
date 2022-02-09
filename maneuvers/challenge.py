from maneuvers.driving.drive import Drive
from maneuvers.jumps.air_dodge import AirDodge
from maneuvers.jumps.jump import Jump
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import look_at, vec3, angle_between, norm
from rlutilities.mechanics import Reorient
from rlutilities.simulation import Car
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.vector_math import direction, ground_distance, angle_to


class Challenge(Maneuver):
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        self.drive = Drive(car, target_speed=1400)
        self.reorient = Reorient(car)

        self.jumped = False

    def step(self, dt: float):
        if self.jumped:
            point_dir = direction(self.car, self.info.ball) + vec3(z=0.5)
            self.reorient.target_orientation = look_at(point_dir, vec3(z=1))
            self.reorient.step(dt)
            self.controls = self.reorient.controls
            self.controls.boost = angle_between(self.car.forward(), point_dir) < 0.5

            if self.car.position.z > self.info.ball.position.z or self.car.position.z > 500:
                self.finished = True
                self.announce("Dodging into ball")
                self.push(AirDodge(self.car, target=self.info.ball.position))
        else:
            target = self.info.ball.position + self.info.ball.velocity * 0.5
            self.drive.target_pos = target
            self.drive.step(dt)
            self.controls = self.drive.controls

            if self.info.ball.position.z < 100:
                self.expire("Ball hit the ground")

            combined_speed = norm(self.car.velocity) + norm(self.info.ball.velocity)
            if ground_distance(self.car, self.info.ball) < combined_speed * 0.6 and angle_to(self.car, target) < 0.2:
                self.jumped = True
                self.announce("Jumping")
                self.push(Jump(self.car, duration=0.2))

    def interruptible(self) -> bool:
        return False

    def render(self, draw: DrawingTool):
        super().render(draw)
