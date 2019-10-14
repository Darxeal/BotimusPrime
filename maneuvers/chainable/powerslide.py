from maneuvers.kit import *
from maneuvers.driving.drive import Drive


class Powerslide(ChainableManeuver):

    def __init__(self, car):
        super().__init__(car)
        self.drive = Drive(car)
        self.drive.target_pos = self.target
        self.first_step = True
        self.first_simulation: Car = None

    def viable(self):
        angle = angle_to(self.car, self.target)
        return angle > 1.8 and norm(self.car.velocity) > 500

    def simulate(self) -> Car:
        copy = Car(self.car)
        angle = angle_to(self.car, self.target)
        turn_sign = sgn(local(self.car, self.target)[1])
        t = angle / 3.14 * 1.2
        x0 = self.car.position
        v0 = self.car.velocity
        a = self.car.forward() * -450 + self.car.left() * turn_sign * 600

        copy.velocity = v0 + a * t
        copy.position = x0 + v0 * t + 0.5 * a * t**2
        copy.orientation = look_at(ground_direction(copy.position, self.target), vec3(0,0,1))
        return copy

    def step(self, dt):
        self.drive.target_pos = self.target
        self.drive.step(dt)
        self.controls = self.drive.controls
        self.controls.boost = 0
        self.controls.throttle = 1

        if self.first_step:
            self.first_step = False
            self.first_simulation = self.simulate()

        if angle_to(self.car, self.target) < 0.5:
            self.finished = True

    def render(self, draw: DrawingTool):
        draw.color(draw.lime)
        draw.vector(self.car.position, self.car.velocity)
        if self.first_simulation:
            draw.color(draw.yellow)
            draw.car_shadow(self.first_simulation)
            draw.vector(self.first_simulation.position, self.first_simulation.velocity)