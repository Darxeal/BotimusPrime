from dataclasses import dataclass
from typing import List, Tuple

from rlutilities.simulation import Input, Car
from tools.announcer import Announcer
from tools.drawing import DrawingTool


@dataclass
class PushToStackException(Exception):
    pushed_maneuver: "Maneuver"


class Maneuver:
    def __init__(self, car: Car):
        self.car: Car = car
        self.controls: Input = Input()
        self.finished: bool = False

    def step(self, dt: float):
        raise NotImplementedError

    def interruptible(self) -> bool:
        return True

    def render(self, draw: DrawingTool):
        pass

    def expire(self, reason: str = None):
        if not self.finished and reason:
            self.announce(f"expiring: {reason}")
        self.finished = True

    def push(self, maneuver: "Maneuver"):
        raise PushToStackException(maneuver)

    def announce(self, message: str):
        Announcer.announce(f"[{type(self).__name__}] {message}", slowmo=True)

    def explain(self, message: str, slowmo=False):
        Announcer.explain(f"[{type(self).__name__}] {message}", slowmo=slowmo)

    def explainable_and(self, conditions: List[Tuple[str, bool]], slowmo=False) -> bool:
        for name, cond in conditions:
            color = DrawingTool.lime if cond else DrawingTool.red
            Announcer.explain(f"[{type(self).__name__}] - {name}", slowmo, color)
        return all(cond for name, cond in conditions)
