from maneuvers.strikes.dodge_strike import DodgeStrike
from maneuvers.strikes.ground_strike import GroundStrike
from maneuvers.strikes.strike import Strike
from utils.game_info import Goal
from maneuvers.kit import *


class Shot(Strike):
    def __init__(self, target_goal: Goal):
        self.target_goal: Goal = target_goal
        self.aim_pos: vec3 = None

    def get_target_direction(self):
        self.aim_pos = self.target_goal.center
        self.aim_pos[0] = signclamp(self.intercept.position[0], self.target_goal.WIDTH / 2 - 300)
        return ground_direction(self.intercept, self.aim_pos)

    def render(self, draw: DrawingTool):
        draw.color(draw.pink)
        draw.crosshair(self.aim_pos)


class DodgeShot(DodgeStrike, Shot):

    def __init__(self, car: Car, ball: Ball, target_goal: Goal):
        DodgeStrike.__init__(self, car, ball)
        Shot.__init__(self, target_goal)

    def render(self, draw):
        Shot.render(self, draw)
        DodgeStrike.render(self, draw)


class GroundShot(GroundStrike, Shot):

    def __init__(self, car: Car, ball: Ball, target_goal: Goal):
        GroundStrike.__init__(self, car, ball)
        Shot.__init__(self, target_goal)

    def render(self, draw):
        Shot.render(self, draw)
        DodgeStrike.render(self, draw)