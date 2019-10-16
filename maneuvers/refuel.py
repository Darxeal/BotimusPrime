from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive


class Refuel(Maneuver):
    def __init__(self, car: Car, info: GameInfo, target: vec3):
        super().__init__(car)
        self.info = info
        self.target = target

        pos = (target + car.position * 2 + info.my_goal.center * 2) / 5
        self.arrive = Arrive(car)
        self.pad = self.nearest_boostpad(pos)
        self.arrive.target = self.pad.position
        self.arrive.target_direction = ground_direction(self.pad.position, target)
        self.arrive.lerp_t = 0.4
        self.arrive.arena_clamp = Arena.size[0] - abs(self.pad.position[0])

    def nearest_boostpad(self, pos: vec3) -> Pad:
        best_pad = None
        best_dist = 9999
        for pad in self.info.large_boost_pads:
            if pad.is_full_boost:
                dist = ground_distance(pos, pad.position)
                time = self.arrive.travel.estimate_time_to(pad.position)
                if (
                    (pad.is_active or pad.timer < time)
                    and dist < best_dist
                ):
                    best_pad = pad
                    best_dist = dist
        return best_pad

    def step(self, dt):
        self.arrive.step(dt)
        self.controls = self.arrive.controls

        if distance(self.car, self.pad) < norm(self.car.velocity) * 0.2:
            if angle_to(self.car, self.target) > 1.0:
                if norm(self.car.velocity) > 1000:
                    self.controls.throttle = -1
        
        self.finished = (
            not self.pad.is_active
            or self.car.boost > 99
            or ground_distance(self.pad.position, self.car.position) < 200
        )

    def render(self, draw: DrawingTool):
        self.arrive.render(draw)