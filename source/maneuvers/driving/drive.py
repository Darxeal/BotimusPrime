from maneuvers.kit import *


class Drive(Maneuver):

    def __init__(self, car, target_pos: vec3 = vec3(0, 0, 0), target_speed: float = 0, backwards: bool = False):
        super().__init__(car)

        self.target_pos = target_pos
        self.target_speed = target_speed
        self.backwards = backwards
        self.drive_on_walls = False

    def step(self, dt):
        target = self.target_pos

        # dont try driving outside the arena
        target = Arena.clamp(target, 100)

        # smoothly escape goal
        if abs(self.car.pos[1]) > Arena.size[1] - 50:
            target = Arena.clamp(target, 200)
            target[0] = signclamp(target[0], 700)

        if not self.drive_on_walls:
            if self.car.pos[2] > 300:
                target = ground(self.car)

        local_target = local(self.car, target)


        if self.backwards:
            local_target[0] *= -1
            local_target[1] *= -1

        #steering
        phi = math.atan2(local_target[1], local_target[0])
        self.controls.steer = clamp11(2.5 * phi)

        #powersliding
        if abs(phi) > 1.5 and self.car.pos[2] < 200:
            self.controls.handbrake = 1
        else:
            self.controls.handbrake = 0

        # forward velocity
        vf = dot(self.car.vel, self.car.forward())
        if self.backwards:
            vf *= -1

        #speed controller
        if vf < self.target_speed:
            self.controls.throttle = 1.0
            if self.target_speed > 1400 and vf < 2250:
                self.controls.boost = 1
            else:
                self.controls.boost = 0
        else:
            if (vf - self.target_speed) > 200:  # 75
                self.controls.throttle = -1.0
            else:
                if self.car.up()[2] > 0.85:
                    self.controls.throttle = 0.0
                else:
                    self.controls.throttle = 0.01
            self.controls.boost = 0

        #backwards driving
        if self.backwards:
            self.controls.throttle *= -1
            self.controls.steer *= -1
            self.controls.boost = 0
            self.controls.handbrake = 0

        #dont boost if not facing target
        if abs(phi) > 0.3:
            self.controls.boost = 0

        #finish when close
        if distance(self.car, self.target_pos) < 100:
            self.finished = True
            


    def render(self, draw: DrawingTool):
        draw.color(draw.cyan)
        draw.square(self.target_pos, 50)
        target_direction = direction(self.car.pos, self.target_pos)
        draw.triangle(self.car.pos + target_direction * 150, target_direction, up=self.car.up())
        