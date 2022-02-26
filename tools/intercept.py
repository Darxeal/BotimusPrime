import math
from typing import List, Callable

from data.acceleration_lut import BOOST, THROTTLE
from rlutilities.linear_algebra import angle_between, dot
from rlutilities.simulation import Car, Ball, BoostPad, BoostPadState
from tools.vector_math import direction, ground_distance


def find_intercept(predictions: List[Ball], predicate: Callable[[Ball], bool]) -> Ball:
    for ball in predictions[1::3]:
        if predicate(ball):
            return ball
    return predictions[-1]


class Intercept(Ball):
    def __init__(self, car: Car, ball: Ball):
        super().__init__(ball)
        self.car = car


def intercept_estimate(car: Car, predictions: List[Ball]) -> Intercept:
    ball = find_intercept(predictions, lambda ball: estimate_time(car, ball.position) < ball.time - car.time)
    return Intercept(car, ball)


def estimate_time(car: Car, target, dd=1, max_accelerate_time=math.inf) -> float:
    # turning_radius = 1 / Drive.max_turning_curvature(norm(car.velocity) + 500)
    # turning = angle_between(car.forward() * dd, direction(car, target)) * turning_radius / 1000
    # if turning < 0.5: turning = 0
    # turning *= 1.2
    turning = angle_between(car.forward() * dd, direction(car, target)) * 0.3
    if turning < 0.2: turning = 0
    turning = min(turning, 0.8)

    dist = max(ground_distance(car, target) - 100, 1)
    speed = dot(car.velocity, car.forward())

    time = 0
    result = None
    if car.boost > 0 and dd > 0 and max_accelerate_time > 0:
        boost_time = car.boost / 33.33
        result = BOOST.simulate_until_limit(speed, distance_limit=dist, time_limit=min(boost_time, max_accelerate_time))
        dist -= result.distance_traveled
        time += result.time_passed
        speed = result.speed_reached
        max_accelerate_time -= result.time_passed

    if dist > 0 and speed < 1410 and max_accelerate_time > 0:
        result = THROTTLE.simulate_until_limit(speed, distance_limit=dist, time_limit=max_accelerate_time)
        dist -= result.distance_traveled
        time += result.time_passed
        speed = result.speed_reached

    if speed == 0:
        return math.inf

    if result is None or not result.distance_limit_reached:
        time += dist / speed

    return time + turning


def pad_available_in_time(pad: BoostPad, car: Car) -> bool:
    return pad.state == BoostPadState.Available or estimate_time(car, pad) > pad.timer
