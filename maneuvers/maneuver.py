from dataclasses import dataclass

from rlutilities.simulation import Input, Car
from tools.announcer import Announcer
from tools.drawing import DrawingTool


@dataclass
class PushToStackException(Exception):
    pushed_maneuver: "Maneuver"


class Maneuver:
    def __init__(self, car):
        self.car: Car = car
        self.controls: Input = Input()
        self.finished: bool = False

        # self.uninterruptible_subaction: Optional[Maneuver] = None

    def expire(self, reason: str = None):
        if not self.finished and reason:
            self.announce(f"expiring: {reason}")
        self.finished = True

    def push(self, maneuver: "Maneuver"):
        raise PushToStackException(maneuver)

    def step(self, dt: float):
        raise NotImplementedError

    def interruptible(self) -> bool:
        return True

    def render(self, draw: DrawingTool):
        pass

    def announce(self, message: str):
        Announcer.announce(f"[{type(self).__name__}] {message}", slowmo=True)

    def explain(self, message: str, slowmo=False):
        Announcer.explain(f"[{type(self).__name__}] {message}", slowmo=slowmo)
