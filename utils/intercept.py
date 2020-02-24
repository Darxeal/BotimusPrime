from rlutilities.simulation import Car, Ball
from rlutilities.mechanics import Aerial
from rlutilities.linear_algebra import look_at

from utils.vector_math import *
from utils.math import *
from utils.misc import *


class Intercept:
    def __init__(self, car: Car, ball_predictions, predicate: callable = None, backwards=False):
        self.ball: Ball = None
        self.is_viable = True

        #find the first reachable ball slice that also meets the predicate
        speed = 1000 if backwards else estimate_max_car_speed(car)
        # for ball in ball_predictions:
        for ball in ball_predictions:
            if estimate_time(car, ball.position, speed, -1 if backwards else 1) < ball.time - car.time \
            and (predicate is None or predicate(car, ball)):
                self.ball = ball
                break

        #if no slice is found, use the last one
        if self.ball is None:
            if not ball_predictions:
                self.ball = Ball()
            else:
                self.ball = ball_predictions[-1]
            self.is_viable = False

        self.time = self.ball.time
        self.ground_pos = ground(self.ball.position)
        self.position = self.ball.position
