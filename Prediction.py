import math
import time
from Unreal import Rotator, Vector3
from Objects import *
from Utils import * 
import numpy as np

#only the first function was actually used in Botimus
#the rest is just me trying to rewrite chip's ball
#prediction in python and failing horribly

def predict(num_of_steps) -> Vector3:
    dt = 1 / 60
    g = Vector3(0, 0, -650)

    v = ball.velocity
    av = ball.av
    loc = ball.location

    steps = []

    for i in range(0, num_of_steps):

        r = 0.03
        a = g - v * r
        v += a * dt

        loc += v * dt + a * 0.5 * dt ** 2

        ground = False
        if v.size > 0:

            # floor
            if loc.z < ball.radius:
                loc.z = ball.radius
                if v.z > 210:  # bounce
                    v.z *= -0.6
                elif v.size > 565:  # sliding
                    v = v * (1 - .6 * dt)
                else:  # rolling
                    v = v * (1 - .2 * dt)

                ground = True

            # ceiling
            if loc.z > arena.z - ball.radius:
                v.z *= -1

            # side walls
            if abs(loc.x) > arena.x - ball.radius:
                v.x *= -1

            # goal walls
            if abs(loc.y) > arena.y - ball.radius:
                if (
                    abs(loc.x) < goal_dimensions.x - ball.radius
                    and loc.z < goal_dimensions.z - ball.radius
                ):
                    break
                v.y *= -1

            if loc.z < ball.radius:
                loc.z = ball.radius

        steps.append((loc, ground, i * dt + dt))

    return steps

def bounce(v: Vector3, av: Vector3, n: Vector3):
    R = ball.radius

    v_perp = n * (v * n)
    v_para = v - v_perp
    v_spin = (n % av) * R
    s = v_para + v_spin
    
    ratio = v_perp.size / max(s.size,0.1)
    
    delta_v_perp = - v_perp * 1.6
    delta_v_para = - s * (min(1.0, ratio * 2) * 0.285)
    
    v += delta_v_perp + delta_v_para
    av += (delta_v_para % n) * 0.0003 * R

    return v, av

def distance_between(start: Vector3, dir: Vector3, p: Vector3):
    u = clamp(((p - start) * dir) / (dir * dir), 0, 1)
    return (start + (u * dir) - p).size
 
#chip's sphere-triangle intersect check, didnt work for me (probably my fault)
def intersect_chip(bl:Vector3, tri, renderer, color):
    rx = sign(bl.x)
    ry = sign(bl.y)

    p0 = Vector3(tri[0][0] * rx, tri[0][1] * ry, tri[0][2])
    p1 = Vector3(tri[1][0] * rx, tri[1][1] * ry, tri[1][2])
    p2 = Vector3(tri[2][0] * rx, tri[2][1] * ry, tri[2][2])

    e1 = p1 - p0
    e2 = p2 - p1
    e3 = p0 - p2
    n = (e3 % e1).normalize()

    A = np.matrix([[e1.x, -e3.x, n.x],
                   [e1.y, -e3.y, n.y],
                   [e1.z, -e3.z, n.z]])

    d = bl - p0
    d = np.array([d.x,d.y,d.z])
    A = A.I
    x = A.dot(d)
    x = np.squeeze(np.asarray(x))
    

    u = x[0]
    v = x[1]
    w = 1 - u - v
    z = x[2]

    if u >= 0 and u <= 1 and v >= 0 and v <= 1 and w >= 0 and w <= 1:
        dist = abs(z)
    else:
        dist = ball.radius + 1
        dist = min(dist, distance_between(p0, e1, bl))
        dist = min(dist, distance_between(p1, e2, bl))
        dist = min(dist, distance_between(p2, e3, bl))
    
    y = dist <= ball.radius
    return y, n

#sphere with triangle intersection
def intersect(P:Vector3, tri, renderer, color):
    r = ball.radius

    rx = sign(P.x)
    ry = sign(P.y)

    A = Vector3(tri[0][0] * rx, tri[0][1] * ry, tri[0][2])
    B = Vector3(tri[1][0] * rx, tri[1][1] * ry, tri[1][2])
    C = Vector3(tri[2][0] * rx, tri[2][1] * ry, tri[2][2])

    A = A - P
    B = B - P
    C = C - P
    rr = r * r
    V = (B - A)%(C - A)
    d = A * V
    e = V * V
    sep1 = d * d > rr * e
    aa = A * A
    ab = A * B
    ac = A * C
    bb = B * B
    bc = B * C
    cc = C * C
    sep2 = aa > rr and ab > aa and ac > aa
    sep3 = bb > rr and ab > bb and bc > bb
    sep4 = cc > rr and ac > cc and bc > cc
    AB = B - A
    BC = C - B
    CA = A - C
    d1 = ab - aa
    d2 = bc - bb
    d3 = ac - cc
    e1 = AB * AB
    e2 = BC * BC
    e3 = CA * CA
    Q1 = (A * e1) - (d1 * AB)
    Q2 = (B * e2) - (d2 * BC)
    Q3 = (C * e3) - (d3 * CA)
    QC = (C * e1) - Q1
    QA = (A * e2) - Q2
    QB = (B * e3) - Q3
    sep5 = ((Q1 * Q1) > (rr * e1 * e1)) & ((Q1 * QC) > 0)
    sep6 = ((Q2 * Q2) > (rr * e2 * e2)) & ((Q2 * QA) > 0)
    sep7 = ((Q3 * Q3) > (rr * e3 * e3)) & ((Q3 * QB) > 0)
    separated = sep1 or sep2 or sep3 or sep4 or sep5 or sep6 or sep7

    # if not separated:
    #     renderer.draw_line_3d(A.to_tuple(),p1.to_tuple(),color)
    #     renderer.draw_line_3d(p1.to_tuple(),p2.to_tuple(),color)
    #     renderer.draw_line_3d(p2.to_tuple(),p0.to_tuple(),color)
        
    return not separated, V.normalize()

def parse_obj_mesh_file(file_path):
    file = open(file_path)
    points = []
    tris = []
    lines = file.readlines()
    for line in lines:
        if line.startswith("v"):
            s = line.split(" ")
            t = float(s[3]), float(s[1]), float(s[2])
            points.append(t)

    for line in lines:
        if line.startswith("f"):
            s = line.split(" ")
            if len(s) == 4:
                p1 = int(s[1].split("/")[0])-1
                p2 = int(s[2].split("/")[0])-1
                p3 = int(s[3].split("/")[0])-1
                t = points[p1], points[p2], points[p3]
                
                tris.append(t)
    
    return tris

def render_tris(renderer, tris):
    yellow = renderer.create_color(255,255,255,0)
    for tri in tris:
        renderer.draw_line_3d(tri[0],tri[1],yellow)
        renderer.draw_line_3d(tri[1],tri[2],yellow)
        renderer.draw_line_3d(tri[2],tri[0],yellow)

def render_points(renderer, points):
    yellow = renderer.create_color(255,255,255,0)
    for point in points:
        renderer.draw_rect_3d(point,3,3,True,yellow,True)
                
