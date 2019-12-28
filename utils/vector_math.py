from rlutilities.linear_algebra import vec3, norm, normalize, dot, cross, mat3, angle_between, inv, vec2, xy
from rlutilities.simulation import Car
from math import asin, atan2, sin, cos

def loc(obj) -> vec3:
    if hasattr(obj, "position"):
        return obj.position
    elif hasattr(obj, "x"):
        return vec3(obj.x, obj.y, obj.z)
    elif hasattr(obj, "X"):
        return vec3(obj.X, obj.Y, obj.Z)
    elif isinstance(obj, vec2):
        return vec3(obj)
    return obj

def ground(pos) -> vec3:
    pos = loc(pos)
    return vec3(pos[0], pos[1], 0)

def distance(obj1, obj2) -> float:
    return norm(loc(obj1) - loc(obj2))

def ground_distance(obj1, obj2) -> float:
    return norm(ground(obj1) - ground(obj2))

def direction(source, target) -> vec3:
    return normalize(loc(target) - loc(source))

def ground_direction(source, target) -> vec3:
    return normalize(ground(target) - ground(source))

def local(car: Car, pos) -> vec3:
    return dot(loc(pos) - car.position, car.orientation)

def world(car: Car, pos) -> vec3:
    return car.position + dot(car.orientation, loc(pos))

def angle_to(car: Car, target, backwards = False) -> float:
    return abs(angle_between(xy(car.forward()) * (-1 if backwards else 1), ground_direction(car.position, target)))

def facing(mat: mat3) -> vec3:
    return vec3(mat[0, 0], mat[1, 0], mat[2, 0])

def flip(vec: vec3, dimension: int) -> vec3:
    new = vec3(vec)
    new[dimension] *= -1
    return new

def circle_tangent(center: vec2, radius: float, point: vec2, sign: int) -> vec2:
    # http://jsfiddle.net/zxqCw/1/
    center = vec2(center)
    point = vec2(point)

    d = center - point
    dd = norm(d)
    
    assert radius < dd

    a = asin(radius / dd)
    b = atan2(d[1], d[0])

    t = b - a * sign
    return vec2(radius * sin(t) * sign, radius * -cos(t) * sign) + center