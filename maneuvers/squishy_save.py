from maneuvers.driving.travel import Travel
from maneuvers.jumps.jump import Jump
from maneuvers.jumps.wavedash_recovery import WavedashRecovery
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3, norm, look_at, vec2, sgn
from rlutilities.mechanics import Drive, Reorient, Dodge
from rlutilities.simulation import Car, Ball
from tools.drawing import DrawingTool
from tools.game_info import GameInfo
from tools.math import abs_clamp
from tools.vector_math import ground, angle_to, direction


class SquishySave(Maneuver):
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        target = vec3(info.my_goal.center)
        target.y *= 0.95
        self.drive_to_goal = Travel(car, target=target)
        self.drive_to_goal.finish_distance = 1000

        self.drive_inside_goal = Drive(car)
        self.reorient = Reorient(car)

    def step(self, dt: float):
        if not self.drive_to_goal.finished:
            self.drive_to_goal.step(dt)
            self.controls = self.drive_to_goal.controls
            return

        self.info.predict_ball(duration=3.0)
        about_to_get_scored_on = self.info.my_goal.inside(self.info.ball_predictions[-1].position)

        target = ground(self.info.my_goal.center)
        if self.car.position.z < 100:
            target.y = 7000 * sgn(target.y)
            remaining_distance = 1000 + (7000 - abs(self.car.position.y))
        else:
            target.y *= 0.5
            target.z = 9999
            remaining_distance = max(0.0, abs(self.car.position.y) - 5120) * 2.0

        if about_to_get_scored_on:
            self.explain("About to get scored on", slowmo=True)
            target.x = self.info.ball_predictions[-1].position.x
            time_left = self.info.ball_predictions[-1].time - self.car.time
            self.drive_inside_goal.speed = remaining_distance / time_left
        else:
            self.drive_inside_goal.speed = 1500
            target.x = abs_clamp(self.info.ball.position.x, 1000)

        if self.car.position.z < 50 and norm(self.car.velocity) > 1500 and angle_to(self.car, target) > 0.5:
            self.drive_inside_goal.speed = 1000
            self.explain("Slowing down to turn faster", slowmo=True)

        self.drive_inside_goal.target = target
        self.drive_inside_goal.step(dt)
        self.controls = self.drive_inside_goal.controls

        if self.car.position.z > 550:
            self.finished = True
            self.announce("Slowmo babyyyy")
            if about_to_get_scored_on:
                self.push([Jump(self.car, 0.2), SquishySaveFinalDodge(self.car, self.info.ball)])
            else:
                self.push([Jump(self.car, 0.2), WavedashRecovery(self.car, self.info.ball.position)])

    def interruptible(self) -> bool:
        return not self.drive_to_goal.finished

    def render(self, draw: DrawingTool):
        pass


class SquishySaveFinalDodge(Maneuver):
    def __init__(self, car: Car, ball: Ball):
        super().__init__(car)
        self.ball = ball

        self.reorient = Reorient(car)
        self.dodge = Dodge(car)
        self.dodge.jump_duration = 0
        self.dodge.delay = 0
        self.dodging = False

    def step(self, dt: float):
        if self.dodging:
            self.dodge.step(dt)
            self.controls = self.dodge.controls
            self.finished = self.dodge.finished
        else:
            self.reorient.target_orientation = look_at(direction(self.car, self.ball), vec3(0, 0, -1))
            self.reorient.step(dt)
            self.controls = self.reorient.controls
            if self.car.position.z + self.car.velocity.z * 0.2 < self.ball.position.z + self.ball.velocity.z * 0.2:
                self.dodge.direction = vec2(direction(self.car, self.ball))
                self.dodging = True

    def interruptible(self) -> bool:
        return False
