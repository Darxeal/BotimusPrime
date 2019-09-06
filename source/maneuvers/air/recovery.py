from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive

class Recovery(Maneuver):
    '''
    Wrapper for RLU recovery (in AerialTurn).
    Not actually used by Botimus, FastRecovery is better.
    '''
    def __init__(self, car: Car):
        super().__init__(car)

        self.turn = AerialTurn(car)

    def step(self, dt):
        self.turn.step(dt)
        self.controls = self.turn.controls
        self.controls.throttle = 1 # in case we're turtling
        self.finished = self.car.on_ground