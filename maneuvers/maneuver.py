from rlbot.utils.logging_utils import get_logger

from rlutilities.simulation import Input, Car
from tools.drawing import DrawingTool


class Maneuver:
    def __init__(self, car):
        self.car: Car = car
        self.controls: Input = Input()
        self.finished: bool = False

        self.logger = get_logger(type(self).__name__)

    def expire(self, reason: str):
        self.finished = True
        self.logger.debug(f"Aborting: {reason}")

    def step(self, dt: float):
        pass

    def interruptible(self) -> bool:
        return True

    def render(self, draw: DrawingTool):
        pass
