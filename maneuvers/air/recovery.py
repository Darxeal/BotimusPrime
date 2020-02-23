from typing import List, Optional

from maneuvers.kit import *

from rlutilities.simulation import Field
from rlutilities.mechanics import AerialTurn


class Recovery(Maneuver):
    """Boost down and try to land smoothly"""

    def __init__(self, car: Car):
        super().__init__(car)

        self.landing = False
        self.aerial_turn = AerialTurn(self.car)

        self.trajectory: List[vec3] = []
        self.landing_pos: Optional[vec3] = None

    def step(self, dt):
        self.simulate_landing()

        self.aerial_turn.step(dt)
        self.controls = self.aerial_turn.controls

        self.controls.boost = angle_between(self.car.forward(), vec3(0, 0, -1)) < 0.8 and not self.landing
        self.controls.throttle = 1  # in case we're turtling

        self.finished = self.car.on_ground

    def simulate_landing(self):
        dummy = Car(self.car)
        self.trajectory = [vec3(dummy.position)]
        self.landing = False
        collision_normal: Optional[vec3] = None

        dt = 1/60
        simulation_duration = 1.0
        for i in range(int(simulation_duration / dt)):
            dummy.step(Input(), dt)
            self.trajectory.append(vec3(dummy.position))

            collision_sphere = sphere(dummy.position, 50)
            collision_ray = Field.collide(collision_sphere)
            collision_normal = collision_ray.direction

            if norm(collision_normal) > 0.0 and i > 20:
                self.landing = True
                self.landing_pos = dummy.position
                break

        if self.landing:
            u = collision_normal
            f = normalize(dummy.velocity - dot(dummy.velocity, u) * u)
            l = normalize(cross(u, f))
            self.aerial_turn.target = mat3(f[0], l[0], u[0],
                                           f[1], l[1], u[1],
                                           f[2], l[2], u[2])
        else:
            self.aerial_turn.target = look_at(vec3(0, 0, -1), xy(self.car.velocity))

    def render(self, draw: DrawingTool):
        if self.landing:
            draw.color(draw.cyan)
            draw.polyline(self.trajectory)

            if self.landing_pos:
                draw.crosshair(self.landing_pos)

        draw.color(draw.green)
        draw.vector(self.car.position, facing(self.aerial_turn.target) * 200)

        draw.color(draw.red)
        draw.vector(self.car.position, self.car.forward() * 200)
