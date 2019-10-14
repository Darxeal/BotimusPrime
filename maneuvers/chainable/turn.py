from maneuvers.kit import *


class Turn(ChainableManeuver):

    def get_tangent_info(self):
        radius = turn_radius(norm(self.car.velocity))
        target_local = vec2(local(self.car, self.target))
        turn_sign = sgn(target_local[1])
        center_local = vec2(0, radius * turn_sign)

        tangent_local = circle_tangent(center_local, radius, target_local, -turn_sign)
        arc_angle = angle_between(center_local * (-1), tangent_local - center_local) * turn_sign
        return radius, center_local, tangent_local, arc_angle

    def viable(self):
        radius = turn_radius(norm(self.car.velocity))
        target_local = vec2(local(self.car, self.target))
        turn_sign = sgn(target_local[1])
        center_local = vec2(0, radius * turn_sign)
        return norm(target_local - center_local) > radius + 100

    def simulate(self) -> Car:
        radius, _, tangent_local, angle = self.get_tangent_info()
        tangent_point = world(self.car, tangent_local)
        arc_length = radius * abs(angle)
        speed = norm(self.car.velocity)

        copy = Car(self.car)
        copy.position = tangent_point
        copy.orientation = look_at(direction(copy.position, self.target), self.car.up())
        copy.time += arc_length / speed
        return copy

    def step(self, dt):
        if not self.viable():
            self.finished = True
            return

        self.controls.throttle = 1
        target_local = vec2(local(self.car, self.target))
        phi = math.atan2(target_local[1], target_local[0])
        self.controls.steer = sgn(phi)

        if abs(phi) < 0.1:
            print("Facing target, turn finished.")
            self.finished = True

    def render(self, draw: DrawingTool):
        radius, center_local, _, arc_angle = self.get_tangent_info()

        center = world(self.car, center_local)
        start_angle = rotation_to_euler(self.car.orientation)[1]
        start_angle -= math.pi * 0.5 * sgn(center_local[1])

        end_angle = start_angle + arc_angle
        if end_angle < start_angle:
            start_angle, end_angle = end_angle, start_angle

        draw.color(draw.white)
        draw.arc(center, radius, start_angle, end_angle)