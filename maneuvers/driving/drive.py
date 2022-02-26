import math

from maneuvers.maneuver import Maneuver
from maneuvers.recovery import Recovery
from rlutilities.linear_algebra import vec3, dot, norm, sgn
from rlutilities.simulation import BoostPadType
from tools.arena import Arena
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.intercept import pad_available_in_time
from tools.math import abs_clamp, clamp11, clamp
from tools.vector_math import ground, local, ground_distance, distance, direction, world, angle_to


class Drive(Maneuver):

    def __init__(self, car, target_pos: vec3 = vec3(0, 0, 0), target_speed: float = 0, backwards: bool = False):
        super().__init__(car)

        self.target_pos = target_pos
        self.target_speed = target_speed
        self.backwards = backwards
        self.drive_on_walls = False
        self.detour_for_pads = True

        self.__changed_target = target_pos  # just for rendering

    def step(self, dt):
        target = self.target_pos

        # don't try driving outside the arena
        threshold = 100 if abs(target.y) > 5000 else 50
        if not Arena.inside(target, threshold):
            self.explain("Clamping target inside arena.")
            target = Arena.clamp(target, threshold)

        if not self.car.on_ground:
            self.announce("Not on ground!")
            self.push(Recovery(self.car))

        # smoothly escape goal
        if abs(self.car.position.y) > Arena.size.y - 50 and abs(self.car.position.x) < 1000:
            target = Arena.clamp(target, 200)
            target.x = abs_clamp(target.x, 700)
            self.explain("Escaping goal.")

        # escape walls
        if not self.drive_on_walls:
            seam_radius = 100 if abs(self.car.position.y) > Arena.size.y - 100 else 200
            if self.car.position.z > seam_radius and self.car.on_ground:
                target = (ground(self.car) * 4 + ground(self.target_pos)) / 5
                self.explain("Driving down wall.")

                # if self.explainable_and([
                #     ("distance from target", ground_distance(self.car, target) > 1500),
                #     ("low height", self.car.position.z < 800),
                #     ("good vel",
                #      norm(self.car.velocity) < 300 or self.car.velocity.z < -100 and norm(self.car.velocity) > 500),
                # ]):
                #     self.announce("Jumping off wall.")
                #     self.push([Jump(self.car, 0.1), WavedashRecovery(self.car, self.target_pos)])

        # picking up boost pads along the way
        if self.detour_for_pads:
            good_pads = []
            for pad in GameInfo.large_boost_pads + GameInfo.small_boost_pads:
                car_to_target = ground_distance(self.car, target)
                car_to_pad = ground_distance(self.car, pad)
                pad_to_target = ground_distance(pad, target)
                tolerance = 1.3 if pad.type == BoostPadType.Full else 1.1
                boost_threshold = 99 if pad.type == BoostPadType.Full else 50
                angle_threshold = (2500 - norm(self.car.velocity)) / 2500 * tolerance
                if (
                        angle_to(self.car, pad.position) < angle_threshold
                        and pad_to_target > 1000
                        and self.car.boost < boost_threshold
                        and car_to_pad + pad_to_target < car_to_target * tolerance
                        and ground_distance(self.car, pad) < 2000
                        and pad_available_in_time(pad, self.car)
                ):
                    good_pads.append(pad)
            if good_pads:
                self.explain("Detouring for a boostpad.")
                target = min(good_pads, key=lambda pad: distance(self.car, pad)).position

        self.__changed_target = target
        local_target = local(self.car, target)

        if self.backwards:
            local_target[0] *= -1
            local_target[1] *= -1

        # steering
        phi = math.atan2(local_target[1], local_target[0])
        self.controls.steer = clamp11(3.0 * phi)

        turn_radius = Drive.turn_radius(norm(self.car.velocity))
        local_turn_center = vec3(0, turn_radius * sgn(local_target.y), 0)

        if (
                not Arena.inside(world(self.car, local_turn_center))
                and abs(phi) > 1.0
                # and ground_distance(self.car, target) > 1000
                and abs(self.car.position.y) < Arena.size.y
        ):
            self.controls.steer *= -1
            self.explain("Turning other way to avoid wall", slowmo=True)

        target_speed = self.target_speed

        # powersliding
        self.controls.handbrake = 0
        if abs(phi) > 1.4:
            if (
                    self.car.position[2] < 300
                    and (ground_distance(self.car, target) < 1000 or not Arena.inside(self.car.position, 200))
                    # and dot(self.car.velocity, self.car.forward()) > 500
            ):
                self.controls.handbrake = 1
                self.explain("Powersliding")
            else:
                target_speed = min(target_speed, 1000)
                self.explain("Slowing down to turn faster")

        # slow down if target inside turn circle
        if ground_distance(local_target, local_turn_center) < turn_radius:
            target_speed = min(target_speed, 1000)
            self.explain("Slowing down (target inside turn circle)")

        # forward velocity
        vf = dot(self.car.velocity, self.car.forward())
        if self.backwards:
            vf *= -1

        # speed controller
        if vf < target_speed:
            self.controls.throttle = 1.0
            if target_speed > 1400 and vf < 2250 and target_speed - vf > 50:
                self.controls.boost = 1
            else:
                self.controls.boost = 0
        else:
            if (vf - target_speed) > 400:  # 75
                self.controls.throttle = -1.0
            elif (vf - target_speed) > 100:
                if self.car.up()[2] > 0.85:
                    self.controls.throttle = 0.0
                else:
                    self.controls.throttle = 0.01
            self.controls.boost = 0

        # backwards driving
        if self.backwards:
            self.controls.throttle *= -1
            self.controls.steer *= -1
            self.controls.boost = 0
            self.controls.handbrake = 0

        # don't boost if not facing target
        if abs(phi) > 0.3 and self.controls.boost:
            self.controls.boost = 0

        # finish when close
        if distance(self.car, self.target_pos) < 100:
            self.finished = True

    @staticmethod
    def turn_radius(speed: float) -> float:
        spd = clamp(speed, 0, 2300)
        return 156 + 0.1 * spd + 0.000069 * spd ** 2 + 0.000000164 * spd ** 3 + -5.62E-11 * spd ** 4

    def render(self, draw: DrawingTool):
        draw.color(draw.cyan)
        draw.square(self.target_pos, 50)

        if self.__changed_target is not self.target_pos:
            draw.square(self.__changed_target, 40)
            draw.vector(self.__changed_target, direction(self.__changed_target, self.target_pos) * 300)
            draw.vector(self.__changed_target, direction(self.__changed_target, self.car) * 300)

        target_direction = direction(self.car.position, self.__changed_target)
        draw.triangle(self.car.position + target_direction * 200, target_direction, up=self.car.up())
