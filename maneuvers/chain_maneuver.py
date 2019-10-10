from maneuvers.kit import *
from typing import List


class ChainManeuver(Maneuver):

    def __init__(self, car: Car, chainable_maneuvers: List[ChainableManeuver], final_maneuver: Maneuver):
        super().__init__(car)

        assert chainable_maneuvers
        self.queue: List[ChainableManeuver] = chainable_maneuvers
        self.final_maneuver: Maneuver = final_maneuver
        self.current_maneuver = chainable_maneuvers[0]

    def resimulate_chainable_maneuvers(self):
        n = len(self.queue) - 1
        for i in range(n):
            self.queue[i+1].car = self.queue[i].simulate()
        self.final_maneuver.car = self.queue[n].simulate()

    def step(self, dt):
        if self.current_maneuver != self.final_maneuver:
            # okay so this is actually needed only for rendering,
            # but I'm keeping it in step() to avoid accidentally having
            # different behaviours when rendering is turned on and off
            self.resimulate_chainable_maneuvers()

        self.current_maneuver.step(dt)
        self.controls = self.current_maneuver.controls

        if self.current_maneuver.finished:
            if self.current_maneuver == self.final_maneuver:
                self.finished = True
            else:
                self.queue.pop(0)
                if self.queue:
                    self.current_maneuver = self.queue[0]
                else:
                    self.current_maneuver = self.final_maneuver
                self.current_maneuver.car = self.car

    def render(self, draw: DrawingTool):
        for maneuver in self.queue:
            maneuver.render(draw)

            transition_car = maneuver.simulate()
            draw.color(draw.cyan)
            draw.car_shadow(transition_car)
            
        self.final_maneuver.render(draw)