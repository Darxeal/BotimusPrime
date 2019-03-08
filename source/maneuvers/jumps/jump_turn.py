from maneuvers.kit import *


class JumpTurn(Maneuver):
    def __init__(self, car: Car, target_direction: vec3):
        super().__init__(car)
        
        self.target_direction = target_direction

        self.jump = Jump(0.05)
        self.turn = AerialTurn(car, look_at(ground(target_direction)))
        self.action = self.jump

    def step(self, dt):
        if self.jump.finished:
            self.action = self.turn
        self.action.step(dt)
        self.controls = self.action.controls
        self.finished = self.jump.finished and self.car.on_ground