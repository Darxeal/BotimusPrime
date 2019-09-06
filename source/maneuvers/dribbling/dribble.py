from maneuvers.kit import *

from maneuvers.dribbling.carry import Carry

class Dribble(Maneuver):
    '''
    Carry the ball on roof, and flick it if an opponent is close or
    if fast enough and facing the target.
    '''
    def __init__(self, car: Car, info: GameInfo, target: vec3):
        super().__init__(car)

        self.target = target
        self.info = info

        self.carry = Carry(car, info.ball, target)
        self.flick = AirDodge(car, 0.15, info.ball.pos)
        self.flicking = False

    def step(self, dt):
        if not self.flicking:
            self.carry.step(dt)
            self.controls = self.carry.controls
            self.finished = self.carry.finished
            car = self.car
            
            # check if it's a good idea to flick
            dir_to_target = direction(ground(car.pos), ground(self.target))
            if (
                distance(car.pos, self.info.ball.pos) < 150
                and distance(ground(car.pos), ground(self.info.ball.pos)) < 80
                and dot(car.forward(), dir_to_target) > 0.9
                and norm(car.vel) > distance(car, self.target) / 4
                and norm(car.vel) > 1500
                and dot(dir_to_target, direction(ground(car.pos), ground(self.info.ball.pos))) > 0.95
            ):
                self.flicking = True
            
            # flick if opponent is close
            for opponent in self.info.opponents:
                if distance(opponent, car) < max(800, norm(opponent.vel)) and distance(car.pos, self.info.ball.pos) < 350:
                    self.flicking = True
        else:
            self.flick.step(dt)
            self.controls = self.flick.controls
            self.finished = self.flick.finished



    def render(self, draw: DrawingTool):
        if not self.flicking:
            self.carry.render(draw)
            