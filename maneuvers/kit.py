import math
from typing import List

# from rlutilities.mechanics import Dodge, AerialTurn
from rlutilities.linear_algebra import vec2, vec3, norm, normalize, look_at, angle_between, clip, cross, dot, sgn, xy, rotation, rotation_to_axis, rotation_to_euler, axis_to_rotation
from rlutilities.simulation import Game, Ball, Car, Input, Field, sphere, obb, ray

from utils.vector_math import *
from utils.math import *
from utils.misc import *
from utils.intercept import Intercept, AerialIntercept
from utils.arena import Arena
from utils.game_info import GameInfo, Goal, Pad
from utils.travel_plan import TravelPlan

from tools.drawing import DrawingTool


class Maneuver:

    def __init__(self, car: Car):
        self.car: Car = car
        self.controls: Input = Input()
        self.finished: bool = False

    def step(self, dt: float):
        raise NotImplementedError

    def render(self, draw: DrawingTool):
        pass

    def __str__(self):
        return str(type(self).__name__)


class ChainableManeuver(Maneuver):

    def __init__(self, car: Car):
        super().__init__(car)
        self.target: vec3 = None

    def viable(self) -> bool:
        raise NotImplementedError

    def simulate(self) -> Car:
        raise NotImplementedError
