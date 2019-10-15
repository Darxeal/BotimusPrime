from maneuvers.kit import *

from maneuvers.strikes.strike import Strike
from maneuvers.jumps.aim_dodge import AimDodge

class DodgeStrike(Strike):

    predodge_time = 0.2

    def __init__(self, car, ball):
        Strike.__init__(self, car, ball)
        self.dodge = AimDodge(car)
        self.dodging = False

    def is_intercept_desirable(self):
        if self.intercept.position[2] > 250:
            return False

        time_left = self.intercept.time - self.car.time
        return time_left > self.get_jump_time() + self.predodge_time


    def get_offset_target(self):
        return ground(self.intercept.position) - self.get_hit_direction() * 100

    @staticmethod
    def get_time_to_z(z, press=0.2) -> float:
        # this function has been stolen from Wildfire
        # https://github.com/robbai/Wildfire/blob/6fa33fe53c8ab44d576b1b63049d5276df332172/src/main/java/wildfire/wildfire/physics/JumpPhysics.java#L20-L38
        # thanks Robbie

        velocity = 300
        acceleration = 1400 - 650

        displacement = velocity * press + 0.5 * acceleration * press**2

        velocity += acceleration * press
        acceleration = -650

        square = 2 * acceleration * (z - displacement) + velocity ** 2
        return press + (math.sqrt(square) - velocity) / acceleration

    def get_jump_time(self) -> float:
        target_height = clamp(self.intercept.position[2] - Ball.radius, 0, 220)

        time = self.get_time_to_z(target_height)
        return clamp(time, 0.05, 0.9) + 0.05

    def configure_mechanics(self):
        super().configure_mechanics()

        self.dodge.car = self.car
        additional_jump = self.get_jump_time()
        self.dodge.duration = additional_jump
        self.arrive.additional_shift = additional_jump * norm(self.car.velocity) * 0.5
        self.arrive.lerp_t = 0.58


    def step(self, dt):
        if self.dodging:
            self.dodge.direction = vec2(ground_direction(self.car, self.intercept))
            self.dodge.step(dt)
            self.controls = self.dodge.controls
        else:
            super().step(dt)
            if self.arrive.time - self.car.time < self.dodge.duration + self.predodge_time:

                car_speed = norm(self.car.velocity)

                if angle_to(self.car, self.get_offset_target()) < 0.1 or car_speed < 500:
                    self.dodging = True
                    self.dodge.direction = vec2(self.get_hit_direction())
                elif car_speed > 800:
                    self.controls.throttle = -1
                    # self.finished = True
        self.finished = self.finished or self.dodge.finished

    def render(self, draw: DrawingTool):
        draw.color(draw.cyan)
        draw.triangle(self.intercept.position, self.get_hit_direction())
        Strike.render(self, draw)