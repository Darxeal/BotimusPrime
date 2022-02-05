from maneuvers.driving.drive import Drive
from maneuvers.driving.stop import Stop
from maneuvers.driving.travel import Travel
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Car
from tools.arena import Arena
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.vector_math import nearest_point, farthest_point, ground_distance, ground_direction, ground, angle_to


class GeneralDefense(Maneuver):
    """
    First, attempt to rotate on the far side, and when far away enough from the target (usually the ball),
    turn around to face it. If already far enough and facing the target, just stop and wait.
    This state expires after a short amount of time, so we can look if there's something better to do. If not,
    it can be simply instantiated again.
    """

    DURATION = 0.5

    def __init__(self, car: Car, info: GameInfo, face_target: vec3, distance_from_target: float, force_nearest=False):
        super().__init__(car)

        self.info = info
        self.face_target = face_target

        dist = min(distance_from_target, ground_distance(face_target, self.info.my_goal.center) - 50)
        target_pos = ground(face_target) + ground_direction(face_target, self.info.my_goal.center) * dist

        near_goal = abs(car.position[1] - info.my_goal.center[1]) < 3000
        side_shift = 400 if near_goal else 1800
        points = target_pos + vec3(side_shift, 0, 0), target_pos - vec3(side_shift, 0, 0)
        target_pos = nearest_point(face_target, points) if near_goal or force_nearest else farthest_point(face_target,
                                                                                                          points)
        if abs(face_target[0]) < 1000 or ground_distance(car, face_target) < 1000:
            target_pos = nearest_point(car.position, points)
        target_pos = Arena.clamp(target_pos, 500)

        self.travel = Travel(car, target_pos)
        self.travel.finish_distance = 800 if near_goal else 1500
        self.drive = Drive(car)
        self.stop = Stop(car)

        self.start_time = car.time

    def interruptible(self) -> bool:
        return self.travel.interruptible()

    def step(self, dt):
        if self.travel.finished:
            # turn around to face the target direction
            if angle_to(self.car, self.face_target) > 0.3:
                self.drive.target_pos = self.face_target
                self.drive.target_speed = 1000
                self.drive.step(dt)
                self.controls = self.drive.controls
                self.controls.handbrake = False
                self.explain("Turning towards target.")
            else:
                self.stop.step(dt)
                self.controls = self.stop.controls

        else:
            self.travel.step(dt)
            self.controls = self.travel.controls

        # don't waste boost during downtime
        if self.car.boost < 100 and ground_distance(self.car, self.travel.target) < 4000:
            self.controls.boost = False
            self.explain("Saving boost.")

        self.finished = self.travel.driving and self.car.time > self.start_time + self.DURATION

    def render(self, draw: DrawingTool):
        self.travel.render(draw)
