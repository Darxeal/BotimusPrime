from maneuvers.kit import *

from maneuvers.driving.arrive import Arrive
from rlutilities.mechanics import AerialTurn
from rlutilities.simulation import Field


class Recovery(Maneuver):
    '''
    Wrapper for RLU recovery (in AerialTurn).
    Not actually used by Botimus, FastRecovery is better.
    '''
    def __init__(self, car: Car):
        super().__init__(car)

        self.turn = AerialTurn(car)
        self.trajectory = []
        self.find_landing_orientation(200)

    def step(self, dt):
        self.turn.step(dt)
        self.controls = self.turn.controls
        self.controls.throttle = 1 # in case we're turtling
        self.finished = self.car.on_ground

    def find_landing_orientation(self, num_points):

        f = vec3(0, 0, 0)
        l = vec3(0, 0, 0)
        u = vec3(0, 0, 0)

        dummy = Car(self.car)
        self.trajectory = [vec3(dummy.position)]
        found = False
        for i in range(0, num_points):
            dummy.step(Input(), 0.0333)
            self.trajectory.append(vec3(dummy.position))
            u = Field.collide(dummy.hitbox()).direction
            if norm(u) > 0.0 and i > 10:
                f = normalize(dummy.velocity - dot(dummy.velocity, u) * u)
                l = normalize(cross(u, f))
                found = True
                break

        if found:
            self.target = mat3(f[0], l[0], u[0],
                               f[1], l[1], u[1],
                               f[2], l[2], u[2])
        else:
            self.target = look_at(ground(self.car.velocity), vec3(0,0,1))

    def render(self, draw: DrawingTool):
        draw.color(draw.cyan)
        draw.polyline(self.trajectory)
