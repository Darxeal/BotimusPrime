from maneuvers.driving.drive import Drive
from maneuvers.jumps.air_dodge import AirDodge
from maneuvers.kit import Maneuver
from rlutilities.linear_algebra import vec3, norm, sgn, look_at
from rlutilities.mechanics import AerialTurn
from rlutilities.simulation import Car
from utils.drawing import DrawingTool
from utils.game_info import GameInfo
from utils.vector_math import distance


class Kickoff(Maneuver):
    """
    Go straight for the ball, dodge in the middle and at the end
    """
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car)
        self.info = info

        target_pos = vec3(0, sgn(info.my_goal.center[1]) * 100, 0)
        self.drive = Drive(car, target_pos, 2300)

        self.action: Maneuver = self.drive
        self.phase = 1

    def step(self, dt):
        car = self.car

        if self.phase == 1:
            if norm(car.velocity) > 1300:
                self.phase = 2
                self.action = AirDodge(car, 0.05, car.position + car.velocity)

        if self.phase == 2:
            if car.on_ground and self.action.finished:
                self.action = self.drive
                self.phase = 3

        if self.phase == 3:
            if distance(car, self.info.ball) < norm(car.velocity) * 0.4:

                # detect if an opponent is going for kickoff
                is_opponent_going_for_kickoff = False
                for opponent in self.info.opponents:
                    if distance(self.info.ball, opponent) < 1500:
                        is_opponent_going_for_kickoff = True

                if is_opponent_going_for_kickoff:
                    self.phase = 4
                    self.action = AirDodge(car, 0.05, self.info.ball.position)
                else:
                    self.phase = "anti-fake-kickoff"
                    self.action = self.drive
        
        if self.phase == 4:
            if self.action.finished:
                self.action = AerialTurn(car)
                self.phase = 5

        if self.phase == 5:
            self.action.target = look_at(self.info.my_goal.center, vec3(0,0,1))
            self.action.controls.throttle = 1
            if car.on_ground:
                self.finished = True

        if self.phase == "anti-fake-kickoff":
            self.drive.target_pos = vec3(80, 0, 0)
            self.finished = self.info.ball.position[1] != 0

        self.action.step(dt)
        self.controls = self.action.controls

    def render(self, draw: DrawingTool):
        if hasattr(self.action, "render"):
            self.action.render(draw)
