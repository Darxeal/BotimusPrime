import math
from typing import List

from rlutilities.mechanics import Aerial
from rlutilities.simulation import Car, Ball


class AirToAirIntercept:
    def __init__(self, car: Car, ball_predictions: List[Ball]):
        self.car: Car = car
        self.ball: Ball = None
        self.is_viable = True

        test_aerial = Aerial(car)
        for i in range(0, len(ball_predictions)):
            ball_slice = ball_predictions[i]
            test_aerial.target = ball_slice.position
            test_aerial.arrival_time = ball_slice.time
            if test_aerial.is_viable():
                self.ball = ball_slice
                break

        # if no slice is found, use the last one
        if self.ball is None:
            if not ball_predictions:
                self.ball = Ball()
                self.ball.time = math.inf
            else:
                self.ball = ball_predictions[-1]
            self.is_viable = False

        self.time = self.ball.time
        self.position = self.ball.position
