from maneuvers.driving.drive import Drive
from maneuvers.jumps.air_dodge import AirDodge
from maneuvers.jumps.speed_flip import SpeedFlip
from maneuvers.kickoffs.kickoff import Kickoff
from maneuvers.maneuver import Maneuver
from rlutilities.linear_algebra import vec3, norm, sgn, look_at
from rlutilities.mechanics import AerialTurn
from rlutilities.simulation import Car
from utils.drawing import DrawingTool
from utils.game_info import GameInfo
from utils.vector_math import distance, local


class SpeedFlipKickoff(Kickoff):
    def __init__(self, car: Car, info: GameInfo):
        super().__init__(car, info)
        self.drive.target_pos = self.info.my_goal.center * 0.07

    def step(self, dt: float):
        car = self.car
        if self.phase == 1:
            if norm(car.velocity) > 1100:
                self.action = SpeedFlip(car, right_handed=local(car, self.info.ball.position)[1] < 0)
                self.phase = 2

        if self.phase == 2:
            if self.action.finished:
                self.finished = True

        super().step(dt)
