from rlutilities.simulation import Input, Car
from tools.announcer import Announcer
from tools.drawing import DrawingTool


class Maneuver:
    def __init__(self, car):
        self.car: Car = car
        self.controls: Input = Input()
        self.finished: bool = False

    def expire(self, reason: str):
        if not self.finished:
            self.announce(f"expiring: {reason}")
        self.finished = True

    def step(self, dt: float):
        pass

    def interruptible(self) -> bool:
        return True

    def render(self, draw: DrawingTool):
        pass

    def announce(self, message: str):
        Announcer.announce(f"[{type(self).__name__}] {message}", slowmo=True)

    def explain(self, message: str, slowmo=False):
        Announcer.announce(f"[{type(self).__name__}] {message}", slowmo=slowmo)
