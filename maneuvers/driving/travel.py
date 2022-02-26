from maneuvers.driving.drive import Drive
from maneuvers.jumps.half_flip import HalfFlip
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3, norm, dot, vec2, xy, normalize
from rlutilities.mechanics import Wavedash, Dodge
from rlutilities.simulation import Car, Game
from tools.drawing import DrawingTool
from tools.vector_math import ground, ground_distance, angle_to, direction, ground_direction


class TravelDodge(Maneuver):
    def __init__(self, car: Car, target: vec3):
        super().__init__(car)
        self.dodge = Dodge(car)
        self.dodge.direction = vec2(direction(car, target))
        self.dodge.jump_duration = 0.05

    def step(self, dt: float):
        self.dodge.step(dt)
        self.controls = self.dodge.controls
        if self.dodge.finished and self.car.on_ground:
            self.expire()

    def interruptible(self) -> bool:
        return False

    def render(self, draw: DrawingTool):
        draw.color(draw.white)
        draw.vector(self.car.position, self.car.velocity)


class TravelWavedash(Maneuver):
    def __init__(self, car: Car, target: vec3):
        super().__init__(car)
        self.wavedash = Wavedash(car)
        self.wavedash.direction = vec2(direction(car, target))

    def step(self, dt: float):
        self.wavedash.step(dt)
        self.controls = self.wavedash.controls
        if self.wavedash.finished:
            self.expire()

    def interruptible(self) -> bool:
        return False

    def render(self, draw: DrawingTool):
        draw.color(draw.white)
        draw.vector(self.car.position, self.car.velocity)


class Travel(Maneuver):
    """
    Get to a location fast, using dodges, wavedashes and maybe a halfflip to gain speed.
    """

    DODGE_DURATION = 1.5
    HALFFLIP_DURATION = 2
    WAVEDASH_DURATION = 1.45

    def __init__(self, car: Car, target: vec3 = vec3(0, 0, 0), waste_boost=False, allow_backwards=False):
        super().__init__(car)

        self.target = target
        self.waste_boost = waste_boost
        self.finish_distance = 500

        self._time_on_ground = 0
        self.driving = True

        self.drive = Drive(car, self.target, 2300)

    def step(self, dt):
        car = self.car
        target = ground(self.target)

        car_speed = norm(car.velocity)
        time_left = (ground_distance(car, target) - self.finish_distance) / max(car_speed + 500, 1400)
        forward_speed = dot(car.forward(), car.velocity)

        if car.on_ground:
            self.drive.target_pos = target
            self._time_on_ground += dt

            # check if it's a good idea to dodge, wavedash or halfflip
            if (
                    self._time_on_ground > 0.2
                    and car.position.z < 100
                    and car_speed < 2000
                    and angle_to(car, target, backwards=forward_speed < 0) < 0.1
                    and dot(normalize(xy(car.velocity)), ground_direction(car, target)) > 0.9
                    and Game.gravity.z < -500  # don't dodge in low gravity
            ):
                # if going forward, use a dodge or a wavedash
                if forward_speed > 0:
                    use_boost_instead = self.waste_boost and car.boost > 20

                    if car_speed > 1200 and not use_boost_instead:
                        if time_left > self.DODGE_DURATION:
                            self._time_on_ground = 0
                            self.push(TravelDodge(car, target))

                        elif time_left > self.WAVEDASH_DURATION:
                            self._time_on_ground = 0
                            self.push(TravelWavedash(car, target))

                # if going backwards, use a halfflip
                elif time_left > self.HALFFLIP_DURATION and car_speed > 800:
                    self._time_on_ground = 0
                    self.push(HalfFlip(car, self.waste_boost and time_left > 3))

        self.drive.step(dt)
        self.controls = self.drive.controls

        if ground_distance(car, target) < self.finish_distance:
            self.finished = True

    def render(self, draw: DrawingTool):
        self.drive.render(draw)

        draw.color(draw.orange)
        draw.crosshair(self.target)
