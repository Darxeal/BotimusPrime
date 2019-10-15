from maneuvers.kit import *


class Drive(Maneuver):

    def __init__(self, car):
        super().__init__(car)

        self.target_pos: vec3 = None
        self.target_speed: float = 2300
        self.backwards: bool = False
        self.drive_on_walls = True

    def step(self, dt):
        target = self.target_pos

        # dont try driving outside the arena
        target = Arena.clamp(target, 100)

        # smoothly escape goal
        if abs(self.car.position[1]) > Arena.size[1] - 50:
            target = Arena.clamp(target, 200)
            target[0] = signclamp(target[0], 700)

        if not self.drive_on_walls:
            if self.car.position[2] > 300:
                target = ground(self.car)

        local_target = local(self.car, target)


        if self.backwards:
            local_target[0] *= -1
            local_target[1] *= -1

        #steering
        phi = math.atan2(local_target[1], local_target[0])
        self.controls.steer = clamp11(2.5 * phi)

        #powersliding
        if abs(phi) > 1.4 and self.car.position[2] < 200 and norm(ground(local_target)) < 3000:
            self.controls.handbrake = 1
        else:
            self.controls.handbrake = 0

        # forward velocity
        vf = dot(self.car.velocity, self.car.forward())
        if self.backwards:
            vf *= -1

        #speed controller
        if vf < self.target_speed:
            self.controls.throttle = 1.0
            if self.target_speed > 1400 and vf < 2250 and self.target_speed - vf > 50:
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
        if abs(phi) > 0.8:
            self.controls.boost = 0

        #finish when close
        if distance(self.car, self.target_pos) < 100:
            self.finished = True
            


    def render(self, draw: DrawingTool):
        if self.target_pos:
            draw.color(draw.cyan)
            draw.crosshair(self.target_pos, 50)
            target_direction = direction(self.car.position, self.target_pos)
            draw.triangle(self.car.position + target_direction * 200, target_direction, up=self.car.up())
        
        # if self.car.on_ground:
        #     self.render_speedometer(draw, vec3(60, 50, 0))
        #     self.render_speedometer(draw, vec3(60, -50, 0))

    def render_speedometer(self, draw: DrawingTool, OFFSET: vec3):
        HALF_WIDTH = 8
        HALF_LENGTH = 50

        draw.color(draw.cyan)
        speed_bar = [
            world(self.car, vec3(-HALF_LENGTH, -HALF_WIDTH, 0) + OFFSET),
            world(self.car, vec3(-HALF_LENGTH,  HALF_WIDTH, 0) + OFFSET),
            world(self.car, vec3( HALF_LENGTH,  HALF_WIDTH, 0) + OFFSET),
            world(self.car, vec3( HALF_LENGTH, -HALF_WIDTH, 0) + OFFSET)
        ]
        draw.cyclic_polyline(speed_bar)

        # target speed
        mapped_speed = interpolate(self.target_speed, 0, 2300, -HALF_LENGTH, HALF_LENGTH)
        draw.color(draw.pink)
        draw.line(
            world(self.car, vec3(mapped_speed, -HALF_WIDTH, 0) + OFFSET),
            world(self.car, vec3(mapped_speed,  HALF_WIDTH, 0) + OFFSET)
        )
        draw.string(world(self.car, vec3(mapped_speed, -HALF_WIDTH, 0) + OFFSET), self.target_speed)

        # current speed
        speed = norm(self.car.velocity)
        mapped_speed = interpolate(speed, 0, 2300, -HALF_LENGTH, HALF_LENGTH)
        draw.color(draw.lime)
        draw.line(
            world(self.car, vec3(mapped_speed, -HALF_WIDTH, 0) + OFFSET),
            world(self.car, vec3(mapped_speed,  HALF_WIDTH, 0) + OFFSET)
        )
        draw.string(world(self.car, vec3(mapped_speed, -HALF_WIDTH, 0) + OFFSET), speed)


        
        