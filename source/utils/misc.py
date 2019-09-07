import math
from RLUtilities.LinearAlgebra import vec3, normalize, dot, norm
from RLUtilities.Simulation import Car, Ball

from utils.vector_math import *
from utils.math import *

def estimate_max_car_speed(car: Car, time_left=0):
    return clamp(max(norm(car.vel), 1300) + car.boost * 50 * time_left, 1400 + math.floor(time_left * 0.5) * 500, 2300)

def estimate_time(car: Car, target, speed, dd=1) -> float:
    dist = distance(car, target)
    travel = dist / speed
    turning = angle_between(car.forward() * dd, direction(car, target)) / math.pi * 1.5
    turning **= 2
    acceleration = (speed * dd - dot(car.vel, car.forward())) / 2100 * dd
    return travel + acceleration * 0.4 + turning * 0.4

def turn_radius(speed: float) -> float:
    spd = clamp(speed, 0, 2300)
    return 156 + 0.1*spd + 0.000069*spd**2 + 0.000000164*spd**3 + -5.62E-11*spd**4

def turning_speed(radius: float) -> float:
    return 10.219 * radius - 1.75404E-2 * radius**2 + 1.49406E-5 * radius**3 - 4.486542E-9 * radius**4 - 1156.05


def on_team_half(team: int, pos: vec3):
    team_sign = 1 if team else -1
    return sign(pos[1]) == team_sign

def align(pos: vec3, ball: Ball, goal: vec3):
    return max(
        dot(ground_direction(pos, ball), ground_direction(ball, goal)),
        dot(ground_direction(pos, ball), ground_direction(ball, goal + vec3(800, 0, 0))),
        dot(ground_direction(pos, ball), ground_direction(ball, goal - vec3(800, 0, 0)))
    )

def nearest_point(pos: vec3, points: list):
    best_dist = 9999999
    best_point = None
    for point in points:
        dist = distance(pos, point)
        if dist < best_dist:
            best_dist = dist
            best_point = point
    return best_point

def furthest_point(pos: vec3, points: list):
    best_dist = 0
    best_point = None
    for point in points:
        dist = distance(pos, point)
        if dist > best_dist:
            best_dist = dist
            best_point = point
    return best_point