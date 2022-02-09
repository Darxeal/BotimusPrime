from typing import List

from rlutilities.linear_algebra import vec3, norm
from tools.announcer import Announcer
from tools.game_info import GameInfo
from tools.vector_math import distance


class TeleportDetector:
    def __init__(self):
        self.prev_car_positions: List[vec3] = None
        self.prev_ball_pos: vec3 = None

    def teleport_happened(self, info: GameInfo) -> bool:
        flag = False
        if self.prev_car_positions is not None:
            if len(info.cars) == len(self.prev_car_positions):
                for car, prev_pos in zip(info.cars, self.prev_car_positions):
                    if distance(car, prev_pos) > norm(car.velocity) * info.time_delta * 2.0:
                        Announcer.announce("[TeleportDetector] Teleport happened.")
                        flag = True
                        break
            else:
                Announcer.announce("[TeleportDetector] Number of cars changed.")
                flag = True

        self.prev_car_positions = [vec3(car.position) for car in info.cars]
        self.prev_ball_pos = [vec3(info.ball.position)]
        return flag
